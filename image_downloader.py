import os
import logging
import requests
from duckduckgo_search import DDGS

class ImageDownloader:
    def __init__(self, max_images=10, download_folder="image_assests"):
        self.max_images = max_images
        self.download_folder = download_folder

        # Create required folders
        os.makedirs(self.download_folder, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        os.makedirs("runtime_logs", exist_ok=True)
        log_path = os.path.join("runtime_logs", "image_downloader.log")

        self.logger = logging.getLogger("ImageDownloader")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.info("Logger initialized.")

    def search_images(self, term):
        self.logger.info(f"Starting search for: {term}")
        downloaded_image_paths = []

        try:
            with DDGS() as ddgs:
                search_results = ddgs.images(keywords=term)
                image_data = list(search_results)
                image_urls = [item.get("image") for item in image_data[:self.max_images]]

            for idx, url in enumerate(image_urls):
                if not url:
                    self.logger.warning(f"Empty URL at index {idx}")
                    continue

                try:
                    self.logger.info(f"Downloading image {idx + 1}: {url}")
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    img_name = f"{term.replace(' ', '_')}_{idx + 1}.jpg"
                    img_path = os.path.join(self.download_folder, img_name)

                    with open(img_path, 'wb') as img_file:
                        img_file.write(response.content)

                    downloaded_image_paths.append(img_path)

                except requests.RequestException as e:
                    self.logger.error(f"Request error for image {idx + 1}: {e}")
                except Exception as e:
                    self.logger.error(f"Failed to download image {idx + 1}: {e}")

        except Exception as e:
            self.logger.critical(f"Image search failed: {e}")

        self.logger.info(f"Downloaded {len(downloaded_image_paths)} images successfully.")
        return downloaded_image_paths


# # Example usage
# if __name__ == "__main__":
#     image_downloader = ImageDownloader(max_images=10)
#     downloaded_images = image_downloader.search_images("indian meme templates no words only images for editing")

#     print("Downloaded images:")
#     for img_path in downloaded_images:
#         print(img_path)
