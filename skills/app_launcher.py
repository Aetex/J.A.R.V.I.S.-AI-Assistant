import subprocess
import os
import webbrowser

# Common Windows App mappings
APP_MAPPING = {
    "chrome": "chrome",
    "notepad": "notepad",
    "calculator": "calc",
    "spotify": "spotify",
    "code": "code",
    "explorer": "explorer"
}

def launch_app(app_name: str):
    """Launches an application by name or common alias."""
    app_lower = app_name.lower()
    
    # Special handling for browser
    if "browser" in app_lower or "chrome" in app_lower:
        try:
            webbrowser.open("https://www.google.com")
            return f"Opening your default browser, sir."
        except Exception as e:
            return f"I had trouble opening the browser: {str(e)}"

    executable = APP_MAPPING.get(app_lower, app_lower)
    
    try:
        # Use 'start' to let Windows handle finding the app in its registry/PATH
        subprocess.Popen(f"start {executable}", shell=True)
        return f"Initiating {app_name}, sir."
    except Exception as e:
        return f"I'm afraid I couldn't launch {app_name}. Error: {str(e)}"

if __name__ == "__main__":
    # print(launch_app("notepad"))
    pass
