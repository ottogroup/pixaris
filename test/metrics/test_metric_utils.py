import unittest

from pixaris.metrics.utils import dict_mean


class TestHelpers(unittest.TestCase):
    def test_dict_mean(self):
        dicts = [{"a": 1, "b": 2}, {"a": 2, "b": 5}]
        result = dict_mean(dicts)
        self.assertDictEqual(result, {"a": 1.5, "b": 3.5})

    def test_dict_mean_single_dict(self):
        dicts = [{"a": 1, "b": 2}]
        result = dict_mean(dicts)
        self.assertDictEqual(result, {"a": 1, "b": 2})

    def test_dict_mean_wrong_keys(self):
        dicts = [{"a": 1, "b": 2}, {"a": 2, "c": 3}]
        self.assertRaises(ValueError, dict_mean, dicts)

    def test_dict_mean_different_lengths(self):
        dicts = [{"a": 1, "b": 2}, {"a": 2, "b": 2, "c": 3}]
        self.assertRaises(ValueError, dict_mean, dicts)


if __name__ == "__main__":
    unittest.main()
