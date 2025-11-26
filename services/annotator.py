import os
import json
import re
import time
from typing import Dict, List, Any, Optional
from PIL import Image
from utils.logger import get_logger
from utils.gemini_client import get_gemini_model

logger = get_logger("annotator")

class AnnotatorService:
    """
    Service responsible for detecting objects and generating bounding boxes.
    
    Features:
    - Multi-object detection
    - Normalized coordinate output (0-1000)
    - Robust JSON parsing and auto-repair
    """
    
    def __init__(self, curated_folder: str = "data/curated", max_retries: int = 3):
        instructions = (
            "You are an Annotation Agent. Your goal is to detect objects in images and provide bounding boxes. "
            "You can detect single or multiple object types in an image. "
            "Return bounding boxes in [ymin, xmin, ymax, xmax] format normalized to 0-1000. "
            "Output ONLY valid JSON - a list of objects with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}, ...]. "
            "Each object instance should have its own entry with the correct label matching the requested object type. "
            "DO NOT use single quotes. DO NOT add trailing commas. DO NOT add any text before or after the JSON."
        )
        self.model = get_gemini_model(system_instruction=instructions)
        self.curated_folder = curated_folder
        self.max_retries = max_retries

    def _parse_json_robust(self, text: str, filename: str) -> Optional[List[Dict]]:
        """
        Robustly parse JSON with multiple fallback strategies.
        
        Args:
            text: Raw text response from model
            filename: Filename for logging purposes
            
        Returns:
            Parsed JSON list or None if all parsing attempts fail
        """
        # Strategy 1: Direct parse
        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Remove markdown code blocks
        if '```' in text:
            # Extract content between code fences
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if match:
                text = match.group(1).strip()
                try:
                    data = json.loads(text)
                    logger.debug(f"Parsed after removing markdown for {filename}")
                    return data
                except json.JSONDecodeError:
                    pass
        
        # Strategy 3: Fix common issues
        try:
            # Replace single quotes with double quotes (carefully)
            fixed_text = re.sub(r"(?<!\\)'", '"', text)
            # Remove trailing commas before closing brackets/braces
            fixed_text = re.sub(r',\s*}', '}', fixed_text)
            fixed_text = re.sub(r',\s*]', ']', fixed_text)
            # Remove any text before the first '[' or '{'
            match = re.search(r'[\[{]', fixed_text)
            if match:
                fixed_text = fixed_text[match.start():]
            # Remove any text after the last ']' or '}'
            match = re.search(r'[\]}](?!.*[\]}])', fixed_text)
            if match:
                fixed_text = fixed_text[:match.end()]
            
            data = json.loads(fixed_text)
            logger.info(f"Fixed JSON formatting for {filename}")
            return data
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Try to extract JSON array using regex
        try:
            # Look for array pattern
            array_match = re.search(r'\[\s*{[\s\S]*}\s*]', text)
            if array_match:
                potential_json = array_match.group(0)
                # Apply fixes
                potential_json = re.sub(r"(?<!\\)'", '"', potential_json)
                potential_json = re.sub(r',\s*}', '}', potential_json)
                potential_json = re.sub(r',\s*]', ']', potential_json)
                data = json.loads(potential_json)
                logger.info(f"Extracted JSON array for {filename}")
                return data
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Strategy 5: Try to find individual bbox objects and reconstruct
        try:
            # Look for bbox patterns like [ymin, xmin, ymax, xmax]
            bbox_pattern = r'\[\s*\d+(?:\.\d+)?\s*,\s*\d+(?:\.\d+)?\s*,\s*\d+(?:\.\d+)?\s*,\s*\d+(?:\.\d+)?\s*]'
            bboxes = re.findall(bbox_pattern, text)
            if bboxes:
                # Try to find labels
                label_pattern = r'["\']?label["\']?\s*:\s*["\']([^"\'\']+)["\']'
                labels = re.findall(label_pattern, text, re.IGNORECASE)
                
                # Construct JSON
                reconstructed = []
                for i, bbox_str in enumerate(bboxes):
                    bbox = json.loads(bbox_str)
                    label = labels[i] if i < len(labels) else "unknown"
                    reconstructed.append({"label": label, "bbox": bbox})
                
                if reconstructed:
                    logger.info(f"Reconstructed JSON from bbox patterns for {filename}")
                    return reconstructed
        except Exception:
            pass
        
        # All strategies failed
        logger.warning(f"All JSON parsing strategies failed for {filename}")
        logger.debug(f"Problematic text (first 300 chars): {text[:300]}...")
        return None

    def _annotate_single_image(self, img_path: str, query: str, objects: List[str], 
                               width: int, height: int, retry_count: int = 0) -> Optional[Dict]:
        """
        Annotate a single image with retry logic.
        
        Args:
            img_path: Path to image
            query: Full query string
            objects: List of object names to detect
            width: Image width
            height: Image height
            retry_count: Current retry attempt (0-indexed)
            
        Returns:
            Annotation data dict or None if failed
        """
        try:
            image = Image.open(img_path)
            
            # Build prompt for single or multiple objects
            if len(objects) == 1:
                if retry_count > 0:
                    # On retry, be more explicit
                    prompt = (
                        f"Find ALL instances of {objects[0]} in this image. "
                        "Return ONLY a JSON array of objects. Each object must have 'label' and 'bbox' keys. "
                        "Format: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000). Example: [{\"label\": \"dog\", \"bbox\": [100, 200, 300, 400]}]. "
                        "Return ONLY the JSON array, no other text."
                    )
                else:
                    prompt = (
                        f"Return bounding boxes for ALL instances of {objects[0]} in this image. "
                        "Output ONLY valid JSON with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000 range). No explanations, just JSON."
                    )
            else:
                objects_list = ', '.join(objects)
                if retry_count > 0:
                    prompt = (
                        f"Find ALL instances of these objects: {objects_list}. "
                        "Return ONLY a JSON array. Each object must have 'label' and 'bbox' keys. "
                        "Format: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000). Return ONLY the JSON array."
                    )
                else:
                    prompt = (
                        f"Return bounding boxes for ALL instances of these objects in this image: {objects_list}. "
                        "Detect and label each object separately. "
                        "Output ONLY valid JSON with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000 range). No explanations, just JSON."
                    )
            
            response = self.model.generate_content([prompt, image])
            if not response or not response.text:
                logger.warning(f"No response from model for {os.path.basename(img_path)} (attempt {retry_count + 1})")
                return None
            
            text = response.text.strip()
            
            # Use robust JSON parsing
            data = self._parse_json_robust(text, os.path.basename(img_path))
            
            if data is None:
                return None
            
            # Basic validation/fix
            if isinstance(data, list) and len(data) > 0:
                # If first element is a list, convert all list elements to dict format
                if isinstance(data[0], list):
                    data = [{'label': query, 'bbox': box} for box in data if isinstance(box, list) and len(box) == 4]
                # Ensure all items have the expected format
                elif not isinstance(data[0], dict):
                    logger.warning(f"Unexpected annotation format for {os.path.basename(img_path)} (attempt {retry_count + 1})")
                    return None
            else:
                logger.warning(f"Invalid annotation format (not a list) for {os.path.basename(img_path)} (attempt {retry_count + 1})")
                return None
            
            # Validate bounding boxes
            valid_data = []
            for item in data:
                if 'bbox' in item and isinstance(item['bbox'], list) and len(item['bbox']) == 4:
                    # Check if bbox values are reasonable (0-1000 range)
                    bbox = item['bbox']
                    if all(0 <= coord <= 1000 for coord in bbox):
                        valid_data.append(item)
                    else:
                        logger.warning(f"Invalid bbox coordinates for {os.path.basename(img_path)}: {bbox}")
            
            if not valid_data:
                logger.warning(f"No valid bounding boxes for {os.path.basename(img_path)} (attempt {retry_count + 1})")
                return None
            
            logger.info(f"Annotated: {os.path.basename(img_path)} -> {len(valid_data)} objects (attempt {retry_count + 1})")
            
            return {
                "bboxes": valid_data,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            logger.error(f"Error annotating {os.path.basename(img_path)} (attempt {retry_count + 1}): {e}")
            return None

    def annotate(self, query: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        Annotates a list of images with bounding boxes.
        
        Args:
            query: Object query (can be single like 'dog' or multiple like 'dog,cat,car')
            image_paths: List of image paths to annotate
            
        Returns:
            Dictionary mapping filenames to annotation data:
            {
                "filename.jpg": {
                    "bboxes": [{"label": "dog", "bbox": [...]}],
                    "width": 800,
                    "height": 600
                }
            }
        """
        # Parse query - support multiple objects (comma-separated)
        objects = [q.strip() for q in query.split(',')]
        query_display = query if len(objects) == 1 else f"{len(objects)} objects ({query})"
        
        logger.info(f"Labeling {len(image_paths)} images for '{query_display}'")
        
        annotations = {}
        
        for img_path in image_paths:
            filename = os.path.basename(img_path)
            
            try:
                # Get image dimensions
                with Image.open(img_path) as image:
                    width, height = image.size
                
                # Try annotation with retry logic
                result = None
                for attempt in range(self.max_retries):
                    result = self._annotate_single_image(
                        img_path, query, objects, width, height, retry_count=attempt
                    )
                    
                    if result is not None:
                        # Success!
                        annotations[filename] = result
                        if attempt > 0:
                            logger.info(f"✅ Successfully annotated {filename} after {attempt + 1} attempts")
                        break
                    
                    # Failed attempt - wait before retry (except on last attempt)
                    if attempt < self.max_retries - 1:
                        wait_time = 1 + attempt  # Exponential backoff: 1s, 2s, 3s
                        logger.info(f"⏳ Retrying {filename} in {wait_time}s... (attempt {attempt + 2}/{self.max_retries})")
                        time.sleep(wait_time)
                
                if result is None:
                    logger.error(f"❌ Failed to annotate {filename} after {self.max_retries} attempts")
                    
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=True)
        
        success_rate = len(annotations) / len(image_paths) * 100 if image_paths else 0
        logger.info(f"✅ Annotation completed: {len(annotations)}/{len(image_paths)} images ({success_rate:.1f}% success rate)")
        
        return annotations

    def as_adk_tool(self, state):
        """
        Returns a callable tool function for ADK integration.
        
        Args:
            state: PipelineState object for tracking progress
            
        Returns:
            Callable function matching the ADK tool signature
        """
        def annotate_tool(images: List[str]) -> Dict:
            """
            Annotate images using the AnnotatorService.
            """
            logger.info(f"🔍 Annotating {len(images)} images")
            
            # Use parallel annotator for performance (hardcoded for now as per original pipeline)
            from agents.parallel_annotator import ParallelAnnotatorAgent
            from utils.pipeline_features import get_pipeline_features
            
            features = get_pipeline_features()
            quality_loop = None
            if features.enable_quality_loop:
                quality_loop = features.create_quality_loop(self)
            
            # Create parallel annotator on the fly
            annotator = ParallelAnnotatorAgent(num_workers=3, quality_loop=quality_loop)
            annotations = annotator.annotate_parallel(state.query, images)
            
            state.record_annotation(len(annotations))
            
            # Add to dataset and check if target reached
            target_reached = state.add_annotations(annotations)
            
            logger.info(f"✅ Annotated {len(annotations)} images. Progress: {state.current_count}/{state.target_count}")
            
            return {
                "status": "success",
                "annotations": annotations,
                "count": len(annotations),
                "stop": target_reached,
                "progress": f"{state.current_count}/{state.target_count}"
            }
            
        return annotate_tool
