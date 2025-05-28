# %% [markdown]
# # Image Generation with Metrics Using ComfyUI and Local Experiment Handler
#
# This script demonstrates how to use the LocalDatasetLoader, ComfyGenerator, and LocalExperimentHandler with all implemented metrics in the pixaris library.
# This is a good starting point to copy metrics you would like to use in your own experiments.
#
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml
# - Test assets available in the project structure
# %% [markdown]
# ## Import Libraries and Setup

# %%


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
from pixaris.metrics.llm import (
    BaseLLMMetric,
    ErrorLLMMetric,
    SimilarityLLMMetric,
    StyleLLMMetric,
)
from pixaris.orchestration.base import generate_images_based_on_dataset
import os
import json
from PIL import Image
# %% [markdown]
# ## Configuration Parameters

# %%
# Configuration parameters - MODIFY THESE VALUES
PROJECT = "test_project"  # Your project name
DATASET = "mock"  # Your dataset name
EXPERIMENT_RUN_NAME = "example-run"  # Name of this experiment run

# Load workflow data from test assets

with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)

# %% [markdown]
# ## Initialize Components

# %%
# Initialize components
data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="test",
)

generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

experiment_handler = LocalExperimentHandler()

# %% [markdown]
# ## Load Images for Metrics

# %%
# Load images for metrics
################################################################
# Define the paths to the images used to calculate the metrics
################################################################

# Style directory contains images that represent the style we want to compare against. The first image will be compared to the first generated image, the second image to the second generated image, and so on.
# here, we take some images from a feedback iteration.
style_dir = "test/test_results/test_project/feedback_iterations/test_iteration/"
style_images = [
    Image.open(os.path.join(style_dir, image)) for image in os.listdir(style_dir)
]

# Object directory contains images that represent the objects we want to compare against, i.e. the original input images showing the unchanged objects before generation.
object_dir = "test/test_project/mock/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]

# Mask directory contains images that represent the masks we want to use for the luminescence and saturation metrics
mask_dir = "test/test_project/mock/mask/"
mask_images = [Image.open(mask_dir + image) for image in os.listdir(mask_dir)]

# %% [markdown]
# ## Define Metrics

# %%
# Define metrics
##########################################################
############### PREIMPLEMENTED LLM METRICS ###############
##########################################################
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

##########################################################
############### DEFINE YOUR OWN LLM METRIC ###############
##########################################################

# BaseLLMMetric is a generic class that can be used for any LLM metric
# The prompt is a string that describes the task to be performed by the LLM
# BaseLLMMetric takes a prompt, and a number of lists of images to be used. For example You can give a list of style images and a list of object images.
# Make sure the prompt describes how to use the style and object images.
# Here is an example of how you could easily define a metric that checks if two images have the same core visual content.

same_content_prompt = """ You will be provided with two images. Your task is to analyze them and determine if their *core visual content* is identical or completely distinct.

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


###################################################################
############### LUMINESCENCE AND SATURATION METRICS ###############
###################################################################

# LuminescenceComparisonByMaskMetric and SaturationComparisonByMaskMetric are specialized metrics that will compare the
# luminescence and saturation of the generated images inside and outdside of the provided mask images.
luminescence_mask_metric = LuminescenceComparisonByMaskMetric(mask_images=mask_images)
saturation_mask_metric = SaturationComparisonByMaskMetric(mask_images=mask_images)
# or we can calculate it over the entire image without a mask
luminence_metric = LuminescenceWithoutMaskMetric()
saturation_metric = SaturationWithoutMaskMetric()

#########################################################
########################## IOU ##########################
#########################################################

# IoUMetric is a metric that calculates the Intersection over Union (IoU) between the generated images and the provided mask images.
# It is only useful if the generated image is a binary image like a mask. We show how to use it here anyway.
iou_metric = IoUMetric(reference_images=mask_images)

# %% [markdown]
# ## Configure and Run Image Generation

# %%
################################################################################
# Now we have all the components needed to generate images based on the dataset
################################################################################

# define the arguments for the generation
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

# Execute image generation with metrics
print("Executing image generation and evaluation...")
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

# %%
print("\n=== Displaying one Generated Image ===")
# Display the first generated imageout[0][0].show()
out[0][0].show()

# %% [markdown]
# ## Next Steps
#
# After execution:
# 1. Generated images and Experiment metadata and are stored in your local experiment directory.
# 2. View results in the Pixaris UI (see how to deploy in examples/frontend_deployment)
