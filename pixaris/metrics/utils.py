from typing import Iterable
from PIL import Image


def dict_mean(input_dict_list: Iterable[dict]) -> dict:
    """
    Calculate the mean value for each key in a list of dictionaries.
    Args:
        input_dict_list Iterable[dict]: A list or iterator of dictionaries.
    Returns:
        dict: A dictionary containing the mean value for each key in the input dictionaries.
    """
    # check if all dicts have the same keys
    if len(set(map(frozenset, input_dict_list))) > 1:
        raise ValueError("All dictionaries must have the same keys.")

    means_dict = {}
    for key in input_dict_list[0].keys():
        values = [d[key] for d in input_dict_list]
        means_dict[key] = sum(values) / len(values)
    return means_dict


def normalize_image(image: Image.Image, max_size=(1024, 1024)) -> Image.Image:
    """
    Normalize the given image by placing it on a white background, scaling it while preserving aspect ratio,
    and returning the resulting image.
    Parameters:
    - image (PIL.Image): The input image to be normalized.
    Returns:
    - PIL.Image: The normalized image with a white background.
    """
    # place on white background
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Scale image while preserving aspect ratio
    image.thumbnail(max_size)

    # Create white background
    white_base = Image.new("RGB", max_size, (255, 255, 255))

    # Paste object image onto white background
    offset = ((max_size[0] - image.size[0]) // 2, (max_size[1] - image.size[1]) // 2)
    white_base.paste(image, offset, image)
    return white_base
