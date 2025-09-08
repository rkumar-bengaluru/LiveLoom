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
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    timeout: int = 30
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return self.model
        
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