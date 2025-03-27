# set DEV_MODE to true if you want to work locally with 8188 port. Has to be set before importing from pixaris.
import os

os.environ["DEV_MODE"] = "true"
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_bucket import GCPBucketWriter
from pixaris.generation.comfyui_cluster import ComfyClusterGenerator
from pixaris.orchestration.kubernetes import pixaris_orchestration_kubernetes_locally
import yaml
import json
from PIL import Image
from datetime import datetime

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "test_project"
DATASET = "test_dataset"
with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
EXPERIMENT_RUN_NAME = "example-run"
current_time = datetime.now().strftime("%y%m%d_%H%M")
BUCKET_RESULTS_PATH = f"pickled_results/{DATASET}/{current_time}_{EXPERIMENT_RUN_NAME}"
print(BUCKET_RESULTS_PATH)
BUCKET_NAME = config["gcp_bucket_name"]


# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="eval_data",
)

generator = ComfyClusterGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

data_writer = GCPBucketWriter(
    gcp_project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=BUCKET_NAME,
    bucket_results_path=BUCKET_RESULTS_PATH,
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "max_parallel_jobs": 2,
}
# -

# execute
pixaris_orchestration_kubernetes_locally(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
    auto_scale=True,
)

# BUG
# currently the gcp_tensorboard data writer is not working on the kubernetes cluster. So we have build the folllwoing workaround:"""
if False:
    data_writer.upload_experiment_from_bucket_to_tensorboard()
