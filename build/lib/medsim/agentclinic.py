import argparse
import anthropic
import torch
from transformers import pipeline
import openai, re, random, time, json, replicate, os
from accelerate import init_empty_weights, infer_auto_device_map
from accelerate import init_empty_weights, infer_auto_device_map
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import requests
import torch
from transformers import MllamaForConditionalGeneration, AutoProcessor
import requests
import torch
from langgraph.checkpoint.memory import MemorySaver
from PIL import Image

llama2_url = "meta/llama-2-70b-chat"
llama2_url_hf = "meta-llama/Llama-2-70b-chat-hf"
llama3_url = "meta-llama/Meta-Llama-3-70B-Instruct"#"meta/meta-llama-3-70b-instruct"
mixtral_url = "mistralai/mixtral-8x7b-instruct-v0.1"
llama_11B = "meta-llama/Llama-3.2-11B-Vision-Instruct"
llama3B = "meta-llama/Llama-3.2-3B-Instruct"
llama3_7B = "meta-llama/Meta-Llama-3-8B-Instruct"
med = "AdaptLLM/medicine-LLM"
med_chat = "AdaptLLM/medicine-chat"
llama3_1_8 = "meta-llama/Llama-3.1-8B-Instruct"


ANTHROPIC_LLMS = ["claude3.5sonnet"]
REPLICATE_LLMS = [
    "llama-3-70b-instruct",
    "llama-2-70b-chat",
    "HF_mistralai/mixtral-8x7b",
]
def check_gpu_memory():
    num_gpus = torch.cuda.device_count()
    for i in range(num_gpus):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        memory_stats = torch.cuda.memory_stats(i)
        total_memory = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)  # Convert to GB
        reserved_memory = memory_stats['reserved_bytes.all.current'] / (1024 ** 3)  # Convert to GB
        allocated_memory = memory_stats['allocated_bytes.all.current'] / (1024 ** 3)  # Convert to GB
        free_memory = total_memory - reserved_memory
        print(f"  Total Memory: {total_memory:.2f} GB")
        print(f"  Reserved Memory: {reserved_memory:.2f} GB")
        print(f"  Allocated Memory: {allocated_memory:.2f} GB")
        print(f"  Free Memory: {free_memory:.2f} GB\n")

# Call the function to check GPU memory
check_gpu_memory()
def load_huggingface_model(model_name, st = "", device = 'auto', load_in_8bit = False):
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from transformers import AutoTokenizer, AutoModelForCausalLM, MllamaForConditionalGeneration, pipeline
    cache_dir = os.getenv("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))
    print(f"Hugging Face cache directory: {cache_dir}")
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    if st == "vision":
        model = MllamaForConditionalGeneration.from_pretrained(model_name, device_map='auto', torch_dtype="auto")
        processor = AutoProcessor.from_pretrained(model_name)
        pipe = (model, processor)
        return pipe
    elif st == "llama":
        pass
    elif st == "AdaptLLM":
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map='auto', torch_dtype="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        pipe = (model, tokenizer)
        return pipe
    else:
        pipe = pipeline(
            "text-generation",
            model=model_name,
            torch_dtype="auto",
            device_map="auto",
            use_fast=False,
        )    
        return pipe
from huggingface_hub import InferenceClient
def inference_huggingface(system_prompt, prompt, pipe, style = ''):
    if pipe is None:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
        client = InferenceClient(style)
        client.chat_completion(messages, max_tokens=100)

    elif style == 'AdaptLLM':
        prompt = f"<s>[INST] <<SYS>>{system_prompt}<</SYS>>\n\n{prompt} [/INST]"
        model, tokenizer = pipe
        # Generate text using the model pipeline
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
        outputs = model.generate(input_ids=inputs, max_new_tokens=256)[0]
        answer_start = int(inputs.shape[-1])
        response = tokenizer.decode(outputs[answer_start:], skip_special_tokens=True)
        response = re.sub(r"\s+", " ", response).strip()
    else: 
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
        terminators = [
            pipe.tokenizer.eos_token_id,
            pipe.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        output = pipe(messages, max_new_tokens=256, eos_token_id=terminators, do_sample=True, temperature=0.6, top_p=0.9,)
        answer = output[0]['generated_text'][-1]['content']
        response = re.sub(r"\s+", " ", answer).strip()
    return response

def _inference_huggingface(messages, url, pipe):
    model, processor = pipe
    image = Image.open(requests.get(url, stream=True).raw)
    input_text = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )
    # breakpoint()
    inputs = processor(image, input_text, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=256)
    response = processor.decode(output[0][inputs["input_ids"].shape[-1]:])

    return response

def query_model(model_str, prompt, system_prompt, tries=5, timeout=30.0, image_requested=False, scene=None, max_prompt_len=2**14, clip_prompt=False, pipe = None):
    # model_str = model_str.replace("HF_", "") if "HF_" in model_str else model_str
    # if model_str not in ["gpt4", "gpt3.5", "gpt4o", 'llama-2-70b-chat', 'Mixtral-8x7B-v0.1', "mixtral-8x7b", "gpt-4o-mini", "llama-3-70b-instruct", "gpt4v", "claude3.5sonnet", "o1-preview"] and "_HF" not in model_str:
    #     raise Exception("No model by the name {}".format(model_str))

    # image_requested=False
    # print(image_requested)
    # breakpoint()
    for _ in tqdm(range(tries), desc="Processing Tries"):

        if clip_prompt: prompt = prompt[:max_prompt_len]
        try:
            
            if image_requested:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url",
                            "image_url": {
                                "url": "{}".format(scene.image_url),
                            },
                        },
                    ]},]
                if model_str == "gpt4v":
                    response = openai.ChatCompletion.create(
                            model="gpt-4-vision-preview",
                            messages=messages,
                            temperature=0.05,
                            max_tokens=200,
                        )
                elif model_str == "gpt-4o-mini":
                    response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            temperature=0.05,
                            max_tokens=200,
                        )
                elif model_str == "gpt4":
                    response = openai.ChatCompletion.create(
                            model="gpt-4-turbo",
                            messages=messages,
                            temperature=0.05,
                            max_tokens=200,
                        )
                elif model_str == "gpt4o":
                    response = openai.ChatCompletion.create(
                            model="gpt-4o",
                            messages=messages,
                            temperature=0.05,
                            max_tokens=200,
                        )
                else:
                    response = inference_huggingface(messages, scene.image_url, pipe)
                answer = response["choices"][0]["message"]["content"]
                model_str = None
            if model_str == "gpt4":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                        model="gpt-4-turbo-preview",
                        messages=messages,
                        temperature=0.05,
                        max_tokens=200,
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == "gpt4v":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                        model="gpt-4-vision-preview",
                        messages=messages,
                        temperature=0.05,
                        max_tokens=200, 
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == "gpt-4o-mini":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.05,
                        max_tokens=200,
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == "o1-preview":
                messages = [
                    {"role": "user", "content": system_prompt + prompt}]
                response = openai.ChatCompletion.create(
                        model="o1-preview-2024-09-12",
                        messages=messages,
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == "gpt3.5":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.05,
                        max_tokens=200,
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == "claude3.5sonnet":
                client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    system=system_prompt,
                    max_tokens=256,
                    messages=[{"role": "user", "content": prompt}])
                answer = json.loads(message.to_json())["content"][0]["text"]
            elif model_str == "gpt4o":
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.05,
                        max_tokens=200,
                    )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub("\s+", " ", answer)
            elif model_str == 'llama-2-70b-chat':
                output = replicate.run(
                    llama2_url, input={
                        "prompt":  prompt, 
                        "system_prompt": system_prompt,
                        "max_new_tokens": 200})
                answer = ''.join(output)
                answer = re.sub("\s+", " ", answer)
            elif model_str == 'mixtral-8x7b':
                output = replicate.run(
                    mixtral_url, 
                    input={"prompt": prompt, 
                            "system_prompt": system_prompt,
                            "max_new_tokens": 75})
                answer = ''.join(output)
                answer = re.sub("\s+", " ", answer)

            # elif model_str == 'mistralai/Mixtral-8x7B-v0.1':
            #     output = replicate.run(
            #         mixtral_url, 
            #         input={"prompt": prompt, 
            #                 "system_prompt": system_prompt,
            #                 "max_new_tokens": 75})
            #     answer = ''.join(output)
            #     answer = re.sub("\s+", " ", answer)

            elif model_str == 'llama-3-70b-instruct':
                output = replicate.run(
                    llama3_url, input={
                        "prompt":  prompt, 
                        "system_prompt": system_prompt,
                        "max_new_tokens": 200})
                answer = ''.join(output)
                answer = re.sub("\s+", " ", answer)
                
            else:
                # Load the model pipeline if pipe is None
                answer = inference_huggingface(system_prompt, prompt, pipe, style = model_str)
                # Generate text using the model pipeline
            return answer

        
        except Exception as e:
            time.sleep(timeout)
            continue
    raise Exception("Max retries: timeout")



class ScenarioMedQA:
    def __init__(self, scenario_dict) -> None:
        self.scenario_dict = scenario_dict
        self.tests = scenario_dict["OSCE_Examination"]["Test_Results"]
        self.diagnosis = scenario_dict["OSCE_Examination"]["Correct_Diagnosis"]
        self.patient_info  = scenario_dict["OSCE_Examination"]["Patient_Actor"]
        self.examiner_info  = scenario_dict["OSCE_Examination"]["Objective_for_Doctor"]
        self.physical_exams = scenario_dict["OSCE_Examination"]["Physical_Examination_Findings"]
    
    def patient_information(self) -> dict:
        return self.patient_info

    def examiner_information(self) -> dict:
        return self.examiner_info
    
    def exam_information(self) -> dict:
        exams = self.physical_exams
        exams["tests"] = self.tests
        return exams
    
    def diagnosis_information(self) -> dict:
        return self.diagnosis


class ScenarioLoaderMedQA:
    def __init__(self) -> None:
        with open("agentclinic_medqa.jsonl", "r") as f:
            self.scenario_strs = [json.loads(line) for line in f]
        self.scenarios = [ScenarioMedQA(_str) for _str in self.scenario_strs]
        self.num_scenarios = len(self.scenarios)
    
    def sample_scenario(self):
        return self.scenarios[random.randint(0, len(self.scenarios)-1)]
    
    def get_scenario(self, id):
        if id is None: return self.sample_scenario()
        return self.scenarios[id]
        


class ScenarioMedQAExtended:
    def __init__(self, scenario_dict) -> None:
        self.scenario_dict = scenario_dict
        self.tests = scenario_dict["OSCE_Examination"]["Test_Results"]
        self.diagnosis = scenario_dict["OSCE_Examination"]["Correct_Diagnosis"]
        self.patient_info  = scenario_dict["OSCE_Examination"]["Patient_Actor"]
        self.examiner_info  = scenario_dict["OSCE_Examination"]["Objective_for_Doctor"]
        self.physical_exams = scenario_dict["OSCE_Examination"]["Physical_Examination_Findings"]
    
    def patient_information(self) -> dict:
        return self.patient_info

    def examiner_information(self) -> dict:
        return self.examiner_info
    
    def exam_information(self) -> dict:
        exams = self.physical_exams
        exams["tests"] = self.tests
        return exams
    
    def diagnosis_information(self) -> dict:
        return self.diagnosis


class ScenarioLoaderMedQAExtended:
    def __init__(self) -> None:
        with open("agentclinic_medqa_extended.jsonl", "r") as f:
            self.scenario_strs = [json.loads(line) for line in f]
        self.scenarios = [ScenarioMedQAExtended(_str) for _str in self.scenario_strs]
        self.num_scenarios = len(self.scenarios)
    
    def sample_scenario(self):
        return self.scenarios[random.randint(0, len(self.scenarios)-1)]
    
    def get_scenario(self, id):
        if id is None: return self.sample_scenario()
        return self.scenarios[id]
        


class ScenarioMIMICIVQA:
    def __init__(self, scenario_dict) -> None:
        self.scenario_dict = scenario_dict
        self.tests = scenario_dict["OSCE_Examination"]["Test_Results"]
        self.diagnosis = scenario_dict["OSCE_Examination"]["Correct_Diagnosis"]
        self.patient_info  = scenario_dict["OSCE_Examination"]["Patient_Actor"]
        self.examiner_info  = scenario_dict["OSCE_Examination"]["Objective_for_Doctor"]
        self.physical_exams = scenario_dict["OSCE_Examination"]["Physical_Examination_Findings"]
    
    def patient_information(self) -> dict:
        return self.patient_info

    def examiner_information(self) -> dict:
        return self.examiner_info
    
    def exam_information(self) -> dict:
        exams = self.physical_exams
        exams["tests"] = self.tests
        return exams
    
    def diagnosis_information(self) -> dict:
        return self.diagnosis


class ScenarioLoaderMIMICIV:
    def __init__(self) -> None:
        with open("agentclinic_mimiciv.jsonl", "r") as f:
            self.scenario_strs = [json.loads(line) for line in f]
        self.scenarios = [ScenarioMIMICIVQA(_str) for _str in self.scenario_strs]
        self.num_scenarios = len(self.scenarios)
    
    def sample_scenario(self):
        return self.scenarios[random.randint(0, len(self.scenarios)-1)]
    
    def get_scenario(self, id):
        if id is None: return self.sample_scenario()
        return self.scenarios[id]


class ScenarioNEJMExtended:
    def __init__(self, scenario_dict) -> None:
        self.scenario_dict = scenario_dict 
        self.question = scenario_dict["question"] 
        self.image_url = scenario_dict["image_url"] 
        self.diagnosis = [_sd["text"] 
            for _sd in scenario_dict["answers"] if _sd["correct"]][0]
        self.patient_info = scenario_dict["patient_info"]
        self.physical_exams = scenario_dict["physical_exams"]

    def patient_information(self) -> str:
        patient_info = self.patient_info
        return patient_info

    def examiner_information(self) -> str:
        return "What is the most likely diagnosis?"
    
    def exam_information(self) -> str:
        exams = self.physical_exams
        return exams
    
    def diagnosis_information(self) -> str:
        return self.diagnosis


class ScenarioLoaderNEJMExtended:
    def __init__(self) -> None:
        with open("agentclinic_nejm_extended.jsonl", "r") as f:
            self.scenario_strs = [json.loads(line) for line in f]
        self.scenarios = [ScenarioNEJMExtended(_str) for _str in self.scenario_strs]
        self.num_scenarios = len(self.scenarios)
    
    def sample_scenario(self):
        return self.scenarios[random.randint(0, len(self.scenarios)-1)]
    
    def get_scenario(self, id):
        if id is None: return self.sample_scenario()
        return self.scenarios[id]


class ScenarioNEJM:
    def __init__(self, scenario_dict) -> None:
        self.scenario_dict = scenario_dict 
        self.question = scenario_dict["question"] 
        self.image_url = scenario_dict["image_url"] 
        self.diagnosis = [_sd["text"] 
            for _sd in scenario_dict["answers"] if _sd["correct"]][0]
        self.patient_info = scenario_dict["patient_info"]
        self.physical_exams = scenario_dict["physical_exams"]

    def patient_information(self) -> str:
        patient_info = self.patient_info
        return patient_info

    def examiner_information(self) -> str:
        return "What is the most likely diagnosis?"
    
    def exam_information(self) -> str:
        exams = self.physical_exams
        return exams
    
    def diagnosis_information(self) -> str:
        return self.diagnosis


class ScenarioLoaderNEJM:
    def __init__(self) -> None:
        with open("agentclinic_nejm.jsonl", "r") as f:
            self.scenario_strs = [json.loads(line) for line in f]
        self.scenarios = [ScenarioNEJM(_str) for _str in self.scenario_strs]
        self.num_scenarios = len(self.scenarios)
    
    def sample_scenario(self):
        return self.scenarios[random.randint(0, len(self.scenarios)-1)]
    
    def get_scenario(self, id):
        if id is None: return self.sample_scenario()
        return self.scenarios[id]


class PatientAgent:
    def __init__(self, scenario, backend_str="gpt4", bias_present=None, pipe=None) -> None:
        # disease of patient, or "correct answer"
        self.disease = ""
        # symptoms that patient presents
        self.symptoms = ""
        # conversation history between doctor and patient
        self.agent_hist = ""
        # language model backend for patient agent
        self.backend = backend_str
        # presentation of any form of bias
        self.bias_present = (None if bias_present == "None" else bias_present)
        # sample initial question from dataset
        self.scenario = scenario
        self.reset()
        self.pipe = pipe

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
        answer = query_model(self.backend, "\nHere is a history of your dialogue: " + self.agent_hist + "\n Here was the doctor response: " + question + "Now please continue your dialogue\nPatient: ", self.system_prompt(), pipe = self.pipe)
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

    def add_hist(self, hist_str, save_path="/home/komal.kumar/documment/MultiAgent/AgentClinic/Results/llma3b_20/Patient_history.txt" ) -> None:
        self.agent_hist += hist_str + "\n\n"
        # with open(save_path, "a") as file:
        #     file.write(hist_str + "\n\n")

class DoctorAgent:
    def __init__(self, scenario, backend_str="gpt4", max_infs=20, bias_present=None, img_request=False, pipe =None) -> None:
        # number of inference calls to the doctor
        self.infs = 0
        # maximum number of inference calls to the doctor
        self.MAX_INFS = max_infs
        # conversation history between doctor and patient
        self.agent_hist = ""
        # presentation information for doctor
        self.presentation = ""
        # language model backend for doctor agent
        self.backend = backend_str
        # presentation of any form of bias
        self.bias_present = (None if bias_present == "None" else bias_present)
        # prepare initial conditions for LLM
        self.scenario = scenario
        self.reset()
        self.pipe = pipe
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

    def inference_doctor(self, question, image_requested=False) -> str:
        answer = str()
        if self.infs >= self.MAX_INFS: return "Maximum inferences reached"
        answer = query_model(self.backend, "\nHere is a history of your dialogue: " + self.agent_hist + "\n Here was the patient response: " + question + "Now please continue your dialogue\nDoctor: ", self.system_prompt(), image_requested=image_requested, scene=self.scenario, pipe = self.pipe)
        self.agent_hist += question + "\n\n" + answer + "\n\n"
        self.infs += 1
        return answer

    def system_prompt(self) -> str:
        bias_prompt = ""
        if self.bias_present is not None:
            bias_prompt = self.generate_bias()
        base = "You are a doctor named Dr. Agent who only responds in the form of dialogue. You are inspecting a patient who you will ask questions in order to understand their disease. You are only allowed to ask {} questions total before you must make a decision but you have to provide find the disease. You have asked {} questions so far. You can request test results using the format \"REQUEST TEST: [test]\". For example, \"REQUEST TEST: Chest_X-Ray\". Your dialogue will only be 1-3 sentences in length. Once you have decided to make a diagnosis please type \"DIAGNOSIS READY: [diagnosis here]\"".format(self.MAX_INFS, self.infs) + ("You may also request medical images related to the disease to be returned with \"REQUEST IMAGES\"." if self.img_request else "")
        presentation = "\n\nBelow is all of the information you have. {}. \n\n Remember, you must discover their disease by asking them questions. You are also able to provide exams.".format(self.presentation)
        return base + bias_prompt + presentation

    def reset(self) -> None:
        self.agent_hist = ""
        self.presentation = self.scenario.examiner_information()

    def add_hist(self, hist_str, save_path="/home/komal.kumar/documment/MultiAgent/AgentClinic/Results/llma3b_20/Doc_history.txt" ) -> None:
        self.agent_hist += hist_str + "\n\n"
        # with open(save_path, "a") as file:
        #     file.write(hist_str + "\n\n")

class MeasurementAgent:
    def __init__(self, scenario, backend_str="gpt4", pipe = None) -> None:
        # conversation history between doctor and patient
        self.agent_hist = ""
        # presentation information for measurement 
        self.presentation = ""
        # language model backend for measurement agent
        self.backend = backend_str
        # prepare initial conditions for LLM
        self.scenario = scenario
        self.pipe = pipe
        self.reset()

    def inference_measurement(self, question) -> str:
        answer = str()
        answer = query_model(self.backend, "\nHere is a history of the dialogue: " + self.agent_hist + "\n Here was the doctor measurement request: " + question, self.system_prompt(), pipe = self.pipe)
        self.agent_hist += question + "\n\n" + answer + "\n\n"
        return answer

    def system_prompt(self) -> str:
        base = "You are an measurement reader who responds with medical test results. Please respond in the format \"RESULTS: [results here]\""
        presentation = "\n\nBelow is all of the information you have. {}. \n\n If the requested results are not in your data then you can respond with NORMAL READINGS.".format(self.information)
        return base + presentation
    
    def add_hist(self, hist_str, save_path="Measure_history.txt") -> None:
        pass
        # with open(save_path, "a") as file:
        #     file.write(hist_str + "\n\n")
    def reset(self) -> None:
        self.agent_hist = ""
        self.information = self.scenario.exam_information()


def compare_results(diagnosis, correct_diagnosis, moderator_llm, mod_pipe):
    answer = query_model(moderator_llm, "\nHere is the correct diagnosis: " + correct_diagnosis + "\n Here was the doctor dialogue: " + diagnosis + "\nAre these the same?", "You are responsible for determining if the corrent diagnosis and the doctor diagnosis are the same disease. Please respond only with Yes or No. Nothing else.", pipe = mod_pipe)
    return answer.lower()

def load_model(model_name, vision=False, device = 'auto', load_in_8bit = False):
    """
    Load the model based on the provided model name.
    """
    if model_name.startswith("HF_"):
        model_identifier = model_name[len("HF_"):]
        style = ""
        if vision:
            style = "vision"
        pipe = load_huggingface_model(model_identifier, st=style, device = device, load_in_8bit = load_in_8bit)
        return pipe
    elif model_name in ANTHROPIC_LLMS:
        # Implement load_anthropic_model if necessary
        raise NotImplementedError("Anthropic models are not implemented in this script.")
    elif model_name in REPLICATE_LLMS:
        # Implement load_replicate_model if necessary
        raise NotImplementedError("Replicate models are not implemented in this script.")
    elif model_name.startswith("gpt"):
        # OpenAI GPT models use API calls; no need to load
        return None
    else:
        return None
# Model alias mapping
MODEL_ALIASES = {
    "llama2": "meta/llama-2-70b-chat",
    "llama2_hf": "meta-llama/Llama-2-70b-chat-hf",
    "llama3": "meta-llama/Meta-Llama-3-70B-Instruct",
    "mixtral": "mistralai/mixtral-8x7b-instruct-v0.1",
    "llama11b": "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "llama3b": "meta-llama/Llama-3.2-3B-Instruct",
    "llama3_7b": "meta-llama/Meta-Llama-3-8B-Instruct",
    "med": "AdaptLLM/medicine-LLM",
    "med_chat": "AdaptLLM/medicine-chat",
    "llama3_1_8": "meta-llama/Llama-3.1-8B-Instruct",
    "llama_70_3p1": "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "llama_med": "HPAI-BSC/Llama3.1-Aloe-Beta-8B", 
    "q": "mlx-community/Llama-3.3-70B-Instruct-8bit"
}

def resolve_model_name(model_name):
    """
    Resolve the model alias to its full name.
    """
    return MODEL_ALIASES.get(model_name, model_name)
def is_diagnosis_ready(dialogue):
    pattern = r'\b(Diagnosis|DIAGNOSIS|diagnosis|diag|diagnostic)\s*(ready|available|complete|done|prepared)\b[:\-]?\s*(.+)'
    match = re.search(pattern, dialogue, re.IGNORECASE | re.MULTILINE)
    if match:
        diagnosis = match.group(1).strip()
        return diagnosis  # Return the diagnosis text
    return None

def main(
    api_key,
    replicate_api_key,
    inf_type,
    doctor_bias,
    patient_bias,
    doctor_llm,
    patient_llm,
    measurement_llm,
    moderator_llm,
    num_scenarios,
    dataset,
    img_request,
    total_inferences,
    output_dir,
    anthropic_api_key=None,
):
    # Set API keys
    openai.api_key = api_key
    if replicate_api_key:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
    if anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key

    # Resolve model names from aliases
    doctor_llm = resolve_model_name(doctor_llm)
    patient_llm = resolve_model_name(patient_llm)
    measurement_llm = resolve_model_name(measurement_llm)
    moderator_llm = resolve_model_name(moderator_llm)

    # Load dataset scenarios
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
        raise Exception(f"Dataset {dataset} does not exist")

    total_correct = 0
    total_presents = 0
    print(f"Using {dataset} for simulation")

    # Load models for agents
    pipe_d = QwenAssistant(doctor_llm)
    pipe_p = QwenAssistant(patient_llm)
    pipe_m = QwenAssistant(measurement_llm)
    mpipe = QwenAssistant(moderator_llm)

    if num_scenarios is None:
        num_scenarios = scenario_loader.num_scenarios

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    for _scenario_id in tqdm(
        range(0, min(num_scenarios, scenario_loader.num_scenarios)),
        desc="Running Scenarios",
    ):
        total_presents += 1
        pi_dialogue = ""
        dialogue_history = []  # Initialize dialogue history list

        # Initialize scenario and agents
        scenario = scenario_loader.get_scenario(id=_scenario_id)
        meas_agent = MeasurementAgent(
            scenario=scenario, backend_str=measurement_llm, pipe=pipe_m
        )
        patient_agent = PatientAgent(
            scenario=scenario,
            bias_present=patient_bias,
            backend_str=patient_llm,
            pipe=pipe_p,
        )
        doctor_agent = DoctorAgent(
            scenario=scenario,
            bias_present=doctor_bias,
            backend_str=doctor_llm,
            max_infs=total_inferences,
            img_request=img_request,
            pipe=pipe_d,
        )
        doctor_dialogue = ""

        for _inf_id in tqdm(range(total_inferences+1), desc="Running Inferences"):
            imgs = (
                dataset == "NEJM"
                and img_request
                and "REQUEST IMAGES" in doctor_dialogue
            )

            if _inf_id == total_inferences - 1:
                pi_dialogue += "This is the final question. Please provide a diagnosis.\n"
            # elif _inf_id == total_inferences:
            #     pi_dialogue += f'Please provide the diagnosis.\n'

            if inf_type == "human_doctor":
                doctor_dialogue = input("\nQuestion for patient: ")
            else:
                # doctor_llm.startswith("HF_"):
                    system_prompt = doctor_agent.get_system_prompt()
                    prompt = doctor_agent.get_prompt(pi_dialogue, image_requested=imgs)
                    doctor_dialogue = inference_huggingface(
                        system_prompt, prompt, pipe_d
                    )
            print(
                f"Doctor [{int(((_inf_id + 1) / total_inferences) * 100)}%]: {doctor_dialogue}"
            )
            dialogue_history.append({"speaker": "Doctor", "text": doctor_dialogue})

            if "DIAGNOSIS READY" in doctor_dialogue:
                correctness = (
                    compare_results(
                        doctor_dialogue,
                        scenario.diagnosis_information(),
                        moderator_llm,
                        mpipe,
                    )
                    == "yes"
                )
                if correctness:
                    total_correct += 1
                print(f"\nCorrect answer: {scenario.diagnosis_information()}")
                print(
                    f"Scene {_scenario_id}, The diagnosis was {'CORRECT' if correctness else 'INCORRECT'}, "
                    f"{int((total_correct / total_presents) * 100)}%"
                )
                dialogue_history.append(
                    {
                        "DIAGNOSIS_READY_Answer": scenario.diagnosis_information(),
                        "DIAGNOSIS_READY_Simulation": f"Scene {_scenario_id}, The diagnosis was "
                        f"{'CORRECT' if correctness else 'INCORRECT'}, "
                        f"{int((total_correct / total_presents) * 100)}%",
                    }
                )
                if correctness:
                    break

            if "REQUEST TEST" in doctor_dialogue:
                pi_dialogue = meas_agent.inference_measurement(doctor_dialogue)
                print(
                    f"Measurement [{int(((_inf_id + 1) / total_inferences) * 100)}%]: {pi_dialogue}"
                )
                patient_agent.add_hist(pi_dialogue)
                dialogue_history.append(
                    {"speaker": "Measurement", "text": pi_dialogue}
                )
            else:
                if inf_type == "human_patient":
                    pi_dialogue = input("\nResponse to doctor: ")
                else:
                    # Use inference_huggingface if patient_llm is a Hugging Face model
                    if patient_llm.startswith("HF_"):
                        system_prompt = patient_agent.get_system_prompt()
                        prompt = patient_agent.get_prompt(doctor_dialogue)
                        pi_dialogue = inference_huggingface(
                            system_prompt, prompt, pipe_p
                        )
                    else:
                        pi_dialogue = patient_agent.inference_patient(doctor_dialogue)
                print(
                    f"Patient [{int(((_inf_id + 1) / total_inferences) * 100)}%]: {pi_dialogue}"
                )
                dialogue_history.append({"speaker": "Patient", "text": pi_dialogue})
            time.sleep(1.0)  # Prevent API timeouts

        # Save the dialogue history to a JSON file at the end of each scenario
        scenario_output_dir = os.path.join(output_dir, f"scenario_{_scenario_id}")
        os.makedirs(scenario_output_dir, exist_ok=True)
        dialogue_file = os.path.join(scenario_output_dir, "dialogue_history.json")
        with open(dialogue_file, "w") as f:
            json.dump(dialogue_history, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Medical Diagnosis Simulation CLI")
    parser.add_argument(
        "--openai_api_key", type=str, required=False, help="OpenAI API Key"
    )
    parser.add_argument(
        "--replicate_api_key", type=str, required=False, help="Replicate API Key"
    )
    parser.add_argument(
        "--inf_type",
        type=str,
        choices=["llm", "human_doctor", "human_patient"],
        default="llm",
    )
    parser.add_argument(
        "--doctor_bias",
        type=str,
        default="None",
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
        help="Doctor bias type",
    )
    parser.add_argument(
        "--patient_bias",
        type=str,
        default="None",
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
        help="Patient bias type",
    )
    parser.add_argument(
        "--doctor_llm", type=str, default="mixtral", help="Doctor model alias or name"
    )
    parser.add_argument(
        "--patient_llm", type=str, default="mixtral", help="Patient model alias or name"
    )
    parser.add_argument(
        "--measurement_llm",
        type=str,
        default="mixtral",
        help="Measurement model alias or name",
    )
    parser.add_argument(
        "--moderator_llm",
        type=str,
        default="mixtral",
        help="Moderator model alias or name",
    )
    parser.add_argument(
        "--agent_dataset",
        type=str,
        default="MedQA",
        help="Dataset to use (MedQA, MIMICIV, NEJM)",
    )
    parser.add_argument(
        "--doctor_image_request",
        action="store_true",
        help="Whether images must be requested or are provided",
    )
    parser.add_argument(
        "--num_scenarios",
        type=int,
        default=None,
        help="Number of scenarios to simulate",
    )
    parser.add_argument(
        "--total_inferences",
        type=int,
        default=20,
        help="Number of inferences between patient and doctor",
    )
    parser.add_argument(
        "--anthropic_api_key",
        type=str,
        default=None,
        help="Anthropic API key for Claude 3.5 Sonnet",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./Results",
        help="Directory to save output files",
    )

    args = parser.parse_args()

    main(
        api_key=args.openai_api_key,
        replicate_api_key=args.replicate_api_key,
        inf_type=args.inf_type,
        doctor_bias=args.doctor_bias,
        patient_bias=args.patient_bias,
        doctor_llm=args.doctor_llm,
        patient_llm=args.patient_llm,
        measurement_llm=args.measurement_llm,
        moderator_llm=args.moderator_llm,
        num_scenarios=args.num_scenarios,
        dataset=args.agent_dataset,
        img_request=args.doctor_image_request,
        total_inferences=args.total_inferences,
        output_dir=args.output_dir,
        anthropic_api_key=args.anthropic_api_key,
    )
    
#python3 agentclinic.py --inf_type "llm" --inf_type "llm" --patient_llm "HF_mistralai/Mixtral-8x7B-v0.1"  --moderator_llm "HF_mistralai/Mixtral-8x7B-v0.1"  --doctor_llm "HF_mistralai/Mixtral-8x7B-v0.1"  --measurement_llm "HF_mistralai/Mixtral-8x7B-v0.1"
#python3 agentclinic.py --inf_type "llm" --inf_type "llm" --patient_llm "gpt-4o-mini"  --moderator_llm "gpt-4o-mini"  --doctor_llm "gpt-4o-mini"  --measurement_llm "gpt-4o-mini" --openai_api_key "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" --output_dir "/home/komal.kumar/documment/MultiAgent/AgentClinic/Results/chatgpt/"