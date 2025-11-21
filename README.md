# Foundry: Multi-Agent Object Detection Dataset Generator

Foundry is an AI-driven multi-agent system designed to automatically create object detection datasets. It orchestrates a team of specialized AI agents to mine, curate, annotate, and engineer high-quality datasets from the web based on simple natural language requests.

## 🤖 The Agent Team

Foundry is built on a robust multi-agent architecture:

1.  **MainAgent (The Orchestrator)**: 
    - The team lead. It parses your natural language request (e.g., "I need 50 images of red sports cars") to understand the goal.
    - It coordinates the workflow, ensuring the target number of images is reached by looping through the mining and curation process.

2.  **MinerAgent (The Researcher)**:
    - **Role**: Finds raw images on the web.
    - **Capabilities**: Uses a custom **SearchTool** (Google Custom Search API) to find relevant images. It intelligently handles pagination to find fresh results and performs hash-based deduplication to ensure variety.

3.  **CuratorAgent (The Quality Control)**:
    - **Role**: Filters the mined images.
    - **Capabilities**: Uses a Vision Language Model (VLM) to visually inspect each image and verify if it strictly matches the user's query. It discards irrelevant or low-quality images.

4.  **AnnotatorAgent (The Labeler)**:
    - **Role**: Detects objects and creates bounding boxes.
    - **Capabilities**: Uses a VLM to analyze the curated images and generate precise bounding box annotations for the target objects.

5.  **EngineerAgent (The Data Engineer)**:
    - **Role**: Formats and saves the data.
    - **Capabilities**: Compiles the images and annotations into standard formats like COCO JSON, ensuring the dataset is ready for training ML models.

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.10+**
2.  **Google Cloud Project** with Custom Search API enabled.
3.  **Google AI Studio API Key** (for Gemini models).

### Obtaining API Keys

1.  **Gemini API Key**:
    - Go to [Google AI Studio](https://aistudio.google.com/).
    - Click on "Get API key" and create a new key.
2.  **Google Custom Search API Key**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project (or select an existing one).
    - Enable the "Custom Search API".
    - Go to "Credentials" and create an API key.
3.  **Search Engine ID (CX)**:
    - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/).
    - Create a new search engine.
    - Enable "Image search" in the settings.
    - Copy the "Search engine ID" (cx).

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your `.env` file:
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    GOOGLE_SEARCH_API_KEY=your_google_search_api_key
    GOOGLE_SEARCH_CX=your_custom_search_engine_id
    ```

### Usage

Run the pipeline with a simple command:

**Option 1: Specific Query and Count**
```bash
python pipeline.py --query "golden retriever" --count 10
```

**Option 2: Natural Language Request**
```bash
python pipeline.py --request "I need 10 images of laptop dataset"
```

- `--query`: The object you want to detect (e.g., "cat", "red apple", "stop sign").
- `--count`: The number of valid, annotated images you want in your final dataset.
- `--request`: A natural language description of your goal. The MainAgent will parse this to extract the query and count.

The system will run until it produces the requested number of images (or hits a safety limit).

## 📂 Output

The generated dataset is saved in `data/output`:
- `coco.json`: Annotations in COCO format.
- Images are stored in `data/curated`.

## 🛠️ Architecture Details

- **BaseAgent**: A custom wrapper around `google-generativeai` that enables agents to have distinct personas, instructions, and tool-using capabilities.
- **Tools**: Modular functions (like `google_search_images`) that agents can call to interact with the external world.
