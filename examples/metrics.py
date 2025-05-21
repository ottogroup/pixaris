from pixaris.metrics.llm import BaseLLMMetric, StyleLLMMetric
from PIL import Image
import os

PROJECT = "test_project"
DATASET = "mock"

# define the paths to the images
object_dir = f"test/{PROJECT}/{DATASET}/input/"
object_images = [Image.open(object_dir + image) for image in os.listdir(object_dir)]

generated_dir = "/home/fidelius/pixaris/local_results/test_project/mock/20250516-155435_example-run/generated_images"
generated_images = [Image.open(os.path.join(generated_dir, image)) for image in os.listdir(generated_dir)]

style_dir = "/home/fidelius/pixaris/local_results/test_project/mock/20250509-163642_example-run/generated_images"
style_images = [Image.open(os.path.join(style_dir, image)) for image in os.listdir(style_dir)]

# define the metrics we want to use
same_content_prompt =""" You will be provided with two images. Your task is to analyze them and determine if their *core visual content* is semantically identical or completely distinct.

**Definition of "Same Content" (output `1` for 'content_metric'):**
The images depict the *exact same unique subject, scene, or specific entity*.
Minor variations are acceptable and *should be ignored* when determining sameness. These include:
*   Slight changes in angle, perspective, or zoom (e.g., the same specific car from slightly different sides or zoomed in/out).
*   Minor cropping or resizing.
*   Differences in lighting conditions, color balance, brightness, contrast, or application of minor stylistic filters.
*   Addition or removal of small watermarks, logos, text overlays, or minor annotations that do not alter the primary subject.
*   Different file formats, compression artifacts, or slight changes in resolution.
*   If one image is clearly a modified version of the other (e.g., a black and white version of a color image, or an edited version of the original scene).

**Definition of "Completely Different Content" (output `0` for 'content_metric'):**
The images depict entirely distinct subjects, scenes, or entities with no semantic overlap. For example:
*   A picture of a cat and a picture of a car.
*   Two different people, even if they share some resemblance.
*   Two different landscapes, even if they are of the same *type* (e.g., two different beaches).
*   Two different objects, even if they are of the same *category* (e.g., two different chairs, two different dogs).
*   Two different events or moments in time.

**Output Format:**
Provide your answer strictly in the following JSON format. Do not include any additional text or explanation outside of this JSON.
```json
{"content_metric": 1}
```
"""
same_content_llm_metric = BaseLLMMetric(
    prompt=same_content_prompt,
    object_images=object_images,
)
style_llm_metric = StyleLLMMetric(
    style_images=generated_images,
)

# same_content_metric_result = same_content_llm_metric.calculate(generated_images)
# print("Content score: " + same_content_metric_result)

style_metric_result = style_llm_metric.calculate(generated_images)
print("Style score: " + style_metric_result)