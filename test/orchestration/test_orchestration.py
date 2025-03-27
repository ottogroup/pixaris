import json
from unittest.mock import patch
from PIL import Image
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset
import unittest
import os


class TestOrchestration(unittest.TestCase):
    @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    def test_generate_images(self, mock_loader, mock_workflow):
        """
        Test the generate_images function. This one is correct
        """
        writer = LocalDataWriter()

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
            "dataset": "test_dataset",
            "experiment_run_name": "testrun",
        }

        mock_loader.load_dataset.return_value = [
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": Image.open(
                            "test/test_dataset/mock/input/model_01.png"
                        ),
                    },
                    {
                        "node_name": "Load Mask Image",
                        "pillow_image": Image.open(
                            "test/test_dataset/mock/mask/model_01.png"
                        ),
                    },
                ]
            },
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": Image.open(
                            "test/test_dataset/mock/input/model_01.png"
                        ),
                    },
                    {
                        "node_name": "Load Mask Image",
                        "pillow_image": Image.open(
                            "test/test_dataset/mock/mask/model_01.png"
                        ),
                    },
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
            mock_loader, generator, writer, [], args
        )
        self.assertEqual(len(images), 2)

    # @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    # @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    # @patch("builtins.print")
    # def test_generate_images_one_fault(self, mock_print, mock_loader, mock_workflow):
    #     """
    #     One of the images is broken. Should run but throw warnings
    #     """
    #     writer = LocalDataWriter()
    #     args = {
    #         "workflow_apiformat_json": os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
    #         ),
    #         "workflow_pillow_image": os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save.png"
    #         ),
    #         "dataset": "test_dataset",
    #         "experiment_run_name": "testrun",
    #     }

    #     mock_fake_image = Image.open("test/assets/fake_image.jpg")

    #     mock_loader.load_dataset.return_value = [
    #         {
    #             "pillow_images": [
    #                 {
    #                     "node_name": "Load Input Image",
    #                     "pillow_image": mock_fake_image,
    #                 },
    #                 {
    #                     "node_name": "Load Mask Image",
    #                     "pillow_image": mock_fake_image,
    #                 },
    #             ]
    #         },
    #         {
    #             "pillow_images": [
    #                 {
    #                     "node_name": "Load Input Image",
    #                     "pillow_image": Image.open("test/test_dataset/mock/input/model_01.png"),
    #                 },
    #                 {
    #                     "node_name": "Load Mask Image",
    #                     "pillow_image": Image.open("test/test_dataset/mock/mask/model_01.png"),
    #                 },
    #             ]
    #         },
    #     ]

    #     generator = ComfyGenerator(
    #         workflow_apiformat_json=os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
    #         )
    #     )
    #     generator.workflow = mock_workflow
    #     mock_workflow.queue_prompt.return_value = json.loads(
    #         b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
    #     )
    #     mock_workflow.download_image.return_value = Image.new(
    #         "RGB", (100, 100), color="red"
    #     )
    #     images = generate_images_based_on_dataset(
    #         mock_loader, generator, writer, [], args
    #     )
    #     mock_print.assert_any_call("continuing with next image.")
    #     mock_print.assert_any_call("Failed to generate images for 1 of 2.")
    #     self.assertEqual(len(images), 1)

    # @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    # @patch("pixaris.data_loaders.gcp.GCPDatasetLoader")
    # def test_generate_images_all_fault(self, mock_loader, mock_workflow):
    #     """
    #     All images are broken. Should throw an error
    #     """
    #     writer = LocalDataWriter()
    #     args = {
    #         "workflow_apiformat_json": os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
    #         ),
    #         "workflow_pillow_image": os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save.png"
    #         ),
    #         "dataset": "test_dataset",
    #         "experiment_run_name": "testrun",
    #     }

    #     mock_fake_image = Image.open("test/assets/fake_image.jpg")

    #     mock_loader.load_dataset.return_value = [
    #         {
    #             "pillow_images": [
    #                 {
    #                     "node_name": "Load Input Image",
    #                     "pillow_image": mock_fake_image,
    #                 },
    #                 {
    #                     "node_name": "Load Mask Image",
    #                     "pillow_image": mock_fake_image,
    #                 },
    #             ]
    #         },
    #     ]

    #     generator = ComfyGenerator(
    #         workflow_apiformat_json=os.path.abspath(
    #             os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
    #         )
    #     )
    #     generator.workflow = mock_workflow
    #     mock_workflow.queue_prompt.return_value = json.loads(
    #         b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
    #     )
    #     mock_workflow.download_image.return_value = Image.new(
    #         "RGB", (100, 100), color="red"
    #     )
    #     with self.assertRaisesRegex(
    #         ValueError,
    #         "Failed to generate images for all 1 images. \nLast error message: cannot identify image file",
    #     ):
    #         generate_images_based_on_dataset(
    #             mock_loader,
    #             generator,
    #             writer,
    #             [],
    #             args,
    #         )


if __name__ == "__main__":
    unittest.main()
