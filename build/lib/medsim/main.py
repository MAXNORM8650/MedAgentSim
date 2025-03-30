import argparse
from agent import *
from MultiAgent.AgentClinic.scenario import *
from query import *
def main(api_key, replicate_api_key, inf_type, doctor_bias, patient_bias, doctor_llm, patient_llm,
         measurement_llm, moderator_llm, num_scenarios, dataset, img_request, total_inferences,
         anthropic_api_key=None):
    openai.api_key = api_key
    anthropic_llms = ["claude3.5sonnet"]
    replicate_llms = ["llama-3-70b-instruct", "llama-2-70b-chat", "mixtral-8x7b"]
    if patient_llm in replicate_llms or doctor_llm in replicate_llms:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
    if doctor_llm in anthropic_llms:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
    output_dir = "./"
    os.makedirs(output_dir, exist_ok=True)
    # Load the appropriate scenario loader
    if dataset == "MedQA":
        scenario_loader = ScenarioLoaderMedQA()
    elif dataset == "MedQA_Ext":
        scenario_loader = ScenarioLoaderMedQAExtended()
    elif dataset == "NEJM":
        scenario_loader = ScenarioLoaderNEJM()
    elif dataset == "NEJM_Ext":
        scenario_loader = ScenarioLoaderNEJMExtended()
    elif dataset == "MIMICIV":
        scenario_loader = ScenarioLoaderMIMICIV()
    else:
        raise Exception("Dataset {} does not exist".format(str(dataset)))
    # Resolve model names from aliases
    doctor_llm = resolve_model_name(doctor_llm)
    patient_llm = resolve_model_name(patient_llm)
    measurement_llm = resolve_model_name(measurement_llm)
    moderator_llm = resolve_model_name(moderator_llm)
    total_correct = 0
    total_presents = 0

    if num_scenarios is None:
        num_scenarios = scenario_loader.num_scenarios
    
    meas_agent = MeasurementAgent(backend_str=measurement_llm)
    patient_agent = PatientAgent(backend_str=patient_llm)
    doctor_agent = DoctorAgent(backend_str=doctor_llm)
    mpipe = BAgent(moderator_llm)
    for _scenario_id in range(0, min(num_scenarios, scenario_loader.num_scenarios)):
        total_presents += 1
        pi_dialogue = ""
        dialogue_history = []
        
        # Initialize scenario and agents
        scenario = scenario_loader.get_scenario(id=_scenario_id)

        meas_agent.update_scenario(
            scenario=scenario)
        patient_agent.update_scenario(
            scenario=scenario, 
            bias_present=patient_bias)
        doctor_agent.update_scenario(
            scenario=scenario, 
            bias_present=doctor_bias,
            max_infs=total_inferences, 
            img_request=img_request)
        doctor_dialogue = ""        
        for _inf_id in range(total_inferences):
            # Determine if images are requested
            if dataset == "NEJM":
                imgs = "REQUEST IMAGES" in doctor_dialogue if img_request else True
            else:
                imgs = False

            # Check if final inference
            if _inf_id == total_inferences - 1:
                pi_dialogue += "This is the final question. Please provide a diagnosis.\n"

            # Obtain doctor's dialogue
            if inf_type == "human_doctor":
                doctor_dialogue = input("\nQuestion for patient: ")
            else:
                doctor_dialogue = doctor_agent.inference_doctor(pi_dialogue, image_requested=imgs)

            # Log and print the doctor's dialogue
            dialogue_text = f"Doctor [{int(((_inf_id+1)/total_inferences)*100)}%]: {doctor_dialogue}"
            print(dialogue_text)

            dialogue_history.append({"speaker": "Doctor", "text": doctor_dialogue})

            # Check for diagnosis
            if "DIAGNOSIS READY" in doctor_dialogue or _inf_id == total_inferences:
                correctness = compare_results(doctor_dialogue, scenario.diagnosis_information(), moderator_llm, mpipe) == "yes"
                if correctness:
                    total_correct += 1
                result_text = f"\nCorrect answer: {scenario.diagnosis_information()}"
                scene_text = f"Scene {_scenario_id}, The diagnosis was {'CORRECT' if correctness else 'INCORRECT'} ({int((total_correct/total_presents)*100)}%)"
                print(result_text)
                print(scene_text)
                # Add this scenario's conversation to the master log
                dialogue_history.append(
                    {
                        "DIAGNOSIS_READY_Answer": scenario.diagnosis_information(),
                        "DIAGNOSIS_READY_Simulation": f"Scene {_scenario_id}, The diagnosis was "
                        f"{'CORRECT' if correctness else 'INCORRECT'}, "
                        f"{int((total_correct / total_presents) * 100)}%",
                    }
                )
                break

            # Handle medical exam request
            if "REQUEST TEST" in doctor_dialogue:
                pi_dialogue = meas_agent.inference_measurement(doctor_dialogue)
                measurement_text = f"Measurement [{int(((_inf_id+1)/total_inferences)*100)}%]: {pi_dialogue}"
                print(measurement_text)
                patient_agent.add_hist(pi_dialogue)
                dialogue_history.append(
                    {"speaker": "Measurement", "text": pi_dialogue}
                )
            else:
                # Obtain patient's response
                if inf_type == "human_patient":
                    pi_dialogue = input("\nResponse to doctor: ")
                else:
                    pi_dialogue = patient_agent.inference_patient(doctor_dialogue)
                patient_text = f"Patient [{int(((_inf_id+1)/total_inferences)*100)}%]: {pi_dialogue}"
                print(patient_text)
                meas_agent.add_hist(pi_dialogue)
                dialogue_history.append({"speaker": "Patient", "text": pi_dialogue})
            # Prevent API timeouts
            time.sleep(1.0)
        
        # Save the dialogue history to a JSON file at the end of each scenario
        scenario_output_dir = os.path.join(output_dir, f"scenario_{_scenario_id}")
        os.makedirs(scenario_output_dir, exist_ok=True)
        dialogue_file = os.path.join(scenario_output_dir, "dialogue_history.json")
        with open(dialogue_file, "w") as f:
            json.dump(dialogue_history, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Medical Diagnosis Simulation CLI')
    parser.add_argument('--openai_api_key', type=str, required=False, help='OpenAI API Key')
    parser.add_argument('--replicate_api_key', type=str, required=False, help='Replicate API Key')
    parser.add_argument('--inf_type', type=str, choices=['llm', 'human_doctor', 'human_patient'], default='llm')
    parser.add_argument('--doctor_bias', type=str, help='Doctor bias type', default='None', choices=["recency", "frequency", "false_consensus", "confirmation", "status_quo", "gender", "race", "sexual_orientation", "cultural", "education", "religion", "socioeconomic"])
    parser.add_argument('--patient_bias', type=str, help='Patient bias type', default='None', choices=["recency", "frequency", "false_consensus", "self_diagnosis", "gender", "race", "sexual_orientation", "cultural", "education", "religion", "socioeconomic"])
    parser.add_argument('--doctor_llm', type=str, default='llama3b')
    parser.add_argument('--patient_llm', type=str, default='llama3b')
    parser.add_argument('--measurement_llm', type=str, default='llama3b')
    parser.add_argument('--moderator_llm', type=str, default='llama3b')
    parser.add_argument('--agent_dataset', type=str, default='MedQA') # MedQA, MIMICIV or NEJM
    parser.add_argument('--doctor_image_request', type=bool, default=False) # whether images must be requested or are provided
    parser.add_argument('--num_scenarios', type=int, default=None, required=False, help='Number of scenarios to simulate')
    parser.add_argument('--total_inferences', type=int, default=20, required=False, help='Number of inferences between patient and doctor')
    parser.add_argument('--anthropic_api_key', type=str, default=None, required=False, help='Anthropic API key for Claude 3.5 Sonnet')
    
    args = parser.parse_args()

    main(args.openai_api_key, args.replicate_api_key, args.inf_type, args.doctor_bias, args.patient_bias, args.doctor_llm, args.patient_llm, args.measurement_llm, args.moderator_llm, args.num_scenarios, args.agent_dataset, args.doctor_image_request, args.total_inferences, args.anthropic_api_key)