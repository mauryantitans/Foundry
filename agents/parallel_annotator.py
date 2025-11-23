"""
Parallel annotation agent for processing multiple images concurrently.
"""
import os
import json
from PIL import Image
from agents.base_agent import Agent
from utils.logger import get_logger

logger = get_logger("parallel_annotator")

class ParallelAnnotatorAgent:
    """
    Wrapper that creates parallel annotation workers for batch processing.
    """
    def __init__(self, num_workers=3, curated_folder="data/curated"):
        """
        Initialize parallel annotator.
        
        Args:
            num_workers: Number of parallel annotation workers
            curated_folder: Folder containing curated images
        """
        self.num_workers = num_workers
        self.curated_folder = curated_folder
        self.workers = []
        
        # Create worker agents
        for i in range(num_workers):
            worker = Agent(
                name=f"AnnotatorWorker{i+1}",
                instructions=(
                    "You are an Annotation Worker Agent. Your goal is to detect objects in a single image and provide bounding boxes. "
                    "Return bounding boxes in [ymin, xmin, ymax, xmax] format normalized to 0-1000. "
                    "Output ONLY valid JSON - a list of objects with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}, ...]. "
                    "DO NOT use single quotes. DO NOT add trailing commas. DO NOT add any text before or after the JSON."
                )
            )
            self.workers.append(worker)
        
        logger.info(f"Initialized {num_workers} parallel annotation workers")
    
    def annotate_image(self, worker_index, img_path, query, objects):
        """
        Annotate a single image using a worker agent.
        
        Args:
            worker_index: Index of the worker to use
            img_path: Path to image file
            query: Original query string
            objects: List of object names to detect
            
        Returns:
            dict with annotation data or None if failed
        """
        worker = self.workers[worker_index % len(self.workers)]
        
        try:
            image = Image.open(img_path)
            width, height = image.size
            
            # Build prompt
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
            
            response = worker.model.generate_content([prompt, image])
            if not response or not response.text:
                logger.warning(f"No response from model for {os.path.basename(img_path)}")
                return None
                
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
                    return None
            
            # Validate and fix format
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], list):
                    data = [{'label': query, 'bbox': box} for box in data if isinstance(box, list) and len(box) == 4]
                elif not isinstance(data[0], dict):
                    logger.warning(f"Unexpected annotation format for {os.path.basename(img_path)}")
                    return None
            else:
                logger.warning(f"Invalid annotation format (not a list) for {os.path.basename(img_path)}")
                return None
            
            logger.debug(f"Annotated: {os.path.basename(img_path)} -> {len(data)} objects")
            
            return {
                "filename": os.path.basename(img_path),
                "bboxes": data,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            logger.error(f"Error annotating {os.path.basename(img_path)}: {e}", exc_info=True)
            return None
    
    def annotate_parallel(self, query, image_paths):
        """
        Annotate multiple images in parallel.
        
        Args:
            query: Object query (can be single like 'dog' or multiple like 'dog,cat,car')
            image_paths: List of image paths to annotate
            
        Returns:
            dict mapping filename to annotation data
        """
        import concurrent.futures
        
        objects = [q.strip() for q in query.split(',')]
        query_display = query if len(objects) == 1 else f"{len(objects)} objects ({query})"
        
        logger.info(f"Parallel annotation: {len(image_paths)} images for '{query_display}' using {self.num_workers} workers")
        
        annotations = {}
        
        # Process images in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all annotation tasks
            future_to_path = {
                executor.submit(self.annotate_image, i % self.num_workers, img_path, query, objects): img_path
                for i, img_path in enumerate(image_paths)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_path):
                img_path = future_to_path[future]
                try:
                    result = future.result()
                    if result:
                        annotations[result["filename"]] = {
                            "bboxes": result["bboxes"],
                            "width": result["width"],
                            "height": result["height"]
                        }
                        logger.info(f"✅ Annotated: {result['filename']} -> {len(result['bboxes'])} objects")
                except Exception as e:
                    logger.error(f"Exception in parallel annotation for {os.path.basename(img_path)}: {e}", exc_info=True)
        
        logger.info(f"Parallel annotation completed: {len(annotations)}/{len(image_paths)} images annotated")
        return annotations

