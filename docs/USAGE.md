# 📘 Foundry Usage Guide

Comprehensive guide for using Foundry to create object detection datasets.

---

## Table of Contents

1. [Command Line Reference](#command-line-reference)
2. [Configuration File Guide](#configuration-file-guide)
3. [Interactive Mode](#interactive-mode)
4. [Advanced Features](#advanced-features)
5. [Troubleshooting](#troubleshooting)
6. [Performance Tuning](#performance-tuning)

---

## Command Line Reference

### All Available Options

```bash
python pipeline.py [OPTIONS]

Options:
  --config PATH                Path to YAML config file
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

### Common Usage Patterns

#### Standard Mode (Create New Dataset)

**Basic:**
```bash
python pipeline.py --query "cats" --count 10
```

**With Quality Loop:**
```bash
python pipeline.py --query "bicycles" --count 5 --enable-quality-loop
```

**With Visual Validation:**
```bash
python pipeline.py --query "dogs" --count 8 \
  --enable-quality-loop --validation-method visual
```

**Multi-Object Detection:**
```bash
python pipeline.py --query "dogs,cats,cars" --count 15
```

**Maximum Quality:**
```bash
python pipeline.py --query "cars" --count 5 \
  --enable-quality-loop --quality-iterations 3 \
  --validation-method hybrid --show-metrics
```

#### BYOD Mode (Annotate Your Images)

**Basic:**
```bash
python pipeline.py --dir "/path/to/images" --query "elephants"
```

**With Quality Loop:**
```bash
python pipeline.py --dir "C:\my_photos" --query "cats" \
  --enable-quality-loop --validation-method visual
```

**Multi-Object:**
```bash
python pipeline.py --dir "/home/user/pics" --query "dog,cat,bird"
```

#### Using Config Files

**Load config:**
```bash
python pipeline.py --config config.yaml
```

**Config + CLI override:**
```bash
python pipeline.py --config config.yaml --count 20
```

---

## Configuration File Guide

### Basic Structure

```yaml
pipeline:
  query: null          # Object to detect (null = interactive mode)
  count: 5             # Number of images
  mode: "standard"     # standard | byod
  image_dir: null      # Path for BYOD mode

quality_loop:
  enabled: true        # Enable quality refinement
  max_iterations: 2    # Max refinement attempts
  validation_method: "visual"  # coordinate | visual | hybrid

annotation:
  num_workers: 1       # Parallel workers (1 for free tier)

metrics:
  enabled: true        # Track performance
  show_summary: true   # Display summary at end
```

### Example Configurations

#### High-Speed Mode (Free Tier)

```yaml
# fast_mode.yaml
pipeline:
  count: 10

quality_loop:
  enabled: false  # Skip quality loop for speed

annotation:
  num_workers: 1

metrics:
  enabled: false  # Skip metrics for speed
```

**Usage:** `python pipeline.py --config fast_mode.yaml --query "dogs"`

#### High-Quality Mode

```yaml
# quality_mode.yaml
quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "hybrid"  # Best accuracy

annotation:
  num_workers: 1  # Still 1 for free tier

metrics:
  enabled: true
  show_summary: true
```

**Usage:** `python pipeline.py --config quality_mode.yaml --query "bicycles" --count 5`

#### BYOD Template

```yaml
# byod_template.yaml
pipeline:
  mode: "byod"
  image_dir: "C:/my_images"  # Change this
  query: "dog"               # Change this

quality_loop:
  enabled: true
  validation_method: "visual"

metrics:
  enabled: true
```

**Usage:** `python pipeline.py --config byod_template.yaml`

---

## Interactive Mode

### How It Works

1. **Run without arguments:**
   ```bash
   python pipeline.py --config config.yaml
   ```

2. **See detailed help:**
   - MODE 1: Create new datasets
   - MODE 2: Annotate your own images (BYOD)
   - Feature highlights
   - Example requests

3. **Enter your request:**
   ```
   Your request: create 5 images of dogs
   ```

4. **System processes automatically**

### Supported Request Formats

#### Standard Mode Requests

```
✅ "create 5 images of dogs"
✅ "get me 10 bicycle images"
✅ "I need 15 images of cats and dogs"
✅ "find 20 car images"
✅ "search for 8 images of birds"
```

#### BYOD Mode Requests

```
✅ "annotate dogs in C:\Users\me\my_photos"
✅ "I have images at /home/user/pics, detect cats"
✅ "detect bicycles in C:\images\bikes"
✅ "label cars in /path/to/folder"
```

### Tips for Interactive Mode

- Be specific about the count: "5 images" not just "images"
- For BYOD, mention the full path clearly
- Multi-object: "cats and dogs" or "cats, dogs"
- The system uses AI to parse your request, so natural language works!

---

## Advanced Features

### Quality Refinement Loop

The quality loop iteratively improves annotations through validation and feedback.

**How it works:**
```
Initial Annotation → Validation → Feedback → Re-annotation → Approval
         ↑                                                      ↓
         └──────────────── (Repeat up to N times) ─────────────┘
```

**Validation Methods:**

1. **Coordinate Validation (Fast)**
   - Checks bbox numbers and logical consistency
   - Best for: Simple objects, speed priority
   - API calls: Low

2. **Visual Validation (Accurate)**
   - Draws boxes on image for model to see
   - Best for: Complex scenes, accuracy priority
   - API calls: Medium

3. **Hybrid Validation (Best)**
   - Runs both coordinate and visual
   - Best for: Critical datasets, maximum quality
   - API calls: High

**Example output:**
```
🔄 Starting refinement loop for image.jpg
   ✓ Iteration 1: 1 boxes, Status: NEEDS_IMPROVEMENT
     Feedback: "Second bicycle in background not detected"
   ✓ Iteration 2: 2 boxes, Status: APPROVED
✅ Annotation approved after 2 iteration(s)
```

### Multi-Object Detection

Detect multiple object types in the same images.

**Usage:**
```bash
python pipeline.py --query "dogs,cats,birds" --count 10
```

**COCO Output:**
```json
{
  "categories": [
    {"id": 1, "name": "dog"},
    {"id": 2, "name": "cat"},
    {"id": 3, "name": "bird"}
  ],
  "annotations": [
    {"category_id": 1, "bbox": [...]},  // dog
    {"category_id": 2, "bbox": [...]},  // cat
    {"category_id": 3, "bbox": [...]}   // bird
  ]
}
```

### Metrics Collection

Track detailed performance metrics.

**Enable:**
```bash
python pipeline.py --query "dogs" --count 5 --show-metrics
```

**Output:**
```
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

## Troubleshooting

### Rate Limit Errors (429)

**Error:**
```
429 Resource exhausted. Please try again later.
```

**Cause:** Exceeded Gemini API free tier limit (15 requests/minute)

**Solutions:**

1. **Reduce workers:**
   ```yaml
   annotation:
     num_workers: 1  # Down from 3
   ```

2. **Use coordinate validation:**
   ```yaml
   quality_loop:
     validation_method: "coordinate"  # Instead of visual
   ```

3. **Wait between runs:**
   - Free tier resets every 60 seconds
   - Wait 1 minute before next run

4. **Disable quality loop temporarily:**
   ```bash
   python pipeline.py --query "dogs" --count 5  # No --enable-quality-loop
   ```

5. **Upgrade to paid tier:**
   - Paid tier: 1000 RPM (vs 15 RPM free)
   - [Pricing info](https://ai.google.dev/pricing)

### No Images Found

**Error:**
```
Miner returned no images
```

**Solutions:**

1. **Check API keys:**
   ```bash
   # Verify .env file exists and has correct keys
   cat .env
   ```

2. **Verify Custom Search setup:**
   - Check `GOOGLE_SEARCH_CX` is correct
   - Verify search engine is configured to search entire web
   - [Setup guide](https://programmablesearchengine.google.com/)

3. **Check API quotas:**
   - [Google Cloud Console](https://console.cloud.google.com/)
   - Custom Search API: 100 queries/day free

4. **Try different query:**
   ```bash
   # More specific
   python pipeline.py --query "golden retriever dog" --count 5
   ```

### All Images Filtered

**Error:**
```
Curator filtered all images in this batch
```

**Cause:** Images don't contain the target object or are low quality

**Solutions:**

1. **Use broader terms:**
   ```bash
   # Instead of "golden retriever puppy"
   python pipeline.py --query "dog" --count 10
   ```

2. **Check search results manually:**
   - Look at images in `data/raw/`
   - Verify they contain the object

3. **Review curation logs:**
   ```bash
   python pipeline.py --query "cats" --count 5 --show-metrics
   # Check why images were rejected
   ```

### AttributeError or KeyError

**Error:**
```
AttributeError: 'list' object has no attribute 'items'
KeyError: 'feedback'
```

**Cause:** Bug in older versions (fixed in latest)

**Solution:**
```bash
# Pull latest code
git pull origin main

# Or verify you have the fixes in:
# - agents/main_agent.py (line 153)
# - agents/quality_loop.py (line 281)
```

### Visualization Fails

**Error:**
```
FileNotFoundError: data/output/coco.json
```

**Cause:** No successful pipeline run yet

**Solution:**
```bash
# Run pipeline first
python pipeline.py --query "dogs" --count 2

# Then visualize
python visualize_results.py
```

---

## Performance Tuning

### Speed vs Quality Trade-offs

| Configuration | Speed | Quality | Use Case |
|--------------|-------|---------|----------|
| No quality loop | Fastest | Good | Quick prototyping |
| Coordinate validation | Fast | Better | Production (balanced) |
| Visual validation | Medium | Best | High-accuracy needs |
| Hybrid validation | Slowest | Maximum | Critical datasets |

### Optimal Configurations

#### Free Tier (15 RPM)

```yaml
annotation:
  num_workers: 1

quality_loop:
  enabled: true
  max_iterations: 2
  validation_method: "coordinate"

metrics:
  enabled: true
```

**Performance:** ~15s for 2 images

#### Paid Tier (1000 RPM)

```yaml
annotation:
  num_workers: 3

quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "visual"

metrics:
  enabled: true
```

**Performance:** ~20s for 10 images

### Benchmarks

Based on testing with 2-image datasets:

| Mode | Workers | Validation | Time | API Calls |
|------|---------|------------|------|-----------|
| Standard | 1 | None | ~10s | ~8 |
| Standard | 1 | Coordinate | ~15s | ~12 |
| Standard | 1 | Visual | ~17s | ~16 |
| BYOD | 1 | Coordinate | ~4s | ~6 |
| BYOD | 1 | Visual | ~5s | ~10 |

---

## Best Practices

### For Free Tier Users

1. **Always use `num_workers: 1`**
2. **Start with coordinate validation**
3. **Use visual validation only when needed**
4. **Batch your work** (wait 60s between runs)
5. **Test with small counts first** (2-5 images)

### For Production Use

1. **Use config files** for reproducibility
2. **Enable metrics** to track performance
3. **Use visual validation** for accuracy
4. **Test with small batches** before large runs
5. **Keep backups** of successful configs

### For Development

1. **Disable quality loop** for faster iteration
2. **Use small counts** (1-2 images)
3. **Enable metrics** to debug issues
4. **Check logs** in console output

---

## Next Steps

- See [EXAMPLES.md](EXAMPLES.md) for real-world use cases
- See [knowledge_transfer.md](knowledge_transfer.md) for technical details
- See [test_report.md](test_report.md) for integration test results
- Check [../README.md](../README.md) for quick reference
