import os
import json
from groq import Groq
from dotenv import load_dotenv
from core.personality import JARVIS_SYSTEM_PROMPT
from core.memory import save_memory, load_memory
from core.profile import load_profile

load_dotenv()

class JARVISEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("Sir, it appears the GROQ_API_KEY is missing from the environment. I cannot function without my core processors.")
        
        self.client = Groq(api_key=api_key)
        # Using Llama 3.3 70B as it is the most reliable current model on Groq
        self.model = "llama-3.3-70b-versatile" 
        
        profile = load_profile()
        personalized_prompt = f"{JARVIS_SYSTEM_PROMPT}\n\n### Current User Profile:\n{json.dumps(profile, indent=2)}"
        
        self.messages = [
            {"role": "system", "content": personalized_prompt}
        ]
        # Load previous memory
        history = load_memory()
        self.messages.extend(history)

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=1024,
            )
            
            assistant_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_response})
            
            # Save updated memory
            save_memory(self.messages)
            
            return assistant_response
        except Exception as e:
            return f"Sir, I've encountered a system error: {str(e)}"

    def clear_history(self):
        self.messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
        if os.path.exists("memory.json"):
            os.remove("memory.json")
