# 💡 Foundry Examples & Use Cases

Real-world examples and practical use cases for Foundry.

---

## Table of Contents

1. [Quick Examples](#quick-examples)
2. [Real-World Use Cases](#real-world-use-cases)
3. [Workflow Examples](#workflow-examples)
4. [Integration Examples](#integration-examples)

---

## Quick Examples

### Example 1: Simple Dataset Creation

**Goal:** Create a small dataset of tables for testing

```bash
python pipeline.py --query "tables" --count 5 --show-metrics
```

**Output:**
```
📋 Standard Mode: Creating dataset with 5 images of 'tables'

2025-11-25 14:30:15 - Mining completed: 5 images saved
2025-11-25 14:30:28 - Finished. Kept 5 images
2025-11-25 14:30:35 - Parallel annotation completed: 5/5 images annotated
2025-11-25 14:30:36 - Dataset saved successfully

============================================================
📊 PIPELINE METRICS SUMMARY
============================================================

📈 Overview:
   Total Images Saved: 5
   Curation Success: 100.0%
   Annotation Success: 100.0%

⏱️  Total Time: 24.33s
============================================================
```

**Result:** `data/output/coco.json` with 5 annotated table images

---

### Example 2: Multi-Object Detection

**Goal:** Detect both dogs and cats in images

```bash
python pipeline.py --query "dogs,cats" --count 3 \
  --enable-quality-loop --show-metrics
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
      "bbox": [120, 80, 200, 150]
    },
    {
      "id": 2,
      "image_id": 1,
      "category_id": 2,
      "bbox": [350, 100, 180, 140]
    }
  ]
}
```

---

### Example 3: BYOD Mode (Your Own Images)

**Goal:** Annotate your personal photo collection

```bash
python pipeline.py --dir "C:\Users\me\my_pandas" \
  --query "panda" --show-metrics
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
- Fast annotation-only workflow (4-5s per image)

---

### Example 4: Quality Refinement in Action

**Goal:** Get highest quality annotations

```bash
python pipeline.py --query "bicycles" --count 2 \
  --enable-quality-loop --quality-iterations 3 \
  --validation-method visual
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

**Result:** Higher quality annotations with multiple iterations

---

## Real-World Use Cases

### Use Case 1: Training a Pet Detector

**Scenario:** You're building a mobile app to detect pets in photos

**Requirements:**
- 50 images each of dogs and cats
- High-quality annotations
- COCO format for PyTorch training

**Solution:**

**Step 1:** Create dog dataset
```bash
python pipeline.py --query "dog" --count 50 \
  --enable-quality-loop --validation-method visual \
  --show-metrics
```

**Step 2:** Create cat dataset
```bash
python pipeline.py --query "cat" --count 50 \
  --enable-quality-loop --validation-method visual \
  --show-metrics
```

**Step 3:** Merge datasets (manual or script)

**Step 4:** Train model
```python
from pycocotools.coco import COCO

coco = COCO('data/output/coco.json')
# Use with your PyTorch/TensorFlow training pipeline
```

**Time:** ~30 minutes total  
**Cost:** Free (using free tier)

---

### Use Case 2: Annotating Security Camera Footage

**Scenario:** You have 1000 frames from security cameras and need to detect vehicles

**Requirements:**
- Annotate existing images (no web search)
- Detect cars, trucks, motorcycles
- Fast processing

**Solution:**

**config.yaml:**
```yaml
pipeline:
  mode: "byod"
  image_dir: "C:/security_footage/frames"
  query: "car,truck,motorcycle"

quality_loop:
  enabled: false  # Speed priority

annotation:
  num_workers: 1  # Free tier

metrics:
  enabled: true
```

**Run:**
```bash
python pipeline.py --config config.yaml
```

**Time:** ~1 hour for 1000 images  
**Result:** All frames annotated with vehicle bounding boxes

---

### Use Case 3: Creating a Retail Product Dataset

**Scenario:** E-commerce company needs product detection for inventory management

**Requirements:**
- Multiple product categories
- High accuracy (visual validation)
- Production-ready dataset

**Solution:**

**products_config.yaml:**
```yaml
pipeline:
  query: "shoes,bags,watches,sunglasses"
  count: 100  # 25 per category

quality_loop:
  enabled: true
  max_iterations: 3
  validation_method: "hybrid"  # Maximum accuracy

annotation:
  num_workers: 1

metrics:
  enabled: true
  show_summary: true
```

**Run:**
```bash
python pipeline.py --config products_config.yaml
```

**Post-processing:**
- Review visualizations in `data/debug/`
- Manually verify critical annotations
- Export to production system

**Time:** ~2 hours  
**Quality:** Production-ready

---

### Use Case 4: Research Dataset for Academic Paper

**Scenario:** PhD student needs a dataset of bicycles for research

**Requirements:**
- 200 high-quality images
- Diverse scenes and angles
- Reproducible methodology

**Solution:**

**research_config.yaml:**
```yaml
pipeline:
  query: "bicycle"
  count: 200

quality_loop:
  enabled: true
  max_iterations: 2
  validation_method: "visual"

annotation:
  num_workers: 1

metrics:
  enabled: true
  show_summary: true
```

**Workflow:**
```bash
# Run pipeline
python pipeline.py --config research_config.yaml

# Visualize results
python visualize_results.py

# Document in paper
# "Dataset created using Foundry v1.0 with visual validation"
```

**Benefits:**
- Reproducible (config file saved)
- Documented (metrics logged)
- High quality (visual validation)

---

## Workflow Examples

### Workflow 1: Iterative Dataset Refinement

**Goal:** Build a dataset incrementally, reviewing and refining

**Step 1:** Start small
```bash
python pipeline.py --query "cars" --count 5 \
  --enable-quality-loop --show-metrics
```

**Step 2:** Review
```bash
python visualize_results.py
# Check data/debug/ for visualizations
```

**Step 3:** Adjust and expand
```bash
# If quality is good, scale up
python pipeline.py --query "cars" --count 20 \
  --enable-quality-loop --validation-method visual
```

**Step 4:** Final production run
```bash
python pipeline.py --query "cars" --count 100 \
  --enable-quality-loop --validation-method hybrid
```

---

### Workflow 2: Multi-Stage Dataset Creation

**Goal:** Create a complex dataset with multiple object types

**Stage 1:** Vehicles
```bash
python pipeline.py --query "car,truck,bus,motorcycle" --count 50
```

**Stage 2:** Pedestrians
```bash
python pipeline.py --query "person,pedestrian" --count 50
```

**Stage 3:** Traffic signs
```bash
python pipeline.py --query "stop sign,traffic light" --count 30
```

**Stage 4:** Merge (manual or script)
```python
import json

# Load all COCO files
datasets = []
for file in ['vehicles.json', 'pedestrians.json', 'signs.json']:
    with open(file) as f:
        datasets.append(json.load(f))

# Merge logic here
# Save final dataset
```

---

### Workflow 3: Quality Assurance Pipeline

**Goal:** Ensure dataset quality through multiple validation stages

**Step 1:** Initial creation (fast)
```bash
python pipeline.py --query "bicycles" --count 20
```

**Step 2:** Visual inspection
```bash
python visualize_results.py
# Manual review of data/debug/
```

**Step 3:** Re-annotate problematic images
```bash
# Copy problematic images to separate folder
python pipeline.py --dir "data/review" --query "bicycle" \
  --enable-quality-loop --validation-method hybrid
```

**Step 4:** Merge and finalize

---

## Integration Examples

### Example 1: PyTorch Integration

```python
from pycocotools.coco import COCO
from torch.utils.data import Dataset
import cv2

class FoundryDataset(Dataset):
    def __init__(self, coco_path, img_dir):
        self.coco = COCO(coco_path)
        self.img_dir = img_dir
        self.img_ids = list(self.coco.imgs.keys())
    
    def __getitem__(self, idx):
        img_id = self.img_ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = f"{self.img_dir}/{img_info['file_name']}"
        
        # Load image
        img = cv2.imread(img_path)
        
        # Load annotations
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns = self.coco.loadAnns(ann_ids)
        
        # Extract bboxes and labels
        boxes = [ann['bbox'] for ann in anns]
        labels = [ann['category_id'] for ann in anns]
        
        return img, boxes, labels
    
    def __len__(self):
        return len(self.img_ids)

# Usage
dataset = FoundryDataset('data/output/coco.json', 'data/curated')
```

---

### Example 2: TensorFlow Integration

```python
import tensorflow as tf
import json

def load_foundry_dataset(coco_path, img_dir):
    with open(coco_path) as f:
        coco = json.load(f)
    
    images = []
    labels = []
    
    for img in coco['images']:
        img_path = f"{img_dir}/{img['file_name']}"
        
        # Load image
        img_data = tf.io.read_file(img_path)
        img_tensor = tf.image.decode_jpeg(img_data)
        
        # Get annotations for this image
        img_anns = [ann for ann in coco['annotations'] 
                    if ann['image_id'] == img['id']]
        
        images.append(img_tensor)
        labels.append(img_anns)
    
    return images, labels

# Usage
images, labels = load_foundry_dataset('data/output/coco.json', 'data/curated')
```

---

### Example 3: Automated Pipeline Script

```python
#!/usr/bin/env python3
"""
Automated dataset creation script
"""
import subprocess
import time

def create_dataset(query, count, config='config.yaml'):
    """Run Foundry pipeline"""
    cmd = [
        'python', 'pipeline.py',
        '--config', config,
        '--query', query,
        '--count', str(count)
    ]
    
    print(f"Creating dataset for: {query}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success: {query}")
    else:
        print(f"❌ Failed: {query}")
        print(result.stderr)
    
    # Wait to avoid rate limits
    time.sleep(60)

# Create multiple datasets
datasets = [
    ('dog', 20),
    ('cat', 20),
    ('bird', 15),
    ('car', 25)
]

for query, count in datasets:
    create_dataset(query, count)

print("All datasets created!")
```

---

### Example 4: Custom Validation Script

```python
#!/usr/bin/env python3
"""
Validate Foundry output quality
"""
import json

def validate_coco(coco_path):
    """Check COCO format validity"""
    with open(coco_path) as f:
        coco = json.load(f)
    
    issues = []
    
    # Check required fields
    required = ['images', 'annotations', 'categories']
    for field in required:
        if field not in coco:
            issues.append(f"Missing field: {field}")
    
    # Check annotations
    for ann in coco.get('annotations', []):
        bbox = ann.get('bbox', [])
        if len(bbox) != 4:
            issues.append(f"Invalid bbox in annotation {ann['id']}")
        
        if bbox[2] <= 0 or bbox[3] <= 0:
            issues.append(f"Invalid bbox dimensions in {ann['id']}")
    
    # Report
    if issues:
        print("❌ Validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Validation passed!")
        return True

# Usage
validate_coco('data/output/coco.json')
```

---

## Tips & Tricks

### Tip 1: Batch Processing with Rate Limits

```bash
# Create a batch script
for query in dog cat bird fish; do
    python pipeline.py --query "$query" --count 10
    echo "Waiting 60s to avoid rate limits..."
    sleep 60
done
```

### Tip 2: Config Templates

Keep a library of configs for different scenarios:

```
configs/
├── fast.yaml          # Speed priority
├── quality.yaml       # Accuracy priority
├── byod.yaml          # Template for own images
└── production.yaml    # Balanced for production
```

### Tip 3: Visualization Review

```bash
# After pipeline run
python visualize_results.py

# Open data/debug/ in image viewer
# Quickly scan all annotations
```

### Tip 4: Incremental Datasets

```bash
# Day 1: Create base
python pipeline.py --query "cars" --count 50

# Day 2: Add more (different search offset)
# Images are deduplicated automatically
python pipeline.py --query "cars" --count 50
```

---

## Next Steps

- See [USAGE.md](USAGE.md) for detailed command reference
- See [../README.md](../README.md) for quick start guide
- See [knowledge_transfer.md](knowledge_transfer.md) for technical details
- See [test_report.md](test_report.md) for integration test results
