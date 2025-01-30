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

args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "image_paths": [
        {
            "node_name": "Load Input Image",
            "image_path": "eval_data/z_test_correct/Input/model_90310595.jpg",
        },
        {
            "node_name": "Load Mask Image",
            "image_path": "eval_data/z_test_correct/Mask/model_90310595.jpg",
        },
    ],
    "generation_params": [],
}

out = generator.generate_single_image(args)
out.show()
