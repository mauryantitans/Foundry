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

# Initialize advanced pipeline features
from utils.pipeline_features import initialize_pipeline_features

from agents.main_agent import MainAgent

def main():
    parser = argparse.ArgumentParser(description="Foundry AI-Powered Dataset Creation System")
    
    # Original arguments
    parser.add_argument("--request", type=str, help="Natural language request (e.g., 'find 5 images of cats')")
    parser.add_argument("--query", type=str, help="Object query (e.g., 'cats' or 'dog,cat' for multiple objects)")
    parser.add_argument("--count", type=int, help="Number of images")
    parser.add_argument("--dir", type=str, help="Directory path containing images to annotate (BYOD mode)")
    
    # Advanced feature arguments
    parser.add_argument("--no-metrics", action="store_true", help="Disable metrics collection")
    parser.add_argument("--enable-quality-loop", action="store_true", help="Enable quality refinement loop (slower but better quality)")
    parser.add_argument("--quality-iterations", type=int, default=2, help="Max iterations for quality loop (default: 2)")
    parser.add_argument("--show-metrics", action="store_true", help="Show detailed metrics summary at end")
    
    args = parser.parse_args()
    
    # Initialize pipeline features with command-line options
    features = initialize_pipeline_features(
        enable_metrics=not args.no_metrics,
        enable_quality_loop=args.enable_quality_loop,
        quality_loop_iterations=args.quality_iterations
    )
    
    # Display feature status
    if args.enable_quality_loop:
        print("🔄 Quality Refinement Loop: ENABLED")
        print(f"   → Max iterations: {args.quality_iterations}")
        print("   ⚠️  This will increase processing time but improve annotation quality\n")
    
    agent = MainAgent()
    
    # Interactive mode: No arguments provided
    if not any([args.request, args.query, args.count, args.dir]):
        agent.run_interactive_mode()
    elif args.dir:
        # BYOD Mode: Process directory of images
        if not args.query:
            print("❌ Error: --query is required when using --dir mode")
            return
        agent.run_byod_mode(image_dir=args.dir, query=args.query)
    else:
        # Standard mode: Mine, curate, and annotate
        agent.run_pipeline(user_request=args.request, query=args.query, count=args.count)
    
    # Show metrics summary if requested
    if args.show_metrics or args.enable_quality_loop:
        features.print_metrics_summary()

if __name__ == "__main__":
    main()
