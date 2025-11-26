# Foundry Usage Guide

**GitHub Repository:** https://github.com/mauryantitans/Foundry

Complete guide to using Foundry for dataset creation.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Modes of Operation](#modes-of-operation)
- [Command Line Reference](#command-line-reference)
- [Configuration File](#configuration-file)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [API Rate Limits](#api-rate-limits)

---

## Getting Started

### First Run

1. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Verify setup:**
```bash
python pipeline.py --help
```

3. **Run interactive mode:**
```bash
python pipeline.py
```

### Quick Examples

```bash
# Simple dataset
python pipeline.py --query "dog" --count 5

# Multi-object
python pipeline.py --query "person,guitar" --count 10

# With quality loop
python pipeline.py --query "bicycle" --count 8 --enable-quality-loop

# Your own images
python pipeline.py --dir "C:\my_photos" --query "cat"
```

---

## Modes of Operation

### 1. Interactive Mode

**Launch:**
```bash
python pipeline.py
```

**Features:**
- Natural language understanding
- Contextual help with examples
- Two modes: Create New | Annotate Existing

**Example Requests:**
```
✅ "create 5 images of dogs"
✅ "get 10 red sports cars"
✅ "I need 15 images of people holding guitars, annotate person and guitar"
✅ "annotate dogs in C:\my_photos"
```

**How it works:**
1. MainAgent parses your natural language request
2. Extracts: search query, objects to annotate, image count
3. Displays execution plan
4. Runs pipeline
5. Shows results and metrics

---

### 2. Command Line Mode

**Basic Syntax:**
```bash
python pipeline.py [OPTIONS]
```

**Core Arguments:**

| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `--query` | TEXT | Object(s) to detect | `--query "dog"` |
| `--count` | INT | Number of images | `--count 10` |
| `--dir` | PATH | Directory for BYOD | `--dir "C:\images"` |
| `--request` | TEXT | Natural language | `--request "5 dog images"` |

**Examples:**
```bash
# Single object
python pipeline.py --query "dog" --count 10

# Multiple objects (comma-separated)
python pipeline.py --query "dog,cat,person" --count 15

# BYOD mode
python pipeline.py --dir "./photos" --query "elephant"

# Natural language via CLI
python pipeline.py --request "create 5 images of bicycles"
```

---

### 3. Config File Mode

**Create config.yaml:**
```yaml
pipeline:
  query: "dog"
  count: 10
  mode: "standard"

quality_loop:
  enabled: true
  max_iterations: 2
  validation_method: "coordinate"

annotation:
  workers: 1

metrics:
  enabled: true
  show_summary: true
```

**Usage:**
```bash
# Use config file
python pipeline.py --config config.yaml

# Override specific values
python pipeline.py --config config.yaml --count 20 --query "cat"
```

**Priority:** CLI args > config file > defaults

---

## Command Line Reference

### Complete Options List

```bash
python pipeline.py [OPTIONS]
```

#### Pipeline Options

**`--config PATH`**
- Path to YAML configuration file
- Example: `--config my_config.yaml`

**`--request TEXT`**
- Natural language request
- Example: `--request "create 10 dog images"`

**`--query TEXT`**
- Object(s) to detect (comma-separated for multi-object)
- Example: `--query "dog,cat"`

**`--count INT`**
- Number of images to collect
- Default: 5
- Example: `--count 15`

**`--dir PATH`**
- Directory path for BYOD mode
- Example: `--dir "C:\Users\me\photos"`

#### Advanced Options

**`--enable-quality-loop`**
- Enable quality refinement loop
- Increases processing time but improves accuracy
- Example: `python pipeline.py --query "dog" --count 5 --enable-quality-loop`

**`--quality-iterations INT`**
- Maximum quality loop iterations
- Default: 2
- Range: 1-5
- Example: `--quality-iterations 3`

**`--validation-method TEXT`**
- Quality validation method
- Choices: `coordinate` | `visual` | `hybrid`
- Default: `coordinate`
- Example: `--validation-method visual`

**`--no-metrics`**
- Disable metrics collection
- Example: `python pipeline.py --query "dog" --count 5 --no-metrics`

**`--show-metrics`**
- Display detailed metrics summary at end
- Example: `python pipeline.py --query "dog" --count 5 --show-metrics`

### Usage Patterns

**Quick Test:**
```bash
python pipeline.py --query "dog" --count 3 --no-metrics
```

**High Quality:**
```bash
python pipeline.py --query "bicycle" --count 10 \
  --enable-quality-loop \
  --quality-iterations 3 \
  --validation-method hybrid \
  --show-metrics
```

**Multi-Object:**
```bash
python pipeline.py --query "person,guitar,microphone" --count 15
```

**BYOD with Quality:**
```bash
python pipeline.py --dir "./my_images" --query "dog,cat" \
  --enable-quality-loop \
  --validation-method visual
```

---

## Configuration File

### Complete config.yaml Reference

```yaml
# Pipeline settings
pipeline:
  query: null              # Search query (null = use CLI/interactive)
  count: 5                 # Number of images
  mode: "standard"         # standard | byod
  image_dir: null          # Directory for BYOD mode

# Quality refinement loop
quality_loop:
  enabled: false           # Enable quality loop
  max_iterations: 2        # Max retry attempts (1-5)
  validation_method: "coordinate"  # coordinate | visual | hybrid

# Annotation settings
annotation:
  workers: 1               # Parallel workers (1 for free tier)

# Metrics tracking
metrics:
  enabled: true            # Collect performance metrics
  show_summary: true       # Display summary at end
```

### Configuration Examples

**Speed-Optimized (Free Tier):**
```yaml
pipeline:
  query: "dog"
  count: 10

quality_loop:
  enabled: false

annotation:
  workers: 1

metrics:
  enabled: true
```

**Quality-Optimized:**
```yaml
pipeline:
  query: "bicycle"
  count: 20

quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "hybrid"

annotation:
  workers: 1

metrics:
  enabled: true
  show_summary: true
```

**BYOD Mode:**
```yaml
pipeline:
  mode: "byod"
  image_dir: "C:/Users/me/photos"
  query: "dog,cat"

quality_loop:
  enabled: true
  validation_method: "visual"

metrics:
  enabled: true
```

---

## Advanced Features

### Multi-Object Detection

Detect multiple object types in the same images.

**Command Line:**
```bash
python pipeline.py --query "person,guitar" --count 10
```

**Natural Language:**
```
"I need 15 images of people holding guitars, annotate person and guitar"
```

**How it works:**
1. **Mining**: Searches for scenes containing all objects
   - Query optimization: "person holding guitar"
2. **Annotation**: Creates separate bounding boxes
   - Person boxes: `category_id: 1`
   - Guitar boxes: `category_id: 2`

**Output:**
```json
{
  "categories": [
    {"id": 1, "name": "person"},
    {"id": 2, "name": "guitar"}
  ],
  "annotations": [
    {"category_id": 1, "bbox": [...], "image_id": 1},  // person
    {"category_id": 2, "bbox": [...], "image_id": 1}   // guitar
  ]
}
```

---

### Quality Refinement Loop

Automatically improve annotation quality through validation and retry.

**Enable:**
```bash
python pipeline.py --query "dog" --count 10 --enable-quality-loop
```

**How it works:**
1. Generate initial annotation
2. Validate annotation quality
3. If validation fails → retry with improved prompt
4. Repeat up to `max_iterations` times
5. Use best result

**Validation Methods:**

**Coordinate Validation** (Fast):
- Checks bbox coordinates are valid (0-1000 range)
- Ensures proper format `[ymin, xmin, ymax, xmax]`
- No additional API calls
- ✅ Best for: Free tier, simple objects

**Visual Validation** (Accurate):
- Uses vision AI to verify annotation correctness
- Checks object actually exists at bbox location
- Additional API calls per validation
- ✅ Best for: Critical datasets, complex scenes

**Hybrid Validation** (Comprehensive):
- Combines coordinate + visual validation
- Most API calls, highest quality
- ✅ Best for: Production datasets, multiple objects

**Configuration:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 3              # Retry up to 3 times
  validation_method: "hybrid"    # Use both methods
```

---

### BYOD Mode (Bring Your Own Data)

Annotate your own images without web search.

**Usage:**
```bash
python pipeline.py --dir "C:\my_photos" --query "dog"
```

**Features:**
- No image mining (uses your images)
- Full annotation pipeline
- Quality loop support
- COCO format export

**Directory Structure:**
```
my_photos/
├── image1.jpg
├── image2.png
├── photo3.jpeg
└── ...
```

**Supported formats:** JPG, JPEG, PNG

**Example with multi-object:**
```bash
python pipeline.py --dir "./photos" --query "dog,cat,person" \
  --enable-quality-loop
```

---

### Metrics & Monitoring

Track pipeline performance in real-time.

**Enable:**
```bash
python pipeline.py --query "dog" --count 10 --show-metrics
```

**Tracked Metrics:**

**Overview:**
- Pipeline runs
- Total images mined, curated, annotated, saved

**Success Rates:**
- Curation success rate (% kept)
- Annotation success rate (% successful)

**Timings:**
- Pipeline total time
- Mining time
- Curation time
- Annotation time
- Engineering time

**Errors:**
- Error counts by type and stage

**Example Output:**
```
============================================================
📊 PIPELINE METRICS SUMMARY
============================================================

📈 Overview:
   Pipeline Runs: 1
   Total Images Mined: 10
   Total Images Curated: 8
   Total Images Annotated: 8
   Total Images Saved: 8

✅ Success Rates:
   Curation Avg: 80.0%
   Annotation Avg: 100.0%

⏱️  Average Timings:
   Pipeline Total: 45.23s (1 runs)
   Mining: 8.12s (1 runs)
   Curation: 15.34s (1 runs)
   Annotation: 18.56s (1 runs)
   Engineering: 0.05s (1 runs)

✅ No errors recorded
============================================================
```

---

## Troubleshooting

### Rate Limit Errors (429)

**Error:**
```
ERROR: 429 Resource exhausted
Quota exceeded for metric: generate_content_free_tier_requests
```

**Solutions:**

1. **Reduce workers:**
```yaml
annotation:
  workers: 1  # Essential for free tier
```

2. **Use coordinate validation:**
```yaml
quality_loop:
  validation_method: "coordinate"  # Fewer API calls
```

3. **Disable quality loop temporarily:**
```bash
python pipeline.py --query "dog" --count 5
# Don't use --enable-quality-loop
```

4. **Wait between runs:**
```bash
python pipeline.py --query "dog" --count 5
sleep 60  # Wait 1 minute
python pipeline.py --query "cat" --count 5
```

5. **Check current usage:**
- Visit [Google AI Studio](https://ai.google.dev/)
- Check "Quota" section
- Free tier: 15 requests/minute
- Paid tier: 1000+ requests/minute

---

### No Images Found

**Error:**
```
Mining completed: 0 images saved
```

**Checklist:**

1. **Verify API keys in `.env`:**
```env
GEMINI_API_KEY=AIza...
GOOGLE_SEARCH_API_KEY=AIza...
GOOGLE_SEARCH_CX=abc123...
```

2. **Check Custom Search API quota:**
- Visit [Google Cloud Console](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/)
- Free tier: 100 queries/day
- Check usage in "Metrics" tab

3. **Test search directly:**
```bash
curl "https://www.googleapis.com/customsearch/v1?q=dog&key=YOUR_API_KEY&cx=YOUR_CX"
```

4. **Try different query:**
```bash
# Instead of:
python pipeline.py --query "small brown dog in park"

# Try:
python pipeline.py --query "dog"
```

---

### All Images Filtered

**Error:**
```
Curated: 0 images
No images passed curation
```

**Causes & Solutions:**

1. **Search returned irrelevant images:**
   - Use more specific query
   - Check Google Custom Search Engine settings

2. **Images too low quality:**
   - Source better images
   - Adjust search query

3. **Debug with logs:**
```bash
python pipeline.py --query "dog" --count 5 --show-metrics 2>&1 | tee debug.log
```
Review rejection reasons in `debug.log`

---

### JSON Parsing Failures

**Error:**
```
WARNING: All JSON parsing strategies failed
```

**Built-in Solutions:**
Foundry has 5-strategy fallback parser that automatically:
1. Direct JSON parse
2. Remove markdown fences
3. Fix common issues (quotes, commas)
4. Extract JSON arrays with regex
5. Reconstruct from bbox patterns

**If persistent:**
1. **Check Gemini API status:**
   - Visit [Google API Status](https://status.cloud.google.com/)

2. **Try simpler query:**
```bash
# Instead of:
python pipeline.py --query "dog,cat,person,bicycle" --count 10

# Try:
python pipeline.py --query "dog" --count 5
```

3. **Enable retry:**
```bash
python pipeline.py --query "dog" --count 5 --enable-quality-loop
# Retry logic activates automatically
```

---

### Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solution:**
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Verify (should see "(venv)" prefix)
python pipeline.py --help

# If still fails, reinstall
pip install --upgrade -r requirements.txt
```

---

## Best Practices

### For Free Tier Users

**Optimal Configuration:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 2              # Balance quality/speed
  validation_method: "coordinate" # Fewest API calls

annotation:
  workers: 1                      # Prevent rate limits

metrics:
  enabled: true
```

**Workflow:**
1. Test with small counts first: `--count 3`
2. Wait 60s between runs
3. Use coordinate validation
4. Monitor rate limit warnings

---

### For Production Datasets

**Optimal Configuration:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "hybrid"

annotation:
  workers: 3  # Parallel processing

metrics:
  enabled: true
  show_summary: true
```

**Workflow:**
1. Use specific queries
2. Enable quality loop
3. Review metrics after each run
4. Validate output with visualizer

---

### For Multi-Object Datasets

**Tips:**
1. **Use natural language for better search:**
```bash
python pipeline.py
> "15 images of people holding guitars, annotate person and guitar"
```

2. **Verify separate categories:**
```bash
python -c "import json; print(json.load(open('data/output/coco.json'))['categories'])"
```

3. **Check annotation distribution:**
```bash
python visualize_results.py  # Verify boxes are separate
```

---

### For BYOD Mode

**Preparation:**
1. Organize images in one directory
2. Use consistent image format (JPG recommended)
3. Remove corrupt/tiny images

**Best Results:**
```bash
# Clear, specific query
python pipeline.py --dir "./photos" --query "dog" \
  --enable-quality-loop \
  --validation-method visual

# Multi-object in own images
python pipeline.py --dir "./photos" --query "dog,cat" \
  --enable-quality-loop
```

---

## API Rate Limits

### Gemini API Limits

**Free Tier:**
- 15 requests per minute (RPM)
- 1,500 requests per day (RPD)
- 1 million tokens per minute (TPM)

**Paid Tier:**
- 1,000+ RPM (varies by plan)
- Higher daily limits
- Priority support

### Google Custom Search API Limits

**Free Tier:**
- 100 queries per day
- Cannot be increased

**Paid Tier:**
- $5 per 1,000 queries
- Up to 10,000 queries/day

### Managing Limits

**Track Usage:**
```bash
# Monitor API calls in logs
python pipeline.py --query "dog" --count 5 --show-metrics 2>&1 | grep "API"
```

**Optimize Calls:**
1. Use `coordinate` validation (no extra calls)
2. Set `workers: 1` (sequential processing)
3. Disable quality loop for testing
4. Batch similar queries together

**Example Calculation:**
```
Standard Run (10 images, no quality loop):
- Mining: 1 call
- Curation: 10 calls (1 per image)
- Annotation: 10 calls (1 per image)
Total: ~21 calls

With Quality Loop (coordinate):
- Same as above (coordinate doesn't add calls)
Total: ~21 calls

With Quality Loop (visual):
- Mining: 1 call
- Curation: 10 calls
- Annotation: 10 calls
- Validation: 10 calls (visual check)
- Retries: up to 10 calls (if needed)
Total: ~41 calls max
```

---

## Getting Help

**Logs:**
```bash
# View detailed logs
python pipeline.py --query "dog" --count 5 2>&1 | tee run.log
```

**Debug Mode:**
```python
# Edit utils/logger.py
# Set level to DEBUG
logger.setLevel(logging.DEBUG)
```

**Community:**
- GitHub Issues: [Report bugs](https://github.com/mauryantitans/Foundry/issues)
- GitHub Discussions: [Ask questions](https://github.com/mauryantitans/Foundry/discussions)
- Documentation: [Full docs](../README.md)

---

**Need more examples?** See [EXAMPLES.md](EXAMPLES.md)

**Technical details?** See [knowledge_transfer.md](knowledge_transfer.md)
