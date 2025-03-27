import os
from PIL import Image
import unittest

from pixaris.metrics.iou import IoUMetric


class IOUMetricTest(unittest.TestCase):
    def test_iou_same(self):
        """
        iou should be 1 if images and masks are the same
        """
        image_path = "test/test_dataset/mock/mask/"
        images = [Image.open(image_path + name) for name in os.listdir(image_path)]

        metric = IoUMetric(images)

        metrics = metric.calculate(images)

        self.assertEqual(metrics["iou"], 1.0)

    def test_iou_different(self):
        """
        iou should be between 0 and 1 if images and masks are different
        """
        image = "test/test_dataset/mock/mask/model_01.png"
        images = [Image.open(image)]
        mask_images = [Image.new("1", image.size, 255) for image in images]

        metric = IoUMetric(images)

        metrics = metric.calculate(mask_images)

        self.assertLessEqual(metrics["iou"], 1.0)
        self.assertGreaterEqual(metrics["iou"], 0.0)


if __name__ == "__main__":
    unittest.main()
