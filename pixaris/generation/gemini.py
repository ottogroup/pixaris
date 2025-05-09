import time
import traceback
from typing import List, Optional
from pixaris.generation.base import ImageGenerator
from PIL import Image
from io import BytesIO
import vertexai
from google.genai import Client, types
from vertexai.generative_models import Image as VertexImage


class GeminiGenerator(ImageGenerator):
    """
    GeminiGenerator is a class that generates images using the Google Gemini API.

    :param gcp_project_id: The Google Cloud Platform project ID.
    :type gcp_project_id: str
    :param gcp_location: The Google Cloud Platform location.
    :type gcp_location: str
    """

    def __init__(
        self,
        gcp_project_id: str,
        gcp_location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-exp",
        verbose: bool = False,
    ):
        self.gcp_project_id = gcp_project_id
        # todo: once gemini is available in other regions, remove this check and the default value for gcp_location
        if gcp_location != "us-central1":
            print(
                f"Warning: Currently, gemini is only supported in 'us-central1'. Setting '{gcp_location}' can result in errors."
            )
        self.gcp_location = gcp_location
        self.model_name = model_name
        self.verbose = verbose

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ):
        """
        Validates the provided dataset and parameters for image generation.

        :param dataset: A list of dicts containing image information.
        :type dataset: List[dict[str, List[dict[str, Image.Image]]]
        :param parameters: A list of dictionaries containing generation parameters.
        :type parameters: list[dict[str, str, any]]
        :raises ValueError: If the validation fails for any reason (e.g., missing fields).
        """

        # Validate dataset
        if not dataset:
            raise ValueError("Dataset cannot be empty.")

        for entry in dataset:
            if not isinstance(entry, dict):
                raise ValueError("Each entry in the dataset must be a dictionary.")

        # Validate parameters, if given
        if parameters:
            for param in parameters:
                if not isinstance(param, dict):
                    raise ValueError("Each parameter must be a dictionary.")

    def _encode_image_to_bytes(self, pillow_image: Image.Image) -> bytes:
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

    def _run_gemini(
        self,
        pillow_images: List[dict],
        generation_params: List[dict],
        num_images: int = 1,
    ) -> Image.Image:
        """
        Generates images using the Imagen API and checks the status until the image is ready.

        :param pillow_images: A list of dictionaries containing pillow images images.
          Example::

          [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}]
        :type pillow_images: List[dict]
        :param generation_params: A list of dictionaries containing generation params.
        :type generation_params: list[dict]
        :return: The generated image.
        :rtype: PIL.Image.Image
        """
        genai_client = Client(
            vertexai=True, project=self.gcp_project_id, location=self.gcp_location
        )
        # if model is not given in generation_params, set to default
        model_name = next(
            (
                param["value"]
                for param in generation_params
                if param["node_name"] == "model_name"
            ),
            self.model_name,
        )
        vertexai.init(project=self.gcp_project_id, location=self.gcp_location)

        # gets the first prompt from the generation_params
        prompt = next(
            (
                param["value"]
                for param in generation_params
                if param["node_name"] == "prompt"
            ),
            None,
        )
        if prompt is None:
            raise ValueError("No generation parameter with node_name 'prompt' found.")

        # gets the first image from the pillow_images with node_name 'Load Input Image'
        input_pillow_image = next(
            (
                image["pillow_image"]
                for image in pillow_images
                if image["node_name"] == "Load Input Image"
            ),
            None,
        )
        if input_pillow_image is None:
            raise ValueError("No image with 'node_name' == 'Load Input Image' found.")

        # turn prompt and image into vertex readable content
        input_image = types.Part.from_bytes(
            data=self._encode_image_to_bytes(input_pillow_image),
            mime_type="image/jpeg",
        )
        msg1_text1 = types.Part.from_text(text=prompt)
        contents = [
            types.Content(role="user", parts=[input_image, msg1_text1]),
        ]

        for i in range(num_images):
            time.sleep(5)
            if not self.verbose:
                print("\n--- Wait 5 seconds to avoid 429 error ---")
                print(f"\n--- Generating image {i + 1}/{num_images} ---")
                print(f"Sending request to model '{model_name}'...")
            candidate_image: Optional[VertexImage] = None
            candidate_text: Optional[str] = None
            error_text: Optional[str] = None

            generated_outputs: List[Optional[VertexImage]] = []

            try:
                # Generate content - expecting one result per call
                response = genai_client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["Text", "Image"]
                    ),
                )
                # verbose extracting of image and error handling
                if response and response.candidates:
                    # Expecting only one candidate since number_of_results is not used
                    if len(response.candidates) > 1 and self.verbose:
                        print(
                            f"  Warning: Received {len(response.candidates)} candidates, expected 1. Processing the first."
                        )

                    candidate = response.candidates[0]
                    if self.verbose:
                        print(
                            f"Processing Candidate 1 (Finish Reason: {candidate.finish_reason})"
                        )

                    if candidate.finish_reason != "STOP":
                        if self.verbose:
                            print(
                                f"  Warning: Candidate finished with reason: {candidate.finish_reason}. Content might be missing or incomplete."
                            )
                        error_text = f"Generation failed: Model finished with reason '{candidate.finish_reason}'."

                    if candidate.content and candidate.content.parts:
                        if self.verbose:
                            print(
                                f"  Candidate has {len(candidate.content.parts)} parts."
                            )
                        image_data = candidate.content.parts[0].inline_data.data
                        candidate_image = VertexImage.from_bytes(image_data)
                        candidate_image = Image.open(BytesIO(candidate_image.data))
                    else:
                        print(
                            f"  Warning: No content or parts found for candidate (Finish Reason: {candidate.finish_reason})."
                        )
                        if (
                            not error_text
                        ):  # Only set error if not already set by finish_reason
                            error_text = (
                                "Generation failed: No content or parts in response."
                            )

                else:
                    print(
                        "  Warning: No candidates found in the response for this call."
                    )
                    error_text = "Generation failed: No candidates in response."
                    # Log the full response if possible for debugging
                    try:
                        print(f"  Full response: {response}")
                    except Exception:
                        pass

                generated_outputs.append(
                    (candidate_image, error_text if error_text else candidate_text)
                )
                if candidate_image:
                    print(f"  -> Extracted Image for call {i + 1}.")
                if (
                    candidate_text and not error_text
                ):  # Log text only if no error occurred
                    print(f"  -> Extracted Text for call {i + 1}.")
                if error_text:
                    print(f"  -> Recorded Error for call {i + 1}: {error_text}")
                if not candidate_image and not candidate_text and not error_text:
                    print(
                        f"  -> Failed to extract Image or Text for call {i + 1} (No specific error text)."
                    )

                print(
                    f"\n--- Background Image Generation Loop Complete ({len(generated_outputs)} outputs processed) ---"
                )
                return generated_outputs

            except Exception as e:
                print(f"An unexpected error occurred outside the generation loop: {e}")
                traceback.print_exc()
                # Return list of Nones matching num_images on error
                return [(None, f"Error: {e}")] * num_images

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.

        :param args: A dictionary containing the following keys:
        * pillow_images (list[dict]): A list of dictionaries containing pillow images images.
        * generation_params (list[dict]): A list of dictionaries containing generation params.
        :type args: dict[str, any]

        :return: A tuple containing:
        * image (Image.Image): The generated image.
        * image_name (str): The name of the generated image.
        :rtype: tuple[Image.Image, str]
        """
        pillow_images = args.get("pillow_images", [])
        generation_params = args.get("generation_params", [])

        image = self._run_gemini(pillow_images, generation_params, num_images=1)
        image = image[0][0]
        # Since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        return image, image_name
