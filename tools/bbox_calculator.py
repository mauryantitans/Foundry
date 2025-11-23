"""
Bounding box calculation tool using code executor for reliable math.
"""
import json
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

# Retry configuration
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

def create_bbox_calculator():
    """
    Creates a specialized agent for bounding box calculations using code execution.
    
    Returns:
        Agent configured for reliable bbox calculations
    """
    calculator = Agent(
        name="BboxCalculator",
        model=Gemini(
            model="gemini-2.0-flash",
            retry_options=retry_config
        ),
        instruction="""You are a specialized bounding box calculator. Your ONLY job is to generate Python code that calculates bounding box coordinates.

RULES:
1. You MUST output ONLY Python code, no explanations or text
2. The code must calculate bounding box coordinates from normalized values (0-1000) to absolute pixel coordinates
3. Input format: normalized_bbox = [ymin, xmin, ymax, xmax] (0-1000 range), image_width, image_height
4. Output format: absolute_bbox = [x, y, width, height] in pixels
5. The code MUST print the result as: print(json.dumps({"bbox": [x, y, width, height]}))

Example calculation:
- normalized: [100, 200, 300, 400] (ymin, xmin, ymax, xmax)
- image: 1000x800 (width x height)
- absolute: x = (200/1000)*1000 = 200, y = (100/1000)*800 = 80
- width = ((400-200)/1000)*1000 = 200, height = ((300-100)/1000)*800 = 160
- result: [200, 80, 200, 160]
""",
        code_executor=BuiltInCodeExecutor()
    )
    return calculator

def calculate_bbox(normalized_bbox, image_width, image_height, calculator_agent=None):
    """
    Calculate absolute bounding box coordinates from normalized values.
    
    Args:
        normalized_bbox: [ymin, xmin, ymax, xmax] in 0-1000 range
        image_width: Image width in pixels
        image_height: Image height in pixels
        calculator_agent: The bbox calculator agent instance (not used, kept for compatibility)
        
    Returns:
        dict with status and bbox:
        Success: {"status": "success", "bbox": [x, y, width, height]}
        Error: {"status": "error", "error_message": "..."}
    """
    import logging
    logger = logging.getLogger("foundry.bbox_calculator")
    
    try:
        ymin, xmin, ymax, xmax = normalized_bbox
        
        # Direct calculation - simple and reliable
        abs_x = (xmin / 1000) * image_width
        abs_y = (ymin / 1000) * image_height
        abs_w = ((xmax - xmin) / 1000) * image_width
        abs_h = ((ymax - ymin) / 1000) * image_height
        
        logger.debug(f"Calculated bbox: [{abs_x}, {abs_y}, {abs_w}, {abs_h}] from normalized {normalized_bbox}")
        
        return {
            "status": "success",
            "bbox": [abs_x, abs_y, abs_w, abs_h]
        }
        
    except Exception as e:
        error_msg = f"Bbox calculation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "error_message": error_msg
        }

