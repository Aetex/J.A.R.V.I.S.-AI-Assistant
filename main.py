import json
import sys
import os
import asyncio
from core.llm_client import JARVISEngine
from core.speech import JARVISSpeech
from skills.volume_control import set_volume, get_volume, mute
from skills.file_manager import create_folder, list_files, open_path
from skills.app_launcher import launch_app
from skills.system_info import get_system_summary
from skills.web_search import web_search

def execute_tool(tool_name, args):
    """Maps tool names from the LLM to actual python functions."""
    if tool_name == "set_volume":
        return set_volume(args.get("level", 50))
    elif tool_name == "create_folder":
        path = args.get("path", os.getcwd())
        return create_folder(path, args.get("folder_name", "New Folder"))
    elif tool_name == "launch_app":
        return launch_app(args.get("app_name", ""))
    elif tool_name == "list_files":
        path = args.get("path", os.getcwd())
        return list_files(path)
    elif tool_name == "get_system_summary":
        return get_system_summary()
    elif tool_name == "web_search":
        return web_search(args.get("query", ""))
    elif tool_name == "shutdown_system":
        # We'll trigger this via the backend logic
        return "Shutting down systems, sir. Goodnight."
    elif tool_name == "open_debug_console":
        os.system('start "JARVIS Debug Console" cmd /k "powershell Get-Content jarvis.log -Wait"')
        return "Opening debugging console, sir. All system logs are now being streamed."
    elif tool_name == "close_debug_console":
        os.system('taskkill /F /FI "WINDOWTITLE eq JARVIS Debug Console*"')
        return "Terminating debug console, sir. Normal operational parameters restored."
    else:
        return f"Tool {tool_name} is not recognized, sir."

async def main():
    try:
        jarvis = JARVISEngine()
        speech = JARVISSpeech()
        print("--- J.A.R.V.I.S. ONLINE ---")
        welcome_msg = "At your service, sir. Systems are fully operational."
        print(f"JARVIS: {welcome_msg}")
        # Only speak welcome if the user just started (optional)
        # await speech.speak(welcome_msg)
    except Exception as e:
        print(f"ERROR: {e}")
        return

    while True:
        try:
            # We use loop.run_in_executor for input to not block the event loop
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, "\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "goodnight jarvis"]:
                msg = "Goodnight, sir. Systems powering down."
                print(f"JARVIS: {msg}")
                await speech.speak(msg)
                break
            
            response = jarvis.chat(user_input)
            
            # Parse response for tool calls
            lines = response.split("\n")
            clean_text_lines = []
            
            for line in lines:
                if line.startswith("TOOL_CALL:"):
                    try:
                        tool_json = line.replace("TOOL_CALL:", "").strip()
                        tool_data = json.loads(tool_json)
                        result = execute_tool(tool_data["name"], tool_data["args"])
                        print(f"[*] Executing {tool_data['name']}... {result}")
                    except Exception as e:
                        print(f"[*] Error executing tool: {e}")
                else:
                    clean_text_lines.append(line)
            
            final_text = "\n".join(clean_text_lines).strip()
            if final_text:
                print(f"JARVIS: {final_text}")
                # Use speech engine to speak the response
                await speech.speak(final_text)
                
        except KeyboardInterrupt:
            print("\nJARVIS: Goodbye, sir.")
            break
        except Exception as e:
            print(f"JARVIS: I've encountered an unexpected error, sir: {e}")

if __name__ == "__main__":
    asyncio.run(main())
