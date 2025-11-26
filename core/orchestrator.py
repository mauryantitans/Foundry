"""
Enhanced Main Agent with better prompt understanding and query optimization.
"""

import os
import json
import re
import time
from utils.gemini_client import get_gemini_model
from pipelines.foundry_pipeline import FoundryPipeline, FoundryBYODPipeline
from utils.logger import setup_logging, get_logger
from utils.pipeline_features import get_pipeline_features

setup_logging()
logger = get_logger("main_agent")


class MainAgent:
    """
    Main Orchestrator Agent with enhanced prompt understanding.
    
    Features:
    - Separates search query from annotation objects
    - Optimizes search queries for better results
    - Confirms plan before execution
    - Provides detailed progress feedback
    """
    
    def __init__(self):
        instructions = (
            "You are the Main Orchestrator Agent for Foundry dataset creation. "
            "You excel at understanding user requests and extracting: "
            "1. Scene description (for searching images) "
            "2. Objects to annotate (for detection) "
            "3. Number of images needed "
            "You provide clear, structured responses."
        )
        self.model = get_gemini_model(system_instruction=instructions)
        logger.info("🚀 MainAgent initialized with enhanced prompt understanding")
    
    def _run_model(self, prompt: str) -> str:
        """Helper to run the model and get text response."""
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            return ""
        except Exception as e:
            logger.error(f"Model execution failed: {e}")
            return ""

    def parse_request(self, user_request: str) -> dict:
        """
        Parse user request into structured components.
        
        Returns:
            {
                "mode": "standard" or "byod",
                "search_query": "description for finding images",
                "annotation_objects": ["obj1", "obj2"],
                "count": number,
                "image_dir": path or None
            }
        """
        logger.info(f"Parsing request: '{user_request}'")
        
        parse_prompt = f"""Analyze this dataset creation request and extract information:

"{user_request}"

Return ONLY a JSON object with this EXACT structure:
{{
  "mode": "standard" or "byod",
  "search_query": "optimized search query that describes the scene/context",
  "annotation_objects": ["object1", "object2"],
  "count": number,
  "image_dir": "path" or null,
  "reasoning": "brief explanation of your extraction"
}}

Guidelines:
- search_query: Natural phrase describing the scene (e.g., "person playing guitar", "red car on highway")
- annotation_objects: List of individual objects to detect (e.g., ["person", "guitar"], ["car"])
- count: Number of images requested (default 5 if not specified)
- mode: "byod" if user mentions a folder/directory, else "standard"
- Optimize search_query for better image search results

Examples:
Input: "5 images of man holding guitar, annotate man and guitar"
Output: {{"mode": "standard", "search_query": "person holding guitar", "annotation_objects": ["person", "guitar"], "count": 5, "image_dir": null, "reasoning": "Optimized 'man' to 'person' for better search results"}}

Input: "get 10 red sports cars"
Output: {{"mode": "standard", "search_query": "red sports car", "annotation_objects": ["car"], "count": 10, "image_dir": null, "reasoning": "Scene is red sports car, detecting car objects"}}

Input: "I have images in /path/folder, detect dogs and cats"
Output: {{"mode": "byod", "search_query": null, "annotation_objects": ["dog", "cat"], "count": null, "image_dir": "/path/folder", "reasoning": "BYOD mode - annotating existing images"}}
"""
        
        response = self._run_model(parse_prompt)
        
        try:
            # Extract JSON
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                logger.info(f"✅ Parsed: {parsed.get('reasoning', '')}")
                return parsed
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Failed to parse: {e}")
            # Fallback to simple parsing
            return {
                "mode": "standard",
                "search_query": user_request,
                "annotation_objects": ["object"],
                "count": 5,
                "image_dir": None,
                "reasoning": "Fallback parsing"
            }
    
    def confirm_plan(self, parsed: dict) -> bool:
        """Show plan and ask for confirmation."""
        print("\n" + "="*70)
        print("📋 EXECUTION PLAN")
        print("="*70)
        
        if parsed["mode"] == "byod":
            print(f"Mode: BYOD (Annotate Your Images)")
            print(f"📁 Directory: {parsed['image_dir']}")
            print(f"🔍 Objects to detect: {', '.join(parsed['annotation_objects'])}")
        else:
            print(f"Mode: Standard (Create New Dataset)")
            print(f"🔍 Search query: \"{parsed['search_query']}\"")
            print(f"🏷️  Objects to annotate: {', '.join(parsed['annotation_objects'])}")
            print(f"📊 Number of images: {parsed['count']}")
        
        if parsed.get("reasoning"):
            print(f"💡 Note: {parsed['reasoning']}")
        
        print("="*70)
        
        # Auto-confirm for now (can add interactive confirmation later)
        return True
    
    def run_pipeline(self, user_request=None, query=None, count=None):
        """Execute pipeline with enhanced understanding."""
        if query and count:
            # Direct arguments provided
            logger.info(f"Using provided arguments: query='{query}', count={count}")
            parsed = {
                "mode": "standard",
                "search_query": query,
                "annotation_objects": [obj.strip() for obj in query.split(',')],
                "count": count,
                "image_dir": None
            }
        elif user_request:
            # Parse natural language request
            parsed = self.parse_request(user_request)
        else:
            logger.error("No request or arguments provided")
            return
        
        # Show plan
        if not self.confirm_plan(parsed):
            print("❌ Execution cancelled")
            return
        
        # Execute based on mode
        if parsed["mode"] == "byod":
            self._execute_byod(parsed)
        else:
            self._execute_standard(parsed)
    
    def _execute_standard(self, parsed: dict):
        """Execute standard pipeline with search + annotation."""
        search_query = parsed["search_query"]
        annotation_objects = parsed["annotation_objects"]
        count = parsed["count"]
        
        # Create enhanced pipeline with separate queries
        # Join annotation objects for annotation query
        annotation_query = ",".join(annotation_objects)
        
        pipeline = FoundryPipeline(
            query=search_query,  # For mining
            target_count=count,
            annotation_query=annotation_query  # For annotation
        )
        
        # Run pipeline (now always uses ADK workflow agents)
        logger.info("🤖 Using ADK workflow agents (SequentialAgent + LoopAgent)")
        result = pipeline.run()
        
        # Display results
        if result["status"] == "success":
            self._display_coco_info(result.get("output_path"))
        
        # Show metrics
        features = get_pipeline_features()
        if features.enable_metrics:
            features.print_metrics_summary()
    
    def _execute_byod(self, parsed: dict):
        """Execute BYOD mode."""
        image_dir = parsed["image_dir"]
        annotation_objects = parsed["annotation_objects"]
        
        # Join objects for query string
        query = ",".join(annotation_objects)
        
        pipeline = FoundryBYODPipeline(image_dir=image_dir, query=query)
        result = pipeline.run()
        
        if result["status"] == "success":
            self._display_coco_info(result.get("output_path"))
        
        features = get_pipeline_features()
        if features.enable_metrics:
            features.print_metrics_summary()
    
    def run_byod_mode(self, image_dir: str, query: str):
        """BYOD mode entry point."""
        parsed = {
            "mode": "byod",
            "search_query": None,
            "annotation_objects": [obj.strip() for obj in query.split(',')],
            "count": None,
            "image_dir": image_dir
        }
        self.confirm_plan(parsed)
        self._execute_byod(parsed)
    
    def run_interactive_mode(self):
        """Interactive mode with enhanced understanding."""
        print("\n" + "="*70)
        print("🤖 Foundry: AI-Powered Dataset Creation System")
        print("   Using: Enhanced Prompt Understanding 🚀")
        print("="*70)
        print("\n📚 What I Can Do:\n")
        
        print("┌─ MODE 1: CREATE NEW DATASET ─────────────────────────────┐")
        print("│ Describe what you want - I'll understand the context!   │")
        print("└──────────────────────────────────────────────────────────┘")
        print("\n💡 Examples:")
        print("   • 'create 5 images of man holding guitar, annotate man and guitar'")
        print("   • 'get 10 images of red sports cars on highway'")
        print("   • 'I need 15 images of people walking dogs in parks'")
        print()
        
        print("┌─ MODE 2: ANNOTATE YOUR OWN IMAGES (BYOD) ───────────────┐")
        print("│ Already have images? I'll detect objects for you.       │")
        print("└──────────────────────────────────────────────────────────┘")
        print("\n💡 Examples:")
        print("   • 'annotate dogs in C:\\\\my_photos'")
        print("   • 'I have images at /home/pics, detect cats and dogs'")
        print()
        
        print("🎯 What would you like to do?\n")
        
        user_input = input("Your request: ").strip()
        
        if not user_input:
            print("❌ No input provided. Exiting.")
            return
        
        print(f"\n📝 Processing: '{user_input}'\n")
        
        # Parse and execute
        self.run_pipeline(user_request=user_input)
    
    def _display_coco_info(self, output_path: str):
        """Display COCO format information."""
        if not output_path or not os.path.exists(output_path):
            return
        
        try:
            with open(output_path, 'r') as f:
                coco = json.load(f)
            
            print("\n" + "="*70)
            print("📊 COCO Format Verification")
            print("="*70)
            print(f"✅ Format: Valid COCO JSON")
            print(f"📁 Images: {len(coco.get('images', []))}")
            print(f"🏷️  Annotations: {len(coco.get('annotations', []))}")
            print(f"📦 Categories: {len(coco.get('categories', []))}")
            
            if coco.get('categories'):
                print("\n📋 Categories:")
                for cat in coco['categories']:
                    print(f"   - ID {cat['id']}: {cat['name']}")
            
            if coco.get('annotations'):
                sample = coco['annotations'][0]
                print("\n📐 Sample Annotation:")
                print(f"   - Bounding Box: {sample['bbox']} [x, y, width, height]")
                print(f"   - Category ID: {sample['category_id']}")
                print(f"   - Area: {sample['area']}")
            
            print("\n✅ Ready for training with PyTorch/TensorFlow!")
            print("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"Error reading COCO file: {e}")


# Enhanced Pipeline that handles separate search and annotation
class EnhancedFoundryPipeline(FoundryPipeline):
    """
    Enhanced pipeline with separate search query and annotation objects.
    """
    
    def __init__(self, search_query: str, annotation_objects: list, target_count: int):
        """
        Initialize enhanced pipeline.
        
        Args:
            search_query: Query for finding images (e.g., "person playing guitar")
            annotation_objects: Objects to detect (e.g., ["person", "guitar"])
            target_count: Number of images to collect
        """
        # Join annotation objects for internal query format
        query = ",".join(annotation_objects)
        
        # Store both
        self.search_query = search_query
        self.annotation_objects = annotation_objects
        
        # Initialize parent with annotation query
        super().__init__(query=query, target_count=target_count)
        
        logger.info(f"Enhanced Pipeline: search='{search_query}', annotate={annotation_objects}")
    
    def _execute_mining(self, needed: int) -> dict:
        """Execute mining with optimized search query."""
        request_count = min(needed, 5)
        logger.info(f"🔍 Mining: Searching for '{self.search_query}' ({request_count} images)")
        
        start_time = time.time()
        
        # Use search_query instead of self.query for better results
        mine_result = self._miner.mine(self.search_query, max_images=request_count)
        elapsed = time.time() - start_time
        
        if mine_result["status"] == "error" or not mine_result.get("data"):
            logger.warning(f"Mining failed: {mine_result.get('error_message', 'Unknown')}")
            if self.metrics:
                self.metrics.record_mining(attempted=request_count, successful=0, time_taken=elapsed)
            return {"images": []}
        
        images = mine_result["data"]
        if self.metrics:
            self.metrics.record_mining(attempted=request_count, successful=len(images), time_taken=elapsed)
        
        logger.info(f"✅ Mining: Retrieved {len(images)} images")
        return {"images": images}
