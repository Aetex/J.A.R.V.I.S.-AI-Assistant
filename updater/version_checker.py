"""
Version Checker Module
Handles version detection and comparison for J.A.R.V.I.S. updates.
"""

import subprocess
import json
import os
from typing import Tuple, Optional


class VersionChecker:
    """Manages version checking and comparison operations."""
    
    def __init__(self, base_dir: str, repo_dir: str):
        self.base_dir = base_dir
        self.repo_dir = repo_dir
        self.package_json_path = os.path.join(base_dir, "ui", "package.json")
        self.repo_package_json_path = os.path.join(repo_dir, "ui", "package.json")
    
    def get_current_version(self) -> Optional[str]:
        """Get the current version from local package.json."""
        try:
            if os.path.exists(self.package_json_path):
                with open(self.package_json_path, 'r') as f:
                    data = json.load(f)
                    return data.get("version")
        except Exception as e:
            print(f"[WARN] Could not read current version: {e}")
        return None
    
    def get_latest_version(self) -> Optional[str]:
        """Get the latest version from repository package.json."""
        try:
            if os.path.exists(self.repo_package_json_path):
                with open(self.repo_package_json_path, 'r') as f:
                    data = json.load(f)
                    return data.get("version")
        except Exception as e:
            print(f"[WARN] Could not read latest version: {e}")
        return None
    
    def get_git_latest_tag(self) -> Optional[str]:
        """Get the latest git tag from the repository."""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"[WARN] Could not get git tag: {e}")
        return None
    
    def check_update_available(self) -> Tuple[bool, str, str]:
        """
        Check if an update is available.
        
        Returns:
            Tuple of (update_available, current_version, latest_version)
        """
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()
        
        if not current_version or not latest_version:
            print("[WARN] Could not determine versions, proceeding with update")
            return True, current_version or "unknown", latest_version or "unknown"
        
        if current_version == latest_version:
            print(f"[OK] Already up to date (version {current_version})")
            return False, current_version, latest_version
        
        print(f"[INFO] Update available: {current_version} -> {latest_version}")
        return True, current_version, latest_version
    
    def compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.
        
        Returns:
            -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
        """
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_part = v1_parts[i] if i < len(v1_parts) else 0
                v2_part = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_part < v2_part:
                    return -1
                elif v1_part > v2_part:
                    return 1
            
            return 0
        except Exception:
            # If version parsing fails, compare as strings
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            return 0
