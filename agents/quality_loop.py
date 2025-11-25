"""
Quality refinement loop for annotations using iterative validation.
"""
import os
import json
from PIL import Image
from agents.base_agent import Agent
from utils.logger import get_logger

logger = get_logger("quality_loop")

class QualityValidator(Agent):
    """Agent that validates annotation quality."""
    
    def __init__(self):
        instructions = (
            "You are a Quality Validator Agent. Your goal is to validate bounding box annotations for accuracy. "
            "Analyze the image and the provided bounding boxes. "
            "Check if: "
            "1. All instances of the target object are detected "
            "2. Bounding boxes are accurate (not too loose or too tight) "
            "3. No false positives (boxes around non-target objects) "
            ""
            "Return ONLY a JSON object: "
            "{\"status\": \"APPROVED\" or \"NEEDS_IMPROVEMENT\", \"feedback\": \"detailed feedback if improvements needed\", \"issues\": [\"list of specific issues\"]} "
            ""
            "Be strict but fair. Only approve high-quality annotations."
        )
        super().__init__(name="QualityValidator", instructions=instructions)
        
    def _draw_boxes_on_image(self, image_path: str, bboxes: list) -> Image:
        """
        Draw bounding boxes on image for visual validation.
        
        Args:
            image_path: Path to image
            bboxes: List of bounding boxes to draw
            
        Returns:
            PIL Image with boxes drawn
        """
        from PIL import ImageDraw, ImageFont
        
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        for i, bbox_data in enumerate(bboxes):
            bbox = bbox_data['bbox']  # [ymin, xmin, ymax, xmax] in 0-1000
            label = bbox_data.get('label', 'object')
            
            # Convert normalized coordinates to pixels
            ymin = int((bbox[0] / 1000) * height)
            xmin = int((bbox[1] / 1000) * width)
            ymax = int((bbox[2] / 1000) * height)
            xmax = int((bbox[3] / 1000) * width)
            
            # Draw rectangle
            draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=4)
            
            # Draw label
            label_text = f"{label} #{i+1}"
            draw.text((xmin + 5, ymin + 5), label_text, fill="red")
        
        return image
    
    def validate(self, image_path: str, query: str, bboxes: list, method: str = "coordinate") -> dict:
        """
        Validate annotation quality using specified method.
        
        Args:
            image_path: Path to the image
            query: Object query (what was being detected)
            bboxes: List of bounding boxes to validate
            method: Validation method - "coordinate", "visual", or "hybrid"
            
        Returns:
            dict with status, feedback, and issues
        """
        if method == "visual":
            return self._validate_visual(image_path, query, bboxes)
        elif method == "hybrid":
            return self._validate_hybrid(image_path, query, bboxes)
        else:  # coordinate (default)
            return self._validate_coordinate(image_path, query, bboxes)
    
    def _validate_coordinate(self, image_path: str, query: str, bboxes: list) -> dict:
        """
        Coordinate-based validation (original method).
        Validator receives image + bbox coordinates as JSON.
        """
        try:
            image = Image.open(image_path)
            
            prompt = (
                f"Validate these bounding box annotations for '{query}':\n"
                f"Number of boxes: {len(bboxes)}\n"
                f"Bounding boxes: {json.dumps(bboxes)}\n\n"
                "Check for:\n"
                "1. Completeness: Are all objects detected?\n"
                "2. Accuracy: Are boxes properly fitted?\n"
                "3. Correctness: No false positives?\n\n"
                "Return JSON: {\"status\": \"APPROVED\" or \"NEEDS_IMPROVEMENT\", \"feedback\": \"...\", \"issues\": [...]}"
            )
            
            response = self.model.generate_content([prompt, image])
            
            if not response or not response.text:
                return {
                    "status": "ERROR",
                    "feedback": "No response from validator",
                    "issues": ["Validation failed"]
                }
                
            text = response.text.strip()
            
            # Clean up markdown
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "")
            text = text.strip()
            
            # Parse response
            try:
                result = json.loads(text)
                return result
            except json.JSONDecodeError:
                # Fallback: look for APPROVED or NEEDS_IMPROVEMENT in text
                if "APPROVED" in text.upper():
                    return {"status": "APPROVED", "feedback": "Quality check passed", "issues": []}
                else:
                    return {"status": "NEEDS_IMPROVEMENT", "feedback": text, "issues": ["Review needed"]}
                    
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "feedback": f"Validation failed: {str(e)}",
                "issues": ["Exception during validation"]
            }
    
    def _validate_visual(self, image_path: str, query: str, bboxes: list) -> dict:
        """
        Visual validation method.
        Draws boxes on image and validator sees the annotated image.
        """
        try:
            # Draw boxes on image
            annotated_image = self._draw_boxes_on_image(image_path, bboxes)
            
            prompt = (
                f"This image shows bounding box annotations for '{query}'.\n"
                f"The RED BOXES show the detected objects.\n"
                f"Number of boxes: {len(bboxes)}\n\n"
                "Evaluate the annotations:\n"
                "1. Are all instances of the object detected?\n"
                "2. Do the boxes properly cover the entire object?\n"
                "3. Are there any false positives (boxes on wrong objects)?\n\n"
                "Return JSON: {\"status\": \"APPROVED\" or \"NEEDS_IMPROVEMENT\", \"feedback\": \"...\", \"issues\": [...]}"
            )
            
            response = self.model.generate_content([prompt, annotated_image])
            
            if not response or not response.text:
                return {
                    "status": "ERROR",
                    "feedback": "No response from validator",
                    "issues": ["Validation failed"]
                }
            
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            
            try:
                result = json.loads(text)
                return result
            except json.JSONDecodeError:
                if "APPROVED" in text.upper():
                    return {"status": "APPROVED", "feedback": "Quality check passed", "issues": []}
                else:
                    return {"status": "NEEDS_IMPROVEMENT", "feedback": text, "issues": ["Review needed"]}
        
        except Exception as e:
            logger.error(f"Visual validation error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "feedback": f"Visual validation failed: {str(e)}",
                "issues": ["Exception during visual validation"]
            }
    
    def _validate_hybrid(self, image_path: str, query: str, bboxes: list) -> dict:
        """
        Hybrid validation method.
        Uses both coordinate and visual validation, combines feedback.
        """
        try:
            # Run both validations
            coord_result = self._validate_coordinate(image_path, query, bboxes)
            visual_result = self._validate_visual(image_path, query, bboxes)
            
            # Combine results - both must approve for overall approval
            if coord_result["status"] == "APPROVED" and visual_result["status"] == "APPROVED":
                return {
                    "status": "APPROVED",
                    "feedback": "Both coordinate and visual validation passed",
                    "issues": []
                }
            else:
                # Combine feedback from both methods
                combined_feedback = []
                if coord_result["status"] != "APPROVED":
                    combined_feedback.append(f"Coordinate check: {coord_result.get('feedback', '')}")
                if visual_result["status"] != "APPROVED":
                    combined_feedback.append(f"Visual check: {visual_result.get('feedback', '')}")
                
                combined_issues = coord_result.get("issues", []) + visual_result.get("issues", [])
                
                return {
                    "status": "NEEDS_IMPROVEMENT",
                    "feedback": " | ".join(combined_feedback),
                    "issues": list(set(combined_issues))  # Remove duplicates
                }
        
        except Exception as e:
            logger.error(f"Hybrid validation error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "feedback": f"Hybrid validation failed: {str(e)}",
                "issues": ["Exception during hybrid validation"]
            }


class AnnotationRefinementLoop:
    """
    Implements iterative refinement loop for annotations.
    """
    
    def __init__(self, annotator_agent, max_iterations: int = 3, validation_method: str = "coordinate"):
        """
        Initialize refinement loop.
        
        Args:
            annotator_agent: The annotation agent to use
            max_iterations: Maximum number of refinement iterations
            validation_method: Validation method - "coordinate", "visual", or "hybrid"
        """
        self.annotator = annotator_agent
        self.validator = QualityValidator()
        self.max_iterations = max_iterations
        self.validation_method = validation_method
        
    def annotate_with_refinement(self, image_path: str, query: str) -> dict:
        """
        Annotate image with iterative quality refinement.
        
        Args:
            image_path: Path to image file
            query: Object query
            
        Returns:
            dict with annotation data and refinement stats
        """
        filename = os.path.basename(image_path)
        logger.info(f"🔄 Starting refinement loop for {filename}")
        
        iteration = 0
        best_annotation = None
        refinement_history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"   Iteration {iteration}/{self.max_iterations}")
            
            # Get annotation
            try:
                image = Image.open(image_path)
                width, height = image.size
                
                # Build prompt (include feedback from previous iteration if available)
                if refinement_history:
                    last_feedback = refinement_history[-1].get("feedback", "")
                    if not last_feedback:
                        # Fallback if no feedback available (e.g. after error)
                        prompt = (
                            f"Annotate ALL instances of '{query}' in this image. "
                            "Output ONLY valid JSON: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                            "Use normalized coordinates (0-1000 range)."
                        )
                    else:
                        prompt = (
                            f"Annotate ALL instances of '{query}' in this image. "
                            f"Previous feedback: {last_feedback} "
                            "Improve the annotations based on this feedback. "
                            "Output ONLY valid JSON: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                            "Use normalized coordinates (0-1000 range)."
                        )
                else:
                    prompt = (
                        f"Annotate ALL instances of '{query}' in this image. "
                        "Output ONLY valid JSON: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}]. "
                        "Use normalized coordinates (0-1000 range)."
                    )
                
                response = self.annotator.model.generate_content([prompt, image])
                
                if not response or not response.text:
                    logger.warning(f"No response in iteration {iteration}")
                    continue
                    
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "")
                text = text.strip()
                
                # Parse JSON
                try:
                    bboxes = json.loads(text)
                except json.JSONDecodeError:
                    # Try to fix
                    import re
                    fixed_text = text.replace("'", '"')
                    fixed_text = re.sub(r',\s*}', '}', fixed_text)
                    fixed_text = re.sub(r',\s*]', ']', fixed_text)
                    bboxes = json.loads(fixed_text)
                
                # Validate format
                if not isinstance(bboxes, list) or not bboxes:
                    logger.warning(f"Invalid bbox format in iteration {iteration}")
                    continue
                    
                # Store this annotation
                current_annotation = {
                    "bboxes": bboxes,
                    "width": width,
                    "height": height
                }
                
                # Validate quality
                validation = self.validator.validate(image_path, query, bboxes, method=self.validation_method)
                
                refinement_history.append({
                    "iteration": iteration,
                    "num_bboxes": len(bboxes),
                    "validation_status": validation["status"],
                    "feedback": validation.get("feedback", ""),
                    "issues": validation.get("issues", [])
                })
                
                logger.info(f"   ✓ Iteration {iteration}: {len(bboxes)} boxes, Status: {validation['status']}")
                
                # Always update to the latest annotation (don't accumulate)
                # This ensures we keep only the most recent iteration's result
                best_annotation = current_annotation
                    
                # If approved, we're done
                if validation["status"] == "APPROVED":
                    logger.info(f"✅ Annotation approved after {iteration} iteration(s)")
                    break
                    
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}", exc_info=True)
                refinement_history.append({
                    "iteration": iteration,
                    "error": str(e)
                })
        
        # Return best annotation with refinement stats
        if best_annotation:
            best_annotation["refinement_stats"] = {
                "iterations": iteration,
                "history": refinement_history,
                "final_status": refinement_history[-1]["validation_status"] if refinement_history else "UNKNOWN"
            }
            logger.info(f"🎯 Refinement complete: {len(best_annotation['bboxes'])} boxes after {iteration} iterations")
            return best_annotation
        else:
            logger.error(f"❌ Failed to generate valid annotation for {filename}")
            return None
