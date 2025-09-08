from langchain.prompts import PromptTemplate
from langchain.agents import Tool
import threading
import time 
import os


# Chat Module (v1)
class ChatModule():
    def __init__(self, llm, app):
        self.llm = llm
        self.app = app

    def chat_with_llm(self, input_text):
        
        prompt = PromptTemplate(
                input_variables=["input"],
                template="Respond to this user message: {input}"
        )

        if self.app.settings.is_steaming() == 1:
            self.llm._call_stream(prompt.format(input=input_text))
        else:
            response = self.llm(prompt.format(input=input_text))
            self.app.answer_queue.put(response)
    

