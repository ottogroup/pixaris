import unittest
import os

from pixaris.data_loaders.local import LocalDatasetLoader


class TestLocalDataset(unittest.TestCase):
    def test_load_dataset(self):
        loader = LocalDatasetLoader(
            project="test_project", dataset="mock", eval_dir_local="test"
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

    def test_retrieve_and_check_dataset_image_names(self):
        loader = LocalDatasetLoader(
            project="test_project", dataset="mock", eval_dir_local="test"
        )
        loader.image_dirs = ["input", "mask"]
        dataset_dir = os.path.join("test", "test_project", "mock")
        image_names = loader._retrieve_and_check_dataset_image_names(
            dataset_dir, loader.image_dirs
        )
        self.assertEqual(
            set(image_names),
            set(["doggo.png", "cat.png", "sillygoose.png", "chinchilla.png"]),
        )

    def test_retrieve_and_check_dataset_image_faulty_names(self):
        loader = LocalDatasetLoader(
            project="test_project", dataset="faulty_names", eval_dir_local="test"
        )
        loader.image_dirs = ["input", "mask"]
        dataset_dir = os.path.join("test", "test_project", "faulty_names")
        with self.assertRaisesRegex(
            ValueError,
            "The names of the images in each image directory should be the same. input does not match mask.",
        ):
            loader._retrieve_and_check_dataset_image_names(
                dataset_dir, loader.image_dirs
            )


if __name__ == "__main__":
    unittest.main()
