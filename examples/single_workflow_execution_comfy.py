import os
import yaml
from pixaris.generation.comfyui import ComfyGenerator

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"

# +
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
# -

image, name = generator.generate_single_image(args)
image.show()
