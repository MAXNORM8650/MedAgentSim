import argparse
import os
import json
import time
import logging
from typing import Tuple, Optional

import openai
import yaml
from agent import (
    MeasurementAgent,
    PatientAgent,
    DoctorAgent,
    BAgent,
    compare_results,
)
# from Lcgent import LBAgent
from scenario import (
    ScenarioLoaderMedQA,
    ScenarioLoaderMedQAExtended,
    ScenarioLoaderNEJM,
    ScenarioLoaderNEJMExtended,
    ScenarioLoaderMIMICIV,
    resolve_model_name,
)
from query import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("simulation.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """
    Loads the YAML configuration file.

    Args:
        config_path (str): Path to the YAML config file.

    Returns:
        dict: Configuration parameters.
    """
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}.")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found.")
        raise
    except yaml.YAMLError as exc:
        logger.error(f"Error parsing YAML file: {exc}")
        raise


def main(config: dict) -> None:
    """
    Main function to run the medical diagnosis simulation.
    """
    try:
        # Extract API keys
        api_key = config["api_keys"].get("openai")
        replicate_api_key = config["api_keys"].get("replicate")
        anthropic_api_key = config["api_keys"].get("anthropic")

        # Set API keys
        openai.api_key = api_key
        anthropic_llms = {"claude3.5sonnet"}
        replicate_llms = {
            "llama-3-70b-instruct",
            "llama-2-70b-chat",
            "mixtral-8x7b",
        }

        # Set environment variables for specific LLMs
        if (
            config["language_models"]["patient"] in replicate_llms
            or config["language_models"]["doctor"] in replicate_llms
        ):
            os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
            logger.info("Set REPLICATE_API_TOKEN.")
        if (
            config["language_models"]["doctor"] in anthropic_llms
            and anthropic_api_key
        ):
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
            logger.info("Set ANTHROPIC_API_KEY.")

        # Set output directory with timestamp for better organization
        print(config)
        test_path = f"{os.getcwd()}\\output"#config['scenario']["output_dir"]

        try:
            os.makedirs(test_path, exist_ok=True)
            print(f"Directory created: {test_path}")
        except Exception as e:
            print(f"Failed to create directory: {e}")
        # breakpoint()
        output_dir = test_path
        logger.info(f"Output directory set to {output_dir}.")

        # Load the appropriate scenario loader
        scenario_loader = load_scenario_loader(config["scenario"]["dataset"])

        # Resolve model names from aliases
        (
            doctor_llm,
            patient_llm,
            measurement_llm,
            moderator_llm,
        ) = resolve_all_model_names(
            config["language_models"]["doctor"],
            config["language_models"]["patient"],
            config["language_models"]["measurement"],
            config["language_models"]["moderator"],
        )
        logger.info(
            f"Resolved LLMs: Doctor={doctor_llm}, Patient={patient_llm}, "
            f"Measurement={measurement_llm}, Moderator={moderator_llm}"
        )

        actual_num_scenarios = config["scenario"]["num_scenarios"] or scenario_loader.num_scenarios
        logger.info(f"Starting simulation for {actual_num_scenarios} scenarios.")

        # Run simulation
        total_correct, total_scenarios = run_simulation(
            scenario_loader,
            config["inference"]["type"],
            doctor_llm,
            patient_llm,
            measurement_llm,
            moderator_llm,
            config["biases"]["doctor"],
            config["biases"]["patient"],
            config["scenario"]["total_inferences"],
            config["scenario"]["image_request"],
            output_dir,
            config["scenario"]["num_scenarios"],
        )

        print_summary(total_correct, total_scenarios)

    except Exception as e:
        logger.exception("An error occurred during the simulation.")
        raise e
    
def prep(config, total_scenarios, total_correct, num_scenarios, scenario_id):
    try:
        # Extract API keys
        api_key = config["api_keys"].get("openai")
        replicate_api_key = config["api_keys"].get("replicate")
        anthropic_api_key = config["api_keys"].get("anthropic")

        # Set API keys
        openai.api_key = api_key
        anthropic_llms = {"claude3.5sonnet"}
        replicate_llms = {
            "llama-3-70b-instruct",
            "llama-2-70b-chat",
            "mixtral-8x7b",
        }

        # Set environment variables for specific LLMs
        if (
            config["language_models"]["patient"] in replicate_llms
            or config["language_models"]["doctor"] in replicate_llms
        ):
            os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
            logger.info("Set REPLICATE_API_TOKEN.")
        if (
            config["language_models"]["doctor"] in anthropic_llms
            and anthropic_api_key
        ):
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
            logger.info("Set ANTHROPIC_API_KEY.")

        # Set output directory with timestamp for better organization
        print(config)
        test_path = f"{os.getcwd()}\\output"#config['scenario']["output_dir"]

        try:
            os.makedirs(test_path, exist_ok=True)
            print(f"Directory created: {test_path}")
        except Exception as e:
            print(f"Failed to create directory: {e}")
        # breakpoint()
        output_dir = test_path
        logger.info(f"Output directory set to {output_dir}.")

        # Load the appropriate scenario loader
        scenario_loader = load_scenario_loader(config["scenario"]["dataset"])

        # Resolve model names from aliases
        (
            doctor_llm,
            patient_llm,
            measurement_llm,
            moderator_llm,
        ) = resolve_all_model_names(
            config["language_models"]["doctor"],
            config["language_models"]["patient"],
            config["language_models"]["measurement"],
            config["language_models"]["moderator"],
        )
        logger.info(
            f"Resolved LLMs: Doctor={doctor_llm}, Patient={patient_llm}, "
            f"Measurement={measurement_llm}, Moderator={moderator_llm}"
        )

        actual_num_scenarios = config["scenario"]["num_scenarios"] or scenario_loader.num_scenarios
        logger.info(f"Starting simulation for {actual_num_scenarios} scenarios.")

        # Run simulation
        is_correct = run_simulation_idx(
            scenario_loader,
            config["inference"]["type"],
            doctor_llm,
            patient_llm,
            measurement_llm,
            moderator_llm,
            config["biases"]["doctor"],
            config["biases"]["patient"],
            config["scenario"]["total_inferences"],
            config["scenario"]["image_request"],
            output_dir,
            total_scenarios,
            total_correct,
            num_scenarios,
            scenario_id
        )

        return is_correct

    except Exception as e:
        logger.exception("An error occurred during the simulation.")
        raise e


def load_scenario_loader(dataset: str):
    """
    Loads the appropriate scenario loader based on the dataset.

    Args:
        dataset (str): Name of the dataset.

    Returns:
        ScenarioLoader: An instance of the scenario loader.

    Raises:
        ValueError: If the dataset is not recognized.
    """
    loaders = {
        "MedQA": ScenarioLoaderMedQA,
        "MedQA_Ext": ScenarioLoaderMedQAExtended,
        "NEJM": ScenarioLoaderNEJM,
        "NEJM_Ext": ScenarioLoaderNEJMExtended,
        "MIMICIV": ScenarioLoaderMIMICIV,
    }
    loader_class = loaders.get(dataset)
    if loader_class:
        logger.info(f"Loading scenario loader for dataset: {dataset}")
        return loader_class()
    else:
        logger.error(f"Dataset {dataset} does not exist.")
        raise ValueError(f"Dataset {dataset} does not exist.")


def resolve_all_model_names(
    doctor_llm: str,
    patient_llm: str,
    measurement_llm: str,
    moderator_llm: str,
) -> Tuple[str, str, str, str]:
    """
    Resolves all model names from their aliases.

    Args:
        doctor_llm (str): Doctor LLM alias.
        patient_llm (str): Patient LLM alias.
        measurement_llm (str): Measurement LLM alias.
        moderator_llm (str): Moderator LLM alias.

    Returns:
        Tuple[str, str, str, str]: Resolved model names.
    """
    resolved_names = (
        resolve_model_name(doctor_llm),
        resolve_model_name(patient_llm),
        resolve_model_name(measurement_llm),
        resolve_model_name(moderator_llm),
    )
    logger.debug(f"Resolved model names: {resolved_names}")
    return resolved_names


def run_simulation(
    scenario_loader,
    inf_type: str,
    doctor_llm: str,
    patient_llm: str,
    measurement_llm: str,
    moderator_llm: str,
    doctor_bias: str,
    patient_bias: str,
    total_inferences: int,
    img_request: bool,
    output_dir: str,
    num_scenarios: Optional[int],
) -> Tuple[int, int]:
    """
    Runs the medical diagnosis simulation.

    Returns:
        Tuple[int, int]: Total correct diagnoses and total scenarios presented.
    """
    meas_agent = MeasurementAgent(backend_str=measurement_llm)
    patient_agent = PatientAgent(backend_str=patient_llm)
    doctor_agent = DoctorAgent(backend_str=doctor_llm, graph=True)
    mpipe = BAgent(moderator_llm)# patient_agent.pipe#BAgent(moderator_llm)

    total_correct = 0
    total_scenarios = 0

    actual_num_scenarios = num_scenarios or scenario_loader.num_scenarios
    logger.info(f"Starting simulation for {actual_num_scenarios} scenarios.")

    for scenario_id in range(min(actual_num_scenarios, scenario_loader.num_scenarios)):
        total_scenarios += 1
        dialogue_history = []
        logger.debug(f"Starting scenario {scenario_id}.")

        # Initialize scenario and agents
        scenario = scenario_loader.get_scenario(id=scenario_id)
        meas_agent.update_scenario(scenario=scenario)
        patient_agent.update_scenario(scenario=scenario, bias_present=patient_bias)
        doctor_agent.update_scenario(
            scenario=scenario,
            bias_present=doctor_bias,
            max_infs=total_inferences,
            img_request=img_request,
        )

        # Run interaction loop
        is_correct = run_interaction_loop(
            scenario=scenario,
            meas_agent=meas_agent,
            patient_agent=patient_agent,
            doctor_agent=doctor_agent,
            mpipe=mpipe,
            moderator_llm=moderator_llm,
            inf_type=inf_type,
            total_inferences=total_inferences,
            img_request=img_request,
            dialogue_history=dialogue_history,
            output_dir=output_dir,
            scenario_id=scenario_id,
            total_correct=total_correct,
            total_scenarios=total_scenarios,
        )
        if is_correct:
            total_correct += 1
        logger.debug(
            f"Scenario {scenario_id} completed with "
            f"{'correct' if is_correct else 'incorrect'} diagnosis."
        )

    logger.info("Simulation completed.")
    return total_correct, total_scenarios


def run_simulation_idx(
    scenario_loader,
    inf_type: str,
    doctor_llm: str,
    patient_llm: str,
    measurement_llm: str,
    moderator_llm: str,
    doctor_bias: str,
    patient_bias: str,
    total_inferences: int,
    img_request: bool,
    output_dir: str,
    total_scenarios: int,
    total_correct: int,
    num_scenarios: int,
    scenario_id: int,
) -> Tuple[int, int]:
    """
    Runs the medical diagnosis simulation.

    Returns:
        Tuple[int, int]: Total correct diagnoses and total scenarios presented.
    """
    meas_agent = MeasurementAgent(backend_str=measurement_llm)
    patient_agent = PatientAgent(backend_str=patient_llm)
    doctor_agent = DoctorAgent(backend_str=doctor_llm, graph=True)
    mpipe = BAgent(moderator_llm)# patient_agent.pipe#BAgent(moderator_llm)

    logger.info(f"Starting simulation {total_scenarios} out of {num_scenarios} scenarios.")

    dialogue_history = []
    logger.debug(f"Starting scenario {scenario_id}.")

    # Initialize scenario and agents
    scenario = scenario_loader.get_scenario(id=scenario_id)
    meas_agent.update_scenario(scenario=scenario)
    patient_agent.update_scenario(scenario=scenario, bias_present=patient_bias)
    doctor_agent.update_scenario(
        scenario=scenario,
        bias_present=doctor_bias,
        max_infs=total_inferences,
        img_request=img_request,
    )

    # Run interaction loop
    is_correct = run_interaction_loop(
        scenario=scenario,
        meas_agent=meas_agent,
        patient_agent=patient_agent,
        doctor_agent=doctor_agent,
        mpipe=mpipe,
        moderator_llm=moderator_llm,
        inf_type=inf_type,
        total_inferences=total_inferences,
        img_request=img_request,
        dialogue_history=dialogue_history,
        output_dir=output_dir,
        scenario_id=scenario_id,
        total_correct=total_correct,
        total_scenarios=total_scenarios,
    )
    
    logger.debug(
        f"Scenario {scenario_id} completed with "
        f"{'correct' if is_correct else 'incorrect'} diagnosis."
    )

    logger.info("Simulation completed.")
    return is_correct


def run_interaction_loop(
    scenario,
    meas_agent: MeasurementAgent,
    patient_agent: PatientAgent,
    doctor_agent: DoctorAgent,
    mpipe: BAgent,
    moderator_llm: str,
    inf_type: str,
    total_inferences: int,
    img_request: bool,
    dialogue_history: list,
    output_dir: str,
    scenario_id: int,
    total_correct: int,
    total_scenarios: int,
) -> bool:
    """
    Runs the interaction loop for a single scenario.

    Returns:
        bool: True if the diagnosis was correct, False otherwise.
    """
    doctor_dialogue = ""
    is_correct = False

    for inf_id in range(total_inferences):
        # Determine if images are requested
        imgs_requested = (
            img_request
            and scenario.dataset == "NEJM"
            and "REQUEST IMAGES" in doctor_dialogue
        )
        logger.debug(f"Images requested: {imgs_requested}")

        # Prepare prompt for final inference
        pi_dialogue = ""
        if inf_id == total_inferences - 1:
            pi_dialogue = "This is the final question. Please provide a diagnosis.\n"
            logger.debug("Final inference prompt set.")

        # Obtain doctor's dialogue
        if inf_type == "human_doctor":
            doctor_dialogue = input("\nQuestion for patient: ")
        else:
            doctor_dialogue = doctor_agent.inference_doctor(
                pi_dialogue, image_requested=imgs_requested, thread_id=inf_id
            )

        # Log and store doctor's dialogue
        dialogue_text = (
            f"Doctor [{int(((inf_id + 1) / total_inferences) * 100)}%]: {doctor_dialogue}"
        )
        logger.info(dialogue_text)
        dialogue_history.append({"speaker": "Doctor", "text": doctor_dialogue})

        # Check for diagnosis
        if "DIAGNOSIS READY" in doctor_dialogue.upper() or inf_id == total_inferences - 1:
            # Compare results
            result = compare_results(
                doctor_dialogue,
                scenario.diagnosis_information(),
                moderator_llm,
                mpipe,
            )
            is_correct = result
            result_text = f"\nCorrect answer: {scenario.diagnosis_information()}"
            accuracy = (total_correct + int(is_correct)) / total_scenarios * 100
            scene_text = (
                f"Scene {scenario_id}, The diagnosis was "
                f"{'CORRECT' if is_correct else 'INCORRECT'} "
                f"({accuracy:.2f}%)"
            )
            logger.info(result_text)
            logger.info(scene_text)
            dialogue_history.append(
                {
                    "DIAGNOSIS_READY_Answer": scenario.diagnosis_information(),
                    "DIAGNOSIS_READY_Simulation": scene_text,
                }
            )
            break

        # Handle medical exam request
        if "REQUEST TEST" in doctor_dialogue.upper():
            pi_dialogue = meas_agent.inference_measurement(doctor_dialogue)
            measurement_text = (
                f"Measurement [{int(((inf_id + 1) / total_inferences) * 100)}%]: "
                f"{pi_dialogue}"
            )
            logger.info(measurement_text)
            patient_agent.add_hist(pi_dialogue)
            dialogue_history.append({"speaker": "Measurement", "text": pi_dialogue})
        else:
            # Obtain patient's response
            if inf_type == "human_patient":
                pi_dialogue = input("\nResponse to doctor: ")
            else:
                pi_dialogue = patient_agent.inference_patient(doctor_dialogue)
            patient_text = (
                f"Patient [{int(((inf_id + 1) / total_inferences) * 100)}%]: {pi_dialogue}"
            )
            logger.info(patient_text)
            meas_agent.add_hist(pi_dialogue)
            dialogue_history.append({"speaker": "Patient", "text": pi_dialogue})

        # Prevent API timeouts
        time.sleep(1.0)

    # Save the dialogue history to a JSON file at the end of each scenario
    try:
        scenario_output_dir = os.path.join(output_dir, f"scenario_{scenario_id}")
        os.makedirs(scenario_output_dir, exist_ok=True)
        dialogue_file = os.path.join(scenario_output_dir, "dialogue_history.json")
        with open(dialogue_file, "w") as f:
            json.dump(dialogue_history, f, indent=2)
        logger.info(
            f"Dialogue history saved for scenario {scenario_id} at {dialogue_file}."
        )
    except Exception as e:
        logger.exception(f"Failed to save dialogue history for scenario {scenario_id}.")

    return is_correct


def print_summary(total_correct: int, total_scenarios: int) -> None:
    """
    Prints the summary of the simulation.
    """
    try:
        accuracy = (total_correct / total_scenarios) * 100 if total_scenarios > 0 else 0
        summary = [
            f"\nTotal Correct Diagnoses: {total_correct}",
            f"Total Scenarios Presented: {total_scenarios}",
            f"Overall Accuracy: {accuracy:.2f}%",
        ]
        for line in summary:
            print(line)
            logger.info(line)
    except Exception as e:
        logger.exception("Failed to print summary.")


def str2bool(v):
    """
    Converts a string to a boolean.

    Args:
        v (str): Input string.

    Returns:
        bool: Converted boolean value.

    Raises:
        argparse.ArgumentTypeError: If the input is not a valid boolean string.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


if __name__ == "__main__":
    import gc
    import torch

    gc.collect()
    torch.cuda.empty_cache()
    os.environ["HF_HOME"] = "/l/users/komal.kumar/datasets/.cache/huggingface/"
    parser = argparse.ArgumentParser(description="Medical Diagnosis Simulation CLI")

    # Configuration file path
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to the YAML configuration file.",
    )

    # Allow overriding specific configuration options via command-line
    parser.add_argument("--openai_api_key", type=str, help="Override OpenAI API Key.")
    parser.add_argument(
        "--replicate_api_key", type=str, help="Override Replicate API Key."
    )
    parser.add_argument(
        "--anthropic_api_key", type=str, help="Override Anthropic API Key."
    )
    parser.add_argument(
        "--inf_type",
        type=str,
        choices=["llm", "human_doctor", "human_patient"],
        help="Override inference type.",
    )
    parser.add_argument(
        "--doctor_bias",
        type=str,
        choices=[
            "None",
            "recency",
            "frequency",
            "false_consensus",
            "confirmation",
            "status_quo",
            "gender",
            "race",
            "sexual_orientation",
            "cultural",
            "education",
            "religion",
            "socioeconomic",
        ],
        help="Override doctor bias type.",
    )
    parser.add_argument(
        "--patient_bias",
        type=str,
        choices=[
            "None",
            "recency",
            "frequency",
            "false_consensus",
            "self_diagnosis",
            "gender",
            "race",
            "sexual_orientation",
            "cultural",
            "education",
            "religion",
            "socioeconomic",
        ],
        help="Override patient bias type.",
    )
    parser.add_argument("--doctor_llm", type=str, help="Override doctor LLM.")
    parser.add_argument("--patient_llm", type=str, help="Override patient LLM.")
    parser.add_argument(
        "--measurement_llm", type=str, help="Override measurement LLM."
    )
    parser.add_argument("--moderator_llm", type=str, help="Override moderator LLM.")
    parser.add_argument(
        "--agent_dataset",
        type=str,
        choices=["MedQA", "MedQA_Ext", "NEJM", "NEJM_Ext", "MIMICIV"],
        help="Override agent dataset.",
    )
    parser.add_argument(
        "--doctor_image_request",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        help="Override doctor image request.",
    )
    parser.add_argument(
        "--num_scenarios", type=int, help="Override number of scenarios to simulate."
    )
    parser.add_argument(
        "--total_inferences",
        type=int,
        help="Override number of inferences between patient and doctor.",
    )
    parser.add_argument("--output_dir", type=str, help="Override output directory.")

    args = parser.parse_args()

    # Load configuration from file
    config = load_config(args.config)

    # Override configurations with command-line arguments if provided
    if args.openai_api_key:
        config["api_keys"]["openai"] = args.openai_api_key
    if args.replicate_api_key:
        config["api_keys"]["replicate"] = args.replicate_api_key
    if args.anthropic_api_key:
        config["api_keys"]["anthropic"] = args.anthropic_api_key
    if args.inf_type:
        config["inference"]["type"] = args.inf_type
    if args.doctor_bias:
        config["biases"]["doctor"] = args.doctor_bias
    if args.patient_bias:
        config["biases"]["patient"] = args.patient_bias
    if args.doctor_llm:
        config["language_models"]["doctor"] = args.doctor_llm
    if args.patient_llm:
        config["language_models"]["patient"] = args.patient_llm
    if args.measurement_llm:
        config["language_models"]["measurement"] = args.measurement_llm
    if args.moderator_llm:
        config["language_models"]["moderator"] = args.moderator_llm
    if args.agent_dataset:
        config["scenario"]["dataset"] = args.agent_dataset
    if args.doctor_image_request is not None:
        config["scenario"]["image_request"] = args.doctor_image_request
    if args.num_scenarios is not None:
        config["scenario"]["num_scenarios"] = args.num_scenarios
    if args.total_inferences is not None:
        config["scenario"]["total_inferences"] = args.total_inferences
    if args.output_dir:
        config["output_dir"] = args.output_dir

    main(config)
