import os
from typing import Optional, Dict, Any
import requests
import json


class LocalLLMManager:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.available_models = self._get_available_models()

    def _get_available_models(self) -> list:
        """Get list of available local models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except:
            pass
        return []

    def _call_ollama(self, model: str, prompt: str, system: str = "",
                     temperature: float = 0.7, max_tokens: int = 4000) -> Dict[str, Any]:
        """Make API call to local Ollama instance"""
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to call local LLM: {str(e)}")

    def get_writer(self, model: str = None):
        """Get writer LLM instance"""
        writer_model = model or os.getenv("LOCAL_WRITER_MODEL", "llama3.1:8b")
        return LocalLLMClient(writer_model, "writer", self)

    def get_researcher(self, model: str = None):
        """Get researcher LLM instance"""
        researcher_model = model or os.getenv("LOCAL_RESEARCHER_MODEL", "llama3.1:8b")
        return LocalLLMClient(researcher_model, "researcher", self)


class LocalLLMClient:
    def __init__(self, model: str, role: str, manager: LocalLLMManager):
        self.model = model
        self.role = role
        self.manager = manager
        self.temperature = 0.7 if role == "writer" else 0.3
        self.max_tokens = 4000 if role == "writer" else 2000

    def invoke(self, messages):
        """Invoke the local LLM with messages"""
        # Convert LangChain message format to prompt
        if isinstance(messages, list):  # FIXED: message -> messages
            system_msg = ""
            human_msg = ""
            for msg in messages:
                if msg[0] == "system":
                    system_msg = msg[1]
                elif msg[0] == "human":
                    human_msg = msg[1]
            prompt = human_msg
            system = system_msg
        else:
            prompt = str(messages)  # FIXED: message -> messages
            system = ""

        response = self.manager._call_ollama(  # FIXED: _call_oliama -> _call_ollama
            model=self.model,
            prompt=prompt,
            system=system,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Create response object similar to LangChain
        class Response:
            def __init__(self, content, metadata):
                self.content = content
                self.response_metadata = metadata

        metadata = {
            "model": self.model,
            "token_usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.get("response", "").split()),
                "total_tokens": len(prompt.split()) + len(response.get("response", "").split())
            }
        }

        return Response(response.get("response", ""), metadata)


# Global instance
local_llm_manager = LocalLLMManager()