import os
from PIL import Image
import unittest

from pixaris.metrics.saturation import (
    SaturationComparisonByMaskMetric,
    SaturationWithoutMaskMetric,
)


class TestSaturationComparisonByMaskMetric(unittest.TestCase):
    def test_saturation_difference(self):
        """
        testing saturation difference metric
        """
        image_path = "test/test_project/mock/input/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]

        metric = SaturationComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertLessEqual(metrics["saturation_difference"], 1.0)
        self.assertGreaterEqual(metrics["saturation_difference"], 0.0)

    def test_saturation_maximal_difference(self):
        """
        testing saturation difference metric worst case. Should return 0 if saturation difference is maximal
        """
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]
        images = [
            Image.composite(
                Image.new("HSV", mask.size, (100, 255, 200)),  # Max saturation
                Image.new("HSV", mask.size, (100, 0, 200)),  # Min saturation
                mask.convert("1"),  # Use mask as a binary mask
            )
            for mask in masks
        ]

        metric = SaturationComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertEqual(metrics["saturation_difference"], 0.0)

    def test_saturation_minimal_difference(self):
        """
        testing saturation difference metric best case. Should return 1 if saturation is the same
        """
        mask_path = "test/test_project/mock/mask/"
        masks = [Image.open(mask_path + name) for name in os.listdir(mask_path)]
        images = [Image.new("RGB", mask.size, "red") for mask in masks]

        metric = SaturationComparisonByMaskMetric(masks)

        metrics = metric.calculate(images)

        self.assertEqual(metrics["saturation_difference"], 1.0)


class TestSaturationWithoutMaskMetric(unittest.TestCase):
    def test_calculate(self):
        """
        testing saturation without mask metric
        """
        image_path = "test/test_project/mock/input/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]

        metric = SaturationWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertLessEqual(metrics["saturation_mean"], 1.0)
        self.assertGreaterEqual(metrics["saturation_mean"], 0.0)
        self.assertLessEqual(metrics["saturation_var"], 1.0)
        self.assertGreaterEqual(metrics["saturation_var"], 0.0)

    def test_high_saturation(self):
        """
        testing saturation yields 1 if all images have max saturation
        """
        images = [Image.new("HSV", (100, 100), (100, 255, 200)) for _ in range(4)]

        metric = SaturationWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertEqual(metrics["saturation_mean"], 1.0)
        self.assertEqual(metrics["saturation_var"], 0.0)

    def test_low_saturation(self):
        """
        testing saturation yields 0 if all images have minimum saturation
        """
        images = [Image.new("HSV", (100, 100), (100, 0, 200)) for _ in range(4)]

        metric = SaturationWithoutMaskMetric()

        metrics = metric.calculate(images)

        self.assertEqual(metrics["saturation_mean"], 0.0)
        self.assertEqual(metrics["saturation_var"], 0.0)


if __name__ == "__main__":
    unittest.main()
