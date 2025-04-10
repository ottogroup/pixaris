from typing import Iterable
import numpy as np
from PIL.Image import Image

from pixaris.metrics.base import BaseMetric
from pixaris.metrics.utils import normalize_image


class IoUMetric(BaseMetric):
    def __init__(self, reference_images: Iterable[Image]):
        super().__init__()
        self.reference_images = reference_images

    def _iou(self, image1, image2) -> float:
        """
        Calculate the Intersection over Union (IoU) of two binary images.

        :param image1: The first binary image.
        :type image1: Image.Image
        :param image2: The second binary image.
        :type image2: Image.Image
        :return: The IoU value, which is the ratio of the intersection area to the union area of the two images.
          Returns 0 if the union is zero.
        :rtype: float
        """

        # Convert images to numpy arrays
        image1 = image1.point(lambda p: p > 125 and 255)
        image2 = image2.point(lambda p: p > 125 and 255)
        image1 = np.array(image1)
        image2 = np.array(image2)

        # Calculate intersection and union
        intersection = np.logical_and(image1, image2).sum()
        union = np.logical_or(image1, image2).sum()

        # Calculate IoU
        return intersection / union if union != 0 else 0

    def calculate(self, generated_images: Iterable[Image]) -> dict:
        """
        Calculate the Intersection over Union (IoU) for a list of generated images.

        :param generated_images: A list of generated images.
        :type generated_images: Iterable[Image]
        :return: A dictionary containing a single entry: "iou": the average IoU score.
        :rtype: dict
        """

        iou_scores = []
        for gen, ref in zip(generated_images, self.reference_images):
            # Normalize images and convert to binary
            ref = normalize_image(ref, gen.size).convert("1")
            gen = gen.convert("1")
            iou_score = self._iou(gen, ref)
            iou_scores.append(iou_score)

        return {"iou": np.mean(iou_scores) if iou_scores else 0}
