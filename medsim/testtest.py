import os
import sys
import gzip
import json
from collections import Counter

from importlib import import_module

import json
import random

import openai

api_key = "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"
openai.api_key = api_key

messages = [] 

def chatgpt_response(message):
    messages = [ 
            {"role": "system", "content":  
              "You are a highly knowledgeable and precise AI assistant specializing in medical reasoning. Your role is to analyze clinical scenarios and provide accurate, evidence-based differential diagnoses. You will assess the details of each case carefully and generate insightful responses that adhere to medical best practices. If there is ambiguity, provide the most likely explanations based on the available data."},
            {"role": "user", "content": message}, 
    ] 
    chat = openai.chat.completions.create( 
                model="gpt-4o", messages=messages 
            ) 
    reply = chat.choices[0].message.content.replace('"',"")
    
    return reply


def extract_bracket_content(s: str):
    if "[" in s and "]" in s:
        return "[" + s.split("[", 1)[-1].split("]")[0] + "]"
    return s  # Return original string if brackets are not found

def clean_diagnosis(message):
    message = extract_bracket_content(message)
    
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

def generate_possible_diagnoses(question: str, answer: str):
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
    response = chatgpt_response(prompt)
    
    # Extract the response as a list
    diagnoses = clean_diagnosis(response)  # Assuming response is in list format
    
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


question = "Provide the most likely final diagnosis for the following patient. A ___ year old man presents with one week of new onset mid epigastric abdominal pain, associated with nausea, vomiting, and poor PO intake. The pain worsened with contact of his right foot to the ground, improved over the day but recurred. Laboratory results show a total bilirubin of 0.5 mg/dL (RR: 0.0 - 1.5) and elevated Alkaline Phosphatase of 67.0 IU/L (RR: 40.0 - 130.0). A right upper quadrant ultrasound revealed gallbladder wall thickening. What is the final diagnosis for this patient?"
answer = "Cholecystitis"
answer_list = generate_possible_diagnoses(question, answer)
answer_choices, correct_answer = generate_answer_choices(answer, answer_list)
generate_question_json(question, answer_choices, correct_answer)


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


def get_diagnosis():
    generate_single = import_generate() # mmlu
    generate_single("temp_question.json")

    # Usage Example
    result_json = get_result_json()
    lst = [result_json[0]["expt"][key]["answer"] for key in result_json[0]["expt"]]

    counter = Counter(lst)
    most_common = counter.most_common(1)[0][0]  # Get the most common element

    expt_keys = result_json[0]["expt"]
    for key in expt_keys:
        print(result_json[0]["expt"][key]["answer"])  # Print the JSON data
    print(result_json[0]["answer_choices"])
    dia = result_json[0]["answer_choices"][most_common]
    print(dia)

    return dia


get_diagnosis()



