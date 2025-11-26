<div align="center">

# 🤖 Foundry: AI-Powered Dataset Creation System

**Automatically create high-quality object detection datasets using multi-agent AI**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

[Quick Start](#-quick-start) • [Usage Guide](docs/USAGE.md) • [Examples](docs/EXAMPLES.md) • [Documentation](docs/knowledge_transfer.md)

</div>

---

## 🌟 What is Foundry?

**Foundry** is an intelligent multi-agent system that autonomously creates annotated object detection datasets. Simply describe what you want, and Foundry will:

1. **🔍 Mine** images from Google Search
2. **🎯 Curate** them for quality and relevance  
3. **🏷️ Annotate** with bounding boxes (multi-object support)
4. **🔄 Refine** annotations with quality loop
5. **📦 Export** to industry-standard COCO format

**Result:** Production-ready datasets in < 5 minutes for pennies.

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🎯 **Core Capabilities**
- **Natural Language Interface** - Describe datasets in plain English
- **Multi-Object Detection** - Separate boxes for each object type
- **Intelligent Mining** - Smart search with deduplication
- **AI-Powered Curation** - Vision-based quality filtering
- **Automatic Annotation** - Bounding box generation
- **COCO Export** - Ready for PyTorch/TensorFlow

</td>
<td width="50%">

### ⚡ **Advanced Features**
- **Quality Refinement Loop** - Self-correcting annotations
- **Robust JSON Parsing** - 5-strategy fallback system
- **Automatic Retry** - 3 attempts with backoff
- **BYOD Mode** - Annotate your own images
- **Comprehensive Metrics** - Track performance
- **Flexible Configuration** - YAML + CLI options

</td>
</tr>
</table>

---

## 🚀 Quick Start

**Get started in 5 minutes!** → [**QUICKSTART.md**](QUICKSTART.md)

```bash
# Clone and install
git clone https://github.com/mauryantitans/Foundry.git
cd Foundry
python -m venv venv
venv\Scripts\activate  # Windows | source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure API keys (create .env file)
GEMINI_API_KEY=your_key_here
GOOGLE_SEARCH_API_KEY=your_key_here
GOOGLE_SEARCH_CX=your_cx_here

# Run your first dataset!
python pipeline.py --query "dog" --count 5
```

**Output:**
```
✅ Images Collected: 5/5
✅ Dataset saved to: data/output/coco.json
📊 Ready for training!
```

➡️ **[Full Quick Start Guide](QUICKSTART.md)** with detailed instructions

---

## 📘 Usage

### Interactive Mode (Recommended)

```bash
python pipeline.py
```

Then type natural language requests:
```
✅ "create 5 images of dogs"
✅ "get 10 images of red sports cars"
✅ "I need 15 images of people holding guitars, annotate person and guitar"
```

### Command Line Mode

```bash
# Single object
python pipeline.py --query "dog" --count 10

# Multi-object detection (separate boxes)
python pipeline.py --query "person,guitar" --count 5

# With quality refinement
python pipeline.py --query "bicycle" --count 8 --enable-quality-loop

# Annotate your own images (BYOD)
python pipeline.py --dir "C:\photos" --query "cat"
```

### Configuration File

```yaml
# config.yaml
pipeline:
  query: "dog"
  count: 10

quality_loop:
  enabled: true
  validation_method: "coordinate"

annotation:
  workers: 1  # Set to 1 for free tier
```

```bash
python pipeline.py --config config.yaml
```

➡️ **[Complete Usage Guide](docs/USAGE.md)** with all options

---

## 🎯 Multi-Object Detection

Foundry supports detecting multiple objects in the same images with **separate bounding boxes** for each object type.

**Example:**
```bash
python pipeline.py --query "person,guitar" --count 5
```

**What happens:**
1. **Mining**: Searches for "person holding guitar"
2. **Annotation**: Creates **separate boxes**:
   - Person boxes → `category_id: 1`
   - Guitar boxes → `category_id: 2`

**Output COCO:**
```json
{
  "categories": [
    {"id": 1, "name": "person"},
    {"id": 2, "name": "guitar"}
  ],
  "annotations": [
    {"category_id": 1, "bbox": [100, 50, 200, 300]},  // person
    {"category_id": 2, "bbox": [150, 200, 100, 150]}   // guitar
  ]
}
```

➡️ **[Multi-Object Examples](docs/EXAMPLES.md#multi-object-detection)**

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│     (CLI | Interactive | Natural Language)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             MainAgent (Orchestrator)                    │
│  • Parse natural language                               │
│  • Extract query & objects                              │
│  • Optimize search queries                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Foundry Pipeline (Core)                      │
│                                                         │
│  Loop: Until target count reached                       │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  1. 🔍 MINE   → Search & Download Images       │    │
│  │     • Google Custom Search                     │     │
│  │     • Perceptual hash deduplication            │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  2. 🎯 CURATE → Quality Filter                 │    │
│  │     • Vision AI validation                     │     │
│  │     • Relevance checking                       │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  3. 🏷️ ANNOTATE → Bounding Boxes              │     │
│  │     • Multi-object detection                   │     │
│  │     • 5-strategy JSON parsing                  │     │
│  │     • 3-attempt retry logic                    │     │
│  │     • Quality validation (optional)            │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  4. ✅ CHECK  → Target Reached?               │    │
│  └────────────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              📦 COCO Dataset
            (coco.json)
```

### Agent Roles

| Agent | Responsibility | Key Features |
|-------|---------------|--------------|
| **MainAgent** | Parse requests & orchestrate | Natural language understanding, query optimization |
| **MinerAgent** | Find & download images | Google Search, deduplication |
| **CuratorAgent** | Validate quality | Vision AI filtering, relevance check |
| **AnnotatorAgent** | Generate bounding boxes | Multi-object support, robust parsing, retry logic |
| **EngineerAgent** | Export COCO format | Coordinate normalization, category mapping |

➡️ **[Complete Architecture Guide](PROJECT_OVERVIEW.md)**

---

## 📊 Output Format

Foundry generates standard COCO format compatible with all major frameworks:

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

## 🔧 Configuration

### Quality Loop Validation Methods

| Method | Speed | Accuracy | Use Case |
|--------|-------|----------|----------|
| **coordinate** | ⚡ Fast | ✅ Good | Simple objects, free tier |
| **visual** | 🔄 Medium | ✅✅ Better | Complex scenes |
| **hybrid** | 🐌 Slow | ✅✅✅ Best | Critical datasets |

### Recommended Settings

**For Free Tier:**
```yaml
quality_loop:
  enabled: true
  validation_method: "coordinate"
  
annotation:
  workers: 1  # Critical!
```

**For Production:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "hybrid"

annotation:
  workers: 3
```

---

## 📚 Documentation

### User Guides
- **[🚀 QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[📖 USAGE.md](docs/USAGE.md)** - Complete usage reference
- **[💡 EXAMPLES.md](docs/EXAMPLES.md)** - Real-world examples (20+)

### Technical Documentation  
- **[🏗️ PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - System architecture

### Quick Links
- **[Multi-Object Guide](docs/EXAMPLES.md#multi-object-detection)** - Separate boxes per object
- **[BYOD Mode](docs/EXAMPLES.md#byod-bring-your-own-data)** - Annotate your images
- **[Quality Loop](docs/USAGE.md#quality-refinement-loop)** - Improve accuracy
- **[Troubleshooting](docs/USAGE.md#troubleshooting)** - Common issues

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository: https://github.com/mauryantitans/Foundry
2. Create a feature branch
3. Make your changes
4. Submit a pull request

➡️ **[Development Guide](PROJECT_OVERVIEW.md#development)**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini 2.0 Flash** - AI capabilities
- **Google Custom Search API** - Image discovery  
- **COCO Format** - Standard dataset format
- **Python Community** - Amazing libraries and tools

---

<div align="center">

**Made with ❤️ for the ML community**

⭐ **[Star us on GitHub](https://github.com/mauryantitans/Foundry)** if Foundry helped you!

[Report Bug](https://github.com/mauryantitans/Foundry/issues) · [Request Feature](https://github.com/mauryantitans/Foundry/issues) · [View Source](https://github.com/mauryantitans/Foundry)

**Version 1.2.0** | **Status: Production Ready ✅**

</div>
