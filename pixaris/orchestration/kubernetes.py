import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = (
    "python"  # fix for aiplatform, it"s currently using pre 3.20 version of protobuf and we using > 5.0
)
import click
from kubernetes import client, config
import uuid
import time

from pixaris.data_loaders.base import DatasetLoader
from pixaris.generation.base import ImageGenerator
from pixaris.data_writers.base import DataWriter
from pixaris.metrics.base import BaseMetric
from pixaris.orchestration.base import generate_images_based_on_dataset
import pickle
import io
import tarfile
import pathlib
from kubernetes.stream import stream


@click.group()
def cli():
    pass


@cli.command(name="cli-kubernetes-generate-images-based-on-eval-set-execute-remotely")
def cli_kubernetes_generate_images_based_on_dataset_execute_remotely():
    """
    CLI command to trigger remote evaluation. This command should be run on the Kubernetes cluster.
    It will wait for a pickled input file to be uploaded to /tmp/input.pkl and then execute the evaluation.
    """
    pickled_input_path = "/tmp/input.pkl"
    # wait on existence of file (until upload is completed)
    wait_cycles = 0
    while not os.path.exists(f"{pickled_input_path}.done"):
        wait_cycles += 1
        if wait_cycles > 100:
            raise ValueError("Timeout: Input file was not uploaded.")
        print("Waiting for inputs to be uploaded...")
        time.sleep(3)
    with open(pickled_input_path, "rb") as f:
        inputs = pickle.load(f)

    data_loader = inputs["data_loader"]
    image_generator = inputs["image_generator"]
    data_writer = inputs["data_writer"]
    metrics = inputs["metrics"]
    args = inputs["args"]

    print("Starting generation...")
    generate_images_based_on_dataset(
        data_loader=data_loader,
        image_generator=image_generator,
        data_writer=data_writer,
        metrics=metrics,
        args=args,
    )


def copy_bytes_to_pod(
    kube_conn, namespace: str, pod_name: str, bytes_to_copy: bytes, dest_path: str
):
    """
    Copy a file to a pod comparable with kubectl cp. See here: https://github.com/kubernetes-client/python/issues/476#issuecomment-2701387338

    Args:
        kube_conn: The connection to the Kubernetes cluster.
        namespace: The namespace of the pod.
        pod_name: The name of the pod.
        bytes_to_copy: The bytes to be copied.
        dest_path: The destination path on the pod.
    """
    # open and compress local tar file
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tarinfo = tarfile.TarInfo(pathlib.Path(dest_path).name)
        tarinfo.size = len(bytes_to_copy)
        tar.addfile(tarinfo, io.BytesIO(bytes_to_copy))
    buf.seek(0)

    # Copying file
    exec_command = ["tar", "xzvf", "-", "-C", str(pathlib.Path(dest_path).parent)]
    resp = stream(
        kube_conn.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=exec_command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    chunk_size = 10 * 1024 * 1024
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print(f"STDOUT: {resp.read_stdout()}")
        if resp.peek_stderr():
            print(f"STDERR: {resp.read_stderr()}")
        if read := buf.read(chunk_size):
            resp.write_stdin(read)
        else:
            break
    resp.close()

    resp = stream(
        kube_conn.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=["touch", f"{dest_path}.done"],
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )
    resp.close()

    print(f"File copied to {pod_name}:{dest_path}")


def pixaris_orchestration_kubernetes_locally(
    data_loader: DatasetLoader,
    image_generator: ImageGenerator,
    data_writer: DataWriter,
    metrics: list[BaseMetric],
    args: dict[str, any],
    auto_scale: bool,
):
    """
    Trigger remote evaluation on the Kubernetes cluster. This function will pickle the inputs and upload them to the
    Kubernetes cluster. It will then trigger the remote evaluation.

    Args:
    data_loader (DatasetLoader): The data loader to load the evaluation set.
    image_generator (ImageGenerator): The image generator to generate images. E.g. ComfyClusterGenerator
    data_writer (DataWriter): The data writer to save generated images.
    metrics (list[BaseMetric]): The metrics to calculate.
    args (dict[str, any]): A dictionary of arguments, including:
        - "workflow_apiformat_json" (str): The path to the workflow file in API format.
        - "workflow_pillow_image" (PIL.Image): The image to use as input for the workflow.
        - "dataset" (str): The evaluation set to use.
        - "pillow_images" (list[dict]): A list of images to use as input for the workflow.
        - "experiment_run_name" (str): The name of the run.
        - "max_parallel_jobs" (int): The maximum number of parallel jobs to run.
    auto_scale (bool): Whether to auto scale the cluster to the maximum number of parallel jobs.

    """
    config.load_kube_config()
    if auto_scale:  # always necessary unless the cluster was already scaled up manually
        max_parallel_jobs = args.get("max_parallel_jobs", 1)
        print("Auto scaling...")
        print(f"Scaling to {max_parallel_jobs} replicas")
        apps_v1 = client.AppsV1Api()
        apps_v1.patch_namespaced_deployment_scale(
            "comfy-ui-deployment", "batch", {"spec": {"replicas": max_parallel_jobs}}
        )
    print("Triggering remote evaluation...")

    # Prepare the inputs and and pickle them
    inputs = {
        "data_loader": data_loader,
        "image_generator": image_generator,
        "data_writer": data_writer,
        "metrics": metrics,
        "args": args,
    }
    pickled_inputs = pickle.dumps(inputs)

    # Trigger the remote evaluation
    batch_v1 = client.BatchV1Api()
    experiment_run_name = args["experiment_run_name"]
    job_name = f"evaluation-{experiment_run_name[0 : (min(30, len(experiment_run_name)))]}-{uuid.uuid4().hex[0:6]}"
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": job_name},
        "spec": {
            "parallelism": 1,
            "completions": 1,
            "backoffLimit": 0,
            "template": {
                "spec": {
                    "serviceAccountName": "experiment",
                    "containers": [
                        {
                            "name": "main",
                            "image": f"europe-west4-docker.pkg.dev/{args['gcp_project_id']}/docker-registry/pixaris_image:latest",
                            "command": [
                                "pixaris-orchestration-kubernetes",
                                "cli-kubernetes-generate-images-based-on-eval-set-execute-remotely",
                            ],
                        }
                    ],
                    "restartPolicy": "Never",
                    "imagePullPolicy": "Always",
                }
            },
        },
    }
    batch_v1.create_namespaced_job(body=job, namespace="batch")

    # Get pod name to upload inputs there
    core_v1 = client.CoreV1Api()
    pod_name = None
    while pod_name is None:
        print("Waiting for pod to start...")
        time.sleep(5)
        job = batch_v1.read_namespaced_job(job_name, "batch")
        if job.status.failed:
            raise ValueError(f"Job {job_name} failed.")

        pods = core_v1.list_namespaced_pod(
            namespace="batch", label_selector=f"job-name={job_name}"
        )
        for pod in pods.items:
            pod_phase = pod.status.phase
            if pod_phase == "Running":
                pod_name = pod.metadata.name

    # Copy the pickled inputs to the pod
    copy_bytes_to_pod(
        kube_conn=core_v1,
        namespace="batch",
        pod_name=pod_name,
        bytes_to_copy=pickled_inputs,
        dest_path="/tmp/input.pkl",
    )

    print("Remote evaluation triggered.")
    print(f"Job logs: kubectl logs -n batch job/{job_name}")
    print(
        f"or https://console.cloud.google.com/kubernetes/job/europe-west4-a/cluster/batch/{job_name}/logs?project={args['gcp_project_id']}"
    )
