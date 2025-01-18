import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import json
import os
import time

import time
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

# from Lcgent import LBAgent


class BAgent:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        # Load the model and tokenizer once during initialization
        print("Loading model and tokenizer...")

        # Configure quantization for low-bit precision
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,  # Use 4-bit precision (set to False for 8-bit)
            bnb_4bit_use_double_quant=True,  # Use double quantization
            bnb_4bit_quant_type="nf4",  # Quantization type (nf4 is generally better)
            bnb_4bit_compute_dtype=torch.float16  # Compute dtype (float16 or float32)
        )

        # Initialize the pipeline
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=model_name,
            torch_dtype = 'auto',
            # quantization_config=bnb_config, 
            # offload_buffers=True,
            # model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
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
        if self.infs >= self.MAX_INFS: return "Maximum inferences reached"
        answer = self.pipe.query_model("\nHere is a history of your dialogue: " + self.agent_hist + "\n Here was the patient response: " + question + "Now please continue your dialogue\nDoctor: ", self.system_prompt(), image_requested=image_requested, scene=self.scenario, thread_id = thread_id)
        self.agent_hist += question + "\n\n" + answer + "\n\n"
        self.infs += 1
        return answer

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

def compare_results(diagnosis, correct_diagnosis, moderator_llm, mod_pipe, tries=3, timeout=5.0):
    """
    Compares the doctor's diagnosis with the correct diagnosis using a moderator model.

    Args:
        diagnosis (str): The diagnosis provided by the doctor.
        correct_diagnosis (str): The correct diagnosis for the case.
        mod_pipe (BAgent): The initialized QAssistant instance for the moderator.
        tries (int): Number of retry attempts for querying the model. Defaults to 3.
        timeout (float): Time in seconds between retries. Defaults to 5.0.

    Returns:
        bool: True if the diagnoses match (Yes), False otherwise (No).
    """
    # Prepare the prompt for comparison
    prompt = (
        f"Here is the correct diagnosis: {correct_diagnosis}\n"
        f"Here was the doctor dialogue and diagnosis: {diagnosis}\n"
        f"Are these the same? Please respond only with Yes or No."
    )

    # Define the system prompt for the moderator
    system_prompt = (
        "You are a medical moderator responsible for determining if the doctor's diagnosis matches the correct "
        "diagnosis. Please respond with either 'Yes' or 'No'. Do not provide any explanation or additional content."
    )

    # Query the moderator model
    for attempt in range(tries):
        try:
            # Use the mod_pipe's query_model to get the response
            response = mod_pipe.query_model(
                prompt=prompt,
                system_prompt=system_prompt,
                tries=1,  # Single attempt per loop iteration
                timeout=timeout
            )

            # Process the response and return a boolean result
            return response.strip().lower() == "yes"

        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(timeout)

    # Raise an exception if all retries fail
    raise Exception("Failed to compare results after multiple attempts.")
