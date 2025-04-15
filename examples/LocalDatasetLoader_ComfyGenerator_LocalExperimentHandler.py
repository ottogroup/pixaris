from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import LLMMetric
from pixaris.orchestration.base import generate_images_based_on_dataset
import os
import yaml
import json
from PIL import Image

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "test_project"
DATASET = "mock"
with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
EXPERIMENT_RUN_NAME = "example-run"

# +
data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="test",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = LocalExperimentHandler()

# Load object and style images for LLMMetric
object_dir = f"test/{PROJECT}/{DATASET}/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]
style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)
llm_metric = LLMMetric(
    object_images=object_images,
    style_images=style_images,
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}
# -

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[llm_metric],
    args=args,
)

out[0][0].show()
