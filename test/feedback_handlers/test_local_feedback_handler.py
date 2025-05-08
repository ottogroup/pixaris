import json
import unittest

from pixaris.feedback_handlers.local import LocalFeedbackHandler
import shutil
import os

TEMP_TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "../../temp_test_files")


def copy_test_results():
    """
    Copy the test results to a temporary location for testing.
    """
    source_dir = os.path.join(os.path.dirname(__file__), "../test_results/")
    destination_dir = TEMP_TEST_FILES_DIR

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)


def copy_test_project():
    """
    Copy the test project to a temporary location for testing.
    """
    source_dir = os.path.join(os.path.dirname(__file__), "../test_project/")
    destination_dir = TEMP_TEST_FILES_DIR
    destination_dir = os.path.join(TEMP_TEST_FILES_DIR, "test_project")

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)


def tearDown():
    """
    Remove the temporary directory after each test.
    """
    # Remove the temporary directory after each test
    if os.path.exists(TEMP_TEST_FILES_DIR):
        shutil.rmtree(TEMP_TEST_FILES_DIR)


class TestLocalFeedbackHandler(unittest.TestCase):
    def test_write_single_feedback(self):
        """
        tests the write_single_feedback method of the LocalFeedbackHandler class
        checks if the feedback was written correctly.
        """
        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        copy_test_results()

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
        feedback_file_path = (
            "temp_test_files/test_project/feedback_iterations/feedback_tracking.jsonl"
        )
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

    def test_save_images_to_feedback_iteration_folder(self):
        """
        tests the _save_images_to_feedback_iteration_folder method of the LocalFeedbackHandler class
        checks if the images are at the correct location.
        """
        copy_test_project()

        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        local_feedback_handler._save_images_to_feedback_iteration_folder(
            local_image_directory="temp_test_files/test_project/mock/input",
            project="test_project",
            feedback_iteration="test_iteration",
        )

        # Check if the images were saved correctly
        feedback_iteration_dir = os.path.join(
            TEMP_TEST_FILES_DIR,
            "test_project",
            "feedback_iterations",
            "test_iteration",
        )
        self.assertTrue(os.path.exists(feedback_iteration_dir))
        self.assertTrue(
            os.path.exists(os.path.join(feedback_iteration_dir, "chinchilla.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(feedback_iteration_dir, "sillygoose.png"))
        )
        tearDown()

    def test_initialise_feedback_iteration_in_table(self):
        """
        tests the _initialise_feedback_iteration_in_table method of the LocalFeedbackHandler class
        checks if the feedback iteration table was initialized correctly.
        """
        copy_test_results()
        os.remove(
            os.path.join(
                TEMP_TEST_FILES_DIR,
                "test_project",
                "feedback_iterations",
                "feedback_tracking.jsonl",
            )
        )

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # Call the method to test
        local_feedback_handler._initialise_feedback_iteration_in_table(
            "test_project",
            "test_iteration",
            ["cat.png", "chinchilla.png", "doggo.png", "sillygoose.png"],
        )

        # Check if the feedback iteration was initialized correctly
        feedback_file_path = (
            "temp_test_files/test_project/feedback_iterations/feedback_tracking.jsonl"
        )
        self.assertTrue(os.path.exists(feedback_file_path))

        # Check if the feedback iteration was initialized correctly
        with open(feedback_file_path, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 4)

        tearDown()

    def test_create_feedback_iteration(self):
        """
        tests the create_feedback_iteration method of the LocalFeedbackHandler class
        checks if images are copied correctly and if the feedback iteration table was created correctly.

        combined functionality from _save_images_to_feedback_iteration_folder and
        _initialise_feedback_iteration_in_table
        """
        copy_test_project()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # Call the method to test
        local_feedback_handler.create_feedback_iteration(
            local_image_directory="temp_test_files/test_project/mock/input",
            project="test_project",
            feedback_iteration="test_iteration",
            date_suffix="010101",
        )

        # Check if the feedback iteration was created correctly
        feedback_file_path = (
            "temp_test_files/test_project/feedback_iterations/feedback_tracking.jsonl"
        )
        self.assertTrue(os.path.exists(feedback_file_path))

        # Check if the feedback iteration was created correctly
        with open(feedback_file_path, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 4)
            self.assertIn("test_project", lines[0])
            self.assertIn("010101_test_iteration", lines[0])

        feedback_iteration_dir = (
            "temp_test_files/test_project/feedback_iterations/010101_test_iteration"
        )
        self.assertTrue(
            os.path.exists(os.path.join(feedback_iteration_dir, "sillygoose.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(feedback_iteration_dir, "doggo.png"))
        )

        tearDown()

    def test_load_projects_list(self):
        """
        tests the load_projects_list method of the LocalFeedbackHandler class
        checks if the projects list is correct.
        """
        copy_test_project()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # Call the method to test
        projects = local_feedback_handler.load_projects_list()

        # Check if the projects list is correct
        self.assertEqual(projects, ["test_project"])

        tearDown()

    def test_load_all_feedback_iterations_for_project(self):
        """
        tests the load_all_feedback_iterations_for_project method of the LocalFeedbackHandler class
        checks if the feedback iterations list is correct.
        """
        copy_test_results()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # Call the method to test
        local_feedback_handler.load_all_feedback_iterations_for_project("test_project")

        # Check if the iterations list is correct
        self.assertEqual(
            local_feedback_handler.feedback_iteration_choices, ["test_iteration"]
        )

        tearDown()

    def test_load_images_for_feedback_iteration_sorting_image_name(self):
        """
        tests the load_images_for_feedback_iteration method of the LocalFeedbackHandler class
        checks if the images list is correct for sorting after name.
        There are only 2 images in the feedback iteration file, even though there are 4 in the dir.
        """
        copy_test_results()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

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
                f"{TEMP_TEST_FILES_DIR}/test_project/feedback_iterations/test_iteration/chinchilla.jpg",
                f"{TEMP_TEST_FILES_DIR}/test_project/feedback_iterations/test_iteration/sillygoose.jpg",
            ],
        )

        tearDown()

    def test_load_images_for_feedback_iteration_sorting_dislikes(self):
        """
        tests the load_images_for_feedback_iteration method of the LocalFeedbackHandler class
        checks if the images list is correct for sorting after dislikes. Sorting for likes is implemented
        exactly the same way.
        """
        copy_test_results()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # load the project into df
        local_feedback_handler.load_all_feedback_iterations_for_project("test_project")

        # Call the method to test
        image_names = local_feedback_handler.load_images_for_feedback_iteration(
            "test_iteration",
            sorting="dislikes",
        )

        # Check if the images list is correct
        self.assertEqual(
            image_names,
            [
                f"{TEMP_TEST_FILES_DIR}/test_project/feedback_iterations/test_iteration/sillygoose.jpg",
                f"{TEMP_TEST_FILES_DIR}/test_project/feedback_iterations/test_iteration/chinchilla.jpg",
            ],
        )

        tearDown()

    def test_load_feedback_per_image(self):
        """
        tests the load_feedback_per_image method of the LocalFeedbackHandler class
        checks if the feedback per image is correct.
        """
        copy_test_results()

        # Create a mock feedback handler
        local_feedback_handler = LocalFeedbackHandler(
            project_feedback_dir="feedback_iterations",
            project_feedback_file="feedback_tracking.jsonl",
            local_feedback_directory=TEMP_TEST_FILES_DIR,
        )

        # load the project into df
        local_feedback_handler.load_all_feedback_iterations_for_project("test_project")

        # Call the method to test
        feedback = local_feedback_handler.get_feedback_per_image(
            "test_iteration", "chinchilla.jpg"
        )

        # Check if the feedback is correct
        self.assertEqual(feedback["likes"], 2)
        self.assertEqual(feedback["dislikes"], 0)
        self.assertEqual(feedback["comments_liked"], ["yes", "yess"])
        self.assertEqual(feedback["comments_disliked"], [])

        tearDown()

if __name__ == "__main__":
    unittest.main()
