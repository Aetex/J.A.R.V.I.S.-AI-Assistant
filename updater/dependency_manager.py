"""
Dependency Manager Module
Handles smart dependency updates with change detection.
"""

import subprocess
import os
import hashlib
from typing import Tuple, Optional


class DependencyManager:
    """Manages dependency updates with change detection."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.requirements_path = os.path.join(base_dir, "requirements.txt")
        self.package_json_path = os.path.join(base_dir, "ui", "package.json")
        self.hash_file = os.path.join(base_dir, "backup", "dependency_hashes.json")
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate MD5 hash of a file."""
        try:
            if not os.path.exists(file_path):
                return None
            
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
            
        except Exception as e:
            print(f"[WARN] Could not calculate hash for {file_path}: {e}")
            return None
    
    def _load_hashes(self) -> dict:
        """Load stored file hashes."""
        try:
            import json
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load hashes: {e}")
        return {}
    
    def _save_hashes(self, hashes: dict) -> Tuple[bool, str]:
        """Save file hashes."""
        try:
            import json
            os.makedirs(os.path.dirname(self.hash_file), exist_ok=True)
            with open(self.hash_file, 'w') as f:
                json.dump(hashes, f, indent=2)
            return True, "Hashes saved"
        except Exception as e:
            error_msg = f"Could not save hashes: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def _requirements_changed(self) -> bool:
        """Check if requirements.txt has changed."""
        current_hash = self._calculate_file_hash(self.requirements_path)
        if not current_hash:
            return True  # If we can't calculate hash, assume changed
        
        stored_hashes = self._load_hashes()
        stored_hash = stored_hashes.get("requirements.txt")
        
        return current_hash != stored_hash
    
    def _package_json_changed(self) -> bool:
        """Check if package.json has changed."""
        current_hash = self._calculate_file_hash(self.package_json_path)
        if not current_hash:
            return True  # If we can't calculate hash, assume changed
        
        stored_hashes = self._load_hashes()
        stored_hash = stored_hashes.get("package.json")
        
        return current_hash != stored_hash
    
    def update_python_dependencies(self, force: bool = False) -> Tuple[bool, str]:
        """
        Update Python dependencies if requirements.txt has changed.
        
        Args:
            force: Force update even if file hasn't changed
            
        Returns:
            Tuple of (success, message)
        """
        if not os.path.exists(self.requirements_path):
            return True, "No requirements.txt found, skipping Python dependencies"
        
        if not force and not self._requirements_changed():
            print("[OK] requirements.txt unchanged, skipping pip install")
            return True, "Python dependencies unchanged"
        
        print("[*] Updating Python dependencies...")
        pip_path = os.path.join(self.base_dir, "venv", "Scripts", "pip.exe")
        
        # Try to find pip in venv, fallback to system pip
        if not os.path.exists(pip_path):
            pip_path = "pip"
        
        try:
            result = subprocess.run(
                [pip_path, "install", "-r", self.requirements_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                error_msg = f"Pip install failed: {result.stderr}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg
            
            # Update hash after successful install
            current_hash = self._calculate_file_hash(self.requirements_path)
            if current_hash:
                hashes = self._load_hashes()
                hashes["requirements.txt"] = current_hash
                self._save_hashes(hashes)
            
            print("[OK] Python dependencies updated")
            return True, "Python dependencies updated"
            
        except subprocess.TimeoutExpired:
            error_msg = "Pip install timed out"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Pip install failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def update_ui_dependencies(self, force: bool = False) -> Tuple[bool, str]:
        """
        Update UI dependencies if package.json has changed.
        
        Args:
            force: Force update even if file hasn't changed
            
        Returns:
            Tuple of (success, message)
        """
        ui_dir = os.path.join(self.base_dir, "ui")
        package_json_path = os.path.join(ui_dir, "package.json")
        
        if not os.path.exists(package_json_path):
            return True, "No package.json found, skipping UI dependencies"
        
        if not force and not self._package_json_changed():
            print("[OK] package.json unchanged, skipping npm install")
            return True, "UI dependencies unchanged"
        
        print("[*] Updating UI dependencies...")
        
        # Check if npm is available
        try:
            npm_check = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if npm_check.returncode != 0:
                print("[WARN] npm not found, skipping UI dependency updates")
                return True, "npm not found, skipping UI dependencies"
        except Exception as e:
            print(f"[WARN] npm not available, skipping UI dependency updates: {e}")
            return True, "npm not available, skipping UI dependencies"
        
        try:
            result = subprocess.run(
                ["npm", "install", "--silent"],
                cwd=ui_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                error_msg = f"Npm install failed: {result.stderr}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg
            
            # Update hash after successful install
            current_hash = self._calculate_file_hash(package_json_path)
            if current_hash:
                hashes = self._load_hashes()
                hashes["package.json"] = current_hash
                self._save_hashes(hashes)
            
            print("[OK] UI dependencies updated")
            return True, "UI dependencies updated"
            
        except subprocess.TimeoutExpired:
            error_msg = "Npm install timed out"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Npm install failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def update_all_dependencies(self, force: bool = False) -> Tuple[bool, str]:
        """
        Update all dependencies (Python and UI).
        
        Args:
            force: Force update even if files haven't changed
            
        Returns:
            Tuple of (success, message)
        """
        print("[*] Checking dependencies...")
        
        py_success, py_msg = self.update_python_dependencies(force)
        ui_success, ui_msg = self.update_ui_dependencies(force)
        
        if py_success and ui_success:
            return True, "All dependencies updated"
        elif not py_success and not ui_success:
            return False, f"Both dependency updates failed: {py_msg}, {ui_msg}"
        elif not py_success:
            return False, f"Python dependency update failed: {py_msg}"
        else:
            return False, f"UI dependency update failed: {ui_msg}"
    
    def reset_hashes(self) -> Tuple[bool, str]:
        """
        Reset stored hashes to force updates on next run.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if os.path.exists(self.hash_file):
                os.remove(self.hash_file)
            return True, "Dependency hashes reset"
        except Exception as e:
            error_msg = f"Failed to reset hashes: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
