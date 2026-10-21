import requests, json
r = requests.get(
    'https://api.groq.com/openai/v1/models',
    headers={'Authorization': 'Bearer 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'}
)
data = r.json()
models = sorted(data.get('data', []), key=lambda x: x.get('created', 0), reverse=True)
print(f"Total: {len(models)} models\n")
for m in models:
    mid = m['id']
    ctx = m.get('context_window', '?')
    owner = m.get('owned_by', '?')
    print(f"  {mid}  |  ctx={ctx}  |  by={owner}")
