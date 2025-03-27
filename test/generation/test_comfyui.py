import os
import re
import unittest
from unittest.mock import MagicMock
from PIL import Image

from pixaris.generation.comfyui import ComfyGenerator
from pixaris.utils.hyperparameters import (
    expand_hyperparameters,
    generate_hyperparameter_grid,
)
import json


class TestComfyUI(unittest.TestCase):
    def setUp(self):
        with open(
            os.getcwd() + "/test/assets/test-background-generation.json", "r"
        ) as file:
            workflow_apiformat_json = json.load(file)

        self.generator = ComfyGenerator(workflow_apiformat_json)

        self.mock_image1 = Image.open("test/test_project/mock/input/model_01.png")
        self.mock_image2 = Image.open("test/test_project/mock/input/model_02.png")
        self.mock_mask1 = Image.open("test/test_project/mock/mask/model_01.png")

    def test_get_unique_int_for_image(self):
        """
        Test if the function returns an integer between 0 and 1000000.
        """
        response = self.generator._get_unique_int_for_image(self.mock_image1)
        self.assertIsInstance(response, int)
        self.assertGreaterEqual(response, 0)
        self.assertLessEqual(response, 1000000)

    def test_get_unique_int_for_image_equal(self):
        """
        Test if the function returns the same integer for the same image.
        """
        response = self.generator._get_unique_int_for_image(self.mock_image1)
        response2 = self.generator._get_unique_int_for_image(self.mock_image1)
        self.assertEqual(response, response2)

    def test_get_unique_int_for_different_images(self):
        """
        Test if the function returns the different integers for the same image with different filenames.
        """
        response = self.generator._get_unique_int_for_image(self.mock_image1)
        response2 = self.generator._get_unique_int_for_image(self.mock_image2)
        self.assertNotEqual(response, response2)

    def test_validate_inputs_and_parameters_correct_dataset(self):
        """
        Test if the function works for a correct dataset.
        """
        dataset = [
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": self.mock_image1,
                    },
                    {
                        "node_name": "Load Mask Image",
                        "pillow_image": self.mock_mask1,
                    },
                ]
            },
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": self.mock_image1,
                    },
                    {
                        "node_name": "Load Mask Image",
                        "pillow_image": self.mock_mask1,
                    },
                ]
            },
        ]
        generation_params = []
        validation = self.generator.validate_inputs_and_parameters(
            dataset, generation_params
        )
        self.assertIsNone(validation)

    def test_validate_inputs_and_parameters_dataset_wrong_keys(self):
        """
        Test if the function raises an error if the keys are wrong.
        """
        dataset = [
            {
                "pillow_images": [
                    {
                        "wrong": "Load Input Image",
                        "wrong1": self.mock_image1,
                    },
                    {
                        "wrong": "Load Mask Image",
                        "wrong1": self.mock_mask1,
                    },
                ]
            },
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError,
            "Each pillow_images dictionary should contain the keys 'node_name' and 'pillow_image'.",
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_dataset_not_image(self):
        """
        Test if the function raises an error if the pillow_image is not a PIL Image.
        """
        dataset = [
            {
                "pillow_images": [
                    {
                        "node_name": "Load Input Image",
                        "pillow_image": "not_a_pillow_image",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "pillow_image": self.mock_mask1,
                    },
                ]
            },
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError, "All pillow_images should be PIL Image objects."
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_correct(self):
        """
        Test if generation works for correct parameters.
        """
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "seed",
                "value": 1,
            },
        ]

        validation = self.generator.validate_inputs_and_parameters(
            dataset, generation_params
        )
        self.assertIsNone(validation)

    def test_validate_inputs_and_parameters_params_wrong_keys1(self):
        """
        Test if the function raises an error if the keys are wrong.
        has key "node" instead of "node_name"
        """
        dataset = []
        generation_params = [
            {
                "node": "KSampler (Efficient) - Generation",
                "input": "seed",
                "value": 1,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "Each generation_param dictionary should contain the keys 'node_name', 'input', and 'value'.",
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_wrong_keys2(self):
        """
        Test if the function raises an error if the keys are wrong.
        'input' is missing
        """
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "seed": 1,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            "Each generation_param dictionary should contain the keys 'node_name', 'input', and 'value'.",
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_nodename(self):
        """
        Test if the function raises an error if the params are wrong.
        nodename 'KSampler' does not exist in the workflow
        """
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler",
                "input": "seed",
                "value": 1,
            },
        ]

        with self.assertRaisesRegex(
            ValueError, "Node KSampler does not exist in the workflow."
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_input(self):
        """
        Test if the function raises an error if the params are wrong.
        input 'schritte' does not exist for the node 'KSampler (Efficient) - Generation'
        """
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "schritte",
                "value": 1,
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            re.escape(
                "Node KSampler (Efficient) - Generation does not have input schritte"
            ),
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_type(self):
        """
        Test if the function raises an error if the params are wrong.
        "value" is a string instead of an integer for the input "seed"
        """
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "seed",
                "value": "1",
            },
        ]

        with self.assertRaisesRegex(
            ValueError,
            re.escape(
                "Node KSampler (Efficient) - Generation input seed has the wrong type"
            ),
        ):
            self.generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_modify_workflow_set_image(self):
        """
        check if the function calls upload_image with the input image
        """
        self.generator.workflow.upload_image = MagicMock()
        pillow_images = [
            {
                "node_name": "Load Input Image",
                "pillow_image": self.mock_image1,
            }
        ]
        self.generator._modify_workflow(pillow_images=pillow_images)
        self.generator.workflow.upload_image.assert_called_with(
            self.mock_image1, "input"
        )

    def test_modify_workflow_set_generation_params(self):
        """
        check if _modify_workflow sets the generation params correctly
        """
        self.generator.workflow.upload_image = MagicMock()
        pillow_images = [
            {
                "node_name": "Load Input Image",
                "pillow_image": self.mock_image1,
            }
        ]
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "steps",
                "value": 1,
            },
        ]
        self.generator._modify_workflow(pillow_images, generation_params)
        self.assertEqual(
            self.generator.workflow.workflow_apiformat_json["76"]["inputs"]["steps"], 1
        )

    def test_expand_hyperparameters(self):
        """
        test if expanding works.
        """
        self.maxDiff = None
        hyperparameters = [
            {
                "node_name": "test1",
                "input": "in1",
                "value": [1, 2],
            },
            {
                "node_name": "test2",
                "input": "in2",
                "value": ["one", "two"],
            },
        ]
        expanded_hyperparameters = expand_hyperparameters(hyperparameters)
        self.assertEqual(
            expanded_hyperparameters,
            [
                {
                    "node_name": "test1",
                    "input": "in1",
                    "value": 1,
                },
                {
                    "node_name": "test1",
                    "input": "in1",
                    "value": 2,
                },
                {
                    "node_name": "test2",
                    "input": "in2",
                    "value": "one",
                },
                {
                    "node_name": "test2",
                    "input": "in2",
                    "value": "two",
                },
            ],
        )

    def test_generate_hyperparameter_grid(self):
        """
        test if grid generation works.
        """
        hyperparameters = [
            {
                "node_name": "test1",
                "input": "in1",
                "value": [1, 2],
            },
            {
                "node_name": "test2",
                "input": "in2",
                "value": ["one", "two"],
            },
        ]
        hyperparameter_grid = generate_hyperparameter_grid(hyperparameters)
        self.assertEqual(
            hyperparameter_grid,
            [
                [
                    {
                        "node_name": "test1",
                        "input": "in1",
                        "value": 1,
                    },
                    {
                        "node_name": "test2",
                        "input": "in2",
                        "value": "one",
                    },
                ],
                [
                    {
                        "node_name": "test1",
                        "input": "in1",
                        "value": 1,
                    },
                    {
                        "node_name": "test2",
                        "input": "in2",
                        "value": "two",
                    },
                ],
                [
                    {
                        "node_name": "test1",
                        "input": "in1",
                        "value": 2,
                    },
                    {
                        "node_name": "test2",
                        "input": "in2",
                        "value": "one",
                    },
                ],
                [
                    {
                        "node_name": "test1",
                        "input": "in1",
                        "value": 2,
                    },
                    {
                        "node_name": "test2",
                        "input": "in2",
                        "value": "two",
                    },
                ],
            ],
        )


if __name__ == "__main__":
    unittest.main()
