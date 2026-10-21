import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("[Error] GROQ_API_KEY not found in .env file.")
    exit(1)

r = requests.get(
    'https://api.groq.com/openai/v1/models',
    headers={'Authorization': f'Bearer {api_key}'}
)
data = r.json()
models = sorted(data.get('data', []), key=lambda x: x.get('created', 0), reverse=True)
print(f"Total: {len(models)} models available on Groq LPU:\n")
for m in models:
    mid = m.get('id', '')
    ctx = m.get('context_window', '?')
    owner = m.get('owned_by', '?')
    print(f"  {mid:<48} | ctx={ctx:<8} | by={owner}")

