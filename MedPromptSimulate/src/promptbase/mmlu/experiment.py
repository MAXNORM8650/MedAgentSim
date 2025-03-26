import traceback
from functools import partial
import re

import torch

from .problem_utils import *
from .utils import openai_configs, run_batch_jobs, text_completion

from .mmlu_paths import mmlu_generations_dir
from .globals import record, experience

from tqdm import tqdm

import openai
import replicate
import anthropic
import gzip

from groq import Groq

# URLs for replicate models
LLAMA2_URL = "meta/llama-2-70b-chat"
LLAMA3_URL = "meta/meta-llama-3-70b-instruct"
MIXTRAL_URL = "mistralai/mixtral-8x7b-instruct-v0.1"

# from problem_utils import *
# from utils import openai_configs, run_batch_jobs, text_completion

# from mmlu_paths import mmlu_generations_dir
# from globals import record, experience

def prepare_options(options, subset_type="train"):
    # Set experiment name
    if "name" not in options:
        if type(options["problems"]) is not str or "/" in options["problems"]:
            raise "You need to set the experiment name."
        name = f"{options['problems']}/{options['prompt_name']}"
        if options.get("example_selector", "") == "knn":
            name += "_knn"
        if "embedding_map" in options:
            name += "_weighted"
        options["name"] = name

    if (
        mmlu_generations_dir / f"expt/{options['name']}"
    ).exists():
        if ("ignore_check" in options):
            if (options["ignore_check"] == False):
                confirm = input(
                    f"Are you sure you want to overwrite the content in {options['name']}? (y/n): "
                )
                if confirm.lower() != "y":
                    print("########################### IGNORED ###########################")
                    quit()
            # else:
            #     quit()
        else:
            confirm = input(
                f"Are you sure you want to overwrite the content in {options['name']}? (y/n): "
            )
            if confirm.lower() != "y":
                print("########################### IGNORED ###########################")
                quit()
            
        # else:
        #     quit()

    if "log_file" not in options:
        options["log_file"] = str(
            mmlu_generations_dir / f"expt" / f"{options['name']}" / "log.md"
        )
        os.makedirs(os.path.dirname(options["log_file"]), exist_ok=True)
        if os.path.exists(options["log_file"]):
            os.remove(options["log_file"])

    # Load problems
    if type(options["problems"]) is str:
        options["problems_name"] = options["problems"]
        options["problems"] = [options["problems"]]

    if type(options["problems"]) is list and type(options["problems"][0]) is str:
        print("Loading problems...")
        problems = []
        for problem_name in options["problems"]:
            problems += load_problems(problem_name, subset_type)
        options["problems"] = problems

    # Load embedding
    if (
        type(options.get("embedding_map", "")) is bool
        and options["embedding_map"] == True
    ):
        options["embedding_map"] = torch.load("data/matrix_v7_2048dim.pt").cpu()

    if options.get("example_selector", "") in ["knn", "svm"]:
        options["embedding_map"] = torch.eye(1536).cpu()

    # Load examples
    if "examples" not in options:
        options["examples"] = []

    if type(options["examples"]) is str:
        print("Loading examples...")
        examples = load_solutions(options["examples"], options, subset_type)

        options["examples"] = [
            example for example in examples if len(example["solution"]) > 0
        ]
        # print(len(options["examples"]))

        # options["examples"] = [
        #     json.load(gzip.open(example, "rt", encoding="utf-8"))  # Extract JSON
        #     for example in examples
        #     if len(json.load(gzip.open(example, "rt", encoding="utf-8"))["solution"]) > 0  # Ensure "solution" is not empty
        # ]

        # options["examples"] = []
        # print(type(examples))
        # print(f"EXAMPLES LEN: {len(examples)}")
        # print(examples)

        #.json.gz
        # for example in eval(examples):
        #     print(f"Processing: {example}")  # Print the filename

        #     with gzip.open(f"{example}.json.gz", "rt", encoding="utf-8") as gz_file:
        #         json_data = json.load(gz_file)  # Extract JSON content

        #     if len(json_data.get("solution", "")) > 0:  # Ensure "solution" exists and is not empty
        #         options["examples"].append(json_data)
        
    ############################### NEEDS TO BE ABLE TO LOAD PROBLEMS FROM A LIST OF FILES################################
    """elif isinstance(options["examples"], list):
        print("Loading examples as list...")
        all_examples = []
        for example_file in options["examples"]:
            examples = load_solutions(example_file, options)
            all_examples.extend(examples)

        # Filter examples with non-empty solutions
        options["examples"] = [
            example for example in all_examples if len(example["solution"]) > 0
    ]"""
#############################################################################################################################


    if options.get("example_selector", "") in ["knn", "svm"]:
        temp_examples = []
        for i in range(len(options["examples"])):
            example = options["examples"][i]
            print(f"Processing: example {i}")  # Print the filename

            with gzip.open(f"{example}.json.gz", "rt", encoding="utf-8") as gz_file:
                json_data = json.load(gz_file)[0]  # Extract JSON content

            # if "embedding" in json_data:  # Ensure "embedding" exists and is not empty
            temp_examples.append(json_data)

        options["examples"] = temp_examples
        print(len(options["examples"]))

        # examples_tensor = (
        #     torch.cat(
        #         [
        #             torch.tensor(d["embedding"], dtype=torch.float32).unsqueeze(0)
        #             for d in options["examples"]
        #         ]
        #     ).cpu()
        #     @ options["embedding_map"]
        # )
        options["examples"] = {
            "problems": options["examples"],
            # "tensor": examples_tensor,
        }

    # defaults settings
    if "example_selector" not in options and len(options["examples"]) > 0:
        options["example_selector"] = "random"

    # debug settings
    if "debug" in options and options["debug"]:
        options["max_questions"] = 20
        options["num_repeat"] = 2

    if (
        "max_questions" in options
        and len(options["problems"]) > options["max_questions"]
    ):
        random.shuffle(options["problems"])
        options["problems"] = options["problems"][: options["max_questions"]]


def has_common_k_gram(str1, str2, k):
    def generate_k_grams(s, k):
        if len(s) <= k:
            return {s}
        else:
            return {s[i : i + k] for i in range(len(s) - k)}

    str1_k_grams = generate_k_grams(str1, k)
    str2_k_grams = generate_k_grams(str2, k)

    return not str1_k_grams.isdisjoint(str2_k_grams)


def query_model(model_str: str,
                prompt: str,
                system_prompt: str,
                tries: int = 1,
                timeout: float = 30.0,
                image_requested: bool = False,
                scene=None,
                max_prompt_len: int = 2 ** 14,
                clip_prompt: bool = False):
    """
    Queries the specified language model with the given prompt and system prompt.
    Retries the query if an exception occurs.
    """
    # Initialize Groq client
    # client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    for _ in tqdm(range(tries), desc="Querying model"):
        # Optionally clip prompt length
        if clip_prompt:
            prompt = prompt[:max_prompt_len]

        try:
            answer = None

            # --- Handle image requests first ---
            if image_requested:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"{scene.image_url}"}}
                    ]},
                ]
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
                answer = response["choices"][0]["message"]["content"]

            # --- Handle text-only requests ---
            elif model_str in ["gpt4", "gpt4v", "gpt-4o-mini", "gpt4o", "gpt3.5"]:
                model_map = {
                    "gpt4": "gpt-4-turbo-preview",
                    "gpt4v": "gpt-4-vision-preview",
                    "gpt-4o-mini": "gpt-4o-mini",
                    "gpt4o": "gpt-4o",
                    "gpt3.5": "gpt-3.5-turbo",
                }
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                response = openai.ChatCompletion.create(
                    model=model_map[model_str],
                    messages=messages,
                    temperature=0.05,
                    max_tokens=200,
                )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub(r"\s+", " ", answer)

            elif model_str == "o1-preview":
                messages = [{"role": "user", "content": system_prompt + prompt}]
                response = openai.ChatCompletion.create(
                    model="o1-preview-2024-09-12",
                    messages=messages,
                )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub(r"\s+", " ", answer)

            elif model_str == "claude3.5sonnet":
                client_anthropic = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
                message = client_anthropic.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    system=system_prompt,
                    max_tokens=256,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = json.loads(message.to_json())["content"][0]["text"]

            elif model_str == "meta/llama-3.1-405b-instruct":
                from openai import OpenAI  # Assuming OpenAI integration for this model
                client_nvidia = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key="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"
                )
                response = client_nvidia.chat.completions.create(
                    model="meta/llama-3.1-405b-instruct",
                    messages=[{"role": "user", "content": "Write a limerick about the wonders of GPU computing."}],
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024,
                    stream=True
                )
                answer = response["choices"][0]["message"]["content"]
                answer = re.sub(r"\s+", " ", answer)

            elif model_str == 'llama-2-70b-chat':
                output = replicate.run(LLAMA2_URL, input={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_new_tokens": 200
                })
                answer = ''.join(output)
                answer = re.sub(r"\s+", " ", answer)

            elif model_str == 'mixtral-8x7b':
                output = replicate.run(MIXTRAL_URL, input={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_new_tokens": 75
                })
                answer = ''.join(output)
                answer = re.sub(r"\s+", " ", answer)

            elif model_str == 'llama-3-70b-instruct':
                output = replicate.run(LLAMA3_URL, input={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_new_tokens": 200
                })
                answer = ''.join(output)
                answer = re.sub(r"\s+", " ", answer)

            elif "GR_" in model_str:
                # For Groq-backed models, remove the prefix and use the Groq client.
                model = model_str.replace("GR_", "")
                chat_completion = openai.ChatCompletion.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    model=model,
                )
                answer = chat_completion.choices[0].message.content
                answer = re.sub(r"\s+", " ", answer)

            else:
                # Fallback to the baseline agent if none of the above match.
                output = replicate.run(MIXTRAL_URL, input={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_new_tokens": 75
                })
                answer = ''.join(output)
                answer = re.sub(r"\s+", " ", answer)

            return answer

        except Exception as e:
            time.sleep(timeout)
            continue


def solve(options, problem, add=None, switch=0, backend=None):
    global record, experience
    prompt_tokens = 0
    completion_tokens = 0
    calls = 0
    name = f"{options['name']}/{options['order']}"
    model = options.get("model", "gpt-4-1106-preview")
    set_order(problem, options["order"])
    print(f"Problem Before################################################: {problem}")
    print("Options Before#################################################: ", options)


    for retry in range(options.get("max_retry", 3)):
        if "example_selector" not in options:
            selected_examples = []
        elif options["example_selector"] in ["random", "knn", "svm"]:
            # if options["example_selector"] in ["knn", "svm"]:
            #     options["problem_embedding"] = (
            #         torch.tensor(problem["embedding"], dtype=torch.float32)
            #         .cpu()
            #         .unsqueeze(0)
            #         @ options["embedding_map"]
            #     )
            selected_examples = select_examples(
                problem, options["examples"], "random", options
            )
        else:
            raise f"Unsupported example_selector: {options['example_selector']}"

        # just some safety check to avoid leaking the answer
        selected_examples = [
            example
            for example in selected_examples
            if example["question"].strip() != problem["question"].strip()
        ]

        if options.get("balance_answer", False):
            assert options["response_type"] in ["decreasing_order", "MC"]
            target_choices = multiple_random_order(
                problem["order"], len(selected_examples)
            )
            for example, target_choice in zip(selected_examples, target_choices):
                result = parse_response(
                    {"order": problem["order"]},
                    {"text": example["answer"]},
                    options["response_type"],
                    False,
                )
                if result is None:
                    continue
                if type(result) is tuple:
                    result = result[0]
                result = result[-1]
                if result == target_choice:
                    continue

                # This is a really bad code here...I assumed the question format.
                assert (
                    f"\n{target_choice}. " in example["question"]
                    and f"\n{result}. " in example["question"]
                )

                example["question"] = (
                    example["question"]
                    .replace(f"\n{target_choice}. ", f"\nTMP. ")
                    .replace(f"\n{result}. ", f"\n{target_choice}. ")
                    .replace(f"\nTMP. ", f"\n{result}. ")
                )
                example["answer"] = (
                    example["answer"]
                    .replace(f"[{target_choice}]", f"[TMP]")
                    .replace(f"[{result}]", f"[{target_choice}]")
                    .replace(f"[TMP]", f"[{result}]")
                )

                example["question"] = reorder_question(example["question"])

        assessments = {}
        if "assessment" in assessments:
            for letter in problem["order"]:
                option = problem["answer_choices"][letter]
                prompt = options["assessment"].render(
                    question=problem["question"], option=option
                )
                response = text_completion(
                    prompt=prompt,
                    temperature=0,
                    max_tokens=300 + retry * 200,
                    stop=["<|diff_marker|>", "\n#"],
                    log_file=options["log_file"],
                )
                if response["success"]:
                    assessments[letter] = response["text"].strip(" \n")
                    # prompt_tokens += response["response"]["usage"]["prompt_tokens"]
                    # completion_tokens += response["response"]["usage"][
                    #     "completion_tokens"
                    # ]
                    calls += 1

        prompt = options["prompt"].render(
            question=problem["description"],
            examples=selected_examples,
            assessments=assessments,
        )
        print("prompt ###############################3PROMPT!!!!!!!!!!!!!!!", prompt)
        ###############################
        #@amrin: I have added the following code block to add LEAP principles/insights to the prompt based on the switch variable
        if switch == 1:
            prompt += add ######USE GENERATED INSIGHTS TO RE-PROMPT AND STORE EXPERIENCE###
        ###############################

        if options["response_type"] in ["logprobs", "letter"]:
            max_tokens = 1
        else:
            max_tokens = 500 + retry * 200

        if (not backend is None):
            sys_prompt = "Please note the exam question has an unique answer based on the information given. Include Answer: [X] at the end where X must be A, B, C, or D."
            response = {"response": None, "text": backend.query_model(prompt, sys_prompt), "success": True}
            print(f"RESPONSE: {response}")
        elif openai_configs.models[model]["type"] == "chat":
            prompt_splits = re.split("## Q|## A", prompt)
            messages = []
            for prompt_split in prompt_splits:
                if prompt_split.startswith("uestion"):
                    content = prompt_split[len("uestion") :].strip()
                    messages.append({"role": "user", "content": content})
                elif prompt_split.startswith("nswer"):
                    content = prompt_split[len("nswer") :].strip()
                    if content == "":
                        continue
                    messages.append({"role": "assistant", "content": content})
            if "## Rank the options from most likely to least likely" in prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": "Please answer the above question in the same style as the examples above. Include the answer and the rank as the examples above.",
                    }
                )
            else:
                messages.append(
                    {
                        "role": "system",
                        "content": "Please note the exam question has an unique answer based on the information given. Include Answer: [X] at the end where X must be A, B, C, or D.",
                    }
                )
            response = text_completion(
                model=model,
                prompt=messages,
                temperature=0.05 * retry,
                max_tokens=max_tokens,
                log_file=options["log_file"],
            )
        else:
            response = text_completion(
                model=model,
                prompt=prompt,
                temperature=0.05 * retry,
                max_tokens=max_tokens,
                logprobs=10,
                stop=["<|diff_marker|>", "## Question"],
                log_file=options["log_file"],
            )

        if response["success"]:
            # prompt_tokens += response["response"]["usage"]["prompt_tokens"]
            # completion_tokens += response["response"]["usage"]["completion_tokens"]
            calls += 1
            result = parse_response(problem, response, options["response_type"])
            if result is not None:
                with open(options["log_file"], "a") as f:
                    f.write(
                        f"########## Answer ##########\n{problem['correct_answer']} (GPT answer: {result})\n"
                    )
                break
            else:
                with open(options["log_file"], "a") as f:
                    f.write(
                        f"########## Invalid Answer ##########\n{problem['correct_answer']} (GPT answer: {response['text']})\n"
                    )

    if "expt" not in problem:
        problem["expt"] = {}

    output = {
        "prompt": prompt,
        "response": response["text"],
        "api_calls": calls,
        "tokens_used_prompt": prompt_tokens,
        "tokens_used_completion": completion_tokens,
    }

    if type(result) == tuple:
        output["result"] = result[0]
        output["scores"] = result[1]
    else:
        output["result"] = result

    if type(output["result"]) is str and len(output["result"]) >= 1:
        output["answer"] = output["result"][-1]
    else:
        output["answer"] = None

    problem["expt"][name] = output
    print("PROBLEM AFTER ......................................................", problem)
    ###############################################################################################################                              
    #BEWARE: THE FOLLOWING CODE BLOCK IS A MODIFIED VERSION OF THE ORIGINAL CODE BLOCK IN THE MMLU EXPERIMENT.PY
    #@amrin: I have added the following code block to save the results to medical record library and experience base separately
    ############# EXPERIENCE BASE #############   
    if switch == 0:
        if problem['correct_answer']==output['answer']: #is there another way to check?
            save_problem(
                str(mmlu_generations_dir / f"expt" / f"{options['name']}" / "result"),
                options["problems"],
            ) 
            record = record + 1
            
        else:
            #reflection phase
            reflect_phase(options, problem, output, model) 
    #####################MEDICAL RECORD LIBRARY#####################  
    elif switch ==1:
        if problem['correct_answer']==output['answer']: #is there another way to check?
            save_problem(
                str(mmlu_generations_dir / f"expt" / f"{options['name']}" / "experience"),
                options["problems"],
            )  # save results regularly
            experience = experience + 1
        
        else:
            #ABORT
            print("Consultation not successful.")
        switch=0
    ################################################################################################################

def reflect_phase(options, problem, output, model):
    switch = 1

    correct_reasoning = {
        "A": "To diagnose appendicitis consider the following criteria: General symptoms usually include pain around the naval that shifts to the right lower quadrant (RLQ) of the abdomen, accompanied by fever and nausea or vomiting. During a physical examination, a patient might show RLQ tenderness, positive rebound tenderness, or signs of peritonitis. Laboratory tests may reveal signs of an inflammatory response, such as an elevated white blood cell count and elevated C-reactive protein levels. Imaging may disclose an enlarged appendix or possibly an appendicolith.",
        "B": "To diagnose cholecystitis, consider the following criteria: General symptoms usually include pain in the right upper quadrant (RUQ) of the abdomen, fever, and nausea. During a physical examination, a patient might display RUQ tenderness or indications of jaundice. Laboratory tests may reveal signs of inflammation, such as elevated white blood cell count and C-reactive protein levels, liver damage, indicated through heightened Alanine Aminotransferase (ALT) or Asparate Aminotransferase (AST) levels, or gallbladder damage, indicated through heightened Bilirubin or Gamma Glutamyltransferase levels. Imaging may show gallstones, thickened gallbladder walls, pericholecystic fluid, and a distended gallbladder.",
        "C": "To diagnose diverticulitis consider the following criteria: General symptoms typically encompass abdominal pain, primarily in the left lower quadrant (LLQ), along with fever, and nausea or vomiting. During a physical examination, a patient may display tenderness in the LLQ, fever, and signs of peritonitis. Laboratory tests often reveal signs of inflammation and infection, which may include an elevated white blood cell count and elevated C-reactive protein levels. Imaging findings often include bowel wall thickening, diverticula, inflammation, or abscesses around the affected segment of the colon.",
        "D": "To diagnose pancreatitis consider the following criteria: General symptoms usually include abdominal pain, primarily in the epigastric region, along with nausea or vomiting. During a physical examination, a patient might display epigastric tenderness, fever, and signs of jaundice. Laboratory tests may reveal signs of inflammation, such as elevated white blood cell count and C-reactive protein levels, and pancreatic damage, indicated through heightened Amylase or Lipase levels. Further lab tests of hematocrit, urea nitrogen, triglycerides, calcium, sodium and potassium can indicate the severity of the disease. Imaging may show inflammation of the pancreas or fluid collection."
    }
     ###############INSIGHT OR PRINCIPLE GENERATION PROMPT TEMPLATE###############
    message = f"""Question: {problem['question']} 
    Generated Reasoning: {output['response']}
    Generated Answer: {output['answer']}
    Correct Reasoning: {correct_reasoning[problem['correct_answer']]} 
    Correct Answer: {problem['correct_answer']} 
    Instruction: Conduct a thorough analysis of the generated answer in comparison to the correct answer. Also observe how the generated reasoning differs from the correct reasoning. Identify any discrepancies, misunderstandings, or errors. Provide clear insights, principles, or guidelines that can be derived from this analysis to improve future responses. We are not focused on this one data point, but rather on the general principle. 
    Reasoning: <discuss why the generated answer is wrong> 
    Insights: <what principle should be looked at carefully to improve the performance in the future>"""

    response = text_completion(
        model=model,
        prompt=message,
        temperature=0.05,
        max_tokens=500,
        log_file=options["log_file"],
    )

    if response["success"]:
        add = response["text"]
        solve(options, problem, add, switch)



def run_experiment(options, subset_type="train", backend=None):
    
    prepare_options(options, subset_type)
    try:
        used_order = ["ACDB", "ADBC", "BCDA", "CBAD", "CDAB"]
        for _ in range(options.get("num_repeat", 5)):
            if options.get("reorder", True):
                order = random_order(options.get("options", "ABCDEFGHIJ"), used_order)
            else:
                order = f"ABCDEFGHIJ{random_order('KLMNOPQRST', used_order)}"  # TODO: cleanup file naming
            used_order.append(order)
            options["order"] = order

            #####################CONVERT TO ONE-BY-ONE#####################
            run_batch_jobs(
                partial(solve, options, backend=backend),
                options["problems"],
                max_thread=options.get("max_thread", 30),
            )
            ################################################################

            # summary = compute_statistics(options["problems"])
            # if options.get("verbose", True):
            #     print(summary)
            
            

        # with open("summary.md", "a") as f:
        #     f.write(summary)
        #     f.write(f"\n{'=' * 80}\n")
    except KeyboardInterrupt:
        quit()
    except:
        traceback.print_exc()
