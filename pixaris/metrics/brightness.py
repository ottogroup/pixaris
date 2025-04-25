from typing import Iterable

import numpy as np
from pixaris.metrics.base import BaseMetric
from PIL.Image import Image


class SaturationMetric(BaseMetric):
    def __init__(self, mask_images: Iterable[Image]):
        super().__init__()
        self.mask_images = mask_images

    def _saturation_difference(self, image: Image, mask: Image) -> float:
        """
        Calculate the differences of saturation in the masked part and the unmasked part of the image.

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

        hue, saturation, brightness = image.convert("HSV").split()
        mean_masked_saturation = np.mean(np.array(saturation) * binary_mask)
        mean_inverted_saturation = np.mean(np.array(saturation) * inverted_mask)
        return abs(
            mean_masked_saturation - mean_inverted_saturation
        )  # natural a number between 0 and 1

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the brightness of a list of generated images.

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing a single entry: "brightness": the average brightness score.
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
