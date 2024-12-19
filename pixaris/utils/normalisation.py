from PIL import Image


def normalize_image(image: Image, max_size=(1024, 1024)) -> Image:
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
