import os
from agents.base_agent import Agent
from agents.miner import MinerAgent
from agents.curator import CuratorAgent
from agents.annotator import AnnotatorAgent
from agents.engineer import EngineerAgent

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
        # EngineerAgent is still a functional helper for now, or we can wrap it too.
        # Keeping it simple as it's the final step.
        self.engineer = EngineerAgent(query="placeholder") 

    def run_pipeline(self, user_request=None, query=None, count=None):
        print(f"🤖 MainAgent: Processing request...")
        
        if query and count:
            print(f"📋 MainAgent: Using provided arguments -> Mine {count} images of '{query}'")
        elif user_request:
            print(f"🤖 MainAgent: Parsing request: '{user_request}'")
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
                print(f"❌ MainAgent: Failed to parse request. Using defaults. Error: {e}")
                query = "unknown"
                count = 2
                
            print(f"📋 MainAgent: Plan -> Mine {count} images of '{query}'")
        else:
            print("❌ MainAgent: No request or arguments provided.")
            return

        # 2. Execution Loop
        final_dataset = {}
        loop_count = 0
        max_loops = 5 # Safety break
        
        while len(final_dataset) < count and loop_count < max_loops:
            loop_count += 1
            needed = count - len(final_dataset)
            print(f"🔄 MainAgent: Loop {loop_count} - Need {needed} more images...")
            
            # Request a bit more than needed to account for filtering
            request_count = max(needed + 2, int(needed * 1.5))
            
            # Step 1: Mine
            mined_images = self.miner.mine(query, max_images=request_count)
            if not mined_images:
                print("   ⚠️ MainAgent: Miner returned no images. Stopping.")
                break
                
            # Step 2: Curate
            curated_images = self.curator.curate(query, mined_images)
            if not curated_images:
                print("   ⚠️ MainAgent: Curator filtered all images in this batch.")
                continue
                
            # Step 3: Annotate
            annotations = self.annotator.annotate(query, curated_images)
            
            # Add to final dataset
            for filename, data in annotations.items():
                if len(final_dataset) < count:
                    final_dataset[filename] = data
                else:
                    break
        
        # Step 4: Engineer (Save)
        if not final_dataset:
             print("❌ MainAgent: Failed to create dataset.")
             return

        print(f"✨ MainAgent: Pipeline finished. Collected {len(final_dataset)} images.")
        
        # Update engineer query
        self.engineer.query = query
        for filename, data in final_dataset.items():
            self.engineer.process_item(filename, data)
        self.engineer.save()
        
        print("✨ MainAgent: Dataset saved successfully!")
