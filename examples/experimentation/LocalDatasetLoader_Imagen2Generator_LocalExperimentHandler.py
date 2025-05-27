# %% [markdown]
# # Local Experiment with Imagen2Generator
# 
# This script demonstrates how to run experiments using Pixaris with local and GCP components:
# - LocalDatasetLoader for loading data from the local filesystem
# - Imagen2Generator for generating images using Google's Imagen 2 model
# - LocalExperimentHandler for storing experiment results locally
# - Standard orchestration for single-machine processing
# 
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml for Imagen2 API access
# - Test assets available in the local experiment inputs directory

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
import json
from PIL import Image

from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.imagen2 import Imagen2Generator
from pixaris.orchestration.base import generate_images_based_on_dataset

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "test_project"
DATASET = "mock"
EXPERIMENT_RUN_NAME = "example-run"
PROMPT = "Place the animal in front of a background of a nice lush green forest."

# %% [markdown]
# ## Initialize Components

# %%
print("\n=== Initializing Components ===")

# Initialize the Local Dataset Loader
print(f"Initializing LocalDatasetLoader for project '{PROJECT}', dataset '{DATASET}'")
data_loader = LocalDatasetLoader(
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
)

# Initialize the Imagen2Generator
print("Initializing Imagen2Generator")
generator = Imagen2Generator(
    gcp_project_id=config["gcp_project_id"],
    gcp_location=config["gcp_location"],
)

# Initialize the Local Experiment Handler
print("Initializing LocalExperimentHandler")
experiment_handler = LocalExperimentHandler()

# %% [markdown]
# ## Set Up Parameters for Orchestration

# %%
# Create arguments dictionary for the orchestrator
args = {
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "prompt": PROMPT,
}

# %% [markdown]
# ## Execute the Orchestration

# %%
print("\n=== Executing Image Generation ===")
print(f"Running experiment '{EXPERIMENT_RUN_NAME}' with prompt: '{PROMPT}'")

# Execute the image generation
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

# %% [markdown]
# ## Display Results

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