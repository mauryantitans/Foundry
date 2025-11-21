import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

class Agent:
    def __init__(self, name, instructions, tools=None, model_name="gemini-2.0-flash"):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model_name = model_name
        self.history = []
        
        # Configure the model
        self._configure_model()

    def _configure_model(self):
        # If tools are provided, convert them to the format expected by Gemini
        # Note: google-generativeai handles python functions directly in many cases,
        # but explicit tool declaration is safer for complex setups.
        # For simplicity here, we pass the functions directly if they are callables.
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools if self.tools else None,
            system_instruction=self.instructions
        )
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)

    def run(self, input_text):
        """Sends a message to the agent and returns the response."""
        print(f"🤖 {self.name} is thinking...")
        try:
            response = self.chat_session.send_message(input_text)
            return response.text
        except Exception as e:
            print(f"❌ Error in {self.name}: {e}")
            return f"Error: {e}"

    def reset(self):
        """Resets the chat history."""
        self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
