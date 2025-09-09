from langchain.prompts import PromptTemplate
from langchain.agents import Tool
import threading
import time 
import os

from src.utils.perf import timer 


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
            with timer() as t:
                response = self.llm._call_stream(prompt.format(input=input_text))
            exec_time = (t[1] - t[0]) * 1000
            self.app.answer_queue.put(f"llm exec time : {exec_time}")
            self.app.session.log_interaction(input_text, response, exec_time,self.llm.model)
        else:
            with timer() as t:
                response = self.llm(prompt.format(input=input_text))
                self.app.answer_queue.put(response)
            exec_time = (t[1] - t[0]) * 1000
            self.app.answer_queue.put(f"llm exec time : {exec_time}")
            self.app.session.log_interaction(input_text, response, exec_time,self.llm.model)
    

