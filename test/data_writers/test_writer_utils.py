import unittest
from pixaris.utils.merge_dicts import merge_dicts


class TestUtils(unittest.TestCase):
    def test_merge_dicts_with_matching_keys(self):
        """
        a has all information, b only adds additional images to exisitng key "image_paths" in a.
        """
        a = {
            "workflow_apiformat_path": "workflow.json",
            "image_paths": [
                {
                    "node_name": "Load Object Image",
                    "image_path": "eval_data/priyasofa2/object/priya2_01.jpeg",
                },
            ],
        }

        b = {
            "image_paths": [
                {
                    "node_name": "Load Composition Image",
                    "image_path": "image.png",
                },
            ]
        }

        expected_result = {
            "workflow_apiformat_path": "workflow.json",
            "image_paths": [
                {
                    "node_name": "Load Object Image",
                    "image_path": "eval_data/priyasofa2/object/priya2_01.jpeg",
                },
                {
                    "node_name": "Load Composition Image",
                    "image_path": "image.png",
                },
            ],
        }

        result = merge_dicts(a, b)
        self.assertDictEqual(result, expected_result)

    def test_merge_dicts_with_additional_key_in_dict_2(self):
        a = {
            "image_paths": [
                {
                    "node_name": "Load Object Image",
                    "image_path": "eval_data/priyasofa2/object/priya2_01.jpeg",
                },
            ],
        }

        b = {
            "workflow_apiformat_path": "workflow.json",
            "image_paths": [
                {
                    "node_name": "Load Composition Image",
                    "image_path": "composition.jpeg",
                },
            ],
        }

        expected_result = {
            "workflow_apiformat_path": "workflow.json",
            "image_paths": [
                {
                    "node_name": "Load Object Image",
                    "image_path": "eval_data/priyasofa2/object/priya2_01.jpeg",
                },
                {
                    "node_name": "Load Composition Image",
                    "image_path": "composition.jpeg",
                },
            ],
        }

        result = merge_dicts(a, b)
        self.assertDictEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
