# %% [markdown]
# # Hyperparameter Search with FluxGenerator and GCP Integration
# 
# This script demonstrates how to run hyperparameter search experiments using Pixaris with GCP integration:
# - GCPDatasetLoader for loading data from Google Cloud
# - FluxFillGenerator for generating images using Beautiful.AI Flux
# - GCPExperimentHandler for storing experiment results in Google Cloud
# - Hyperparameter search for exploring different parameter combinations
# 
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml
# - Beautiful.AI Flux API key in config.yaml

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import (
    generate_images_for_hyperparameter_search_based_on_dataset,
)

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
config = yaml.safe_load(open("pixaris/config.yaml", "r"))
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name
EXPERIMENT_RUN_NAME = "example-flux"  # Name of this experiment run

# Define hyperparameter search values
PROMPT_1 = "A beautiful woman in the desert"
PROMPT_2 = "A beautiful woman on a moon"

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

# Initialize the FluxFillGenerator
print("Initializing FluxFillGenerator")
generator = FluxFillGenerator()

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
# Create arguments dictionary for hyperparameter search
print("\n=== Configuring Hyperparameter Search ===")
print(f"Experiment run name: {EXPERIMENT_RUN_NAME}")
print(f"Testing prompts: {PROMPT_1}, {PROMPT_2}")

args = {
    "hyperparameters": [
        {
            "node_name": "prompt",
            "input": "prompt",
            "value": [PROMPT_1, PROMPT_2],
        },
    ],
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

# %% [markdown]
# ## Execute the Hyperparameter Search

# %%
print("\n=== Executing Hyperparameter Search ===")
print("Running generation with multiple prompts...")

out = generate_images_for_hyperparameter_search_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

print(f"\n=== Experiment Completed ===")

# %% [markdown]
# ## Next Steps
# 
# After execution:
# 1. Generated images are stored in the specified GCP bucket.
# 2. Experiment metadata are stored in Google BigQuery.
# 3. View results in the Pixaris UI 