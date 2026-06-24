"""
J.A.R.V.I.S. Updater
A comprehensive updater system with version detection, backup, rollback, 
smart dependency management, and automatic restart capabilities.
"""

import subprocess
import shutil
import os
import sys
from typing import Tuple, Optional

# Add the base directory to path for imports
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Import updater modules
from updater.version_checker import VersionChecker
from updater.backup_manager import BackupManager
from updater.rollback import RollbackManager
from updater.dependency_manager import DependencyManager
from updater.update_manifest import UpdateManifest


class JARVISUpdater:
    """Main updater class for J.A.R.V.I.S."""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.repo_dir = os.path.join(self.base_dir, "Github", "J.A.R.V.I.S.-AI-Assistant")
        
        # Initialize modules
        self.version_checker = VersionChecker(self.base_dir, self.repo_dir)
        self.backup_manager = BackupManager(self.base_dir)
        self.rollback_manager = RollbackManager(self.base_dir, self.backup_manager)
        self.dependency_manager = DependencyManager(self.base_dir)
        self.update_manifest = UpdateManifest(self.base_dir)
        
        # Configuration
        self.ignored_items = {
            ".git",
            "venv",
            "node_modules",
            "voice",
            ".env",
            "memory.json",
            "jarvis.log",
            "Github",
            "__pycache__"
        }
    
    def run_git_pull(self) -> Tuple[bool, str]:
        """
        Run git pull to fetch latest changes.
        
        Returns:
            Tuple of (success, message)
        """
        print(f"[*] Running git pull in {self.repo_dir}...")
        
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                error_msg = f"Git pull failed: {result.stderr}"
                print(f"[ERROR] {error_msg}")
                return False, error_msg
            
            print("[OK] Git pull completed.")
            return True, "Git pull completed"
            
        except subprocess.TimeoutExpired:
            error_msg = "Git pull timed out"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Git pull failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def synchronize_files(self) -> Tuple[bool, str]:
        """
        Synchronize files from repository to base directory.
        
        Returns:
            Tuple of (success, message)
        """
        print("[*] Synchronizing files...")
        
        try:
            # Recursive copy helper
            for root, dirs, files in os.walk(self.repo_dir):
                # Calculate relative path from repo_dir
                rel_path = os.path.relpath(root, self.repo_dir)
                
                # Skip ignored directories at the top level
                parts = rel_path.split(os.sep)
                if parts[0] in self.ignored_items or (len(parts) > 1 and parts[1] == "node_modules"):
                    continue
                
                # Target directory in base_dir
                target_dir = self.base_dir if rel_path == "." else os.path.join(self.base_dir, rel_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    if file in self.ignored_items:
                        continue
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(target_dir, file)
                    
                    # Skip if destination is identical to source
                    try:
                        shutil.copy2(src_file, dest_file)
                    except Exception as e:
                        print(f"[WARN] Could not copy {file}: {e}")
            
            print("[OK] File synchronization complete.")
            return True, "File synchronization complete"
            
        except Exception as e:
            error_msg = f"File synchronization failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def check_for_updates(self) -> Tuple[bool, str, str, str]:
        """
        Check if updates are available.
        
        Returns:
            Tuple of (update_available, current_version, latest_version, message)
        """
        print("[*] Checking for updates...")
        
        if not os.path.exists(self.repo_dir):
            return False, "unknown", "unknown", f"Repository directory not found at: {self.repo_dir}"
        
        update_available, current_version, latest_version = self.version_checker.check_update_available()
        
        if update_available:
            message = f"Update available: {current_version} -> {latest_version}"
        else:
            message = f"Already up to date (version {current_version})"
        
        return update_available, current_version, latest_version, message
    
    def perform_update(self, force: bool = False, auto_restart: bool = False) -> Tuple[bool, str]:
        """
        Perform the complete update process.
        
        Args:
            force: Force update even if already up to date
            auto_restart: Automatically restart JARVIS after successful update
            
        Returns:
            Tuple of (success, message)
        """
        print("[*] Starting J.A.R.V.I.S. Updater...")
        
        # Check for updates
        update_available, current_version, latest_version, check_message = self.check_for_updates()
        
        if not update_available and not force:
            return True, check_message
        
        print(f"[INFO] Proceeding with update: {current_version} -> {latest_version}")
        
        # Record update start in manifest
        self.update_manifest.record_update_start(current_version, latest_version)
        
        # Create backup before update
        print("[*] Creating backup...")
        backup_success, backup_path = self.backup_manager.create_backup()
        
        if not backup_success:
            error_msg = f"Backup creation failed: {backup_path}"
            self.update_manifest.record_update_failed(error_msg)
            return False, error_msg
        
        # Save pre-update state for rollback
        self.rollback_manager.save_pre_update_state(backup_path)
        
        # Pull latest changes
        git_success, git_message = self.run_git_pull()
        if not git_success:
            error_msg = f"Git pull failed: {git_message}"
            self.update_manifest.record_update_failed(error_msg)
            print("[*] Attempting rollback due to git pull failure...")
            self.rollback_manager.perform_rollback()
            return False, error_msg
        
        # Synchronize files
        sync_success, sync_message = self.synchronize_files()
        if not sync_success:
            error_msg = f"File synchronization failed: {sync_message}"
            self.update_manifest.record_update_failed(error_msg)
            print("[*] Attempting rollback due to sync failure...")
            self.rollback_manager.perform_rollback()
            return False, error_msg
        
        # Update dependencies
        dep_success, dep_message = self.dependency_manager.update_all_dependencies(force=force)
        if not dep_success:
            print(f"[WARN] Dependency update issues: {dep_message}")
            # Don't fail on dependency issues, just warn
        
        # Mark update as complete
        self.update_manifest.record_update_complete(backup_path)
        self.rollback_manager.mark_update_complete()
        
        # Cleanup old backups
        self.backup_manager.cleanup_old_backups(keep_count=5)
        self.update_manifest.cleanup_old_history(keep_count=20)
        
        success_message = f"J.A.R.V.I.S. updated successfully to version {latest_version}!"
        
        # Auto-restart if requested
        if auto_restart:
            print("[*] Restarting J.A.R.V.I.S....")
            restart_success, restart_message = self.restart_jarvis()
            if restart_success:
                success_message += " J.A.R.V.I.S. is restarting..."
            else:
                success_message += f" Restart failed: {restart_message}"
        
        return True, success_message
    
    def restart_jarvis(self) -> Tuple[bool, str]:
        """
        Restart J.A.R.V.I.S. after successful update.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if JARVIS is running and terminate it
            self.terminate_jarvis()
            
            # Start JARVIS
            launch_script = os.path.join(self.base_dir, "launch_jarvis.py")
            if os.path.exists(launch_script):
                subprocess.Popen([sys.executable, launch_script], cwd=self.base_dir)
                return True, "J.A.R.V.I.S. restarted"
            
            # Try batch file on Windows
            launch_bat = os.path.join(self.base_dir, "launch_jarvis.bat")
            if os.path.exists(launch_bat):
                subprocess.Popen([launch_bat], cwd=self.base_dir, shell=True)
                return True, "J.A.R.V.I.S. restarted"
            
            return False, "Could not find launch script"
            
        except Exception as e:
            error_msg = f"Restart failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def terminate_jarvis(self) -> Tuple[bool, str]:
        """
        Terminate running J.A.R.V.I.S. processes.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Kill Python processes running backend.py or main.py
            if os.name == 'nt':  # Windows
                subprocess.run(
                    ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq JARVIS*"],
                    capture_output=True
                )
            else:  # Unix-like
                subprocess.run(
                    ["pkill", "-f", "backend.py"],
                    capture_output=True
                )
                subprocess.run(
                    ["pkill", "-f", "main.py"],
                    capture_output=True
                )
            
            return True, "J.A.R.V.I.S. terminated"
            
        except Exception as e:
            print(f"[WARN] Termination had issues: {e}")
            return True, "Termination completed with warnings"
    
    def rollback_update(self) -> Tuple[bool, str]:
        """
        Perform a rollback to the previous version.
        
        Returns:
            Tuple of (success, message)
        """
        print("[*] Starting rollback...")
        
        rollback_success, rollback_message = self.rollback_manager.perform_rollback()
        
        if rollback_success:
            self.rollback_manager.cleanup_after_rollback()
            return True, f"Rollback completed: {rollback_message}"
        else:
            return False, f"Rollback failed: {rollback_message}"
    
    def get_update_status(self) -> dict:
        """
        Get current update status and statistics.
        
        Returns:
            Dictionary with update status information
        """
        return self.update_manifest.get_update_statistics()


def update(force: bool = False, auto_restart: bool = False) -> Tuple[bool, str]:
    """
    Convenience function to perform update.
    
    Args:
        force: Force update even if already up to date
        auto_restart: Automatically restart JARVIS after successful update
        
    Returns:
        Tuple of (success, message)
    """
    updater = JARVISUpdater()
    return updater.perform_update(force=force, auto_restart=auto_restart)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Updater")
    parser.add_argument("--force", action="store_true", help="Force update even if already up to date")
    parser.add_argument("--auto-restart", action="store_true", help="Automatically restart JARVIS after update")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous version")
    parser.add_argument("--status", action="store_true", help="Show update status")
    
    args = parser.parse_args()
    
    updater = JARVISUpdater()
    
    if args.status:
        status = updater.get_update_status()
        print("\n=== J.A.R.V.I.S. Update Status ===")
        print(f"Current Version: {status.get('current_version', 'Unknown')}")
        print(f"Last Update: {status.get('last_update', 'Never')}")
        print(f"Total Updates: {status.get('total_updates', 0)}")
        print(f"Successful Updates: {status.get('successful_updates', 0)}")
        print(f"Failed Updates: {status.get('failed_updates', 0)}")
        print(f"Success Rate: {status.get('success_rate', 0):.1f}%")
        sys.exit(0)
    
    if args.rollback:
        success, msg = updater.rollback_update()
        print(msg)
        sys.exit(0 if success else 1)
    
    success, msg = updater.perform_update(force=args.force, auto_restart=args.auto_restart)
    print(msg)
    sys.exit(0 if success else 1)
