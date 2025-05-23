from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.gemini import GeminiGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset
import yaml

config = yaml.safe_load(open("pixaris/config.yaml", "r"))
PROJECT = "dummy_project"
DATASET = "dummy_dataset"
EXPERIMENT_RUN_NAME = "example-run"
MODEL_NAME = "gemini-2.0-flash-exp"
PROMPT = (
    "Generate a background for this woman. She should be standing on a beautiful beach."
)

# +
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
    force_download=False,
)

generator = GeminiGenerator(
    gcp_project_id=config["gcp_project_id"],
    gcp_location="us-central1",  # seeting this as us-central1 for now, since model not currently available in europe
    model_name=MODEL_NAME,
    verbose=True,
)

experiment_handler = LocalExperimentHandler()

args = {
    "workflow_apiformat_json": {},
    "workflow_pillow_image": {},
    "prompt": PROMPT,
    "model_name": MODEL_NAME,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
    # how many parallel jobs to run. If you want to parallelize calls to the API, set this to a number > 1
    "max_parallel_jobs": 1,
}

# execute
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

out[0][0].show()
