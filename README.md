<div align="center">

# 🤖 Foundry: AI-Powered Dataset Creation System

**Automatically create high-quality object detection datasets using multi-agent AI**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

[Quick Start](#-quick-start) • [Usage Guide](docs/USAGE.md) • [Examples](docs/EXAMPLES.md) • [Documentation](docs/knowledge_transfer.md)

</div>

---

## 📖 Overview

Foundry is an intelligent, multi-agent system that automates the entire pipeline of creating object detection datasets. From searching the web for images to generating production-ready COCO format annotations, Foundry handles it all with minimal human intervention.

### What Makes Foundry Special?

🎯 **Fully Autonomous** - Mine, curate, annotate, and export datasets automatically  
🔄 **Self-Improving** - Iterative quality refinement ensures high-quality annotations  
📊 **Observable** - Comprehensive metrics track success rates and performance  
🛡️ **Robust** - Intelligent error handling with automatic retry logic  
⚡ **Efficient** - Configurable parallel processing  
🎨 **Flexible** - Single/multi-object detection, works with your own images too

---

## ✨ Key Features

- **Intelligent Image Mining** - Automated web search with smart deduplication
- **AI-Powered Curation** - Vision-based quality assessment and relevance filtering
- **Advanced Annotation** - Multi-object detection with quality refinement loop
- **Multiple Validation Methods** - Coordinate, Visual, or Hybrid validation
- **YAML Configuration** - Centralized config with CLI overrides
- **BYOD Mode** - Annotate your own images directly
- **COCO Format Export** - Production-ready output for PyTorch, TensorFlow

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google API keys (Gemini + Custom Search)

### Installation

1. **Clone and setup:**
```bash
git clone https://github.com/mauryantitans/Foundry.git
cd Foundry
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

2. **Configure API keys:**

Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_CX=your_custom_search_engine_id
```

**Get API Keys:**
- [Gemini API](https://ai.google.dev/)
- [Google Custom Search](https://developers.google.com/custom-search/v1/overview)
- [Custom Search Engine](https://programmablesearchengine.google.com/)

3. **Configure settings (optional):**

Edit `config.yaml` to set your preferences:
```yaml
quality_loop:
  enabled: true
  validation_method: "visual"  # coordinate | visual | hybrid

annotation:
  num_workers: 1  # Set to 1 for free tier to avoid rate limits
```

### First Run

**Interactive Mode (Recommended):**
```bash
python pipeline.py --config config.yaml
```

The system will show you detailed help with examples for:
- Creating new datasets (web mining)
- Annotating your own images (BYOD mode)

**Quick CLI Usage:**
```bash
# Create a dataset
python pipeline.py --query "dogs" --count 5 --enable-quality-loop

# Annotate your own images
python pipeline.py --dir "/path/to/images" --query "cats"

# Multi-object detection
python pipeline.py --query "dogs,cats" --count 10
```

**Output:** COCO format JSON at `data/output/coco.json`

---

## 📘 Usage

### Interactive Mode

Run without arguments to see detailed help:
```bash
python pipeline.py --config config.yaml
```

You'll see:
- **MODE 1:** Create new datasets (with examples)
- **MODE 2:** Annotate your own images (BYOD)
- **Features:** Multi-object detection, quality loop, COCO output

**Example requests:**
```
✅ create 5 images of dogs
✅ get me 10 bicycle images
✅ I need 15 images of cats and dogs  (multi-object)
✅ annotate dogs in C:\Users\me\my_photos  (BYOD)
```

### Command Line Mode

```bash
# Basic usage
python pipeline.py --query "cats" --count 10

# With quality refinement
python pipeline.py --query "bicycles" --count 5 \
  --enable-quality-loop --validation-method visual

# BYOD mode
python pipeline.py --dir "C:\path\to\images" --query "elephants"

# Multi-object
python pipeline.py --query "dogs,cats,cars" --count 15
```

### Configuration File

Create custom configs for different scenarios:

**Standard mode with visual validation:**
```yaml
pipeline:
  query: "bicycle"
  count: 10

quality_loop:
  enabled: true
  validation_method: "visual"
```

**BYOD mode:**
```yaml
pipeline:
  mode: "byod"
  image_dir: "C:/my_images"
  query: "dog"

quality_loop:
  enabled: true
```

Run with: `python pipeline.py --config my_config.yaml`

---

## 📊 Output Format

Foundry generates standard COCO JSON format:

```json
{
  "categories": [
    {"id": 1, "name": "dog", "supercategory": "object"}
  ],
  "images": [
    {"id": 1, "file_name": "image.jpg", "width": 800, "height": 600}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [100, 150, 200, 180],  // [x, y, width, height]
      "area": 36000
    }
  ]
}
```

**Compatible with:** PyTorch, TensorFlow, CVAT, LabelImg

**Visualize results:**
```bash
python visualize_results.py
```

---

## 🔧 Configuration Options

### Quality Loop Validation Methods

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| **coordinate** | Fast | Good | Simple objects, speed priority |
| **visual** | Medium | Better | Complex scenes, accuracy priority |
| **hybrid** | Slow | Best | Critical datasets, maximum quality |

### Free Tier Optimization

For Gemini API free tier (15 RPM):
```yaml
annotation:
  num_workers: 1  # Prevents rate limit errors

quality_loop:
  validation_method: "coordinate"  # Faster, fewer API calls
```

---

## 🛠️ Troubleshooting

### Rate Limit Errors (429)

**Problem:** `429 Resource exhausted`

**Solutions:**
- Set `num_workers: 1` in `config.yaml`
- Use `coordinate` validation instead of `visual`
- Wait 60 seconds between runs (free tier resets every minute)
- Consider upgrading to paid tier (1000 RPM)

### No Images Found

**Problem:** `Miner returned no images`

**Solutions:**
- Check API keys in `.env` file
- Verify Google Custom Search API quota
- Try different search query
- Check internet connection

### All Images Filtered

**Problem:** `Curator filtered all images`

**Solutions:**
- Use broader search terms
- Check image quality from search results
- Run with `--show-metrics` to see rejection reasons

For more troubleshooting, see [USAGE.md](docs/USAGE.md#troubleshooting)

---

## 📚 Documentation

- **[USAGE.md](docs/USAGE.md)** - Detailed usage guide, all CLI options, advanced features
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Real-world examples and use cases
- **[knowledge_transfer.md](docs/knowledge_transfer.md)** - Technical architecture and development guide
- **[test_report.md](docs/test_report.md)** - Integration test results and system verification

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
         │      └──► Parallel Mode: Batch annotation (configurable workers)
         │            ├─ Worker 1 ──► Image A
         │            ├─ Worker 2 ──► Image B
         │            └─ Worker 3 ──► Image C
         │
         ├──► 🔄 Quality Loop ──────► Refine Annotations (Optional)
         │      ├─ Validate completeness
         │      ├─ Check accuracy (coordinate/visual/hybrid)
         │      ├─ Provide feedback
         │      └─ Re-annotate if needed (max iterations)
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
│  1. Mine Images ──────► Search Google, download URLs      │
│     └─ Deduplicate                                        │
│                                                            │
│  2. Curate ───────────► AI quality check, filter          │
│     └─ Relevance filter                                   │
│                                                            │
│  3. Annotate ─────────► Process images                    │
│     ├─ Single image: Direct annotation                    │
│     └─ Multiple: Parallel workers                         │
│                                                            │
│  4. Quality Loop ─────► Validate & refine (if enabled)    │
│     └─ Iterate until approved                             │
│                                                            │
│  5. Check Progress ───► Have enough? ─┬─ Yes → Done       │
│                                        └─ No → Repeat      │
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

For detailed architecture, see [knowledge_transfer.md](docs/knowledge_transfer.md)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Google Gemini 2.0 Flash for AI capabilities
- Google Custom Search API for image discovery
- COCO format specification for standardized output

---

**Made with ❤️ for the ML community**
