import os
import json
from groq import Groq
from google import genai
from dotenv import load_dotenv
from core.personality import JARVIS_SYSTEM_PROMPT
from core.memory import save_memory, load_memory
from core.profile import load_profile

load_dotenv()

class JARVISEngine:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        
        # Determine provider
        if self.google_key and len(self.google_key) > 10:
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
        elif self.groq_key:
            print("[*] Initializing Groq Engine (Llama 3.3)...")
            self.client = Groq(api_key=self.groq_key)
            self.model_name = "llama-3.3-70b-versatile"
            self.provider = "groq"
        else:
            raise ValueError("Sir, it appears no API keys are found in the environment. I cannot function without my core processors.")
        
        profile = load_profile()
        self.system_prompt = f"{JARVIS_SYSTEM_PROMPT}\n\n### Current User Profile:\n{json.dumps(profile, indent=2)}"
        
        # Initialize memory
        self.messages = load_memory()
        if not self.messages:
            self.messages = [{"role": "system", "content": self.system_prompt}]

    def chat(self, user_input: str):
        # Always try Gemini first if available
        if self.provider == "gemini":
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
