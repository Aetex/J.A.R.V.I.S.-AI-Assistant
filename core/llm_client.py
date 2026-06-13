import os
import json
import requests
from groq import Groq
from google import genai
from dotenv import load_dotenv
from core.personality import JARVIS_SYSTEM_PROMPT
from core.memory import save_memory, load_memory
from core.profile import load_profile

load_dotenv()

class JARVISEngine:
    def __init__(self):
        self.groq_key = None
        self.google_key = None
        self.google_client = None
        self.client = None
        self.provider = None
        
        self.load_engines()
        
        profile = load_profile()
        self.system_prompt = f"{JARVIS_SYSTEM_PROMPT}\n\n### Current User Profile:\n{json.dumps(profile, indent=2)}"
        
        # Initialize memory
        self.messages = load_memory()
        if not self.messages:
            self.messages = [{"role": "system", "content": self.system_prompt}]

    def load_engines(self):
        """Dynamically loads or reloads the AI engines from environment configuration."""
        load_dotenv(override=True)
        
        # Re-fetch keys
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.lm_studio_enabled = os.getenv("LM_STUDIO_ENABLED", "").lower() in ("1", "true", "yes", "on")
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
        self.lm_studio_model = os.getenv("LM_STUDIO_MODEL", "local-model")
        
        # Determine provider and initialize clients accordingly
        if self.lm_studio_enabled:
            if self.provider != "lm_studio":
                print("[*] Initializing LM Studio Engine (Local OpenAI-Compatible API)...")
                print(f"[*] LM Studio Endpoint: {self.lm_studio_url}")
                print(f"[*] LM Studio Model: {self.lm_studio_model}")
            self.provider = "lm_studio"
        elif self.google_key and len(self.google_key) > 10 and not self.google_key.startswith("PASTE_YOUR_"):
            if self.provider != "gemini" or self.google_client is None:
                print("[*] Initializing Gemini Engine (Google GenAI SDK)...")
                self.google_client = genai.Client(api_key=self.google_key)
                
                # Diagnostic: Check available models
                try:
                    for m in self.google_client.models.list():
                        if "flash" in m.name.lower():
                            print(f"[*] Found Flash Model: {m.name}")
                except Exception as e:
                    print(f"[!] Warning: Could not list models: {e}")

                # Allow user to override model in .env, otherwise use the most stable latest flash
                self.model_name = os.getenv("GOOGLE_MODEL", "gemini-flash-latest")
                print(f"[*] Gemini Model Selected: {self.model_name}")
            self.provider = "gemini"
        elif self.groq_key and len(self.groq_key) > 10 and not self.groq_key.startswith("PASTE_YOUR_"):
            if self.provider != "groq" or self.client is None:
                print("[*] Initializing Groq Engine (Llama 3.3)...")
                self.client = Groq(api_key=self.groq_key)
                self.model_name = "llama-3.3-70b-versatile"
            self.provider = "groq"
        else:
            if self.provider is not None:
                print("[WARN] Engines disabled/reset: No active keys found.")
            self.provider = None

    def chat(self, user_input: str):
        # Reload configuration dynamically in case of updates
        self.load_engines()

        if not self.provider:
            return "Sir, I cannot process your request because no AI engine is configured. Please paste your API keys in the settings menu."

        if self.provider == "lm_studio":
            return self.call_lm_studio(user_input)
        elif self.provider == "gemini":
            print("[*] Attempting Gemini request...")
            response = self.call_gemini(user_input)
            
            # If Gemini hits a rate limit or not found, fall back to Groq as a fail-safe
            if "429" in response or "404" in response or "RESOURCE_EXHAUSTED" in response:
                if self.groq_key:
                    print("[!] Gemini Rate Limit/Error. Falling back to Groq fail-safe...")
                    return self.call_groq(user_input)
            return response
        else:
            return self.call_groq(user_input)

    def call_lm_studio(self, user_input: str):
        if not any(m["role"] == "system" for m in self.messages):
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})

        self.messages.append({"role": "user", "content": user_input})
        try:
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": self.lm_studio_model,
                    "messages": self.messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            assistant_response = data["choices"][0]["message"]["content"]
            self.messages.append({"role": "assistant", "content": assistant_response})
            save_memory(self.messages)
            return assistant_response
        except requests.exceptions.ConnectionError:
            self.messages.pop()
            return "Sir, LM Studio is not responding. Please open LM Studio, load a model, and start the local server."
        except Exception as e:
            self.messages.pop()
            return f"Sir, the local LM Studio core stumbled: {str(e)}"

    def call_groq(self, user_input: str):
        # Ensure we have the system prompt for the fallback
        if not any(m["role"] == "system" for m in self.messages):
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})
            
        self.messages.append({"role": "user", "content": user_input})
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.messages,
                temperature=0.7,
                max_tokens=1024,
            )
            assistant_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_response})
            save_memory(self.messages)
            return assistant_response
        except Exception as e:
            return f"Sir, even my fail-safe Groq processors are struggling: {str(e)}"

    def call_gemini(self, user_input: str):
        try:
            # New SDK usage
            response = self.google_client.models.generate_content(
                model=self.model_name,
                contents=f"{self.system_prompt}\n\nUser: {user_input}"
            )
            
            if not response.text:
                return "Sir, Gemini returned an empty response."
                
            assistant_response = response.text
            
            # Record in history
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": assistant_response})
            save_memory(self.messages)
            
            return assistant_response
        except Exception as e:
            error_msg = str(e)
            print(f"[!] Gemini Error: {error_msg}")
            return f"Gemini Error: {error_msg}"

    def clear_history(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]
        if os.path.exists("memory.json"):
            os.remove("memory.json")
