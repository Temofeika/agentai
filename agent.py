import os
import json
from openai import OpenAI
from tools import tools_schema, execute_tool

class Agent:
    def __init__(self, model="meta/llama3-70b-instruct"):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        self.model = model
        self.messages = [
            {"role": "system", "content": "You are a helpful desktop AI assistant in the form of a virtual pet. You can answer questions, analyze the user's screen, read text via OCR, convert PDFs, Words and Excel files. When a user asks what's on the screen, use the recognize_text_from_screen tool."}
        ]

    def chat(self, user_input: str, output_callback=None) -> str:
        """
        Sends a message to the LLM and handles tool calls.
        Calls output_callback(text) if provided, to stream updates to UI.
        Returns the final response string.
        """
        self.messages.append({"role": "user", "content": user_input})
        
        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)
        
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=tools_schema,
                    temperature=0.2,
                    max_tokens=1024,
                )
            except Exception as e:
                err = f"API Error: {e}"
                log(err)
                return err

            response_message = response.choices[0].message
            
            # If the model wants to call tools
            if response_message.tool_calls:
                self.messages.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        function_args = {}
                    
                    log(f"*[Thinking]* Calling tool: {function_name}...")
                    
                    # Execute tool
                    tool_result = execute_tool(function_name, function_args)
                    log(f"*[Tool Finished]* {function_name}")
                    
                    # Add result to messages
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })
                
                # Loop back to model with tool outputs
                continue
            
            # No more tool calls, we have a final answer
            if response_message.content:
                self.messages.append({"role": "assistant", "content": response_message.content})
                return response_message.content
            
            return "Done."
