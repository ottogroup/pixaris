import unittest
from PIL import Image
import io

from pixaris.generation.utils import (
    encode_image_to_bytes,
    extract_value_from_list_of_dicts,
)


class TestGenerationUtils(unittest.TestCase):
    def test_image_to_bytes(self):
        # Create a simple image for testing
        img = Image.open("test/test_project/mock/input/chinchilla.png")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        # Convert the image to bytes
        result = encode_image_to_bytes(img)

        # Check if the result is equal to the original byte array
        self.assertEqual(result, img_byte_arr)

    def test_extract_value_from_list_of_dicts(self):
        """
        Test the extract_value_from_list_of_dicts function.
        """
        dict_list = [
            {"node_name": "Load Input Image", "pillow_image": "image1"},
            {"node_name": "Load Mask Image", "pillow_image": "image2"},
        ]
        identifying_key = "node_name"
        identifying_value = "Load Input Image"
        return_key = "pillow_image"

        result = extract_value_from_list_of_dicts(
            dict_list, identifying_key, identifying_value, return_key
        )

        self.assertEqual(result, "image1")

    def test_extract_value_from_list_of_dicts_multiple_instances(self):
        """
        There are multiple fitting instances. Tests if the first is returned
        """
        dict_list = [
            {"node_name": "Load Input Image", "pillow_image": "image1"},
            {"node_name": "Load Input Image", "pillow_image": "image2"},
        ]
        identifying_key = "node_name"
        identifying_value = "Load Input Image"
        return_key = "pillow_image"

        result = extract_value_from_list_of_dicts(
            dict_list, identifying_key, identifying_value, return_key
        )

        self.assertEqual(result, "image1")

    def test_extract_value_from_list_of_dicts_no_instances(self):
        """
        There are no fitting instances. Tests if the default value is returned
        """
        dict_list = [{"node_name": "Load Input Image", "pillow_image": "image1"}]
        identifying_key = "node_name"
        identifying_value = "Load Mask Image"
        return_key = "pillow_image"
        default_value = "default_image"

        result = extract_value_from_list_of_dicts(
            dict_list, identifying_key, identifying_value, return_key, default_value
        )

        self.assertEqual(result, "default_image")

    def test_extract_value_from_list_of_dicts_no_instances_no_default_value(self):
        """
        There are no fitting instances. Since there is no default value, a ValueError is raised
        """
        dict_list = [{"node_name": "Load Input Image", "pillow_image": "image1"}]
        identifying_key = "node_name"
        identifying_value = "Load Mask Image"
        return_key = "pillow_image"

        with self.assertRaisesRegex(
            ValueError,
            "No dict with pair 'node_name': 'Load Mask Image' and key 'pillow_image' found.",
        ):
            extract_value_from_list_of_dicts(
                dict_list, identifying_key, identifying_value, return_key
            )

    def test_extract_value_from_list_of_dicts_wrong_return_value(self):
        """
        There is a fitting instance, but the return key is wrong. Tests if a ValueError is raised
        """
        dict_list = [{"node_name": "Load Input Image", "pillow_image": "image1"}]
        identifying_key = "node_name"
        identifying_value = "Load Mask Image"
        return_key = "image"

        with self.assertRaisesRegex(
            ValueError,
            "No dict with pair 'node_name': 'Load Mask Image' and key 'image' found.",
        ):
            extract_value_from_list_of_dicts(
                dict_list, identifying_key, identifying_value, return_key
            )


if __name__ == "__main__":
    unittest.main()
