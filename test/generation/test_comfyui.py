import os
import re
import unittest
from unittest.mock import MagicMock

import PIL

from pixaris.generation.comfyui import ComfyGenerator


class TestComfyUI(unittest.TestCase):
    def test_get_unique_int_for_image(self):
        """
        Test if the function returns an integer between 0 and 1000000.
        """

        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        response = generator._get_unique_int_for_image(
            "test/test_eval_data/mock/Input/model_90310595.jpg"
        )
        self.assertIsInstance(response, int)
        self.assertGreaterEqual(response, 0)
        self.assertLessEqual(response, 1000000)

    def test_get_unique_int_for_image_equal(self):
        """
        Test if the function returns the same integer for the same image.
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        response = generator._get_unique_int_for_image(
            "test/test_eval_data/mock/Input/model_90310595.jpg"
        )
        response2 = generator._get_unique_int_for_image(
            "test/test_eval_data/mock/Input/model_90310595.jpg"
        )
        self.assertEqual(response, response2)

    def test_validate_inputs_and_parameters_correct_dataset(self):
        """
        Test if the function works for a correct dataset.
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        dataset = [
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
        generation_params = []
        validation = generator.validate_inputs_and_parameters(
            dataset, generation_params
        )
        self.assertIsNone(validation)

    def test_validate_inputs_and_parameters_wrong_dataset_paths(self):
        """
        Test if the function raises an error if the paths are wrong.
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        dataset = [
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
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError,
            re.escape(
                "All image_paths should be valid paths. These paths do not exist: "
            ),
        ):
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_dataset_wrong_keys1(self):
        """
        Test if the function raises an error if the keys are wrong.
        has key "image" instead of "image_path"
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        dataset = [
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image": "test/test_eval_data/mock/Input/model_90310595.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/model_90310595.jpg",
                    },
                ]
            },
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError,
            "Each image_paths dictionary should contain the keys 'node_name' and 'image_path'.",
        ):
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_dataset_wrong_keys2(self):
        """
        Test if the function raises an error if the keys are wrong.
        has key "node" instead of "node_name"
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        dataset = [
            {
                "image_paths": [
                    {
                        "node": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/model_90310595.jpg",
                    },
                    {
                        "node_name": "Load Mask Image",
                        "image_path": "test/test_eval_data/mock/Mask/model_90310595.jpg",
                    },
                ]
            },
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError,
            "Each image_paths dictionary should contain the keys 'node_name' and 'image_path'.",
        ):
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_dataset_not_path(self):
        """
        Test if the function raises an error if the image_path is not a string.
        gave an image instead of a path
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        image = PIL.Image.open("test/test_eval_data/mock/Input/model_90310595.jpg")
        dataset = [
            {
                "image_paths": [
                    {
                        "node_name": "Load Input Image",
                        "image_path": "test/test_eval_data/mock/Input/model_90310595.jpg",
                    },
                    {"node_name": "Load Mask Image", "image_path": image},
                ]
            },
        ]
        generation_params = []

        with self.assertRaisesRegex(
            ValueError, "All image_paths should be strings. Got: "
        ):
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )
        image.close()  # avoid ResourceWarning of unclosed file

    def test_validate_inputs_and_parameters_params_correct(self):
        """
        Test if generation works for correct parameters.
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        dataset = []
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "seed",
                "value": 1,
            },
        ]

        validation = generator.validate_inputs_and_parameters(
            dataset, generation_params
        )
        self.assertIsNone(validation)

    def test_validate_inputs_and_parameters_params_wrong_keys1(self):
        """
        Test if the function raises an error if the keys are wrong.
        has key "node" instead of "node_name"
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
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
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_wrong_keys2(self):
        """
        Test if the function raises an error if the keys are wrong.
        'input' is missing
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
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
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_nodename(self):
        """
        Test if the function raises an error if the params are wrong.
        nodename 'KSampler' does not exist in the workflow
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
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
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_input(self):
        """
        Test if the function raises an error if the params are wrong.
        input 'schritte' does not exist for the node 'KSampler (Efficient) - Generation'
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
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
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_validate_inputs_and_parameters_params_type(self):
        """
        Test if the function raises an error if the params are wrong.
        "value" is a string instead of an integer for the input "seed"
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
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
            generator.validate_inputs_and_parameters(
                dataset,
                generation_params,
            )

    def test_modify_workflow_set_image(self):
        """
        check if the function calls upload_image with the input image
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        generator.workflow.upload_image = MagicMock()
        input_image = PIL.Image.open(
            "test/test_eval_data/mock/Input/model_90310595.jpg"
        )
        image_paths = [
            {
                "node_name": "Load Input Image",
                "image_path": "test/test_eval_data/mock/Input/model_90310595.jpg",
            }
        ]
        generator._modify_workflow(image_paths=image_paths)
        generator.workflow.upload_image.assert_called_with(input_image, "input")

    def test_modify_workflow_set_generation_params(self):
        """
        check if _modify_workflow sets the generation params correctly
        """
        generator = ComfyGenerator(
            workflow_apiformat_path=os.path.abspath(
                os.getcwd() + "/test/assets/test-background-generation.json"
            ),
        )
        generator.workflow.upload_image = MagicMock()
        image_paths = [
            {
                "node_name": "Load Input Image",
                "image_path": "test/test_eval_data/mock/Input/model_90310595.jpg",
            }
        ]
        generation_params = [
            {
                "node_name": "KSampler (Efficient) - Generation",
                "input": "steps",
                "value": 1,
            },
        ]
        generator._modify_workflow(image_paths, generation_params)
        self.assertEqual(generator.workflow.prompt_workflow["76"]["inputs"]["steps"], 1)


if __name__ == "__main__":
    unittest.main()
