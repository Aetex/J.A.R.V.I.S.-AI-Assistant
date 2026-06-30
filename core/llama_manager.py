import os
import platform
import subprocess
import requests
import json
import shutil
import sys
from pathlib import Path

class LlamaManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.llama_dir = os.path.join(base_dir, "llama.cpp")
        self.models_dir = os.path.join(base_dir, "models")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.llama_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    def get_hardware_info(self):
        """Detect system hardware capabilities"""
        hardware = {
            "os": platform.system(),
            "architecture": platform.machine(),
            "cpu_cores": os.cpu_count(),
            "ram_gb": self._get_ram_gb(),
            "gpu_info": self._get_gpu_info(),
            "recommended_model": None
        }
        
        # Determine recommended model based on hardware
        hardware["recommended_model"] = self._recommend_model(hardware)
        
        return hardware
    
    def _get_ram_gb(self):
        """Get system RAM in GB"""
        try:
            if platform.system() == "Windows":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", c_ulonglong),
                        ("ullAvailPhys", c_ulonglong),
                        ("ullTotalPageFile", c_ulonglong),
                        ("ullAvailPageFile", c_ulonglong),
                        ("ullTotalVirtual", c_ulonglong),
                        ("ullAvailVirtual", c_ulonglong),
                        ("ullAvailExtendedVirtual", c_ulonglong),
                    ]
                memoryStatus = MEMORYSTATUSEX()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
                return round(memoryStatus.ullTotalPhys / (1024**3), 1)
            else:
                # Linux/Mac
                result = subprocess.run(['free', '-b'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    mem_line = [l for l in lines if l.startswith('Mem:')][0]
                    total_bytes = int(mem_line.split()[1])
                    return round(total_bytes / (1024**3), 1)
        except:
            return 8.0  # Default fallback
    
    def _get_gpu_info(self):
        """Get GPU information"""
        gpu_info = {"has_gpu": False, "gpu_name": None, "cuda_available": False}
        
        try:
            # Check for NVIDIA GPU
            if platform.system() == "Windows":
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = result.stdout.strip()
                    gpu_info["cuda_available"] = True
            else:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = result.stdout.strip()
                    gpu_info["cuda_available"] = True
        except:
            pass
        
        return gpu_info
    
    def _recommend_model(self, hardware):
        """Recommend a model based on hardware capabilities"""
        ram = hardware["ram_gb"]
        has_gpu = hardware["gpu_info"]["has_gpu"]
        
        # Model recommendations based on RAM and GPU
        if ram >= 32 and has_gpu:
            return {
                "name": "Llama-3.2-3B-Instruct-Q5_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q5_K_M.gguf",
                "size_gb": 2.3,
                "description": "Best quality for high-end systems with GPU acceleration"
            }
        elif ram >= 16:
            return {
                "name": "Llama-3.2-3B-Instruct-Q4_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "size_gb": 1.9,
                "description": "Balanced performance for mid-range systems"
            }
        elif ram >= 8:
            return {
                "name": "Phi-3-mini-4k-instruct-Q4_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q4_K_M.gguf",
                "size_gb": 1.2,
                "description": "Lightweight model for systems with 8GB RAM"
            }
        else:
            return {
                "name": "Phi-3-mini-4k-instruct-Q3_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q3_K_M.gguf",
                "size_gb": 0.9,
                "description": "Minimal model for low-end systems (may have reduced quality)"
            }
    
    def get_available_models(self):
        """Get list of available models from Hugging Face"""
        recommended_models = [
            {
                "name": "Llama-3.2-3B-Instruct-Q5_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q5_K_M.gguf",
                "size_gb": 2.3,
                "description": "Best quality for high-end systems",
                "recommended": True
            },
            {
                "name": "Llama-3.2-3B-Instruct-Q4_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "size_gb": 1.9,
                "description": "Balanced performance for mid-range systems",
                "recommended": True
            },
            {
                "name": "Phi-3-mini-4k-instruct-Q4_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q4_K_M.gguf",
                "size_gb": 1.2,
                "description": "Lightweight model for 8GB RAM systems",
                "recommended": True
            }
        ]
        
        # Add hardware-based recommendation
        hardware = self.get_hardware_info()
        for model in recommended_models:
            if model["name"] == hardware["recommended_model"]["name"]:
                model["recommended"] = "MAIN"
            else:
                model["recommended"] = model["recommended"] if model["recommended"] else False
        
        return recommended_models
    
    def get_downloaded_models(self):
        """Get list of downloaded models"""
        models = []
        if not os.path.exists(self.models_dir):
            return models
        
        for file in os.listdir(self.models_dir):
            if file.endswith('.gguf'):
                file_path = os.path.join(self.models_dir, file)
                size_gb = round(os.path.getsize(file_path) / (1024**3), 2)
                models.append({
                    "name": file.replace('.gguf', ''),
                    "file": file,
                    "path": file_path,
                    "size_gb": size_gb
                })
        
        return models
    
    def download_model(self, repo, filename, progress_callback=None):
        """Download a model from Hugging Face"""
        url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
        dest_path = os.path.join(self.models_dir, filename)
        
        if os.path.exists(dest_path):
            return {"success": True, "path": dest_path, "message": "Model already exists"}
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, downloaded, total_size)
            
            return {"success": True, "path": dest_path, "message": "Model downloaded successfully"}
            
        except Exception as e:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return {"success": False, "message": f"Download failed: {str(e)}"}
    
    def delete_model(self, filename):
        """Delete a downloaded model"""
        file_path = os.path.join(self.models_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"success": True, "message": "Model deleted successfully"}
        return {"success": False, "message": "Model not found"}
    
    def install_llama_cpp(self, progress_callback=None):
        """Download and install llama.cpp"""
        system = platform.system()
        architecture = platform.machine()
        
        # Determine the correct release URL
        if system == "Windows":
            if architecture == "AMD64":
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-win-avx2-x64.zip"
            else:
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-win-avx2-x64.zip"
        elif system == "Darwin":  # macOS
            if architecture == "arm64":
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-macos-arm64.zip"
            else:
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-macos-x64.zip"
        else:  # Linux
            url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-linux-avx2-x64.zip"
        
        try:
            # Download
            if progress_callback:
                progress_callback(10, "Downloading llama.cpp...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(self.llama_dir, "llama_cpp.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if progress_callback:
                progress_callback(50, "Extracting llama.cpp...")
            
            # Extract
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.llama_dir)
            
            # Clean up
            os.remove(zip_path)
            
            # Find and move the executable to the root of llama.cpp
            for root, dirs, files in os.walk(self.llama_dir):
                for file in files:
                    if file.startswith('llama-cli') or file.startswith('main'):
                        src = os.path.join(root, file)
                        dst = os.path.join(self.llama_dir, file)
                        shutil.move(src, dst)
            
            if progress_callback:
                progress_callback(100, "llama.cpp installed successfully")
            
            return {"success": True, "message": "llama.cpp installed successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Installation failed: {str(e)}"}
    
    def is_llama_cpp_installed(self):
        """Check if llama.cpp is installed"""
        system = platform.system()
        if system == "Windows":
            exe_name = "llama-cli.exe"
        else:
            exe_name = "llama-cli"
        
        exe_path = os.path.join(self.llama_dir, exe_name)
        return os.path.exists(exe_path)

if __name__ == "__main__":
    manager = LlamaManager()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    if command == "get_hardware_info":
        hardware = manager.get_hardware_info()
        print(json.dumps(hardware))
    elif command == "get_downloaded_models":
        models = manager.get_downloaded_models()
        print(json.dumps(models))
    elif command == "get_available_models":
        models = manager.get_available_models()
        print(json.dumps(models))
    elif command == "download_model":
        if len(sys.argv) < 4:
            print(json.dumps({"success": False, "message": "Missing repo or filename"}))
            sys.exit(1)
        
        repo = sys.argv[2]
        filename = sys.argv[3]
        
        def progress_callback(percentage, downloaded, total):
            print(f"PROGRESS: {json.dumps({'percentage': percentage, 'downloaded': downloaded, 'total': total})}")
        
        result = manager.download_model(repo, filename, progress_callback)
        print(json.dumps(result))
    elif command == "delete_model":
        if len(sys.argv) < 3:
            print(json.dumps({"success": False, "message": "Missing filename"}))
            sys.exit(1)
        
        filename = sys.argv[2]
        result = manager.delete_model(filename)
        print(json.dumps(result))
    else:
        print(json.dumps({"success": False, "message": "Unknown command"}))
        sys.exit(1)
    
    def get_hardware_info(self):
        """Detect system hardware capabilities"""
        hardware = {
            "os": platform.system(),
            "architecture": platform.machine(),
            "cpu_cores": os.cpu_count(),
            "ram_gb": self._get_ram_gb(),
            "gpu_info": self._get_gpu_info(),
            "recommended_model": None
        }
        
        # Determine recommended model based on hardware
        hardware["recommended_model"] = self._recommend_model(hardware)
        
        return hardware
    
    def _get_ram_gb(self):
        """Get system RAM in GB"""
        try:
            if platform.system() == "Windows":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", c_ulonglong),
                        ("ullAvailPhys", c_ulonglong),
                        ("ullTotalPageFile", c_ulonglong),
                        ("ullAvailPageFile", c_ulonglong),
                        ("ullTotalVirtual", c_ulonglong),
                        ("ullAvailVirtual", c_ulonglong),
                        ("ullAvailExtendedVirtual", c_ulonglong),
                    ]
                memoryStatus = MEMORYSTATUSEX()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
                return round(memoryStatus.ullTotalPhys / (1024**3), 1)
            else:
                # Linux/Mac
                result = subprocess.run(['free', '-b'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    mem_line = [l for l in lines if l.startswith('Mem:')][0]
                    total_bytes = int(mem_line.split()[1])
                    return round(total_bytes / (1024**3), 1)
        except:
            return 8.0  # Default fallback
    
    def _get_gpu_info(self):
        """Get GPU information"""
        gpu_info = {"has_gpu": False, "gpu_name": None, "cuda_available": False}
        
        try:
            # Check for NVIDIA GPU
            if platform.system() == "Windows":
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = result.stdout.strip()
                    gpu_info["cuda_available"] = True
            else:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_info["has_gpu"] = True
                    gpu_info["gpu_name"] = result.stdout.strip()
                    gpu_info["cuda_available"] = True
        except:
            pass
        
        return gpu_info
    
    def _recommend_model(self, hardware):
        """Recommend a model based on hardware capabilities"""
        ram = hardware["ram_gb"]
        has_gpu = hardware["gpu_info"]["has_gpu"]
        
        # Model recommendations based on RAM and GPU
        if ram >= 32 and has_gpu:
            return {
                "name": "Llama-3.2-3B-Instruct-Q5_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q5_K_M.gguf",
                "size_gb": 2.3,
                "description": "Best quality for high-end systems with GPU acceleration"
            }
        elif ram >= 16:
            return {
                "name": "Llama-3.2-3B-Instruct-Q4_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "size_gb": 1.9,
                "description": "Balanced performance for mid-range systems"
            }
        elif ram >= 8:
            return {
                "name": "Phi-3-mini-4k-instruct-Q4_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q4_K_M.gguf",
                "size_gb": 1.2,
                "description": "Lightweight model for systems with 8GB RAM"
            }
        else:
            return {
                "name": "Phi-3-mini-4k-instruct-Q3_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q3_K_M.gguf",
                "size_gb": 0.9,
                "description": "Minimal model for low-end systems (may have reduced quality)"
            }
    
    def get_available_models(self):
        """Get list of available models from Hugging Face"""
        recommended_models = [
            {
                "name": "Llama-3.2-3B-Instruct-Q5_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q5_K_M.gguf",
                "size_gb": 2.3,
                "description": "Best quality for high-end systems",
                "recommended": True
            },
            {
                "name": "Llama-3.2-3B-Instruct-Q4_K_M",
                "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
                "file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "size_gb": 1.9,
                "description": "Balanced performance for mid-range systems",
                "recommended": True
            },
            {
                "name": "Phi-3-mini-4k-instruct-Q4_K_M",
                "repo": "bartowski/Phi-3-mini-4k-instruct-GGUF",
                "file": "Phi-3-mini-4k-instruct-Q4_K_M.gguf",
                "size_gb": 1.2,
                "description": "Lightweight model for 8GB RAM systems",
                "recommended": True
            }
        ]
        
        # Add hardware-based recommendation
        hardware = self.get_hardware_info()
        for model in recommended_models:
            if model["name"] == hardware["recommended_model"]["name"]:
                model["recommended"] = "MAIN"
            else:
                model["recommended"] = model["recommended"] if model["recommended"] else False
        
        return recommended_models
    
    def get_downloaded_models(self):
        """Get list of downloaded models"""
        models = []
        if not os.path.exists(self.models_dir):
            return models
        
        for file in os.listdir(self.models_dir):
            if file.endswith('.gguf'):
                file_path = os.path.join(self.models_dir, file)
                size_gb = round(os.path.getsize(file_path) / (1024**3), 2)
                models.append({
                    "name": file.replace('.gguf', ''),
                    "file": file,
                    "path": file_path,
                    "size_gb": size_gb
                })
        
        return models
    
    def download_model(self, repo, filename, progress_callback=None):
        """Download a model from Hugging Face"""
        url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
        dest_path = os.path.join(self.models_dir, filename)
        
        if os.path.exists(dest_path):
            return {"success": True, "path": dest_path, "message": "Model already exists"}
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, downloaded, total_size)
            
            return {"success": True, "path": dest_path, "message": "Model downloaded successfully"}
            
        except Exception as e:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return {"success": False, "message": f"Download failed: {str(e)}"}
    
    def delete_model(self, filename):
        """Delete a downloaded model"""
        file_path = os.path.join(self.models_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"success": True, "message": "Model deleted successfully"}
        return {"success": False, "message": "Model not found"}
    
    def install_llama_cpp(self, progress_callback=None):
        """Download and install llama.cpp"""
        system = platform.system()
        architecture = platform.machine()
        
        # Determine the correct release URL
        if system == "Windows":
            if architecture == "AMD64":
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-win-avx2-x64.zip"
            else:
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-win-avx2-x64.zip"
        elif system == "Darwin":  # macOS
            if architecture == "arm64":
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-macos-arm64.zip"
            else:
                url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-macos-x64.zip"
        else:  # Linux
            url = "https://github.com/ggerganov/llama.cpp/releases/download/b3593/llama-b3593-bin-linux-avx2-x64.zip"
        
        try:
            # Download
            if progress_callback:
                progress_callback(10, "Downloading llama.cpp...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(self.llama_dir, "llama_cpp.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if progress_callback:
                progress_callback(50, "Extracting llama.cpp...")
            
            # Extract
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.llama_dir)
            
            # Clean up
            os.remove(zip_path)
            
            # Find and move the executable to the root of llama.cpp
            for root, dirs, files in os.walk(self.llama_dir):
                for file in files:
                    if file.startswith('llama-cli') or file.startswith('main'):
                        src = os.path.join(root, file)
                        dst = os.path.join(self.llama_dir, file)
                        shutil.move(src, dst)
            
            if progress_callback:
                progress_callback(100, "llama.cpp installed successfully")
            
            return {"success": True, "message": "llama.cpp installed successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Installation failed: {str(e)}"}
    
    def is_llama_cpp_installed(self):
        """Check if llama.cpp is installed"""
        system = platform.system()
        if system == "Windows":
            exe_name = "llama-cli.exe"
        else:
            exe_name = "llama-cli"
        
        exe_path = os.path.join(self.llama_dir, exe_name)
        return os.path.exists(exe_path)