import yaml
from pixaris.data_loaders.gcp import GCPDatasetLoader

config = yaml.safe_load(open("config.yaml", "r"))

# Make sure a dataset exists locally, how to create one you can find in
# dummy_data_creation/create_dummy_dataset_for_Generator_locally.py
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name

data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
    force_download=False,
)

data_loader.create_dataset()
