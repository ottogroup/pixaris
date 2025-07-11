# %% [markdown]
# # Deploy Pixaris Frontend Locally with Local Data Handling
#
# This script demonstrates how to deploy the Pixaris UI locally with local data handling:
# - LocalFeedbackHandler for storing feedback locally
# - LocalExperimentHandler for handling experiment data locally
# - Local UI server for interacting with the system
#
# ## Requirements
# - pixaris package installed
# - Valid configuration in config.yaml

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
from pixaris.frontend.main import launch_ui
from pixaris.feedback_handlers.local import LocalFeedbackHandler
from pixaris.experiment_handlers.local import LocalExperimentHandler

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
print("\n=== Loading Configuration ===")
config = yaml.safe_load(open("config.yaml", "r"))

# Note: To create dummy data for the frontend:
# Run examples/dummy_data_creation/create_dummy_data_for_frontend_locally.py

# %% [markdown]
# ## Initialize Components

# %%
print("\n=== Initializing Components ===")

# Initialize the Local Feedback Handler
print("Initializing LocalFeedbackHandler")
feedback_handler = LocalFeedbackHandler()

# Initialize the Local Experiment Handler
print("Initializing LocalExperimentHandler")
experiment_handler = LocalExperimentHandler()

# %% [markdown]
# ## Launch the UI

# %%
print("\n=== Launching Pixaris UI ===")
print("Starting local UI server with local data handling")
launch_ui(feedback_handler, experiment_handler)
