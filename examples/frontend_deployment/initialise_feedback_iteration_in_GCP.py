# %% [markdown]
# # Initialize Feedback Iteration in Google Cloud Platform (GCP)
#
# This script creates a new feedback iteration in GCP using the GCPFeedbackHandler:
# - Loads configuration from the config.yaml file
# - Uploads images from a local directory to GCP for use in the Pixaris feedback interface
# - Creates a structured feedback iteration in GCP
#
# ## Requirements
# - pixaris package installed
# - Valid GCP credentials configured
# - config.yaml with GCP settings (project_id, bucket_name, etc.)
# - Local directory containing images for feedback

# %% [markdown]
# ## Import Libraries and Setup

# %%
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler
import os
import yaml

print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
print("\n=== Loading Configuration ===")
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Note: For dummy data examples, see: examples/dummy_data_creation

# Define project-specific parameters
print("\n=== Setting Project Parameters ===")
PROJECT = "examples_for_readme"  # Your project name
FEEDBACK_ITERATION = "other_feedback_iteration"  # Name of this feedback iteration
LOCAL_IMAGE_DIRECTORY = "local_results/examples_for_readme/250605-example-2/generated_images"  # change this to the path of the folder that contains the images you want to add to the new feedback iteration.

# %% [markdown]
# ## Initialize Components

# %%
print("\n=== Initializing Components ===")

# Initialize the GCP Feedback Handler
print("Initializing GCPFeedbackHandler")
feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# %% [markdown]
# ## Create Feedback Iteration

# %%
print("\n=== Creating Feedback Iteration ===")
print(f"Project: {PROJECT}")
print(f"Feedback Iteration: {FEEDBACK_ITERATION}")
print(f"Local Image Directory: {LOCAL_IMAGE_DIRECTORY}")

# Create feedback iteration with the provided parameters
feedback_handler.create_feedback_iteration(
    local_image_directory=LOCAL_IMAGE_DIRECTORY,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)

print("Feedback iteration created successfully in GCP.")
