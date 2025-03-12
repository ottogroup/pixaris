## Pixaris: An Evaluation Framework for Image Generation

Welcome to Pixaris, the experiment tracking solution for data scientists, AI engineers, and creatives working on image generation. Pixaris empowers you to efficiently track, compare, and evaluate your image generation experiments with precision and ease.

**Why Pixaris?**

Keeping track of experiments and optimizing complex workflows for image generation can be challenging. Pixaris integrates seamlessly with tools like ComfyUI and Flux, providing advanced orchestration capabilities and comprehensive metrics. Pixaris is specifically tailored for the unique demands of image generation.

Inspired by the MLOps mindset, we aim to cultivate an ImageOps approach. With Pixaris, you can track, compare, and evaluate your experiments with advanced orchestration capabilities and comprehensive metrics.

![Tensorboard](test/assets/tensorboard-example.png)

**Key Features**

- **Advanced Orchestration**: Connect effortlessly with ComfyUI and other tools, streamlining complex workflows and enabling efficient experimentation.
- **Comprehensive Metrics**: Implement custom metrics, including multimodal LLM evaluations, to gain deeper insights into the quality of your generated images.
- **Scalable Experiment Tracking**: Designed for image generation at scale, Pixaris allows you to manage and visualize large sets of experiments with ease, leveraging the power of TensorBoard and Google Cloud Platform (GCP).
- **Flexible Hyperparameter Search**: Explore a limitless range of parameters, such as prompt, model, cfg, noise, seed, ... to discover the optimal settings for your image generation tasks.
- **Local and Remote Workflow Execution**: Trigger ComfyUI workflows locally or remotely, with options to store results locally if you are not using TensorBoard.

**Target Audience**

Pixaris is tailored for data scientists, AI engineers and all other enthusiasts who are focused on image generation, requiring sophisticated testing and evaluation mechanisms.

## Installation
To install Pixaris, follow these steps:

0. Make sure to have Python 3.12 and Poetry 2.0.1 or higher installed.
1. Clone the repository:
    ```sh
    git clone https://github.com/OG-DW/tiga_pixaris
    ```
2. Navigate to the project directory:
    ```sh
    cd pixaris
    ```
3. Install the required dependencies:
    ```sh
    poetry install
    ```
4. Optional: If you prefer working with Notebooks, install [jupytext](https://github.com/mwouts/jupytext) and you can convert our py files to ipynb.
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

## Getting Started

Follow these steps to set up and run your experiment:

1. **[Load Your Data Set](#loading-your-data-set)**:
   Begin by defining your `DatasetLoader`. This component contains all the images required for your ComfyUI workflow, including masks, Canny images, and inspirational images.

2. **[Set Up Image Generation](#setting-up-how-you-are-generating-images)**:
   Next, define the functionality for generating images using the `Generator`. For example, the `ComfyGenerator` allows you to trigger ComfyUI workflows via API.

3. **[Set Up Experiment Tracking](#setting-up-your-experiment-tracking)**:
   Use the `DataWriter` to specify where your experiment data will be saved.

4. **[OPTIONAL: Set Up Evaluation Metrics](#optional-setup-evaluation-metrics)**:
   If desired, you can add metrics to your experiment run, such as `llm_metric`, which allows an LLM to evaluate your images.

5. **[Define Arguments for Your Experiment Run](#define-args-for-your-experiment-run)**:
   Here, you will define `args` for your experiment run, such as the path to your comfyui-workflow.json and the `run_name`.

6. **[Orchestrate Your Experiment Run](#orchestrate-your-experiment-run)**:
   Finally, orchestrate your experiment run using one of the generate functions, e.g., `generate_images_based_on_eval_set`.

### Summary

To utilize Pixaris for evaluating your experiments, you will always need a `DatasetLoader`, `ImageGenerator`, `DataWriter`, and `args`. Once all components are defined, they will be passed to an orchestration function like `generate_images_based_on_eval_set`. This function is responsible for loading the data, executing the experiment, and saving the results.

For each component, we offer several options to choose from. For example, the `DatasetLoader` includes the `GCPDatasetLoader` for accessing data in Google Cloud Storage and a separate `LocalDatasetLoader` for accessing local evaluation data. Additionally, you have the flexibility to implement your own component tailored to your specific needs. Attached is an overview of the various components and their implementations.

![Overview of Classes](test/assets/overview.png)

For example usages, check the [examples](examples). Please note, to set up the GCP components, such as `GCPDatasetLoader`, we use a config. Here is an [example_config.yaml](examples/example_config.yaml), please adjust and save a local version in the `pixaris` folder.

### Loading your data set
First step: load your dataset using a `DatasetLoader`. If you have your data in a Google Cloud bucket, you can use the `GCPDatasetLoader`.

```
from pixaris.data_loaders.gcp import GCPDatasetLoader
loader = GCPDatasetLoader(
    gcp_project_id=<your gcp_project_id here>,
    gcp_bucket_name=<your gcp_bucket_name here>,
    eval_set=<your eval_dir here>,
    eval_dir_local="eval_data", # this is the local path where all your eval_sets are stored
)
```
Alternatively, you can  use the `LocalDatasetLoader` if you have your `eval_set` saved locally, or implement your own `DatasetLoader` with whatever requirements and tools you have. A `DatasetLoader` should return a dataset that can be parsed by an `ImageGenerator`.

Information on how what an `eval_set` consists of and how you can create one can be found here TODO.

### Setting up how you are generating images
We implemented a neat `ImageGenerator` that uses ComfyUI.
```
from pixaris.generation.comfyui import ComfyGenerator
comfy_generator = ComfyGenerator(workflow_apiformat_path=<WORKFLOW_PATH>)
```
The workflow_apiformat_path should lead to a JSON file exported from ComfyUI. You can export your workflow in apiformat as shown [here][test/assets/export_apiformat.png].

You can implement your own `ImageGenerator` for image generation with different tools, an API, or whatever you like. Your class needs to inherit from `ImageGenerator` and should call any image generation pipeline. A generator should parse a dataset into usable arguments for your generation. Override the function `generate_single_image` to call your generation.

### Setting up your experiment tracking
To save the generated images and possibly metrics, we define a `DataWriter`. In our case, we want to have a nice visualization of all input and output images and metrics, so we choose the `GCPTensorboardWriter` using the Google-managed version. This decision was made because a lot of functionality is already implemented, e.g. we like that you can zoom in and out of images.
```
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter
writer = GCPTensorboardWriter(
    project_id=<your gcp_project_id here>,
    location=<your gcp_location here>,
    bucket_name=<your gcp_bucket_name here>,
)
```
Alternatively, you can choose to save your results locally using the `LocalDataWriter` or implement your own class that inherits from the `DataWriter`. Usually, it would save images and possibly metrics from your experiment. If you use the `LocalDataWriter`, you store your results locally and continue working with the JSON outputs. However, you can only look at the generated images one by one and miss out on one of our favorite features of Pixaris: That you can directly compare images from different experiment runs.

### Optional: Setup evaluation metrics
Maybe we want to generate some metrics to evaluate our results, e.g., for mask generation, calculate the IoU with the correct masks.
```
from pixaris.metrics.iou import IoUMetric
correct_masks_path = <path to your correct masks>
correct_masks = [Image.open(correct_masks_path + name) for name in os.listdir(correct_masks_path)]
iou_metric = IoUMetric(true_masks)
```

As always, it is intended for you to implement your own metrics by inheriting from the `BaseMetric` class.

### Define args for your experiment run
Depending on the specific components we defined and what they provide, we need to give some more arguments.
`args` can include whatever data is needed by any of the components and is not given explicitly through parameters of a component. The content of `args` is highly dependent on the components you use.

For example, additional parameters you want to set in the workflow for the `ComfyGenerator` can be specified by `generation_params`.
In `args` you can set a seed, an inspiration image for the workflow, or which workflow image should be uploaded for documentation. In contrast to the inputs in the `eval_set`, these will be the same for each execution over the workflow within your experiment.

```
args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "generation_params": [
        {
            "node_name": "KSampler (Efficient)",
            "input": "seed",
            "value": 42,
        }
    ],
    "image_paths": [
        {
            "node_name": "Load Inspo Image",
            "image_path": "test/assets/test_inspo_image.jpg",
        }
    ],
    "run_name": "example_run",
}
```

### Orchestrate your experiment run
After defining all aforementioned components, we simply pass them to the orchestration
```
from pixaris.orchestration.base import generate_images_based_on_eval_set
out = generate_images_based_on_eval_set(
    data_loader=loader,
    image_generator=comfy_generator,
    data_writer=writer,
    metrics=[iou_metric],
    args=args,
)
```
Internally, it will load data, generate images, calculate metrics, and save data using the previously defined objects. In a nutshell: do all the magic :)

## Naming Conventions
For clarity, we would like to state what terminology we use in Pixaris:
- **Workflow Execution**: Running a workflow for a single input, e.g., object image + mask image.
- **Eval Set**: Set of evaluation inputs, e.g., 10 * (object image + mask image).
- **Experiment Run**: One eval set gets run with 1 workflow and 1 set of generation_params.
- **Hyperparameter Search**: One workflow, one eval set, multiple sets of generation_params, which results in multiple experiment runs.
- **Generation Params**: Set of parameters to execute a single run.
- **Hyperparameters**: Multiple sets of different Generation Params, used in hyperparameter search.
- **args**: Includes inputs, e.g., can include workflow apiformat, input images, generation params, save directory, etc.

## License Information
TODO....Pixaris is open-source software licensed

## Contribute
We published this project to inspire everyone to contribute their own ideas to this project. Feel free to fork and add new data loaders, generators, writers, or metrics to Pixaris! Learn here how: https://opensource.guide/how-to-contribute/
