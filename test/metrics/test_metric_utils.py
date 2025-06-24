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

    def test_normalize_image_sizes_and_background(self):
        from PIL import Image
        from pixaris.metrics.utils import normalize_image

        img = Image.new("RGB", (200, 100), "red")
        result = normalize_image(img, max_size=(300, 300))

        self.assertEqual(result.size, (300, 300))
        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        center = (150, 150)
        self.assertEqual(result.getpixel(center), (255, 0, 0))

    def test_normalize_image_downscale(self):
        from PIL import Image
        from pixaris.metrics.utils import normalize_image

        img = Image.new("RGB", (600, 400), "blue")
        result = normalize_image(img, max_size=(300, 300))
        self.assertEqual(result.size, (300, 300))

    def test_dict_mean_different_lengths(self):
        dicts = [{"a": 1, "b": 2}, {"a": 2, "b": 2, "c": 3}]
        self.assertRaises(ValueError, dict_mean, dicts)


if __name__ == "__main__":
    unittest.main()
