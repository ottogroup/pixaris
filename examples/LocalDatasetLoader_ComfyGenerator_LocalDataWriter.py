from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_eval_set
import os
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "mock"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"
WORKFLOW_IMAGE_PATH = os.getcwd() + "/test/assets/test-background-generation.png"
RUN_NAME = "example_run"

# +
data_loader = LocalDatasetLoader(
    eval_set=EVAL_SET,
    eval_dir_local="test/test_eval_set",
)

generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)

data_writer = LocalDataWriter()

args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "image_paths": [
        {
            "node_name": "Load Inspo Image",
            "image_path": "test/assets/test_inspo_image.jpg",
        }
    ],
    "run_name": RUN_NAME,
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

out
