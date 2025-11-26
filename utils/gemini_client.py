import os
import google.generativeai as genai
from utils.logger import get_logger

logger = get_logger("gemini_client")

def get_gemini_model(model_name: str = "gemini-2.5-flash", system_instruction: str = None):
    """
    Get a configured Gemini GenerativeModel instance.
    
    Args:
        model_name: Name of the model to use (default: gemini-2.5-flash)
        system_instruction: Optional system instruction for the model
        
    Returns:
        genai.GenerativeModel: Configured model instance
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY not found")
        
    genai.configure(api_key=api_key)
    
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )
