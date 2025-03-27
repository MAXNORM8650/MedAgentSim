from huggingface_hub import InferenceClient
messages = [{"role": "user", "content": "What is the capital of France?"}]
client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct")
client.chat_completion(messages, max_tokens=100)