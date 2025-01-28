from google.cloud import storage


def upload_workflow_file_to_bucket(
    project_id: str,
    bucket_name: str,
    eval_set: str,
    run_name: str,
    local_file_path: str,
) -> str:
    """
    Upload a file to a Google Cloud Storage bucket.

    Args:
        project_id (str): The Google Cloud project ID.
        bucket_name (str): The name of the bucket.
        eval_set (str): The name of the evaluation set.
        run_name (str): The name of the experiment.
        local_file_path (str): The path to the file to upload.
    Returns:
        str: The path to the uploaded file in the bucket.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    file_name = f"{run_name}_{local_file_path.split('/')[-1]}"
    destination_path = f"workflows/{eval_set}/{file_name}"
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(local_file_path)

    clickable_link = f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/workflows/{eval_set}/{file_name}?project={project_id}"
    return clickable_link
