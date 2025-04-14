import json
import unittest

from pixaris.feedback_handlers.local import LocalFeedbackHandler
import shutil
import os


def copy_test_project():
    source_dir = os.path.join(os.path.dirname(__file__), "../test_results/")
    destination_dir = os.path.join("temp_test_files")

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)


def tearDown():
    # Remove the temporary directory after each test
    if os.path.exists("temp_test_files"):
        shutil.rmtree("temp_test_files")


class TestLocalFeedbackHandler(unittest.TestCase):
    def test_write_single_feedback(self):
        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory="temp_test_files",
        )

        copy_test_project()

        # Create a mock feedback dictionary
        feedback = {
            "project": "test_project",
            "feedback_iteration": "test_iteration",
            "dataset": "test_dataset",
            "image_name": "test_image.jpg",
            "experiment_name": "test_experiment",
            "feedback_indicator": "Like",
            "comment": "Great image!",
        }

        # Call the method to test
        local_feedback_handler.write_single_feedback(feedback)

        # check if the feedback was written to the correct file
        feedback_file_path = "temp_test_files/test_project/feedback_tracking.jsonl"
        self.assertTrue(os.path.exists(feedback_file_path))

        # check if the feedback was written correctly
        with open(feedback_file_path, "r") as f:
            lines = f.readlines()
            last_line = json.loads(lines[-1])
            self.assertEqual(last_line["project"], feedback["project"])
            self.assertEqual(
                last_line["feedback_iteration"], feedback["feedback_iteration"]
            )
            self.assertEqual(last_line["dataset"], feedback["dataset"])
            self.assertEqual(last_line["image_name"], feedback["image_name"])
            self.assertEqual(last_line["experiment_name"], feedback["experiment_name"])
            self.assertEqual(last_line["likes"], 1)
            self.assertEqual(last_line["dislikes"], 0)
            self.assertEqual(last_line["comment"], feedback["comment"])

        tearDown()

    def test_load_projects_list(self):
        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory="temp_test_files",
        )

        copy_test_project()

        # Call the method to test
        projects = local_feedback_handler.load_projects_list()

        # Check if the projects list is correct
        self.assertEqual(projects, ["test_project"])

        tearDown()

    def test_load_all_feedback_iterations_for_project(self):
        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory="temp_test_files",
        )

        copy_test_project()

        # Call the method to test
        local_feedback_handler.load_all_feedback_iterations_for_project("test_project")

        # Check if the iterations list is correct
        self.assertEqual(
            local_feedback_handler.feedback_iteration_choices, ["test_iteration"]
        )

        tearDown()

    def test_load_images_for_feedback_iteration(self):
        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory="temp_test_files",
        )

        copy_test_project()

        # load the project into df
        local_feedback_handler.load_all_feedback_iterations_for_project("test_project")

        # Call the method to test
        image_names = local_feedback_handler.load_images_for_feedback_iteration(
            "test_iteration"
        )

        # Check if the images list is correct
        self.assertEqual(
            image_names,
            [
                "temp_test_files/test_project/feedback_iterations/test_iteration/chinchilla.jpg",
                "temp_test_files/test_project/feedback_iterations/test_iteration/sillygoose.jpg",
            ],
        )

        tearDown()


if __name__ == "__main__":
    unittest.main()
