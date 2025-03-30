import os
import subprocess
import threading
import webbrowser
import time
import logging
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use pathlib for better path handling
WORKING_DIR = Path(os.getcwd())

BACKEND_DIR = WORKING_DIR / "Simulacra" / "reverie" / "backend_server"
SIMULATION_CONTROLLER_PATH = BACKEND_DIR / "simulation_controller.json"
CONFIG_PATH = WORKING_DIR / "medsim" / "configs" / "config_sim.yaml"
LOGS_PATH = WORKING_DIR / "logs"

# Create logs directory
LOGS_PATH.mkdir(exist_ok=True)

# Scenario loader classes
from medsim.core.scenario import (
    ScenarioLoaderMedQA,
    ScenarioLoaderMedQAExtended,
    ScenarioLoaderNEJM,
    ScenarioLoaderNEJMExtended,
    ScenarioLoaderMIMICIV,
    resolve_model_name,
)

# Mapping of dataset names to their loader classes
SCENARIO_LOADERS = {
    "MedQA": ScenarioLoaderMedQA,
    "MedQA_Ext": ScenarioLoaderMedQAExtended,
    "NEJM": ScenarioLoaderNEJM,
    "NEJM_Ext": ScenarioLoaderNEJMExtended,
    "MIMICIV": ScenarioLoaderMIMICIV,
}

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and return configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise

def load_scenario_loader(dataset: str):
    """Get the appropriate scenario loader based on dataset name."""
    loader_class = SCENARIO_LOADERS.get(dataset)
    if not loader_class:
        logger.error(f"Dataset {dataset} does not exist.")
        raise ValueError(f"Dataset {dataset} does not exist.")
    return loader_class()

def print_summary():
    """Print summary of simulation results."""
    try:
        with open(SIMULATION_CONTROLLER_PATH, 'r') as file:
            data = json.load(file)
            
        total_correct = data.get("total_correct", 0)
        total_scenarios = data.get("total_scenarios", 0)
        
        accuracy = (total_correct / total_scenarios) * 100 if total_scenarios > 0 else 0
        
        summary = [
            f"\n===== SIMULATION SUMMARY =====",
            f"Total Correct Diagnoses: {total_correct}",
            f"Total Scenarios Presented: {total_scenarios}",
            f"Overall Accuracy: {accuracy:.2f}%",
            f"==============================="
        ]
        
        for line in summary:
            logger.info(line)
    except Exception as e:
        logger.error(f"Failed to print summary: {e}")

def update_json_file(file_path: Path, updates: Dict[str, Any]):
    """Update JSON file with new values."""
    try:
        # Create default data if file doesn't exist
        if not file_path.exists():
            logger.info(f"File not found. Creating a new file: {file_path}")
            data = {"simulation_active": 0, "simulation_index": 0, "total_scenarios": 0, "total_correct": 0}
        else:
            # Load existing data
            with open(file_path, 'r') as file:
                data = json.load(file)
        
        # Update values
        data.update(updates)
        
        # Save updated data
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            
        return True
    except Exception as e:
        logger.error(f"Failed to update JSON file {file_path}: {e}")
        return False

def run_backend_server(target: str, stop_event: threading.Event):
    """Run the backend server for a specific target scenario."""
    try:
        # Backend configuration
        backend_script_file = "reverie.py"
        url = "http://127.0.0.1:8000/simulator_home"
        
        logger.info(f"Running backend server at: {url}")
        logger.info(f"Target scenario: {target}")
        
        # Navigate to backend directory
        os.chdir(BACKEND_DIR)
        logger.info(f"Changed directory to: {BACKEND_DIR}")
        
        # Generate timestamp for log file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = LOGS_PATH / f"{target}_{timestamp}.txt"
        
        # Construct command
        command = f'python "{backend_script_file}" --origin "test-simulation" --target "{target}" --command "toq"'
        logger.info(f"Executing command: {command}")
        
        # Run command with output logging
        with open(log_file, "w") as log:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True
            )
            
            for line in process.stdout:
                logger.info(line.strip())  # Log to console
                log.write(line)  # Write to log file
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            logger.info(f"Server ran successfully. Logs saved to: {log_file}")
        else:
            logger.error(f"Server failed with return code {process.returncode}. Check logs: {log_file}")
            
    except Exception as e:
        logger.error(f"Error running backend server: {e}")
    finally:
        # Signal completion
        stop_event.set()
        # Change back to original directory
        os.chdir(WORKING_DIR)

def open_webpage(url: str, delay: int, stop_event: threading.Event):
    """Open the simulation webpage after a delay."""
    try:
        logger.info(f"Waiting {delay} seconds before opening webpage: {url}")
        time.sleep(delay)
        
        if not stop_event.is_set():
            logger.info(f"Opening webpage: {url}")
            webbrowser.open(url)
        else:
            logger.info("Webpage opening skipped as backend has finished.")
    except Exception as e:
        logger.error(f"Error opening webpage: {e}")

def run_scenarios(num_scenarios: int, delay: int = 5):
    """Run multiple clinical scenarios in sequence."""
    try:
        # Initialize counters
        total_scenarios = 0
        total_correct = 0
        
        # Reset simulation state
        update_json_file(
            SIMULATION_CONTROLLER_PATH, 
            {
                "total_scenarios": total_scenarios, 
                "total_correct": total_correct, 
                "num_scenarios": num_scenarios
            }
        )
        
        # Run each scenario
        for i in range(num_scenarios):
            logger.info(f"\n=== Starting Scenario {i+1}/{num_scenarios} ===")
            
            # Update scenario index
            update_json_file(SIMULATION_CONTROLLER_PATH, {"simulation_index": i})
            
            # Setup for this scenario
            target = f"scenario-{i}"
            url = "http://127.0.0.1:8000/simulator_home"
            stop_event = threading.Event()
            
            # Create and start threads
            backend_thread = threading.Thread(
                target=run_backend_server, 
                args=(target, stop_event),
                name=f"Backend-{i}"
            )
            
            webpage_thread = threading.Thread(
                target=open_webpage, 
                args=(url, delay, stop_event),
                name=f"Webpage-{i}"
            )
            
            backend_thread.start()
            webpage_thread.start()
            
            # Wait for completion
            backend_thread.join()
            webpage_thread.join()
            
            logger.info(f"=== Scenario {i+1}/{num_scenarios} completed ===\n")
            
        logger.info("All scenarios have completed.")
        print_summary()
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user.")
        print_summary()
    except Exception as e:
        logger.error(f"Error running scenarios: {e}")
        print_summary()

def main():
    """Main function to run the simulation."""
    try:
        # Load configuration
        logger.info(f"Loading configuration from {CONFIG_PATH}")
        config = load_config(CONFIG_PATH)
        
        # Initialize scenario loader
        dataset = config["scenario"]["dataset"]
        logger.info(f"Using dataset: {dataset}")
        scenario_loader = load_scenario_loader(dataset)
        
        # Determine number of scenarios
        configured_num = config["scenario"]["num_scenarios"]
        total_available = scenario_loader.num_scenarios
        num_scenarios = configured_num or total_available
        
        logger.info(f"Running {num_scenarios} scenarios (out of {total_available} available)")
        
        # Run the simulation
        run_scenarios(10)  # Currently hardcoded to 1 scenario
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")

if __name__ == "__main__":
    logger.info("Starting clinical scenario simulation")
    main()