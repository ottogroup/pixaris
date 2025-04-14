from pixaris.feedback_handlers.local import LocalFeedbackHandler

# ### Create Feedback Iteration
feedback_handler = LocalFeedbackHandler()
project = "dummy_project"
feedback_iteration = "dummy_feedback_iteration"
local_image_directory = "path_to_local_directory_containing_images"

feedback_handler.create_feedback_iteration(
    local_image_directory=local_image_directory,
    project=project,
    feedback_iteration=feedback_iteration,
    dataset=None,  # optional
    experiment_name=None,  # optional
)
