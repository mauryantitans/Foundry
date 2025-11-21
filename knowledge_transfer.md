# Foundry Codebase Knowledge Transfer

This document provides a detailed overview of the Foundry codebase, explaining the architecture, component interactions, and specific code implementations. It is designed to help new developers understand how the multi-agent system functions.

## 1. High-Level Architecture

Foundry operates as a **hierarchical multi-agent system**. 

- **Root Level**: The `MainAgent` acts as the controller. It does not perform the actual work of mining or annotating but instead plans and delegates tasks to sub-agents.
- **Sub-Agent Level**: Specialized agents (`MinerAgent`, `CuratorAgent`, `AnnotatorAgent`) perform specific phases of the pipeline. They are "AI-driven," meaning they use LLMs/VLMs to make decisions or process data.
- **Tool Level**: Agents are equipped with tools (e.g., `SearchTool`) to interact with external APIs.

## 2. Core Components

### 2.1 Base Agent (`agents/base_agent.py`)
This is the foundation for all AI agents in the system.
- **Purpose**: Wraps the `google.generativeai` library to provide a consistent interface for agents.
- **Key Features**:
    - **`__init__`**: Accepts `name`, `instructions` (system prompt), and `tools`. It configures the Gemini model with these parameters.
    - **`run(input_text)`**: Sends a message to the model and returns the text response. It handles the "thinking" state and error catching.
    - **Tool Integration**: It automatically enables function calling if tools are provided.

### 2.2 Main Agent (`agents/main_agent.py`)
- **Role**: Orchestrator.
- **Key Logic**:
    - **Request Parsing**: Uses the LLM to extract structured data (`query`, `count`) from natural language requests.
    - **Execution Loop**: Implements a `while` loop to guarantee the target count.
        - It calculates `needed = count - current`.
        - It requests `needed * buffer` images from the Miner to account for attrition during curation.
        - It calls Miner -> Curator -> Annotator in sequence.
        - It aggregates results into `final_dataset`.

### 2.3 Miner Agent (`agents/miner.py`)
- **Role**: Data Acquisition.
- **Key Logic**:
    - **Tool Use**: It has access to `google_search_images` (from `tools/search_tool.py`).
    - **State Management**: Maintains `self.search_index` to track pagination across multiple calls. This ensures that if the MainAgent asks for more images in loop 2, the Miner doesn't return the same results from loop 1.
    - **Deduplication**: Maintains `self.seen_hashes` (perceptual hash) to detect and remove duplicate images immediately after download.

### 2.4 Curator Agent (`agents/curator.py`)
- **Role**: Data Filtering.
- **Key Logic**:
    - **VLM Verification**: It sends each image + the query to the VLM with a prompt: "Does this image contain {query}? Answer strictly YES or NO."
    - **Filtering**: Only images with a "YES" response are moved to the `curated` folder and passed to the next stage.

### 2.5 Annotator Agent (`agents/annotator.py`)
- **Role**: Data Labeling.
- **Key Logic**:
    - **VLM Annotation**: Asks the VLM to "Return bounding boxes for ALL instances of {query}...".
    - **JSON Parsing**: Robustly parses the JSON output from the model to extract bounding box coordinates (normalized 0-1000).

### 2.6 Engineer Agent (`agents/engineer.py`)
- **Role**: Data Formatting.
- **Key Logic**:
    - **Deterministic**: Unlike other agents, this is a Python class without an LLM loop. This is intentional because file format specifications (like COCO JSON) are strict and better handled by code than probabilistic models.
    - **Coordinate Conversion**: Converts the normalized (0-1000) coordinates from the Annotator into absolute pixel coordinates required by COCO.

### 2.7 Search Tool (`tools/search_tool.py`)
- **Purpose**: Provides Google Custom Search capabilities.
- **Key Logic**:
    - Wraps `googleapiclient`.
    - Accepts `start_index` for pagination.
    - Returns a list of image URLs.

## 3. Pipeline Flow (`pipeline.py`)

The `pipeline.py` script is the entry point.
1.  **Setup**: Loads environment variables and configures Gemini.
2.  **CLI Parsing**: Uses `argparse` to accept `--query`, `--count`, and `--request`.
3.  **Initialization**: Instantiates the `MainAgent`.
4.  **Execution**: Calls `agent.run_pipeline()`.

## 4. Key Concepts for Extension

- **Adding a new Tool**: Define a python function in `tools/`, import it in the agent, and pass it to the `super().__init__(..., tools=[new_tool])`.
- **Changing the Model**: The `BaseAgent` defaults to `gemini-2.0-flash`. You can override this in the `__init__` of any specific agent.
- **Improving Curation**: You could add a "Feedback Loop" where the Curator explains *why* an image was rejected, which could be logged for analysis.
