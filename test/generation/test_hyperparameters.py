# TODO: merge with test_generation after merge TIGA-550 and TIGA-643 (for merge conflict reasons)

import unittest
from pixaris.utils.hyperparameters import (
    expand_hyperparameters,
    generate_hyperparameter_grid,
)


class TestHyperparameters(unittest.TestCase):
    def test_expand_hyperparameters(self):
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
