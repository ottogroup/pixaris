from typing import Iterable

import numpy as np
from pixaris.metrics.base import BaseMetric
from PIL.Image import Image


class SaturationComparisonByMaskMetric(BaseMetric):
    """
    Calculate the saturation difference between the masked part and the unmasked part of an image.
    The metric is calculated as the absolute difference between the average saturation of the masked part
    and the unmasked part of the image.
    The result is a number between 0 and 1 with 1 being the best possible score and 0 being the worst score.
    """

    def __init__(self, mask_images: Iterable[Image]):
        super().__init__()
        self.mask_images = mask_images

    def _saturation_difference(self, image: Image, mask: Image) -> float:
        """
        Calculate the differences of saturation in the masked part and the unmasked part of the image.
        a number close to 1 means the saturation is close, a number close to 0 means the saturation is very different.

        :param image: The input image.
        :type image: Image.Image
        :param mask: The mask image.
        :type mask: Image.Image
        :return: The brightness value of the image.
        :rtype: float
        """
        # convert image to HSV
        binary_mask = np.array(mask.convert("L").point(lambda p: p > 125 and 255)) / 255
        inverted_mask = 1 - binary_mask

        _, saturation, _ = image.convert("HSV").split()
        mean_masked_saturation = np.average(np.array(saturation), weights=binary_mask)
        mean_inverted_saturation = np.average(
            np.array(saturation), weights=inverted_mask
        )
        return (
            abs(mean_masked_saturation - mean_inverted_saturation) / 255
        )  # natural a number between 0 and 1

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the saturation score of a list of generated images.
        For each image we calculate the average saturation of the masked part and the unmasked part,
        and return the absolute difference between them.
        Will be normed to 0-1.

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing a single entry: "saturation_difference": the average saturation_difference score.
        :rtype: dict
        """
        saturation_scores = []
        for gen, mask in zip(generated_images, self.mask_images):
            brightness_difference = self._saturation_difference(gen, mask)
            saturation_scores.append(brightness_difference)

        return {
            "saturation_difference": np.mean(saturation_scores)
            if saturation_scores
            else 0
        }


class SaturationWithoutMaskMetric(BaseMetric):
    """
    Calculates mean and variance of the saturation of the image.
    """

    def _saturation(self, image: Image) -> float:
        """
        Calculate the mean and variance of the saturation of the image. Normed to 0-1.

        :param image: The input image.
        :type image: Image.Image
        :return: mean and variance of the saturation
        :rtype: tuple[float, float]
        """
        _, saturation, _ = image.convert("HSV").split()
        saturation = np.array(saturation) / 255
        mean = np.mean(np.array(saturation))
        var = np.var(np.array(saturation))
        return (mean, var)

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the saturation score of a list of generated images.
        For each image we calculate the mean and variance of the saturation,
        and return the average of them. The results is 2 numbers between 0 and 1

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing different saturation statistics:
        :rtype: dict
        """
        saturation_scores = []
        for gen in generated_images:
            brightness_difference = self._saturation(gen)
            saturation_scores.append(brightness_difference)

        mean_values = np.mean(saturation_scores, axis=0)
        return {"saturation_mean": mean_values[0], "saturation_var": mean_values[1]}
