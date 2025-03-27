import openai, re, random, time, json, replicate, os
import anthropic
from transformers import pipeline
def query_model(model_str, prompt, system_prompt, tries=30, timeout=20.0, image_requested=False, scene=None, max_prompt_len=2**14, clip_prompt=False):
    if model_str not in ["gpt4", "gpt3.5", "gpt4o", 'llama-2-70b-chat', "mixtral-8x7b", "gpt-4o-mini", "llama-3-70b-instruct", "gpt4v", "claude3.5sonnet", "o1-preview"] and "_HF" not in model_str:
        raise Exception("No model by the name {}".format(model_str))
    for _ in range(tries):
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
                answer = response["choices"][0]["message"]["content"]
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
            elif model_str == 'llama-3-70b-instruct':
                output = replicate.run(
                    llama3_url, input={
                        "prompt":  prompt, 
                        "system_prompt": system_prompt,
                        "max_new_tokens": 200})
                answer = ''.join(output)
                answer = re.sub("\s+", " ", answer)
            elif "HF_" in model_str:
                input_text = system_prompt + prompt 
                #if self.pipe is None:
                #    self.pipe = load_huggingface_model(self.backend.replace("HF_", ""))
                raise Exception("Sorry, fixing TODO :3") #inference_huggingface(input_text, self.pipe)
            return answer
        
        except Exception as e:
            time.sleep(timeout)
            continue
    raise Exception("Max retries: timeout")

