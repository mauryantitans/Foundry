import os
from typing import List, Dict, Optional
import imagehash
from PIL import Image
from tools.search_tool import google_search_images
from utils.file_manager import save_image
from utils.logger import get_logger

logger = get_logger("miner")

class MinerService:
    """
    Service responsible for discovering and downloading images.
    
    Features:
    - Google Custom Search integration
    - Perceptual hash deduplication
    - Automatic pagination management
    """
    
    def __init__(self, download_folder: str = "data/raw"):
        self.download_folder = download_folder
        self.search_index = 1
        self.seen_hashes = []

    def mine(self, query: str, max_images: int = 10) -> Dict:
        """
        Mines images by directly calling the search tool.
        
        Args:
            query: Search query string
            max_images: Number of images to attempt to download
            
        Returns:
            Dict containing:
            - status: "success" or "error"
            - data: List of saved image paths
            - count: Number of images saved
            - errors: List of error messages (optional)
        """
        logger.info(f"Mining {max_images} images for '{query}' starting at index {self.search_index}")
        
        # Call search tool directly (no LLM needed for deterministic search)
        search_result = google_search_images(
            query=query,
            num_images=max_images,
            start_index=self.search_index
        )
        
        if search_result["status"] == "error":
            logger.error(f"Search failed: {search_result['error_message']}")
            return search_result
        
        urls = search_result["data"]
        logger.info(f"Found {len(urls)} image URLs")
        
        saved_paths = []
        errors = []
        
        for url in urls:
            if len(saved_paths) >= max_images:
                break
            
            logger.debug(f"Downloading: {url[:60]}...")
            saved_path = save_image(url, self.download_folder)
            
            if saved_path:
                # Deduplication check
                try:
                    with Image.open(saved_path) as img:
                        img_hash = imagehash.phash(img)
                    
                    # Check if duplicate
                    is_duplicate = False
                    for seen_hash in self.seen_hashes:
                        if img_hash - seen_hash < 5:  # Hamming distance threshold
                            logger.debug(f"Duplicate detected: {saved_path}")
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        os.remove(saved_path)
                        continue
                    
                    # Not a duplicate - keep it
                    self.seen_hashes.append(img_hash)
                    saved_paths.append(saved_path)
                    logger.debug(f"Saved: {saved_path}")
                    
                except Exception as e:
                    logger.warning(f"Error processing {saved_path}: {e}")
                    if os.path.exists(saved_path):
                        os.remove(saved_path)
                    errors.append(f"Processing failed: {url[:50]}")
            else:
                logger.warning(f"Failed to download: {url[:60]}...")
                errors.append(f"Download failed: {url[:50]}")
        
        # Update search index for next call
        self.search_index = search_result.get("next_index", self.search_index + max_images)
        
        if saved_paths:
            logger.info(f"✅ Mining completed: {len(saved_paths)} images saved")
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

    def as_adk_tool(self, state):
        """
        Returns a callable tool function for ADK integration.
        
        Args:
            state: PipelineState object for tracking progress
            
        Returns:
            Callable function matching the ADK tool signature
        """
        def mine_tool(count: int) -> Dict:
            """
            Mine images using the MinerService.
            """
            logger.info(f"🔍 Mining {count} images for '{state.query}'")
            result = self.mine(state.query, max_images=count)
            
            if result["status"] == "success":
                state.record_mining(len(result["data"]))
                logger.info(f"✅ Mined {len(result['data'])} images")
                return {"status": "success", "images": result["data"], "count": len(result["data"])}
            else:
                logger.warning(f"❌ Mining failed: {result.get('error_message')}")
                return {"status": "error", "images": [], "count": 0}
                
        return mine_tool
