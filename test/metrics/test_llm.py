import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
from pixaris.metrics.llm import BaseLLMMetric, SimilarityLLMMetric, StyleLLMMetric
import itertools


class LLMMetricTest(unittest.TestCase):
    def test_llm_correct(self):
        object_dir = "test/test_project/mock/input/"
        object_images = [
            Image.open(object_dir + image) for image in os.listdir(object_dir)
        ]
        style_images = [Image.open("test/assets/test_inspo_image.jpg")] * len(
            object_images
        )
        llm_metric = BaseLLMMetric(
            prompt="test prompt",
            object_images=object_images,
            style_images=style_images,
        )
        llm_metric._call_gemini = MagicMock(return_value='{"base_llm_metric": 1.0}')

        metrics = llm_metric.calculate(object_images)

        self.assertIsInstance(metrics, dict)
        for name, value in metrics.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(value, float)

        self.assertEqual(metrics["base_llm_metric"], 1.0)

    def test_llm_wrong_images(self):
        """
        if the number of object images and style images are not the same, it should raise a ValueError
        """
        object_dir = "test/test_project/mock/input/"
        object_images = [
            Image.open(object_dir + image) for image in os.listdir(object_dir)
        ]
        style_images = [Image.open("test/assets/test_inspo_image.jpg")] * (
            len(object_images) + 1
        )
        llm_metric = BaseLLMMetric(
            prompt="test prompt",
            object_images=object_images,
            style_images=style_images,
        )
        llm_metric._call_gemini = MagicMock(return_value='{"base_llm_metric": 1.0}')

        self.assertRaises(
            ValueError,
            llm_metric.calculate,
            object_images,
        )

    @patch("pixaris.metrics.llm.BaseLLMMetric._call_gemini")
    def test_similarity_llm_metric(self, mock_call_gemini):
        """
        Test the SimilarityLLMMetric class to ensure it calculates the similarity metric correctly.
        """
        object_dir = "test/test_project/mock/input/"
        object_images = [
            Image.open(object_dir + image) for image in os.listdir(object_dir)
        ]
        llm_metric = SimilarityLLMMetric(
            reference_images=object_images,
        )
        mock_call_gemini.side_effect = itertools.cycle(
            ['{"similarity_llm_metric": 1.0}'] * (len(object_images) - 1)
            + ['{"similarity_llm_metric": 0.0}']
        )

        metrics = llm_metric.calculate(object_images)

        self.assertIsInstance(metrics, dict)
        for name, value in metrics.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(value, float)

        self.assertEqual(metrics["similarity_llm_metric"], 0.75)

    # @patch("pixaris.metrics.llm.BaseLLMMetric._call_gemini")
    def test_style_llm_metric(self, ): # mock_call_gemini
        """
        Test the SimilarityLLMMetric class to ensure it calculates the similarity metric correctly.
        """
        object_dir = "test/test_project/mock/input/"
        object_images = [
            Image.open(object_dir + image) for image in os.listdir(object_dir)
        ]
        llm_metric = StyleLLMMetric(
            reference_images=object_images,
        )
        # mock_call_gemini.side_effect = itertools.cycle(
        #     ['{"similarity_llm_metric": 1.0}'] * (len(object_images) - 1)
        #     + ['{"similarity_llm_metric": 0.0}']
        # )

        metrics = llm_metric.calculate(object_images)

        self.assertIsInstance(metrics, dict)
        for name, value in metrics.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(value, float)

        self.assertEqual(metrics["similarity_llm_metric"], 0.75)

if __name__ == "__main__":
    # unittest.main()
    LLMMetricTest().test_style_llm_metric()
