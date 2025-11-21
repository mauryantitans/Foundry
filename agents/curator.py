import os
import shutil
from PIL import Image
import imagehash
from agents.base_agent import Agent

class CuratorAgent(Agent):
    def __init__(self, raw_folder="data/raw", curated_folder="data/curated"):
        instructions = (
            "You are a Curator Agent. Your goal is to filter images to ensure they match the user's query. "
            "You will be given an image and a query. "
            "You must analyze the image and determine if it strictly contains the object described in the query. "
            "Answer strictly with 'YES' or 'NO'."
        )
        super().__init__(name="CuratorAgent", instructions=instructions)
        self.raw_folder = raw_folder
        self.curated_folder = curated_folder
        self.seen_hashes = []

    def curate(self, query, image_paths):
        """
        Curates a list of image paths.
        """
        print(f"🧐 Curator: Filtering {len(image_paths)} images for '{query}'...")
        
        kept_images = []
        
        for img_path in image_paths:
            try:
                image = Image.open(img_path)
                
                # Deduplication
                img_hash = imagehash.phash(image)
                is_duplicate = False
                for seen_hash in self.seen_hashes:
                    if img_hash - seen_hash < 5:
                        print(f"   👯 Duplicate found: {os.path.basename(img_path)}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                self.seen_hashes.append(img_hash)
                
                # AI Verification
                prompt = f"Does this image contain {query}? Answer strictly with YES or NO."
                
                # We need to pass the image to the model. 
                # The BaseAgent.run method currently takes text. 
                # We need to extend it or access the chat session directly to send images.
                # Let's access the chat session directly for this specific call or modify BaseAgent.
                # For now, I'll access the internal chat_session or model directly since I know the implementation.
                
                response = self.model.generate_content([prompt, image])
                answer = response.text.strip().upper()
                
                if "YES" in answer:
                    dest_path = os.path.join(self.curated_folder, os.path.basename(img_path))
                    shutil.copy(img_path, dest_path)
                    kept_images.append(dest_path)
                    print(f"   ✅ Kept: {os.path.basename(img_path)}")
                else:
                    print(f"   🗑️  Discarded: {os.path.basename(img_path)} (Reason: {answer})")
                    
            except Exception as e:
                print(f"   ⚠️ Error processing {os.path.basename(img_path)}: {e}")
                
        print(f"🧐 Curator: Finished. Kept {len(kept_images)} images.")
        return kept_images
