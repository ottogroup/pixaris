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

    def test_validate_inputs_and_parameters_wrong_dataset_format(self):
        """
        Test if the function raises an error if dataset is not in the correct format.
        """
        dataset = ["wrong_format"]
        generation_params = []

        with self.assertRaises(
            ValueError,
            msg="Each entry in the dataset must be a dictionary.",
        ):
            self.generator.validate_inputs_and_parameters(dataset, generation_params)

    def test_run_imagen_success(self):
        """
        Test if the _run_imagen method correctly generates an image.
        """
        pillow_images = self.args["pillow_images"]
        prompt = self.args["prompt"]

        # Mocking requests.post and requests.get to simulate API response
        with (
            unittest.mock.patch("requests.post") as mock_post,
            unittest.mock.patch("requests.get") as mock_get,
        ):
            mock_post.return_value.json.return_value = {"id": "request_id"}
            mock_get.return_value.json.return_value = {
                "status": "Ready",
                "result": {"sample": "https://example.com/generated_image.jpeg"},
            }

            # return random bytes to simulate image content
            mock_get.return_value.content = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
                b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe"
                b"\x02\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
            )

            generated_image = self.generator._run_imagen(pillow_images, prompt)
            self.assertIsInstance(generated_image, Image.Image)

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
