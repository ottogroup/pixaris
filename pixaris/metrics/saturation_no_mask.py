from typing import Iterable

import numpy as np
from pixaris.metrics.base import BaseMetric
from PIL.Image import Image


class SaturationWithoutMaskMetric(BaseMetric):
    """
    Calculates some statistics of the saturation of the image.
    provides the mean, variance, min, max and difference of the saturation of the image.
    """

    def _saturation(self, image: Image) -> float:
        """
        Calculate the mean, variance, min, max and difference of the saturation of the image.

        :param image: The input image.
        :type image: Image.Image
        :return: mean, variance, min, max and difference of the saturation
        :rtype: tuple[float, float, float, float, float]
        """
        hue, saturation, brightness = image.convert("HSV").split()
        mean = np.mean(np.array(saturation))
        var = np.var(np.array(saturation))
        min = np.min(np.array(saturation))
        max = np.max(np.array(saturation))
        diff = max - min
        return (mean, var, min, max, diff)

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the saturation score of a list of generated images.
        For each image we calculate the mean, variance, min, max and difference of the saturation,
        and return the average of them.
        The result is 5 numbers between 0 and 1.

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing different saturation statistics:
        :rtype: dict
        """
        saturation_scores = []
        for gen in generated_images:
            brightness_difference = self._saturation(gen)
            saturation_scores.append(brightness_difference)

        mean_values = np.mean(saturation_scores)
        return {
            "mean_saturation": mean_values[0],
            "var_saturation": mean_values[1],
            "min_saturation": mean_values[2],
            "max_saturation": mean_values[3],
            "difference_in_saturation": mean_values[4],
        }
