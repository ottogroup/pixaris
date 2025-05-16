from io import BytesIO
from PIL import Image


def extract_value_from_list_of_dicts(
    dict_list,
    itentifying_key,
    identifying_value,
    return_key,
    default_value=None,
):
    """
    Extracts a value from a list of dictionaries based on a key-value pair.
    This function searches through a list of dictionaries and returns the value associated with a specified key
    for the first dictionary that matches a given key-value pair. If no such dictionary is found, it returns a default value.
    If the default value is not provided and no matching dictionary is found, a ValueError is raised.

    :param dict_list: A list of dictionaries to search through.
    :type dict_list: list[dict]
    :param itentifying_key: The key to identify the dictionary.
    :type itentifying_key: _any
    :param identifying_value: The value to match against the identifying key.
    :type identifying_value: _any
    :param return_key: The key whose value is to be returned from the matching dictionary.
    :type return_key: _any
    :param default_value: The value to return if no matching dictionary is found. If not provided, defaults to None.
    :type default_value: _any, optional
    :raises ValueError: If no matching dictionary is found and no default value is provided.
    :return: The value associated with the return key from the matching dictionary, or the default value if no match is found.
    :rtype: _any
    """
    return_value = next(
        (
            param[return_key]
            for param in dict_list
            if param[itentifying_key] == identifying_value
        ),
        default_value,
    )
    if return_value is None:
        raise ValueError(
            f"No dict with pair '{itentifying_key}': '{identifying_value}' and key '{return_key}' found."
        )
    return return_value


def encode_image_to_bytes(pillow_image: Image.Image) -> bytes:
    """
    Encodes a PIL image to bytes.

    :param pillow_image: The PIL image.
    :type pillow_image: PIL.Image.Image

    :return: Byte array representation of the image.
    :rtype: bytes
    """
    imgByteArr = BytesIO()
    pillow_image.save(imgByteArr, format=pillow_image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr
