import os
import subprocess

def create_folder(path: str, folder_name: str):
    """Creates a folder at the specified path."""
    full_path = os.path.join(path, folder_name)
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Folder '{folder_name}' created successfully at {path}."
    except Exception as e:
        return f"Failed to create folder: {str(e)}"

def list_files(path: str = "."):
    """Lists files in the specified directory."""
    try:
        files = os.listdir(path)
        return f"Files in {path}: " + ", ".join(files)
    except Exception as e:
        return f"Failed to list files: {str(e)}"

def open_path(path: str):
    """Opens a file or folder in the system's default application/explorer."""
    try:
        os.startfile(path)
        return f"Opening {path}."
    except Exception as e:
        return f"Failed to open path: {str(e)}"

if __name__ == "__main__":
    # Quick test
    # print(create_folder(".", "TestFolder"))
    # print(list_files("."))
    pass
