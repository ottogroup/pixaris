import unittest
from unittest.mock import MagicMock
from PIL import Image
import vertexai
from pixaris.generation.imagen2 import Imagen2Generator


class TestImagen2Generator(unittest.TestCase):
    """
    A few tests for the Imagen2Generator class.
    """

    def setUp(self):
        vertexai.init = MagicMock()
        self.generator = Imagen2Generator("test_project_id", "test_location")
        mock_image1 = Image.open("test/test_project/mock/input/chinchilla.png")
        mock_mask1 = Image.open("test/test_project/mock/mask/chinchilla.png")

        self.args = {
            "pillow_images": [
                {
                    "node_name": "Load Input Image",
                    "pillow_image": mock_image1,
                },
                {
                    "node_name": "Load Mask Image",
                    "pillow_image": mock_mask1,
                },
            ],
            "prompt": "TEST",
        }

    def test_validate_inputs_and_parameters_correct(self):
        """
        Test if the function does not raise an error if dataset is in the correct format.
        """
        pillow_images = self.args.get("pillow_images", [])
        prompt = self.args.get("prompt", "")

        self.assertIsNone(
            self.generator.validate_inputs_and_parameters(pillow_images, prompt)
        )

    def test_validate_inputs_and_parameters_wrong_dataset_format(self):
        """
        Test if the function raises an error if dataset is not in the correct format.
        """
        pillow_images = ["wrong_format"]
        prompt = self.args.get("prompt", "")

        with self.assertRaises(
            ValueError,
            msg="Each entry in the dataset must be a dictionary.",
        ):
            self.generator.validate_inputs_and_parameters(pillow_images, prompt)

    def test_validate_inputs_and_parameters_wrong_prompt(self):
        """
        Test if the function raises an error if prompt is not in the correct format.
        """
        pillow_images = self.args.get("pillow_images", [])
        prompt = []

        with self.assertRaises(
            ValueError,
            msg="Prompt must be a string.",
        ):
            self.generator.validate_inputs_and_parameters(pillow_images, prompt)

    def test_generate_single_image(self):
        """
        Test if generate_single_image works correctly by checking if the output
        is a PIL Image and the name is matching the expected name.
        """

        with unittest.mock.patch.object(
            self.generator, "_run_imagen", return_value=Image.new("RGB", (100, 100))
        ):
            image, image_name = self.generator.generate_single_image(self.args)
            self.assertIsInstance(image, Image.Image)
            self.assertEqual(image_name, "chinchilla.png")


if __name__ == "__main__":
    unittest.main()
