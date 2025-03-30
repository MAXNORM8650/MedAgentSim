import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import json
import os
import random
import re
import sys
import gzip
from collections import Counter
from importlib import import_module

import time
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

# from Lcgent import LBAgent


class BAgent:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct", loaded=True):
        """
        Initialize the BAgent class. Load the model and tokenizer if a model name is provided.
        If a Hugging Face pipeline is passed, use it directly.
        """
        print("Initializing BAgent...")
        if loaded:
            # Use the provided pipeline directlyzssss
            self.pipeline = model_name.pipeline
            print("Using the provided Hugging Face pipeline.")
        else:
            # Load the model and tokenizer if a model name is provided
            print("Loading model and tokenizer...")

            # Configure quantization for low-bit precision
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,  # Use 4-bit precision (set to False for 8-bit)
                llm_int8_enable_fp32_cpu_offload=True
                # bnb_4bit_use_double_quant=True,  # Use double quantization
                # bnb_4bit_quant_type="nf4",  # Quantization type (nf4 is generally better)
                # bnb_4bit_compute_dtype=torch.float16  # Compute dtype (float16 or float32)
            )

            # Load the model with quantization
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",  # Automatically map to GPU if available
            )

            # Load the tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            # Initialize the pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device_map="auto",  # Ensure the device map is passed correctly
            )

            print("Model and tokenizer loaded successfully.")
    
    def query_model(
        self,
        prompt,
        system_prompt,
        tries=3,
        timeout=5.0,
        image_requested=False,
        scene=None,
        max_prompt_len=2**14,
        clip_prompt=False,
        thread_id = 1
    ):
        for attempt in range(tries):
            if clip_prompt:
                prompt = prompt[:max_prompt_len]
            try:
                if image_requested:
                    if scene is None or not hasattr(scene, 'image_url'):
                        raise ValueError("Image requested but no scene or image_url provided.")
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": scene.image_url}},
                        ]},
                    ]
                else:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ]
                
                # Use the pipeline to generate the response
                outputs = self.pipeline(
                    messages,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                answer = outputs[0]['generated_text'][-1]['content']
                # response = re.sub(r"\s+", " ", answer).strip()
                return answer
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(timeout)
                continue
        raise Exception("Max retries exceeded: unable to generate response.")
    
    def import_generate():
        # Get the absolute path of the current script (agent.py)
        current_file = os.path.abspath(__file__)

        # Find the root directory (Medical_Project) dynamically
        root_dir = os.path.dirname(os.path.dirname(current_file))  # Move up two levels

        # Construct the path to MedPromptSimulate/src
        src_path = os.path.join(root_dir, "MedPromptSimulate", "src")

        # Add src to sys.path if not already present
        if src_path not in sys.path:
            sys.path.append(src_path)

        # Import generate.py as part of the package structure
        module = import_module("promptbase.mmlu.generate")

        # Return the function generate_single from the module
        return module.generate_single
    
    def get_result_json():
        """
        Extracts and reads the JSON data from result.json.gz, then deletes the file.
        """
        # Get the absolute path of the current script (agent.py)
        current_file = os.path.abspath(__file__)

        # Find the root directory (Medical_Project) dynamically
        root_dir = os.path.dirname(os.path.dirname(current_file))  # Move up two levels

        # Construct the path to the result.json.gz file
        json_gz_path = os.path.join(root_dir, "MedPromptSimulate", "src", "promptbase", "generations", "expt", "train", "cot", "result.json.gz")

        # Ensure the file exists
        if not os.path.exists(json_gz_path):
            raise FileNotFoundError(f"File not found: {json_gz_path}")

        with gzip.open(json_gz_path, "rt", encoding="utf-8") as gz_file:
            json_data = json.load(gz_file)  # Read JSON content

        return json_data
    
    def get_diagnosis(self):
        generate_single = self.import_generate() # mmlu
        generate_single("temp_question.json")

        # Usage Example
        result_json = self.get_result_json()
        lst = [result_json[0]["expt"][key]["answer"] for key in result_json[0]["expt"]]

        counter = Counter(lst)
        most_common = counter.most_common(1)[0][0]  # Get the most common element

        dia = result_json[0]["answer_choices"][most_common]

        return dia
    
    def extract_bracket_content(s: str):
        if "[" in s and "]" in s:
            return "[" + s.split("[", 1)[-1].split("]")[0] + "]"
        return s  # Return original string if brackets are not found

    def clean_diagnosis(self, message):
        message = self.extract_bracket_content(message)
        
        message = message.replace("```python", "")
        message = message.replace("```", "")
        message = message.replace("\n", "")
        message = message.replace(", ", ",")
        formatted_str = message.strip()
        formatted_str = formatted_str.replace('[', '["')
        formatted_str = formatted_str.replace(']', '"]')
        formatted_str = formatted_str.replace(',', '", "')
        
        diagnosis_list = eval(formatted_str)
        diagnosis_list = [dia.strip() for dia in diagnosis_list]
        return diagnosis_list

    def generate_possible_diagnoses(self, question: str, answer: str):
        """
        Generates a Python list of 3 possible diagnoses based on the question while ensuring:
        - The generated diagnoses match the format of the correct diagnosis.
        - The correct diagnosis is excluded.
        - The diagnoses are unique.
        
        Parameters:
            question (str): The medical question.
            answer (str): The correct diagnosis.

        Returns:
            list: A list of 3 possible diagnoses.
        """
        prompt = (
            f"Given the following medical question, suggest three possible diagnoses in a format similar to the correct diagnosis. "
            f"Ensure that the diagnoses are unique, medically plausible, and formatted in a way that makes them indistinguishable from the correct answer. Do NOT suggest the correct diagnosis.\n\n"
            f"Question: {question}\n"
            f"Correct Diagnosis: {answer}\n\n"
            f"Provide the diagnoses in a Python list format."
        )   

        system_prompt = "You are a highly knowledgeable and precise AI assistant specializing in medical reasoning. Your role is to analyze clinical scenarios and provide accurate, evidence-based differential diagnoses. You will assess the details of each case carefully and generate insightful responses that adhere to medical best practices."
        response = self.generate_response(system_prompt, prompt)
        
        # Extract the response as a list
        diagnoses = self.clean_diagnosis(response)  # Assuming response is in list format
        
        return diagnoses

    def generate_answer_choices(correct_answer, answer_list):
        letter_answers = ['A', 'B', 'C', 'D']
        answer_list.append(correct_answer)
        random.shuffle(answer_list)  # Shuffle the list
        result = dict(zip(letter_answers, answer_list))  # Map keys to shuffled conditions
        answer_letter = letter_answers[answer_list.index(correct_answer)]
        return result, answer_letter

    def generate_question_json(question: str, answer_choices: dict, correct_answer: str, filename: str = "temp_question.json"):
        """
        Generates and saves a JSON file with a question, answer choices, and the correct answer.
        
        Parameters:
            question (str): The question text.
            answer_choices (dict): Dictionary of answer choices, e.g., {"A": "Answer1", "B": "Answer2"}.
            correct_answer (str): The correct answer key (e.g., "A").
            filename (str): The filename to save the JSON data. Default is "question.json".
        """
        data = [
            {
                "id": 1,
                "question": question,
                "answer_choices": answer_choices,
                "correct_answer": correct_answer
            }
        ]

        # Get the absolute path of the current script (agent.py or test script in TOQ folder)
        current_file = os.path.abspath(__file__)

        # Find the root directory (Medical_Project) dynamically
        root_dir = os.path.dirname(os.path.dirname(current_file))  # Move up two levels

        # Construct the destination folder path
        save_folder = os.path.join(root_dir, "MedPromptSimulate", "src", "promptbase", "datasets", "mmlu", "train")

        # Construct the full file path
        save_path = os.path.join(save_folder, filename)
        
        # Save to JSON file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def extract_question(self, patient_statement, agent_hist, parsed_responses):
        # Prompt for the model
        prompt = (
            f"Given the following patient statement, additional context, and doctor discussion, "
            f"generate a structured diagnostic question that extracts key insights and relevant test results:\n\n"
            f"Patient Statement:\n{patient_statement}\n\n"
            f"Additional Context:\n{agent_hist}\n\n"
            f"Doctor Discussion:\n{parsed_responses}\n\n"
            f"Ensure the question is formatted in the following structured manner using as much information from the provided context above:\n"
            f"Provide the most likely final diagnosis for the following patient. A ___ year old [man/woman] "
            f"presents with [duration] of [symptom description], associated with [other symptoms]. "
            f"The symptoms worsened with [trigger], improved with [relief], but recurred. "
            f"Laboratory results show [lab findings]. Imaging revealed [imaging findings]. "
            f"What is the final diagnosis for this patient?"
        )

        system_prompt = "You are a highly knowledgeable and precise AI assistant specializing in medical reasoning. Your role is to analyze clinical scenarios and provide accurate, evidence-based differential diagnoses. You will assess the details of each case carefully and generate insightful responses that adhere to medical best practices."

        response = self.generate_response(system_prompt, prompt) # maybe do some cleaning too

        return response

    def query_model_with_ensembling(
        self,
        prompt,
        system_prompt,
        tries=3,
        timeout=5.0,
        image_requested=False,
        scene=None,
        max_prompt_len=2**14,
        clip_prompt=False,
        thread_id=1,
        shuffle_ensemble_count=3  # Number of ensembles to create using choice shuffling
    ):
        for attempt in range(tries):
            if clip_prompt:
                prompt = prompt[:max_prompt_len]
            try:
                responses = []

                # Generate multiple responses using shuffled prompts
                for _ in range(shuffle_ensemble_count):
                    shuffled_prompt = self.shuffle_choices_in_prompt(prompt)
                    messages = self.build_messages(system_prompt, shuffled_prompt, image_requested, scene)

                    # Use the pipeline to generate the response
                    outputs = self.pipeline(
                        messages,
                        max_new_tokens=200,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9
                    )
                    responses.append(outputs[0]['generated_text'][-1]['content'])

                # Aggregate responses (e.g., majority vote, longest consistent response, etc.)
                final_response = self.aggregate_responses(responses)
                return final_response

            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(timeout)
                continue
        raise Exception("Max retries exceeded: unable to generate response.")

    def shuffle_choices_in_prompt(self, prompt):
        # This function identifies choices (e.g., multiple-choice options) and shuffles them
        choices_pattern = r"\((a|b|c|d)\)\s+[^\n]+"
        choices = re.findall(choices_pattern, prompt)
        if choices:
            random.shuffle(choices)
            shuffled_prompt = re.sub(choices_pattern, lambda match: choices.pop(0), prompt, count=len(choices))
            return shuffled_prompt
        return prompt

    def build_messages(self, system_prompt, prompt, image_requested, scene):
        if image_requested:
            if scene is None or not hasattr(scene, 'image_url'):
                raise ValueError("Image requested but no scene or image_url provided.")
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": scene.image_url}},
                ]},
            ]
        else:
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

    def aggregate_responses(self, responses):
        # Aggregate responses (e.g., by selecting the most common one)
        response_counts = {response: responses.count(response) for response in responses}
        return max(response_counts, key=response_counts.get)

    def generate_response(self, system_prompt, user_prompt):
        return self.query_model(
            prompt=user_prompt,
            system_prompt=system_prompt,
            tries=3,
            timeout=5.0,
            image_requested=False
        )

class PatientAgent:
    def __init__(self, backend_str="Qwen/Qwen2.5-0.5B-Instruct") -> None:
        # language model backend for patient agent
        self.backend = backend_str
        self.pipe = BAgent(model_name=backend_str)

    def update_scenario(self, scenario, bias_present=None):
        # disease of patient, or "correct answer"
        self.disease = ""
        # symptoms that patient presents
        self.symptoms = ""
        # conversation history between doctor and patient
        self.agent_hist = ""
        # presentation of any form of bias
        self.bias_present = (None if bias_present == "None" else bias_present)
        # sample initial question from dataset
        self.scenario = scenario        
        self.reset()
        self.biases = ["recency", "frequency", "false_consensus", "self_diagnosis", "gender", "race", "sexual_orientation", "cultural", "education", "religion", "socioeconomic"]
    def generate_bias(self) -> str:
        """ 
        ================
        Cognitive biases 
        ================
        """
        if self.bias_present == "recency":
            return "\nRecently, you had a friend with similar symptoms to yours that was diagnosed with cancer. This affects how you interact with the doctor.\n"
        elif self.bias_present == "frequency":
            return "\nYou recently learned that most frequently, doctors diagnose this as cancer based on past cases. This affects how you interact with the doctor.\n"
        elif self.bias_present == "false_consensus":
            return "\nMost of your friends who heard about your symptoms believe that you have cancer. This affects how you interact with the doctor.\n"
        elif self.bias_present == "self_diagnosis":
            return "\nYou recently performed a thorough investigation of your symptoms online and have come to the conclusion that you should be diagnosed with cancer. While the doctor may believe otherwise you remain convinced you have cancer. This affects how you interact with the doctor.\n"
        elif self.bias_present == "gender":
            return "\nYou are uncomfortable with your doctor because you find out that they are a particular gender and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "race":
            return "\nYou are uncomfortable with your doctor because you find out that they are a particular race and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "sexual_orientation":
            return "\nYou are uncomfortable with your doctor because you find out that they are a particular sexual orientation and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "cultural":
            return "\nYou are uncomfortable with your doctor because you find out that they are from a particular culture and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "education":
            return "\nYou are uncomfortable with your doctor because you find out that they went to a low ranked medical school and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "religion":
            return "\nYou are uncomfortable with your doctor because you find out that they believe in a particular religion and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "socioeconomic":
            return "\nYou are uncomfortable with your doctor because you find out that they are from a particular socioeconomic background and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present is None:
            pass
        else:
            print("BIAS TYPE {} NOT SUPPORTED, ignoring bias...".format(self.bias_present))
        return ""

    def inference_patient(self, question) -> str:
        answer = self.pipe.query_model("\nHere is a history of your dialogue: " + self.agent_hist + "\n Here was the doctor response: " + question + "Now please continue your dialogue\nPatient: ", self.system_prompt())
        self.agent_hist += question + "\n\n" + answer + "\n\n"
        return answer
    def system_prompt(self) -> str:
        bias_prompt = ""
        if self.bias_present is not None:
            bias_prompt = self.generate_bias()
        base = """You are a patient in a clinic who only responds in the form of dialogue. You are being inspected by a doctor who will ask you questions and will perform exams on you in order to understand your disease. Your answer will only be 1-3 sentences in length."""
        symptoms = "\n\nBelow is all of your information. {}. \n\n Remember, you must not reveal your disease explicitly but may only convey the symptoms you have in the form of dialogue if you are asked.".format(self.symptoms)
        return base + bias_prompt + symptoms
    
    def reset(self) -> None:
        self.agent_hist = ""
        self.symptoms = self.scenario.patient_information()
    def add_hist(self, hist_str) -> None:
        self.agent_hist += hist_str + "\n\n"


class DoctorAgent:
    def __init__(self, backend_str="gpt4", graph=False) -> None:
        self.backend = backend_str
        # if graph:
        #     self.pipe = LBAgent(model_name=backend_str)
        # else:
        self.pipe = BAgent(model_name=backend_str)
        self.num_doctors = 5
    def update_scenario(self, scenario, max_infs=20, bias_present=None, img_request=False):
        # number of inference calls to the doctor
        self.infs = 0
        # maximum number of inference calls to the doctor
        self.MAX_INFS = max_infs
        # conversation history between doctor and patient
        self.agent_hist = ""
        # presentation information for doctor
        self.presentation = ""
        # language model backend for doctor agent

        # presentation of any form of bias
        self.bias_present = (None if bias_present == "None" else bias_present)
        # prepare initial conditions for LLM
        self.scenario = scenario
        self.reset()      
        self.img_request = img_request
        self.biases = ["recency", "frequency", "false_consensus", "confirmation", "status_quo", "gender", "race", "sexual_orientation", "cultural", "education", "religion", "socioeconomic"]

    def generate_bias(self) -> str:
        """ 
        ================
        Cognitive biases 
        ================
        """
        if self.bias_present == "recency":
            return "\nRecently, you learned that a doctor with similar symptoms to the patient that diagnosed their patient with cancer. This affects how you interact with the patient.\n"
        elif self.bias_present == "frequency":
            return "\nYou recently learned that most frequently, doctors diagnose patients with similar symptoms with cancer based on past cases. This affects how you interact with the patient.\n"
        elif self.bias_present == "false_consensus":
            return "\nMost of your colleagues who heard about the patient's symptoms believe that they have cancer. This affects how you interact with the patient.\n"
        elif self.bias_present == "status_quo":
            return "\nYour hosptial has been diagnosing these patient's symptoms with cancer for the past 10 years. This affects how you interact with the patient.\n"
        elif self.bias_present == "confirmation":
            return "\nYou are initially confident that the patient has cancer. This affects how you interact with the patient.\n"
        elif self.bias_present == "gender":
            return "\nYou are uncomfortable with your patient because you find out that they are a particular gender and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "race":
            return "\nYou are uncomfortable with your patient because you find out that they are a particular race and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "sexual_orientation":
            return "\nYou are uncomfortable with your patient because you find out that they are a particular sexual orientation and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "cultural":
            return "\nYou are uncomfortable with your patient because you find out that they are from a particular culture and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "education":
            return "\nYou are uncomfortable with your patient because you find out that they are uneducated and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "religion":
            return "\nYou are uncomfortable with your patient because you find out that they believe in a particular religion and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present == "socioeconomic":
            return "\nYou are uncomfortable with your patient because you find out that they are from a particular socioeconomic background and you do not trust their judgement. This affects how you interact with them.\n"
        elif self.bias_present is None:
            pass
        else:
            print("BIAS TYPE {} NOT SUPPORTED, ignoring bias...".format(self.bias_present))
        return ""
    


    def inference_doctor(self, question, image_requested=False, thread_id = 1) -> str:
        answer = str()
        if self.infs >= self.MAX_INFS-1:
            return self.internal_discussion(question)
        answer = self.pipe.query_model("\nHere is a history of your dialogue: " + self.agent_hist + "\n Here was the patient response: " + question + "Now please continue your dialogue\nDoctor: ", self.system_prompt(), image_requested=image_requested, scene=self.scenario, thread_id = thread_id)
        self.agent_hist += question + "\n\n" + answer + "\n\nq[[[]"
        self.infs += 1
        return answer
    def col_system_prompt(self):
        return (
            "You are a team of collaborative doctors engaged in a discussion about a patient's case. Each doctor is expected to provide their professional opinion "
            "based on the presented symptoms and test results. The objective is to work together to reach a consensus diagnosis. "
            "Each response should be formatted as 'Doctor X: [response]'. Once the discussion concludes, the group will collectively decide on the diagnosis, "
            "summarized as 'DIAGNOSIS READY: [final diagnosis based on majority vote]'."
        )

    def internal_discussion(self, patient_statement, image_requested = None, thread_id=1)->str:
        """
        Simulates an internal multi-doctor discussion to refine diagnosis.

        Args:
            patient_statement (str): The patient's latest statement or response.
            context (str): Additional context (e.g., test results or history).

        Returns:
            str: The final diagnosis after internal discussion.
        """
        discussion_prompt = (
            f"Patient Statement: {patient_statement}\n"
            f"Additional Context: {self.agent_hist}\n"
            f"Doctors, please discuss this case and refine your opinions based on the symptoms and test results. "
        )
        responses = []

        for i in range(1, self.num_doctors + 1):
            # breakpoint()
            prompt = (f"{discussion_prompt} Doctor {i}, please share your opinion on the diagnosis and reasoning.\n")
            response = self.pipe.query_model(prompt, self.col_system_prompt(), image_requested=image_requested, scene=self.scenario, thread_id = thread_id)
            responses.append(f"Doctor {i}: {response.strip()}")

        question = self.extract_question(patient_statement, self.agent_hist, "\n".join(responses))
        answer = self.scenario.diagnosis_information()
        answer_list = self.generate_possible_diagnoses(question, answer)
        answer_choices, correct_answer = self.generate_answer_choices(answer, answer_list)
        self.generate_question_json(question, answer_choices, correct_answer)

        generate_single = self.import_generate() # mmlu
        generate_single('temp_question.json')

        # generate prediction from mmlu
        diagnosis_pred = self.get_diagnosis()

        # Final consensus based on discussion
        consensus_prompt = (f"The following discussion occurred among doctors:\n\n" + "\n".join(responses) + f"\n\nAnd you have come to the conclusion that the correct diagnosis is: {diagnosis_pred}" + "\n\nBased on this discussion and findings, provide a Final Diagnosis.")

        final_response = self.pipe.query_model(consensus_prompt, self.col_system_prompt(), image_requested=None, scene=self.scenario, thread_id = thread_id)
        self.agent_hist += "\n".join(responses) + f"\nFinal Diagnosis: {final_response.strip()}\n"

        return final_response.strip()

    def system_prompt(self) -> str:
        bias_prompt = ""
        if self.bias_present is not None:
            bias_prompt = self.generate_bias()
        base = "You are a doctor named Dr. Agent who only responds in the form of dialogue. You are inspecting a patient who you will ask questions in order to understand their disease. You are only allowed to ask {} questions total before you must make a decision. You have asked {} questions so far. You can request test results using the format \"REQUEST TEST: [test]\". For example, \"REQUEST TEST: Chest_X-Ray\". Your dialogue will only be 1-3 sentences in length. Once you have decided to make a diagnosis please type \"DIAGNOSIS READY: [diagnosis here]\"".format(self.MAX_INFS, self.infs) + ("You may also request medical images related to the disease to be returned with \"REQUEST IMAGES\"." if self.img_request else "")
        presentation = "\n\nBelow is all of the information you have. {}. \n\n Remember, you must discover their disease by asking them questions. You are also able to provide exams.".format(self.presentation)
        return base + bias_prompt + presentation

    def reset(self) -> None:
        self.agent_hist = ""
        self.presentation = self.scenario.examiner_information()


class MeasurementAgent:
    def __init__(self, backend_str="gpt4") -> None:
        # language model backend for measurement agent
        self.backend = backend_str
        self.pipe = BAgent(model_name=backend_str)

    def update_scenario(self, scenario):
        self.agent_hist = ""
        # presentation information for measurement 
        self.presentation = ""
        # prepare initial conditions for LLM
        self.scenario = scenario
        self.reset()
    def inference_measurement(self, question) -> str:
        answer = str()
        answer = self.pipe.query_model("\nHere is a history of the dialogue: " + self.agent_hist + "\n Here was the doctor measurement request: " + question, self.system_prompt())
        self.agent_hist += question + "\n\n" + answer + "\n\n"
        return answer

    def system_prompt(self) -> str:
        base = "You are an measurement reader who responds with medical test results. Please respond in the format \"RESULTS: [results here]\""
        presentation = "\n\nBelow is all of the information you have. {}. \n\n If the requested results are not in your data then you can respond with NORMAL READINGS.".format(self.information)
        return base + presentation
    
    def add_hist(self, hist_str) -> None:
        self.agent_hist += hist_str + "\n\n"

    def reset(self) -> None:
        self.agent_hist = ""
        self.information = self.scenario.exam_information()


def compare_results(diagnosis, correct_diagnosis, mod_pipe, similarity_threshold=0.8, tries=3, timeout=5.0):
    """
    Compares the doctor's diagnosis with the correct diagnosis using a similarity-based approach.

    Args:
        diagnosis (str): The diagnosis provided by the doctor.
        correct_diagnosis (str): The correct diagnosis for the case.
        mod_pipe (BAgent): The initialized moderator instance.
        similarity_threshold (float): Threshold for similarity to decide "Yes". Defaults to 0.8.
        tries (int): Number of retry attempts. Defaults to 3.
        timeout (float): Time in seconds between retries. Defaults to 5.0.

    Returns:
        tuple: (decision (str), similarity (float))
    """
    prompt = (
        f"Here is the correct diagnosis: {correct_diagnosis}\n"
        f"Here was the doctor's diagnosis: {diagnosis}\n"
        f"Rate the similarity between the two diagnoses on a scale of 0 to 1, where 0 means completely dissimilar and 1 means identical. "
        f"Based on the similarity score, decide whether they match. Respond strictly in the format:\n"
        f"[0.XX]\n"
        f"Do not include any additional text or explanation."
    )
    system_prompt = (
        "You are a medical moderator responsible for assessing similarity between two diagnoses. "
        "Respond strictly in the format [0.XX] where 0.XX is similarity. Do not include any extra text."
    )
    # breakpoint()
    for attempt in range(tries):
        try:
            # Query the model
            response = mod_pipe.query_model(prompt=prompt, system_prompt=system_prompt, tries=1, timeout=timeout)
            print(f"Attempt {attempt + 1} response: {response}")

            # Extract response
            if response.startswith("[") and response.endswith("]"):
                similarity_str = response[1:-1]  # Remove square brackets
                # similarity_str, decision_str = response_content.split(",")
                
                # Parse similarity and decision
                similarity = float(similarity_str)
                # decision = decision_str.split(":")[1].strip().lower()

                # Validate response
                if 0 <= similarity <= 1:
                    return similarity>=similarity_threshold
                else:
                    print(f"Invalid similarity score: {similarity}")

            else:
                print(f"Response not in expected format: {response}")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")

        # Wait before retrying
        time.sleep(timeout)

    raise Exception("Failed to compare results after multiple attempts.")
