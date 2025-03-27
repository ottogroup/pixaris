from PIL import Image
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import LLMMetric
from pixaris.orchestration.base import generate_images_based_on_dataset
import os
import yaml
import json

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "test_project"
DATASET = "test_dataset"
with open(os.getcwd() + "/test/assets/test_inspo_apiformat.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(os.getcwd() + "/test/assets/test_inspo.png")
EXPERIMENT_RUN_NAME = "example-run"


# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="eval_data",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)
data_writer = GCPTensorboardWriter(
    gcp_project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)

object_dir = "test/test_project/mock/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]
style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)
llm_metric = LLMMetric(
    object_images=object_images,
    style_images=style_images,
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "dataset": DATASET,
    "pillow_images": [
        {
            "node_name": "Load Inspo Image",
            "pillow_image": Image.open("test/assets/test_inspo_image.jpg"),
        }
    ],
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}
# -

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    data_writer=data_writer,
    metrics=[llm_metric],
    args=args,
)

out[0][0].show()
