# %% [markdown]
# # Local Experiment with GeminiGenerator and Local Experiment Handling
#
# This script demonstrates how to run experiments using Pixaris with:
# - GCPDatasetLoader for loading data from Google Cloud
# - GeminiGenerator for generating images using Gemini AI model
# - LocalExperimentHandler for storing experiment results locally
#
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml

# %% [markdown]
# ## Import Libraries and Setup

# %%
import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.gemini import GeminiGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset

print(f"Current working directory: {__import__('os').getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name
EXPERIMENT_RUN_NAME = "example-run"  # Name of this experiment run
MODEL_NAME = "gemini-2.0-flash-exp"  # Gemini model to use
PROMPT = (
    "Generate a background for this woman. She should be standing on a beautiful beach."
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

# Initialize the GeminiGenerator
print(f"Initializing GeminiGenerator with model '{MODEL_NAME}'")
generator = GeminiGenerator(
    gcp_project_id=config["gcp_project_id"],
    gcp_location="us-central1",  # setting this as us-central1 for now, since model not currently available in europe
    model_name=MODEL_NAME,
    verbose=True,
)

# Initialize the Local Experiment Handler
print("Initializing LocalExperimentHandler")
experiment_handler = LocalExperimentHandler()

# %% [markdown]
# ## Set Up Parameters for Orchestration

# %%
# Create arguments dictionary for the orchestrator
args = {
    "prompt": PROMPT,
    "model_name": MODEL_NAME,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    # how many parallel jobs to run. If you want to parallelize calls to the API, set this to a number > 1
    "max_parallel_jobs": 1,
}

# %% [markdown]
# ## Execute the Orchestration

# %%
print("\n=== Executing Image Generation ===")
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
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
