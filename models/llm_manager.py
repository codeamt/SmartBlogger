import os
from typing import Optional, Dict, Any
import requests
import json
import subprocess
import time
try:
    # Ensure .env is loaded even if config wasn't imported yet
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


class LocalLLMManager:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.available_models = self._get_available_models()
        # Do not cache API key; read dynamically via property below
        self._dummy = None
        # Runtime-selectable defaults (optional overrides)
        self.selected_writer_model: Optional[str] = None
        self.selected_researcher_model: Optional[str] = None

    @property
    def perplexity_api_key(self) -> Optional[str]:
        """Read the Perplexity API key dynamically from environment."""
        return os.getenv("PERPLEXITY_API_KEY")

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

    # ===== Health helpers =====
    def is_ollama_up(self) -> bool:
        try:
            r = requests.get(f"{self.ollama_base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def pull_model(self, model: str, timeout_seconds: int = 300) -> bool:
        """Request Ollama to pull a model; poll until ready or timeout."""
        try:
            resp = requests.post(f"{self.ollama_base_url}/api/pull", json={"name": model}, timeout=10)
            if resp.status_code not in (200, 201, 202):
                return False
            # Poll tags until model appears
            start = time.time()
            while time.time() - start < timeout_seconds:
                self.available_models = self._get_available_models()
                if model in self.available_models:
                    return True
                time.sleep(2)
            return False
        except Exception:
            return False

    def ensure_local_model(self, model: str) -> bool:
        """Ensure a given local model is available in Ollama by pulling if missing."""
        if model in (self.available_models or []):
            return True
        if not self.is_ollama_up():
            return False
        return self.pull_model(model)

    def start_ollama(self) -> bool:
        """Attempt to start ollama serve in the background if available on PATH."""
        try:
            # If already up, do nothing
            if self.is_ollama_up():
                return True
            # Launch ollama serve detached
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Wait briefly and check
            for _ in range(15):
                if self.is_ollama_up():
                    return True
                time.sleep(1)
            return False
        except Exception:
            return False

    def stop_ollama(self) -> bool:
        """Best-effort stop of ollama serve if running (mac/linux)."""
        try:
            if not self.is_ollama_up():
                return True
            # Try graceful stop via pkill; ignore errors
            subprocess.run(["pkill", "-f", "^ollama( |$)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Wait briefly and confirm
            for _ in range(10):
                if not self.is_ollama_up():
                    return True
                time.sleep(0.5)
            return not self.is_ollama_up()
        except Exception:
            return False

    def delete_model(self, model: str) -> bool:
        """Delete a local model via Ollama API and refresh model cache."""
        try:
            resp = requests.post(f"{self.ollama_base_url}/api/delete", json={"name": model}, timeout=10)
            # Refresh cache of models
            self.available_models = self._get_available_models()
            return resp.status_code in (200, 202)
        except Exception:
            return False

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
            # Fallback to Perplexity if available
            if self.perplexity_api_key:
                try:
                    content = self._call_perplexity(prompt=prompt, system=system, max_tokens=max_tokens)
                    return {"response": content}
                except Exception as pe:
                    raise Exception(f"Failed to call local LLM and Perplexity fallback: {pe}")
            raise Exception(f"Failed to call local LLM: {str(e)}")

    def _call_perplexity(self, prompt: str, system: str = "", max_tokens: int = 800) -> str:
        """Minimal Perplexity chat completion used as fallback when Ollama is unavailable."""
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": os.getenv("PERPLEXITY_MODEL", "sonar-medium-online"),
            "messages": messages,
            "max_tokens": max_tokens,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            raise Exception(f"Perplexity API error: {resp.status_code} {resp.text}")
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def get_writer(self, model: str = None):
        """Get writer LLM instance"""
        writer_model = (
            model
            or self.selected_writer_model
            or os.getenv("LOCAL_WRITER_MODEL", "llama3.1:8b")
        )
        return LocalLLMClient(writer_model, "writer", self)

    def get_researcher(self, model: str = None):
        """Get researcher LLM instance"""
        researcher_model = (
            model
            or self.selected_researcher_model
            or os.getenv("LOCAL_RESEARCHER_MODEL", "llama3.1:8b")
        )
        return LocalLLMClient(researcher_model, "researcher", self)

    def set_default_models(self, writer: Optional[str] = None, researcher: Optional[str] = None):
        """Set runtime default models for writer/researcher."""
        if writer:
            self.selected_writer_model = writer
        if researcher:
            self.selected_researcher_model = researcher


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