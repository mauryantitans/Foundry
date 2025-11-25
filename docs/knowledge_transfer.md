# 📚 Foundry Knowledge Transfer Document

**Document Purpose:** Comprehensive technical guide for developers to understand, maintain, and extend Foundry

**Last Updated:** November 23, 2025  
**System Status:** Production Ready

---

## 📖 Table of Contents

1. [System Overview](#-system-overview)
2. [Architecture Deep Dive](#-architecture-deep-dive)
3. [Agent Details](#-agent-details)
4. [Data Flow](#-data-flow)
5. [Code Examples](#-code-examples)
6. [Testing & Debugging](#-testing--debugging)
7. [Deployment Guide](#-deployment-guide)
8. [Extension Points](#-extension-points)
9. [Performance Optimization](#-performance-optimization)
10. [Troubleshooting Guide](#-troubleshooting-guide)

---

## 🎯 System Overview

### **What is Foundry?**

Foundry is a multi-agent AI system that automates object detection dataset creation. It handles the entire pipeline from image discovery to annotated COCO format output.

### **Core Value Proposition**

```
Manual Dataset Creation:
- Search images: 2 hours
- Download & organize: 1 hour
- Annotate (50 images): 8 hours
- Format conversion: 30 minutes
Total: ~11.5 hours
-----------------------------------
Foundry Automation:
- Entire process: ~5 minutes
- Quality: Higher (AI validation)
- Reproducibility: Perfect
Total: ~5 minutes (140x faster!)
```

### **Technology Stack**

```python
# Core Technologies
Python 3.10+                    # Base language
Google Gemini 2.0 Flash         # Vision + Language AI
Google Custom Search API        # Image discovery
google-generativeai             # AI SDK
PIL (Pillow)                    # Image processing
imagehash                       # Deduplication

# Architecture Pattern
Multi-Agent System              # Specialized agents
Producer-Consumer               # Parallel processing
Loop Pattern                    # Quality refinement
Observer Pattern                # Metrics & logging
```

---

## 🏗️ Architecture Deep Dive

### **1. Multi-Agent System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   USER INPUT                                                │
│   "create 10 images of dogs"                                │
│         │                                                   │
│         ↓                                                   │
│   ┌──────────────────────────────────────┐                  │
│   │      MAIN AGENT (Orchestrator)       │                  │
│   │  - Parses request                    │                  │
│   │  - Manages workflow                  │                  │
│   │  - Coordinates sub-agents            │                  │
│   │  - Handles loops & retries           │                  │
│   └──────────────┬───────────────────────┘                  │
│                  │                                          │
│     ┌────────────┼────────────┬────────────┬──────────┐     │
│     │            │            │            │          │     │
│     ↓            ↓            ↓            ↓          ↓     │
│  ┌──────┐   ┌────────┐   ┌──────────┐  ┌────────┐  ┌───┐    │
│  │MINER │   │CURATOR │   │ANNOTATOR │  │QUALITY │  │ENG│    │
│  │      │   │        │   │          │  │ LOOP   │  │   │    │
│  └──────┘   └────────┘   └──────────┘  └────────┘  └───┘    │
│                                                             │
│  Supporting Systems:                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Metrics Collector  │  Error Handler  │  Logger   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
│                         ↓                                   │
│                   COCO OUTPUT                               │
│              data/output/coco.json                          │
└─────────────────────────────────────────────────────────────┘

### **2. Configuration System**

**File:** `utils/config_loader.py` & `config.yaml`

Foundry uses a layered configuration system:

1.  **Defaults:** Hardcoded safe defaults
2.  **Config File:** `config.yaml` (System Settings)
3.  **CLI Arguments:** Overrides everything (Job Parameters)

**Config Structure (`config.yaml`):**
```yaml
pipeline:
  mode: "standard"
quality_loop:
  enabled: true
  validation_method: "visual"  # The magic happens here
annotation:
  num_workers: 3
```

**Loading Logic:**
```python
def initialize_config(config_path=None, cli_args=None):
    # 1. Load defaults
    config = Config()
    
    # 2. Merge YAML
    if config_path:
        config.load_from_yaml(config_path)
        
    # 3. Apply CLI overrides
    if cli_args:
        if cli_args.query: config.set('pipeline.query', cli_args.query)
        if cli_args.validation_method: 
            config.set('quality_loop.validation_method', cli_args.validation_method)
            
    return config
```
```

### **2. Agent Communication Pattern**

```python
# Agent Base Class
class Agent:
    """
    Base agent with Gemini model integration.
    All agents inherit from this base class.
    """
    def __init__(self, name, instructions, tools=None, model_name="gemini-2.0-flash"):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = self._configure_model()
        
    def run(self, input_text):
        """Send message and get response"""
        response = self.chat_session.send_message(input_text)
        return response.text
```

**Communication Flow:**
```
MainAgent.run_pipeline()
    ↓
    calls → MinerAgent.mine(query, count)
    ↓
    receives → {status: "success", data: [paths], count: 5}
    ↓
    calls → CuratorAgent.curate(query, paths)
    ↓
    receives → [curated_paths]
    ↓
    calls → ParallelAnnotatorAgent.annotate_parallel(query, paths)
    ↓
    receives → {filename: {bboxes, width, height}, ...}
    ↓
    calls → EngineerAgent.process_item() for each
    ↓
    calls → EngineerAgent.save()
    ↓
    receives → output_path
```

### **3. Data Structures**

#### **Image Metadata**
```python
{
    "filename": "abc123.jpg",
    "bboxes": [
        {
            "label": "dog",
            "bbox": [100, 150, 300, 450]  # [ymin, xmin, ymax, xmax] (0-1000)
        }
    ],
    "width": 800,   # pixels
    "height": 600   # pixels
}
```

#### **COCO Format**
```python
{
    "info": {
        "year": 2025,
        "version": "1.0",
        "description": "Dataset for dogs generated by Foundry",
        "contributor": "Foundry Agent",
        "date_created": "2025-11-23T17:30:00"
    },
    "licenses": [],
    "categories": [
        {"id": 1, "name": "dog", "supercategory": "object"}
    ],
    "images": [
        {
            "id": 1,
            "width": 800,
            "height": 600,
            "file_name": "abc123.jpg"
        }
    ],
    "annotations": [
        {
            "id": 1,
            "image_id": 1,
            "category_id": 1,
            "bbox": [120, 90, 200, 180],  # [x, y, width, height] pixels
            "area": 36000,
            "iscrowd": 0,
            "segmentation": []
        }
    ]
}
```

#### **Error Structure**
```python
{
    "category": "timeout",      # ErrorCategory enum
    "severity": "medium",       # ErrorSeverity enum
    "message": "Mining timeout after 10 images",
    "stage": "mining",          # Which pipeline stage
    "details": {
        "query": "dogs",
        "attempted": 10,
        "error": "Connection timeout"
    },
    "recoverable": True,
    "retry_suggested": True
}
```

#### **Metrics Structure**
```python
{
    "pipeline_runs": 1,
    "images_mined": 10,
    "images_curated": 8,
    "images_annotated": 8,
    "images_saved": 8,
    "curation_success_rate": [80.0],  # 8/10 = 80%
    "annotation_success_rate": [100.0],  # 8/8 = 100%
    "timings": {
        "mining": [3.21],
        "curation": [12.45],
        "annotation": [8.67],
        "engineering": [0.34],
        "pipeline_total": [24.67]
    },
    "errors": {}  # {stage_error_type: count}
}
```

---

## 🤖 Agent Details

### **1. Main Agent (Orchestrator)**

**File:** `agents/main_agent.py`

**Responsibilities:**
- Parse user requests using LLM
- Orchestrate pipeline execution
- Manage execution loops
- Handle mode switching (Standard vs BYOD)
- Coordinate sub-agents

**Key Methods:**

```python
class MainAgent(Agent):
    def __init__(self):
        # Initialize all sub-agents
        self.miner = MinerAgent()
        self.curator = CuratorAgent()
        self.annotator = AnnotatorAgent()
        self.parallel_annotator = ParallelAnnotatorAgent(num_workers=3)
        self.engineer = None  # Initialized per run
        
    def run_pipeline(self, user_request=None, query=None, count=None):
        """
        Standard mode: Mine → Curate → Annotate → Save
        
        Flow:
        1. Parse request to extract query & count
        2. Loop until target count reached:
            a. Mine images
            b. Curate for quality
            c. Annotate in parallel
            d. Add to dataset
        3. Engineer to COCO format
        4. Save output
        """
        # Parse request
        if user_request:
            query, count = self._parse_request(user_request)
        
        # Execution loop
        final_dataset = {}
        loop_count = 0
        max_loops = 5
        
        while len(final_dataset) < count and loop_count < max_loops:
            # Mine
            mine_result = self.miner.mine(query, max_images=count)
            
            # Curate
            curated_images = self.curator.curate(query, mine_result["data"])
            
            # Annotate (parallel if multiple images)
            if len(curated_images) > 1:
                annotations = self.parallel_annotator.annotate_parallel(
                    query, curated_images
                )
            else:
                annotations = self.annotator.annotate(query, curated_images)
            
            # Add to final dataset
            final_dataset.update(annotations)
            loop_count += 1
        
        # Engineer & save
        self.engineer = EngineerAgent(query=query)
        for filename, data in final_dataset.items():
            self.engineer.process_item(filename, data)
        self.engineer.save()
    
    def run_byod_mode(self, image_dir, query):
        """
        BYOD mode: Annotate → Save
        
        Skips mining and curation, directly annotates
        existing images in the provided directory.
        """
        image_paths = list_images(image_dir)
        annotations = self.parallel_annotator.annotate_parallel(query, image_paths)
        
        self.engineer = EngineerAgent(query=query)
        for filename, data in annotations.items():
            self.engineer.process_item(filename, data)
        self.engineer.save()
```

**Request Parsing Example:**

```python
# Input: "create 10 images of dogs and cats"

# LLM Prompt:
"""Extract the object query and count from: 'create 10 images of dogs and cats'
Return JSON: {'query': 'object name', 'count': number}"""

# LLM Response:
{"query": "dogs,cats", "count": 10}

# Parsed:
query = "dogs,cats"
count = 10
```

---

### **2. Miner Agent**

**File:** `agents/miner.py`

**Responsibilities:**
- Search web for images using Google Custom Search
- Download images
- Deduplicate using perceptual hashing
- Return file paths

**Key Algorithm:**

```python
class MinerAgent(Agent):
    def mine(self, query, max_images=10):
        """
        Mining Algorithm:
        
        1. Call Google Custom Search API
        2. Get image URLs
        3. Download each URL
        4. Check for duplicates (perceptual hash)
        5. Save unique images
        6. Return paths
        """
        # Step 1-2: Search and get URLs
        urls = self._search_images(query, max_images)
        
        # Step 3-6: Download and deduplicate
        saved_paths = []
        for url in urls:
            # Download
            saved_path = save_image(url, self.download_folder)
            
            if saved_path:
                # Calculate perceptual hash
                with Image.open(saved_path) as img:
                    img_hash = imagehash.phash(img)
                
                # Check duplicates
                is_duplicate = False
                for seen_hash in self.seen_hashes:
                    if img_hash - seen_hash < 5:  # Hamming distance threshold
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    self.seen_hashes.append(img_hash)
                    saved_paths.append(saved_path)
                else:
                    os.remove(saved_path)  # Remove duplicate
        
        return {
            "status": "success",
            "data": saved_paths,
            "count": len(saved_paths)
        }
```

**Deduplication Explained:**

```
Perceptual Hashing (pHash):
- Creates a hash based on image visual content
- Similar images have similar hashes
- Hamming distance measures similarity

Example:
Image A hash: 10110101...  ┐
Image B hash: 10110001...  ├─ Distance = 1 → Similar!
                           │
Image C hash: 01001110...  ├─ Distance = 8 → Different
                           ┘

Threshold = 5: Images with distance < 5 are duplicates
```

---

### **3. Curator Agent**

**File:** `agents/curator.py`

**Responsibilities:**
- Filter images for quality and relevance
- Ensure target object is present
- Deduplicate across batches
- Reject low-quality images

**Quality Check Prompt:**

```python
prompt = f"""
Does this image contain the actual, visible {query} object?

IMPORTANT: The {query} must be physically present and clearly visible.

REJECT if:
- Only text mentioning '{query}'
- Packaging/labels with '{query}' written on them
- Products that mention '{query}' but don't show actual object

Answer strictly with YES or NO.
"""
```

**Decision Tree:**

```
For each image:
    │
    ├─→ Calculate hash
    │   │
    │   ├─→ Duplicate? → Reject
    │   └─→ Unique → Continue
    │
    ├─→ Send to Vision LLM with prompt
    │   │
    │   ├─→ Response contains "YES" → Accept ✅
    │   └─→ Response contains "NO" → Reject ❌
    │
    └─→ Copy accepted images to curated folder
```

---

### **4. Annotator Agents**

#### **4a. Regular Annotator**

**File:** `agents/annotator.py`

**Use:** Single image annotation

```python
class AnnotatorAgent(Agent):
    def annotate(self, query, image_paths):
        """
        Annotate images sequentially.
        
        Process:
        1. Load image
        2. Build prompt based on query (single vs multi-object)
        3. Send to Vision LLM
        4. Parse JSON response
        5. Auto-fix common JSON issues
        6. Validate format
        7. Return annotations
        """
        annotations = {}
        
        for img_path in image_paths:
            image = Image.open(img_path)
            width, height = image.size
            
            # Build prompt
            if single_object:
                prompt = f"""
                Return bounding boxes for ALL instances of {query}.
                Output JSON: [{{"label": "object_name", "bbox": [ymin, xmin, ymax, xmax]}}]
                Use normalized coordinates (0-1000 range).
                """
            else:
                prompt = f"""
                Return bounding boxes for ALL instances of: {objects_list}
                Label each object separately.
                Output JSON: [{{"label": "object_name", "bbox": [ymin, xmin, ymax, xmax]}}]
                """
            
            # Get response
            response = self.model.generate_content([prompt, image])
            
            # Parse and auto-fix
            data = self._parse_with_autofix(response.text)
            
            annotations[filename] = {
                "bboxes": data,
                "width": width,
                "height": height
            }
        
        return annotations
```

**JSON Auto-Fix:**

```python
def _parse_with_autofix(text):
    """
    Auto-fix common JSON formatting issues.
    
    Fixes:
    - Single quotes → double quotes
    - Trailing commas → removed
    - Markdown wrapping → stripped
    """
    # Clean markdown
    text = text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try fixes
        fixed = text.replace("'", '"')  # Single → double quotes
        fixed = re.sub(r',\s*}', '}', fixed)  # Remove trailing commas
        fixed = re.sub(r',\s*]', ']', fixed)
        return json.loads(fixed)
```

#### **4b. Parallel Annotator**

**File:** `agents/parallel_annotator.py`

**Use:** Batch annotation (3 concurrent workers)

**Architecture:**

```
┌──────────────────────────────────────────────────────┐
│           Parallel Annotation System                  │
├──────────────────────────────────────────────────────┤
│                                                        │
│  Input: [img1, img2, img3, img4, img5]               │
│                                                        │
│         ↓                                              │
│                                                        │
│  ThreadPoolExecutor (3 workers)                       │
│  ┌─────────────┬─────────────┬─────────────┐        │
│  │  Worker 1   │  Worker 2   │  Worker 3   │        │
│  │             │             │             │        │
│  │  img1 ✅    │  img2 ✅    │  img3 ✅    │        │
│  │    ↓        │    ↓        │    ↓        │        │
│  │  img4 ✅    │  img5 ✅    │  (idle)     │        │
│  └─────────────┴─────────────┴─────────────┘        │
│                                                        │
│         ↓                                              │
│                                                        │
│  Collect Results as they complete                     │
│  {img1: {bboxes: [...], width: 800, height: 600},    │
│   img2: {...}, ...}                                   │
│                                                        │
└──────────────────────────────────────────────────────┘
```

**Implementation:**

```python
class ParallelAnnotatorAgent:
    def __init__(self, num_workers=3):
        self.num_workers = num_workers
        self.workers = [self._create_worker(i) for i in range(num_workers)]
    
    def annotate_parallel(self, query, image_paths):
        """
        Parallel annotation using ThreadPoolExecutor.
        
        Benefits:
        - 3x faster than sequential
        - Non-blocking I/O during API calls
        - Efficient resource utilization
        """
        annotations = {}
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.annotate_image, i % self.num_workers, 
                               img_path, query, objects): img_path
                for i, img_path in enumerate(image_paths)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                result = future.result()
                if result:
                    annotations[result["filename"]] = {
                        "bboxes": result["bboxes"],
                        "width": result["width"],
                        "height": result["height"]
                    }
        
        return annotations
```

---

### **5. Quality Loop Agent**

**File:** `agents/quality_loop.py`

**Purpose:** Iteratively improve annotation quality through validation

**Flow Diagram:**

```
┌──────────────────────────────────────────────────────────┐
│              Quality Refinement Loop                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  START                                                     │
│    ↓                                                       │
│  [Annotate Image]                                         │
│    ↓                                                       │
│  {bboxes: [...], iteration: 1}                           │
│    ↓                                                       │
│  [Validate Quality]                                       │
│    ├─ Check completeness (all objects detected?)         │
│    ├─ Check accuracy (boxes well-fitted?)                │
│    └─ Check correctness (no false positives?)            │
│    ↓                                                       │
│  Decision:                                                 │
│    ├─→ APPROVED → Return annotation ✅                    │
│    │                                                       │
│    └─→ NEEDS_IMPROVEMENT → Generate feedback             │
│        ↓                                                   │
│        "Second dog in background not detected"            │
│        ↓                                                   │
│        [Re-annotate with feedback]                        │
│        ↓                                                   │
│        iteration += 1                                      │
│        ↓                                                   │
│        [iteration < max?]                                 │
│         ├─→ YES → Go to [Annotate Image]                 │
│         └─→ NO → Return best annotation                   │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
class AnnotationRefinementLoop:
    def annotate_with_refinement(self, image_path, query):
        """
        Iterative refinement algorithm.
        
        Process:
        1. Initial annotation
        2. Validate quality
        3. If not approved:
            a. Generate feedback
            b. Re-annotate with feedback
            c. Repeat (max 3 times)
        4. Return best annotation
        """
        iteration = 0
        best_annotation = None
        refinement_history = []
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Annotate (with feedback from previous iteration if available)
            if refinement_history:
                feedback = refinement_history[-1]["feedback"]
                annotation = self._annotate_with_feedback(
                    image_path, query, feedback
                )
            else:
                annotation = self._annotate(image_path, query)
            
            # Validate
            validation = self.validator.validate(
                image_path, query, annotation["bboxes"]
            )
            
            # Track history
            refinement_history.append({
                "iteration": iteration,
                "num_bboxes": len(annotation["bboxes"]),
                "validation_status": validation["status"],
                "feedback": validation.get("feedback", ""),
                "issues": validation.get("issues", [])
            })
            
            # Update best
            if best_annotation is None or validation["status"] == "APPROVED":
                best_annotation = annotation
            
            # Stop if approved
            if validation["status"] == "APPROVED":
                break
        
        # Add refinement stats
        best_annotation["refinement_stats"] = {
            "iterations": iteration,
            "history": refinement_history,
            "final_status": refinement_history[-1]["validation_status"]
        }
        
        return best_annotation
```

**Validation Prompt:**

```python
prompt = f"""
Validate these bounding box annotations for '{query}':
Number of boxes: {len(bboxes)}
Bounding boxes: {json.dumps(bboxes)}

Check for:
1. Completeness: Are all {query} instances detected?
2. Accuracy: Are boxes properly fitted (not too loose/tight)?
3. Correctness: Any false positives (wrong objects)?

Return JSON:
{{
    "status": "APPROVED" or "NEEDS_IMPROVEMENT",
    "feedback": "detailed feedback if improvements needed",
    "issues": ["list of specific issues"]
}}
"""

**Validation Methods:**

The `QualityValidator` supports three modes:

1.  **Coordinate (`_validate_coordinate`):**
    *   Fastest.
    *   Sends raw coordinates to LLM.
    *   Good for checking logical consistency.

2.  **Visual (`_validate_visual`):**
    *   **Most Accurate.**
    *   Draws the bounding boxes onto the image using PIL.
    *   Sends the *annotated image* to the Vision LLM.
    *   Prompt: "Do these red boxes accurately cover the dogs?"
    *   Eliminates coordinate hallucination issues.

3.  **Hybrid (`_validate_hybrid`):**
    *   Runs both methods.
    *   Requires both to pass.
    *   Maximum rigor for high-stakes datasets.

**Visual Helper:**
```python
def _draw_boxes_on_image(self, image_path, bboxes):
    """Draws red boxes on a copy of the image for validation"""
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        for box in bboxes:
            # Convert normalized 0-1000 to pixels
            # Draw rectangle with width=3
            draw.rectangle(coords, outline="red", width=3)
        return img
```

**Error Handling:**

The quality loop includes robust error handling:

1. **API Errors (429):** Caught and logged, refinement history records the error
2. **Missing Feedback:** Safe access using `.get("feedback", "")` prevents KeyError
3. **Failed Iterations:** Returns best annotation from successful iterations

```python
except Exception as e:
    logger.error(f"Error in iteration {iteration}: {e}", exc_info=True)
    refinement_history.append({
        "iteration": iteration,
        "error": str(e)
        # Note: No "feedback" key when error occurs
    })

# Next iteration safely accesses feedback
last_feedback = refinement_history[-1].get("feedback", "")
if not last_feedback:
    # Use default prompt without feedback
```

```

---

### **6. Engineer Agent**

**File:** `agents/engineer.py`

**Responsibilities:**
- Convert normalized bboxes to absolute coordinates
- Map object labels to category IDs
- Generate COCO format JSON
- Save to disk

**Coordinate Transformation:**

```python
def process_item(self, filename, data):
    """
    Transform annotations to COCO format.
    
    Input (normalized 0-1000):
    {
        "bboxes": [{"label": "dog", "bbox": [100, 200, 300, 400]}],
        "width": 800,
        "height": 600
    }
    
    Output (absolute pixels):
    {
        "bbox": [160, 60, 160, 120],  # [x, y, width, height]
        "category_id": 1,
        "area": 19200
    }
    """
    for item in data["bboxes"]:
        # Extract normalized bbox
        ymin, xmin, ymax, xmax = item["bbox"]  # 0-1000 range
        
        # Convert to absolute coordinates
        abs_x = (xmin / 1000) * data["width"]     # Left edge
        abs_y = (ymin / 1000) * data["height"]    # Top edge
        abs_w = ((xmax - xmin) / 1000) * data["width"]   # Width
        abs_h = ((ymax - ymin) / 1000) * data["height"]  # Height
        
        # Get category ID
        label = item.get("label")
        category_id = self.cat_name_to_id.get(label, 1)
        
        # Add annotation
        self.coco_data["annotations"].append({
            "id": self.annotation_id,
            "image_id": self.image_id,
            "category_id": category_id,
            "bbox": [abs_x, abs_y, abs_w, abs_h],
            "area": abs_w * abs_h,
            "iscrowd": 0,
            "segmentation": []
        })
        
        self.annotation_id += 1
```

**Coordinate System:**

```
Normalized (0-1000):          Absolute (Pixels):
┌────────────┐               ┌────────────┐
│            │               │            │
│  ymin,xmin │               │    x,y     │
│  ┌───────┐ │               │  ┌───────┐ │
│  │       │ │               │  │       │ │
│  └───────┘ │               │  └───────┘ │
│  ymax,xmax │               │    w,h     │
│            │               │            │
└────────────┘               └────────────┘
  (0-1000)                      (pixels)

Transformation:
x = (xmin / 1000) * image_width
y = (ymin / 1000) * image_height
w = ((xmax - xmin) / 1000) * image_width
h = ((ymax - ymin) / 1000) * image_height
```

---

## 🔄 Data Flow

### **Complete Pipeline Flow**

```
┌──────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. USER INPUT                                                 │
│     "create 10 images of dogs"                                │
│     ↓                                                          │
│                                                                │
│  2. PARSE REQUEST (Main Agent + LLM)                          │
│     Input: "create 10 images of dogs"                         │
│     Output: {query: "dogs", count: 10}                        │
│     ↓                                                          │
│                                                                │
│  3. MINING (Miner Agent)                                      │
│     Input: query="dogs", max_images=10                        │
│     Process:                                                   │
│       → Google Search API call                                │
│       → Download 10 URLs                                      │
│       → Deduplicate (perceptual hash)                         │
│     Output: {status: "success", data: [paths], count: 8}     │
│     Files: data/raw/abc123.jpg, data/raw/def456.jpg, ...     │
│     ↓                                                          │
│                                                                │
│  4. CURATION (Curator Agent)                                  │
│     Input: query="dogs", paths=[8 image paths]               │
│     Process:                                                   │
│       For each image:                                          │
│         → Calculate hash (deduplicate across batches)         │
│         → Vision LLM quality check                            │
│         → "Does image contain actual dog?"                    │
│         → Copy to curated if YES                              │
│     Output: [6 curated paths]                                 │
│     Files: data/curated/abc123.jpg, ...                       │
│     ↓                                                          │
│                                                                │
│  5. ANNOTATION (Parallel Annotator - 3 workers)              │
│     Input: query="dogs", paths=[6 curated images]            │
│     Process:                                                   │
│       Worker 1: img1, img2                                    │
│       Worker 2: img3, img4                                    │
│       Worker 3: img5, img6                                    │
│       Each:                                                    │
│         → Load image                                           │
│         → Vision LLM annotation                               │
│         → Parse JSON (with auto-fix)                          │
│         → Return {bboxes: [...], width, height}              │
│     Output: {                                                  │
│       "abc123.jpg": {                                         │
│         "bboxes": [{"label": "dog", "bbox": [100,200,300,400]}],│
│         "width": 800, "height": 600                           │
│       },                                                       │
│       ...                                                      │
│     }                                                          │
│     ↓                                                          │
│                                                                │
│  6. QUALITY LOOP (Optional)                                   │
│     Input: annotations from step 5                            │
│     Process:                                                   │
│       For each annotation:                                     │
│         → Validate quality                                     │
│         → If not approved:                                    │
│             → Generate feedback                               │
│             → Re-annotate with feedback                       │
│             → Repeat (max 3 times)                            │
│         → Return best annotation                              │
│     Output: Refined annotations                               │
│     ↓                                                          │
│                                                                │
│  7. ENGINEERING (Engineer Agent)                              │
│     Input: Final annotations                                   │
│     Process:                                                   │
│       For each image:                                          │
│         → Add image entry to COCO                             │
│         → For each bbox:                                      │
│             → Transform coordinates (normalized → absolute)   │
│             → Map label to category_id                        │
│             → Add annotation entry                            │
│     Output: COCO JSON structure                               │
│     ↓                                                          │
│                                                                │
│  8. SAVE                                                      │
│     Write to: data/output/coco.json                           │
│     Format: Standard COCO JSON                                │
│     ↓                                                          │
│                                                                │
│  9. METRICS (If enabled)                                      │
│     Display:                                                   │
│       - Success rates                                          │
│       - Timing for each stage                                │
│       - Error counts                                           │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### **BYOD Mode Flow**

```
┌──────────────────────────────────────────────────────────────┐
│                    BYOD MODE FLOW                             │
│           (Bring Your Own Data - Skip Mining)                 │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. USER INPUT                                                 │
│     --dir "C:\my_images" --query "pandas"                    │
│     ↓                                                          │
│                                                                │
│  2. LIST IMAGES                                               │
│     Scan directory for .jpg, .jpeg, .png                     │
│     Output: [path1, path2, ..., path15]                      │
│     ↓                                                          │
│                                                                │
│  3. ANNOTATION (Parallel - 3 workers)                        │
│     [Same as standard mode step 5]                            │
│     ↓                                                          │
│                                                                │
│  4. QUALITY LOOP (Optional)                                   │
│     [Same as standard mode step 6]                            │
│     ↓                                                          │
│                                                                │
│  5. ENGINEERING                                               │
│     [Same as standard mode step 7]                            │
│     ↓                                                          │
│                                                                │
│  6. SAVE                                                      │
│     data/output/coco.json                                     │
│                                                                │
└──────────────────────────────────────────────────────────────┘

Time Saved: ~50% (skips mining and curation)
```

---

## 💻 Code Examples

### **Example 1: Basic Usage**

```python
from agents.main_agent import MainAgent

# Create agent
agent = MainAgent()

# Run pipeline
agent.run_pipeline(query="dogs", count=5)

# Output will be at: data/output/coco.json
```

### **Example 2: With Metrics**

```python
from agents.main_agent import MainAgent
from utils.phase2_integration import initialize_phase2_features

# Initialize with metrics
phase2 = initialize_phase2_features(enable_metrics=True)

# Run pipeline
agent = MainAgent()
agent.run_pipeline(query="cats", count=10)

# Show metrics
metrics = phase2.get_metrics()
summary = metrics.get_summary()
print(f"Success rate: {summary['success_rates']['annotation_avg']}")
phase2.print_metrics_summary()
```

### **Example 3: With Quality Loop**

```python
from utils.phase2_integration import initialize_phase2_features
from agents.main_agent import MainAgent

# Enable quality refinement
phase2 = initialize_phase2_features(
    enable_metrics=True,
    enable_quality_loop=True,
    quality_loop_iterations=3  # Max 3 refinement attempts
)

# Run with quality validation
agent = MainAgent()
agent.run_pipeline(query="bicycles", count=5)

# Metrics will include refinement stats
phase2.print_metrics_summary()
```

### **Example 4: BYOD Mode**

```python
from agents.main_agent import MainAgent

agent = MainAgent()

# Annotate existing images
agent.run_byod_mode(
    image_dir="C:\\Users\\me\\my_images",
    query="elephants"
)

# Output: data/output/coco.json with annotations
```

### **Example 5: Custom Agent Configuration**

```python
from agents.main_agent import MainAgent
from agents.parallel_annotator import ParallelAnnotatorAgent

# Create custom parallel annotator with 5 workers
custom_annotator = ParallelAnnotatorAgent(num_workers=5)

# Create main agent
agent = MainAgent()

# Replace default parallel annotator
agent.parallel_annotator = custom_annotator

# Run with custom configuration
agent.run_pipeline(query="cars", count=20)
```

### **Example 6: Error Handling**

```python
from utils.error_handler import (
    ErrorHandler,
    create_error_response,
    create_success_response
)

def safe_pipeline_run(query, count):
    """Pipeline with comprehensive error handling."""
    try:
        agent = MainAgent()
        agent.run_pipeline(query=query, count=count)
        
        return create_success_response(
            message=f"Successfully created dataset with {count} images",
            data={"query": query, "count": count}
        )
        
    except Exception as e:
        # Create structured error
        error = ErrorHandler.handle_mining_error(e, query=query, attempted=count)
        
        # Log it
        ErrorHandler.log_error(error)
        
        # Check if should retry
        if ErrorHandler.should_retry(error, attempt=1, max_attempts=3):
            print("Retrying...")
            return safe_pipeline_run(query, count)
        else:
            return create_error_response(
                message="Pipeline failed after retries",
                error=error
            )
```

### **Example 7: Custom Metrics Tracking**

```python
from utils.metrics import get_metrics_collector
import time

# Get metrics collector
metrics = get_metrics_collector()

# Start pipeline tracking
metrics.start_pipeline()

# Track custom stage
metrics.start_stage("custom_processing")
time.sleep(2)  # Your processing here
metrics.end_stage("custom_processing", success=True, count=10)

# Record custom metrics
metrics.record_mining(attempted=15, successful=12, time_taken=5.2)
metrics.record_annotation(total=12, successful=11, time_taken=8.3)

# End and display
metrics.end_pipeline()
metrics.print_summary()
```

### **Example 8: Manual Quality Loop**

```python
from agents.quality_loop import AnnotationRefinementLoop
from agents.annotator import AnnotatorAgent

# Create annotator and quality loop
annotator = AnnotatorAgent()
quality_loop = AnnotationRefinementLoop(
    annotator_agent=annotator,
    max_iterations=3
)

# Annotate with refinement
result = quality_loop.annotate_with_refinement(
    image_path="path/to/image.jpg",
    query="dog"
)

# Check results
if result:
    print(f"Bboxes: {len(result['bboxes'])}")
    print(f"Iterations: {result['refinement_stats']['iterations']}")
    print(f"Final status: {result['refinement_stats']['final_status']}")
    
    # Access refinement history
    for iteration in result['refinement_stats']['history']:
        print(f"Iteration {iteration['iteration']}: {iteration['validation_status']}")
```

### **Example 9: Load and Process COCO Output**

```python
import json

# Load COCO output
with open('data/output/coco.json', 'r') as f:
    coco_data = json.load(f)

# Create category lookup
categories = {cat['id']: cat['name'] for cat in coco_data['categories']}

# Create image lookup
images = {img['id']: img for img in coco_data['images']}

# Process annotations
for ann in coco_data['annotations']:
    image_id = ann['image_id']
    category_name = categories[ann['category_id']]
    bbox = ann['bbox']  # [x, y, width, height]
    
    image = images[image_id]
    filename = image['file_name']
    
    print(f"{filename}: {category_name} at [{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]")
```

### **Example 10: Integrate with PyTorch DataLoader**

```python
from pycocotools.coco import COCO
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os

class FoundryDataset(Dataset):
    """PyTorch Dataset from Foundry output."""
    
    def __init__(self, coco_json_path, image_dir, transform=None):
        self.coco = COCO(coco_json_path)
        self.image_dir = image_dir
        self.transform = transform
        self.ids = list(sorted(self.coco.imgs.keys()))
    
    def __len__(self):
        return len(self.ids)
    
    def __getitem__(self, index):
        # Load image info
        img_id = self.ids[index]
        img_info = self.coco.loadImgs(img_id)[0]
        path = os.path.join(self.image_dir, img_info['file_name'])
        
        # Load image
        image = Image.open(path).convert("RGB")
        
        # Load annotations
        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns = self.coco.loadAnns(ann_ids)
        
        # Extract boxes and labels
        boxes = []
        labels = []
        for ann in anns:
            x, y, w, h = ann['bbox']
            boxes.append([x, y, x+w, y+h])  # Convert to [x1, y1, x2, y2]
            labels.append(ann['category_id'])
        
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        
        target = {"boxes": boxes, "labels": labels, "image_id": torch.tensor([img_id])}
        
        if self.transform:
            image = self.transform(image)
        
        return image, target

# Usage
dataset = FoundryDataset(
    coco_json_path='data/output/coco.json',
    image_dir='data/curated'
)

dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

for images, targets in dataloader:
    # Train your model
    pass
```

---

## 🧪 Testing & Debugging

### **Test Cases**

```python
# Test 1: Simple dataset creation
def test_simple_creation():
    agent = MainAgent()
    agent.run_pipeline(query="dogs", count=3)
    
    # Verify output exists
    assert os.path.exists('data/output/coco.json')
    
    # Load and validate
    with open('data/output/coco.json') as f:
        coco = json.load(f)
    
    assert len(coco['images']) == 3
    assert len(coco['categories']) == 1
    assert coco['categories'][0]['name'] == 'dog'

# Test 2: Multi-object detection
def test_multi_object():
    agent = MainAgent()
    agent.run_pipeline(query="dogs,cats", count=2)
    
    with open('data/output/coco.json') as f:
        coco = json.load(f)
    
    assert len(coco['categories']) == 2
    category_names = {cat['name'] for cat in coco['categories']}
    assert 'dog' in category_names
    assert 'cat' in category_names

# Test 3: BYOD mode
def test_byod_mode():
    # Create test images
    test_dir = 'test_images'
    os.makedirs(test_dir, exist_ok=True)
    
    # ... create test images ...
    
    agent = MainAgent()
    agent.run_byod_mode(image_dir=test_dir, query="test")
    
    assert os.path.exists('data/output/coco.json')

# Test 4: Metrics tracking
def test_metrics():
    from utils.phase2_integration import initialize_phase2_features
    
    phase2 = initialize_phase2_features(enable_metrics=True)
    metrics = phase2.get_metrics()
    
    metrics.start_pipeline()
    metrics.record_mining(attempted=5, successful=5, time_taken=2.0)
    metrics.end_pipeline()
    
    summary = metrics.get_summary()
    assert summary['overview']['total_images_mined'] == 5

# Test 5: Error handling
def test_error_handling():
    from utils.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
    
    error = ErrorHandler.handle_mining_error(
        Exception("Timeout"),
        query="test",
        attempted=5
    )
    
    assert error.category == ErrorCategory.TIMEOUT
    assert error.recoverable == True
    assert error.retry_suggested == True
```

### **Debugging Tips**

```python
# Enable debug logging
from utils.logger import setup_logging
import logging

setup_logging(log_level=logging.DEBUG)

# Log will show:
# - All agent interactions
# - API calls and responses
# - Stage transitions
# - Error details with stack traces

# Check specific logs
logger = logging.getLogger("foundry.miner")
logger.debug("Mining started")
logger.info("Found 5 images")
logger.warning("Duplicate detected")
logger.error("Download failed", exc_info=True)
```

### **Common Debug Scenarios**

```python
# Scenario 1: Pipeline hangs
# Check: API rate limits, network connectivity
# Solution: Add timeout, check API quotas

# Scenario 2: Poor annotation quality
# Check: Image quality, object visibility
# Solution: Enable quality loop, adjust prompts

# Scenario 3: Memory issues with large batches
# Check: Number of images, parallel workers
# Solution: Reduce batch size, decrease workers

# Scenario 4: Inconsistent COCO output
# Check: Coordinate transformations, category mapping
# Solution: Verify bbox calculations, validate categories
```

---

## 🚀 Deployment Guide

### **Production Checklist**

```bash
# 1. Environment Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API Keys
cat > .env << EOF
GEMINI_API_KEY=your_production_key
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_CX=your_cx_id
EOF

# 3. Test Run
python pipeline.py --query "test" --count 2 --show-metrics

# 4. Verify Output
cat data/output/coco.json | jq '.info'

# 5. Production Run
python pipeline.py --query "your_object" --count 100 \
  --enable-quality-loop --quality-iterations 2 --show-metrics
```

### **Docker Deployment (Optional)**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/raw data/curated data/output

# Run
CMD ["python", "pipeline.py"]
```

```bash
# Build and run
docker build -t foundry .
docker run -v $(pwd)/data:/app/data -v $(pwd)/.env:/app/.env foundry \
  --query "dogs" --count 10
```

### **Monitoring**

```python
# Add application monitoring
from utils.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Export metrics to your monitoring system
summary = metrics.get_summary()
send_to_monitoring_system(summary)
```

---

## 🔧 Extension Points

### **1. Add New Agent**

```python
# agents/my_custom_agent.py
from agents.base_agent import Agent

class MyCustomAgent(Agent):
    def __init__(self):
        instructions = "You are a custom agent..."
        super().__init__(name="MyCustomAgent", instructions=instructions)
    
    def process(self, input_data):
        # Your custom logic
        result = self.run(f"Process: {input_data}")
        return result

# Use in main_agent.py
class MainAgent(Agent):
    def __init__(self):
        # ...existing agents...
        self.custom_agent = MyCustomAgent()
    
    def run_pipeline(self, ...):
        # ...existing pipeline...
        custom_result = self.custom_agent.process(data)
```

### **2. Add Custom Tool**

```python
# tools/my_tool.py
def my_custom_tool(param1: str, param2: int) -> dict:
    """
    Custom tool with structured return.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        {"status": "success"|"error", "data": ..., "error_message": ...}
    """
    try:
        # Your tool logic
        result = process(param1, param2)
        return {
            "status": "success",
            "data": result,
            "count": len(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "data": None
        }

# Use in agent
from tools.my_tool import my_custom_tool

class MyAgent(Agent):
    def __init__(self):
        super().__init__(name="MyAgent", tools=[my_custom_tool], ...)
```

### **3. Add Custom Validator**

```python
# agents/my_validator.py
from agents.quality_loop import QualityValidator

class MyCustomValidator(QualityValidator):
    """Custom validation logic"""
    
    def validate(self, image_path, query, bboxes):
        # Custom validation logic
        issues = []
        
        # Check 1: Custom rule
        if len(bboxes) < 1:
            issues.append("No objects detected")
        
        # Check 2: Another rule
        if self._check_overlap(bboxes):
            issues.append("Overlapping bounding boxes")
        
        if issues:
            return {
                "status": "NEEDS_IMPROVEMENT",
                "feedback": "; ".join(issues),
                "issues": issues
            }
        else:
            return {
                "status": "APPROVED",
                "feedback": "Passed custom validation",
                "issues": []
            }
```

### **4. Add MCP Integration (Future)**

```python
# Connect to external image database via MCP
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

# Create MCP toolset
image_db_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-images"]
        )
    )
)

# Add to miner
class MinerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="MinerAgent",
            tools=[google_search_images, image_db_mcp]  # Multiple sources
        )
```

---

## ⚡ Performance Optimization

### **1. Parallel Processing Tuning**

```python
# Adjust worker count based on system
from agents.parallel_annotator import ParallelAnnotatorAgent

# For CPU-heavy systems
annotator = ParallelAnnotatorAgent(num_workers=8)

# For API rate-limited scenarios
annotator = ParallelAnnotatorAgent(num_workers=2)
```

### **2. Batch Size Optimization**

```python
# Process in smaller batches
def optimized_pipeline(query, total_count):
    agent = MainAgent()
    batch_size = 20
    
    for i in range(0, total_count, batch_size):
        count = min(batch_size, total_count - i)
        agent.run_pipeline(query=query, count=count)
        
        # Process incrementally
        print(f"Processed {i + count}/{total_count}")
```

### **3. Caching**

```python
# Cache search results
class MinerAgent:
    def __init__(self):
        self.search_cache = {}
    
    def mine(self, query, max_images):
        cache_key = f"{query}_{max_images}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        result = self._do_mine(query, max_images)
        self.search_cache[cache_key] = result
        return result
```

### **4. Memory Management**

```python
# Process images one at a time for large batches
import gc

for img_path in image_paths:
    annotation = annotate_image(img_path)
    process_annotation(annotation)
    gc.collect()  # Force garbage collection
```

---

## 🐛 Troubleshooting Guide

### **Problem: API Rate Limit**

```
Error: Rate limit exceeded (429)
```

**Solution:**
```python
# Add retry with exponential backoff
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,  # Exponential backoff: 7^n seconds
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Use in agent
model = Gemini(
    model="gemini-2.0-flash",
    retry_options=retry_config
)
```

### **Problem: Out of Memory**

```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Reduce parallel workers
parallel_annotator = ParallelAnnotatorAgent(num_workers=2)

# Process in smaller batches
# Or increase system memory
```

### **Problem: Slow Performance**

```python
# Diagnose with metrics
phase2 = initialize_phase2_features(enable_metrics=True)
agent.run_pipeline(query="test", count=5)
phase2.print_metrics_summary()

# Check timings:
# - Mining slow? → Check network
# - Curation slow? → Reduce image count
# - Annotation slow? → Reduce quality iterations
```

### **Problem: Poor Annotation Quality**

```python
# Enable quality loop
python pipeline.py --enable-quality-loop --quality-iterations 3

# Or adjust prompts in agents/annotator.py
```

### **Problem: COCO Format Issues**

```python
# Validate COCO output
from pycocotools.coco import COCO

try:
    coco = COCO('data/output/coco.json')
    print("✅ Valid COCO format")
except Exception as e:
    print(f"❌ Invalid COCO: {e}")
```

---

## 📚 Additional Resources

### **External Documentation**
- **COCO Format:** https://cocodataset.org/#format-data
- **Gemini API:** https://ai.google.dev/
- **Google Custom Search:** https://developers.google.com/custom-search
- **PyTorch COCO Utils:** https://github.com/cocodataset/cocoapi

### **Internal Documentation**
- **README.md** - User guide
- **COURSE_IMPLEMENTATION_GUIDE.md** - Feature roadmap
- **PHASE2_SUMMARY.md** - Advanced features
- **phase2_examples.py** - Code examples

---

## 🎓 Best Practices

### **1. Always Use Metrics for Production**
```python
phase2 = initialize_phase2_features(enable_metrics=True)
```

### **2. Enable Quality Loop for Important Datasets**
```python
phase2 = initialize_phase2_features(
    enable_quality_loop=True,
    quality_loop_iterations=2
)
```

### **3. Use Structured Error Handling**
```python
from utils.error_handler import ErrorHandler, create_error_response

try:
    result = agent.run_pipeline(...)
except Exception as e:
    error = ErrorHandler.handle_mining_error(e, ...)
    ErrorHandler.log_error(error)
```

### **4. Monitor Resource Usage**
```python
# Add logging
import psutil

logger.info(f"Memory: {psutil.virtual_memory().percent}%")
logger.info(f"CPU: {psutil.cpu_percent()}%")
```

### **5. Version Your Datasets**
```bash
# Save with timestamps
output_dir = f"data/output/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
agent.engineer.output_folder = output_dir
```

---

## 🔐 Security Considerations

### **API Key Management**
```python
# Never commit .env files
# Use environment variables in production
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("API key not found")
```

### **Input Validation**
```python
# Validate user inputs
def validate_query(query):
    if not query or len(query) > 100:
        raise ValueError("Invalid query")
    return query.strip()

# Validate paths
def validate_path(path):
    if not os.path.exists(path):
        raise ValueError(f"Path not found: {path}")
    return os.path.abspath(path)
```

### **Rate Limiting**
```python
# Implement rate limiting for API calls
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

---

## 📞 Support & Maintenance

### **Logging System**
```python
from utils.logger import setup_logging, get_logger

# Setup
setup_logging(log_level=logging.INFO, log_file="foundry.log")

# Use
logger = get_logger("my_module")
logger.info("Operation completed")
logger.error("Error occurred", exc_info=True)
```

### **Health Check**
```python
def health_check():
    """Verify system is ready."""
    checks = {
        "api_keys": check_api_keys(),
        "disk_space": check_disk_space(),
        "network": check_network(),
        "dependencies": check_dependencies()
    }
    
    return all(checks.values()), checks

def check_api_keys():
    return bool(os.getenv('GEMINI_API_KEY'))

def check_disk_space():
    import shutil
    stats = shutil.disk_usage('/')
    return stats.free > 1_000_000_000  # 1GB

def check_network():
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
```

---

**Document End**

For questions or issues, refer to:
1. README.md for user guide
2. This document for technical details
3. phase2_examples.py for code examples
4. Error logs for debugging

Last Updated: November 23, 2025
