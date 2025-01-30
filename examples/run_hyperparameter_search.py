from pixaris.data_loaders.google import GCPDatasetLoader
from pixaris.data_writers.tensorboard import TensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_eval_set as generate,
)
import os
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "z_test_correct"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"
WORKFLOW_IMAGE_PATH = os.getcwd() + "/test/assets/test-background-generation.png"

loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)
comfy_generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)
writer = TensorboardWriter(
    project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)
# Define the arguments
args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "run_name": "example_run_debug",
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

out = generate(
    data_loader=loader,
    image_generator=comfy_generator,
    data_writer=writer,
    args=args,
)

out
