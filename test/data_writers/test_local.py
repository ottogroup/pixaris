import unittest

from pixaris.data_loaders.local import LocalDatasetLoader


class TestLocalDataset(unittest.TestCase):
    def test_get_image_paths(self):
        loader = LocalDatasetLoader(
            eval_set="mock", eval_dir_local="test/test_eval_data"
        )
        dataset = loader.load_dataset()
        print(dataset)
        self.assertEqual(len(dataset), 2)
        for entry in dataset:
            self.assertIn("image_paths", entry)
            paths = entry["image_paths"]
            for path in paths:
                self.assertIn("node_name", path)
                self.assertIn("image_path", path)


if __name__ == "__main__":
    unittest.main()
