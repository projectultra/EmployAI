import requests

MODEL_ID = "Sammy1611/gemma-2b-it-quant"

# Replace with your Hugging Face API token
API_TOKEN = "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"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


output = query(
    {
        "inputs": "Write me a job description for a Machine Learning Engineer Job",
        "parameters": {"max_length": 50, "do_sample": True, "temperature": 70},
    }
)

print(output)
