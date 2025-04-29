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


if __name__ == "__main__":
    unittest.main()
