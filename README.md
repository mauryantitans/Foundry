# 🤖 Foundry: AI-Powered Dataset Creation System

<div align="center">

**Automatically create high-quality object detection datasets using multi-agent AI**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage-guide) • [Documentation](#-documentation) • [Examples](#-usage-examples)

</div>

---

## 📖 Overview

Foundry is an intelligent, multi-agent system that automates the entire pipeline of creating object detection datasets. From searching the web for images to generating production-ready COCO format annotations, Foundry handles it all with minimal human intervention.

### **What Makes Foundry Special?**

🎯 **Fully Autonomous** - Mine, curate, annotate, and export datasets automatically  
🔄 **Self-Improving** - Iterative quality refinement ensures high-quality annotations  
📊 **Observable** - Comprehensive metrics track success rates and performance  
🛡️ **Robust** - Intelligent error handling with automatic retry logic  
⚡ **Efficient** - Parallel processing for fast batch operations  
🎨 **Flexible** - Single/multi-object detection, works with your own images too

---

## ✨ Features

### **Core Capabilities**

#### 🔍 **Intelligent Image Mining**
- Automated web search using Google Custom Search API
- Smart deduplication using perceptual hashing
- Configurable search parameters and pagination
- Automatic download and format conversion

#### 🎯 **AI-Powered Curation**
- Vision-based quality assessment
- Relevance filtering to ensure target objects are present
- Duplicate detection across batches
- Configurable acceptance thresholds

#### 🏷️ **Advanced Annotation**
- Single and multi-object detection support
- Normalized bounding box coordinates (0-1000 range)
- Parallel annotation for batch processing (3 concurrent workers)
- Optional quality refinement loop with validation

#### 📦 **Production-Ready Export**
- Standard COCO JSON format
- Compatible with PyTorch, TensorFlow, CVAT, LabelImg
- Includes all required metadata (categories, images, annotations)
- Automatic coordinate transformations

### **Quality & Reliability**

#### 🔄 **Quality Refinement Loop**
Iteratively improve annotation quality through automatic validation:
```
Initial Annotation → Validation → Feedback → Re-annotation → Approval
         ↑                                                      ↓
         └──────────────── (Repeat up to 3 times) ─────────────┘
```

**Benefits:**
- Ensures all object instances are detected
- Validates bounding box accuracy
- Eliminates false positives
- Provides detailed feedback for improvements
- **New:** Supports 3 validation methods:
  - **Coordinate:** Fast, checks bbox numbers
  - **Visual:** Draws boxes on image for model to see (More Accurate)
  - **Hybrid:** Combines both for maximum quality

#### 📊 **Comprehensive Metrics**
Track everything that matters:
- **Performance:** Timing for each pipeline stage
- **Success Rates:** Curation and annotation pass rates
- **Progress:** Real-time pipeline status
- **Errors:** Categorized error tracking with retry suggestions

#### ❌ **Intelligent Error Handling**
- **Structured Errors:** Category, severity, stage, and recovery info
- **Smart Retry Logic:** Automatic retries for transient failures
- **Graceful Degradation:** Skip bad items, continue processing
- **Detailed Logging:** Full stack traces for debugging

### **Operational Features**

#### ⚡ **Parallel Processing**
- 3 concurrent annotation workers for batch operations
- Thread-safe image processing
- Efficient resource utilization
- 3-4x faster than sequential processing

#### 🎨 **Flexible Input Options**

**Standard Mode:** Let Foundry find and curate images
```bash
python pipeline.py --query "dogs" --count 10
```

**BYOD Mode:** Bring Your Own Data - annotate existing images
```bash
python pipeline.py --dir "/path/to/images" --query "cats"
```

**Multi-Object Detection:** Detect multiple object types simultaneously
```bash
python pipeline.py --query "dogs,cats,cars" --count 5
```

#### 🛠️ **Configurable Options**
- **New:** YAML Config File support (`config.yaml`)
- Enable/disable metrics collection
- Toggle quality refinement loop
- Choose validation method (Coordinate/Visual/Hybrid)
- Adjust iteration limits
- Control parallel worker count
- Customize output directories

> **💡 Free Tier Optimization:** When using `visual` validation on the free tier (15 RPM), set `num_workers: 1` in `config.yaml` to avoid rate limit errors.

---

## 🏗️ Architecture

### **Multi-Agent System Design**

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main Agent                              │
│                    (Orchestrator)                               │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──► 🔍 Miner Agent ──────► Search & Download Images
         │      ├─ Google Custom Search API
         │      ├─ Perceptual hash deduplication
         │      └─ Format conversion & validation
         │
         ├──► 🎯 Curator Agent ─────► Filter & Quality Check
         │      ├─ Vision-based relevance check
         │      ├─ Duplicate detection
         │      └─ Quality assessment
         │
         ├──► 🏷️ Annotator Agent ───► Detect & Annotate Objects
         │      │
         │      ├──► Regular Mode: Single image annotation
         │      │     └─ Fast, reliable bounding boxes
         │      │
         │      └──► Parallel Mode: Batch annotation (3 workers)
         │            ├─ Worker 1 ──► Image A
         │            ├─ Worker 2 ──► Image B
         │            └─ Worker 3 ──► Image C
         │
         ├──► 🔄 Quality Loop ──────► Refine Annotations (Optional)
         │      ├─ Validate completeness
         │      ├─ Check accuracy
         │      ├─ Provide feedback
         │      └─ Re-annotate if needed (max 3 iterations)
         │
         └──► 📦 Engineer Agent ────► Export COCO Format
                ├─ Category mapping
                ├─ Coordinate transformation
                └─ COCO JSON generation

                         ↓
                   
              📊 Metrics Collector (tracks all stages)
              ❌ Error Handler (manages failures)
              📝 Logger (records everything)
```

### **Data Flow**

```
User Request
    │
    ├─→ "create 10 images of dogs and cats"
    │
    ↓
Parse Request ─────► query: "dogs,cats"
                     count: 10
    │
    ↓
┌───────────────────────────────────────────────────────────┐
│                    Execution Loop                          │
│  (Repeats until target count reached or max loops)        │
│                                                            │
│  1. Mine Images ──────► Search Google, download 10 URLs   │
│     └─ Deduplicate                                        │
│                                                            │
│  2. Curate ───────────► AI quality check, keep 7/10       │
│     └─ Relevance filter                                   │
│                                                            │
│  3. Annotate ─────────► Parallel process 7 images         │
│     ├─ Worker 1: images 1-2                               │
│     ├─ Worker 2: images 3-5                               │
│     └─ Worker 3: images 6-7                               │
│                                                            │
│  4. Quality Loop ─────► Validate & refine (if enabled)    │
│     └─ Iterate until approved                             │
│                                                            │
│  5. Check Progress ───► Have 10 images? ─┬─ Yes → Done   │
│                                           └─ No → Repeat  │
└───────────────────────────────────────────────────────────┘
    │
    ↓
Engineer ──────────► Transform to COCO format
    │                ├─ Normalize coordinates
    │                ├─ Map categories
    │                └─ Generate JSON
    ↓
Save Output ───────► data/output/coco.json
    │
    ↓
Display Metrics ───► Success rates, timing, errors
```

### **File Structure**

```
foundry/
├── agents/                     # AI agents
│   ├── main_agent.py          # Orchestrator
│   ├── miner.py               # Image search & download
│   ├── curator.py             # Quality filtering
│   ├── annotator.py           # Single image annotation
│   ├── parallel_annotator.py  # Batch annotation (3 workers)
│   ├── engineer.py            # COCO format export
│   ├── quality_loop.py        # Iterative refinement
│   └── base_agent.py          # Base agent class
│
├── tools/                      # Utility tools
│   ├── search_tool.py         # Google Custom Search
│   └── bbox_calculator.py     # Coordinate transformations
│
├── utils/                      # Support utilities
│   ├── logger.py              # Structured logging
│   ├── file_manager.py        # File operations
│   ├── metrics.py             # Performance tracking
│   ├── error_handler.py       # Error management
│   └── phase2_integration.py  # Feature integration
│
├── data/                       # Data directories
│   ├── raw/                   # Downloaded images
│   ├── curated/               # Filtered images
│   └── output/                # COCO datasets
│
├── pipeline.py                 # Main entry point
├── requirements.txt            # Dependencies
└── .env                        # API keys (create this)
```

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.10 or higher
- Google API keys (Gemini + Custom Search)

### **Installation**

1. **Clone the repository:**
```bash
git clone <repository-url>
cd kaggle_capstone
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure API keys:**

Create a `.env` file in the project root:
```env
# Required: Gemini API for AI agents
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Google Custom Search for image mining
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_CX=your_custom_search_engine_id
```

**Get API Keys:**
- **Gemini API:** https://ai.google.dev/
- **Google Custom Search:** https://developers.google.com/custom-search/v1/overview
- **Custom Search Engine:** https://programmablesearchengine.google.com/

### **First Run**

```bash
python pipeline.py
```

When prompted, enter:
```
create 5 images of dogs
```

That's it! Foundry will automatically:
1. 🔍 Search for dog images
2. 🎯 Filter for quality and relevance
3. 🏷️ Annotate with bounding boxes
4. 📦 Export to COCO format at `data/output/coco.json`

---

## 📘 Usage Guide

### **Interactive Mode (Recommended)**

1. **Configure Settings:** Edit `config.yaml` to set your preferences (quality loop, visual validation, etc.).
2. **Run Pipeline:**
   ```bash
   python pipeline.py --config config.yaml
   ```
3. **See Detailed Help:** The system will show you:
   - **Mode 1:** Create new datasets (with examples)
   - **Mode 2:** Annotate your own images (BYOD mode)
   - **Features:** Multi-object detection, quality loop, COCO output
   - **Examples:** Specific request formats you can use

4. **Enter Your Request:**
   ```
   Your request: create 5 images of dogs
   ```
   Foundry will use your config settings to process the request!

**Example Requests:**

**Standard Mode (Create New Dataset):**
```
✅ create 5 images of dogs
✅ get me 10 bicycle images
✅ I need 15 images of cats and dogs  (multi-object)
✅ find 20 car images
```

**BYOD Mode (Annotate Your Images):**
```
✅ annotate dogs in C:\Users\me\my_photos
✅ I have images at /home/user/pics, detect cats
✅ detect bicycles in C:\images\bikes
```

### **Command Line Mode**

#### **Basic Dataset Creation**
```bash
python pipeline.py --query "cats" --count 10
```

#### **Multi-Object Detection**
```bash
python pipeline.py --query "dogs,cats,cars" --count 15
```

#### **BYOD Mode (Your Own Images)**
```bash
python pipeline.py --dir "C:\path\to\images" --query "elephants"
```

#### **With Quality Refinement**
```bash
python pipeline.py --query "bicycles" --count 5 --enable-quality-loop
```

#### **Show Performance Metrics**
```bash
python pipeline.py --query "birds" --count 8 --show-metrics
```

#### **Maximum Quality (Slower)**
```bash
python pipeline.py --query "cars" --count 5 \
  --enable-quality-loop --quality-iterations 3 --show-metrics
```

#### **Fast Mode (Skip Extras)**
```bash
python pipeline.py --query "dogs" --count 10 --no-metrics
```

### **All Command-Line Options**

```bash
Options:
  --config PATH                Path to YAML config file (Recommended)
  --request TEXT               Natural language request
  --query TEXT                 Object query (e.g., 'cats' or 'dog,cat')
  --count INT                  Number of images to create
  --dir PATH                   Directory with existing images (BYOD mode)
  
  --enable-quality-loop        Enable iterative quality refinement
  --quality-iterations INT     Max refinement iterations (default: 2)
  --validation-method STR      Validation method: coordinate, visual, hybrid
  --show-metrics              Display detailed metrics summary
  --no-metrics                Disable metrics collection (faster)
  
  --help                      Show this message and exit
```

---

## 💡 Usage Examples

### **Example 1: Simple Dataset Creation**

```bash
python pipeline.py --query "tables" --count 5 --show-metrics
```

**Output:**
```
📋 Standard Mode: Creating dataset with 5 images of 'tables'

2025-11-23 17:30:15 - Mining completed: 5 images saved
2025-11-23 17:30:28 - Finished. Kept 5 images
2025-11-23 17:30:35 - Parallel annotation completed: 5/5 images annotated
2025-11-23 17:30:36 - Dataset saved successfully

============================================================
📊 PIPELINE METRICS SUMMARY
============================================================

📈 Overview:
   Pipeline Runs: 1
   Total Images Mined: 5
   Total Images Curated: 5
   Total Images Annotated: 5
   Total Images Saved: 5

✅ Success Rates:
   Curation Avg: 100.0%
   Annotation Avg: 100.0%

⏱️  Average Timings:
   Mining: 3.21s
   Curation: 12.45s
   Annotation: 8.67s
   Pipeline Total: 24.33s
============================================================
```

---

### **Example 2: Multi-Object Detection**

```bash
python pipeline.py --query "dogs,cats" --count 3 --enable-quality-loop --show-metrics
```

**What happens:**
1. Searches for images containing dogs or cats
2. Each image may contain one or both object types
3. Separate bounding boxes for each object
4. Quality validation ensures both are detected
5. COCO format with 2 categories

**Sample COCO Output:**
```json
{
  "categories": [
    {"id": 1, "name": "dog"},
    {"id": 2, "name": "cat"}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [120, 80, 200, 150],
      "area": 30000
    },
    {
      "id": 2,
      "image_id": 1,
      "category_id": 2,
      "bbox": [350, 100, 180, 140],
      "area": 25200
    }
  ]
}
```

---

### **Example 3: BYOD Mode (Your Own Images)**

```bash
python pipeline.py --dir "C:\Users\me\my_pandas" --query "panda" --show-metrics
```

**Use case:** You have your own images and just want annotations

**Process:**
1. Skips mining and curation
2. Directly annotates all images in the directory
3. Detects pandas and generates bounding boxes
4. Exports to COCO format

**Benefits:**
- No web search needed
- Works with private/proprietary images
- Fast annotation-only workflow

---

### **Example 4: Quality Refinement in Action**

```bash
python pipeline.py --query "bicycles" --count 2 --enable-quality-loop --quality-iterations 3
```

**Console Output:**
```
🔄 Starting refinement loop for bicycle_001.jpg
   Iteration 1/3
   ✓ Iteration 1: 1 boxes, Status: NEEDS_IMPROVEMENT
     Feedback: "Second bicycle in background not detected"
   
   Iteration 2/3
   ✓ Iteration 2: 2 boxes, Status: NEEDS_IMPROVEMENT
     Feedback: "Bounding box too loose on left bicycle"
   
   Iteration 3/3
   ✓ Iteration 3: 2 boxes, Status: APPROVED
✅ Annotation approved after 3 iteration(s)
🎯 Refinement complete: 2 boxes after 3 iterations
```

**Result:** Higher quality annotations with multiple iterations.

**Validation Methods:**
- **Visual (Recommended):** Draws boxes on the image so the validator "sees" the annotation.
- **Coordinate:** Checks the numbers (faster).
- **Hybrid:** Uses both for critical tasks.

---

### **Example 5: Production Workflow**

For production-quality datasets:

```bash
# Step 1: Create with maximum quality
python pipeline.py --query "vehicles,pedestrians" --count 50 \
  --enable-quality-loop --quality-iterations 3 --show-metrics

# Step 2: Review output
cat data/output/coco.json | jq '.info'

# Step 3: Visualize (use your preferred tool)
# The COCO format works with standard visualization tools
```

---

### **Example 6: Programmatic Usage**

```python
from agents.main_agent import MainAgent
from utils.phase2_integration import initialize_phase2_features

# Initialize features
phase2 = initialize_phase2_features(
    enable_metrics=True,
    enable_quality_loop=True,
    quality_loop_iterations=2
)

# Create agent and run pipeline
agent = MainAgent()
agent.run_pipeline(query="dogs,cats", count=10)

# Get metrics
metrics = phase2.get_metrics()
summary = metrics.get_summary()

print(f"Success rate: {summary['success_rates']['annotation_avg']}")
print(f"Total time: {summary['timings']['pipeline_total']['avg']}")

# Show full summary
phase2.print_metrics_summary()
```

---

### **Example 7: Error Handling**

Foundry gracefully handles errors:

```python
from utils.error_handler import ErrorHandler, create_error_response

try:
    # Some operation
    result = mine_images("dogs", 10)
except Exception as e:
    # Create structured error
    error = ErrorHandler.handle_mining_error(e, query="dogs", attempted=10)
    
    # Check if should retry
    if ErrorHandler.should_retry(error, attempt=1, max_attempts=3):
        # Retry the operation
        result = mine_images("dogs", 10)
    else:
        # Log and continue
        ErrorHandler.log_error(error)
```

---

## 📊 Output Format

### **COCO JSON Structure**

```json
{
  "info": {
    "year": 2025,
    "version": "1.0",
    "description": "Dataset for dogs,cats generated by Foundry",
    "date_created": "2025-11-23T17:30:00"
  },
  "categories": [
    {
      "id": 1,
      "name": "dog",
      "supercategory": "object"
    },
    {
      "id": 2,
      "name": "cat",
      "supercategory": "object"
    }
  ],
  "images": [
    {
      "id": 1,
      "file_name": "abc123.jpg",
      "width": 800,
      "height": 600
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [100, 150, 200, 180],  // [x, y, width, height] in pixels
      "area": 36000,
      "iscrowd": 0
    }
  ]
}
```

### **Understanding Bounding Boxes**

Foundry uses the standard COCO bounding box format:

```
bbox: [x, y, width, height]

Where:
  x = left edge (pixels from left)
  y = top edge (pixels from top)
  width = box width in pixels
  height = box height in pixels
```

**Visualization:**
```
(0,0) ────────────────────────► x
  │
  │        (x, y)
  │          ↓
  │        ┌─────────────┐
  │        │             │
  │        │   Object    │ height
  │        │             │
  │        └─────────────┘
  │            width
  ↓
  y
```

### **Working with Output**

**Load with Python:**
```python
import json

with open('data/output/coco.json', 'r') as f:
    coco_data = json.load(f)

# Get categories
categories = {cat['id']: cat['name'] for cat in coco_data['categories']}

# Iterate annotations
for ann in coco_data['annotations']:
    image_id = ann['image_id']
    category = categories[ann['category_id']]
    bbox = ann['bbox']  # [x, y, w, h]
    print(f"Image {image_id}: {category} at {bbox}")
```

**Use with PyTorch:**
```python
from pycocotools.coco import COCO

coco = COCO('data/output/coco.json')
cat_ids = coco.getCatIds(catNms=['dog'])
img_ids = coco.getImgIds(catIds=cat_ids)
annotations = coco.loadAnns(coco.getAnnIds(imgIds=img_ids))
```

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_CX=your_cx_id

# Optional - Advanced Configuration
# (Not currently used but reserved for future features)
```

### **Runtime Configuration**

Modify behavior via command-line flags:

```bash
# Performance vs Quality Trade-offs
--no-metrics                    # Fastest, minimal overhead
--show-metrics                  # Track performance (default)
--enable-quality-loop           # Better quality, slower (2-3x)
--quality-iterations 3          # Maximum quality, slowest (3-4x)

# Processing Options
--count 10                      # Number of images
--query "object1,object2"       # Single or multi-object

# Mode Selection
--dir /path                     # BYOD mode (your images)
# (no --dir)                    # Standard mode (mine & curate)
```

### **Code Configuration**

```python
from utils.phase2_integration import initialize_phase2_features

# Initialize with custom settings
phase2 = initialize_phase2_features(
    enable_metrics=True,              # Track performance
    enable_quality_loop=True,         # Enable refinement
    quality_loop_iterations=2         # Max iterations
)

# Create agent with custom folders
from agents.main_agent import MainAgent

agent = MainAgent()
agent.miner.download_folder = "custom/raw"
agent.curator.curated_folder = "custom/curated"
agent.engineer.output_folder = "custom/output"
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **1. API Key Errors**
```
Error: GEMINI_API_KEY not found in .env file
```

**Solution:**
- Create `.env` file in project root
- Add: `GEMINI_API_KEY=your_key_here`
- Ensure no spaces around `=`

#### **2. No Images Found**
```
Miner returned no images
```

**Solutions:**
- Check Google Custom Search API quota
- Verify `GOOGLE_SEARCH_CX` is correct
- Try different search query
- Check internet connection

#### **3. Curation Filters All Images**
```
Curator filtered all images in this batch
```

**Solutions:**
- Query might be too specific

#### **4. Rate Limit Errors (429)**
```
429 Resource exhausted. Please try again later.
```

**Solutions:**
- **Free Tier:** Set `num_workers: 1` in `config.yaml`
- **Visual Validation:** Uses more API calls, reduce workers or switch to `coordinate` method
- **Wait:** Free tier resets every minute (15 requests/minute limit)
- **Upgrade:** Consider paid tier for higher limits (1000 RPM)
- Try broader search terms
- Check image quality from search results
- Run with `--show-metrics` to see rejection reasons

#### **4. Annotation Failures**
```
Failed to parse JSON for image.jpg
```

**Solutions:**
- This is usually handled automatically with retry
- If persistent, check Gemini API quota
- Try running again (transient LLM issue)

#### **5. Slow Performance**
```
Pipeline taking too long
```

**Solutions:**
- Disable quality loop: remove `--enable-quality-loop`
- Disable metrics: add `--no-metrics`
- Reduce worker count (edit `parallel_annotator.py`)
- Check internet speed for image downloads

### **Debug Mode**

Enable detailed logging:

```python
from utils.logger import setup_logging
import logging

setup_logging(log_level=logging.DEBUG)
```

### **Getting Help**

1. Check logs in console output
2. Review error messages (now structured and helpful!)
3. Try with `--show-metrics` to see pipeline stats
4. Check `.env` file configuration
5. Verify API quotas and limits

---

## 📈 Performance Benchmarks

### **Typical Performance (5 images)**

| Mode | Time | Quality | Best For |
|------|------|---------|----------|
| Standard | ~25s | ✅ Good | Daily use, prototyping |
| + Quality Loop (2 iter) | ~50s | ⭐⭐ Better | Important datasets |
| + Quality Loop (3 iter) | ~75s | ⭐⭐⭐ Best | Production, presentations |
| --no-metrics | ~24s | ✅ Good | Speed testing |

### **Scalability**

| Dataset Size | Standard | + Quality Loop |
|--------------|----------|----------------|
| 5 images | ~25s | ~50s |
| 10 images | ~45s | ~95s |
| 20 images | ~85s | ~180s |
| 50 images | ~200s | ~450s |

**Note:** Times vary based on:
- Internet speed (image downloads)
- API response times
- Image complexity
- Number of objects per image

### **Resource Usage**

- **CPU:** Moderate (parallel processing)
- **Memory:** ~200-500MB
- **Disk:** Depends on image count (~10MB per image)
- **Network:** Downloads images (varies by quality)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### **Areas for Improvement**

1. **Additional MCP Integrations** - Connect to more image sources
2. **Visualization Dashboard** - Web UI for metrics and results
3. **Session Management** - Resume interrupted pipelines
4. **Custom Validators** - Domain-specific quality checks
5. **Performance Optimization** - Faster processing strategies

### **Development Setup**

```bash
# Clone and setup
git clone <repo>
cd kaggle_capstone
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
python -m pytest tests/  # (when test suite exists)

# Make changes and test
python pipeline.py --query "test" --count 2
```

### **Code Style**

- Follow PEP 8
- Add docstrings to functions
- Include type hints where applicable
- Write descriptive commit messages

---

## 📚 Documentation

- **README.md** - This file (overview and usage)
- **knowledge_transfer.md** - Technical deep dive and architecture
- **COURSE_IMPLEMENTATION_GUIDE.md** - Feature roadmap
- **phase2_examples.py** - Code examples for advanced features
- **PHASE2_SUMMARY.md** - Feature documentation
- **BUG_FIXES_SUMMARY.md** - Bug fix history

---

## 🛡️ Error Handling

Foundry uses intelligent, structured error handling:

### **Error Categories**

- **Network** - Connection issues, timeouts
- **API** - Rate limits, authentication failures
- **Validation** - Data format issues
- **Parsing** - JSON decoding errors
- **Filesystem** - Disk space, permissions
- **Timeout** - Operations taking too long
- **Rate Limit** - API quota exceeded
- **Authentication** - Invalid API keys
- **Configuration** - Missing settings

### **Severity Levels**

- 🟢 **LOW** - Minor issue, pipeline continues
- 🟡 **MEDIUM** - Significant issue, may retry
- 🔴 **HIGH** - Critical issue, needs attention
- ⚫ **FATAL** - Unrecoverable, pipeline stops

### **Automatic Recovery**

Foundry automatically handles common failures:

```python
# Automatic retry for transient errors
- Rate limits → Wait and retry
- Timeouts → Retry with backoff
- Network errors → Retry up to 3 times

# Graceful degradation
- Bad image → Skip and continue
- Parse error → Auto-fix JSON, retry
- Missing data → Use defaults, log warning
```

---

## 🎓 Learn More

### **Based on Concepts From:**

- **Kaggle 5-Day Agents Course** - Multi-agent patterns
- **COCO Dataset Format** - Industry standard annotations
- **Google ADK** - Agent Development Kit patterns
- **Production ML** - Real-world deployment practices

### **Key Concepts Implemented:**

1. **Multi-Agent Systems** - Specialized agents for each task
2. **Loop Patterns** - Iterative refinement for quality
3. **Parallel Processing** - Efficient batch operations
4. **Observability** - Comprehensive metrics and logging
5. **Error Resilience** - Smart retry and recovery
6. **Structured Data** - Standard COCO format output

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Google Gemini API for vision and language models
- Google Custom Search API for image discovery
- COCO dataset format standard
- Kaggle 5-Day Agents Course for architecture patterns

---

## 📞 Support

Having issues? Here's what to check:

1. ✅ API keys configured in `.env`
2. ✅ Python 3.10+ installed
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ Internet connection active
5. ✅ API quotas not exceeded

For detailed help, see [Troubleshooting](#-troubleshooting) section above.

---

<div align="center">

**Built with ❤️ using AI agents**

[⬆ Back to Top](#-foundry-ai-powered-dataset-creation-system)

</div>
