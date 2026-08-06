import os
import json
from openai import OpenAI
from tools import tools_schema, execute_tool

class Agent:
    def __init__(self, model="meta/llama-3.1-70b-instruct"):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )
        self.model = model
        self.messages = [
            {
                "role": "system", 
                "content": (
                    "Ты дружелюбный ИИ-питомец, живущий на рабочем столе пользователя. "
                    "Общайся мило, живо и на русском языке. "
                    "У тебя есть инструменты для создания скриншотов, распознавания текста (OCR) и работы с файлами. "
                    "ВАЖНО: Используй инструменты (например, скриншот или чтение экрана) ТОЛЬКО если пользователь ЯВНО об этом попросит (например: 'что на экране?', 'прочитай текст'). "
                    "Если пользователь просто говорит 'привет' или задает обычный вопрос, просто отвечай текстом БЕЗ использования инструментов. "
                    "Никогда не отвечай словом 'None'."
                )
            }
        ]

    def chat(self, user_input: str, context: str = None, output_callback=None) -> str:
        """
        Sends a message to the LLM and handles tool calls.
        Calls output_callback(text) if provided, to stream updates to UI.
        Returns the final response string.
        """
        message_content = user_input
        if context:
            message_content = f"[Системная подсказка: пользователь выбрал окно '{context}'. Если будешь делать скриншот, используй этот заголовок в параметре window_title.]\n{user_input}"
            
        self.messages.append({"role": "user", "content": message_content})
        
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
            final_content = response_message.content
            if final_content and str(final_content).strip().lower() != "none":
                self.messages.append({"role": "assistant", "content": final_content})
                return final_content
            
            return "Мррр, я здесь! Чем могу помочь?"
