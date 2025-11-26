"""
ADK-based pipeline implementation with real agent integration.

This module wraps the existing Foundry agents (Miner, Curator, Annotator)
as function tools for ADK's LlmAgent, then orchestrates them using:
- `SequentialAgent` for Miner → Curator → Annotator flow
- `LoopAgent` to repeat until target count is reached
"""

from typing import Dict, List
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from pipelines.adk_state import PipelineState
from services.miner import MinerService
from services.curator import CuratorService
from services.annotator import AnnotatorService
from utils.logger import get_logger

logger = get_logger("adk_pipeline")

def create_adk_pipeline(state: PipelineState):
    """
    Create ADK pipeline with state-aware tools.
    
    Args:
        state: Pipeline state to pass to tools
        
    Returns:
        Configured LoopAgent
    """
    
    # Create tools with state bound
    miner_tool = MinerService().as_adk_tool(state)
    curator_tool = CuratorService().as_adk_tool(state)
    annotator_tool = AnnotatorService().as_adk_tool(state)
    
    # MinerAgent with real search capability
    miner_agent = LlmAgent(
        name="MinerAgent",
        model="gemini-2.5-flash",
        instruction=(
            "You are a Mining Agent responsible for finding images. "
            f"Use the mine_tool to search for images matching '{state.query}'. "
            f"Request {state.get_needed_count()} images. "
            "The tool will return a list of image URLs that have been downloaded and deduplicated."
        ),
        tools=[miner_tool]
    )
    
    # CuratorAgent with real validation
    curator_agent = LlmAgent(
        name="CuratorAgent",
        model="gemini-2.5-flash",
        instruction=(
            "You are a Curator Agent. Your goal is to filter images to ensure they match the user's query. "
            f"Use the curate_tool to validate images for '{state.query}'. "
            "Pass the mined images to the tool. "
            "The tool will analyze each image and determine if it strictly contains the ACTUAL OBJECT visually present in the image. "
            "CRITICAL RULES: "
            "- The object must be VISUALLY PRESENT and clearly visible in the image. "
            "- Text mentioning the object (like labels, packaging, signs) is NOT sufficient. "
            "- Products or packaging that mention the object but don't show the actual object will be REJECTED. "
            f"- For example: A box labeled 'hot dogs' does NOT contain a dog. A sign saying 'cat food' does NOT contain a cat. "
            "- Only images where the actual physical object can be clearly seen and identified will be kept. "
            "The tool returns only valid, unique images."
        ),
        tools=[curator_tool]
    )
    
    # AnnotatorAgent with real bounding box generation
    annotator_agent = LlmAgent(
        name="AnnotatorAgent",
        model="gemini-2.5-flash",
        instruction=(
            "You are an Annotation Agent. Your goal is to detect objects in images and provide bounding boxes. "
            f"Use the annotate_tool to generate bounding boxes for '{state.query}'. "
            "Pass the curated images to the tool. "
            "The tool can detect single or multiple object types in an image. "
            "It returns bounding boxes in [ymin, xmin, ymax, xmax] format normalized to 0-1000. "
            "Output will be valid JSON - a list of objects with double quotes: [{\"label\": \"object_name\", \"bbox\": [ymin, xmin, ymax, xmax]}, ...]. "
            "Each object instance will have its own entry with the correct label matching the requested object type. "
            "The tool will also return a 'stop' signal when the target count is reached, indicating the loop should terminate."
        ),
        tools=[annotator_tool]
    )
    
    # ---------------------------------------------------------------------------
    # ADK Pipeline Definition
    # ---------------------------------------------------------------------------
    sequential_pipeline = SequentialAgent(
        name="FoundrySequentialPipeline",
        sub_agents=[miner_agent, curator_agent, annotator_agent]
    )
    
    loop_pipeline = LoopAgent(
        name="FoundryTargetLoop",
        sub_agents=[sequential_pipeline],
        max_iterations=20  # Safety limit to prevent infinite loops
    )
    
    return loop_pipeline

if __name__ == "__main__":
    # Example: Create pipeline for 5 dog images
    state = PipelineState(target_count=5, query="dog")
    pipeline = create_adk_pipeline(state)
    
    print("Running ADK LoopAgent with real agents...")
    result = pipeline.run_async()
    
    print("\nPipeline Summary:")
    summary = state.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print(f"\nDataset size: {len(state.dataset)} images")
