from pixaris.utils.helpers import merge_dicts


def test_merge_dicts_with_matching_keys():
    """
    a has all information, b only adds additional images to exisitng key "image_paths" in a.
    """
    a = {
        "workflow_apiformat_path": "workflow.json",
        "image_paths": [
            {
                "node_name": "Load Object Image",
                "image_path": "eval_data/priyasofa2/Object/priya2_01.jpeg",
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
                "image_path": "eval_data/priyasofa2/Object/priya2_01.jpeg",
            },
            {
                "node_name": "Load Composition Image",
                "image_path": "image.png",
            },
        ],
    }

    result = merge_dicts(a, b)
    assert result == expected_result


def test_merge_dicts_with_additional_key_in_dict_2():
    a = {
        "image_paths": [
            {
                "node_name": "Load Object Image",
                "image_path": "eval_data/priyasofa2/Object/priya2_01.jpeg",
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
                "image_path": "eval_data/priyasofa2/Object/priya2_01.jpeg",
            },
            {
                "node_name": "Load Composition Image",
                "image_path": "composition.jpeg",
            },
        ],
    }

    result = merge_dicts(a, b)
    assert result == expected_result
