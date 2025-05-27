from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.iou import IoUMetric
from pixaris.metrics.luminescence import (
    LuminescenceComparisonByMaskMetric,
    LuminescenceWithoutMaskMetric,
)
from pixaris.metrics.saturation import (
    SaturationComparisonByMaskMetric,
    SaturationWithoutMaskMetric,
)
from pixaris.orchestration.base import generate_images_based_on_dataset
import os
import json
from PIL import Image

PROJECT = "test_project"
DATASET = "mock"
with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
EXPERIMENT_RUN_NAME = "example-run"

data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="test",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = LocalExperimentHandler()

# Load mask images from the local directory
test_dir = f"test/{PROJECT}/{DATASET}/mask/"
mask_images = [Image.open(test_dir + image) for image in os.listdir(test_dir)]

# LuminescenceComparisonByMaskMetric and SaturationComparisonByMaskMetric are specialized metrics that will compare the
# luminescence and saturation of the generated images inside and outdside of the provided mask images.
luminescence_mask_metric = LuminescenceComparisonByMaskMetric(mask_images=mask_images)
saturation_mask_metric = SaturationComparisonByMaskMetric(mask_images=mask_images)
# or we can calculate it over the entire image without a mask
luminence_metric = LuminescenceWithoutMaskMetric()
saturation_metric = SaturationWithoutMaskMetric()

# IoUMetric is a metric that calculates the Intersection over Union (IoU) between the generated images and the provided mask images.
# Only useful if the generated image is a binary image like a mask.
iou_metric = IoUMetric(reference_images=mask_images)

# define the arguments for the generation
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

out[0][0].show()
