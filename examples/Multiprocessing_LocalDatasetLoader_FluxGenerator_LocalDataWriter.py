from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import generate_images_based_on_eval_set
import os
import yaml

EVAL_SET = "mock"
PROMPT = "A beautiful woman on a beach"
RUN_NAME = "example-flux"

# Set your API Key
config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

# +
data_loader = LocalDatasetLoader(
    eval_set=EVAL_SET,
    eval_dir_local="test/test_eval_set",
)

generator = FluxFillGenerator()

data_writer = LocalDataWriter()

args = {
    "generation_params": [
        {
            "node_name": "prompt",
            "input": "prompt",
            "value": PROMPT,
        },
    ],
    "eval_set": EVAL_SET,
    "run_name": RUN_NAME,
    "max_parallel_jobs": 2,
}
# -

# execute
out = generate_images_based_on_eval_set(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
)

out[0][0].show()
