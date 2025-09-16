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
        language = "Golang"
        prompt = PromptTemplate(
            input_variables=["question", "language"],
            template=(
                    "You are given a transcript extracted from an audio recording. "
                    "This transcript may contain irrelevant discussion or non-technical content.\n\n "
                    "Your task is to:\n"
                    "1. Identify and extract the most relevant technical question from the transcript below.\n"
                    "2. Determine whether the question is theoretical(e.g., concept explanation) or practical (e.g., requires code).\n"
                    "3. If theoretical, provide a clear and concise explanation.\n" 
                    "4. If practical, provide a concise, correct code solution in {language}.\n"
                    "If no language is mentioned or it's unclear, default to Python.\n\n"
                    "Transcript:\n{question}\n\n"
                    "Respond in the following format:\n"
                    "Question: <extracted question>\n"
                    "Answer:\n```{language}\n<code here>\n```"
            )
        )
        
        # prompt = PromptTemplate(
        #         input_variables=["input"],
        #         template="Respond to this user message: {input}"
        # )

        if self.app.settings.is_steaming() == 1:
            with timer() as t:
                response = self.llm._call_stream(prompt.format(question=input_text, language=language))
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
    

