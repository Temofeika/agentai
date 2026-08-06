import os
from openai import OpenAI

try:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

    completion = client.chat.completions.create(
      model="meta/llama-3.1-70b-instruct",
      messages=[{"role":"user","content":"Respond with 'OK'"}],
      temperature=0.2,
      top_p=0.7,
      max_tokens=10,
    )

    print("Success:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)
