from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset
import os
import yaml

PROJECT = "test_project"
DATASET = "mock"
PROMPT = "A beautiful woman on a beach"
EXPERIMENT_RUN_NAME = "example-flux"

# Set your API Key
config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

# +
data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="test",
)

generator = FluxFillGenerator()

experiment_handler = LocalExperimentHandler()

args = {
    "generation_params": [
        {
            "node_name": "prompt",
            "input": "prompt",
            "value": PROMPT,
        },
    ],
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "max_parallel_jobs": 2,  # how many parallel jobs/calls to API to run
}
# -

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

out[0][0].show()
