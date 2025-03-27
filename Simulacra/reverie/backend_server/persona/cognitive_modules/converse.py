"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: converse.py
Description: An extra cognitive module for generating conversations. 
"""
import math
import sys
import datetime
import random
import json
import re
import os
import glob
import yaml
sys.path.append('../')

from global_methods import *

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *
from persona.cognitive_modules.retrieve import *
from persona.prompt_template.run_gpt_prompt import *

# Add the TOQ directory to sys.path
# Dynamically add the TOQ directory to sys.path
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of converse.py
toq_dir = os.path.abspath(os.path.join(current_file_dir, "../../../../../TOQ"))
# toq_dir = os.path.abspath("../../../../../TOQ")
print(f"Resolved TOQ directory: {toq_dir}")
if toq_dir not in sys.path:
    sys.path.append(toq_dir)

from run import prep

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def generate_agent_chat_summarize_ideas(init_persona, 
                                        target_persona, 
                                        retrieved, 
                                        curr_context): 
  all_embedding_keys = list()
  for key, val in retrieved.items(): 
    for i in val: 
      all_embedding_keys += [i.embedding_key]
  all_embedding_key_str =""
  for i in all_embedding_keys: 
    all_embedding_key_str += f"{i}\n"

  try: 
    summarized_idea = run_gpt_prompt_agent_chat_summarize_ideas(init_persona,
                        target_persona, all_embedding_key_str, 
                        curr_context)[0]
  except:
    summarized_idea = ""
  return summarized_idea


def generate_summarize_agent_relationship(init_persona, 
                                          target_persona, 
                                          retrieved): 
  all_embedding_keys = list()
  for key, val in retrieved.items(): 
    for i in val: 
      all_embedding_keys += [i.embedding_key]
  all_embedding_key_str =""
  for i in all_embedding_keys: 
    all_embedding_key_str += f"{i}\n"

  summarized_relationship = run_gpt_prompt_agent_chat_summarize_relationship(
                              init_persona, target_persona,
                              all_embedding_key_str)[0]
  return summarized_relationship


def generate_agent_chat(maze, 
                        init_persona, 
                        target_persona,
                        curr_context, 
                        init_summ_idea, 
                        target_summ_idea): 
  summarized_idea = run_gpt_prompt_agent_chat(maze, 
                                              init_persona, 
                                              target_persona,
                                              curr_context, 
                                              init_summ_idea, 
                                              target_summ_idea)[0]
  for i in summarized_idea: 
    print (i)
  return summarized_idea


def agent_chat_v1(maze, init_persona, target_persona): 
  # Chat version optimized for speed via batch generation
  curr_context = (f"{init_persona.scratch.name} " + 
              f"was {init_persona.scratch.act_description} " + 
              f"when {init_persona.scratch.name} " + 
              f"saw {target_persona.scratch.name} " + 
              f"in the middle of {target_persona.scratch.act_description}.\n")
  curr_context += (f"{init_persona.scratch.name} " +
              f"is thinking of initating a conversation with " +
              f"{target_persona.scratch.name}.")

  summarized_ideas = []
  part_pairs = [(init_persona, target_persona), 
                (target_persona, init_persona)]
  for p_1, p_2 in part_pairs: 
    focal_points = [f"{p_2.scratch.name}"]
    retrieved = new_retrieve(p_1, focal_points, 50)
    relationship = generate_summarize_agent_relationship(p_1, p_2, retrieved)
    focal_points = [f"{relationship}", 
                    f"{p_2.scratch.name} is {p_2.scratch.act_description}"]
    retrieved = new_retrieve(p_1, focal_points, 25)
    summarized_idea = generate_agent_chat_summarize_ideas(p_1, p_2, retrieved, curr_context)
    summarized_ideas += [summarized_idea]

  return generate_agent_chat(maze, init_persona, target_persona, 
                      curr_context, 
                      summarized_ideas[0], 
                      summarized_ideas[1])


def generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat): 
  # Chat version optimized for speed via batch generation
  curr_context = (f"{init_persona.scratch.name} " + 
              f"was {init_persona.scratch.act_description} " + 
              f"when {init_persona.scratch.name} " + 
              f"saw {target_persona.scratch.name} " + 
              f"in the middle of {target_persona.scratch.act_description}.\n")
  curr_context += (f"{init_persona.scratch.name} " +
              f"is initiating a conversation with " +
              f"{target_persona.scratch.name}.")

  print ("July 23 5")
  x = run_gpt_generate_iterative_chat_utt(maze, init_persona, target_persona, retrieved, curr_context, curr_chat)[0]

  print ("July 23 6")

  print ("adshfoa;khdf;fajslkfjald;sdfa HERE", x)

  return x["utterance"], x["end"]

def agent_chat_v2(maze, init_persona, target_persona): 
  curr_chat = []
  print ("July 23")

  for i in range(8): 
    focal_points = [f"{target_persona.scratch.name}"]
    retrieved = new_retrieve(init_persona, focal_points, 50)
    relationship = generate_summarize_agent_relationship(init_persona, target_persona, retrieved)
    print ("-------- relationshopadsjfhkalsdjf", relationship)
    last_chat = ""
    for i in curr_chat[-4:]:
      last_chat += ": ".join(i) + "\n"
    if last_chat: 
      focal_points = [f"{relationship}", 
                      f"{target_persona.scratch.name} is {target_persona.scratch.act_description}", 
                      last_chat]
    else: 
      focal_points = [f"{relationship}", 
                      f"{target_persona.scratch.name} is {target_persona.scratch.act_description}"]
    retrieved = new_retrieve(init_persona, focal_points, 15)
    utt, end = generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat)

    curr_chat += [[init_persona.scratch.name, utt]]
    if end:
      break


    focal_points = [f"{init_persona.scratch.name}"]
    retrieved = new_retrieve(target_persona, focal_points, 50)
    relationship = generate_summarize_agent_relationship(target_persona, init_persona, retrieved)
    print ("-------- relationshopadsjfhkalsdjf", relationship)
    last_chat = ""
    for i in curr_chat[-4:]:
      last_chat += ": ".join(i) + "\n"
    if last_chat: 
      focal_points = [f"{relationship}", 
                      f"{init_persona.scratch.name} is {init_persona.scratch.act_description}", 
                      last_chat]
    else: 
      focal_points = [f"{relationship}", 
                      f"{init_persona.scratch.name} is {init_persona.scratch.act_description}"]
    retrieved = new_retrieve(target_persona, focal_points, 15)
    utt, end = generate_one_utterance(maze, target_persona, init_persona, retrieved, curr_chat)

    curr_chat += [[target_persona.scratch.name, utt]]
    if end:
      break

  print ("July 23 PU")
  for row in curr_chat: 
    print (row)
  print ("July 23 FIN")

  return curr_chat


def extract_sim_info():
  current_file_dir = os.path.dirname(os.path.abspath(__file__))
  json_file_path = os.path.join(current_file_dir, "../..", "simulation_controller.json")
  json_file_path = os.path.normpath(json_file_path)  # Normalize the path

  # Load the existing JSON file
  with open(json_file_path, 'r') as file:
    data = json.load(file)

  # Get info
  return data["total_scenarios"], data["total_correct"], data["num_scenarios"], data["simulation_index"]


def update_sim_info(is_correct):
  current_file_dir = os.path.dirname(os.path.abspath(__file__))
  json_file_path = os.path.join(current_file_dir, "../..", "simulation_controller.json")
  json_file_path = os.path.normpath(json_file_path)  # Normalize the path

  # Load the existing JSON file
  with open(json_file_path, 'r') as file:
    data = json.load(file)

  total_scenarios = data["total_scenarios"]
  total_correct = data["total_correct"]

  # Update scenario info
  data["total_scenarios"] = total_scenarios + 1
  if is_correct:
    data["total_correct"] = total_correct + 1

  # Save the JSON data (either new or updated) back to the file
  with open(json_file_path, 'w') as file:
    json.dump(data, file, indent=4)


def generate_chat_v3(total_scenarios, total_correct, num_scenarios, scenario_id):
  current_file_dir = os.path.dirname(os.path.abspath(__file__))
  config_path = os.path.join(current_file_dir, "../../../../..", "TOQ/configs/config_sim.yaml")
  config = load_config(config_path)

  working_dir = os.getcwd()
  os.chdir(toq_dir)

  is_correct = prep(config, total_scenarios, total_correct, num_scenarios, scenario_id)
  os.chdir(working_dir)
  return is_correct

def agent_chat_v3(doctor_name, patient_name):
  # Specify the path to the JSON file
  total_scenarios, total_correct, num_scenarios, idx = extract_sim_info()
  is_correct = generate_chat_v3(total_scenarios, total_correct, num_scenarios, idx)
  update_sim_info(is_correct)
  
  current_file_dir = os.path.dirname(os.path.abspath(__file__))
  json_paths = os.path.join(current_file_dir, "../../../../..", "TOQ/output")
  print(json_paths)
  json_files = glob.glob(os.path.join(json_paths, "*.json"))

  # Extract and print the results
  convo = extract_speaker_text(json_files[idx], doctor_name, patient_name)
  # return [['Maria Lopez', 'Hello Klaus, how can I help you today?'], ['Klaus Mueller', "Hello Dr. Lopez, I'm not feeling well and need your help."], ['Maria Lopez', "I'm sorry to hear that. Can you please describe your symptoms to me?"], ['Klaus Mueller', "I have been experiencing a sharp pain in my tooth for the past few days and it's becoming unbearable. I think I may have a dental issue that needs to be addressed."],['Maria Lopez', 'I understand, Klaus. Let me take a look at your tooth and do an examination to determine the cause of the pain.'],['Klaus Mueller', 'Thank you for taking the time to examine my tooth, Dr. Lopez.'],['Maria Lopez', 'Let me get my equipment ready to examine your tooth. Please have a seat in the examination chair over there.'],['Klaus Mueller', 'Thank you, Dr. Lopez. I appreciate your help.'],['Maria Lopez', "Let's start by taking some X-rays of your tooth to get a better understanding of the issue."],['Klaus Mueller', "Thank you, Dr. Lopez. I'm glad we're taking steps to address my dental issue."],['Maria Lopez', 'After reviewing the X-rays, I can see that you have a cavity in your tooth. We will need to schedule a filling procedure to address the issue.'],['Maria Lopez', 'We can schedule the filling procedure for Thursday at 2 pm. Does that work for you?'],['Klaus Mueller', 'That works for me, thank you for scheduling the filling procedure on Thursday at 2pm, Dr. Lopez.'],['Maria Lopez', 'Great, I will see you on Thursday at 2 pm for the filling procedure. In the meantime, make sure to avoid any hard or sticky foods that could aggravate the cavity.'],['Klaus Mueller', 'Thank you, Dr. Lopez. I will make sure to follow your advice on avoiding hard or sticky foods.']]
  return convo

# Function to load JSON from a file and extract speaker-text pairs
def extract_speaker_text(json_path, doc_name, pat_name):
    try:
        # Load JSON data from the file
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        corrected_conversations = []
        buffer_text = ""

        for entry in data:
            if "speaker" in entry and "text" in entry:
                speaker = entry["speaker"]
                
                # Skip entries where speaker is "Measurement"
                if speaker == "Measurement":
                    continue
                    
                if speaker == "Doctor":
                    speaker = doc_name
                elif speaker == "Patient":
                    speaker = pat_name
                    
                text = buffer_text + entry["text"]
                buffer_text = ""
                
                text = re.sub(r"\bREQUEST TEST:\s*", "", text)

                # Regex to check if text contains an unintended speaker mention
                match = re.search(r"\n\n(Doctor|Patient):", text)
                if match:
                    split_index = match.start()
                    current_text = text[:split_index].strip()
                    next_text = text[split_index:].strip()

                    # Remove the "Doctor: " or "Patient: " prefix from the next text
                    next_text = re.sub(r"^(Doctor|Patient):\s*", "", next_text).strip()

                    # Add current speaker's corrected text
                    corrected_conversations.append([speaker, current_text])

                    # Buffer the next speaker's text for the next entry with a space
                    buffer_text = next_text + " "
                else:
                    corrected_conversations.append([speaker, text])
                    
        # Remove duplicate consecutive speaker entries (keep only the latest one)
        deduplicated_conversations = []
        for i in range(len(corrected_conversations)):
            if i > 0 and corrected_conversations[i][0] == corrected_conversations[i - 1][0]:
                # Remove the previous entry and add the current one
                deduplicated_conversations.pop()  # Remove the previous duplicate
            deduplicated_conversations.append(corrected_conversations[i])

        corrected_conversations = deduplicated_conversations
                    
        # Process last element to remove "DIAGNOSIS READY:" section
        last_speaker, last_text = corrected_conversations[-1]
        diagnosis_pattern = re.search(r"DIAGNOSIS READY:.*?\n\n", last_text, re.DOTALL)
        if diagnosis_pattern:
            last_text = last_text.replace(diagnosis_pattern.group(), "").strip()
            corrected_conversations[-1] = [last_speaker, last_text]

        return corrected_conversations

    except FileNotFoundError:
        print(f"Error: The file '{json_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{json_path}'.")
        return []

def generate_summarize_ideas(persona, nodes, question): 
  statements = ""
  for n in nodes:
    statements += f"{n.embedding_key}\n"
  summarized_idea = run_gpt_prompt_summarize_ideas(persona, statements, question)[0]
  return summarized_idea


def generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea):
  # Original chat -- line by line generation 
  prev_convo = ""
  for row in curr_convo: 
    prev_convo += f'{row[0]}: {row[1]}\n'

  next_line = run_gpt_prompt_generate_next_convo_line(persona, 
                                                      interlocutor_desc, 
                                                      prev_convo, 
                                                      summarized_idea)[0]  
  return next_line


def generate_inner_thought(persona, whisper):
  inner_thought = run_gpt_prompt_generate_whisper_inner_thought(persona, whisper)[0]
  return inner_thought

def generate_action_event_triple(act_desp, persona): 
  """TODO 

  INPUT: 
    act_desp: the description of the action (e.g., "sleeping")
    persona: The Persona class instance
  OUTPUT: 
    a string of emoji that translates action description.
  EXAMPLE OUTPUT: 
    "🧈🍞"
  """
  if debug: print ("GNS FUNCTION: <generate_action_event_triple>")
  return run_gpt_prompt_event_triple(act_desp, persona)[0]


def generate_poig_score(persona, event_type, description): 
  if debug: print ("GNS FUNCTION: <generate_poig_score>")

  if "is idle" in description: 
    return 1

  if event_type == "event" or event_type == "thought": 
    return run_gpt_prompt_event_poignancy(persona, description)[0]
  elif event_type == "chat": 
    return run_gpt_prompt_chat_poignancy(persona, 
                           persona.scratch.act_description)[0]


def load_history_via_whisper(personas, whispers):
  for count, row in enumerate(whispers): 
    persona = personas[row[0]]
    whisper = row[1]

    thought = generate_inner_thought(persona, whisper)

    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
    s, p, o = generate_action_event_triple(thought, persona)
    keywords = set([s, p, o])
    thought_poignancy = generate_poig_score(persona, "event", whisper)
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o, 
                              thought, keywords, thought_poignancy, 
                              thought_embedding_pair, None)


def open_convo_session(persona, convo_mode, safe_mode=True, direct=False, question: str=None): 
  if direct and question is None:
    raise ValueError("If direct is True, question must be provided.")
  if convo_mode == "analysis": 
    curr_convo = []
    interlocutor_desc = "Interviewer"

    while True:
      if direct:
        line = question
      else:
        line = input("Enter Input: ")
      if line == "end_convo": 
        break

      if int(run_gpt_generate_safety_score(persona, line)[0]) >= 8 and safe_mode: 
        print (f"{persona.scratch.name} is a computational agent, and as such, it may be inappropriate to attribute human agency to the agent in your communication.")        

      else: 
        retrieved = new_retrieve(persona, [line], 50)[line]
        summarized_idea = generate_summarize_ideas(persona, retrieved, line)
        curr_convo += [[interlocutor_desc, line]]

        next_line = generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea)
        curr_convo += [[persona.scratch.name, next_line]]
        if direct: 
          return curr_convo


  elif convo_mode == "whisper": 
    whisper = input("Enter Input: ")
    thought = generate_inner_thought(persona, whisper)

    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
    s, p, o = generate_action_event_triple(thought, persona)
    keywords = set([s, p, o])
    thought_poignancy = generate_poig_score(persona, "event", whisper)
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o, 
                              thought, keywords, thought_poignancy, 
                              thought_embedding_pair, None)
































