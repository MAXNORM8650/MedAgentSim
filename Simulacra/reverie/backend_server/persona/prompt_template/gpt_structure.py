"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""
import time 
import json
from pathlib import Path
from openai import AzureOpenAI, OpenAI

from utils import *
from openai_cost_logger import DEFAULT_LOG_PATH
from persona.prompt_template.openai_logger_singleton import OpenAICostLogger_Singleton
import os 
import sys
from importlib import import_module

config_path = Path("../../openai_config.json")
with open(config_path, "r") as f:
    openai_config = json.load(f) 


def import_bagent():
    # Get absolute path of current file
    current_file = os.path.abspath(__file__)

    # Move up to project root (TOQ/)
    root_dir = os.path.abspath(os.path.join(current_file, "../../../../.."))

    # Add the inner TOQ/TOQ to path so we can import query_model
    toq_path = os.path.join(root_dir, "medsim")
    if toq_path not in sys.path:
        sys.path.append(toq_path)

    # Import the module and return the class
    module = import_module("query_model")  # NOT "medsim.query_model" since TOQ is now in sys.path
    return module.BAgent

# def setup_client(type: str, config: dict):
#   """Setup the OpenAI client.

#   Args:
#       type (str): the type of client. Either "azure" or "openai".
#       config (dict): the configuration for the client.

#   Raises:
#       ValueError: if the client is invalid.

#   Returns:
#       The client object created, either AzureOpenAI or OpenAI.
#   """
#   if type == "azure":
#     client = AzureOpenAI(
#         azure_endpoint=config["endpoint"],
#         api_key=config["key"],
#         api_version=config["api-version"],
#     )
#   elif type == "openai":
#     client = OpenAI(
#         api_key=config["key"],
#     )
#   else:
#     raise ValueError("Invalid client")
#   return client

# if openai_config["client"] == "azure":
#   client = setup_client("azure", {
#       "endpoint": openai_config["model-endpoint"],
#       "key": openai_config["model-key"],
#       "api-version": openai_config["model-api-version"],
#   })
# elif openai_config["client"] == "openai":
#   client = setup_client("openai", { "key": openai_config["model-key"] })

# if openai_config["embeddings-client"] == "azure":  
#   embeddings_client = setup_client("azure", {
#       "endpoint": openai_config["embeddings-endpoint"],
#       "key": openai_config["embeddings-key"],
#       "api-version": openai_config["embeddings-api-version"],
#   })
# elif openai_config["embeddings-client"] == "openai":
#   embeddings_client = setup_client("openai", { "key": openai_config["embeddings-key"] })
# else:
#   raise ValueError("Invalid embeddings client")

# cost_logger = OpenAICostLogger_Singleton(
#   experiment_name = openai_config["experiment-name"],
#   log_folder = DEFAULT_LOG_PATH,
#   cost_upperbound = openai_config["cost-upperbound"]
# )

BAgent = import_bagent()
backend = BAgent()

def temp_sleep(seconds=0.1):
  time.sleep(seconds)


def ChatGPT_single_request(prompt): 
  temp_sleep()
  # completion = client.chat.completions.create(
  #   model=openai_config["model"],
  #   messages=[{"role": "user", "content": prompt}]
  # )
  # return completion.choices[0].message.content
  return backend.query_model(prompt)


def ChatGPT_request(prompt): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  # temp_sleep()
  try: 
    # completion = client.chat.completions.create(
    # model=openai_config["model"],
    # messages=[{"role": "user", "content": prompt}]
    # )
    # return completion.choices[0].message.content
    return backend.query_model(prompt)
  
  except Exception as e: 
    print(f"Error: {e}")
    return "ChatGPT ERROR"


def ChatGPT_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
  prompt = '"""\n' + prompt + '\n"""\n'
  prompt += f"Output the response to the prompt above in json. {special_instruction}\n"
  prompt += "Example output json:\n"
  prompt += '{"output": "' + str(example_output) + '"}'

  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 

    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      end_index = curr_gpt_response.rfind('}') + 1
      curr_gpt_response = curr_gpt_response[:end_index]
      curr_gpt_response = json.loads(curr_gpt_response)["output"]
      
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      
      if verbose: 
        print ("---- repeat count: \n", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass

  return False


def ChatGPT_safe_generate_response_OLD(prompt, 
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
  if verbose: 
    print ("CHAT GPT PROMPT")
    print (prompt)

  for i in range(repeat): 
    try: 
      curr_gpt_response = ChatGPT_request(prompt).strip()
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print (f"---- repeat count: {i}")
        print (curr_gpt_response)
        print ("~~~~")

    except: 
      pass
  print ("FAIL SAFE TRIGGERED") 
  return fail_safe_response


def GPT_request(prompt, gpt_parameter): 
  """
  Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
  server and returns the response. 
  ARGS:
    prompt: a str prompt
    gpt_parameter: a python dictionary with the keys indicating the names of  
                   the parameter and the values indicating the parameter 
                   values.   
  RETURNS: 
    a str of GPT-3's response. 
  """
  temp_sleep()
  try: 
    messages = [{
      "role": "system", "content": prompt
    }]
    # response = client.chat.completions.create(
    #             model=gpt_parameter["engine"],
    #             messages=messages,
    #             temperature=gpt_parameter["temperature"],
    #             max_tokens=gpt_parameter["max_tokens"],
    #             top_p=gpt_parameter["top_p"],
    #             frequency_penalty=gpt_parameter["frequency_penalty"],
    #             presence_penalty=gpt_parameter["presence_penalty"],
    #             stream=gpt_parameter["stream"],
    #             stop=gpt_parameter["stop"],)
    # return response.choices[0].message.content
    return backend.query_model(prompt)
  except Exception as e:
    print(f"Error: {e}")
    return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file): 
  """
  Takes in the current input (e.g. comment that you want to classifiy) and 
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this 
  function replaces this substr with the actual curr_input to produce the 
  final promopt that will be sent to the GPT3 server. 
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file. 
  RETURNS: 
    a str prompt that will be sent to OpenAI's GPT server.  
  """
  if type(curr_input) == type("string"): 
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):   
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt: 
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()


def safe_generate_response(prompt, 
                           gpt_parameter,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None,
                           verbose=False): 
  if verbose: 
    print (prompt)

  for i in range(repeat): 
    curr_gpt_response = GPT_request(prompt, gpt_parameter)
    try:
      if func_validate(curr_gpt_response, prompt=prompt): 
        return func_clean_up(curr_gpt_response, prompt=prompt)
      if verbose: 
        print ("---- repeat count: ", i, curr_gpt_response)
        print (curr_gpt_response)
        print ("~~~~")
    except:
      pass
  return fail_safe_response


def get_embedding(text, model=openai_config["embeddings"]):
  # text = text.replace("\n", " ")
  # if not text: 
  #   text = "this is blank"
  # response = embeddings_client.embeddings.create(input=[text], model=model)
  # cost_logger.update_cost(response=response, input_cost=openai_config["embeddings-costs"]["input"], output_cost=openai_config["embeddings-costs"]["output"])
  # return response.data[0].embedding
  return None


if __name__ == '__main__':
  gpt_parameter = {"engine": openai_config["model"], "max_tokens": 50, 
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0, 
                   "stop": ['"']}
  curr_input = ["driving to a friend's house"]
  prompt_lib_file = "prompt_template/test_prompt_July5.txt"
  prompt = generate_prompt(curr_input, prompt_lib_file)

  def __func_validate(gpt_response): 
    if len(gpt_response.strip()) <= 1:
      return False
    if len(gpt_response.strip().split(" ")) > 1: 
      return False
    return True
  def __func_clean_up(gpt_response):
    cleaned_response = gpt_response.strip()
    return cleaned_response

  output = safe_generate_response(prompt, 
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

  print (output)


















