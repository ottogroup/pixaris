# set DEV_MODE to true if you want to work locally with 8188 port. Has to be set before importing from pixaris.
import os

os.environ["DEV_MODE"] = "true"
from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.comfyui_cluster import ComfyClusterGenerator
from pixaris.orchestration.kubernetes import pixaris_orchestration_kubernetes_locally
import yaml
import json
from PIL import Image

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "mock"
with open(os.getcwd() + "/test/assets/test_inspo_apiformat.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
RUN_NAME = "example-run"


# +
data_loader = LocalDatasetLoader(
    eval_set=EVAL_SET,
    eval_dir_local="test/test_eval_set",
)

generator = ComfyClusterGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

data_writer = LocalDataWriter()

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "eval_set": EVAL_SET,
    "run_name": RUN_NAME,
    "max_parallel_jobs": 2,
}
# -

# execute
pixaris_orchestration_kubernetes_locally(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[],
    args=args,
    auto_scale=True,
)
