from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_eval_set,
)
import os
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "test_eval_set"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"
WORKFLOW_IMAGE_PATH = os.getcwd() + "/test/assets/test-background-generation.png"

data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)
generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)
data_writer = GCPTensorboardWriter(
    project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)
# Define the arguments
args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "run_name": "example_run",
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

out = generate_images_for_hyperparameter_search_based_on_eval_set(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
)

out
