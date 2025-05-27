# %% [markdown]
# # Initialize Feedback Iteration Locally
#
# This script demonstrates how to create a new feedback iteration using the LocalFeedbackHandler:
# - LocalFeedbackHandler for managing feedback data locally
# - Processes images from a local directory for use in the Pixaris feedback interface
# - Stores feedback data in local files
#
# ## Requirements
# - pixaris package installed
# - config.yaml file
# - Local directory containing images for feedback

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
from pixaris.feedback_handlers.local import LocalFeedbackHandler

print(f"Current working directory: {os.getcwd()}")

# Optional: Adjust working directory if running from a notebook
if False:  # set to True if executing from notebook
    os.chdir("../../")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
print("\n=== Loading Configuration ===")
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
FEEDBACK_ITERATION = "dummy_feedback_iteration"  # Name of this feedback iteration
LOCAL_IMAGE_DIRECTORY = (
    "local_results/dummy_project/feedback_iterations/250428_dummy_feedback_iteration"
)

# Note: For dummy data examples, see: examples/dummy_data_creation

# %% [markdown]
# ## Initialize Components

# %%
print("\n=== Initializing Components ===")

# Initialize the Local Feedback Handler
print("Initializing LocalFeedbackHandler")
feedback_handler = LocalFeedbackHandler()

# %% [markdown]
# ## Create Feedback Iteration

# %%
print("\n=== Creating Feedback Iteration ===")

# Create feedback iteration with the provided parameters
feedback_handler.create_feedback_iteration(
    local_image_directory=LOCAL_IMAGE_DIRECTORY,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)

print("\n=== Feedback Iteration Created Successfully ===")
