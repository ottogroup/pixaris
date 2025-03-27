import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)
import os

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

PROJECT = "test_project"
DATASET = "test_dataset"
PROMPT_1 = "A beautiful woman in the desert"
PROMPT_2 = "A beautiful woman on a moon"
EXPERIMENT_RUN_NAME = "example-flux"

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="eval_data",
    force_download=False,
)

generator = FluxFillGenerator()

data_writer = GCPTensorboardWriter(
    gcp_project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)

args = {
    "hyperparameters": [
        {
            "node_name": "prompt",
            "input": "prompt",
            "value": [PROMPT_1, PROMPT_2],
        },
    ],
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}
# -

# execute
out = generate_images_for_hyperparameter_search_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
)
