from pycaw.pycaw import AudioUtilities

def get_volume_interface():
    """Gets the volume control interface using the modern pycaw API."""
    devices = AudioUtilities.GetSpeakers()
    # The modern pycaw provides EndpointVolume directly on the device
    return devices.EndpointVolume

def set_volume(level: int):
    """Sets the system volume to a specific percentage (0-100)."""
    try:
        volume = get_volume_interface()
        # level is 0-100, pycaw expects 0.0 to 1.0 for scalar
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume: {str(e)}"

def get_volume():
    """Returns the current system volume percentage."""
    try:
        volume = get_volume_interface()
        current_level = volume.GetMasterVolumeLevelScalar()
        return int(current_level * 100)
    except Exception as e:
        return f"Error getting volume: {str(e)}"

def mute(state: bool):
    """Mutes or unmutes the system volume."""
    try:
        volume = get_volume_interface()
        volume.SetMute(1 if state else 0, None)
        return "System muted" if state else "System unmuted"
    except Exception as e:
        return f"Failed to mute: {str(e)}"

if __name__ == "__main__":
    # Quick test
    print(f"Current volume: {get_volume()}%")
