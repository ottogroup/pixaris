from google.cloud import storage


def upload_workflow_file_to_bucket(
    gcp_project_id: str,
    bucket_name: str,
    dataset: str,
    experiment_run_name: str,
    local_file_path: str,
) -> str:
    """
    Upload a file to a Google Cloud Storage bucket.

    Args:
        gcp_project_id (str): The Google Cloud project ID.
        bucket_name (str): The name of the bucket.
        dataset (str): The name of the evaluation set.
        experiment_run_name (str): The name of the experiment.
        local_file_path (str): The path to the file to upload.
    Returns:
        str: The path to the uploaded file in the bucket.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    file_name = f"{experiment_run_name}_{local_file_path.split('/')[-1]}"
    destination_path = f"workflows/{dataset}/{file_name}"
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(local_file_path)

    clickable_link = f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/workflows/{dataset}/{file_name}?project={gcp_project_id}"
    return clickable_link
