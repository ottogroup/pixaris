# %% [markdown]
# # Image Generation with Metrics Using Local Resources
#
# This script demonstrates how to use Pixaris for image generation and evaluation using local resources.
# It configures a LocalDatasetLoader, ComfyGenerator, and LocalExperimentHandler with multiple metrics
# to generate and evaluate images.
#
# ## Requirements
# - pixaris package installed
# - test assets available in the project structure

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import json
from PIL import Image
from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import LLMMetric
from pixaris.metrics.luminescence import LuminescenceComparisonByMaskMetric
from pixaris.metrics.saturation import SaturationComparisonByMaskMetric
from pixaris.orchestration.base import generate_images_based_on_dataset

if False:  # set to True if executing from notebook
    os.chdir("../../")

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

# Load workflow image
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
object_dir = f"test/{PROJECT}/{DATASET}/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]

style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)

test_dir = f"test/{PROJECT}/{DATASET}/mask/"
mask_images = [Image.open(test_dir + image) for image in os.listdir(test_dir)]

# %% [markdown]
# ## Define Metrics

# %%
# Define metrics
llm_metric = LLMMetric(
    object_images=object_images,
    style_images=style_images,
)

luminescence_metric = LuminescenceComparisonByMaskMetric(mask_images=mask_images)

saturation_metric = SaturationComparisonByMaskMetric(mask_images=mask_images)

# %% [markdown]
# ## Configure and Run Image Generation

# %%
# Define arguments for generation
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
    metrics=[llm_metric, luminescence_metric, saturation_metric],
    args=args,
)

# %%
print("\n=== Displaying one Generated Image ===")
# Display the first generated image
out[0][0].show()

# %% [markdown]
# ## Next Steps
#
# After execution:
# 1. Generated images and Experiment metadata and are stored in your local experiment directory.
# 2. View results in the Pixaris UI (see how to deploy in examples/frontend_deployment)
