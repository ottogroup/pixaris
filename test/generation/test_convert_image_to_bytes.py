import unittest
from PIL import Image
import io

from pixaris.generation.utils import encode_image_to_bytes


class TestImageToBytes(unittest.TestCase):
    def test_image_to_bytes(self):
        # Create a simple image for testing
        img = Image.open("test/test_project/mock/input/chinchilla.png")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        # Convert the image to bytes
        result = encode_image_to_bytes(img)

        # Check if the result is equal to the original byte array
        self.assertEqual(result, img_byte_arr)


if __name__ == "__main__":
    unittest.main()
