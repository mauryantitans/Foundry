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
        
    def validate(self, image_path: str, query: str, bboxes: list) -> dict:
        """
        Validate annotation quality.
        
        Args:
            image_path: Path to the image
            query: Object query (what was being detected)
            bboxes: List of bounding boxes to validate
            
        Returns:
            dict with status, feedback, and issues
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


class AnnotationRefinementLoop:
    """
    Implements iterative refinement loop for annotations.
    """
    
    def __init__(self, annotator_agent, max_iterations: int = 3):
        """
        Initialize refinement loop.
        
        Args:
            annotator_agent: The annotation agent to use
            max_iterations: Maximum number of refinement iterations
        """
        self.annotator = annotator_agent
        self.validator = QualityValidator()
        self.max_iterations = max_iterations
        
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
                    last_feedback = refinement_history[-1]["feedback"]
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
                validation = self.validator.validate(image_path, query, bboxes)
                
                refinement_history.append({
                    "iteration": iteration,
                    "num_bboxes": len(bboxes),
                    "validation_status": validation["status"],
                    "feedback": validation.get("feedback", ""),
                    "issues": validation.get("issues", [])
                })
                
                logger.info(f"   ✓ Iteration {iteration}: {len(bboxes)} boxes, Status: {validation['status']}")
                
                # Update best annotation
                if best_annotation is None or validation["status"] == "APPROVED":
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
