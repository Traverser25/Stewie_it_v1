import os
import re
from typing import List
from datetime import datetime
import subprocess
import shutil
class Utils:
    """
    A utility class providing common helper functions for various tasks.
    """
    @staticmethod
    def stop_vm():
        try:
            subprocess.run(['sudo', '/sbin/shutdown', 'now'], check=True)
            print("Reboot command issued successfully.")
          
        except subprocess.CalledProcessError as e:
            print(f"Failed to reboot the VM: {e}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
           

    @staticmethod
    def get_ordered_audio_files(folder_path: str) -> List[str]:
        """
        Returns a list of .mp3 filenames from the folder, ordered by the number in the filename.

        Example:
            Input: ['peter_audio_1.mp3', 'stewie_audio_2.mp3', 'peter_3.mp3']
            Output: ['peter_audio_1.mp3', 'stewie_audio_2.mp3', 'peter_3.mp3']
        """
        try:
            audio_files = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".mp3")
            ]

            def extract_number(filename: str) -> int:
                match = re.search(r'(\d+)', filename)
                return int(match.group(1)) if match else float('inf')

            sorted_files = sorted(audio_files, key=extract_number)
            return sorted_files

        except Exception as e:
            print(f"[Utils] Error reading audio files from '{folder_path}': {e}")
            return []


    @staticmethod
    def archive_audio_assets():
        """
        Moves all files from 'audio_assets/' to 'archive/YYYY-MM-DD/' and ensures the source folder is empty.
        """
        source_dir = 'audio_assests'
        archive_root = 'archives_audios'
        today_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        target_dir = os.path.join(archive_root, today_str)

        try:
            os.makedirs(target_dir, exist_ok=True)

            for filename in os.listdir(source_dir):
                src_path = os.path.join(source_dir, filename)
                if os.path.isfile(src_path):
                    shutil.move(src_path, os.path.join(target_dir, filename))

            print(f"Archived files to {target_dir}.")
        except Exception as e:
            print(f"[Utils] Error archiving audio assets: {e}")

# Utils.archive_audio_assets()