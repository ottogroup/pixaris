import PIL
from pixaris.data_loaders.google import GCPDatasetLoader
from pixaris.data_writers.tensorboard import TensorboardWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.llm import LLMMetric
from pixaris.orchestration.base import generate_images_based_on_eval_set
import os
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
EVAL_SET = "z_test_correct"
WORKFLOW_PATH = os.getcwd() + "/test/assets/test_inspo_apiformat.json"
WORKFLOW_IMAGE_PATH = os.getcwd() + "/test/assets/test-just-load-and-save.png"

# Define the dataset Loader
loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_bucket_name=config["gcp_bucket_name"],
    eval_set=EVAL_SET,
    eval_dir_local="eval_data",
)

# Define the Generator
comfy_generator = ComfyGenerator(workflow_apiformat_path=WORKFLOW_PATH)
writer = TensorboardWriter(
    project_id=config["gcp_project_id"],
    location=config["gcp_location"],
    bucket_name=config["gcp_bucket_name"],
)

# Define Metrics and all nessecary images to run these metrics
object_dir = "test/test_eval_data/mock/Input/"
object_images = [PIL.Image.open(object_dir + image) for image in os.listdir(object_dir)]
style_images = [PIL.Image.open("test/assets/test_inspo_image.jpg")] * len(object_images)
llm_metric = LLMMetric(
    object_images=object_images,
    style_images=style_images,
)

# Define args for additional info
args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "image_paths": [
        {
            "node_name": "Load Inspo Image",
            "image_path": "test/assets/test_inspo_image.jpg",
        }
    ],
    "run_name": "example_run_metrics_5",
}

# execute
out = generate_images_based_on_eval_set(
    data_loader=loader,
    image_generator=comfy_generator,
    data_writer=writer,
    metrics=[llm_metric],
    args=args,
)

out
