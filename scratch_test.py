import os
from openai import OpenAI
from tools import tools_schema

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)
messages = [
    {"role": "system", "content": "You are a helpful AI assistant. Answer normally in Russian."},
    {"role": "user", "content": "привет"}
]
response = client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=messages,
    tools=tools_schema,
    temperature=0.2,
    max_tokens=1024,
)
print("Content:", repr(response.choices[0].message.content))
print("Tool calls:", response.choices[0].message.tool_calls)
