# Foundry Examples

**GitHub Repository:** https://github.com/mauryantitans/Foundry

Real-world examples and use cases for Foundry dataset creation.

---

## Table of Contents

- [Basic Examples](#basic-examples)
- [Multi-Object Detection](#multi-object-detection)
- [BYOD (Bring Your Own Data)](#byod-bring-your-own-data)
- [Quality Optimization](#quality-optimization)
- [Production Workflows](#production-workflows)
- [Advanced Use Cases](#advanced-use-cases)

---

## Basic Examples

### Example 1: Simple Dog Detector

**Goal:** Create a basic dog detection dataset

```bash
python pipeline.py --query "dog" --count 10
```

**What happens:**
1. Mines 20 dog images (2x for filtering)
2. Curates for relevance and quality
3. Annotates with bounding boxes
4. Exports to COCO format

**Expected output:**
```
✅ Images Collected: 10/10
✅ Dataset saved to: data/output/coco.json
📊 Success Rate: 100%
```

**COCO structure:**
```json
{
  "categories": [{"id": 1, "name": "dog"}],
  "images": [10 images],
  "annotations": [10+ bounding boxes]
}
```

---

### Example 2: Bicycle Dataset with Quality Loop

**Goal:** High-quality bicycle detection dataset

```bash
python pipeline.py --query "bicycle" --count 15 \
  --enable-quality-loop \
  --validation-method visual \
  --show-metrics
```

**Features used:**
- Quality refinement loop
- Visual validation (more accurate)
- Metrics tracking

**Output:**
```
✅ Images Collected: 15/15
✅ Annotation Success Rate: 93.3%
⏱️  Total Time: 2m 15s
```

**When to use:**
- Production datasets
- Complex objects
- Need high accuracy

---

### Example 3: Quick Test Dataset

**Goal:** Fast dataset for testing/prototyping

```bash
python pipeline.py --query "cat" --count 3 --no-metrics
```

**Optimizations:**
- Small count (3 images)
- No metrics overhead
- No quality loop

**Output time:** ~30 seconds

**When to use:**
- Testing pipeline
- Learning the system
- Quick experiments

---

## Multi-Object Detection

### Example 4: Person with Guitar

**Goal:** Detect both people and guitars in images

**Method 1: Command Line**
```bash
python pipeline.py --query "person,guitar" --count 10
```

**Method 2: Natural Language**
```bash
python pipeline.py

> Input: "I need 10 images of people holding guitars, annotate person and guitar"
```

**What happens:**
1. **Mining**: Searches "person holding guitar"
2. **Curation**: Filters images with both objects
3. **Annotation**: Creates **separate boxes**:
   - All persons → category_id: 1
   - All guitars → category_id: 2

**Output COCO:**
```json
{
  "categories": [
    {"id": 1, "name": "person"},
    {"id": 2, "name": "guitar"}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,  // person
      "bbox": [100, 50, 200, 300]
    },
    {
      "id": 2,
      "image_id": 1,
      "category_id": 2,  // guitar
      "bbox": [150, 200, 100, 150]
    }
  ]
}
```

**Visualization:**
```
Image 1:
┌─────────────────────────┐
│  [Person Box]           │
│     [Guitar Box]        │
│                         │
│  Separate annotations!  │
└─────────────────────────┘
```

---

### Example 5: Street Scene (Dog, Cat, Person)

**Goal:** Urban scene with multiple object types

```bash
python pipeline.py --query "dog,cat,person" --count 20
```

**Search strategy:**
- Finds images containing any/all of these objects
- Each object type gets separate category
- Multiple instances per image supported

**Example annotation:**
```
Image: "person_walking_dog_past_cat.jpg"
Annotations:
  - person: [bbox1]
  - dog: [bbox2]
  - cat: [bbox3]
```

**When to use:**
- Complex scene understanding
- Multiple object relationships
- Rich training data

---

### Example 6: Sports Equipment

**Goal:** Detect various sports equipment

```bash
python pipeline.py --query "basketball,soccer_ball,tennis_racket" --count 25 \
  --enable-quality-loop
```

**Tip:** Use underscores for multi-word objects
- ✅ `soccer_ball`
- ❌ `soccer ball` (might be split)

**Expected categories:**
```json
{
  "categories": [
    {"id": 1, "name": "basketball"},
    {"id": 2, "name": "soccer_ball"},
    {"id": 3, "name": "tennis_racket"}
  ]
}
```

---

## BYOD (Bring Your Own Data)

### Example 7: Annotate Personal Photos

**Scenario:** You have 50 dog photos, need annotations

**Directory structure:**
```
my_dog_photos/
├── IMG_0001.jpg
├── IMG_0002.jpg
├── IMG_0003.jpg
└── ...
```

**Command:**
```bash
python pipeline.py --dir "C:\Users\me\my_dog_photos" --query "dog"
```

**What happens:**
1. Skips mining (uses your images)
2. Skips curation (trusts your images)
3. Annotates all images
4. Exports COCO format

**Output:**
```
✅ Annotated: 50/50 images
✅ Success Rate: 100%
📊 Output: data/output/coco.json
```

---

### Example 8: BYOD with Multi-Object

**Scenario:** Photos containing both cats and dogs

```bash
python pipeline.py --dir "./pet_photos" --query "dog,cat" \
  --enable-quality-loop \
  --validation-method visual
```

**Features:**
- Detects both object types
- Quality validation
- Separate categories for each pet

**Use case:**
- Pet recognition apps
- Animal shelter databases
- Multi-pet households

---

### Example 9: BYOD with Quality Validation

**Scenario:** Critical dataset, need high accuracy

```bash
python pipeline.py --dir "./important_images" --query "defect" \
  --enable-quality-loop \
  --quality-iterations 3 \
  --validation-method hybrid
```

**When to use:**
- Manufacturing defect detection
- Medical imaging
- Safety-critical applications

**Trade-off:**
- Higher accuracy
- Longer processing time
- More API calls

---

## Quality Optimization

### Example 10: Maximum Quality

**Goal:** Best possible annotations, don't care about time

```bash
python pipeline.py --query "bicycle" --count 15 \
  --enable-quality-loop \
  --quality-iterations 5 \
  --validation-method hybrid \
  --show-metrics
```

**Configuration:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 5      # Maximum retries
  validation_method: "hybrid"  # Best validation

annotation:
  workers: 3             # Parallel processing
```

**Expected:**
- Processing time: 5-10 minutes
- Success rate: 95-98%
- API calls: High

---

### Example 11: Speed Optimized

**Goal:** Fastest possible dataset creation

```bash
python pipeline.py --query "dog" --count 10 --no-metrics
```

**Configuration:**
```yaml
quality_loop:
  enabled: false

annotation:
  workers: 1
  
metrics:
  enabled: false
```

**Expected:**
- Processing time: 1-2 minutes
- Success rate: 80-85%
- API calls: Minimal

---

### Example 12: Balanced Approach (Recommended)

**Goal:** Good quality, reasonable speed

```bash
python pipeline.py --query "cat" --count 20 \
  --enable-quality-loop \
  --validation-method coordinate
```

**Configuration:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 2
  validation_method: "coordinate"

annotation:
  workers: 1
```

**Expected:**
- Processing time: 3-4 minutes
- Success rate: 90-92%
- API calls: Moderate

**Best for:**
- Most use cases
- Free tier users
- Good balance

---

## Production Workflows

### Example 13: Batch Dataset Creation

**Scenario:** Need multiple datasets for different objects

**Script: `create_datasets.sh`**
```bash
#!/bin/bash

# Activate environment
source venv/bin/activate

# Create datasets
python pipeline.py --query "dog" --count 50 --config prod_config.yaml
sleep 60  # Wait for rate limit

python pipeline.py --query "cat" --count 50 --config prod_config.yaml
sleep 60

python pipeline.py --query "bird" --count 50 --config prod_config.yaml

# Merge outputs (custom script)
python merge_datasets.py --output final_dataset.json
```

**prod_config.yaml:**
```yaml
quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "visual"

annotation:
  workers: 3

metrics:
  enabled: true
  show_summary: true
```

---

### Example 14: Incremental Dataset Growth

**Scenario:** Start with 10 images, grow to 100

**Week 1:**
```bash
python pipeline.py --query "bicycle" --count 10 \
  --enable-quality-loop
# Output: data/output/coco_v1.json
```

**Week 2:**
```bash
python pipeline.py --query "bicycle" --count 20 \
  --enable-quality-loop
# Output: data/output/coco_v2.json
```

**Merge script:**
```python
# merge.py
import json

def merge_coco_datasets(file1, file2, output):
    with open(file1) as f1, open(file2) as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
    
    # Merge logic here
    merged = {
        "categories": d1["categories"],
        "images": d1["images"] + d2["images"],
        "annotations": d1["annotations"] + d2["annotations"]
    }
    
    with open(output, 'w') as f:
        json.dump(merged, f)

merge_coco_datasets('coco_v1.json', 'coco_v2.json', 'coco_final.json')
```

---

### Example 15: Dataset Validation Pipeline

**Scenario:** Create and validate dataset quality

```bash
# Step 1: Create dataset
python pipeline.py --query "dog" --count 50 \
  --enable-quality-loop \
  --validation-method hybrid \
  --show-metrics > creation_log.txt

# Step 2: Visualize
python visualize_results.py

# Step 3: Manual review
# Check visualizations, note any issues

# Step 4: Re-run if needed with different config
```

---

## Advanced Use Cases

### Example 16: Domain-Specific Objects

**Scenario:** Detecting specific car models

```bash
python pipeline.py --query "tesla_model3,bmw_x5,honda_civic" --count 30 \
  --enable-quality-loop \
  --validation-method visual
```

**Tips:**
- Use specific, unambiguous names
- Include model identifiers
- Consider using custom search engine with car sites

---

### Example 17: Rare Objects

**Scenario:** Objects that are hard to find

```bash
python pipeline.py --query "red_panda" --count 20 \
  --enable-quality-loop
```

**Challenges:**
- Fewer search results
- May need multiple mining iterations
- Curation may filter heavily

**Solution:**
```yaml
# Adjust config for rare objects
pipeline:
  count: 20  # Start modest

quality_loop:
  enabled: true
  validation_method: "visual"  # Ensure relevance
```

---

### Example 18: Indoor vs Outdoor Scenes

**Scenario:** Need scene-specific datasets

**Indoor:**
```bash
python pipeline.py --query "indoor_cat,indoor_dog" --count 25
```

**Outdoor:**
```bash
python pipeline.py --query "outdoor_cat,outdoor_dog" --count 25
```

**Tip:** Search engine context matters
- Add location hints to query
- Use scene descriptors
- Filter in curation stage

---

### Example 19: Time-Sensitive Datasets

**Scenario:** Current events, seasonal objects

```bash
# Holiday decorations
python pipeline.py --query "christmas_tree,halloween_pumpkin" --count 15

# Seasonal
python pipeline.py --query "winter_coat,summer_dress" --count 20
```

**Note:** Search results vary by time of year

---

### Example 20: Creating Training/Validation Splits

**Scenario:** Need separate train/val/test sets

```bash
# Create large dataset
python pipeline.py --query "dog" --count 100 \
  --enable-quality-loop

# Use custom script to split
python split_dataset.py --input data/output/coco.json \
  --train 0.7 --val 0.15 --test 0.15
```

**split_dataset.py:**
```python
import json
import random

def split_coco(input_file, train_ratio, val_ratio, test_ratio):
    with open(input_file) as f:
        data = json.load(f)
    
    images = data['images']
    random.shuffle(images)
    
    n = len(images)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    train_imgs = images[:train_end]
    val_imgs = images[train_end:val_end]
    test_imgs = images[val_end:]
    
    # Create separate COCO files for each split
    # ... (implementation details)
    
split_coco('coco.json', 0.7, 0.15, 0.15)
```

---

## Tips & Tricks

### Tip 1: Verify Multi-Object Output

```bash
# Check categories were created correctly
python -c "
import json
data = json.load(open('data/output/coco.json'))
print('Categories:', [c['name'] for c in data['categories']])
print('Total annotations:', len(data['annotations']))
"
```

### Tip 2: Monitor API Usage

```bash
# Track API calls in real-time
python pipeline.py --query "dog" --count 10 --show-metrics 2>&1 | \
  grep -E "(API|Mining|Curation|Annotation)"
```

### Tip 3: Batch Processing with Error Recovery

```python
# batch_create.py
import subprocess
import time

queries = ["dog", "cat", "bird", "fish"]

for query in queries:
    try:
        subprocess.run([
            "python", "pipeline.py",
            "--query", query,
            "--count", "20",
            "--enable-quality-loop"
        ], check=True)
        
        time.sleep(60)  # Rate limit cooldown
        
    except subprocess.CalledProcessError:
        print(f"Failed for {query}, continuing...")
        continue
```

---

## Common Patterns

### Pattern 1: Iterative Refinement

```bash
# Round 1: Quick test
python pipeline.py --query "bicycle" --count 5

# Review output
python visualize_results.py

# Round 2: Full dataset with adjustments
python pipeline.py --query "bicycle" --count 50 \
  --enable-quality-loop \
  --validation-method visual
```

### Pattern 2: Progressive Quality

```bash
# Start fast, low quality
python pipeline.py --query "dog" --count 100

# Enhance subset with quality loop
python enhance_annotations.py --input coco.json \
  --output coco_enhanced.json \
  --enable-quality-loop
```

### Pattern 3: Multi-Stage Pipeline

```bash
# Stage 1: Mine images
python pipeline.py --query "dog" --count 50

# Stage 2: Manual review & filtering
# (Use external tools)

# Stage 3: Re-annotate filtered set
python pipeline.py --dir "data/curated" --query "dog" \
  --enable-quality-loop
```

---

## Next Steps

- **Integrate with training:** See [Training Guide](TRAINING.md)
- **Advanced configuration:** See [USAGE.md](USAGE.md)
- **Troubleshooting:** See [README.md](../README.md#troubleshooting)
- **Architecture details:** See [knowledge_transfer.md](knowledge_transfer.md)
