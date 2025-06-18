import unittest
from unittest.mock import patch
import shutil
import os

from pixaris.data_loaders.gcp import GCPDatasetLoader


def copy_test_project():
    """
    Copy the test project to a temporary location for testing.
    """
    # Copy the test project to a temporary location
    test_project_path = os.path.join(os.getcwd(), "test", "test_project")
    temp_test_project_path = os.path.join(
        os.getcwd(), "temp_test_files", "test_project"
    )

    if os.path.exists(temp_test_project_path):
        shutil.rmtree(temp_test_project_path)

    shutil.copytree(test_project_path, temp_test_project_path)


def tearDown():
    """
    Remove the temporary directory after each test.
    """
    # Remove the temporary directory after each test
    temp_test_project_path = os.path.join(os.getcwd(), "temp_test_files")
    if os.path.exists(temp_test_project_path):
        shutil.rmtree(temp_test_project_path)


def mock_download(self):
    base_path = os.path.join(
        os.getcwd(), "temp_test_files", "test_project", self.dataset
    )
    self.image_dirs = [
        name
        for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]
    dir_to_names = {
        d: [
            name
            for name in os.listdir(os.path.join(base_path, d))
            if name != ".DS_Store"
        ]
        for d in self.image_dirs
    }
    all_names = set().union(*dir_to_names.values())
    self.dataset_blob_map = {name: {} for name in all_names}
    for name in all_names:
        for d in self.image_dirs:
            path = os.path.join(base_path, d, name)
            if os.path.exists(path):
                self.dataset_blob_map[name][d] = path


def mock_blob_bytes(self, path):
    with open(path, "rb") as f:
        return f.read()


class TestLocalDataset(unittest.TestCase):
    @patch(
        "pixaris.data_loaders.gcp.GCPDatasetLoader._download_blob_bytes",
        mock_blob_bytes,
    )
    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader._download_dataset", mock_download)
    def test_load_dataset(self):
        """
        tests the load_dataset method of the GCPDatasetLoader class
        It creates a mock GCPDatasetLoader, loads the dataset, and checks if the dataset is formatted correctly.
        """
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

    def test_decide_if_download_needed_empty_local_dir(self):
        """
        if the local directory is empty, the dataset should be downloaded
        """
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
        """
        if the local directory is not empty, the dataset should not be downloaded
        """
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
        """
        tests the retrieve_and_check_dataset_image_names method of the GCPDatasetLoader class
        It retrieves the image names, and checks if the image names are correct.
        """
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="mock",
            eval_dir_local="temp_test_files",
        )
        mock_download(loader)
        image_names = loader._retrieve_and_check_dataset_image_names()
        self.assertEqual(
            set(image_names),
            set(["doggo.png", "cat.png", "sillygoose.png", "chinchilla.png"]),
        )

        # Clean up the temporary directory
        tearDown()

    def test_retrieve_and_check_dataset_image_faulty_names(self):
        """
        tests the retrieve_and_check_dataset_image_names method of the GCPDatasetLoader class
        It tries to retrieve the image names, they are faulty and there should be an error
        """
        # Copy the test project to a temporary location
        copy_test_project()

        loader = GCPDatasetLoader(
            gcp_project_id="test_project_id",
            gcp_pixaris_bucket_name="test_bucket_name",
            project="test_project",
            dataset="faulty_names",
            eval_dir_local="temp_test_files",
        )
        mock_download(loader)
        with self.assertRaisesRegex(
            ValueError,
            "The names of the images in each image directory should be the same. input does not match mask.",
        ):
            loader._retrieve_and_check_dataset_image_names()

        # Clean up the temporary directory
        tearDown()


if __name__ == "__main__":
    unittest.main()
