# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: pixaris-cO8jBQMx-py3.12
#     language: python
#     name: python3
# ---

# %%
from google.cloud import aiplatform
import yaml

config = yaml.safe_load(open("pixaris/config.yaml"))

PROJECT_ID = config["gcp_project_id"]
LOCATION = config["gcp_location"]
aiplatform.init(project=PROJECT_ID, location=LOCATION)
# Get tensorboard instances
all_tensorboard_instances = aiplatform.Tensorboard.list(
    project=PROJECT_ID, location=LOCATION
)

# %%
# HERE YOU CAN CHANGE THE INSTANCE IF YOU DONT WANT THE DEFAULT / FIRST ONE
my_instance_index = 0

# get resource and name
instance = all_tensorboard_instances[my_instance_index]
instance_resource_name = instance.resource_name.split("/")[-1]
print("Instance Resource Name: ", instance_resource_name)
tensorboard_instance = aiplatform.Tensorboard(
    project=PROJECT_ID, location=LOCATION, tensorboard_name=instance_resource_name
)
print(tensorboard_instance)

# %%
# Display experiments with their respective index
tensorboard_experiments = aiplatform.TensorboardExperiment.list(
    tensorboard_name=tensorboard_instance.resource_name
)
for idx, experiment in enumerate(tensorboard_experiments):
    print(f"Experiment {experiment.display_name.split("/")[-1]} has index {idx}")

# %%
# HERE SELECT THE EXPERIMENT YOU WANT TO USE
my_experiment_index = 2

tensorboard_experiment = tensorboard_experiments[my_experiment_index]
print(
    f"In the next step you will delete all runs within experiment ------- {tensorboard_experiment.display_name.split("/")[-1]} --------"
)
print("ARE YOU SURE YOU WANT TO DELETE ALL RUNS WITHIN THIS EXPERIMENT?")

# %%
# CAUTION! This will delete all runs within the experiment. Delete single runs in the UI!
if False:
    tensorboard_experiment.delete()
