import unittest
from PIL import Image
from pixaris.utils.merge_dicts import merge_dicts


class TestMergeDicts(unittest.TestCase):
    def test_merge_dicts_with_matching_keys(self):
        """
        a has all information, b only adds additional images to existing key "pillow_images" in a.
        """
        a = {
            "workflow_apiformat_json": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ],
        }

        b = {
            "pillow_images": [
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ]
        }

        expected_result = {
            "workflow_apiformat_json": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ],
        }

        result = merge_dicts(a, b)
        self.assertDictEqual(result, expected_result)

    def test_merge_dicts_with_additional_key_in_dict_2(self):
        a = {
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ],
        }

        b = {
            "workflow_apiformat_json": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ],
        }

        expected_result = {
            "workflow_apiformat_json": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_project/mock/input/chinchilla.png"
                    ),
                },
            ],
        }

        result = merge_dicts(a, b)
        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
