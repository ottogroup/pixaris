from typing import Iterable, Union, Callable

import numpy as np
from pixaris.metrics.base import BaseMetric
from PIL.Image import Image


def _luminescence(image: Image, luminescence_definition) -> np.array:
    """
    calculates the luminescence values for an image

    :param image: input Image
    :type image: Image
    :return: luminescence values per pixel
    :rtype: np.array
    """
    match luminescence_definition:
        case "1":

            def luminescence(x):
                # L = (0.2126*R + 0.7152*G + 0.0722*B)
                return 0.2126 * x[:, :, 0] + 0.7152 * x[:, :, 1] + 0.0722 * x[:, :, 2]

            image = np.asarray(image)
            return luminescence(image)
        case "2":
            # L = (0.299*R + 0.587*G + 0.114*B)
            return np.asarray(image.convert("L"))
        case "3":

            def luminescence(x):
                # L = sqrt( 0.299*R^2 + 0.587*G^2 + 0.114*B^2 )
                return np.sqrt(
                    0.299 * x[:, :, 0] ** 2
                    + 0.587 * x[:, :, 1] ** 2
                    + 0.114 * x[:, :, 2] ** 2
                )

            image = np.asarray(image)
            return luminescence(image)
        case _ if callable(luminescence_definition):
            return np.asarray(luminescence_definition(image))


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
        luminescence_definition: Union[str, Callable] = "2",
    ):
        super().__init__()
        self.mask_images = mask_images
        assert luminescence_definition in ["1", "2", "3"] or callable(
            luminescence_definition
        )
        self.luminescence_definition = luminescence_definition

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

        luminescence = _luminescence(image, self.luminescence_definition)
        mean_masked_luminescence = np.average(luminescence, weights=binary_mask)
        mean_inverted_luminescence = np.average(luminescence, weights=inverted_mask)
        return (
            abs(mean_masked_luminescence - mean_inverted_luminescence) / 255
        )  # natural a number between 0 and 1

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the luminescence score of a list of generated images.
        For each image we calculate the average luminescence of the masked part and the unmasked part,
        and return the absolute difference between them. luminescence is a number between 0 and 1, so
        the result is also a number between 0 and 1. We invert them to make 1 the best score and 0 the worst.

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

    def __init__(self, luminescence_definition: Union[str, Callable] = "2"):
        super().__init__()
        assert luminescence_definition in ["1", "2", "3"] or callable(
            luminescence_definition
        )
        self.luminescence_definition = luminescence_definition

    def _luminescence_mean_and_var(self, image: Image) -> float:
        """
        Calculate the mean and variance of the luminescence of the image.

        :param image: The input image.
        :type image: Image.Image
        :return: mean and variance of the luminescence
        :rtype: tuple[float, float]
        """
        luminescence = _luminescence(image, self.luminescence_definition) / 255
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
