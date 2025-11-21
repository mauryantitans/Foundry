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

from agents.main_agent import MainAgent

def main():
    parser = argparse.ArgumentParser(description="Foundry Multi-Agent System")
    parser.add_argument("--request", type=str, help="Natural language request (e.g., 'find 5 images of cats')")
    parser.add_argument("--query", type=str, help="Object query (e.g., 'cats')")
    parser.add_argument("--count", type=int, help="Number of images")
    args = parser.parse_args()
    
    agent = MainAgent()
    agent.run_pipeline(user_request=args.request, query=args.query, count=args.count)

if __name__ == "__main__":
    main()
