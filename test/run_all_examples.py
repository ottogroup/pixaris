import os
import sys
import traceback
import subprocess
import time

# this is a file that runs all examples after oneanother. Intended for testing, however not included in automated testing, since secrets and tunnels are nessecary.

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../examples")

# Collect all .py files in the examples directory and subdirectories
example_files = []
for root, dirs, files in os.walk(EXAMPLES_DIR):
    for file in files:
        if file.endswith(".py"):
            example_files.append(os.path.join(root, file))

# Ensure create_dummy_dataset_for_Generator_locally.py runs first if present
dummy_data_generation_file = os.path.join(
    EXAMPLES_DIR, "dummy_data_creation", "create_dummy_dataset_for_Generator_locally.py"
)
dummy_data_creation_dir = os.path.join(EXAMPLES_DIR, "dummy_data_creation")
dummy_data_files = []

# Collect all files in dummy_data_creation except the data creation file to run them afterwards
for file in example_files[:]:
    if file.startswith(dummy_data_creation_dir):
        if file == dummy_data_generation_file:
            continue
        dummy_data_files.append(file)
        example_files.remove(file)

data_generation_examples = []
if os.path.exists(dummy_data_generation_file):
    data_generation_examples.append(dummy_data_generation_file)
data_generation_examples.extend(sorted(dummy_data_files))
other_example_files = example_files

print(
    f"Found {len(data_generation_examples) + len(other_example_files)} example scripts."
)

failures = []

# Run dummy data creation scripts in the foreground (wait for them to finish)
for example in data_generation_examples:
    print(f"\n========= Running: {example} =========")
    try:
        exit_code = os.system(f'{sys.executable} "{example}"')
        if exit_code != 0:
            print(f"[FAIL] {example} exited with code {exit_code}")
            failures.append(example)
        else:
            print(f"[PASS] {example}")
    except Exception as e:
        print(f"[ERROR] Exception while running {example}: {e}")
        traceback.print_exc()
        failures.append(example)

# Run all other examples sequentially in the foreground (wait for each to finish)
for example in other_example_files:
    print(f"\n========= Running: {example} =========")
    try:
        # Special handling for deploy_frontend_locally_*.py files
        if example.endswith(
            "deploy_frontend_locally_with_GCP_handling.py"
        ) or example.endswith("deploy_frontend_locally_with_local_handling.py"):
            print("[INFO] This script will be terminated after 30 seconds...")
            proc = subprocess.Popen([sys.executable, example])
            time.sleep(30)
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"[STOPPED] {example} was terminated after 30 seconds.")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(
                    f"[KILLED] {example} did not terminate gracefully and was killed."
                )
            # Treat exit code -15 (SIGTERM) as success for these scripts
            exit_code = proc.returncode
            if exit_code == -15:
                print(f"[PASS] {example} (terminated as intended)")
            elif exit_code != 0:
                print(f"[FAIL] {example} exited with code {exit_code}")
                failures.append(example)
            else:
                print(f"[PASS] {example}")
        else:
            exit_code = os.system(f'{sys.executable} "{example}"')
            if exit_code != 0:
                print(f"[FAIL] {example} exited with code {exit_code}")
                failures.append(example)
            else:
                print(f"[PASS] {example}")
    except Exception as e:
        print(f"[ERROR] Exception while running {example}: {e}")
        traceback.print_exc()
        failures.append(example)

print("\n=== Summary ===")
if failures:
    print(f"{len(failures)} example(s) failed to start or run:")
    for fail in failures:
        print(f" - {fail}")
else:
    print("All examples launched!")
