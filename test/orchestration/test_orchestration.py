import json
from unittest.mock import patch

import PIL
from pixaris.data_writers.local import LocalDataWriter
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_eval_set
import unittest
import os


class TestOrchestration(unittest.TestCase):
    @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    @patch("pixaris.data_loaders.google.GCPDatasetLoader")
    def test_generate_images(self, mock_loader, mock_workflow):
        writer = LocalDataWriter()
        args = {
            "workflow_apiformat_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            ),
            "workflow_image_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save.png"
            ),
            "eval_set": "z_test_correct",
            "run_name": "testrun",
        }
        loader = mock_loader
        loader.load_dataset.return_value = [
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/model_90310595.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/model_90310595.jpg",
                    },
                ]
            },
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/model_91803795.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/model_91803795.jpg",
                    },
                ]
            },
        ]

        # call Generator with mock workflow
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            )
        )
        generator.workflow = mock_workflow
        mock_workflow.queue_prompt.return_value = json.loads(
            b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
        )
        mock_workflow.download_image.return_value = PIL.Image.new(
            "RGB", (100, 100), color="red"
        )
        images = generate_images_based_on_eval_set(loader, generator, writer, args)
        self.assertEqual(len(images), 2)

    @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    @patch("pixaris.data_loaders.google.GCPDatasetLoader")
    @patch("builtins.print")
    def test_generate_images_one_fault(self, mock_print, mock_loader, mock_workflow):
        writer = LocalDataWriter()
        args = {
            "workflow_apiformat_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            ),
            "workflow_image_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save.png"
            ),
            "eval_set": "z_test_correct",
            "run_name": "testrun",
        }

        loader = mock_loader
        loader.load_dataset.return_value = [
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/fake.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/fake.jpg",
                    },
                ]
            },
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/model_91803795.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/model_91803795.jpg",
                    },
                ]
            },
        ]

        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            )
        )
        generator.workflow = mock_workflow
        mock_workflow.queue_prompt.return_value = json.loads(
            b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
        )
        mock_workflow.download_image.return_value = PIL.Image.new(
            "RGB", (100, 100), color="red"
        )
        images = generate_images_based_on_eval_set(loader, generator, writer, args)
        mock_print.assert_any_call("continuing with next image.")
        mock_print.assert_any_call("Failed to generate images for 1 of 2.")
        self.assertEqual(len(images), 1)

    @patch("pixaris.generation.comfyui_utils.workflow.ComfyWorkflow")
    @patch("pixaris.data_loaders.google.GCPDatasetLoader")
    def test_generate_images_all_fault(self, mock_loader, mock_workflow):
        writer = LocalDataWriter()
        args = {
            "workflow_apiformat_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            ),
            "workflow_image_path": os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save.png"
            ),
            "eval_set": "z_test_correct",
            "run_name": "testrun",
        }

        loader = mock_loader
        loader.load_dataset.return_value = [
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/fake.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/fake.jpg",
                    },
                ]
            },
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/also_fake.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/also_fake.jpg",
                    },
                ]
            },
        ]

        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-just-load-and-save_apiformat.json"
            )
        )
        generator.workflow = mock_workflow
        mock_workflow.queue_prompt.return_value = json.loads(
            b'{"prompt_id": "test-prompt-id", "number": 2, "node_errors": {}}'
        )
        mock_workflow.download_image.return_value = PIL.Image.new(
            "RGB", (100, 100), color="red"
        )
        try:
            generate_images_based_on_eval_set(loader, generator, writer, args)
        except Exception as e:
            self.assertEqual(
                str(e),
                "Failed to generate images for all 2 images. \nLast error message: [Errno 2] No such file or directory: 'test/test_eval_data/mock/Input/also_fake.jpg'",
            )
        else:
            self.fail("Exception not raised when all images failed")


if __name__ == "__main__":
    unittest.main()
