import os
import unittest
from unittest.mock import MagicMock
from PIL import Image
from pixaris.metrics.llm import LLMMetric


class LLMMetricTest(unittest.TestCase):
    def test_llm_correct(self):
        object_dir = "test/test_project/mock/input/"
        object_images = [
            Image.open(object_dir + image) for image in os.listdir(object_dir)
        ]
        style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(
            object_images
        )
        llm_metric = LLMMetric(
            object_images=object_images,
            style_images=style_images,
        )
        llm_metric._call_gemini = MagicMock(
            return_value='{"llm_reality": 1, "llm_similarity": 1, "llm_errors": 0, "llm_style": 1}'
        )

        metrics = llm_metric.calculate(object_images)

        self.assertIsInstance(metrics, dict)
        for name, value in metrics.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(value, float)

        self.assertEqual(metrics["llm_reality"], 1.0)
        self.assertEqual(metrics["llm_similarity"], 1.0)
        self.assertEqual(metrics["llm_errors"], 1.0)
        self.assertEqual(metrics["llm_style"], 1.0)


if __name__ == "__main__":
    unittest.main()
