import os
import json
from PIL import Image
from agents.base_agent import Agent
from utils.logger import get_logger

logger = get_logger("annotator")

class AnnotatorAgent(Agent):
    def __init__(self, curated_folder="data/curated"):
        instructions = (
            "You are an Annotation Agent. Your goal is to detect objects in images and provide bounding boxes. "
            "You can detect single or multiple object types in an image. "
            "Return bounding boxes in [ymin, xmin, ymax, xmax] format normalized to 0-1000. "
            "Output ONLY valid JSON - a list of objects with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}, ...]. "
            "Each object instance should have its own entry with the correct label matching the requested object type. "
            "DO NOT use single quotes. DO NOT add trailing commas. DO NOT add any text before or after the JSON."
        )
        super().__init__(name="AnnotatorAgent", instructions=instructions)
        self.curated_folder = curated_folder

    def annotate(self, query, image_paths):
        """
        Annotates a list of images.
        
        Args:
            query: Object query (can be single like 'dog' or multiple like 'dog,cat,car')
            image_paths: List of image paths to annotate
        """
        # Parse query - support multiple objects (comma-separated)
        objects = [q.strip() for q in query.split(',')]
        query_display = query if len(objects) == 1 else f"{len(objects)} objects ({query})"
        
        logger.info(f"Labeling {len(image_paths)} images for '{query_display}'")
        
        annotations = {}
        
        for img_path in image_paths:
            try:
                image = Image.open(img_path)
                width, height = image.size
                
                # Build prompt for single or multiple objects
                if len(objects) == 1:
                    prompt = (
                        f"Return bounding boxes for ALL instances of {objects[0]} in this image. "
                        "Output ONLY valid JSON with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000 range). No explanations, just JSON."
                    )
                else:
                    objects_list = ', '.join(objects)
                    prompt = (
                        f"Return bounding boxes for ALL instances of these objects in this image: {objects_list}. "
                        "Detect and label each object separately. "
                        "Output ONLY valid JSON with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000 range). No explanations, just JSON."
                    )
                
                response = self.model.generate_content([prompt, image])
                if not response or not response.text:
                    logger.warning(f"No response from model for {os.path.basename(img_path)}")
                    continue
                    
                text = response.text.strip()
                
                # Clean up markdown and common formatting issues
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "")
                text = text.strip()
                
                # Try to fix common JSON issues (single quotes, trailing commas)
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as e:
                    logger.warning(f"Initial JSON parse failed for {os.path.basename(img_path)}: {e}")
                    # Try to fix common issues
                    try:
                        # Replace single quotes with double quotes
                        fixed_text = text.replace("'", '"')
                        # Remove trailing commas before closing brackets
                        import re
                        fixed_text = re.sub(r',\s*}', '}', fixed_text)
                        fixed_text = re.sub(r',\s*]', ']', fixed_text)
                        data = json.loads(fixed_text)
                        logger.info(f"Fixed JSON formatting for {os.path.basename(img_path)}")
                    except json.JSONDecodeError as e2:
                        logger.warning(f"Failed to parse JSON for {os.path.basename(img_path)} even after fixes: {e2}")
                        logger.debug(f"Problematic text: {text[:200]}...")
                        continue
                
                # Basic validation/fix
                if isinstance(data, list) and len(data) > 0:
                    # If first element is a list, convert all list elements to dict format
                    if isinstance(data[0], list):
                        data = [{'label': query, 'bbox': box} for box in data if isinstance(box, list) and len(box) == 4]
                    # Ensure all items have the expected format
                    elif not isinstance(data[0], dict):
                        logger.warning(f"Unexpected annotation format for {os.path.basename(img_path)}")
                        continue
                else:
                    logger.warning(f"Invalid annotation format (not a list) for {os.path.basename(img_path)}")
                    continue
                
                logger.info(f"Annotated: {os.path.basename(img_path)} -> {len(data)} objects")
                
                annotations[os.path.basename(img_path)] = {
                    "bboxes": data,
                    "width": width,
                    "height": height
                }
                
            except Exception as e:
                logger.error(f"Error annotating {os.path.basename(img_path)}: {e}", exc_info=True)
                
        return annotations
