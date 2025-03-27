"""
query_model.py
---------------
This module provides the query_model() function, which abstracts the logic for querying different
language model backends (e.g., OpenAI, Anthropic, Replicate, and Groq). It uses a retry loop with a timeout.
"""

import os
import time
import re
import json
import random
from tqdm import tqdm

import openai
import replicate
import anthropic

from groq import Groq

# URLs for replicate models
LLAMA2_URL = "meta/llama-2-70b-chat"
LLAMA3_URL = "meta/meta-llama-3-70b-instruct"
MIXTRAL_URL = "mistralai/mixtral-8x7b-instruct-v0.1"

import time
import requests
import logging
from transformers import pipeline, AutoConfig, AutoModel, AutoTokenizer
import json

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BAgent:
    def __init__(self, model_name="mistralai/Mistral-Small-24B-Instruct-2501", server_url="http://10.127.30.115:8000/v1/completions"):
        """
        Initializes the BAgent:
        - Uses vLLM server if available.
        - Otherwise, loads the model locally.
        """
        self.server_url = server_url
        self.model_name = model_name
        self.use_server = self._check_server()
        print(f"Using vLLM server: {self.use_server}")

        if not self.use_server:
            self._load_model()
        else:
            logger.info(f"Using vLLM server at {self.server_url}, skipping local model loading.")

    def _check_server(self):
        """Checks if the vLLM server is running."""
        try:
            response = requests.get(self.server_url.replace("/v1/chat/completions", "/health"), timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _load_model(self):
        """Loads the model locally if no vLLM server is found."""
        logger.info("Loading model and tokenizer locally...")
        try:
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                device_map="auto",
                trust_remote_code=True
            )
            logger.info("Model loaded successfully.")
        except ValueError as e:
            if "Unknown quantization type" in str(e):
                logger.warning("Quantization not supported. Loading without quantization...")
                try:
                    config = AutoConfig.from_pretrained(self.model_name, trust_remote_code=True)
                    if hasattr(config, "quantization_config"):
                        delattr(config, "quantization_config")

                    model = AutoModel.from_pretrained(self.model_name, config=config, device_map="auto", trust_remote_code=True)
                    tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                    self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto", trust_remote_code=True)
                    logger.info("Model loaded successfully without quantization.")
                except Exception as e:
                    logger.error(f"Failed to load model without quantization: {e}")
                    raise
            else:
                logger.error(f"Unexpected error during model loading: {e}")
                raise

    def query_model(self, prompt, system_prompt="You are a helpful assistant.", tries=5, timeout=5.0, image_requested=False, scene=None, max_prompt_len=2500, clip_prompt=False, thread_id=1):
        """Queries the vLLM server if available, otherwise uses local model."""
        if self.use_server:
            return self._query_server(prompt, system_prompt, tries, timeout)
        return self._query_local(prompt, system_prompt, image_requested, scene, max_prompt_len, clip_prompt, tries, timeout)

    def _query_server(self, user_prompt, system_prompt, tries=10, timeout=20.0) -> str:
        """
        Queries the vLLM model endpoint with system and user prompts.
        Returns the generated text.
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 200 # Control response length
        }

        headers = {"Content-Type": "application/json"}

        for attempt in range(tries):
            try:
                response = requests.post(self.server_url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                response_data = response.json()

                # Introduce a short delay to avoid rate limits
                time.sleep(2.0)

                # Return the generated response
                return response_data["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Server query attempt {attempt + 1} failed: {e}")
                time.sleep(timeout)

        logger.error("Max retries exceeded: Unable to fetch response from server.")
        return "Error: Failed to fetch response from server."

    def _query_local(self, prompt, system_prompt, image_requested=False, scene=None, max_prompt_len=2500, clip_prompt=False, tries=3, timeout=5.0):
        """Uses the locally loaded model to generate responses."""
        for attempt in range(tries):
            try:
                if clip_prompt:
                    prompt = prompt[:max_prompt_len]

                if image_requested:
                    if scene is None or not hasattr(scene, 'image_url'):
                        raise ValueError("Image requested but no scene or image_url provided.")
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": scene.image_url}}
                        ]}
                    ]
                else:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]

                outputs = self.pipeline(
                    messages,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                return outputs[0]['generated_text'][-1]['content']
            except Exception as e:
                logger.warning(f"Local query attempt {attempt + 1} failed: {e}")
                time.sleep(timeout)

        logger.error("Max retries exceeded: Unable to generate response from local model.")
        return "Error: Failed to generate response from local model."
    def _query_server_wot_system_prompt(self, user_prompt, tries=5, timeout=15.0) -> str:
        """
        Queries the vLLM model endpoint with only the user prompt.
        Returns the generated text.
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 80  # Control response length
        }

        headers = {"Content-Type": "application/json"}

        for attempt in range(tries):
            try:
                response = requests.post(self.server_url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                response_data = response.json()

                # Introduce a short delay to avoid rate limits
                time.sleep(2.0)

                # Return the generated response
                return response_data["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Server query attempt {attempt + 1} failed: {e}")
                time.sleep(timeout)

        logger.error("Max retries exceeded: Unable to fetch response from server.")
        return "Error: Failed to fetch response from server."
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
                    # messages = self.build_messages(system_prompt, shuffled_prompt, image_requested, scene)

                    # Use the pipeline to generate the response
                    # breakpoint()
                    outputs = self._query_server(shuffled_prompt, system_prompt, tries, timeout)#self._query_server_wot_system_prompt(messages)
                    responses.append(outputs)

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

fallback_agent = BAgent()

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
                chat_completion = client.chat.completions.create(
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
                answer = fallback_agent.query_model(prompt, system_prompt)

            return answer

        except Exception as e:
            time.sleep(timeout)
            continue

    raise Exception("Max retries exceeded: timeout")
# Example Usage
if __name__ == "__main__":
    agent = BAgent()
    response = agent.query_model("Hello! How are you?")
    print("Response:", response)