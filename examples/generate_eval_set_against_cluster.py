import os
import yaml
from pixaris.data_loaders.google import GCPDatasetLoader
from pixaris.generation.comfyui import ComfyGenerator

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "z_test_correct"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"

loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)
generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)

# Case
# - One Workflow
# - Two Images
# - Two Instances

# Step 1: Connect to Cluster
# gcloud container clusters get-credentials cluster --zone europe-west4-a --project oghub-paws-b-d

# Step 2: Adapt Workflow? (optional?)

# Step 3: Upload Images and workflow to Bucket

# Step 4: Parallelize (inputs: path to images und workflows in the buckets)
# Step 4a: Download Images and Workflow to selected instance
# Step 4b: Run Image Workflow
# Step 4c: Download/Save Image


args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "image_paths": [
        {
            "node_name": "Load Input Image",
            "image_path": "eval_data/z_test_correct/Input/model_01.png",
        },
        {
            "node_name": "Load Mask Image",
            "image_path": "eval_data/z_test_correct/Mask/model_01.png",
        },
    ],
    "generation_params": [],
}

image, name = generator.generate_single_image(args)
image, name.show()
