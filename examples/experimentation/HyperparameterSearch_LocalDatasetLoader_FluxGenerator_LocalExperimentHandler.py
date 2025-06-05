import yaml
from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)
import os

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

PROJECT = "test_project"  # Your project name
DATASET = "mock"  # Your dataset name
PROMPT_1 = "A beautiful woman in the desert"
PROMPT_2 = "A beautiful woman on a moon"
EXPERIMENT_RUN_NAME = "example-flux"

# +
data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="test",
)

generator = FluxFillGenerator()

experiment_handler = LocalExperimentHandler()

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
