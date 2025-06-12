# %% [markdown]
# # Parallelised Orchestration with Local Components and Flux Integration
#
# This script demonstrates how to run parallelised experiments using Pixaris with local components:
# - LocalDatasetLoader for loading data from the local filesystem
# - FluxFillGenerator for generating images using the Flux API
# - LocalExperimentHandler for storing experiment results locally
# - Parallelised orchestration for efficient processing
#
# ## Requirements
# - pixaris package installed
# - Valid Flux API key in config.yaml
# - Test assets available in the project structure

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
from pixaris.data_loaders.local import LocalDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.flux import FluxFillGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
config = yaml.safe_load(open("config.yaml", "r"))

# Set your API Key for Flux
os.environ["BFL_API_KEY"] = config["bfl_api_key"]

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name
PROMPT = "An animal on a beach"  # The prompt to use for generation
EXPERIMENT_RUN_NAME = "example-flux"  # Name of this experiment run

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

# Initialize the FluxFillGenerator
print("Initializing FluxFillGenerator")
generator = FluxFillGenerator()

# Initialize the Local Experiment Handler
print("Initializing LocalExperimentHandler")
experiment_handler = LocalExperimentHandler()

# %% [markdown]
# ## Set Up Parameters for Orchestration

# %%
# Create arguments dictionary for the orchestrator
args = {
    "generation_params": [
        {
            "node_name": "prompt",
            "input": "prompt",
            "value": PROMPT,
        },
    ],
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    "max_parallel_jobs": 2,  # how many parallel jobs/calls to API to run
}

# %% [markdown]
# ## Execute the Orchestration

# %%
print("\n=== Executing Parallelized Orchestration ===")
# Execute the image generation process
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
