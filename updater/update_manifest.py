"""
Update Manifest Module
Handles tracking and management of update history and metadata.
"""

import json
import os
from datetime import datetime
from typing import Tuple, Optional, List


class UpdateManifest:
    """Manages update manifest and history tracking."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.manifest_file = os.path.join(base_dir, "backup", "update_manifest.json")
    
    def _load_manifest(self) -> dict:
        """Load the update manifest."""
        try:
            if os.path.exists(self.manifest_file):
                with open(self.manifest_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load manifest: {e}")
        
        # Return default manifest structure
        return {
            "current_version": None,
            "last_update": None,
            "update_history": []
        }
    
    def _save_manifest(self, manifest: dict) -> Tuple[bool, str]:
        """Save the update manifest."""
        try:
            os.makedirs(os.path.dirname(self.manifest_file), exist_ok=True)
            with open(self.manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            return True, "Manifest saved"
        except Exception as e:
            error_msg = f"Could not save manifest: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def record_update_start(self, from_version: str, to_version: str) -> Tuple[bool, str]:
        """
        Record the start of an update operation.
        
        Args:
            from_version: Current version before update
            to_version: Target version after update
            
        Returns:
            Tuple of (success, message)
        """
        try:
            manifest = self._load_manifest()
            
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "from_version": from_version,
                "to_version": to_version,
                "status": "in_progress",
                "backup_used": None
            }
            
            manifest["update_history"].insert(0, update_entry)
            manifest["current_update"] = update_entry
            
            return self._save_manifest(manifest)
            
        except Exception as e:
            error_msg = f"Failed to record update start: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def record_update_complete(self, backup_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Record successful completion of an update.
        
        Args:
            backup_path: Path to backup used for this update
            
        Returns:
            Tuple of (success, message)
        """
        try:
            manifest = self._load_manifest()
            
            if "current_update" in manifest:
                manifest["current_update"]["status"] = "complete"
                manifest["current_update"]["complete_timestamp"] = datetime.now().isoformat()
                if backup_path:
                    manifest["current_update"]["backup_used"] = backup_path
                
                # Move to history
                manifest["update_history"][0] = manifest["current_update"]
                del manifest["current_update"]
                
                # Update current version
                if manifest["update_history"]:
                    manifest["current_version"] = manifest["update_history"][0]["to_version"]
                    manifest["last_update"] = manifest["update_history"][0]["complete_timestamp"]
                
                return self._save_manifest(manifest)
            
            return True, "No current update found"
            
        except Exception as e:
            error_msg = f"Failed to record update complete: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def record_update_failed(self, error_message: str) -> Tuple[bool, str]:
        """
        Record a failed update attempt.
        
        Args:
            error_message: Description of the failure
            
        Returns:
            Tuple of (success, message)
        """
        try:
            manifest = self._load_manifest()
            
            if "current_update" in manifest:
                manifest["current_update"]["status"] = "failed"
                manifest["current_update"]["failed_timestamp"] = datetime.now().isoformat()
                manifest["current_update"]["error"] = error_message
                
                # Move to history
                manifest["update_history"][0] = manifest["current_update"]
                del manifest["current_update"]
                
                return self._save_manifest(manifest)
            
            return True, "No current update found"
            
        except Exception as e:
            error_msg = f"Failed to record update failure: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def get_current_version(self) -> Optional[str]:
        """Get the current recorded version."""
        manifest = self._load_manifest()
        return manifest.get("current_version")
    
    def get_last_update_time(self) -> Optional[str]:
        """Get the last update timestamp."""
        manifest = self._load_manifest()
        return manifest.get("last_update")
    
    def get_update_history(self, limit: int = 10) -> List[dict]:
        """
        Get recent update history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of update entries
        """
        manifest = self._load_manifest()
        history = manifest.get("update_history", [])
        return history[:limit]
    
    def get_failed_updates(self) -> List[dict]:
        """Get list of failed update attempts."""
        history = self.get_update_history(limit=100)
        return [entry for entry in history if entry.get("status") == "failed"]
    
    def cleanup_old_history(self, keep_count: int = 20) -> Tuple[int, str]:
        """
        Remove old update history entries.
        
        Args:
            keep_count: Number of recent entries to keep
            
        Returns:
            Tuple of (removed_count, message)
        """
        try:
            manifest = self._load_manifest()
            history = manifest.get("update_history", [])
            
            if len(history) <= keep_count:
                return 0, "No old history to remove"
            
            removed_count = len(history) - keep_count
            manifest["update_history"] = history[:keep_count]
            
            self._save_manifest(manifest)
            print(f"[OK] Removed {removed_count} old history entries")
            
            return removed_count, f"Removed {removed_count} old history entries"
            
        except Exception as e:
            error_msg = f"Failed to cleanup history: {e}"
            print(f"[ERROR] {error_msg}")
            return 0, error_msg
    
    def get_update_statistics(self) -> dict:
        """Get statistics about update history."""
        history = self.get_update_history(limit=1000)
        
        total_updates = len(history)
        successful_updates = len([e for e in history if e.get("status") == "complete"])
        failed_updates = len([e for e in history if e.get("status") == "failed"])
        
        return {
            "total_updates": total_updates,
            "successful_updates": successful_updates,
            "failed_updates": failed_updates,
            "success_rate": (successful_updates / total_updates * 100) if total_updates > 0 else 0,
            "current_version": self.get_current_version(),
            "last_update": self.get_last_update_time()
        }
