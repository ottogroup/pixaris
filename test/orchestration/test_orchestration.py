import json
import shutil
from unittest.mock import patch
from PIL import Image
from pixaris.experiment_handlers.local import LocalExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset
import unittest
import os


def tearDown():
    # Remove the temporary directory after each test
    if os.path.exists("temp_test_results"):
        shutil.rmtree("temp_test_results")


class TestOrchestration(unittest.TestCase):
    @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    def test_generate_images(self, mock_loader, mock_workflow):
        """
        Test the generate_images function. This one is correct
        """
        experiment_handler = LocalExperimentHandler(
            local_results_folder="temp_test_results"
        )

        with open(
            os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json", "r"
        ) as file:
            workflow_apiformat_json = json.load(file)

        args = {
            "workflow_apiformat_json": workflow_apiformat_json,
            "workflow_pillow_image": Image.open(
                os.path.abspath(
                    os.getcwd() + "/test/assets/test-just-load-and-save.png"
                )
            ),
            "project": "test_project",
            "dataset": "test_dataset",
            "experiment_run_name": "testrun",
        }

        mock_image = Image.open("test/test_project/mock/input/model_01.png")

        mock_loader.load_dataset.return_value = [
            {
                "pillow_images": [
                    {"node_name": "Load Input Image", "pillow_image": mock_image},
                    {"node_name": "Load Mask Image", "pillow_image": mock_image},
                ]
            },
            {
                "pillow_images": [
                    {"node_name": "Load Input Image", "pillow_image": mock_image},
                    {"node_name": "Load Mask Image", "pillow_image": mock_image},
                ]
            },
        ]

        # Call Generator with mock workflow
        generator = ComfyGenerator(workflow_apiformat_json=workflow_apiformat_json)
        generator.workflow = mock_workflow
        mock_workflow.queue_prompt.return_value = json.loads(
            b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
        )
        mock_workflow.download_image.return_value = Image.new(
            "RGB", (100, 100), color="red"
        )
        images = generate_images_based_on_dataset(
            mock_loader, generator, experiment_handler, [], args
        )
        self.assertEqual(len(images), 2)

        tearDown()

    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    @patch("builtins.print")
    @patch("pixaris.generation.comfyui.ComfyGenerator.generate_single_image")
    def test_generate_images_one_fault(
        self, mock_generate_single_image, mock_print, mock_loader
    ):
        """
        One of the images is broken. Should run but throw warnings
        """
        experiment_handler = LocalExperimentHandler(
            local_results_folder="temp_test_results"
        )

        with open(
            os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json", "r"
        ) as file:
            workflow_apiformat_json = json.load(file)

        args = {
            "workflow_apiformat_json": workflow_apiformat_json,
            "workflow_pillow_image": Image.open(
                os.path.abspath(
                    os.getcwd() + "/test/assets/test-just-load-and-save.png"
                )
            ),
            "project": "test_project",
            "dataset": "test_dataset",
            "experiment_run_name": "testrun",
        }

        mock_image = Image.open("test/test_project/mock/input/model_01.png")

        mock_loader.load_dataset.return_value = [
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": mock_image,
                    }
                ]
            },
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": mock_image,
                    }
                ]
            },
        ]

        generator = ComfyGenerator(workflow_apiformat_json=workflow_apiformat_json)
        mock_generate_single_image.side_effect = [
            (Image.new("RGB", (100, 100), color="red"), "correct.png"),
            Exception("Test"),
        ]
        images = generate_images_based_on_dataset(
            mock_loader, generator, experiment_handler, [], args
        )
        mock_print.assert_any_call("Failed to generate images for 1 of 2.")
        self.assertEqual(len(images), 1)

        tearDown()

    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    @patch("pixaris.generation.comfyui.ComfyGenerator.generate_single_image")
    def test_generate_images_all_fault(self, mock_generate_single_image, mock_loader):
        """
        All images are broken. Should throw an error
        """
        experiment_handler = LocalExperimentHandler(
            local_results_folder="temp_test_results"
        )

        with open(
            os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json", "r"
        ) as file:
            workflow_apiformat_json = json.load(file)

        args = {
            "workflow_apiformat_json": workflow_apiformat_json,
            "workflow_pillow_image": Image.open(
                os.path.abspath(
                    os.getcwd() + "/test/assets/test-just-load-and-save.png"
                )
            ),
            "project": "test_project",
            "dataset": "test_dataset",
            "experiment_run_name": "testrun",
        }

        error_image = Image.open("test/assets/test_inspo.png")

        mock_loader.load_dataset.return_value = [
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": error_image,
                    }
                ]
            },
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": error_image,
                    }
                ]
            },
        ]

        generator = ComfyGenerator(workflow_apiformat_json=workflow_apiformat_json)
        mock_generate_single_image.side_effect = [Exception("Test"), Exception("Test")]
        with self.assertRaisesRegex(
            ValueError,
            "Failed to generate images for all 2 images. \nLast error message: Test",
        ):
            generate_images_based_on_dataset(
                mock_loader,
                generator,
                experiment_handler,
                [],
                args,
            )

        tearDown()


if __name__ == "__main__":
    unittest.main()
