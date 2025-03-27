import unittest

from pixaris.data_loaders.local import LocalDatasetLoader


class TestLocalDataset(unittest.TestCase):
    def test_get_pillow_images(self):
        loader = LocalDatasetLoader(project="test_project", dataset="mock", eval_dir_local="test/")
        dataset = loader.load_dataset()
        print(dataset)
        self.assertEqual(len(dataset), 2)
        for entry in dataset:
            self.assertIn("pillow_images", entry)
            paths = entry["pillow_images"]
            for path in paths:
                self.assertIn("node_name", path)
                self.assertIn("pillow_image", path)


if __name__ == "__main__":
    unittest.main()
