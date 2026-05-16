from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.llm_client import JARVISEngine
from core.speech import JARVISSpeech
from core.stt import JARVISSTT
from core.wakeword import WakeWordDetector
from core.logger import setup_logger
from skills.volume_control import get_volume, set_volume
from contextlib import asynccontextmanager
import psutil
import asyncio
import json
import os
import threading
import time

setup_logger()

# Global state
is_listening = False
loop = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop = asyncio.get_event_loop()
    # Start wake word listener in background
    threading.Thread(target=run_wakeword_listener, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize JARVIS
jarvis = JARVISEngine()
speech = JARVISSpeech()
stt = JARVISSTT()
detector = WakeWordDetector()

def run_wakeword_listener():
    """Background thread to listen for the wake word."""
    global is_listening
    while True:
        if not is_listening:
            if detector.listen_for_keyword("jarvis"):
                print("[*] Wake word detected!")
                asyncio.run_coroutine_threadsafe(process_voice_command(), loop)
        time.sleep(0.1)

from sse_starlette.sse import EventSourceResponse

# Queue for UI events
events_queue = asyncio.Queue()

async def push_event(event_type: str, data: dict):
    await events_queue.put({"event": event_type, "data": json.dumps(data)})

@app.get("/events")
async def events_handler():
    async def event_generator():
        while True:
            event = await events_queue.get()
            yield event

    return EventSourceResponse(event_generator())

async def process_voice_command():
    global is_listening
    is_listening = True
    try:
        # 1. Notify UI we heard the wake word
        await push_event("wakeword", {"status": "detected"})
        
        # 2. Stop JARVIS if he's talking
        speech.stop()
        
        # 3. Start full transcription
        print("[*] Capturing command...")
        text = stt.listen_and_transcribe()
        
        if text:
            print(f"[*] Voice Command: {text}")
            await push_event("user_speech", {"text": text})
            
            # 4. Process with LLM
            response_data = await chat(ChatRequest(message=text))
            await push_event("jarvis_response", response_data)
            
    finally:
        is_listening = False

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tools_executed: list

@app.post("/stop")
async def stop_jarvis():
    """Stops JARVIS from talking."""
    stopped = speech.stop()
    return {"stopped": stopped}

@app.get("/listen")
async def listen_jarvis():
    """Triggers the microphone and transcribes user speech."""
    text = stt.listen_and_transcribe()
    return {"text": text}

@app.post("/shutdown")
async def shutdown_all():
    """Gracefully shuts down the system."""
    print("[*] Shutdown sequence initiated...")
    # Speak one last time before exiting
    asyncio.create_task(speech.speak("Powering down systems, sir. Goodnight."))
    # Increase delay to allow for long departure messages
    await asyncio.sleep(10) 
    os._exit(0)

@app.get("/status")
async def get_status():
    """Returns system status for the dashboard."""
    return {
        "volume": get_volume(),
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "online": True
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Processes a chat message and returns the response + tool logs."""
    try:
        response_text = jarvis.chat(request.message)
        
        # Parse for tool calls (similar to main.py logic)
        lines = response_text.split("\n")
        clean_text_lines = []
        tools_executed = []
        
        from main import execute_tool # Reuse execution logic
        
        for line in lines:
            if line.startswith("TOOL_CALL:"):
                try:
                    tool_json = line.replace("TOOL_CALL:", "").strip()
                    tool_data = json.loads(tool_json)
                    result = execute_tool(tool_data["name"], tool_data["args"])
                    tools_executed.append({"name": tool_data["name"], "result": result})
                    
                    if tool_data["name"] == "shutdown_system":
                        # Trigger shutdown after a short delay to let the response send
                        asyncio.create_task(shutdown_all())
                except Exception as e:
                    tools_executed.append({"name": "error", "result": str(e)})
            else:
                clean_text_lines.append(line)
        
        final_text = "\n".join(clean_text_lines).strip()
        
        # Failsafe: Trigger shutdown if the LLM says goodbye but forgets the tool call
        shutdown_keywords = ["*jarvis offline*", "shutting down systems", "goodnight, sir"]
        if any(kw in final_text.lower() for kw in shutdown_keywords):
            if not any(t["name"] == "shutdown_system" for t in tools_executed):
                print("[*] Failsafe: Shutdown keyword detected. Initiating power down...")
                tools_executed.append({"name": "shutdown_system", "result": "Failsafe triggered"})
                asyncio.create_task(shutdown_all())
        
        # Speak the response in the background
        asyncio.create_task(speech.speak(final_text))
        
        return {
            "response": final_text,
            "tools_executed": tools_executed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
