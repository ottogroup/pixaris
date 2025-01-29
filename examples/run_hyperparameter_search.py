from pixaris.data_loaders.google import GCPDatasetLoader
from pixaris.data_writers.tensorboard import TensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_eval_set as generate,
)
import os
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))

loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set="z_test_correct",
    eval_dir_local="eval_data",
)
comfy_generator = ComfyGenerator(
    workflow_apiformat_path=os.path.abspath(
        os.getcwd() + "/test/assets/test-background-generation.json"
    )
)
writer = TensorboardWriter(
    project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name="pixaris",
)
# Define the arguments
args = {
    "workflow_apiformat_path": os.path.abspath(
        os.getcwd() + "/test/assets/test-background-generation.json"
    ),
    "workflow_image_path": os.path.abspath(
        os.getcwd() + "/test/assets/test-background-generation.png"
    ),
    "eval_set": "z_test_correct",
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
