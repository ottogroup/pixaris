from typing import Iterable

import numpy as np
from pixaris.metrics.base import BaseMetric
from PIL.Image import Image


def _luminescence(image: Image) -> np.array:
    """
    calculates the luminescence values for an image
    definition luminance: https://www.101computing.net/colour-luminance-and-contrast-ratio/

    :param image: input Image
    :type image: Image
    :return: luminescence values per pixel, normed between 0 and 1
    :rtype: np.array
    """
    image = np.asarray(image) / 255
    image = np.where(image <= 0.03928, image / 12.92, ((image + 0.055) / 1.055) ** 2.4)
    return 0.2126 * image[:, :, 0] + 0.7152 * image[:, :, 1] + 0.0722 * image[:, :, 2]


class LuminescenceComparisonByMaskMetric(BaseMetric):
    """
    Calculate the luminescence difference between the masked part and the unmasked part of an image.
    The metric is calculated as the absolute difference between the average luminescence of the masked part
    and the unmasked part of the image.
    The result is a number between 0 and 1 with 1 being the best possible score and 0 being the worst score.
    """

    def __init__(
        self,
        mask_images: Iterable[Image],
    ):
        super().__init__()
        self.mask_images = mask_images

    def _luminescence_difference(self, image: Image, mask: Image) -> float:
        """
        Calculate the differences of luminescence in the masked part and the unmasked part of the image.
        a number close to 1 means the luminescence is close, a number close to 0 means the luminescence is very different.

        :param image: The input image.
        :type image: Image.Image
        :param mask: The mask image.
        :type mask: Image.Image
        :return: The luminescence difference value of the image.
        :rtype: float
        """
        binary_mask = np.array(mask.convert("L").point(lambda p: p > 125 and 255)) / 255
        inverted_mask = 1 - binary_mask

        luminescence = _luminescence(image)
        mean_masked_luminescence = np.average(luminescence, weights=binary_mask)
        mean_inverted_luminescence = np.average(luminescence, weights=inverted_mask)
        return 1 - abs(
            mean_masked_luminescence - mean_inverted_luminescence
        )  # natural a number between 0 and 1

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the luminescence score of a list of generated images.
        For each image we calculate the average luminescence of the masked part and the unmasked part,
        and return the absolute difference between them. Luminescence is a number between 0 and 1, so
        the result is also a number between 0 and 1. We invert them to make 1 the best score (minimal difference in luminescence of masked and unmasked part) and 0 the worst (maximal difference).

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing a single entry: "luminescence_difference": the average luminescence_difference score.
        :rtype: dict
        """
        luminescence_scores = []
        for gen, mask in zip(generated_images, self.mask_images):
            brightness_difference = self._luminescence_difference(gen, mask)
            luminescence_scores.append(brightness_difference)

        return {
            "luminescence_difference": np.mean(luminescence_scores)
            if luminescence_scores
            else 0
        }


class LuminescenceWithoutMaskMetric(BaseMetric):
    """
    Calculates mean and variance of the luminescence of the image.
    """

    def _luminescence_mean_and_var(self, image: Image) -> float:
        """
        Calculate the mean and variance of the luminescence of the image.

        :param image: The input image.
        :type image: Image.Image
        :return: mean and variance of the luminescence
        :rtype: tuple[float, float]
        """
        luminescence = _luminescence(image)
        mean = np.mean(luminescence)
        var = np.var(luminescence)
        return [mean, var]

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the luminescence score of a list of generated images.
        For each image we calculate the mean and variance of the luminescence,
        and return the average of them. The results is 2 numbers between 0 and 1

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing different luminescence statistics:
        :rtype: dict
        """
        luminescence_scores = []
        for gen in generated_images:
            brightness_difference = self._luminescence_mean_and_var(gen)
            luminescence_scores.append(brightness_difference)

        mean_values = np.mean(np.array(luminescence_scores), axis=0)
        return {"luminescence_mean": mean_values[0], "luminescence_var": mean_values[1]}
