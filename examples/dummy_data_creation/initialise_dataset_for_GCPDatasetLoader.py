# %% [markdown]
# # Initialize Dataset for Pixaris GCP Data Loader
#
# This script initializes a dataset in Google Cloud Platform (GCP) for use with the Pixaris GCPDatasetLoader.
# It connects to your GCP project and creates the necessary dataset structure in your specified GCP bucket.
#
# ## Prerequisites
# - A local dataset must exist first (create one using create_dummy_dataset_for_Generator_locally.py or create your own dataset locally)
# - config.yaml file with GCP credentials and bucket information
#
# ## What this script does:
# 1. Loads GCP configuration from config.yaml
# 2. Creates a GCPDatasetLoader instance
# 3. Initializes the dataset structure in your GCP bucket


# %% [markdown]
# ## Import Libraries and Load Configuration

# %%
import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader

# %%
config = yaml.safe_load(open("config.yaml", "r"))

# %% [markdown]
# ## Configuration Parameters

# %%
# Make sure a dataset exists locally, how to create one you can find in
# dummy_data_creation/create_dummy_dataset_for_Generator_locally.py
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name

# %% [markdown]
# ## Initialize GCP Dataset Loader and Create Dataset

# %%

data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
)

print(f"Creating dataset '{DATASET}' in project '{PROJECT}' on GCP...")
data_loader.create_dataset(project=PROJECT, dataset=DATASET)
print("Dataset initialization completed successfully!")
