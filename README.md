# Stewie_it v1


🎥 **Demo Reel:** [Watch on Instagram](https://www.instagram.com/stewie_codes_absurd/)

**Stewie_it v1** is an experimental automation project inspired by a viral Instagram trend where Stewie and Peter Griffin humorously explain coding topics over gameplay footage (recent trend)

This project automates assembling these videos by combining user-provided scripts, AI-scraped voices, character images, and gameplay background, then sending them to user.

> ⚠️ This is an experimental project, created for fun and educational purposes. It uses tricks like scraping voices and rotating IPs via AWS EC2.
---

## 🎥 Example Video Format

| ![Stewie](image_assests/stewie.png) | ![Peter](image_assests/peter.png) |
|:----------------------------------------:|:-------------------------------------:|
| **Stewie** explains a coding concept with AI voiceover | **Peter** reacts or adds commentary with AI voiceover |
| Meanwhile, gameplay footage plays in the background |

---

## 🧠 How It Works

### 1. Script Input via Telegram  
- The user sends a coding topic or full dialogue script to the Telegram bot.  
- The bot expects a back-and-forth conversation format alternating between Stewie and Peter lines.  
- Users can optionally generate or fetch scripts using ChatGPT externally and paste them in.

### 2. Voice Generation  
- Voices are scraped from [Parrot AI](https://parrot.ai/) by spinning up an AWS EC2 instance that:  
  - Launches, scrapes voice clips for the dialogue, then shuts down automatically.  
- AWS **CloudWatch Events + Lambda** handle EC2 lifecycle management to rotate IP addresses and avoid bans.

### 3. Image & Asset Collection  
- Character images (`stewie.png`, `peter.png`) are stored locally.  
- Gameplay footage videos are pre-stored, you can add any footage in reel size video in video assests folder 
- DuckDuckGo scraping is used to find additional relevant images if needed.

### 4. Video Assembly  
- Using Python’s `moviepy`, the audio clips, character images, and gameplay footage are synchronized and combined into the final video.  
- Each dialogue line is paired with the corresponding character’s image and AI voice clip.

### 5. Telegram Monitoring  
- The Telegram bot notifies users about job status, errors, or when the video is ready.  
- Users can send new scripts or topics directly to the bot.

### 6. Telegram Delivery  
- When the video is ready, it is **sent directly back to the Telegram user**.
- You always receive your video, even if posting fails.

### 7. (Optional) Instagram Auto-Posting  
- Auto-posting is available via **Instagram Graph API**.
- Since IP address changes with EC2, this is best handled via a **cron job** if a valid session/IP is known.
- You can also manually post using the Telegram-delivered video.
## ⚙️ Requirements

- Python 3.9+
- AWS account with:
  - EC2 instance for voice scraping
  - CloudWatch + Lambda to manage EC2 lifecycle and IP rotation
- Telegram Bot Token
- OpenAI API key (optional, for manual ChatGPT use outside project)



## 📄 Sample Content Format

Below is an example of how the script content is structured to generate the videos. The `audio` field paths are managed internally and are omitted here for privacy.

```json
[
  {
    "audio": "[path to Peter's audio clip]",
    "image": "peter.png",
    "dialogue": "Peter: Hello Indian dev! You’ve seen reels like this, right?",
    "character": "peter",
    "image_search": "indian developer"
  },
  {
    "audio": "[path to Stewie's audio clip]",
    "image": "stewie.png",
    "dialogue": "Stewie: Yeah! Those viral AI voice skits? Everyone’s reposting this one.",
    "character": "stewie",
    "image_search": "viral ai reel"
  },
  {
    "audio": "[path to Peter's audio clip]",
    "image": "peter.png",
    "dialogue": "Peter: I built the automation for this. No paid AI, all open source!",
    "character": "peter",
    "image_search": "automation setup"
  }
]






## ⚙️ Setup & Running

- The main automation service runs via `flow_main.py`.  
- Run it as a background service or use process managers like `systemd`, `pm2`, or `screen`/`tmux` to keep it alive.  
- This script keeps the Telegram bot live and handles the entire workflow end-to-end.

