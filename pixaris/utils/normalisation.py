from PIL import Image


def normalize_image(image: Image, max_size=(1024, 1024)) -> Image:
    """
    Normalize the given image by placing it on a white background, scaling it while preserving aspect ratio,
      and returning the resulting image.
    
    :param image: The input image to be normalized.
    :type image: PIL.Image.Image
    :param max_size: The maximum size of the output image, defaults to (1024, 1024).
    :type max_size: tuple[int, int]
    :return: The normalized image with a white background.
    :rtype: PIL.Image.Image
    """
    # place on white background
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Scale image while preserving aspect ratio
    image.thumbnail(max_size, resample=Image.LANCZOS)

    # Create white background
    white_base = Image.new("RGB", max_size, (255, 255, 255))

    # Paste object image onto white background
    offset = ((max_size[0] - image.size[0]) // 2, (max_size[1] - image.size[1]) // 2)
    white_base.paste(image, offset, image)
    return white_base
