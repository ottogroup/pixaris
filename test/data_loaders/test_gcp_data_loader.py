import unittest
from unittest.mock import patch
import shutil
import os

from pixaris.data_loaders.gcp import GCPDatasetLoader


def copy_test_project():
    # Copy the test project to a temporary location
    test_project_path = os.path.join(os.getcwd(), "test", "test_project")
    temp_test_project_path = os.path.join(
        os.getcwd(), "temp_test_files", "test_project"
    )

    if os.path.exists(temp_test_project_path):
        shutil.rmtree(temp_test_project_path)

    shutil.copytree(test_project_path, temp_test_project_path)


def tearDown():
    # Remove the temporary directory after each test
    temp_test_project_path = os.path.join(os.getcwd(), "temp_test_files")
    if os.path.exists(temp_test_project_path):
        shutil.rmtree(temp_test_project_path)


class TestLocalDataset(unittest.TestCase):
    def mock_download(self):
        self.image_dirs = ["input", "mask"]

    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader._download_dataset", mock_download)
    def test_load_dataset(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="mock",
            eval_dir_local="temp_test_files",
        )
        dataset = loader.load_dataset()
        print(dataset)
        self.assertEqual(len(dataset), 4)
        for entry in dataset:
            self.assertIn("pillow_images", entry)
            paths = entry["pillow_images"]
            for path in paths:
                self.assertIn("node_name", path)
                self.assertIn("pillow_image", path)

        # Clean up the temporary directory
        tearDown()

    def test_decide_if_download_needed_force_download(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="mock",
            eval_dir_local="temp_test_files",
            force_download=True,
        )
        self.assertTrue(loader._decide_if_download_needed())

        # Clean up the temporary directory
        tearDown()

    def test_decide_if_download_needed_empty_local_dir(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="empty",
            eval_dir_local="temp_test_files",
            force_download=False,
        )
        self.assertTrue(loader._decide_if_download_needed())

        # Clean up the temporary directory
        tearDown()

    def test_decide_if_download_needed_full_local_dir(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="mock",
            eval_dir_local="temp_test_files",
            force_download=False,
        )
        self.assertFalse(loader._decide_if_download_needed())

        # Clean up the temporary directory
        tearDown()

    def test_retrieve_and_check_dataset_image_names(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="mock",
            eval_dir_local="temp_test_files",
        )
        loader.image_dirs = ["input", "mask"]
        image_names = loader._retrieve_and_check_dataset_image_names()
        self.assertEqual(
            set(image_names),
            set(["doggo.png", "cat.png", "sillygoose.png", "chinchilla.png"]),
        )

        # Clean up the temporary directory
        tearDown()

    def test_retrieve_and_check_dataset_image_faulty_names(self):
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="faulty_names",
            eval_dir_local="temp_test_files",
        )
        loader.image_dirs = ["input", "mask"]
        with self.assertRaisesRegex(
            ValueError,
            "The names of the images in each image directory should be the same. input does not match mask.",
        ):
            loader._retrieve_and_check_dataset_image_names()

        # Clean up the temporary directory
        tearDown()


if __name__ == "__main__":
    unittest.main()
