import unittest
from PIL import Image
from pixaris.utils.merge_dicts import merge_dicts


class TestMergeDicts(unittest.TestCase):
    def test_merge_dicts_with_matching_keys(self):
        """
        a has all information, b only adds additional images to existing key "pillow_images" in a.
        """
        a = {
            "workflow_apiformat_path": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
            ],
        }

        b = {
            "pillow_images": [
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
            ]
        }

        expected_result = {
            "workflow_apiformat_path": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
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
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
            ],
        }

        b = {
            "workflow_apiformat_path": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
            ],
        }

        expected_result = {
            "workflow_apiformat_path": "workflow.json",
            "pillow_images": [
                {
                    "node_name": "Load Object Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
                {
                    "node_name": "Load Composition Image",
                    "pillow_image": Image.open(
                        "test/test_eval_set/mock/input/model_01.png"
                    ),
                },
            ],
        }

        result = merge_dicts(a, b)
        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
