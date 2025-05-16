<p align="center">
  <a href="https://github.com/ottogroup/pixaris">
    <img src="https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/pixaris_logo.png" alt="Pixaris Logo" width="160">
  </a>
</p>

# [Pixaris](https://github.com/ottogroup/pixaris): An Evaluation Framework for Image Generation

[![PyPI Version](https://img.shields.io/pypi/v/pixaris)](https://pypi.org/project/pixaris/)
[![License](https://img.shields.io/github/license/ottogroup/pixaris)](https://github.com/ottogroup/pixaris/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/pixaris)](https://pypi.org/project/pixaris/)
[![GitHub Issues](https://img.shields.io/github/issues/ottogroup/pixaris)](https://github.com/ottogroup/pixaris/issues)


[Pixaris](https://github.com/ottogroup/pixaris) is an open-source Python framework designed to streamline the evaluation and experimentation of image generation workflows. Whether you're a data scientist, AI engineer, or creative professional, Pixaris provides the tools you need to efficiently track, compare, and optimize your image generation projects, with built-in support for tools like ComfyUI and Flux. By tracking metrics, orchestrating experiments, and providing a user-friendly interface for feedback, Pixaris helps you achieve the highest quality results in your image generation endeavors.

**Table of Contents**

- [Pixaris: An Evaluation Framework for Image Generation](#pixaris-an-evaluation-framework-for-image-generation)
  - [Key Features](#key-features)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
    - [Summary](#summary)
      - [Load the examples as a notebook](#load-the-examples-as-a-notebook)
    - [Loading your data set](#loading-your-data-set)
    - [Setting up how you are generating images](#setting-up-how-you-are-generating-images)
    - [Setting up your experiment tracking](#setting-up-your-experiment-tracking)
    - [Optional: Setup evaluation metrics](#optional-setup-evaluation-metrics)
    - [Define args for your experiment run](#define-args-for-your-experiment-run)
    - [Orchestrate your experiment run](#orchestrate-your-experiment-run)
  - [Orchestration: Generating Images at Scale](#orchestration-generating-images-at-scale)
    - [Parallelised Calls to Generator](#parallelised-calls-to-generator)
    - [Run Generation on kubernetes Cluster](#run-generation-on-kubernetes-cluster)
  - [Pixaris UI: Viewing Results and Giving Feedback](#pixaris-ui-viewing-results-and-giving-feedback)
    - [Viewing the Experiment Results](#viewing-the-experiment-results)
    - [Giving Feedback on Generated Images](#giving-feedback-on-generated-images)
  - [Naming Conventions](#naming-conventions)
  - [Contribute](#contribute)
  - [License](#license)

## Key Features

- **Advanced Orchestration:** Seamlessly integrates with ComfyUI, Flux, and other tools, simplifying complex image generation workflows.
- **Comprehensive Metrics:** Allows the implementation of custom metrics, including multimodal LLM evaluations, for in-depth analysis of image quality.
- **Scalable Experiment Tracking:** Designed for managing and visualizing large-scale image generation experiments, with a Gradio UI and optional Google Cloud Platform (GCP) integration.
- **Flexible Hyperparameter Search:** Facilitates exploration of a wide range of parameters (e.g., prompt, model, CFG, noise, seed) to optimize image generation tasks.
- **Local and Remote Workflow Execution:** Supports triggering ComfyUI workflows locally, remotely via IAP tunnel, or deploying them onto a Kubernetes cluster.
- **Integrated Feedback Mechanism:** Enables collecting feedback on generated images directly within the Pixaris UI, fostering collaboration and iterative improvement.

## Installation

You can install the latest stable version of Pixaris from PyPI using pip:

```sh
pip install pixaris
```

Online documentation is available [here](https://ottogroup.github.io/pixaris/modules.html).
The open source repository is found [here](https://github.com/ottogroup/pixaris).
## Getting Started

The following steps will guide you through setting up and running your first image generation experiment with Pixaris.

1.  **Load Your Data Set:** Define a `DatasetLoader` to manage your input images, masks, and other data required by your image generation workflow.

2.  **Set Up Image Generation:** Configure an `Generator` to handle the actual image generation process. Pixaris provides pre-built generators, e.g. for ComfyUI (`ComfyGenerator`) and Flux (`FluxFillGenerator`).

3.  **Set Up Experiment Tracking:** Utilize an `ExperimentHandler` to specify where your experiment data (generated images and metrics) will be stored.

4.  **Optional: Set Up Evaluation Metrics:** Implement custom metrics (e.g., using LLMs) to automatically evaluate the quality of the generated images.

5.  **Define Arguments for Your Experiment Run:** Create an `args` dictionary to hold any additional parameters required by your components, such as the path to your ComfyUI workflow or the experiment run name.

6.  **Orchestrate Your Experiment Run:** Use one of the `generate_images_*` functions to execute the experiment, passing in your configured components and arguments.

7.  **View Your Results:** Launch the Pixaris UI to visualize the generated images, metrics, and collected feedback.

### Summary

At a high level, using Pixaris involves defining a `DatasetLoader`, `ImageGenerator`, `ExperimentHandler`, and any necessary arguments. These components are then passed to an orchestration function like `generate_images_based_on_dataset`, which handles loading the data, executing the experiment, and saving the results.

Pixaris provides several pre-built components to choose from, such as the `GCPDatasetLoader` for accessing data in Google Cloud Storage and the `LocalDatasetLoader` for accessing local evaluation data. You can also implement your own custom components to tailor Pixaris to your specific needs.

![Overview of Classes for Orchestration](https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/overview.png)

For example usages, check the [examples](https://github.com/ottogroup/pixaris/tree/main/examples) directory. To set up GCP components, such as `GCPDatasetLoader`, we use a configuration file. An [example_config.yaml](https://github.com/ottogroup/pixaris/tree/main/examples/example_config.yaml) is provided; just adjust it and save a local version.

#### Load the examples as a notebook
If you prefer working with Notebooks, install [jupytext](https://github.com/mwouts/jupytext) and you can convert our py files to ipynb.
```sh
pip install jupytext
```

Most common jupytext CLI commands:
```sh
# convert notebook.ipynb to a .py file
jupytext --to py notebook.ipynb

# convert notebook.py to an .ipynb file with no outputs
jupytext --to notebook notebook.py
```

### Loading your data set
First step: load your dataset using a `DatasetLoader`. If you have your data in a Google Cloud bucket, you can use the `GCPDatasetLoader`.

```python
from pixaris.data_loaders.gcp import GCPDatasetLoader
loader = GCPDatasetLoader(
    gcp_project_id=<your gcp_project_id here>,
    gcp_pixaris_bucket_name=<your gcp_pixaris_bucket_name here>,
    project=<your project_name here>
    dataset=<your eval_dir here>,
    eval_dir_local="local_experiment_inputs", # this is the local path where all your datasets are stored
)
```
Alternatively, you can  use the `LocalDatasetLoader` if you have your `dataset` saved locally, or implement your own `DatasetLoader` with whatever requirements and tools you have. A `DatasetLoader` should return a dataset that can be parsed by an `ImageGenerator`.

Information on how what an `dataset` consists of and how you can create one can be found [here](https://github.com/ottogroup/pixaris/tree/main/examples/helpful_scripts/setup_local_experiment_inputs_dummy.py).

### Setting up how you are generating images
We implemented a neat `ImageGenerator` that uses ComfyUI.
```python
from pixaris.generation.comfyui import ComfyGenerator
comfy_generator = ComfyGenerator(workflow_apiformat_json=<WORKFLOW_APIFORMAT_JSON>)
```
The workflow_apiformat_json should lead to a JSON file exported from ComfyUI. You can export your workflow in apiformat as shown [here][https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/export_apiformat.png].

Pixaris also includes an implementation of `FluxFillGenerator`, that calls a Flux API for generation. You can implement your own `ImageGenerator` for image generation with different tools, an API, or whatever you like. Your class needs to inherit from `ImageGenerator` and should call any image generation pipeline. A generator parses a dataset into usable arguments for your generation. Override the function `generate_single_image` to call your generation.

### Setting up your experiment tracking
To save the generated images and possibly metrics, we define an `ExperimentHandler`. In our case, we want to have the results saved locally, so we choose the `LocalExperimentHandler`.
```python
from pixaris.experiment_handlers.local import LocalExperimentHandler
handler = LocalExperimentHandler()
```
Alternatively, you can choose to save your results remotely in GCP using the `GCPExperimentHandler` or implement your own class that inherits from the `ExperimentHandler`. Usually, it would save images and possibly metrics from your experiment.

### Optional: Setup evaluation metrics
Maybe we want to generate some metrics to evaluate our results, e.g., for mask generation, calculate the IoU with the correct masks.
```python
from pixaris.metrics.llm import LLMMetric
object_images = [<PIL images with the objects>]
style_images = [<PIL images with style references>]
llm_metric = LLMMetric(object_images, style_images)
```

As always, it is intended for you to implement your own metrics by inheriting from the `BaseMetric` class.

### Define args for your experiment run
Depending on the specific components we defined and what they provide, we need to give some more arguments.
`args` can include whatever data is needed by any of the components and is not given explicitly through parameters of a component. The content of `args` is highly dependent on the components you use.

For example, additional parameters you want to set in the workflow for the `ComfyGenerator` can be specified by `generation_params`.
In `args` you can set a seed, an inspiration image for the workflow, or which workflow image should be uploaded for documentation. In contrast to the inputs in the `dataset`, these will be the same for each execution over the workflow within your experiment.

Experiment handling follows the logic, that there is a `project`, which serves as an organising level, e.g. you might want to experiment with beach backdrops. And then in one `project`, there can be multiple `dataset`s to work with, e.g. generation of backgrounds for square and landscape format images, beach_square and beach_landscape.

```python
from PIL.Image import Image
PROJECT = "beach"
DATASET = "beach_square"
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "generation_params": [
        {
            "node_name": "KSampler (Efficient)",
            "input": "seed",
            "value": 42,
        }
    ]
    "pillow_images": [
        {
            "node_name": "Load Inspo Image",
            "pillow_image": Image.open("test/assets/test_inspo_image.jpg"),
        }
    ],
    "experiment_run_name": "example_run",
}
```

### Orchestrate your experiment run
After defining all aforementioned components, we simply pass them to the orchestration
```python
from pixaris.orchestration.base import generate_images_based_on_dataset
out = generate_images_based_on_dataset(
    data_loader=loader,
    image_generator=comfy_generator,
    experiment_handler=handler,
    metrics=[iou_metric],
    args=args,
)
```
Internally, it will load data, generate images, calculate metrics, and save data using the previously defined objects. In a nutshell: do all the magic :)

## Orchestration: Generating Images at Scale

Are you planning to run a huge hyperparameter search to finally figure out which parameter combination is the sweet spot and don't want to wait forever until it has finished? We implemented two neat solutions to orchestrate image generation at scale.

### Parallelised Calls to Generator
By handing over the `max_parallel_jobs` in `args` to the orchestration, you can parallelise the calls to any generator. E.g. see [here](https://github.com/ottogroup/pixaris/tree/main/examples/ParallelisedOrchestration_LocalDatasetLoader_FluxGenerator_LocalExperimentHandler.py) how to parallelise calls to the flux api.

### Run Generation on kubernetes Cluster

We implemented an orchestration that is based on ComfyUI and Google Kubernetes Engine (GKE). This uploads the inputs to the cluster and then triggers generation within the cluster. See [here](https://github.com/ottogroup/pixaris/tree/main/examples/GCPDatasetLoader_ComfyClusterGenerator_GCPExperimentHandler.py) for example usage.

If you want to use Pixaris without setting it up manually, you can pull the prebuilt Pixaris Docker image from this repository:
```sh
docker pull ghcr.io/ottogroup/pixaris:latest
```

## Pixaris UI: Viewing Results and Giving Feedback
You can directly use the GUI to inspect your experiment results and provide feedback on them. For this, you need to define an `ExperimentHandler` and `FeedbackHandler` to call `launch_ui`. They will handle loading experiments and managing feedback. Both experiment handling and feedback handling have an organising level `project` at the top. This allows you to sort your experiments and feedbacks per use case, topic, time, or whatever you like.

<img src="https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/UI_overview.png" alt="Overview of Classes for UI" width="400">

Using local components:
```python
from pixaris.feedback_handlers.local import LocalFeedbackHandler
feedback_handler = LocalFeedbackHandler()
experiment_handler = LocalExperimentHandler()

launch_ui(feedback_handler, experiment_handler)
```
The UI is then available at `http://localhost:8080`.

Find code to setup dummy data and deploy the frontend in [this folder](https://github.com/ottogroup/pixaris/tree/main/examples/frontend/).
### Viewing the Experiment Results
In the Experiment Tab, you can see the generated images as well as the results of metrics in tabular form.
![ExperimentTrackingView](https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/pixaris_experiment_screenshot_explanations.png)

### Giving Feedback on Generated Images
When reviewing your generated images, Pixaris UI lets you rate which images are good and which aren't. To do this either alone or with your team, you can use Feedback tab in the UI. `feedback_iteration`s are independent from experiment datasets. You could e.g. have a feedback_iteration that consists of your favorite experiment runs, or you could freely generate a bunch of images and form them into a `feedback_iteration`. It is completely up to you. Here you can see some cute chinchillas and how the author would rate the images.

![FeedbackTrackingView](https://raw.githubusercontent.com/ottogroup/pixaris/refs/heads/main/assets/pixaris_feedback_screenshot_explanations.png)


## Naming Conventions
For clarity, we would like to state what terminology we use in Pixaris:
- **Workflow Execution**: Running a workflow for a single input, e.g., object image + mask image.
- **Dataset**: Set of evaluation inputs, e.g., 10 * (object image + mask image).
- **Experiment Run**: One eval set gets run with 1 workflow and 1 set of generation_params.
- **Hyperparameter Search**: One workflow, one eval set, multiple sets of generation_params, which results in multiple experiment runs.
- **Generation Params**: Set of parameters to execute a single run.
- **Hyperparameters**: Multiple sets of different Generation Params, used in hyperparameter search.
- **args**: Includes inputs, e.g., can include workflow apiformat, input images, generation params, save directory, etc.

## Contribute

We encourage contributions to Pixaris!  If you'd like to contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Submit a pull request with a clear description of your changes.

For more detailed guidelines, see our [Contributing Guide](https://opensource.guide/how-to-contribute/).


## Release
1. Update the version in `pyproject.toml`.
2. Create a new release. Follow [GitHub Release Docu](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
3. Validate that the github action `release_new_version.yaml` was successful. 

## License

Pixaris is released under the GPL-3.0 license License. See the [LICENSE](https://github.com/ottogroup/pixaris/tree/main/LICENSE) file for details.
