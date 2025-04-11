from pixaris.feedback_handlers.base import FeedbackHandler
from google.cloud import bigquery, storage
import gradio as gr
from datetime import datetime
import os
from PIL import Image

from pixaris.utils.bigquery import ensure_table_exists


class GCPFeedbackHandler(FeedbackHandler):
    """
    GCPFeedbackHandler is a class that handles feedback for Pixaris using Google Cloud Platform (GCP).
    Contains methods to start handle feedback iterations storing data in BigQuery and images in a GCP bucket.
    It also retrieves feedback data from the BigQuery table and downloads images from the GCP bucket to display them in the frontend.

    :param gcp_project_id: GCP project ID
    :type gcp_project_id: str
    :param gcp_bq_feedback_table: GCP BigQuery table for feedback
    :type gcp_bq_feedback_table: str
    :param gcp_pixaris_bucket_name: GCP bucket name for Pixaris
    :type gcp_pixaris_bucket_name: str
    :param local_feedback_directory: Local directory to store feedback images, default is "local_results"
    :type local_feedback_directory: str
    """

    def __init__(
        self,
        gcp_project_id: str,
        gcp_bq_feedback_table: str,
        gcp_pixaris_bucket_name: str,
        local_feedback_directory: str = "local_results",
    ):
        self.gcp_project_id = gcp_project_id
        self.gcp_bq_feedback_table = gcp_bq_feedback_table
        self.gcp_pixaris_bucket_name = gcp_pixaris_bucket_name
        os.makedirs(local_feedback_directory, exist_ok=True)
        self.local_feedback_directory = local_feedback_directory
        self.feedback_df = None
        self.feedback_iteration_choices = None
        self.projects = None

    def write_single_feedback(self, feedback: dict) -> None:
        """
        Writes feedback for one image to BigQuery table.

        :param feedback: dict with feedback information. Dict is expected to have the following keys:
        * project: name of the project
        * feedback_iteration: name of the iteration
        * dataset: name of the evaluation set (optional)
        * image_name: name of the image
        * experiment_name: name of the experiment (optional)
        * feedback_indicator: string with feedback value (either "Like", "Dislike", or "Neither")
        * comment: string with feedback comment (optional)
        :type feedback: dict
        """
        # assert non-nullable values are present
        assert all(
            key in feedback.keys()
            for key in [
                "project",
                "feedback_iteration",
                "image_name",
                "feedback_indicator",
            ]
        ), (
            "Missing required feedback keys. Must have 'project', 'feedback_iteration', 'image_name', 'feedback_indicator'"
        )

        # setup row to insert to table
        row_to_insert = {
            "project": feedback["project"],
            "feedback_iteration": feedback["feedback_iteration"],
            "dataset": feedback.get("dataset", ""),
            "image_name": feedback["image_name"],
            "experiment_name": feedback.get("experiment_name", ""),
            "date": datetime.now().isoformat(),
            "comment": feedback.get("comment", ""),
        }

        # determine what to write to feedback columns
        feedback_indicator = feedback["feedback_indicator"]

        if feedback_indicator == "Like":
            row_to_insert["likes"] = 1
            row_to_insert["dislikes"] = 0
        elif feedback_indicator == "Dislike":
            row_to_insert["likes"] = 0
            row_to_insert["dislikes"] = 1
        elif (
            feedback_indicator == "Neither"
        ):  # Is used when uploading images (no feedback given)
            row_to_insert["likes"] = 0
            row_to_insert["dislikes"] = 0
        else:
            raise ValueError(
                "Invalid feedback indicator. Must be 'Like', 'Dislike', or 'Neither'"
            )

        client = bigquery.Client(project=self.gcp_project_id)
        errors = client.insert_rows_json(self.gcp_bq_feedback_table, [row_to_insert])

        # Check for errors and display warnings to UI
        if errors == []:  # todo: move displaying this to frontend!
            gr.Info("Feedback sent successfully", duration=1)
        else:
            gr.Warning(
                f"Errors occurred while inserting row: {errors[0]['errors']}",
                duration=10,
            )

    def _initialise_feedback_iteration_in_table(
        self,
        project: str,
        feedback_iteration: str,
        image_names: list[str],
        dataset: str = None,
        experiment_run_name: str = None,
    ):
        """
        Initialise feedback iteration in BigQuery and upload images to GCP bucket.

        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_names: List of image names to upload
        :type image_names: list[str]
        :param dataset: Name of the evaluation set (optional)
        :type dataset: str
        :param experiment_name: Name of the experiment (optional)
        :type experiment_name: str
        """
        # ensure table exists
        ensure_table_exists(
            table_ref=self.gcp_bq_feedback_table,
            bigquery_input={
                "project": "placeholder_project",
                "feedback_iteration": "placeholder_iteration",
                "dataset": "placeholder_dataset",
                "image_name": "placeholder_name",
                "experiment_name": "placeholder_experiment",
                "likes": 0,
                "dislikes": 0,
                "comment": "placeholder_comment",
            },
        )
        # for each image, create the upload entry in feedback table
        for image in image_names:
            feedback = {
                "project": project,
                "feedback_iteration": feedback_iteration,
                "image_name": image,
                "dataset": dataset,
                "experiment_name": experiment_run_name,
                "feedback_indicator": "Neither",  # used only for initialisation of feedback iteration
                "comment": "upload",
            }
            self.write_single_feedback(feedback)

    def _save_images_to_feedback_iteration_folder(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
        image_names: list[str],
    ):
        """
        Upload images to GCP bucket.

        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_names: List of image names to upload
        :type image_names: list[str]
        :param images_directory: Path to local directory containing images to upload
        :type images_directory: str
        """
        storage_client = storage.Client(project=self.gcp_project_id)
        bucket = storage_client.bucket(self.gcp_pixaris_bucket_name)

        for filename in image_names:
            if filename.endswith((".jpg", ".jpeg", ".png", ".tif")):
                blob = bucket.blob(
                    f"results/{project}/feedback_iterations/{feedback_iteration}/{filename}"
                )
                blob.upload_from_filename(os.path.join(local_image_directory, filename))
                print(f"Uploaded {filename} to {feedback_iteration}")

    def create_feedback_iteration(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
        date_suffix: str = None,
        dataset: str = None,
        experiment_run_name: str = None,
    ):
        """
        Upload images to GCP bucket and persist initialisation of feedback iteration to BigQuery.

        :param images_directory: Path to local directory containing images to upload
        :type images_directory: str
        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param date_suffix: Date suffix for versioning. Will be set automatically to today if not provided.
        :type date_suffix: str
        :param dataset: Name of the evaluation dataset (optional)
        :type dataset: str
        :param experiment_name: Name of the experiment (optional)
        :type experiment_name: str
        """
        image_names = os.listdir(local_image_directory)

        # add date for versioning if not provided
        if not date_suffix:
            date_suffix = datetime.now().strftime("%y%m%d")
        feedback_iteration = f"{date_suffix}_{feedback_iteration}"

        self._save_images_to_feedback_iteration_folder(
            local_image_directory=local_image_directory,
            project=project,
            feedback_iteration=feedback_iteration,
            image_names=image_names,
        )
        self._initialise_feedback_iteration_in_table(
            project=project,
            feedback_iteration=feedback_iteration,
            image_names=image_names,
            dataset=dataset,
            experiment_run_name=experiment_run_name,
        )

    def load_projects_list(self) -> list[str]:
        """
        Retrieves list of projects from BigQuery table.

        Returns:
            List of project names.
        """
        print("Querying BigQuery for list of projects...")
        client = bigquery.Client(project=self.gcp_project_id)

        query = f"""
            SELECT
                DISTINCT `project`
            FROM
                {self.gcp_bq_feedback_table};
        """
        rows = client.query_and_wait(query)
        projects = rows.to_dataframe()["project"].tolist()
        projects.sort()
        self.projects = projects

        print(f"Done. Found projects: {projects}")
        return projects

    def load_all_feedback_iterations_for_project(self, project: str) -> None:
        """
        Retrieves feedback data for a project from BigQuery table. Adds paths for location of images in
        GCP bucket and local directory to the dataframe. Saves the resulting df to self.feedback_df.
        Saves the list of feedback iterations to self.feedback_iteration_choices.

        Args:
            project: str Name of the project

        Returns:
            None
        """
        print(f"Querying BigQuery for feedback data for project {project}...")
        client = bigquery.Client(project=self.gcp_project_id)

        query = f"""
            SELECT
                `project`,
                feedback_iteration,
                dataset,
                image_name,
                SUM(likes) AS likes_count,
                SUM(dislikes) AS dislikes_count,
                STRING_AGG(IF(likes > 0 AND comment <> "upload", comment, NULL), ', ') AS comments_liked,
                STRING_AGG(IF(dislikes > 0 AND comment <> "upload", comment, NULL), ', ') AS comments_disliked
            FROM
                {self.gcp_bq_feedback_table}

            WHERE
                `project` = "{project}"
            GROUP BY
                `project`,
                dataset,
                feedback_iteration,
                image_name;
        """
        rows = client.query_and_wait(query)
        df = rows.to_dataframe()

        # add paths for images to df (local and GCS bucket)
        df["image_path_bucket"] = (
            "results/"
            + df["project"]
            + "/feedback_iterations/"
            + df["feedback_iteration"]
            + "/"
            + df["image_name"]
        )
        df["image_path_local"] = (
            f"{self.local_feedback_directory}/"
            + df["project"]
            + "/feedback_iterations/"
            + df["feedback_iteration"]
            + "/"
            + df["image_name"]
        )

        # determine feedback iterations to choose from in this project
        choices = df["feedback_iteration"].unique().tolist()
        choices.sort()

        self.feedback_iteration_choices = choices
        self.feedback_df = df

        print(f"Done. Found feedback iterations: {choices}")

    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
    ) -> list[str]:
        """
        Downloads images for a feedback iteration from GCP bucket to local directory.
        Returns list of local image paths that belong to the feedback iteration.

        Args:
            feedback_iteration: str Name of the feedback iteration

        Returns:
            List of local image paths.
        """
        print(f"Downloading images for feedback iteration {feedback_iteration}...")

        # get relevant data for this feedback iteration
        iteration_df = self.feedback_df.loc[
            (
                self.feedback_df["feedback_iteration"] == feedback_iteration
            )  # only this feedback iteration
            & (self.feedback_df["dataset"] != "")  # only the entries of initialisation
        ].copy()

        # download images
        for row in iteration_df.iterrows():
            image_path_bucket = row[1]["image_path_bucket"]
            image_path_local = row[1]["image_path_local"]
            if not os.path.exists(image_path_local):
                gr.Info(f"Downloading image '{image_path_bucket}'...", duration=1)
                os.makedirs(os.path.dirname(image_path_local), exist_ok=True)
                self._download_image(image_path_bucket, image_path_local)

        print("Done.")
        return iteration_df["image_path_local"].tolist()

    def _download_image(
        self,
        image_path_bucket: str,
        image_path_local: str,
    ) -> None:
        storage_client = storage.Client(project=self.gcp_project_id)
        bucket = storage_client.bucket(self.gcp_pixaris_bucket_name)

        # download image if possible, otherwise fill with white placeholder image
        try:
            blob = bucket.blob(image_path_bucket)
            blob.download_to_filename(image_path_local)
        except Exception as e:
            print(f"Error downloading image '{image_path_bucket}': {e}")
            print("Filling with placeholder image")
            Image.new(mode="RGB", size=(256, 256), color="white").save(image_path_local)
