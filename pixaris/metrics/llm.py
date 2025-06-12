from concurrent.futures import ThreadPoolExecutor
import json
import re
import io
from PIL.Image import Image
import vertexai
from vertexai.generative_models import GenerativeModel, Image as GenAIImage, Part
import yaml
from pixaris.metrics.base import BaseMetric
from pixaris.metrics import prompts
from pixaris.metrics.utils import dict_mean
from pixaris.utils.retry import retry


class BaseLLMMetric(BaseMetric):
    """
    BaseLLMMetric is a base class for metrics that use a Gemini large language model (LLM) to evaluate images.

    :param prompt: The prompt string for the LLM. The prompt has to determine what should be evaluated and that
        the output is JSON formatted. '{"base_llm_metric": x}' where x is the score. Can also be multiple scores in one.
    :type prompt: str
    :param sample_size: The number of times to call the LLM for the same image. Defaults to 3.
    :type sample_size: int, optional
    :param reference_images: A dictionary of reference images.
    :type reference_images: dict[str, list[Image]]
    """

    def __init__(
        self, prompt: str, sample_size: int = 3, **reference_images: list[Image]
    ):
        """Initialise the metric with prompt, sample size and references."""
        super().__init__()
        self.prompt = prompt
        self.sample_size = sample_size
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

    @retry(exceptions=Exception, tries=3, delay=0.5, max_delay=2, backoff=2)
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
            *[
                Part.from_image(self._PIL_image_to_vertex_image(image))
                for image in images
            ],
        ]

    def _postprocess_response(self, response_text: str) -> str:
        """
        If there is some sort of JSON-like structure in the response text, extract it and return it.

        :param response_text: The response text from the model.
        :type response_text: str
        :return: The extracted JSON-like structure if found, otherwise the original response text.
        :rtype: str
        """
        pattern = r"\{.*?\}"
        match = re.search(pattern, response_text, re.DOTALL)
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
        return json.loads(parsed_text)

    def _call_gemini(self, prompt: list[vertexai.generative_models.Part, str]) -> str:
        """
        Sends the prompt to Google API

        :param prompt: The prompt for the LLM metrics. Generated by _llm_prompt().
        :type prompt: list[vertexai.generative_models.Part, str]
        :return: The LLM response.
        :rtype: str
        """
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        vertexai.init(project=config["gcp_project_id"], location=config["gcp_location"])

        model = GenerativeModel("gemini-2.0-flash")

        responses = model.generate_content(prompt, stream=False)

        return responses.text

    def _successful_evaluation(
        self, prompt: list[vertexai.generative_models.Part, str], max_tries: int = 3
    ) -> dict:
        """
        Perform an evaluation by calling the `_call_gemini` function with the given parameters.
        Assures that gemini returns correct json code by calling it up to max_tries times if it fails.

        :param prompt: The prompt for the LLM metrics. Generated by llm_prompt().
        :type prompt: list[vertexai.generative_models.Part, str]
        :param max_tries: The maximum number of tries to perform the LLM call. Defaults to 3.
        :type max_tries: int
        :return: The LLM response as a dictionary.
        :rtype: dict
        :raises ValueError: If the response cannot be parsed as JSON.
        """
        for _ in range(max_tries):
            try:
                ans = self._response_to_dict(self._call_gemini(prompt))
                return ans
            except ValueError:
                pass

    def _llm_scores_per_image(
        self,
        evaluation_image: Image,
        *reference_images: list[Image],
    ) -> dict:
        """
        Calculates the LLM score for the generated image and possibly some reference images.

        :param evaluation_image: The generated image.
        :type evaluation_image: PIL.Image.Image
        :param reference_images: A list of reference images.
        :type reference_images: list[Image]
        :return: A dictionary containing the LLM scores for the evaluation image.
        :rtype: dict
        """
        scores = [
            self._successful_evaluation(
                self._llm_prompt(self.prompt, [evaluation_image, *reference_images]),
            )
            for _ in range(self.sample_size)
        ]

        # Calculate the average score for each metric
        average_scores_per_metric = dict_mean(scores)

        return average_scores_per_metric

    def _get_mean_metric(self, responses: list[dict]) -> float:
        """
        Calculate the mean error metric from the cleaned response.

        :param responses: A list of dictionaries containing the responses from the LLM.
        :type responses: list[dict]
        :return: The mean error metric.
        :rtype: float
        """
        # Parse the response and calculate the overall mean value
        mean_value = [
            (sum(response.values()) / len(response) if responses else 1)
            for response in responses
        ]
        return sum(mean_value) / len(mean_value) if mean_value else 1

    def calculate(self, evaluation_images: list[Image]) -> dict:
        """
        Calculate the LLM metrics for a list of evaluation images.

        :param evaluation_images: A list of evaluation images.
        :type evaluation_images: list[Image]
        :return: A dictionary containing the LLM metrics for the evaluation images.
        :rtype: dict
        :raises ValueError: If the number of evaluation images does not match the number of reference images.
        """
        self._verify_input_images(evaluation_images)

        with ThreadPoolExecutor(len(evaluation_images)) as executor:
            llm_metrics = dict_mean(
                list(
                    executor.map(
                        self._llm_scores_per_image,
                        evaluation_images,
                        *self.reference_images.values(),
                    )
                )
            )
            return llm_metrics


class SimilarityLLMMetric(BaseLLMMetric):
    """
    SimilarityLLMMetric is a class inheriting from BaseLLMMetric that uses a Gemini LLM to evaluate the similarity between images.
    Compare the objects in your images against objects in a set of reference images. Calculates a rough estimate of how similar they are.
    The metric ranges from 0 (not similar) to 1 (very similar).

    :param reference_images: A list of reference images to compare against.
    :type reference_images: list[Image]
    """

    def __init__(self, reference_images: list[Image]):
        """
        Initialize the SimilarityLLMMetric.

        :param reference_images: A list of reference images to compare against.
        :type reference_images: dict[str, list[Image]]
        """
        super().__init__(
            prompt=prompts.SIMILARITY_PROMPT,
            reference_images=reference_images,
        )

    def calculate(self, evaluation_images: list[Image]) -> dict:
        """
        Calculate the LLM metrics for a list of evaluation images.

        :param evaluation_images: A list of evaluation images.
        :type evaluation_images: list[Image]
        :return: A dictionary containing the LLM metrics for the evaluation images.
        :rtype: dict
        :raises ValueError: If the number of evaluation images does not match the number of reference images.
        """
        self._verify_input_images(evaluation_images)
        vertex_prompts = [
            self._llm_prompt(self.prompt, list(images))
            for images in zip(evaluation_images, *self.reference_images.values())
        ]

        with ThreadPoolExecutor(len(evaluation_images)) as executor:
            llm_metrics = list(
                executor.map(
                    self._successful_evaluation,
                    vertex_prompts,
                )
            )

        mean_metric = self._get_mean_metric(llm_metrics)

        return {"similarity_llm_metric": mean_metric}


class StyleLLMMetric(BaseLLMMetric):
    """
    StyleLLMMetric is a class inheriting from BaseLLMMetric that uses a Gemini LLM to evaluate the style of images.
    Compares the style of the generated images against a (multiple) reference style images.
    The metric ranges from 0 (bad style match) to 1 (excellent style match).

    :param reference_images: A **kwargs dictionary of reference images. Pass lists of images that you want to compare to.
    Example::
        style_images = [image1, image2]
        object_images = [image3, image4]

        Will compare image1 and image3 to the first evaluation image and image2 and image4 to the second evaluation image.
    :type reference_images: dict[str, list[Image]]
    """

    def __init__(self, **reference_images: list[Image]):
        """
        Initialize the StyleLLMMetric.

        :param reference_images: A dictionary of reference images.
        :type reference_images: dict[str, list[Image]]
        """
        super().__init__(
            prompt=prompts.STYLE_PROMPT,
        )
        self.reference_images = reference_images

    def _describe_images(self, images: list[list[Image]]) -> list[str]:
        """
        Describe the images using the style extraction prompt.
        images is a list of lists. All the n-th images will be described together.
        Example::
            images = [[image1, image2], [image3, image4]]
            will describe image1 and image3 together and image2 and image4 together.

        :param images: A list of list images to describe.
        :type images: list[list[Image]]
        :return: A list of descriptions for the reference images.
        :rtype: list[str]
        """
        # Transpose the list of lists to group images by index
        grouped_images = list(zip(*images))
        vertex_prompts = [
            self._llm_prompt(self.prompt, list(images)) for images in grouped_images
        ]
        with ThreadPoolExecutor(len(self.reference_images)) as executor:
            descriptions = list(
                executor.map(
                    self._call_gemini,
                    vertex_prompts,
                )
            )
            return descriptions

    def _compare_images_to_descriptions(
        self,
        evaluation_images: list[Image],
        reference_image_descriptions: list[str],
    ) -> dict:
        """
        Compare the evaluation images to the reference image descriptions.

        :param evaluation_images: A list of evaluation images.
        :type evaluation_images: list[Image]
        :param reference_image_descriptions: A list of reference image descriptions.
        :type reference_image_descriptions: list[str]
        :return: A dictionary containing the LLM metrics for the evaluation images.
        :rtype: dict
        """
        image_parts = [
            Part.from_image(self._PIL_image_to_vertex_image(image))
            for image in evaluation_images
        ]
        vertex_prompts = [
            [prompts.COMPARISON_PROMPT, image_part, description]
            for image_part, description in zip(
                image_parts, reference_image_descriptions
            )
        ]

        with ThreadPoolExecutor(len(evaluation_images)) as executor:
            responses = list(
                executor.map(
                    self._successful_evaluation,
                    vertex_prompts,
                )
            )

        return responses

    def calculate(self, evaluation_images: list[Image]) -> dict:
        """
        Calculate the Style LLM metrics for a list of evaluation images.

        :param evaluation_images: A list of evaluation images.
        :type evaluation_images: list[Image]
        :return: A dictionary containing the LLM metrics for the evaluation images.
        :rtype: dict
        :raises ValueError: If the number of evaluation images does not match the number of reference images.
        """
        self._verify_input_images(evaluation_images)

        reference_image_descriptions = self._describe_images(
            self.reference_images.values()
        )
        comparison_results = self._compare_images_to_descriptions(
            evaluation_images,
            reference_image_descriptions,
        )
        return {"style_llm_metric": self._get_mean_metric(comparison_results)}


class ErrorLLMMetric(BaseLLMMetric):
    """
    ErrorLLMMetric is a class inheriting from BaseLLMMetric that uses a Gemini LLM to evaluate the error in the generated images.
    This metric is used to find errors in the generated images, such as missing objects, incorrect colors, or other visual artifacts.
    Does not require any reference images.
    The metric ranges from 0 (many errors) to 1 (no errors).
    """

    def __init__(self):
        """
        Initialize the ErrorLLMMetric.

        :param reference_images: A dictionary of reference images.
        :type reference_images: dict[str, list[Image]]
        """
        super().__init__(
            prompt=prompts.ERROR_PROMPT,
        )

    def calculate(self, evaluation_images: list[Image]) -> dict:
        """
        Calculate the Error LLM metrics for a list of evaluation images.

        :param evaluation_images: A list of evaluation images.
        :type evaluation_images: list[Image]
        :return: A dictionary containing the LLM metrics for the evaluation images.
        :rtype: dict
        :raises ValueError: If the number of evaluation images does not match the number of reference images.
        """
        self._verify_input_images(evaluation_images)
        vertex_prompts = [
            self._llm_prompt(self.prompt, [evaluation_image])
            for evaluation_image in evaluation_images
        ]

        with ThreadPoolExecutor(len(evaluation_images)) as executor:
            llm_metrics = list(
                executor.map(
                    self._successful_evaluation,
                    vertex_prompts,
                )
            )

        mean_metric = self._get_mean_metric(llm_metrics)

        return {"error_llm_metric": mean_metric}
