import os
from agents.base_agent import Agent
from tools.search_tool import google_search_images
from utils.file_manager import save_image
from utils.logger import get_logger

logger = get_logger("miner")

class MinerAgent(Agent):
    def __init__(self, download_folder="data/raw"):
        instructions = (
            "You are a Mining Agent. Your goal is to find and download images based on a user's query. "
            "You have access to a 'google_search_images' tool. "
            "When asked to mine images, use the tool to find image URLs, then I (the system) will handle the downloading. "
            "You should return a list of URLs found. "
            "If the user asks for a specific number of images, pass that number to the search tool."
            "If you are asked to continue mining, use the 'start_index' parameter to get new results."
        )
        super().__init__(name="MinerAgent", instructions=instructions, tools=[google_search_images])
        self.download_folder = download_folder
        self.search_index = 1
        self.seen_hashes = []

    def mine(self, query, max_images=10):
        """
        Mines images using the AI agent with tools.
        
        Returns:
            dict with status and data:
            Success: {"status": "success", "data": [...], "count": 5}
            Error: {"status": "error", "error_message": "...", "data": [], "count": 0}
        """
        logger.info(f"Received request to mine {max_images} images for '{query}' starting at index {self.search_index}")
        
        # We ask the agent to find the images.
        # The agent will call the tool, and the tool will return structured response.
        prompt = f"Find {max_images} images of '{query}' starting at index {self.search_index}. Use the google_search_images tool and return the URLs found."
        response_text = self.run(prompt)
        
        import json
        import re
        import imagehash
        from PIL import Image
        
        urls = []
        try:
            # Extract JSON from response
            match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if match:
                urls = json.loads(match.group(0))
            else:
                # Fallback: try to find http links
                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', response_text)
        except Exception as e:
            logger.warning(f"Error parsing agent response: {e}")
            
        logger.info(f"Miner Agent found {len(urls)} URLs")
        
        count = 0
        saved_paths = []
        errors = []
        
        for url in urls:
            if count >= max_images:
                break
            
            logger.debug(f"Downloading: {url[:50]}...")
            saved_path = save_image(url, self.download_folder)
            
            if saved_path:
                # Deduplication Check
                try:
                    with Image.open(saved_path) as img:
                        img_hash = imagehash.phash(img)
                        
                    is_duplicate = False
                    for seen_hash in self.seen_hashes:
                        if img_hash - seen_hash < 5:
                            logger.debug(f"Duplicate detected and removed: {saved_path}")
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        os.remove(saved_path)
                        continue
                        
                    self.seen_hashes.append(img_hash)
                    count += 1
                    saved_paths.append(saved_path)
                    logger.debug(f"Saved to {saved_path}")
                    
                except Exception as e:
                    logger.warning(f"Error checking hash for {saved_path}: {e}")
                    # If we can't open it, it might be corrupt
                    if os.path.exists(saved_path):
                         os.remove(saved_path)
                    errors.append(f"Hash check failed for {url[:50]}: {str(e)}")
            else:
                logger.warning(f"Failed to download: {url[:50]}...")
                errors.append(f"Download failed: {url[:50]}")
        
        # Update search index for next time
        if len(urls) > 0:
            self.search_index += len(urls)
        else:
            self.search_index += min(max_images, 10)
        
        if saved_paths:
            logger.info(f"Mining completed: {len(saved_paths)} images saved")
            return {
                "status": "success",
                "data": saved_paths,
                "count": len(saved_paths),
                "errors": errors if errors else None
            }
        else:
            error_msg = f"No images saved. Errors: {len(errors)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error_message": error_msg,
                "data": [],
                "count": 0,
                "errors": errors
            }
