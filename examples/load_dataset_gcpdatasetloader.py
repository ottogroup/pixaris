import yaml
from pixaris.data_loaders.google import GCPDatasetLoader

config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# eval set is downloaded upon initialisation
loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set="z_test_correct",
    eval_dir_local="eval_data",
)

print("done")
