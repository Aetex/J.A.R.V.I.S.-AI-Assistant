import json
import os

PROFILE_FILE = "user_profile.json"

DEFAULT_PROFILE = {
    "name": "Sir",
    "preferences": {},
    "last_interaction": ""
}

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_PROFILE

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def update_user_name(name):
    profile = load_profile()
    profile["name"] = name
    save_profile(profile)
    return f"I shall address you as {name} from now on."
