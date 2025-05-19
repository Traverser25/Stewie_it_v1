import time
import requests
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence

class VoiceGenerator:
    PETER_URL = "https://www.tryparrotai.com/ai-voice/peter-griffin"
    STEWIE_URL = "https://www.tryparrotai.com/ai-voice/stewie-griffin"

    def __init__(self):
        self.setup_logging()
        self.driver = self.setup_driver()
        self.output_dir = "audio_assests"
        os.makedirs(self.output_dir, exist_ok=True)

    def setup_logging(self):
        """Set up logging configuration"""
        # Create runtime_logs folder if it doesn't exist
        if not os.path.exists('runtime_logs'):
            os.makedirs('runtime_logs')
        self.logger = logging.getLogger("VoiceGenerator")
        self.logger.setLevel(logging.DEBUG)
        log_file = os.path.join('runtime_logs', 'voice_generator.log')
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Logging initialized.")

    def setup_driver(self):
        """Setup the WebDriver for Selenium"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
            self.logger.info("WebDriver initialized successfully.")
            return driver
        except Exception as e:
            self.logger.error(f"Error initializing WebDriver: {e}")
            raise

    def download_video(self, url, filename):
        """Download video from the provided URL"""
        try:
            self.logger.info(f"Downloading from: {url}")
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
                self.logger.info("Video downloaded successfully!")
            else:
                self.logger.error(f"Failed to download video. Status: {r.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading video: {e}")
            raise

    def convert_video_to_audio(self, video_filename, audio_filename):
        """Convert video file to audio, save in 'audio_assests', and delete the original video."""
        try:
            audio_path = os.path.join(self.output_dir, audio_filename)
            self.logger.info(f"Converting {video_filename} to {audio_path}")

            video_clip = VideoFileClip(video_filename)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path,logger=None)

            audio_clip.close()
            video_clip.close()

            # Delete original video file
            if os.path.exists(video_filename):
                os.remove(video_filename)
                self.logger.info(f"Deleted video file: {video_filename}")
            else:
                self.logger.warning(f"Video file not found: {video_filename}")

            self.logger.info(f"Audio saved as {audio_path}")
            return audio_path
        except Exception as e:
            self.logger.error(f"Error converting video to audio: {e}")
            raise

    def remove_silence(self, audio_file):
        """Remove silence from audio"""
        try:
            audio = AudioSegment.from_mp3(audio_file)

            # Split the audio based on silence
            chunks = split_on_silence(
                audio,
                min_silence_len=500,  # Silence length to consider for splitting
                silence_thresh=-40,   # Silence threshold in dB
                keep_silence=250      # Keep 250ms of silence between chunks
            )

            # Combine the chunks after splitting
            combined_audio = AudioSegment.empty()
            for chunk in chunks:
                combined_audio += chunk

            # Export the combined audio to the same output file (overwrite original)
            combined_audio.export(audio_file, format="mp3")
            self.logger.info(f"Processed audio saved to {audio_file}")
            return audio_file
        except Exception as e:
            self.logger.error(f"Error removing silence from audio: {e}")
            raise

    def generate_audio_from_sentence(self, sentence, speaker, index):
        """Generate audio from sentence using the specified speaker"""
        try:
            page_url = self.PETER_URL if speaker.lower() == "peter" else self.STEWIE_URL
            filename_prefix = speaker.lower()

            # Load the page
            self.driver.delete_all_cookies()
            self.logger.info("Cookies cleared.")
            self.driver.get(page_url)

            # Input text
            textarea = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            textarea.clear()
            textarea.send_keys(sentence)

            # Click generate
            generate_btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "Generate")]')
            generate_btn.click()

            # Wait for video
            video = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            for _ in range(30):
                video_url = video.get_attribute("src")
                if video_url and video_url.startswith("https://"):
                    break
                time.sleep(1)

            if video_url:
                self.logger.info(f"Video URL: {video_url}")
                mp4_name = f"{filename_prefix}_voice_{index}.mp4"
                mp3_name = f"{filename_prefix}_audio_{index}.mp3"
                self.download_video(video_url, mp4_name)
                audio_path = self.convert_video_to_audio(mp4_name, mp3_name)
                
                # Remove silence from the audio
                self.remove_silence(audio_path)

            else:
                self.logger.warning("Video URL not found.")
        except Exception as e:
            self.logger.error(f"Error during sentence generation: {e}")
            raise

    def process_conversation(self, line: str, dialogue_id: int) -> bool:
        """Process a single conversation line to generate an audio file"""
        try:
            if ":" not in line:
                self.logger.warning(f"Skipping malformed line: '{line}'")
                return False

            speaker, sentence = map(str.strip, line.split(":", 1))

            if len(sentence) <= 100:
                self.logger.info(f"Generating for: '{sentence}' with ID: {dialogue_id}")
                self.generate_audio_from_sentence(sentence, speaker, dialogue_id)
                time.sleep(2)
                return True  # Success
            else:
                self.logger.warning(f"Skipping sentence (too long): '{sentence}'")
                return False  # Sentence too long

        except Exception as e:
            self.logger.error(f"Error processing conversation ID {dialogue_id}: {e}")
            return False  # Exception occurred

# Example usage:

if __name__ == "__main__":
    conversation_list = [
        "Peter: Time complexity tells you how long your code will take as input grows.",
        "Stewie: So it's not about actual seconds?",
        "Peter: Correct. It measures how the effort scales with more data.",
        "Stewie: And space complexity?",
        "Peter: It measures how much memory your code needs as input grows.",
        "Stewie: So time is speed, space is memory?",
        "Peter: Exactly. Both use Big O to describe growth.",
        "Stewie: O of one means constant time and space?",
        "Peter: Yes. It doesn’t matter how big the input is.",
        "Stewie: Got it. So we aim for efficiency in both time and space."
    ]
    
    voice_generator = VoiceGenerator()
    for idx,line in enumerate(conversation_list):
        voice_generator.process_conversation(line,idx)
