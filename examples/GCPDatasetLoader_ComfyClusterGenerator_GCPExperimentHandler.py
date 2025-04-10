# set DEV_MODE to true if you want to work locally with 8188 port. Has to be set before importing from pixaris.
import os

os.environ["DEV_MODE"] = "true"
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.comfyui_cluster import ComfyClusterGenerator
from pixaris.orchestration.kubernetes import pixaris_orchestration_kubernetes_locally
import yaml
import json
from PIL import Image

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "dummy_project"
DATASET = "dummy_dataset"
with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
EXPERIMENT_RUN_NAME = "example-cluster-run"

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
)

generator = ComfyClusterGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "max_parallel_jobs": 2,
    "gcp_project_id": config["gcp_project_id"],
}
# -

# execute
pixaris_orchestration_kubernetes_locally(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
    auto_scale=True,
)
