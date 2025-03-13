import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_eval_set,
)
import os

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

EVAL_SET = "test_eval_set"
PROMPT_1 = "A beautiful woman in the desert"
PROMPT_2 = "A beautiful woman on a moon"
RUN_NAME = "example-flux"

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)

generator = FluxFillGenerator()

data_writer = GCPTensorboardWriter(
    project_id=config["gcp_project_id"],
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
    "eval_set": EVAL_SET,
    "run_name": RUN_NAME,
}
# -

# execute
out = generate_images_for_hyperparameter_search_based_on_eval_set(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
)
