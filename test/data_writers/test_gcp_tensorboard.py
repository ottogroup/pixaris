import unittest
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter


class TestGCPTensorboardWriter(unittest.TestCase):
    def setUp(self):
        self.writer = GCPTensorboardWriter(
            gcp_project_id="test_project", location="test_location"
        )

    def test_validate_experiment_run_name_valid(self):
        """Test that _validate_experiment_run_name does not raise an AssertionError for a valid run name."""
        try:
            self.writer._validate_experiment_run_name("valid-run-name")
        except AssertionError:
            self.fail(
                "_validate_experiment_run_name raised AssertionError unexpectedly!"
            )

    def test_validate_experiment_run_name_uppercase(self):
        """Test that _validate_experiment_run_name raises an AssertionError for an uppercase run name with underscore."""
        with self.assertRaises(AssertionError):
            self.writer._validate_experiment_run_name("Invalid_Run_Name")


if __name__ == "__main__":
    unittest.main()
