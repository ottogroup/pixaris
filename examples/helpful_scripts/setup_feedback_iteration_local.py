import os
from pixaris.feedback_handlers.local import LocalFeedbackHandler

# ### Create Feedback Iteration
feedback_handler = LocalFeedbackHandler()
project = "test_project"
dataset = "mock"
experiment_name = "20250411-103343_example-run"
feedback_iteration = "test_feedback_iteration_01"
images_directory = os.path.join("local_results", project, dataset, experiment_name)

feedback_handler.create_feedback_iteration(
    experiment_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
    dataset=dataset,  # optional
    experiment_name=experiment_name,  # optional
)
