# %% [markdown]
# # Deploy Pixaris Frontend Locally with GCP Integration
#
# This script demonstrates how to deploy the Pixaris UI locally while using GCP for data handling:
# - GCPFeedbackHandler for storing feedback in Google Cloud
# - GCPExperimentHandler for handling experiment data from Google Cloud
# - Local UI server for interacting with the system
#
# ## Requirements
# - pixaris package installed
# - Valid GCP configuration in pixaris/config.yaml
# - GCP resources properly configured (BigQuery tables, GCS buckets)

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler
from pixaris.frontend.main import launch_ui
from pixaris.experiment_handlers.gcp import GCPExperimentHandler

print(f"Current working directory: {os.getcwd()}")

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration from config file
print("\n=== Loading Configuration ===")
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Note: To create dummy data for the frontend:
# Run examples/dummy_data_creation/create_dummy_data_for_frontend_in_GCP.py

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

# Initialize the GCP Experiment Handler
print("Initializing GCPExperimentHandler")
experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# %% [markdown]
# ## Launch the UI

# %%
print("\n=== Launching Pixaris UI ===")
print("Starting local UI server with GCP integration")
launch_ui(feedback_handler, experiment_handler)
