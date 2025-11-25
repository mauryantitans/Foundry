import os
from dotenv import load_dotenv
import argparse
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize logging
from utils.logger import setup_logging
setup_logging()

# Initialize config and advanced pipeline features
from utils.config_loader import initialize_config
from utils.pipeline_features import initialize_pipeline_features

from agents.main_agent import MainAgent

def main():
    parser = argparse.ArgumentParser(description="Foundry AI-Powered Dataset Creation System")
    
    # Config file argument
    parser.add_argument("--config", type=str, help="Path to YAML config file")
    
    # Original arguments
    parser.add_argument("--request", type=str, help="Natural language request (e.g., 'find 5 images of cats')")
    parser.add_argument("--query", type=str, help="Object query (e.g., 'cats' or 'dog,cat' for multiple objects)")
    parser.add_argument("--count", type=int, help="Number of images")
    parser.add_argument("--dir", type=str, help="Directory path containing images to annotate (BYOD mode)")
    
    # Advanced feature arguments
    parser.add_argument("--no-metrics", action="store_true", help="Disable metrics collection")
    parser.add_argument("--enable-quality-loop", action="store_true", help="Enable quality refinement loop (slower but better quality)")
    parser.add_argument("--quality-iterations", type=int, help="Max iterations for quality loop (default: 2)")
    parser.add_argument("--validation-method", type=str, choices=["coordinate", "visual", "hybrid"],
                       help="Quality loop validation method: coordinate (fast), visual (accurate), hybrid (best)")
    parser.add_argument("--show-metrics", action="store_true", help="Show detailed metrics summary at end")
    
    args = parser.parse_args()
    
    # Initialize config (load from file if provided, then override with CLI args)
    config = initialize_config(config_path=args.config, args=args)
    
    # Print config summary if config file was used
    if args.config:
        config.print_summary()
    
    # Initialize pipeline features using config values
    features = initialize_pipeline_features(
        enable_metrics=config.get('metrics.enabled', True),
        enable_quality_loop=config.get('quality_loop.enabled', False),
        quality_loop_iterations=config.get('quality_loop.max_iterations', 2),
        validation_method=config.get('quality_loop.validation_method', 'coordinate')
    )
    
    # Display feature status
    if config.get('quality_loop.enabled'):
        print("🔄 Quality Refinement Loop: ENABLED")
        print(f"   → Max iterations: {config.get('quality_loop.max_iterations')}")
        print(f"   → Validation method: {config.get('quality_loop.validation_method')}")
        print("   ⚠️  This will increase processing time but improve annotation quality\n")
    
    agent = MainAgent()
    
    # Get pipeline settings from config
    query = config.get('pipeline.query')
    count = config.get('pipeline.count')
    request = config.get('pipeline.request')
    mode = config.get('pipeline.mode')
    image_dir = config.get('pipeline.image_dir')
    
    # Interactive mode: If no specific task (query/request/dir) is provided, run interactive
    # We ignore 'count' here because it might be a default setting in config
    if not any([request, query, image_dir]):
        agent.run_interactive_mode()
    elif mode == 'byod' or image_dir:
        # BYOD Mode: Process directory of images
        if not query:
            print("❌ Error: query is required when using BYOD mode")
            return
        agent.run_byod_mode(image_dir=image_dir, query=query)
    else:
        # Standard mode: Mine, curate, and annotate
        agent.run_pipeline(user_request=request, query=query, count=count)
    
    # Show metrics summary if requested
    if config.get('metrics.show_summary') or config.get('quality_loop.enabled'):
        features.print_metrics_summary()

if __name__ == "__main__":
    main()
