import unittest
from PIL import Image
from pixaris.generation.flux import FluxFillGenerator


class TestFluxFillGenerator(unittest.TestCase):
    """
    A few tests for the FluxFillGenerator class.
    """

    def setUp(self):
        self.generator = FluxFillGenerator()
        self.mock_image1 = Image.open("test/test_eval_set/mock/input/model_01.png")
        self.mock_mask1 = Image.open("test/test_eval_set/mock/mask/model_01.png")

    def test_encode_image_to_base64(self):
        """
        Test if the image is correctly encoded to base64.
        """
        mock_image = Image.new("RGB", (100, 100), color="red")
        base64_string = self.generator._encode_image_to_base64(mock_image)
        mock_image.close()

        with open("test/test_eval_set/mock_image_base64encoded.txt", "r") as file:
            expected_base64_string = file.read()

        self.assertTrue(base64_string == expected_base64_string)

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

    def test_run_flux_success(self):
        """
        Test if the _run_flux method correctly generates an image.
        """
        args = {
            "pillow_images": [
                {
                    "node_name": "Load Input Image",
                    "pillow_image": self.mock_image1,
                },
                {
                    "node_name": "Load Mask Image",
                    "pillow_image": self.mock_mask1,
                },
            ],
            "generation_params": [
                {"node_name": "PROMPT", "input": "PROMPT", "value": "TEST"},
            ],
        }

        pillow_images = args["pillow_images"]
        generation_params = args["generation_params"]

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

            generated_image = self.generator._run_flux(pillow_images, generation_params)
            self.assertIsInstance(generated_image, Image.Image)

    def test_generate_single_image(self):
        """
        Test if generate_single_image works correctly by checking if the output
        is a PIL Image and the name is matching the expected name.
        """
        args = {
            "pillow_images": [
                {
                    "node_name": "Load Input Image",
                    "pillow_image": self.mock_image1,
                },
                {
                    "node_name": "Load Mask Image",
                    "pillow_image": self.mock_mask1,
                },
            ],
            "generation_params": [
                {"node_name": "PROMPT", "input": "PROMPT", "value": "TEST"},
            ],
        }

        with unittest.mock.patch.object(
            self.generator, "_run_flux", return_value=Image.new("RGB", (100, 100))
        ):
            image, image_name = self.generator.generate_single_image(args)
            self.assertIsInstance(image, Image.Image)
            self.assertEqual(image_name, "model_01.png")


if __name__ == "__main__":
    unittest.main()
