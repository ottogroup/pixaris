from PIL import Image
from google.cloud import storage
import io


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


def open_image(image_file_path, norm_image=False) -> Image.Image:
    """Load Image from gcs or local path."""
    if image_file_path.startswith("gs://"):
        img = download_image_from_gcs_path(image_file_path)
    else:
        img = Image.open(image_file_path)

    if norm_image:
        img = normalize_image(img)

    return img


def download_image_from_bucket(bucket_name: str, image_path: str) -> Image:
    """
    Download an image from a Google Cloud Storage bucket. The image is returned as a PIL Image object.

    Args:
        bucket_name (str): The name of the bucket.
        image_path (str): The path to the image in the bucket.
    Returns:
        Image: The image as a PIL Image object.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_path)
    image_content = blob.download_as_string()

    return Image.open(io.BytesIO(image_content))


def download_image_from_gcs_path(image_path: str) -> Image:
    """
    Download an image from a Google Cloud Storage path. The image is returned as a PIL Image object.

    Args:
        image_path (str): The path to the image in the bucket. Needs to start with 'gs://'.
    Returns:
        Image: The image as a PIL Image object.
    """
    image_path = image_path.replace("gs://", "")
    bucket_name, image_path = image_path.split("/", 1)
    return download_image_from_bucket(bucket_name, image_path)
