from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_eval_set
import os

EVAL_SET = "mock"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test_inspo_apiformat.json"
WORKFLOW_IMAGE_PATH = os.getcwd() + "/test/assets/test-just-load-and-save.png"

# Define the dataset Loader
loader = LocalDatasetLoader(
    eval_set=EVAL_SET,
    eval_dir_local="test/test_eval_data",
)

# Define the Generator
comfy_generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)
writer = LocalDataWriter()

# Define args for additional info
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
    "run_name": "example_run_metrics_5",
}

# execute
out = generate_images_based_on_eval_set(
    data_loader=loader,
    image_generator=comfy_generator,
    data_writer=writer,
    metrics=[],
    args=args,
)

out
