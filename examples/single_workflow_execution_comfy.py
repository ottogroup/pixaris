import os
import yaml
from pixaris.data_loaders.google import GCPDatasetLoader
from pixaris.generation.comfyui import ComfyGenerator

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "test_eval_set"
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
            "image_path": "eval_data/test_eval_set/input/model_01.png",
        },
        {
            "node_name": "Load Mask Image",
            "image_path": "eval_data/test_eval_set/mask/model_01.png",
        },
    ],
    "generation_params": [],
}

image, name = generator.generate_single_image(args)
image.show()
