import psutil
import platform
import datetime

def get_system_summary():
    """Returns a comprehensive summary of the system health and info."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    # Battery info (if laptop)
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}" if battery else "N/A"

    summary = (
        f"System OS: {platform.system()} {platform.release()}\n"
        f"CPU Load: {cpu_usage}%\n"
        f"Memory Usage: {memory.percent}% ({memory.used // (1024**2)} MB / {memory.total // (1024**2)} MB)\n"
        f"Disk Space: {disk.percent}% free\n"
        f"Battery: {battery_status}\n"
        f"System Boot Time: {boot_time}"
    )
    return summary

if __name__ == "__main__":
    print(get_system_summary())
