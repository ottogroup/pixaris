import os
from PIL import Image
import unittest

import numpy as np

from pixaris.metrics.luminescence import (
    LuminescenceComparisonByMaskMetric,
    LuminescenceWithoutMaskMetric,
    _luminescence,
)


class TestLuminescenceComparisonByMaskMetric(unittest.TestCase):
    def test_luminescence_1(self):
        """
        testing luminescence with definition 1
        """
        image_path = "test/test_project/mock/input/sillygoose.png"
        image = Image.open(image_path)
        luminescence = _luminescence(image, "1")

        self.assertEqual(luminescence.shape, (image.size[1], image.size[0]))
        self.assertIsInstance(luminescence, np.ndarray)
        self.assertLessEqual(luminescence.max(), 255.0)
        self.assertGreaterEqual(luminescence.min(), 0.0)

    def test_luminescence_2(self):
        """
        testing luminescence with definition 2
        """
        image_path = "test/test_project/mock/input/sillygoose.png"
        image = Image.open(image_path)
        luminescence = _luminescence(image, "2")

        self.assertEqual(luminescence.shape, (image.size[1], image.size[0]))
        self.assertIsInstance(luminescence, np.ndarray)
        self.assertLessEqual(luminescence.max(), 255.0)
        self.assertGreaterEqual(luminescence.min(), 0.0)

    def test_luminescence_3(self):
        """
        testing luminescence with definition 3
        """
        image_path = "test/test_project/mock/input/sillygoose.png"
        image = Image.open(image_path)
        luminescence = _luminescence(image, "3")

        self.assertEqual(luminescence.shape, (image.size[1], image.size[0]))
        self.assertIsInstance(luminescence, np.ndarray)
        self.assertLessEqual(luminescence.max(), 255.0)
        self.assertGreaterEqual(luminescence.min(), 0.0)

    def test_luminescence_callable(self):
        """
        testing luminescence with definition 1
        """
        image_path = "test/test_project/mock/input/sillygoose.png"
        image = Image.open(image_path)
        luminescence = _luminescence(image, lambda image: image.convert("L"))

        self.assertEqual(luminescence.shape, (image.size[1], image.size[0]))
        self.assertIsInstance(luminescence, np.ndarray)
        self.assertLessEqual(luminescence.max(), 255.0)
        self.assertGreaterEqual(luminescence.min(), 0.0)

    def test_luminescence_difference(self):
        """
        testing luminescence difference metric
        """
        image_path = "test/test_project/mock/input/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]

        metric = LuminescenceComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertLessEqual(metrics["luminescence_difference"], 1.0)
        self.assertGreaterEqual(metrics["luminescence_difference"], 0.0)

    def test_luminescence_difference_worst_case(self):
        """
        testing luminescence difference metric
        """
        image_path = "test/test_project/mock/mask/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]

        metric = LuminescenceComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertEqual(metrics["luminescence_difference"], 1.0)


class TestLuminescenceComparisonNoMaskMetric(unittest.TestCase):
    def test_calculate(self):
        """
        testing luminescence without mask metric
        """
        image_path = "test/test_project/mock/input/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]

        metric = LuminescenceWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertLessEqual(metrics["luminescence_mean"], 1.0)
        self.assertGreaterEqual(metrics["luminescence_mean"], 0.0)
        self.assertLessEqual(metrics["luminescence_var"], 1.0)
        self.assertGreaterEqual(metrics["luminescence_var"], 0.0)


if __name__ == "__main__":
    unittest.main()
