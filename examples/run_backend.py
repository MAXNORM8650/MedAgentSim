import os
import subprocess
from datetime import datetime
import yaml
import json

import threading
import webbrowser
import time
import logging

working_dir = os.getcwd()

logger = logging.getLogger(__name__)

def print_summary():
    json_file_path = f"{working_dir}\\Simulacra\\reverie\\backend_server\\simulation_controller.json"
    
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        
    total_correct = data["total_correct"]
    total_scenarios = data["total_scenarios"]
    
    accuracy = (total_correct / total_scenarios) * 100 if total_scenarios > 0 else 0
    summary = [
        f"\nTotal Correct Diagnoses: {total_correct}",
        f"Total Scenarios Presented: {total_scenarios}",
        f"Overall Accuracy: {accuracy:.2f}%",
    ]
    for line in summary:
        print(line)


from TOQ.scenario import (
    ScenarioLoaderMedQA,
    ScenarioLoaderMedQAExtended,
    ScenarioLoaderNEJM,
    ScenarioLoaderNEJMExtended,
    ScenarioLoaderMIMICIV,
    resolve_model_name,
)

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_scenario_loader(dataset: str):
    loaders = {
        "MedQA": ScenarioLoaderMedQA,
        "MedQA_Ext": ScenarioLoaderMedQAExtended,
        "NEJM": ScenarioLoaderNEJM,
        "NEJM_Ext": ScenarioLoaderNEJMExtended,
        "MIMICIV": ScenarioLoaderMIMICIV,
    }
    loader_class = loaders.get(dataset)
    if loader_class:
        return loader_class()
    else:
        logger.error(f"Dataset {dataset} does not exist.")
        raise ValueError(f"Dataset {dataset} does not exist.")

config = load_config(f"{working_dir}\\TOQ\\configs\\config_sim.yaml")
scenario_loader = load_scenario_loader(config["scenario"]["dataset"])
actual_num_scenarios = config["scenario"]["num_scenarios"] or scenario_loader.num_scenarios

print(actual_num_scenarios)

def run_backend_server(target, stop_event):
    # Configuration
    BACKEND_SCRIPT_PATH = f"{working_dir}\\Simulacra\\reverie\\backend_server"
    print(BACKEND_SCRIPT_PATH)
    BACKEND_SCRIPT_FILE = "reverie.py"
    LOGS_PATH = "../../logs"

    # Print the server information
    print("Running backend server at: http://127.0.0.1:8000/simulator_home")

    # Navigate to the backend script directory
    backend_path = os.path.abspath(BACKEND_SCRIPT_PATH)
    if not os.path.exists(backend_path):
        raise FileNotFoundError(f"Backend script path does not exist: {backend_path}")
    
    os.chdir(backend_path)
    print(f"Changed directory to: {backend_path}")

    # Generate a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"Timestamp: {timestamp}")

    # Create the logs directory if it doesn't exist
    logs_path = os.path.abspath(LOGS_PATH)
    os.makedirs(logs_path, exist_ok=True)

    # Log file name
    log_file = os.path.join(logs_path, f"{target}_{timestamp}.txt")

    # Construct the command to run the backend script
    command = f'python "{BACKEND_SCRIPT_FILE}" --origin "test-simulation" --target "{target}" --command "toq"'

    print(f"Executing command: {command}")

    # Run the command and log output
    with open(log_file, "w") as log:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")  # Print to console
            log.write(line)  # Write to log file

    # Wait for the process to complete
    process.wait()
    if process.returncode == 0:
        print(f"Server ran successfully. Logs saved to: {log_file}")
    else:
        print(f"Server failed with return code {process.returncode}. Check logs: {log_file}")
    stop_event.set()  # Signal that the backend thread is finished


# Function to open the webpage after a delay
def open_webpage(url, delay, stop_event):
    print(f"Waiting {delay} seconds before opening webpage: {url}")
    time.sleep(delay)
    if not stop_event.is_set():  # Only open the webpage if the backend is still running
        print(f"Opening webpage: {url}")
        webbrowser.open(url)
    else:
        print(f"Webpage opening skipped as backend has finished.")


def update_scenarios_json(json_file_path, total_scenarios, total_correct, num_scenarios):
    if not os.path.exists(json_file_path):
        print(f"File not found. Creating a new file: {json_file_path}")
        # Create a new file with the default structure
        data = {"simulation_active": 0, "simulation_index": 0, "total_scenarios": 0, "total_correct": 0}
    else:
        # Load the existing JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

    # Update values
    data["total_scenarios"] = total_scenarios
    data["total_correct"] = total_correct
    data["num_scenarios"] = num_scenarios

    # Save the JSON data (either new or updated) back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)
        
def update_id_json(json_file_path, scenario_id):
    if not os.path.exists(json_file_path):
        print(f"File not found. Creating a new file: {json_file_path}")
        # Create a new file with the default structure
        data = {"simulation_active": 0, "simulation_index": 0, "total_scenarios": 0, "total_correct": 0}
    else:
        # Load the existing JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

    # Update values
    data["simulation_index"] = scenario_id

    # Save the JSON data (either new or updated) back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)


# Main function to run scenarios
def run_scenarios(num_scenarios, delay=5):
    total_scenarios = 0
    total_correct = 0
    update_scenarios_json(f"{working_dir}\\Simulacra\\reverie\\backend_server\\simulation_controller.json", total_scenarios, total_correct, num_scenarios)

    for i in range(num_scenarios):   
        update_id_json(f"{working_dir}\\Simulacra\\reverie\\backend_server\\simulation_controller.json", i)
        
        target = f"scenario-{i}"
        url = "http://127.0.0.1:8000/simulator_home"
        
        # Create a stop event for this scenario
        stop_event = threading.Event()

        # Create a thread for the backend server
        backend_thread = threading.Thread(target=run_backend_server, args=(target, stop_event))

        # Create a thread to open the webpage
        webpage_thread = threading.Thread(target=open_webpage, args=(url, delay, stop_event))

        # Start both threads
        backend_thread.start()
        webpage_thread.start()

        # Wait for both threads to complete before moving to the next scenario
        backend_thread.join()
        webpage_thread.join()

        print(f"Scenario {i} completed.\n")

    print("All scenarios have completed.")
    print_summary()


run_scenarios(1)