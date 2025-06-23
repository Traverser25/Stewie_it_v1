from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
)
from PIL import Image
from duckduckgo_search import DDGS
import requests
import os
import random

from moviepy.config_defaults import IMAGEMAGICK_BINARY
#IMAGEMAGICK_BINARY = r"/usr/bin/convert"   chnage this path to  your  imagemagick file path

class DynamicVideoEditor:
    def __init__(self, video_path, output_path, dialogue_data):
        self.video_path = video_path
        self.output_path = output_path
        self.dialogue_data = dialogue_data
        self.audio_clips = []
        self.image_clips = []
        self.subtitle_clips = []
        self.current_start = 0
    
        self.video = VideoFileClip(video_path).subclip(10, 60)

    def search_image(self, term):
        with DDGS() as ddgs:
            search_results = ddgs.images(keywords=term)
            image_data = list(search_results)
            image_urls = [item.get("image") for item in image_data[:1]]
            if image_urls:
                url = image_urls[0]
                print(f"Downloading image for '{term}': {url}")
                img_data = requests.get(url).content
                os.makedirs("downloaded_images", exist_ok=True)
                img_name = f"downloaded_images/{term.replace(' ', '_')}.jpg"
                with open(img_name, 'wb') as img_file:
                    img_file.write(img_data)
                return img_name
        return None

    def create_title_clip(self, text, duration):
        return (
            TextClip(text, fontsize=60, color='white', font='Arial-Bold', bg_color='black')
            .set_duration(duration)
            .set_position(("center", 80))
        )

    def create_end_title_clip(self, text, duration=3):
        return (
            TextClip(text, fontsize=50, color='white', font='Arial-Bold', bg_color='black',method="caption")
            .set_duration(duration)
            .set_position(("center", "center"))
        )

    def add_word_by_word_subtitles(self, text, start_time, duration):
        words = text.split()
        word_duration = duration / len(words)
        word_clips = []

        current_time = start_time
        for word in words:
            clip = (
                TextClip(word, fontsize=95, color='yellow', font='DejaVu-Sans-Bold', stroke_color="black", stroke_width=0.3)
                .set_start(current_time)
                .set_duration(word_duration)
                .set_position(("center", "center"))
                .fadein(0.1)
                .fadeout(0.1)
            )
            word_clips.append(clip)
            current_time += word_duration
        return word_clips

    def edit(self):
        #title_clip = self.create_title_clip(self.title, duration=self.video.duration)

        for item in self.dialogue_data:
            audio_path = f"audio_assests/{item['character'].lower()}_audio_{item['id']}.mp3"
            #audio_path=r'C:\Users\HP\Desktop\stewie_v1\audio_assests\peter_audio_2.mp3'
            image_path = f"image_assests/{item['image']}"

            subtitle_text = item["sentence"]
            search_term = item.get("image_search", "")

            # Load and position audio
            audio = AudioFileClip(audio_path).set_start(self.current_start)
            self.audio_clips.append(audio)

            # Position character image
            char_position = "left" if "peter" in image_path.lower() else "right"
            if image_path:
                char_image = (
                    ImageClip(image_path)
                    .set_start(self.current_start)
                    .set_duration(audio.duration)
                    .resize(height=500)
                    
                )

                y_position = max(0, self.video.h - 500 - 50)

 
                x_position = 50 if char_position == "left" else max(0, self.video.w - char_image.w - 50)

  
                char_image = char_image.set_position((x_position, y_position))
                self.image_clips.append(char_image)

            # Subtitle
            subtitle_clips = self.add_word_by_word_subtitles(subtitle_text, self.current_start, audio.duration)
            self.subtitle_clips.extend(subtitle_clips)

            # Optional: Related image search
            try:
                relevant_image = self.search_image(search_term)
                if relevant_image:
                    searched_image = (
                        ImageClip(relevant_image)
                        .set_start(self.current_start)
                        .set_duration(audio.duration)
                        .resize(height=350)
                        .set_position(("center", 300))
                    )
                    self.image_clips.append(searched_image)
            except Exception as e:
                print(f"Image search failed: {e}")

            self.current_start += audio.duration + 0.5

        # end_clip = self.create_end_title_clip("Like, Share, thanks for watching.")
        # self.image_clips.append(end_clip)

        final_audio = CompositeAudioClip(self.audio_clips)
        final_video = CompositeVideoClip(
            [self.video] + self.image_clips + self.subtitle_clips
        ).set_audio(final_audio)

        final_video.write_videofile(self.output_path, codec="libx264", audio_codec="aac", fps=24)


# === Usage Example ===
# if __name__ == "__main__":
#     from db_handler import DBOperation
#     db=DBOperation()
#     dialogue_data=db.get_raedy_assests()
#     print(dialogue_data)
    
#     editor = DynamicVideoEditor(
#         video_path=r"/home/ubuntu/mainrepo/stewie_v1/video_assests/video_without_audio.webm",
#         output_path="output_final_video.mp4",
#         dialogue_data=dialogue_data
#     )
#     editor.edit()
