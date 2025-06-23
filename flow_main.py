import os
import logging
from db_handler import DBOperation
from telegram_handler import TelegramBot
from scrap_audio import VoiceGenerator
from editor_agent import DynamicVideoEditor
from utils import Utils
import  time 
#changes in editor  , in flow, in telegram file 


def run_flow():
    # Setup logging
    os.makedirs("runtime_logs", exist_ok=True)
    logging.basicConfig(
        filename="runtime_logs/flow_log.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    bot = TelegramBot()
    db = DBOperation()

    logging.info("Fetching stage and unprocessed dialogues...")
    stage_data = db.get_stage_and_unprocessed_dialogues()
    current_stage = stage_data.get("stage")

    if current_stage == 0:
        logging.info("Stage 0: Table is empty. Polling Telegram for new content.")
        try:
            content = bot.poll_for_content()
            db.add_dialogues(content)
            logging.info("New dialogues added to the database.")
        except Exception as e:
            logging.error(f"Error polling or adding dialogues: {e}")

    elif current_stage == 1:
        bot.send_message("Current stage is 1, collecting the audio")
        voice_generator = VoiceGenerator()
        logging.info("Stage 1: Starting audio processing phase...")
        sentences = stage_data.get("dialogues")

        for cur in sentences:
            dialogue_id = cur.get("id")
            dialogue_line = cur.get("sentence")

            try:
                logging.info(f"Processing dialogue ID {dialogue_id}: {dialogue_line}")
                success_flag = voice_generator.process_conversation(dialogue_line, dialogue_id)
                db.mark_processed(dialogue_id, success_flag)
                logging.info(f"Marked dialogue ID {dialogue_id} as processed: {success_flag}")
            except Exception as e:
                logging.error(f"Error processing dialogue ID {dialogue_id}: {e}")
                db.mark_processed(dialogue_id, False)

        bot.send_message("Collection of audio ended, shutting down the VM")

    elif current_stage == 2:
        logging.info("Stage 2: Starting video editing...")
        bot.send_message("Ready to edit the video")
        assets = db.get_raedy_assests()
        editor = DynamicVideoEditor(
            video_path=r"/home/ubuntu/mainrepo/stewie_v1/video_assests/video_without_audio.webm", 
            output_path="output_final_video.mp4",
            dialogue_data=assets,
          
        )
        editor.edit()
        logging.info("Video editing completed.")
        db.truncate_dialouge_stage()
        Utils.archive_audio_assets()
        try:
            bot.send_message("editimg completed sending you video")
            bot.send_video_file("")
        except Exception as e:
            logging.error(f"Error  while sending the video: {e}")

    else:
        logging.warning(f"Unexpected stage value: {current_stage}")

if __name__ == "__main__":
    try:
        run_flow()
    except Exception as e:
        logging.critical(f"Critical failure in main workflow: {e}")
    finally:
        time.sleep(60*3)
        print("shutting down the vm")
        #pass
        #here  shutdwon the  machine  
        Utils.stop_vm()  
