import os
import shutil
import json
import unittest
import pandas as pd

from pixaris.experiment_handlers.local import LocalExperimentHandler

TEMP_RESULTS_DIR = "temp_test_results_local_handler"


def tearDown():
    if os.path.exists(TEMP_RESULTS_DIR):
        shutil.rmtree(TEMP_RESULTS_DIR)


class TestLocalExperimentHandler(unittest.TestCase):
    def test_load_results_file_missing(self):
        handler = LocalExperimentHandler(local_results_folder=TEMP_RESULTS_DIR)
        df = handler.load_experiment_results_for_dataset("proj", "dataset")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        tearDown()

    def test_load_results_file_corrupt(self):
        os.makedirs(os.path.join(TEMP_RESULTS_DIR, "proj", "dataset"), exist_ok=True)
        with open(
            os.path.join(TEMP_RESULTS_DIR, "proj", "dataset", "experiment_tracking.jsonl"),
            "w",
        ) as f:
            f.write("not a json line")

        handler = LocalExperimentHandler(local_results_folder=TEMP_RESULTS_DIR)
        df = handler.load_experiment_results_for_dataset("proj", "dataset")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        tearDown()

    def test_load_results_file_valid(self):
        os.makedirs(os.path.join(TEMP_RESULTS_DIR, "proj", "dataset"), exist_ok=True)
        file_path = os.path.join(
            TEMP_RESULTS_DIR, "proj", "dataset", "experiment_tracking.jsonl"
        )
        with open(file_path, "w") as f:
            f.write(json.dumps({"val": 1}) + "\n")
            f.write(json.dumps({"val": 2}) + "\n")

        handler = LocalExperimentHandler(local_results_folder=TEMP_RESULTS_DIR)
        df = handler.load_experiment_results_for_dataset("proj", "dataset")
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["val"], 1)
        tearDown()


if __name__ == "__main__":
    unittest.main()

