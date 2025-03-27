"""
utils.py
---------
This module provides helper functions such as comparing diagnosis results and logging conversation data.
"""

import os
from query_model import query_model

def compare_results(doctor_diagnosis: str, correct_diagnosis: str, moderator_llm: str, mod_pipe):
    """
    Compares the doctor’s diagnosis with the correct diagnosis using the moderator LLM.
    Returns a lowercase string ("yes" or "no").
    """
    prompt = (
        "\nHere is the correct diagnosis: " + correct_diagnosis +
        "\nHere was the doctor dialogue: " + doctor_diagnosis +
        "\nAre these the same?"
    )
    system_prompt = ("You are responsible for determining if the correct diagnosis and the doctor diagnosis "
                     "are the same disease. Please respond only with Yes or No. Nothing else.")
    answer = query_model(moderator_llm, prompt, system_prompt)
    return answer.lower()


def save_conversation_log(conversation_log: list, scenario_id: int, output_dir: str = "org_results/DeepSeek-R1-Distill-Llama-70B"):
    """Saves the conversation log for a scenario to a text file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f'{output_dir}/{scenario_id}.txt'
    with open(filename, 'w') as file:
        for line in conversation_log:
            file.write(line + '\n')
    print(f"Conversation log for scenario {scenario_id} saved to {filename}")