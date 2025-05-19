import time
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TelegramBot:
    def __init__(self):
        # Fetch credentials from environment
        self.BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        self.url = f'https://api.telegram.org/bot{self.BOT_TOKEN}/'
        self.update_id_file = "last_update_id.txt"

    def send_message(self, text):
        """Send a plain text message to Telegram."""
        try:
            response = requests.post(f'{self.url}sendMessage', data={'chat_id': self.CHAT_ID, 'text': text})
            print("Sent message:", text)
            return response
        except Exception as e:
            self.log_error(f"Failed to send message: {e}")

    def send_video_file(self, video_path, caption=None):
        """Send a video file as a document to Telegram."""
        try:
            with open(video_path, 'rb') as video_file:
                files = {'document': video_file}
                data = {'chat_id': self.CHAT_ID}
                if caption:
                    data['caption'] = caption
                response = requests.post(f'{self.url}sendDocument', data=data, files=files)
                print("Sent video file:", video_path)
                return response
        except Exception as e:
            self.log_error(f"Failed to send video file: {e}")

    def get_updates(self, offset=None):
        """Fetch new updates from Telegram."""
        params = {'timeout': 10, 'offset': offset}
        try:
            response = requests.get(f'{self.url}getUpdates', params=params)
            return response.json()
        except Exception as e:
            self.log_error(f"Error fetching updates: {e}")
            return {}

    def extract_json_from_message(self, msg_text):
        """Extract and parse JSON if message starts with 'from:'."""
        msg_text = msg_text.strip()
        if msg_text.lower().startswith('from:'):
            try:
                raw_json_lines = msg_text.split(':', 1)[1].strip().splitlines()
                raw_json = ' '.join(line.strip() for line in raw_json_lines if line.strip())
                print("Extracted JSON string:\n", raw_json)
                data = json.loads(raw_json)
                print("Parsed data:\n", data)
                return data
            except json.JSONDecodeError as e:
                self.log_error(f"JSON decode error: {e}\nText:\n{msg_text}")
        else:
            print("Message does not start with 'from:'")
        return None

    def is_valid_list_of_dicts(self, data):
        """Check if data is a list of dictionaries."""
        valid = isinstance(data, list) and all(isinstance(d, dict) for d in data)
        print("Is valid list of dicts:", valid)
        return valid

    def get_last_update_id(self):
        """Read last update ID from file."""
        try:
            with open(self.update_id_file, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return None

    def set_last_update_id(self, last_update_id):
        """Write the last processed update ID to a file."""
        with open(self.update_id_file, "w") as f:
            f.write(str(last_update_id))

    def poll_for_content(self, timeout_minutes=15):
        """Poll for messages for a specific duration."""
        print("Polling for content...")
        self.send_message("Please send your data in format:\nfrom: [ {...}, {...} ]")
        start_time = time.time()
        last_update_id = self.get_last_update_id()

        while time.time() - start_time < timeout_minutes * 60:
            updates = self.get_updates(last_update_id)
            results = updates.get('result', [])

            for update in results:
                last_update_id = update['update_id'] + 1
                self.set_last_update_id(last_update_id)

                message = update.get('message', {})
                text = message.get('text')
                if text:
                    print("New message received:", text)
                    data = self.extract_json_from_message(text)
                    if data and self.is_valid_list_of_dicts(data):
                        self.send_message("Content accepted and added to DB.")
                        return list(data)
                    else:
                        self.send_message("Invalid format. Please resend as:\nfrom: [ {...}, {...} ]")
            time.sleep(3)

        self.send_message("Timeout: No valid content received in 15 minutes.")

    def log_error(self, message):
        """Log an error to a file with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("errors.log", "a") as f:
            f.write(f"[{timestamp}] {message}\n")


# if __name__ == "__main__":
#     bot = TelegramBot()
#     data = bot.poll_for_content()
#     if data:
#         print("Received data:", data)