from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import BaseLLMMetric
from pixaris.metrics.luminescence import LuminescenceComparisonByMaskMetric
from pixaris.metrics.saturation import SaturationComparisonByMaskMetric
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

# Load object, style and mask images for metrics
object_dir = f"test/{PROJECT}/{DATASET}/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]
style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)
test_dir = f"test/{PROJECT}/{DATASET}/mask/"
mask_images = [Image.open(test_dir + image) for image in os.listdir(test_dir)]

# define the metrics we want to use
same_item_prompt =""" You will be provided with two images. Your task is to analyze them and determine if their *core visual content* is semantically identical or completely distinct.

**Definition of "Same Content" (output `1` for 'content_metric'):**
The images depict the *exact same unique subject, scene, or specific entity*.
Minor variations are acceptable and *should be ignored* when determining sameness. These include:
*   Slight changes in angle, perspective, or zoom (e.g., the same specific car from slightly different sides or zoomed in/out).
*   Minor cropping or resizing.
*   Differences in lighting conditions, color balance, brightness, contrast, or application of minor stylistic filters.
*   Addition or removal of small watermarks, logos, text overlays, or minor annotations that do not alter the primary subject.
*   Different file formats, compression artifacts, or slight changes in resolution.
*   If one image is clearly a modified version of the other (e.g., a black and white version of a color image, or an edited version of the original scene).

**Definition of "Completely Different Content" (output `0` for 'content_metric'):**
The images depict entirely distinct subjects, scenes, or entities with no semantic overlap. For example:
*   A picture of a cat and a picture of a car.
*   Two different people, even if they share some resemblance.
*   Two different landscapes, even if they are of the same *type* (e.g., two different beaches).
*   Two different objects, even if they are of the same *category* (e.g., two different chairs, two different dogs).
*   Two different events or moments in time.

**Output Format:**
Provide your answer strictly in the following JSON format. Do not include any additional text or explanation outside of this JSON.
```json
{"content_metric": [0 or 1]}"""
same_content_llm_metric = BaseLLMMetric(
    prompt=same_item_prompt,
    object_images=object_images,
)
luminescence_metric = LuminescenceComparisonByMaskMetric(mask_images=mask_images)
saturation_metric = SaturationComparisonByMaskMetric(mask_images=mask_images)

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
    metrics=[same_content_llm_metric, luminescence_metric, saturation_metric],
    args=args,
)

out[0][0].show()
