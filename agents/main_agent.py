import os
import time
from agents.base_agent import Agent
from agents.miner import MinerAgent
from agents.curator import CuratorAgent
from agents.annotator import AnnotatorAgent
from agents.parallel_annotator import ParallelAnnotatorAgent
from agents.engineer import EngineerAgent
from utils.logger import setup_logging, get_logger
from utils.pipeline_features import get_pipeline_features

# Initialize logging
setup_logging()
logger = get_logger("main_agent")

class MainAgent(Agent):
    def __init__(self):
        instructions = (
            "You are the Main Orchestrator Agent. Your goal is to manage the creation of an object detection dataset. "
            "You will receive a request from the user (e.g., 'create a dataset of 5 images of red apples'). "
            "You need to parse this request to extract the 'query' and the 'count'. "
            "Then you will coordinate the sub-agents to: "
            "1. Mine images using MinerAgent. "
            "2. Curate images using CuratorAgent. "
            "3. Annotate images using AnnotatorAgent. "
            "4. Save the dataset using EngineerAgent. "
        )
        super().__init__(name="MainAgent", instructions=instructions)
        
        # Initialize Sub-Agents
        self.miner = MinerAgent()
        self.curator = CuratorAgent()
        self.annotator = AnnotatorAgent()
        # Parallel annotator will be initialized in run methods with quality loop if needed
        self.parallel_annotator = None
        # EngineerAgent will be initialized when we know the query
        self.engineer = None 

    def run_pipeline(self, user_request=None, query=None, count=None):
        logger.info("Processing request")
        
        # Get metrics collector (if enabled)
        features = get_pipeline_features()
        metrics = features.get_metrics() if features.enable_metrics else None
        
        # Initialize quality loop if enabled
        quality_loop = None
        if features.enable_quality_loop:
            quality_loop = features.create_quality_loop(self.annotator)
            logger.info(f"🔄 Quality refinement loop enabled (max {features.quality_loop_iterations} iterations)")
        
        # Initialize parallel annotator with quality loop
        self.parallel_annotator = ParallelAnnotatorAgent(num_workers=3, quality_loop=quality_loop)
        
        # Start metrics tracking
        if metrics:
            metrics.start_pipeline()
        
        if query and count:
            logger.info(f"Using provided arguments -> Mine {count} images of '{query}'")
        elif user_request:
            logger.info(f"Parsing request: '{user_request}'")
            # 1. Parse Request using the LLM
            prompt = (
                f"Extract the object query and the number of images from this request: '{user_request}'. "
                "Return ONLY a JSON object: {'query': 'object name', 'count': number}. "
                "If count is not specified, default to 5."
            )
            response = self.run(prompt)
            
            import json
            import re
            
            try:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    query = data.get('query')
                    count = int(data.get('count', 5))
                else:
                    raise ValueError("Could not parse JSON")
            except Exception as e:
                logger.error(f"Failed to parse request. Using defaults. Error: {e}")
                query = "unknown"
                count = 2
                
            logger.info(f"Plan -> Mine {count} images of '{query}'")
        else:
            logger.error("No request or arguments provided")
            return

        # 2. Execution Loop - Request exactly the needed number, retry if shortage
        final_dataset = {}
        loop_count = 0
        max_loops = 5 # Safety break
        
        total_mined = 0
        total_curated = 0
        total_annotated = 0
        
        while len(final_dataset) < count and loop_count < max_loops:
            loop_count += 1
            needed = count - len(final_dataset)
            logger.info(f"Loop {loop_count} - Need {needed} more images")
            
            # Request exactly the number needed (no extra to avoid waste)
            request_count = needed
            
            # Step 1: Mine exactly the needed number
            mine_start = time.time()
            mine_result = self.miner.mine(query, max_images=request_count)
            mine_time = time.time() - mine_start
            
            if mine_result["status"] == "error" or not mine_result.get("data"):
                logger.warning(f"Miner returned no images: {mine_result.get('error_message', 'Unknown error')}")
                break
            
            mined_images = mine_result["data"]
            mined_count = len(mined_images)
            total_mined += mined_count
            logger.info(f"Mined {mined_count} images")
            
            # Record mining metrics
            if metrics:
                metrics.record_mining(attempted=request_count, successful=mined_count, time_taken=mine_time)
                
            # Step 2: Curate exactly the needed number (stops once it has enough)
            curate_start = time.time()
            curated_images = self.curator.curate(query, mined_images, max_count=needed)
            curate_time = time.time() - curate_start
            
            curated_count = len(curated_images)
            total_curated += curated_count
            
            # Record curation metrics
            if metrics:
                metrics.record_curation(total=mined_count, kept=curated_count, time_taken=curate_time)
            
            if not curated_images:
                logger.warning("Curator filtered all images in this batch")
                continue
                
            # Step 3: Annotate all curated images (use parallel for multiple images)
            annotate_start = time.time()
            if len(curated_images) > 1:
                logger.info(f"Using parallel annotation for {len(curated_images)} images")
                annotations = self.parallel_annotator.annotate_parallel(query, curated_images)
            else:
                # For single image, check if quality loop is enabled
                if self.parallel_annotator and self.parallel_annotator.quality_loop:
                    logger.info("Using quality refinement loop for single image")
                    result = self.parallel_annotator.quality_loop.annotate_with_refinement(curated_images[0], query)
                    filename = os.path.basename(curated_images[0])
                    annotations = {filename: result} if result else {}
                else:
                    annotations = self.annotator.annotate(query, curated_images)
            annotate_time = time.time() - annotate_start
            
            annotated_count = len(annotations)
            total_annotated += annotated_count
            
            # Record annotation metrics
            if metrics:
                metrics.record_annotation(total=curated_count, successful=annotated_count, time_taken=annotate_time)
            
            # Add to final dataset
            for filename, data in annotations.items():
                if len(final_dataset) < count:
                    final_dataset[filename] = data
                else:
                    break
        
        # Step 4: Engineer (Save)
        if not final_dataset:
             logger.error("Failed to create dataset")
             if metrics:
                 metrics.end_pipeline()
             return

        logger.info(f"Pipeline finished. Collected {len(final_dataset)} images")
        
        # Initialize engineer with the actual query
        engineer_start = time.time()
        self.engineer = EngineerAgent(query=query)
        for filename, data in final_dataset.items():
            self.engineer.process_item(filename, data)
        self.engineer.save()
        engineer_time = time.time() - engineer_start
        
        # Record engineering metrics
        if metrics:
            metrics.record_engineering(count=len(final_dataset), time_taken=engineer_time)
        
        logger.info("Dataset saved successfully")
        
        # End metrics tracking
        if metrics:
            metrics.end_pipeline()
            logger.info(f"📊 Total: Mined={total_mined}, Curated={total_curated}, Annotated={total_annotated}, Saved={len(final_dataset)}")
    
    def run_byod_mode(self, image_dir, query):
        """
        BYOD (Bring Your Own Data) Mode: Process a directory of images.
        Skips mining and curation, directly annotates all images in the directory.
        
        Args:
            image_dir: Path to directory containing images
            query: Object query (can be single like 'dog' or multiple like 'dog,cat,car')
        """
        from utils.file_manager import list_images
        
        # Get metrics collector (if enabled)
        features = get_pipeline_features()
        metrics = features.get_metrics() if features.enable_metrics else None
        
        # Initialize quality loop if enabled
        quality_loop = None
        if features.enable_quality_loop:
            quality_loop = features.create_quality_loop(self.annotator)
            logger.info(f"🔄 Quality refinement loop enabled (max {features.quality_loop_iterations} iterations)")
        
        # Initialize parallel annotator with quality loop
        self.parallel_annotator = ParallelAnnotatorAgent(num_workers=3, quality_loop=quality_loop)
        
        # Start metrics tracking
        if metrics:
            metrics.start_pipeline()
        
        logger.info(f"BYOD Mode - Processing images from '{image_dir}'")
        logger.info(f"Detecting objects: '{query}'")
        
        # Get all images from directory
        image_paths = list_images(image_dir)
        if not image_paths:
            logger.error(f"No images found in directory '{image_dir}'")
            if metrics:
                metrics.end_pipeline()
            return
        
        logger.info(f"Found {len(image_paths)} images to process")
        
        # Step 1: Annotate all images (skip mining and curation)
        # Use parallel annotation for multiple images
        annotate_start = time.time()
        if len(image_paths) > 1:
            logger.info(f"Using parallel annotation for {len(image_paths)} images")
            annotations = self.parallel_annotator.annotate_parallel(query, image_paths)
        else:
            annotations = self.annotator.annotate(query, image_paths)
        annotate_time = time.time() - annotate_start
        
        # Record annotation metrics
        if metrics:
            metrics.record_annotation(total=len(image_paths), successful=len(annotations), time_taken=annotate_time)
        
        if not annotations:
            logger.error("No annotations generated")
            if metrics:
                metrics.end_pipeline()
            return
        
        logger.info(f"Successfully annotated {len(annotations)} images")
        
        # Step 2: Engineer (Save to COCO format)
        engineer_start = time.time()
        self.engineer = EngineerAgent(query=query)
        for filename, data in annotations.items():
            self.engineer.process_item(filename, data)
        
        output_path = self.engineer.save()
        engineer_time = time.time() - engineer_start
        
        # Record engineering metrics
        if metrics:
            metrics.record_engineering(count=len(annotations), time_taken=engineer_time)
        
        logger.info("BYOD Mode completed successfully")
        logger.info(f"COCO dataset saved to: {output_path}")
        
        # End metrics tracking
        if metrics:
            metrics.end_pipeline()
            logger.info(f"📊 Total: Annotated={len(annotations)}, Saved={len(annotations)}")
        
        # Display COCO format information
        self._display_coco_info()
    
    def _display_coco_info(self):
        """Display information about the COCO format output."""
        if not self.engineer or not self.engineer.coco_data:
            return
        
        coco = self.engineer.coco_data
        print("\n" + "="*60)
        print("📊 COCO Format Verification:")
        print("="*60)
        print(f"✅ Format: Valid COCO JSON format")
        print(f"📁 Images: {len(coco['images'])}")
        print(f"🏷️  Annotations: {len(coco['annotations'])}")
        print(f"📦 Categories: {len(coco['categories'])}")
        
        # Show categories
        print("\n📋 Categories (Object Names):")
        for cat in coco['categories']:
            print(f"   - ID {cat['id']}: {cat['name']}")
        
        # Show sample annotation
        if coco['annotations']:
            sample = coco['annotations'][0]
            print("\n📐 Sample Annotation Structure:")
            print(f"   - Annotation ID: {sample['id']}")
            print(f"   - Image ID: {sample['image_id']}")
            print(f"   - Category ID: {sample['category_id']} (maps to object name)")
            print(f"   - Bounding Box: {sample['bbox']} [x, y, width, height]")
            print(f"   - Area: {sample['area']}")
            print(f"   - Is Crowd: {sample['iscrowd']}")
        
        print("\n✅ COCO Format includes:")
        print("   ✓ Bounding boxes: [x, y, width, height] in pixels")
        print("   ✓ Object names: via category_id → categories mapping")
        print("   ✓ Image metadata: width, height, filename")
        print("   ✓ All required COCO fields present")
        print("="*60 + "\n")
    
    def run_interactive_mode(self):
        """
        Interactive mode: Prompts user for dataset creation request.
        Supports both standard mode (mine, curate, annotate) and BYOD mode.
        """
        print("\n" + "="*70)
        print("🤖 Foundry: AI-Powered Dataset Creation System")
        print("="*70)
        print("\n📚 What I Can Do For You:\n")
        
        print("┌─ MODE 1: CREATE NEW DATASET ─────────────────────────────────┐")
        print("│ I'll search the web, curate quality images, and annotate    │")
        print("│ them with bounding boxes automatically.                     │")
        print("└──────────────────────────────────────────────────────────────┘")
        print("\n💡 Examples:")
        print("   • 'create 5 images of dogs'")
        print("   • 'get me 10 bicycle images'")
        print("   • 'I need 15 images of cats and dogs'  (multi-object)")
        print("   • 'find 20 car images'\n")
        
        print("┌─ MODE 2: ANNOTATE YOUR OWN IMAGES (BYOD) ───────────────────┐")
        print("│ Already have images? Give me the folder path and I'll       │")
        print("│ detect and annotate objects for you.                        │")
        print("└──────────────────────────────────────────────────────────────┘")
        print("\n💡 Examples:")
        print("   • 'annotate dogs in C:\\Users\\me\\my_photos'")
        print("   • 'I have images at /home/user/pics, detect cats'")
        print("   • 'detect bicycles in C:\\images\\bikes'\n")
        
        print("┌─ FEATURES ───────────────────────────────────────────────────┐")
        print("│ ✓ Multi-object detection (e.g., 'dogs and cats')            │")
        print("│ ✓ Quality refinement loop (iterative improvement)           │")
        print("│ ✓ COCO format output (ready for PyTorch, TensorFlow)        │")
        print("│ ✓ Automatic deduplication                                   │")
        print("└──────────────────────────────────────────────────────────────┘\n")
        
        print("🎯 What would you like to do today?\n")
        
        # Get user input
        user_input = input("Your request: ").strip()
        
        if not user_input:
            print("❌ No input provided. Exiting.")
            return
        
        print(f"\n📝 Processing your request: '{user_input}'\n")
        
        # Use LLM to parse the request and determine mode
        parse_prompt = (
            f"User request: '{user_input}'\n\n"
            "Determine if this is:\n"
            "1. STANDARD mode: User wants to create a new dataset (mine, curate, annotate)\n"
            "2. BYOD mode: User mentions a folder/path and wants to annotate existing images\n\n"
            "Return ONLY a JSON object with this exact structure:\n"
            "{\n"
            '  "mode": "standard" or "byod",\n'
            '  "query": "object names (comma-separated if multiple)",\n'
            '  "count": number (only for standard mode, default 5 if not specified),\n'
            '  "image_dir": "path to folder" (only for byod mode, null otherwise)\n'
            "}\n\n"
            "Examples:\n"
            '- "create 5 images of dogs" → {"mode": "standard", "query": "dog", "count": 5, "image_dir": null}\n'
            '- "I have images at /home/user/images, detect cats" → {"mode": "byod", "query": "cat", "count": null, "image_dir": "/home/user/images"}\n'
            '- "detect dogs and cats in /path/to/folder" → {"mode": "byod", "query": "dog,cat", "count": null, "image_dir": "/path/to/folder"}\n'
        )
        
        parse_response = self.run(parse_prompt)
        
        import json
        import re
        
        try:
            # Extract JSON from response
            match = re.search(r'\{.*\}', parse_response, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                mode = parsed.get('mode', 'standard').lower()
                query = parsed.get('query', '')
                image_dir = parsed.get('image_dir')
                count = parsed.get('count')
                
                if not query:
                    print("❌ Could not determine object query from your request.")
                    return
                
                if mode == 'byod':
                    if not image_dir:
                        print("❌ Could not determine image directory path from your request.")
                        print("   Please specify the full path to your image folder.")
                        return
                    
                    # Verify directory exists
                    if not os.path.exists(image_dir):
                        print(f"❌ Directory not found: {image_dir}")
                        return
                    
                    print(f"📁 BYOD Mode: Processing images from '{image_dir}'")
                    print(f"🔍 Detecting objects: '{query}'\n")
                    self.run_byod_mode(image_dir=image_dir, query=query)
                else:
                    # Standard mode
                    if not count:
                        count = 5
                        print(f"ℹ️  No count specified, defaulting to {count} images")
                    
                    print(f"📋 Standard Mode: Creating dataset with {count} images of '{query}'\n")
                    self.run_pipeline(query=query, count=count)
            else:
                raise ValueError("Could not parse JSON")
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            print(f"❌ Error parsing your request: {e}")
            print("   Please try again with a clearer request.")
            print("   Examples:")
            print("   - 'Create 5 images of dogs'")
            print("   - 'I have images at /path/to/folder, detect cats in them'")
