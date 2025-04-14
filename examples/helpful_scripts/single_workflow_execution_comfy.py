import os
import yaml
from PIL import Image
from pixaris.generation.comfyui import ComfyGenerator
import json

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
WORKFLOW_APIFORMAT_JSON = json.load(
    os.getcwd() + "/test/assets/test-background-generation.json"
)

# +
generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "pillow_images": [
        {
            "node_name": "Load Input Image",
            "pillow_image": Image.open(
                "local_experiment_inputs/dummy_project/dummy_dataset/input/chinchilla.png"
            ),
        },
        {
            "node_name": "Load Mask Image",
            "pillow_image": Image.open(
                "local_experiment_inputs/ummy_project/dummy_dataset/mask/chinchilla.png"
            ),
        },
    ],
    "generation_params": [],
}
# -

image, name = generator.generate_single_image(args)
image.show()
