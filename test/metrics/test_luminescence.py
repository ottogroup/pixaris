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
    def test_luminescence(self):
        """
        testing luminescence function. Should produce a numpy array with the same shape
        as the input image and values between 0 and 1
        """
        image_path = "test/test_project/mock/input/sillygoose.png"
        image = Image.open(image_path)
        luminescence = _luminescence(image)

        self.assertEqual(luminescence.shape, (image.size[1], image.size[0]))
        self.assertIsInstance(luminescence, np.ndarray)
        self.assertLessEqual(luminescence.max(), 1.0)
        self.assertGreaterEqual(luminescence.min(), 0.0)

    def test_luminescence_difference(self):
        """
        testing luminescence difference metric. Should produce valued between 0 and 1
        """
        image_path = "test/test_project/mock/input/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]

        metric = LuminescenceComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertLessEqual(metrics["luminescence_difference"], 1.0)
        self.assertGreaterEqual(metrics["luminescence_difference"], 0.0)

    def test_luminescence_maximal_difference(self):
        """
        testing luminescence difference metric with maximal luminence difference inside and outside of mask
        Should return 0 if the difference of luminescence is maximal
        """
        image_path = "test/test_project/mock/mask/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]

        metric = LuminescenceComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertEqual(metrics["luminescence_difference"], 0.0)

    def test_luminescence_minimal_difference(self):
        """
        testing luminescence difference metric with minimal luminence difference inside and outside of mask
        Should return 1 if luminescence is the same
        """
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]
        images = [Image.new("RGB", mask.size, "white") for mask in masks]

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

    def test_high_luminescence(self):
        """
        testing luminescence yields 1 if all images are white
        """
        images = [Image.new("RGB", (100, 100), "white") for _ in range(4)]

        metric = LuminescenceWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertEqual(metrics["luminescence_mean"], 1.0)
        self.assertEqual(metrics["luminescence_var"], 0.0)

    def test_low_luminescence(self):
        """
        testing luminescence yields 0 if all images are black
        """
        images = [Image.new("RGB", (100, 100), "black") for _ in range(4)]

        metric = LuminescenceWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertEqual(metrics["luminescence_mean"], 0.0)
        self.assertEqual(metrics["luminescence_var"], 0.0)


if __name__ == "__main__":
    unittest.main()
