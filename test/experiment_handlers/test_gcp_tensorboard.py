import unittest
from pixaris.experiment_handlers.gcp_tensorboard import GCPTensorboardHandler


class TestGCPTensorboardHandler(unittest.TestCase):
    def setUp(self):
        self.experiment_handler = GCPTensorboardHandler(
            gcp_project_id="test_project", location="test_location"
        )

    def test_validate_experiment_run_name_valid(self):
        """Test that _validate_experiment_run_name does not raise an AssertionError for a valid run name."""
        try:
            self.experiment_handler._validate_experiment_run_name("valid-run-name")
        except AssertionError:
            self.fail(
                "_validate_experiment_run_name raised AssertionError unexpectedly!"
            )

    def test_validate_experiment_run_name_uppercase(self):
        """Test that _validate_experiment_run_name raises an AssertionError for an uppercase run name with underscore."""
        with self.assertRaises(AssertionError):
            self.experiment_handler._validate_experiment_run_name("Invalid_Run_Name")


if __name__ == "__main__":
    unittest.main()
