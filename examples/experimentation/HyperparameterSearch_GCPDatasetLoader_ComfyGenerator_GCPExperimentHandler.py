# %% [markdown]
# # Hyperparameter Search with ComfyGenerator and GCP Integration
# 
# This script demonstrates how to run hyperparameter search experiments using Pixaris with GCP integration:
# - GCPDatasetLoader for loading data from Google Cloud
# - ComfyGenerator for generating images using ComfyUI 
# - GCPExperimentHandler for storing experiment results in Google Cloud
# 
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml
# - Test assets available in the project structure

# %% [markdown]
# ## Import Libraries and Setup

# %%
# Set DEV_MODE to true if you want to work locally with 8188 port
# This must be set before importing from pixaris
import os
os.environ["DEV_MODE"] = "true"

import json
import yaml
from PIL import Image
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name
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
print("\n=== Initializing Components ===")

# Initialize the GCP Dataset Loader
print(f"Initializing GCPDatasetLoader for project '{PROJECT}', dataset '{DATASET}'")
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
    force_download=False,
)

# Initialize the ComfyGenerator
print("Initializing ComfyGenerator")
generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

# Initialize the GCP Experiment Handler
print("Initializing GCPExperimentHandler")
experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# %% [markdown]
# ## Set Up Parameters for Hyperparameter Search

# %%
# Create arguments dictionary for the orchestrator
print("Setting up hyperparameter search parameters")
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "hyperparameters": [
        {
            "node_name": "KSampler (Efficient) - Generation",
            "input": "steps",
            "value": [10, 15],
        },
        {
            "node_name": "KSampler (Efficient) - Generation",
            "input": "sampler_name",
            "value": ["euler_ancestral", "euler"],
        },
    ],
}

# %% [markdown]
# ## Execute the Hyperparameter Search

# %%
print("\n=== Executing Hyperparameter Search ===")
print(f"Running hyperparameter search for experiment '{EXPERIMENT_RUN_NAME}'")
print(f"Testing {len(args['hyperparameters'])} hyperparameter groups")

# Execute the hyperparameter search
out = generate_images_for_hyperparameter_search_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

print(f"Hyperparameter search completed successfully!")
print(f"Check results using the experiment run name: {EXPERIMENT_RUN_NAME}")

# ## Next Steps
# 
# After execution:
# 1. Generated images are stored in the specified GCP bucket.
# 2. Experiment metadata are stored in Google BigQuery.
# 3. View results in the Pixaris UI 

# %%