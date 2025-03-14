from PIL import Image
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import LLMMetric
from pixaris.orchestration.base import generate_images_based_on_eval_set
import os
import yaml
import json

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "test_eval_set"
with open(os.getcwd() + "/test/assets/test_inspo_apiformat.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-just-load-and-save.png"
)
RUN_NAME = "example-run"


# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)
data_writer = GCPTensorboardWriter(
    project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)

object_dir = "test/test_eval_set/mock/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]
style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)
llm_metric = LLMMetric(
    object_images=object_images,
    style_images=style_images,
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "eval_set": EVAL_SET,
    "pillow_images": [
        {
            "node_name": "Load Inspo Image",
            "pillow_image": Image.open("test/assets/test_inspo_image.jpg"),
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
    metrics=[llm_metric],
    args=args,
)

out[0][0].show()
