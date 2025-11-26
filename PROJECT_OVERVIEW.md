# Foundry - Project Overview

**GitHub Repository:** https://github.com/mauryantitans/Foundry

**AI-Powered Dataset Creation System**

---

## What is Foundry?

Foundry is an intelligent multi-agent system that automatically creates annotated object detection datasets from simple text descriptions. It transforms the dataset creation process from a 100+ hour manual task into a 5-minute automated workflow.

---

## Key Capabilities

### 🎯 Core Features
- **Natural Language Interface** - Describe datasets in plain English
- **Intelligent Mining** - Automated image search with deduplication
- **AI Curation** - Vision-based quality filtering
- **Automatic Annotation** - Multi-object bounding box generation
- **Quality Refinement** - Self-correcting annotation loop
- **COCO Export** - Industry-standard format output

### ⚡ Advanced Features
- **Multi-Object Detection** - Separate boxes for each object type
- **BYOD Mode** - Annotate your own images
- **Robust Parsing** - 5-strategy JSON fallback system
- **Automatic Retry** - 3 attempts with exponential backoff
- **Comprehensive Metrics** - Track success rates and performance
- **Flexible Configuration** - YAML + CLI options

---

## System Architecture

```
┌──────────────────────────────────────────────────────┐
│                   User Interface                      │
│  (CLI, Interactive Mode, Natural Language)           │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│               MainAgent (Orchestrator)                │
│  • Parse natural language                             │
│  • Extract query & objects                            │
│  • Optimize search queries                            │
│  • Plan execution                                     │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│             Foundry Pipeline (Core)                   │
│                                                       │
│  Loop: Until target count reached                    │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  1. MINE Phase                                │  │
│  │     • Google Custom Search                    │  │
│  │     • Download images                         │  │
│  │     • Perceptual hash deduplication           │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  2. CURATE Phase                              │  │
│  │     • Vision AI quality check                 │  │
│  │     • Relevance filtering                     │  │
│  │     • Remove low-quality images               │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  3. ANNOTATE Phase                            │  │
│  │     • Multi-object detection                  │  │
│  │     • Bounding box generation                 │  │
│  │     • 5-strategy JSON parsing                 │  │
│  │     • 3-attempt retry logic                   │  │
│  │     • Quality validation (optional)           │  │
│  └───────────────────────────────────────────────┘  │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  4. CHECK Phase                               │  │
│  │     • Target count reached?                   │  │
│  │     • Continue or finish                      │  │
│  └───────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│            Engineer Agent (Export)                    │
│  • Transform to COCO format                           │
│  • Normalize coordinates                              │
│  • Generate category mappings                         │
│  • Export JSON                                        │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
           COCO Dataset
          (coco.json)
```

---

## Agent Roles

### MainAgent (Orchestrator)
**Responsibilities:**
- Parse natural language requests
- Extract search queries and annotation objects
- Optimize queries for better results
- Manage pipeline execution

**Example:**
```
Input: "I need 10 images of people holding guitars, annotate person and guitar"
Output:
  - Search query: "person holding guitar"
  - Objects: ["person", "guitar"]
  - Count: 10
```

---

### MinerAgent (Image Discovery)
**Responsibilities:**
- Search Google Custom Search API
- Download images
- Deduplicate using perceptual hashing
- Track pagination state

**Features:**
- Automatic retry on download failures
- Hash-based duplicate detection
- Incremental pagination

**Output:** List of downloaded image paths

---

### CuratorAgent (Quality Control)
**Responsibilities:**
- Validate image relevance
- Check image quality
- Filter inappropriate content
- Ensure images match query

**Validation:**
- Vision AI analysis
- Binary decision (keep/reject)
- Logging of rejection reasons

**Output:** Filtered list of high-quality images

---

### AnnotatorAgent (Bounding Boxes)
**Responsibilities:**
- Detect objects in images
- Generate bounding boxes
- Support multi-object detection
- Handle annotation failures

**Enhanced Features:**
- **5-Strategy JSON Parser**:
  1. Direct parse
  2. Markdown removal
  3. Common fixes (quotes, commas)
  4. Regex extraction
  5. Pattern reconstruction

- **3-Attempt Retry**:
  - Initial attempt
  - Retry with improved prompt (1s delay)
  - Final retry with explicit format (2s delay)

- **Coordinate Validation**:
  - Range check (0-1000)
  - Format validation
  - Bbox completeness

**Output:** Dictionary of annotations per image

---

### EngineerAgent (Format Conversion)
**Responsibilities:**
- Convert to COCO format
- Normalize coordinates
- Generate category IDs
- Create proper JSON structure

**COCO Structure:**
```json
{
  "info": {...},
  "categories": [{...}],
  "images": [{...}],
  "annotations": [{...}]
}
```

---

## Data Flow

### Standard Mode Flow

```
User: "create 10 images of dogs"
  │
  ├─► MainAgent parses
  │     query: "dog"
  │     count: 10
  │
  ├─► Pipeline Loop (iteration 1)
  │     │
  │     ├─► Mine: Search "dog", download 20 images
  │     │   └─► Output: 18 images (2 failed downloads)
  │     │
  │     ├─► Curate: Filter for quality
  │     │   └─► Output: 12 images (6 filtered)
  │     │
  │     ├─► Annotate: Generate bounding boxes
  │     │   └─► Output: 10 annotations (2 failed)
  │     │
  │     └─► Check: 10/10 reached ✓
  │
  └─► Engineer: Export to COCO
      └─► Output: coco.json
```

### Multi-Object Flow

```
User: "person,guitar"
  │
  ├─► MainAgent optimizes
  │     search_query: "person holding guitar"
  │     annotation_query: "person,guitar"
  │
  ├─► Mine: Search "person holding guitar"
  │   └─► Images of people with guitars
  │
  ├─► Curate: Validate relevance
  │   └─► Images containing both objects
  │
  ├─► Annotate: Detect separately
  │   ├─► Category 1: person → [bbox1, bbox2, ...]
  │   └─► Category 2: guitar → [bbox3, bbox4, ...]
  │
  └─► Engineer: Export with 2 categories
      {
        "categories": [
          {"id": 1, "name": "person"},
          {"id": 2, "name": "guitar"}
        ]
      }
```

---

## Technology Stack

### Core Technologies
- **Python 3.10+** - Main language
- **Google Gemini 2.5 Flash** - Vision AI
- **Google Custom Search API** - Image discovery
- **PIL/Pillow** - Image processing
- **ImageHash** - Perceptual hashing

### Key Libraries
- `google-generativeai` - Gemini SDK
- `google-api-python-client` - Search API
- `pydantic` - Data validation
- `PyYAML` - Configuration
- `imagehash` - Deduplication

### Frameworks
- Custom multi-agent system (no external agent framework)
- Direct sequential pipeline
- State management system

---

## Configuration

### config.yaml Structure

```yaml
pipeline:
  query: null                    # Set via CLI or interactive
  count: 5                       # Number of images
  mode: "standard"               # standard | byod

quality_loop:
  enabled: false                 # Enable quality refinement
  max_iterations: 2              # Max retry attempts
  validation_method: "coordinate" # coordinate | visual | hybrid

annotation:
  workers: 1                     # Parallel workers

metrics:
  enabled: true                  # Track performance
  show_summary: true             # Display at end
```

### Environment Variables (.env)

```env
GEMINI_API_KEY=your_gemini_key
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_CX=your_engine_id
```

---

## Project Structure

```
foundry/
├── core/                   # Core orchestration
│   └── orchestrator.py     # MainAgent
│
├── services/               # Agent implementations
│   ├── miner.py           # Image mining
│   ├── curator.py         # Quality filtering
│   ├── annotator.py       # Annotation (enhanced)
│   ├── parallel_annotator.py  # Batch processing
│   ├── quality_loop.py    # Refinement loop
│   └── engineer.py        # COCO export
│
├── pipelines/              # Pipeline orchestration
│   ├── foundry_pipeline.py    # Main pipeline
│   ├── adk_state.py       # State management
│   └── adk_pipeline.py    # Legacy ADK
│
├── tools/                  # Agent tools
│   └── search_tool.py     # Google Search wrapper
│
├── utils/                  # Utilities
│   ├── logger.py          # Logging
│   ├── metrics.py         # Performance tracking
│   ├── config_loader.py   # YAML config
│   ├── file_manager.py    # File operations
│   └── pipeline_features.py   # Feature flags
│
├── docs/                   # Documentation
│   ├── USAGE.md           # Usage guide
│   ├── EXAMPLES.md        # Examples
│   └── knowledge_transfer.md  # Technical docs
│
├── data/                   # Data directories
│   ├── raw/               # Downloaded images
│   ├── curated/           # Filtered images
│   └── output/            # COCO datasets
│
├── pipeline.py            # Main entry point
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── .env                   # API keys
└── README.md             # Documentation
```

---

## Performance Characteristics

### Benchmarks (Standard Configuration)

| Metric | Value |
|--------|-------|
| **Processing Speed** | 5-8 images/minute |
| **Success Rate** | 85-95% |
| **API Calls per Image** | 8-12 calls |
| **Cost (free tier)** | ~$0.02/10 images |
| **Mining Time** | 8-12s |
| **Curation Time** | 15-20s |
| **Annotation Time** | 18-25s |
| **Engineering Time** | <1s |

### Optimization Trade-offs

**Speed vs Quality:**
- No quality loop: Faster, 80-85% success
- With quality loop: Slower, 95%+ success

**Free Tier vs Paid:**
- Free: 15 req/min, workers=1
- Paid: 1000 req/min, workers=3+

---

## API Usage

### Gemini API Limits

**Free Tier:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Typical Usage (10 images):**
- Parsing: 1 call
- Curation: 10 calls
- Annotation: 10 calls
- Quality validation: 0-10 calls (optional)
- **Total**: ~21-31 calls

**Time to Process:** ~5-8 minutes for 10 images (free tier)

### Google Search API Limits

**Free Tier:**
- 100 queries/day
- Cannot be increased

**Typical Usage:**
- 1 query per mining batch
- ~1 query per 10 images

---

## Error Handling

### Built-in Recovery
- **Network failures**: Automatic retry
- **JSON parsing errors**: 5-strategy fallback
- **Annotation failures**: 3-attempt retry
- **Rate limits**: Exponential backoff
- **Download failures**: Skip and continue

### Logging
- Comprehensive debug logs
- Error tracebacks
- Performance metrics
- Success/failure tracking

---

## Testing

### Manual Testing
```bash
# Quick test
python pipeline.py --query "dog" --count 3

# Full test
python pipeline.py --query "person,guitar" --count 10 \
  --enable-quality-loop \
  --show-metrics
```

### Validation
```bash
# Verify COCO format
python -m json.tool data/output/coco.json

# Visualize results
python visualize_results.py
```

---

## Future Roadmap

### Short Term
- [ ] Web UI interface
- [ ] Batch processing scripts
- [ ] Enhanced visualization
- [ ] Custom validation rules

### Medium Term
- [ ] Video frame extraction
- [ ] Segmentation masks
- [ ] Active learning integration
- [ ] Cloud deployment templates

### Long Term
- [ ] Collaborative annotation
- [ ] Dataset versioning
- [ ] Model training integration
- [ ] Enterprise features

---

## Documentation

### User Guides
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup
- **[README.md](README.md)** - Main documentation
- **[USAGE.md](docs/USAGE.md)** - Complete usage guide
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Real-world examples

### Technical Docs
- **[CHANGELOG.md](CHANGELOG.md)** - Version history & fixes
- **[knowledge_transfer.md](docs/knowledge_transfer.md)** - Architecture
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Recent improvements

---

## Support

- **Issues**: [GitHub Issues](https://github.com/mauryantitans/Foundry/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mauryantitans/Foundry/discussions)
- **Documentation**: [Full Docs](README.md)

---

**Version**: 1.2.0  
**Status**: Production Ready ✅  
**License**: MIT  
**Last Updated**: November 26, 2025
