from pixaris.feedback_handlers.base import FeedbackHandler
from google.cloud import bigquery, storage
import gradio as gr
from datetime import datetime
import os
from PIL import Image
import logging

from pixaris.utils.bigquery import ensure_table_exists

logger = logging.getLogger(__name__)


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
        row_to_insert = self._construct_feedback_row_to_insert(feedback)

        bigquery_client = bigquery.Client(project=self.gcp_project_id)
        errors = bigquery_client.insert_rows_json(
            self.gcp_bq_feedback_table, [row_to_insert]
        )

        # Check for errors and display warnings to UI
        if errors == []:  # todo: move displaying this to frontend!
            gr.Info("Feedback sent successfully", duration=1)
        else:
            gr.Warning(
                f"Errors occurred while inserting row: {errors[0]['errors']}",
                duration=10,
            )
            raise ValueError(
                f"Errors occurred while inserting row: {errors[0]['errors']}"
            )

    def _initialise_feedback_iteration_in_table(
        self,
        project: str,
        feedback_iteration: str,
        image_names: list[str],
        dataset: str = None,
        experiment_name: str = None,
    ):
        """
        Initialise feedback iteration in BigQuery.

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
        bigquery_client = bigquery.Client(project=self.gcp_project_id)
        # ensure table exists with a dummy entry that will not be persisted
        ensure_table_exists(
            table_ref=self.gcp_bq_feedback_table,
            bigquery_input={
                "project": "placeholder_project",
                "feedback_iteration": "placeholder_iteration",
                "dataset": "placeholder_dataset",
                "image_name": "placeholder_name",
                "experiment_name": "placeholder_experiment",
                "date": datetime.now().isoformat(),
                "likes": 0,
                "dislikes": 0,
                "comment": "placeholder_comment",
            },
            bigquery_client=bigquery_client,
        )
        # for each image, create the upload entry in feedback table
        for image in image_names:
            feedback = {
                "project": project,
                "feedback_iteration": feedback_iteration,
                "dataset": dataset,
                "image_name": image,
                "experiment_name": experiment_name,
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

        for image_name in image_names:
            blob = bucket.blob(
                f"results/{project}/feedback_iterations/{feedback_iteration}/{image_name}"
            )
            blob.upload_from_filename(os.path.join(local_image_directory, image_name))
            logger.info("Uploaded %s to %s", image_name, feedback_iteration)

    def create_feedback_iteration(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
        date_suffix: str = None,
        dataset: str = None,
        experiment_name: str = None,
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
        image_names = [
            filename
            for filename in os.listdir(local_image_directory)
            if filename.endswith((".jpg", ".jpeg", ".png"))
        ]

        # add date for versioning if not provided
        if not date_suffix:
            date_suffix = datetime.now().strftime("%y%m%d")
        feedback_iteration = f"{date_suffix}_{feedback_iteration}"

        self._initialise_feedback_iteration_in_table(
            project=project,
            feedback_iteration=feedback_iteration,
            image_names=image_names,
            dataset=dataset,
            experiment_name=experiment_name,
        )

        self._save_images_to_feedback_iteration_folder(
            local_image_directory=local_image_directory,
            project=project,
            feedback_iteration=feedback_iteration,
            image_names=image_names,
        )

    def load_projects_list(self) -> list[str]:
        """
        Retrieves list of projects from BigQuery table.

        :return: List of projects
        :rtype: list[str]
        """
        logger.info("Querying BigQuery for list of projects...")
        bigquery_client = bigquery.Client(project=self.gcp_project_id)

        query = f"""
            SELECT
                DISTINCT `project`
            FROM
                {self.gcp_bq_feedback_table};
        """
        rows = bigquery_client.query_and_wait(query)
        projects = rows.to_dataframe()["project"].tolist()
        projects.sort()
        self.projects = projects

        logger.info("Done. Found projects: %s", projects)
        return projects

    def _load_feedback_df(self, project: str):
        """
        Loads feedback data from BigQuery table for a specific project.

        :param project: Name of the project
        :type project: str
        :return: DataFrame with feedback data
        :rtype: pd.DataFrame
        """
        logger.info(
            "Querying BigQuery for feedback data for project %s...",
            project,
        )
        bigquery_client = bigquery.Client(project=self.gcp_project_id)

        query = f"""
            SELECT
                `project`,
                feedback_iteration,
                STRING_AGG(dataset) AS dataset,
                image_name,
                SUM(likes) AS likes,
                SUM(dislikes) AS dislikes,
                STRING_AGG(IF(likes > 0 AND comment <> "upload", comment, NULL), ', ') AS comments_liked,
                STRING_AGG(IF(dislikes > 0 AND comment <> "upload", comment, NULL), ', ') AS comments_disliked
            FROM
                {self.gcp_bq_feedback_table}

            WHERE
                `project` = "{project}"
            GROUP BY
                `project`,
                feedback_iteration,
                image_name;
        """
        rows = bigquery_client.query_and_wait(query)
        feedback_df = rows.to_dataframe()

        # adjust feedback columns so that they are lists of strings
        feedback_df["comments_liked"] = feedback_df["comments_liked"].apply(
            lambda x: [e.strip() for e in x.split(",") if e not in ["", " "]]
            if x
            else []
        )
        feedback_df["comments_disliked"] = feedback_df["comments_disliked"].apply(
            lambda x: [e.strip() for e in x.split(",") if e not in ["", " "]]
            if x
            else []
        )

        # add paths for images to feedback_df (local and GCS bucket)
        feedback_df["image_path_bucket"] = (
            "results/"
            + feedback_df["project"]
            + "/feedback_iterations/"
            + feedback_df["feedback_iteration"]
            + "/"
            + feedback_df["image_name"]
        )
        feedback_df["image_path_local"] = (
            f"{self.local_feedback_directory}/"
            + feedback_df["project"]
            + "/feedback_iterations/"
            + feedback_df["feedback_iteration"]
            + "/"
            + feedback_df["image_name"]
        )

        return feedback_df

    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
        sorting: str = "image_name",
    ) -> list[str]:
        """
        Downloads images for a feedback iteration from GCP bucket to local directory.
        Returns list of local image paths that belong to the feedback iteration.

        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param sorting: Sorting option for the images. Can be "image_name", "likes", or "dislikes". Default is "image_name".
        :type sorting: str
        :return: List of local image paths that belong to the feedback iteration.
        :rtype: list[str]
        """
        logger.info(
            "Downloading images for feedback iteration %s...",
            feedback_iteration,
        )

        # get relevant data for this feedback iteration
        iteration_df = self.feedback_df.loc[
            # only this feedback iteration
            self.feedback_df["feedback_iteration"] == feedback_iteration
        ].copy()

        # download images
        for row in iteration_df.iterrows():
            image_path_bucket = row[1]["image_path_bucket"]
            image_path_local = row[1]["image_path_local"]
            if not os.path.exists(image_path_local):
                gr.Info(f"Downloading image '{image_path_bucket}'...", duration=1)
                os.makedirs(os.path.dirname(image_path_local), exist_ok=True)
                self._download_image(image_path_bucket, image_path_local)
        logger.info("Done with download.")

        # sort images according to user preference
        sorted_df = self._sort_iteration_df(
            iteration_df=iteration_df,
            sorting=sorting,
        )
        # deduplicate image paths
        image_paths_local = sorted_df["image_path_local"].unique().tolist()
        return image_paths_local

    def _download_image(
        self,
        image_path_bucket: str,
        image_path_local: str,
    ) -> None:
        """
        Downloads image from GCP bucket to local directory. If the image cannot be downloaded,
        a white placeholder image is created and saved instead.

        :param image_path_bucket: Path to the image in GCP bucket
        :type image_path_bucket: str
        :param image_path_local: Path to the local directory where the image will be saved
        :type image_path_local: str
        """
        storage_client = storage.Client(project=self.gcp_project_id)
        bucket = storage_client.bucket(self.gcp_pixaris_bucket_name)

        # download image if possible, otherwise fill with white placeholder image
        try:
            blob = bucket.blob(image_path_bucket)
            blob.download_to_filename(image_path_local, timeout=400)
        except Exception as e:
            logger.error("Error downloading image '%s': %s", image_path_bucket, e)
            logger.warning("Filling with placeholder image")
            Image.new(mode="RGB", size=(256, 256), color="white").save(image_path_local)
