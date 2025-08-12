import logging
import time
import traceback
from io import BytesIO
from typing import List, Optional

from PIL import Image
from google.genai import Client, types
from vertexai.generative_models import Image as VertexImage

from pixaris.generation.base import ImageGenerator

from pixaris.generation.utils import (
    encode_image_to_bytes,
    extract_value_from_list_of_dicts,
)

logger = logging.getLogger(__name__)


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
            logger.warning(
                "Warning: Currently, gemini is only supported in 'us-central1'. Setting '%s' can result in errors.",
                gcp_location,
            )
        self.gcp_location = gcp_location
        self.model_name = model_name
        self.verbose = verbose

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        args: dict[str, any] = {},
    ):
        """
        Validates the provided dataset and parameters for image generation.

        :param dataset: A list of dicts containing image information.
        :type dataset: List[dict[str, List[dict[str, Image.Image]]]
        :param args: A dictionary containing the parameters to be used for the image generation process.
        :type args: dict[str, any]
        :raises ValueError: If the validation fails for any reason (e.g., missing fields).
        """
        parameters = args.get("generation_params", [])

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

    def _run_gemini(
        self,
        pillow_images: List[dict],
        prompt: str,
        num_images: int = 1,
    ) -> Image.Image:
        """
        Generates images using the Imagen API and checks the status until the image is ready.

        :param pillow_images: A list of dictionaries containing pillow images.
          Example::

          [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}]
        :type pillow_images: List[dict]
        :return: The generated image.
        :rtype: PIL.Image.Image
        """
        genai_client = Client(
            vertexai=True, project=self.gcp_project_id, location=self.gcp_location
        )

        # gets the first image from the pillow_images with node_name 'Load Input Image'
        input_pillow_image = extract_value_from_list_of_dicts(
            pillow_images,
            identifying_key="node_name",
            identifying_value="Load Input Image",
            return_key="pillow_image",
        )

        # turn prompt and image into vertex readable content
        input_image = types.Part.from_bytes(
            data=encode_image_to_bytes(input_pillow_image),
            mime_type="image/jpeg",
        )
        msg1_text1 = types.Part.from_text(text=prompt)
        contents = [
            types.Content(role="user", parts=[input_image, msg1_text1]),
        ]

        for i in range(num_images):
            time.sleep(5)
            if not self.verbose:
                logger.info("\n--- Wait 5 seconds to avoid 429 error ---")
                logger.info("\n--- Generating image %s/%s ---", i + 1, num_images)
                logger.info("Sending request to model '%s'...", self.model_name)
            candidate_image: Optional[VertexImage] = None
            candidate_text: Optional[str] = None
            error_text: Optional[str] = None

            generated_outputs: List[Optional[VertexImage]] = []

            try:
                # Generate content - expecting one result per call
                response = genai_client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["Text", "Image"]
                    ),
                )
                # verbose extracting of image and error handling
                if response and response.candidates:
                    # Expecting only one candidate since number_of_results is not used
                    if len(response.candidates) > 1 and self.verbose:
                        logger.warning(
                            "  Warning: Received %s candidates, expected 1. Processing the first.",
                            len(response.candidates),
                        )

                    candidate = response.candidates[0]
                    if self.verbose:
                        logger.info(
                            "Processing Candidate 1 (Finish Reason: %s)",
                            candidate.finish_reason,
                        )

                    if candidate.finish_reason != "STOP":
                        if self.verbose:
                            logger.warning(
                                "  Warning: Candidate finished with reason: %s. Content might be missing or incomplete.",
                                candidate.finish_reason,
                            )
                        error_text = f"Generation failed: Model finished with reason '{candidate.finish_reason}'."

                    if candidate.content and candidate.content.parts:
                        if self.verbose:
                            logger.info(
                                "Candidate has %s parts.",
                                len(candidate.content.parts),
                            )
                        image_data = candidate.content.parts[0].inline_data.data
                        candidate_image = VertexImage.from_bytes(image_data)
                        candidate_image = Image.open(BytesIO(candidate_image.data))
                    else:
                        logger.warning(
                            "No content or parts found for candidate (Finish Reason: %s).",
                            candidate.finish_reason,
                        )
                        if (
                            not error_text
                        ):  # Only set error if not already set by finish_reason
                            error_text = (
                                "Generation failed: No content or parts in response."
                            )

                else:
                    logger.warning(
                        "No candidates found in the response for this call."
                    )
                    error_text = "Generation failed: No candidates in response."
                    # Log the full response if possible for debugging
                    try:
                        logger.debug("  Full response: %s", response)
                    except Exception:
                        pass

                generated_outputs.append(
                    (candidate_image, error_text if error_text else candidate_text)
                )
                if candidate_image:
                    logger.info("  -> Extracted Image for call %s.", i + 1)
                if candidate_text and not error_text:
                    logger.info("  -> Extracted Text for call %s.", i + 1)
                if error_text:
                    logger.warning(
                        "  -> Recorded Error for call %s: %s", i + 1, error_text
                    )
                if not candidate_image and not candidate_text and not error_text:
                    logger.warning(
                        "  -> Failed to extract Image or Text for call %s (No specific error text).",
                        i + 1,
                    )

                logger.info(
                    "\n--- Background Image Generation Loop Complete (%s outputs processed) ---",
                    len(generated_outputs),
                )
                return generated_outputs

            except Exception as e:
                logger.error(
                    "An unexpected error occurred outside the generation loop: %s", e
                )
                traceback.print_exc()
                # Return list of Nones matching num_images on error
                return [(None, f"Error: {e}")] * num_images

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.

        :param args: A dictionary containing the following keys:
        * pillow_images (list[dict]): A list of dictionaries containing pillow images.
        * prompt (str): The prompt that should be used for the generation.
        :type args: dict[str, any]

        :return: A tuple containing:
        * image (Image.Image): The generated image.
        * image_name (str): The name of the generated image.
        :rtype: tuple[Image.Image, str]
        """
        pillow_images = args.get("pillow_images", [])
        prompt = args.get("prompt", "")

        image = self._run_gemini(pillow_images, prompt, num_images=1)
        image = image[0][0]
        # Since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        return image, image_name
