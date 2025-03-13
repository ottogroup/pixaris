import os
import yaml
from PIL import Image
from pixaris.generation.comfyui import ComfyGenerator

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
WORKFLOW_PATH = os.getcwd() + "/test/assets/test-background-generation.json"

# +
generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)

args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "pillow_images": [
        {
            "node_name": "Load Input Image",
            "pillow_image": Image.open("eval_data/test_eval_set/input/model_01.png"),
        },
        {
            "node_name": "Load Mask Image",
            "pillow_image": Image.open("eval_data/test_eval_set/mask/model_01.png"),
        },
    ],
    "generation_params": [],
}
# -

image, name = generator.generate_single_image(args)
image.show()
