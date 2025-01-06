from kubernetes import client, config
from PIL import Image
import requests
from threading import Lock, Thread
import time
from pixaris.generation.comfyui_utils.workflow import ComfyWorkflow
import os

DEV_MODE = os.getenv("DEV_MODE", "false") == "true"
mutex = Lock()


class ComfyCluster:
    """
    Cluster to run Comfy workflows. It will automatically fetch available hosts and distribute the workflows to them.
    If the environment variable DEV_MODE is set to true, it will run the workflows locally and it uses localhost:8188.
    """

    def __init__(self):
        self.hosts = {}
        if DEV_MODE:
            config.load_kube_config()
        else:
            config.load_incluster_config()
        self.run_background_task = True
        self.start_background_task()

    def _fetch_pod_ips(self) -> list[str]:
        """
        Fetch the IPs of the pods running the Comfy UI in the cluster. If the environment variable DEV_MODE is set to true, it will return localhost.

        Returns:
            list[str]: List of IPs of the pods
        """
        if DEV_MODE:
            return ["127.0.0.1"]
        v1 = client.CoreV1Api()
        pod_list = v1.list_namespaced_pod(
            namespace="batch", label_selector="app=comfy-ui", watch=False
        )
        ips = []
        for pod in pod_list.items:
            ips.append(pod.status.pod_ip)
        print(f"Found Pod IPs: {ips}")
        return ips

    def _fetch_available_hosts(self) -> list[str]:
        """
        Fetch the available hosts by checking if the Comfy UI is running on the pod.

        Returns:
            list[str]: List of available hosts
        """
        hosts = []
        for ip in self._fetch_pod_ips():
            host = f"{ip}:8188"
            try:
                resp = requests.get(f"http://{host}", timeout=5)
                if resp.status_code == 200:
                    hosts.append(host)
            except Exception:
                pass
        return hosts

    def update_available_hosts(self):
        """
        Update the available hosts by fetching the IPs of the pods and checking if the Comfy UI is running on them. Use mutex to avoid conflicts.
        """
        available_hosts = self._fetch_available_hosts()
        global mutex
        with mutex:
            for host in available_hosts:
                if host not in self.hosts:
                    self.hosts[host] = {"in_use": False, "unresponsive": False}
                else:
                    self.hosts[host]["unresponsive"] = False
        print(f"Available hosts: {self.hosts}")

    def _get_host(self) -> str:
        """
        Get an available host. If no host is available, it will wait with a exponential backoff and try again, after the 15th retry, it will raise an exception. Use mutex to avoid conflicts.

        Returns:
            str: The host to use
        """
        global mutex
        for i in range(1, 15 + 1):
            with mutex:
                for host, info in self.hosts.items():
                    if not info["in_use"] and not info["unresponsive"]:
                        self.hosts[host]["in_use"] = True
                        return host
            time.sleep(i * i)
        raise Exception("Timeout for getting host")

    def _release_host(self, host: str):
        """
        Release a host. Use mutex to avoid conflicts.

        Args:
            host (str): The host to release
        """
        global mutex
        with mutex:
            self.hosts[host]["in_use"] = False

    def _mark_host_as_unresponsive(self, host: str):
        """
        Mark a host as unresponsive. Use mutex to avoid conflicts.

        Args:
            host (str): The host to mark as unresponsive
        """
        global mutex
        with mutex:
            self.hosts[host]["unresponsive"] = True

    def start_background_task(self):
        """
        Start a background task to update the available hosts every minute.
        """

        def task():
            while self.run_background_task:
                self.update_available_hosts()
                time.sleep(60)

        self.background_task = Thread(target=task, daemon=True)
        self.background_task.start()

    def close(self):
        """
        Close the cluster and release all hosts.
        """
        self.run_background_task = False

    def run_image_workflow(
        self,
        workflow_url: str,
        args: dict[str, dict[str, any]] = {},
        image_args: dict[str, Image.Image] = {},
        output_node_name: str = "Save Image",
    ) -> list[Image.Image]:
        """
        Run a workflow with the given arguments and images. It will retry 3 times if an error occurs.

        Args:
            workflow_url (str): The URL of the workflow
            args (dict[str, dict[str, any]]): The arguments for the nodes of the workflow
            image_args (dict[str, Image.Image]): The images for the nodes of the workflow
            output_node_name (str): The name of the output node. Defaults to "Save Image".
        Returns:
            list[Image.Image]: The output images of the workflow, base one the output node name
        """
        for retry in range(3):
            host = self._get_host()
            try:
                wf = ComfyWorkflow(host, workflow_url)
                for node_name, values in args.items():
                    for field, value in values.items():
                        wf.set_value(node_name, field, value)
                for key, image in image_args.items():
                    wf.set_image(key, image)
                start_time = time.time()
                wf.execute()
                print(
                    f"Workflow '{workflow_url}' executed in {time.time() - start_time:.2f} seconds"
                )
                return wf.get_image(output_node_name)
            except Exception as e:
                print(f"Error executing workflow: {e}")
                self._mark_host_as_unresponsive(host)
                time.sleep((retry + 1) ** 2)
                if retry == 2:
                    raise e
                return []
            finally:
                self._release_host(host)
