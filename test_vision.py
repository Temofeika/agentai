import base64
from openai import OpenAI

def test_vision():
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )
    img_data = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.2-90b-vision-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_data.decode('utf-8')}"}}
                    ]
                }
            ],
            max_tokens=100
        )
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_vision()
