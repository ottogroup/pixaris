from concurrent.futures import ThreadPoolExecutor
import json
import re
import io
from PIL.Image import Image
import vertexai
from vertexai.generative_models import GenerativeModel, Image as GenAIImage, Part
import yaml
from pixaris.metrics.base import BaseMetric
from pixaris.metrics.utils import dict_mean
from pixaris.utils.retry import retry

class BaseLLMMetric(BaseMetric):
    """
    BaseLLMMetric is a base class for metrics that use a Gemini large language model (LLM) to evaluate images.

    :param object_images: A list of object images to compare against.
    :type object_images: list[Image]
    :param style_images: A list of style images to compare against.
    :type style_images: list[Image]
    """

    def __init__(self, prompt: str, **reference_images: list[Image]):
        """
        Initialize the BaseLLMMetric.

        :param prompt: The prompt string.
        :type prompt: str
        :param object_images: A list of object images to compare against.
        :type object_images: list[Image]
        :param style_images: A list of style images to compare against.
        :type style_images: list[Image]
        :param extra_image_lists: Additional named lists of images as keyword arguments.
        """
        super().__init__()
        self.prompt = prompt
        self.reference_images = reference_images
    
    def _verify_input_images(self, input_images: list[Image]):
        """
        Verify that the input images are valid and that the number of input images matches the number of reference images.
        """
        if not isinstance(input_images, list):
            raise ValueError("Input images must be a list.")
        if not all(isinstance(image, Image) for image in input_images):
            raise ValueError("All input images must be PIL Image objects.")
        
        input_image_len = len(input_images)
        
        for image_list in self.reference_images.values():
            if not isinstance(image_list, list):
                raise ValueError("Reference images must be a list.")
            if not all(isinstance(image, Image) for image in image_list):
                raise ValueError("All reference images must be PIL Image objects.")
            if len(image_list) != input_image_len:
                raise ValueError(
                    f"Number of reference images ({len(image_list)}) does not match number of input images ({input_image_len})."
                )

    def _PIL_image_to_vertex_image(self, image: Image) -> GenAIImage:
        """
        Converts a PIL image to a vertex image.

        :param image: The PIL image.
        :type image: PIL.Image.Image
        :return: The vertex image.
        :rtype: vertexai.generative_models.Image
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return GenAIImage.from_bytes(img_byte_arr.getvalue())

    def _llm_prompt(
        self,
        json_prompt: str,
        images: list[Image],
    ):
        """
        Generates a prompt for the LLM using the provided JSON prompt and images.
        
        :param json_prompt: The JSON prompt string.
        :type json_prompt: str
        :param images: A list of images to include in the prompt.
        :type images: list[Image]
        :return: A list containing the JSON prompt and the images as vertexai.generative_models.Part objects.
        :rtype: list[vertexai.generative_models.Part, str]
        """
        return [
            json_prompt,
            *[Part.from_image(self._PIL_image_to_vertex_image(image)) for image in images],
        ]
        
    def _postprocess_response(self, response_text: str) -> str:
        """
        If there is some sort of JSON-like structure in the response text, extract it and return it.

        :param response_text: The response text from the model.
        :type response_text: str
        :return: The extracted JSON-like structure if found, otherwise the original response text.
        :rtype: str
        """
        pattern = r"\{.*\}"
        match = re.search(pattern, response_text)
        if match:
            extracted_string = match.group(0)
            return extracted_string
        else:
            raise ValueError("No JSON-like structure found in the llm response text.")

    def _response_to_dict(self, response_text: str) -> dict:
        """
        Converts the response text to a dictionary.

        :param response_text: The response text from the model.
        :type response_text: str
        :return: The response text as a dictionary.
        :rtype: dict
        """
        parsed_text = self._postprocess_response(response_text)
        response_dict = json.loads(parsed_text)
        response_dict = {key: float(value) for key, value in response_dict.items()}

        if not all(
            metrics in response_dict
            for metrics in ["llm_reality", "llm_similarity", "llm_errors", "llm_style"]
        ):
            raise ValueError("Response dictionary does not contain all required keys.")
        return response_dict

    def _call_gemini(self, prompt) -> str:
        """
        Sends the prompt to Google API

        :param prompt: The prompt for the LLM metrics. Generated by llm_prompt().
        :type prompt: list[vertexai.generative_models.Part, str]
        :return: The LLM response.
        :rtype: str
        """
        with open("pixaris/config.yaml", "r") as f:
            config = yaml.safe_load(f)

        vertexai.init(project=config["gcp_project_id"], location=config["gcp_location"])

        model = GenerativeModel("gemini-2.0-flash")

        responses = model.generate_content(prompt, stream=False)

        return responses.text

    def _successful_evaluation(self, prompt, max_tries: int = 3) -> dict:
        """
        Perform an evaluation by calling the `call_gemini` function with the given parameters.
        Assures that gemini returns correct json code by calling it up to max_tries times if it fails.

        :param prompt: The prompt for the LLM metrics. Generated by llm_prompt().
        :type prompt: list[vertexai.generative_models.Part, str]
        :param max_tries: The maximum number of tries to perform the LLM call. Defaults to 3.
        :type max_tries: int
        :return: The LLM response as a dictionary.
        :rtype: dict
        :raises ValueError: If the response cannot be parsed as JSON.
        """
        for i in range(max_tries):
            try:
                return self._response_to_dict(self._call_gemini(prompt))
            except ValueError:
                pass

    def _combined_score(self, response: dict) -> float:
        """
        Calculates the combined score from the response dictionary.

        :param response: The response dictionary.
        :type response: dict
        return: The combined score. Score is the unweighted mean of all the scores.
        :rtype: float
        """
        return sum(response.values()) / len(response.values())

    def _llm_scores_per_image(
        self,
        evaluation_image: Image,
        sample_size: int = 3,
    ) -> dict:
        """
        Calculates the LLM score for the generated image.

        :param evaluation_image: The generated image.
        :type evaluation_image: PIL.Image.Image
        :param object_image: The object image the evaluation image should be similar to.
        :type object_image: PIL.Image.Image
        :param style_image: The style image the evaluation image should be similar to.
        :type style_image: PIL.Image.Image
        :param sample_size: The number of times to call the LLM for the same image. Defaults to 3.
        :type sample_size: int, optional
        :return: A dictionary containing the LLM scores for the evaluation image.
        :rtype: dict
        """
        scores = [
            self._successful_evaluation(
                self._llm_prompt(evaluation_image, object_image, style_image)
            )
            for _ in range(sample_size)
        ]

        # Calculate the average score for each metric
        average_scores_per_metric = dict_mean(scores)

        # Invert the error count to get a score
        average_scores_per_metric["llm_errors"] = 1 / (
            1 + average_scores_per_metric["llm_errors"]
        )

        # Calculate the llm_average score
        average_scores_per_metric["llm_average"] = self._combined_score(
            average_scores_per_metric
        )

        return average_scores_per_metric

    def calculate(self, evaluation_images: list[Image]) -> dict:
        """
        Calculate the LLM metrics for a list of generated images.

        :param evaluation_images: A list of generated images.
        :type evaluation_images: list[Image]
        :return: A dictionary containing the LLM metrics for the generated images.
        :rtype: dict
        :raises ValueError: If the number of evaluation images does not match the number of object or style images.
        """
        self._verify_input_images(evaluation_images)

        with ThreadPoolExecutor(len(evaluation_images)) as executor:
            llm_metrics = dict_mean(
                list(
                    executor.map(
                        self._llm_scores_per_image,
                        evaluation_images,
                        *[image for image in self.reference_images.values()],
                    )
                )
            )
            return llm_metrics
