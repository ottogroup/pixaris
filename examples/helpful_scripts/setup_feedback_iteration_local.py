import os
from pixaris.feedback_handlers.local import LocalFeedbackHandler

# ### Create Feedback Iteration
feedback_handler = LocalFeedbackHandler()
project = "dummy_project"
dataset = "dummy_dataset"
experiment_name = "example_run_name"
feedback_iteration = "feedback_iteration_name"
images_directory = os.path.join("local_results", project, dataset, experiment_name)

feedback_handler.create_feedback_iteration(
    experiment_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
    dataset=dataset,  # optional
    experiment_name=experiment_name,  # optional
)
