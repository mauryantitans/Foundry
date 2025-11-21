# Foundry: AI-Powered Dataset Creation Agent

Foundry is an automated, multi-agent system designed to create high-quality, labeled object detection datasets (COCO format) from scratch. It leverages Google's **Gemini 2.0 Flash** Vision Language Model (VLM) and **Custom Search API** to mine, curate, and annotate images autonomously.

## 🚀 Features

*   **Automated Mining**: Searches and downloads images from the web using Google Custom Search.
*   **Intelligent Curation**: Uses Gemini VLM to filter irrelevant images and `imagehash` to remove duplicates.
*   **Auto-Annotation**: Generates bounding box annotations for specific objects using Gemini VLM.
*   **Self-Correction**: Includes a feedback loop where the AI verifies and corrects its own annotations.
*   **BYOD Mode**: "Bring Your Own Data" support to process local image directories.
*   **Rate Limiting**: Configurable "Free" and "Paid" tiers to manage API usage and prevent rate limits.
*   **COCO Output**: Exports final datasets in the standard COCO JSON format.

## 🏗️ Architecture

Foundry operates as a parallel pipeline of four specialized agents:

1.  **Miner Agent**: Acquires images via Google Search or loads local files.
2.  **Curator Agent**: Validates image content (Yes/No check) and deduplicates.
3.  **Annotator Agent**: Detects objects and generates bounding boxes (0-1000 normalized).
4.  **Engineer Agent**: Formats annotations into COCO standard and saves the dataset.


## 📂 Output

The pipeline creates a `data` directory:

*   `data/raw`: Raw downloaded images.
*   `data/curated`: Validated and deduplicated images.
*   `data/output/coco.json`: Final COCO dataset file.