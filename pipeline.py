"""
Foundry Pipeline - Entry Point

AI-powered dataset creation using Google ADK workflow agents.

Architecture:
    LoopAgent
      └─ SequentialAgent
          ├─ MinerAgent (search images)
          ├─ CuratorAgent (validate quality)
          ├─ AnnotatorAgent (create bboxes)
          └─ CheckProgressAgent (verify target)

Usage:
    # Standard mode
    python pipeline.py --query "dog" --count 10
    
    # Multi-object
    python pipeline.py --query "dog,cat,car" --count 15
    
    # BYOD mode (annotate your own images)
    python pipeline.py --dir ./my_images --query "dog"
    
    # Interactive mode
    python pipeline.py
    
    # With config file
    python pipeline.py --config config.yaml
"""

import os
from dotenv import load_dotenv
import argparse
import google.generativeai as genai

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize logging
from utils.logger import setup_logging
setup_logging()

# Initialize config and features
from utils.config_loader import initialize_config
from utils.pipeline_features import initialize_pipeline_features
from core.orchestrator import MainAgent


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("🤖 FOUNDRY - AI-Powered Dataset Creation")
    print("="*70)
    print("Architecture: Google ADK Workflow Agents")
    print("  LoopAgent → SequentialAgent → [Mine, Curate, Annotate, Check]")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Foundry: AI-Powered Dataset Creation with Google ADK",
        epilog="""
Examples:
  # Standard mode
  python pipeline.py --query dog --count 10
  
  # Multi-object detection
  python pipeline.py --query "dog,cat,bird" --count 20
  
  # BYOD mode (annotate your own images)
  python pipeline.py --dir ./my_images --query dog
  
  # With quality loop (slower but better annotations)
  python pipeline.py --query car --count 15 --enable-quality-loop
  
  # With config file
  python pipeline.py --config config.yaml
  
  # Interactive mode (no arguments)
  python pipeline.py
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Config file
    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML config file"
    )
    
    # Main arguments
    parser.add_argument(
        "--request",
        type=str,
        help="Natural language request (e.g., 'find 5 images of cats')"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Object query (e.g., 'dog' or 'dog,cat' for multiple)"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        help="Number of images to collect"
    )
    
    parser.add_argument(
        "--dir",
        type=str,
        help="Directory path for BYOD mode (annotate your own images)"
    )
    
    # Advanced features
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Disable metrics collection"
    )
    
    parser.add_argument(
        "--enable-quality-loop",
        action="store_true",
        help="Enable iterative quality refinement (slower but better)"
    )
    
    parser.add_argument(
        "--quality-iterations",
        type=int,
        help="Max iterations for quality loop (default: 2)"
    )
    
    parser.add_argument(
        "--validation-method",
        type=str,
        choices=["coordinate", "visual", "hybrid"],
        help="Quality validation method: coordinate (fast), visual (accurate), hybrid (best)"
    )
    
    parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Show detailed metrics summary"
    )
    
    args = parser.parse_args()
    
    # Initialize config
    config = initialize_config(config_path=args.config, args=args)
    
    # Print config summary if file was used
    if args.config:
        config.print_summary()
    
    # Initialize pipeline features
    features = initialize_pipeline_features(
        enable_metrics=config.get('metrics.enabled', True),
        enable_quality_loop=config.get('quality_loop.enabled', False),
        quality_loop_iterations=config.get('quality_loop.max_iterations', 2),
        validation_method=config.get('quality_loop.validation_method', 'coordinate')
    )
    
    # Print header and feature status
    print_header()
    
    if config.get('quality_loop.enabled'):
        print("🔄 Quality Refinement Loop: ENABLED")
        print(f"   → Max iterations: {config.get('quality_loop.max_iterations')}")
        print(f"   → Validation: {config.get('quality_loop.validation_method')}")
        print("   ⚠️  This improves quality but increases processing time\n")
    
    if config.get('metrics.enabled'):
        print("📊 Metrics Collection: ENABLED")
        print("   Tracking: mining, curation, annotation, engineering\n")
    
    # Initialize MainAgent (uses ADK workflow agents)
    agent = MainAgent()
    
    # Get pipeline settings
    query = config.get('pipeline.query')
    count = config.get('pipeline.count')
    request = config.get('pipeline.request')
    mode = config.get('pipeline.mode')
    image_dir = config.get('pipeline.image_dir')
    
    # Determine mode and execute
    if not any([request, query, image_dir]):
        # Interactive mode
        agent.run_interactive_mode()
        
    elif mode == 'byod' or image_dir:
        # BYOD mode: Annotate existing images
        if not query:
            print("❌ Error: --query required for BYOD mode")
            print("Example: python pipeline.py --dir ./images --query dog")
            return
        
        if not os.path.exists(image_dir):
            print(f"❌ Error: Directory not found: {image_dir}")
            return
        
        agent.run_byod_mode(image_dir=image_dir, query=query)
        
    else:
        # Standard mode: Mine, curate, annotate
        if not query and not request:
            print("❌ Error: --query or --request required for standard mode")
            print("Example: python pipeline.py --query dog --count 10")
            return
        
        agent.run_pipeline(user_request=request, query=query, count=count)
    
    # Show metrics summary if requested
    if config.get('metrics.show_summary') or config.get('quality_loop.enabled'):
        features.print_metrics_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting gracefully.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
