from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)
import os
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
EXPERIMENT_RUN_NAME = "example-run"

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
    force_download=False,
)
generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
# Define the arguments
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "hyperparameters": [
        {
            "node_name": "KSampler (Efficient) - Generation",
            "input": "steps",
            "value": [10, 15],
        },
        {
            "node_name": "KSampler (Efficient) - Generation",
            "input": "sampler_name",
            "value": ["euler_ancestral", "euler"],
        },
    ],
}
# -

out = generate_images_for_hyperparameter_search_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)
