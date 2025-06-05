import unittest
import logging

from pixaris.data_loaders.local import LocalDatasetLoader

logger = logging.getLogger(__name__)


class TestLocalDataset(unittest.TestCase):
    def test_load_dataset(self):
        loader = LocalDatasetLoader(
            project="test_project", dataset="mock", eval_dir_local="test"
        )
        dataset = loader.load_dataset()
        logger.debug(dataset)
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
        image_names = loader._retrieve_and_check_dataset_image_names()
        self.assertEqual(
            set(image_names),
            set(["doggo.png", "cat.png", "sillygoose.png", "chinchilla.png"]),
        )

    def test_retrieve_and_check_dataset_image_faulty_names(self):
        loader = LocalDatasetLoader(
            project="test_project", dataset="faulty_names", eval_dir_local="test"
        )
        loader.image_dirs = ["input", "mask"]
        with self.assertRaisesRegex(
            ValueError,
            "The names of the images in each image directory should be the same. input does not match mask.",
        ):
            loader._retrieve_and_check_dataset_image_names()


if __name__ == "__main__":
    unittest.main()
