from PIL import Image
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
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
from pixaris.metrics.llm import (
    BaseLLMMetric,
    ErrorLLMMetric,
    SimilarityLLMMetric,
    StyleLLMMetric,
)
import os
import yaml
import json

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "dummy_project"
DATASET = "dummy_dataset"
with open(os.getcwd() + "/test/assets/test_inspo_apiformat.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(os.getcwd() + "/test/assets/test_inspo.png")
EXPERIMENT_RUN_NAME = "example-run"


# Setup the GCPDatasetLoader, ComfyGenerator, and GCPExperimentHandler
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "pillow_images": [
        {
            "node_name": "Load Inspo Image",
            "pillow_image": Image.open("test/assets/test_inspo_image.jpg"),
        }
    ],
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

# Define the paths to the images used to calculate the metrics
style_dir = "test/test_results/dummy_project/dummy_dataset/example_run/"
style_images = [
    Image.open(os.path.join(style_dir, image)) for image in os.listdir(style_dir)
]
object_dir = "test/test_results/dummy_project/dummy_dataset/example_run/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]
test_dir = "test/test_project/mock/mask/"
mask_images = [Image.open(test_dir + image) for image in os.listdir(test_dir)]

# define the metrics we want to use

# BaseLLMMetric is a generic class that can be used for any LLM metric
# The prompt is a string that describes the task to be performed by the LLM
# BaseLLMMetric takes a prompt, and a number of lists of images to be used. For example You can give a list of style images and a list of object images.
# Make sure the prompt describes how to use the style and object images.

same_content_prompt = """ You will be provided with two images. Your task is to analyze them and determine if their *core visual content* is semantically identical or completely distinct.

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
{"content_metric": 1}
```
"""
same_content_llm_metric = BaseLLMMetric(
    prompt=same_content_prompt,
    object_images=object_images,
)
# SimilarityLLMMetric is a specialized LLM Metric that will compare the similartities of the generated images vs. the reference images.
similarity_llm_metric = SimilarityLLMMetric(
    reference_images=object_images,
)
# StyleLLMMetric is a specialized LLM Metric that will compare the styles of the generated images vs. the style images.
style_llm_metric = StyleLLMMetric(
    style_images=style_images,
)
# ErrorLLMMetric is a specialized LLM Metric that will find errors in the generated images.
error_llm_metric = ErrorLLMMetric()

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

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[
        same_content_llm_metric,
        similarity_llm_metric,
        style_llm_metric,
        error_llm_metric,
        luminescence_mask_metric,
        saturation_mask_metric,
        saturation_metric,
        luminence_metric,
        iou_metric,
    ],
    args=args,
)

out[0][0].show()
