import json
import random
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw


num_entries = 2  # Define the number of dummy data entries you want to create
current_directory = os.getcwd()
local_results_folder = "local_results"
project_name = "dummy_project"
dataset_name = "dummy_dataset"
base_experiment_run_name = "dummy_experiment_run_"
file_name = "experiment_results.jsonl"
base_output_directory = os.path.join(
    current_directory, local_results_folder, project_name, dataset_name
)


def random_date():
    start_date = datetime(2025, 1, 1)
    return (start_date + timedelta(days=random.randint(0, 1000))).strftime("%Y-%m-%d")


def random_timestamp():
    start_date = datetime(2025, 1, 1)
    random_datetime = start_date + timedelta(
        days=random.randint(0, 1000), seconds=random.randint(0, 86400)
    )
    return random_datetime.isoformat()


def create_tiger_image():
    # Create a blank 64x64 pixel image
    img = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(img)

    # Define colors
    orange = (255, 165, 0)
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Draw a simple tiger head shape
    draw.ellipse([16, 16, 48, 48], fill=orange)  # Head

    # Draw ears
    draw.polygon([(16, 16), (20, 8), (24, 16)], fill=orange)
    draw.polygon([(48, 16), (44, 8), (40, 16)], fill=orange)

    # Draw black stripes
    draw.line([(28, 20), (24, 28)], fill=black, width=2)  # Left stripe
    draw.line([(36, 20), (40, 28)], fill=black, width=2)  # Right stripe
    draw.arc([24, 28, 40, 44], start=0, end=180, fill=black, width=2)  # Top stripe
    draw.arc([20, 36, 44, 52], start=180, end=360, fill=black, width=2)  # Bottom stripe

    # Draw eyes
    draw.ellipse([(26, 30), (30, 34)], fill=white)  # Left eye
    draw.ellipse([(38, 30), (42, 34)], fill=white)  # Right eye
    draw.point([(28, 32), (40, 32)], fill=black)  # Pupils

    # Draw nose
    draw.polygon([(31, 40), (33, 38), (35, 40)], fill=black)

    # Draw mouth
    draw.arc([30, 42, 34, 46], start=0, end=180, fill=black, width=1)
    draw.arc([32, 42, 36, 46], start=0, end=180, fill=black, width=1)

    return img


def create_dummy_data_entries(
    base_output_directory, num_entries, base_experiment_run_name
):
    # Create the base output directory
    os.makedirs(base_output_directory, exist_ok=True)

    dummy_experiment_data = []
    dummy_feedback_data = []
    for i in range(num_entries):
        experiment_run_name = f"{base_experiment_run_name}{i + 1}"

        experiment_directory = os.path.join(base_output_directory, experiment_run_name)
        os.makedirs(experiment_directory, exist_ok=True)

        # create experiment output image
        image_name = f"{experiment_run_name}.jpg"

        image_path = os.path.join(experiment_directory, image_name)
        img = create_tiger_image()
        img.save(image_path)

        experiment_entry = {
            "timestamp": random_timestamp(),
            "initials": f"AB{i + 1}",
            "experiment_name": experiment_run_name,
            "experiment_folder_name": experiment_run_name,
            "execution_time_per_image": round(random.uniform(0, 5), 2),
            "llm_reality": round(random.uniform(0, 1), 2),
            "llm_similarity": round(random.uniform(0, 1), 2),
            "llm_errors": round(random.uniform(0, 1), 2),
            "llm_todeloy": round(random.uniform(0, 1), 2),
        }
        dummy_experiment_data.append(experiment_entry)

        feedback_entry = {
            "project": project_name,
            "feedback_iteration": "dummy_iteration",
            "dataset": "",
            "image_name": image_name,
            "experiment_name": experiment_run_name,
            "date": random_date(),
            "comment": "dummy_comment",
            "likes": random.randint(0, 100),
            "dislikes": random.randint(0, 100),
        }
        dummy_feedback_data.append(feedback_entry)
        feedback_iteration_path = os.path.join(
            current_directory,
            local_results_folder,
            project_name,
            "feedback_iterations",
            "dummy_iteration",
        )
        # save dummy images in feedback iteration
        os.makedirs(feedback_iteration_path, exist_ok=True)
        img.save(os.path.join(feedback_iteration_path, "dummy_experiment_run_1.jpg"))
        img.save(os.path.join(feedback_iteration_path, "dummy_experiment_run_2.jpg"))

    return dummy_experiment_data, dummy_feedback_data


def create_dummy_files(base_output_directory, num_entries, base_experiment_run_name):
    dummy_experiment_data, dummy_feedback_data = create_dummy_data_entries(
        base_output_directory, num_entries, base_experiment_run_name
    )
    output_path = os.path.join(base_output_directory, "experiment_results.jsonl")
    with open(output_path, "w") as f:
        for item in dummy_experiment_data:
            f.write(json.dumps(item) + "\n")

    feedback_tracking_path = os.path.join(
        current_directory,
        local_results_folder,
        project_name,
        "feedback_tracking.jsonl",
    )
    with open(feedback_tracking_path, "w") as f:
        for item in dummy_feedback_data:
            f.write(json.dumps(item) + "\n")

    print(f"dummy data and images created in '{base_output_directory}'")


if __name__ == "__main__":
    create_dummy_files(base_output_directory, num_entries, base_experiment_run_name)
