import os
import json
from PIL import Image
from agents.base_agent import Agent

class AnnotatorAgent(Agent):
    def __init__(self, curated_folder="data/curated"):
        instructions = (
            "You are an Annotation Agent. Your goal is to detect objects in images and provide bounding boxes. "
            "Return bounding boxes in [ymin, xmin, ymax, xmax] format normalized to 0-1000. "
            "Output ONLY a JSON list of objects: [{'label': 'name', 'bbox': [ymin, xmin, ymax, xmax]}, ...]."
        )
        super().__init__(name="AnnotatorAgent", instructions=instructions)
        self.curated_folder = curated_folder

    def annotate(self, query, image_paths):
        """
        Annotates a list of images.
        """
        print(f"✏️  Annotator: Labeling {len(image_paths)} images for '{query}'...")
        
        annotations = {}
        
        for img_path in image_paths:
            try:
                image = Image.open(img_path)
                width, height = image.size
                
                prompt = (
                    f"Return bounding boxes for ALL instances of {query} in this image. "
                    "Output ONLY a JSON list."
                )
                
                response = self.model.generate_content([prompt, image])
                text = response.text.strip()
                
                # Clean up markdown
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "")
                
                data = json.loads(text)
                
                # Basic validation/fix
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                     data = [{'label': query, 'bbox': box} for box in data]
                
                print(f"   ✅ Annotated: {os.path.basename(img_path)} -> {len(data)} objects")
                
                annotations[os.path.basename(img_path)] = {
                    "bboxes": data,
                    "width": width,
                    "height": height
                }
                
            except Exception as e:
                print(f"   ⚠️ Error annotating {os.path.basename(img_path)}: {e}")
                
        return annotations
