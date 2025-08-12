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
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Current working directory: %s", os.getcwd())

# Optional: Adjust working directory if running from a notebook
if False:  # set to True if executing from notebook
    os.chdir("../../")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
logger.info("\n=== Loading Configuration ===")
config = yaml.safe_load(open("config.yaml", "r"))

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
FEEDBACK_ITERATION = "dummy_feedback_iteration"  # Name of this feedback iteration
LOCAL_IMAGE_DIRECTORY = "local_results/dummy_project/feedback_iterations/feedback_iteration_with_dummy_images"  # change this to the path of the folder that contains the images you want to add to the new feedback iteration.

# Note: For dummy data examples, see: examples/dummy_data_creation

# %% [markdown]
# ## Initialize Components

# %%
logger.info("\n=== Initializing Components ===")

# Initialize the Local Feedback Handler
logger.info("Initializing LocalFeedbackHandler")
feedback_handler = LocalFeedbackHandler()

# %% [markdown]
# ## Create Feedback Iteration

# %%
logger.info("\n=== Creating Feedback Iteration ===")

# Create feedback iteration with the provided parameters
feedback_handler.create_feedback_iteration(
    local_image_directory=LOCAL_IMAGE_DIRECTORY,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)

logger.info("\n=== Feedback Iteration Created Successfully ===")
