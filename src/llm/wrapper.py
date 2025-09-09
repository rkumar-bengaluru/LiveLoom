# llm wrapper .py
from __future__ import annotations
import os
from typing import Any, List, Optional
import requests
from langchain.llms.base import LLM
from pydantic import BaseModel
import json 
import queue  

class LLMWrapper(LLM):
    """LangChain LLM base-class wrapper for Google Gemini (OpenAI-compatible)."""

    model: Optional[str]  = None
    api_key: Optional[str] = None
    api_url: str 
    answer_queue: queue.Queue 
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    timeout: int = 30
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return self.model
    
    def _call_stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Core synchronous call required by LLM base."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "n": 1,
            "stream": True,
            # "extra_body": {
            #     "google": {
            #         "thinking_config": {
            #             "thinking_budget": 0
            #         }
            #     }
            # }  
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if stop:
            payload["stop"] = stop
        
        # resp = requests.post(
        #     self.api_url,
        #     headers=headers,
        #     json=payload,
        #     timeout=self.timeout,
        # )
        # resp.raise_for_status()
        stream = True
        full_response = ""
        if stream:
           with requests.post(self.api_url, headers=headers, json=payload, stream=True) as r:
                for line in r.iter_lines(decode_unicode=True):
                    if not line:                      # skip keep-alive
                        continue
                    if line == "data: [DONE]":        # upstream done
                        self.answer_queue.put("data: [DONE]")
                        break
                    if line.startswith("data: "):
                        chunk = json.loads(line[6:])  # remove "data: " prefix
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        self.answer_queue.put(content)
                        full_response += content
        return full_response
    
    def _call(self, prompt: str, stop=None) -> str:
        try:
            # print("prompt--", prompt)
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",  # Valid Groq model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7,  # Valid float32 value
                    "n": 1  # Must be 1 for Groq
                }
            )
            response.raise_for_status()  # Raises exception for 4xx/5xx errors
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP Error: {e.response.status_code} - {e.response.text}"
            raise Exception(error_message)
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    # LangChain ≥ 0.2 uses `invoke`; delegate to `_call` for compatibility
    def invoke(
        self,
        input: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        return self._call(input, stop=stop, **kwargs)