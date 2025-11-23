import os
import shutil
from PIL import Image
import imagehash
from agents.base_agent import Agent
from utils.logger import get_logger

logger = get_logger("curator")

class CuratorAgent(Agent):
    def __init__(self, raw_folder="data/raw", curated_folder="data/curated"):
        instructions = (
            "You are a Curator Agent. Your goal is to filter images to ensure they match the user's query. "
            "You will be given an image and a query. "
            "You must analyze the image and determine if it strictly contains the ACTUAL OBJECT visually present in the image. "
            "CRITICAL RULES: "
            "- The object must be VISUALLY PRESENT and clearly visible in the image. "
            "- Text mentioning the object (like labels, packaging, signs) is NOT sufficient. "
            "- Products or packaging that mention the object but don't show the actual object should be REJECTED. "
            "- For example: A box labeled 'hot dogs' does NOT contain a dog. A sign saying 'cat food' does NOT contain a cat. "
            "- Only accept images where the actual physical object can be clearly seen and identified. "
            "Answer strictly with 'YES' or 'NO'."
        )
        super().__init__(name="CuratorAgent", instructions=instructions)
        self.raw_folder = raw_folder
        self.curated_folder = curated_folder
        self.seen_hashes = []

    def curate(self, query, image_paths, max_count=None):
        """
        Curates a list of image paths.
        
        Args:
            query: The object query to match
            image_paths: List of image paths to curate
            max_count: Maximum number of images to curate (stops once reached). 
                      If None, curates all images.
        """
        logger.info(f"Filtering {len(image_paths)} images for '{query}'" + 
                    (f" (target: {max_count})" if max_count else ""))
        
        kept_images = []
        
        for img_path in image_paths:
            # Stop if we've reached the target count
            if max_count is not None and len(kept_images) >= max_count:
                logger.info(f"Reached target of {max_count} curated images")
                break
            try:
                image = Image.open(img_path)
                
                # Deduplication
                img_hash = imagehash.phash(image)
                is_duplicate = False
                for seen_hash in self.seen_hashes:
                    if img_hash - seen_hash < 5:
                        logger.info(f"🔄 Duplicate found: {os.path.basename(img_path)}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    logger.debug(f"Duplicate found: {os.path.basename(img_path)}")
                    continue
                
                self.seen_hashes.append(img_hash)
                
                # AI Verification - Strict prompt to avoid false positives
                prompt = (
                    f"Does this image contain the actual, visible {query} object? "
                    f"IMPORTANT: The {query} must be physically present and clearly visible in the image. "
                    f"REJECT if the image only shows: text mentioning '{query}', packaging/labels with '{query}' written on them, "
                    f"or products that mention '{query}' but don't show the actual object. "
                    f"Only answer YES if you can clearly see the actual {query} object in the image. "
                    f"Answer strictly with YES or NO."
                )
                
                response = self.model.generate_content([prompt, image])
                if not response or not response.text:
                    logger.warning(f"No response from model for {os.path.basename(img_path)}")
                    continue
                    
                answer = response.text.strip().upper()
                
                if "YES" in answer:
                    # Ensure directory exists
                    os.makedirs(self.curated_folder, exist_ok=True)
                    dest_path = os.path.join(self.curated_folder, os.path.basename(img_path))
                    shutil.copy(img_path, dest_path)
                    kept_images.append(dest_path)
                    logger.info(f"✅ Kept: {os.path.basename(img_path)}")
                else:
                    # Log rejection reason at INFO level to help debug
                    logger.info(f"❌ Rejected: {os.path.basename(img_path)} | Reason: {response.text.strip()}")
                    logger.debug(f"Full response: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error processing {os.path.basename(img_path)}: {e}", exc_info=True)
                
        logger.info(f"Finished. Kept {len(kept_images)} images")
        return kept_images
