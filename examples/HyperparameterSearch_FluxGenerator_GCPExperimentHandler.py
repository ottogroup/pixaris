import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)
import os

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

PROJECT = "dummy_project"
DATASET = "dummy_dataset"
PROMPT_1 = "A beautiful woman in the desert"
PROMPT_2 = "A beautiful woman on a moon"
EXPERIMENT_RUN_NAME = "example-flux"

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
    force_download=False,
)

generator = FluxFillGenerator()

experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
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
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)
