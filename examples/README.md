# Pixaris Examples

This directory contains various examples demonstrating how to use the Pixaris framework for image generation, experimentation, and UI deployment. These examples showcase different combinations of data loaders, generators, and experiment handlers to help you get started with Pixaris.

## Directory Structure

The examples are organized into three main categories:

```
examples/
├── dummy_data_creation/        # Scripts to create test data for development and testing
├── experimentation/            # Examples of different experimentation configurations
├── frontend_deployment/        # Scripts to deploy and interact with the Pixaris UI
└── example_config.yaml         # Template configuration file
```

## Configuration for GCP or Flux usage

Before running any examples, you should customize the `example_config.yaml` file with your own settings, particularly if you're using Google Cloud Platform (GCP) resources. This file contains configuration parameters for:

- GCP project ID, location, and bucket names
- BigQuery tables for experiment and feedback tracking
- App Engine deployment settings
- API keys for various services

## Getting Started for the frontend

1. Run `examples/dummy_data_creation/create_dummy_data_for_frontend_locally.py`
2. Run `examples/frontend_deployment/initialise_feedback_iteration_locally.py`
3. Run `examples/frontend_deployment/deploy_frontend_locally_with_local_handling.py`


## Example Categories

### 1. Dummy Data Creation

Located in the `dummy_data_creation/` directory, these scripts help create synthetic data for development and testing:

- `create_dummy_data_for_frontend_locally.py` - Creates dummy data for local frontend development
- `create_dummy_data_for_frontend_in_GCP.py` - Creates dummy data in GCP for cloud-based frontend testing
- `create_dummy_eval_data_for_Generator_locally.py` - Creates evaluation data (mask and input image) for testing generator components

### 2. Experimentation

Located in the `experimentation/` directory, these scripts provide examples of different combinations of data loaders, generators, and experiment handlers:

#### Local Configurations
- `LocalDatasetLoader_ComfyGenerator_LocalExperimentHandler_WithMetrics.py` - Run experiments locally using ComfyUI with metrics
- `LocalDatasetLoader_Imagen2Generator_LocalExperimentHandler.py` - Run experiments locally using Imagen2
- `ParallelisedOrchestration_LocalDatasetLoader_FluxGenerator_LocalExperimentHandler.py` - Run parallelized experiments locally

#### Cloud Configurations
- `GCPDatasetLoader_ComfyGenerator_GCPExperimentHandler.py` - Run experiments using GCP data and storing results in GCP
- `GCPDatasetLoader_GeminiGenerator_LocalExperimentHandler.py` - Load data from GCP, use Gemini for generation, store locally

#### Advanced Configurations
- `HyperparameterSearch_GCPDatasetLoader_ComfyGenerator_GCPExperimentHandler.py` - Run hyperparameter search with ComfyUI
- `HyperparameterSearch_GCPDatasetLoader_FluxGenerator_GCPExperimentHandler.py` - Run hyperparameter search with 


#### Run on Kubernetes
- `GCPDatasetLoader_ComfyClusterGenerator_GCPExperimentHandler.py` - Run experiments with clustered ComfyUI generators

### 3. Frontend Deployment

Located in the `frontend_deployment/` directory, these scripts help you deploy and interact with the Pixaris UI:

- `deploy_frontend_locally_with_local_handling.py` - Deploy the UI locally with local data storage
- `deploy_frontend_locally_with_GCP_handling.py` - Deploy the UI locally but connect to GCP for data storage
- `initialise_feedback_iteration_locally.py` - Set up a feedback iteration loop with local storage
- `initialise_feedback_iteration_in_GCP.py` - Set up a feedback iteration loop with GCP storage

## Naming Convention

The example scripts follow a naming convention that indicates the components used:
- `[DataLoader]_[Generator]_[ExperimentHandler]_[AdditionalFeatures].py`

This helps you quickly identify which components are being used in each example.

## Getting Started

1. Install the Pixaris package and its dependencies
2. Optional: Configure your `example_config.yaml` file with appropriate settings
3. Select an example that matches your use case
4. Run the example script, either in a notebook environment or directly from Python

For most examples, you can execute them directly as Python scripts or in a notebook environment. Most examples include markdown cells with explanations and are structured to be run in a Jupyter notebook.