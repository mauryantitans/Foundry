import os
from agents.base_agent import Agent
from tools.search_tool import google_search_images
from utils.file_manager import save_image

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
        """
        print(f"⛏️  Miner: Received request to mine {max_images} images for '{query}' starting at index {self.search_index}")
        
        # We ask the agent to find the images.
        # The agent will call the tool, and the tool will return URLs.
        prompt = f"Find {max_images} images of '{query}' starting at index {self.search_index}. Return ONLY a JSON list of the image URLs found."
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
            print(f"   ⚠️ Error parsing agent response: {e}")
            
        print(f"   Miner Agent found {len(urls)} URLs.")
        
        count = 0
        saved_paths = []
        for url in urls:
            if count >= max_images:
                break
            
            print(f"   Downloading: {url[:50]}...")
            saved_path = save_image(url, self.download_folder)
            
            if saved_path:
                # Deduplication Check
                try:
                    with Image.open(saved_path) as img:
                        img_hash = imagehash.phash(img)
                        
                    is_duplicate = False
                    for seen_hash in self.seen_hashes:
                        if img_hash - seen_hash < 5:
                            print(f"   👯 Duplicate detected and removed: {saved_path}")
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        os.remove(saved_path)
                        continue
                        
                    self.seen_hashes.append(img_hash)
                    count += 1
                    saved_paths.append(saved_path)
                    print(f"   ✅ Saved to {saved_path}")
                    
                except Exception as e:
                    print(f"   ⚠️ Error checking hash for {saved_path}: {e}")
                    # If we can't open it, it might be corrupt, so maybe don't count it?
                    # For now, let's assume if save_image worked, it's a file.
                    # But if Image.open fails, it's not a valid image.
                    if os.path.exists(saved_path):
                         os.remove(saved_path)
            else:
                print(f"   ❌ Failed to download")
        
        # Update search index for next time
        # We increment by the number of URLs found (or requested) to page forward
        # Google Search index is 1-based.
        self.search_index += len(urls)
        if len(urls) == 0:
             # If no URLs found, maybe jump a bit or just stop?
             # Let's increment by max_images to try to get past a bad block
             self.search_index += max_images
                
        return saved_paths
