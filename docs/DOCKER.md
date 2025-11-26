# Docker Deployment Guide

Complete guide for running Foundry in Docker.

**GitHub Repository:** https://github.com/mauryantitans/Foundry

---

## 📋 Overview

This guide covers:
- Building Docker images
- Running containers
- Using docker-compose
- Environment configuration
- Data persistence
- Troubleshooting

---

## 🐳 Quick Start with Docker

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- API keys ready

---

## 🚀 Method 1: Docker Compose (Recommended)

### Step 1: Setup

```bash
# Clone repository
git clone https://github.com/mauryantitans/Foundry.git
cd Foundry

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_SEARCH_API_KEY=your_search_key_here
GOOGLE_SEARCH_CX=your_cx_here
EOF
```

### Step 2: Build

```bash
docker-compose build
```

### Step 3: Run

```bash
# Show help
docker-compose run foundry --help

# Create a dataset
docker-compose run foundry --query "dog" --count 5

# Multi-object
docker-compose run foundry --query "person,guitar" --count 10

# With quality loop
docker-compose run foundry --query "bicycle" --count 8 --enable-quality-loop

# Using config file
docker-compose run foundry --config config.yaml
```

### Step 4: Access Output

```bash
# Output is in ./data/output/
ls -l data/output/coco.json

# Visualize (run locally since it needs display)
python visualize_results.py
```

---

## 🏗️ Method 2: Docker CLI

### Build Image

```bash
docker build -t foundry:latest .
```

### Run Container

**Basic usage:**
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  foundry:latest --query "dog" --count 5
```

**With config file:**
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  foundry:latest --config config.yaml
```

**Interactive mode:**
```bash
docker run -it --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  foundry:latest
```

**BYOD mode:**
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/my_images:/app/my_images:ro \
  foundry:latest --dir /app/my_images --query "cat"
```

---

## 🔧 Dockerfile Improvements

### What's Included

✅ **Python 3.11** - Latest stable (upgraded from 3.10)  
✅ **System dependencies** - Image processing libraries for Pillow  
✅ **Non-root user** - Security best practice  
✅ **Data directories** - Pre-created for persistence  
✅ **Health check** - Verifies Python modules load  
✅ **Optimized caching** - requirements.txt copied first  

### Key Features

**1. Image Processing Libraries:**
```dockerfile
libjpeg-dev libpng-dev libtiff-dev  # Image formats
libfreetype6-dev liblcms2-dev       # Font/color management
libwebp-dev libharfbuzz-dev         # WebP support
```

**2. Security:**
```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

**3. Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import google.generativeai; import PIL; print('OK')"
```

---

## 📦 Data Persistence

### Volume Mounts

Docker containers are ephemeral - mount volumes to persist data:

**Automatic (docker-compose):**
```yaml
volumes:
  - ./data:/app/data           # All data
  - ./config.yaml:/app/config.yaml:ro  # Config (read-only)
```

**Manual (docker CLI):**
```bash
-v $(pwd)/data:/app/data                    # Data directory
-v $(pwd)/config.yaml:/app/config.yaml:ro  # Config file
-v $(pwd)/my_images:/app/my_images:ro      # BYOD images
```

### Directory Structure

```
Host Machine          Container
./data           →    /app/data
  ├── raw        →      /app/data/raw        (downloaded images)
  ├── curated    →      /app/data/curated    (filtered images)
  └── output     →      /app/data/output     (COCO datasets)
```

**After running:**
```bash
ls data/output/
# coco.json  ← Your dataset!
```

---

## 🔐 Environment Variables

### Required Variables

Create `.env` file in project root:

```env
# Required
GEMINI_API_KEY=AIza...
GOOGLE_SEARCH_API_KEY=AIza...
GOOGLE_SEARCH_CX=abc123...

# Optional
FOUNDRY_LOG_LEVEL=INFO
FOUNDRY_OUTPUT_DIR=/app/data/output
```

### Passing to Container

**docker-compose:**
```yaml
env_file:
  - .env
```

**docker CLI:**
```bash
docker run --env-file .env foundry:latest
```

**Individual vars:**
```bash
docker run \
  -e GEMINI_API_KEY=your_key \
  -e GOOGLE_SEARCH_API_KEY=your_key \
  -e GOOGLE_SEARCH_CX=your_cx \
  foundry:latest --query "dog" --count 5
```

---

## 🎯 Common Usage Patterns

### Pattern 1: One-Off Dataset Creation

```bash
# Build once
docker-compose build

# Create dataset
docker-compose run --rm foundry --query "dog" --count 10

# Access output
cat data/output/coco.json
```

---

### Pattern 2: Batch Processing

**create_datasets.sh:**
```bash
#!/bin/bash

queries=("dog" "cat" "bird" "fish")

for query in "${queries[@]}"; do
    echo "Creating dataset for: $query"
    
    docker-compose run --rm foundry \
        --query "$query" \
        --count 20 \
        --enable-quality-loop
    
    # Rename output for each query
    mv data/output/coco.json data/output/coco_${query}.json
    
    # Wait for rate limit
    echo "Waiting 60s for rate limit..."
    sleep 60
done

echo "All datasets created!"
```

```bash
chmod +x create_datasets.sh
./create_datasets.sh
```

---

### Pattern 3: BYOD in Docker

```bash
# Place your images in ./my_images/
docker-compose run --rm \
    -v $(pwd)/my_images:/app/input_images:ro \
    foundry --dir /app/input_images --query "elephant"
```

---

### Pattern 4: Custom Config

```bash
# Create custom config
cat > custom_config.yaml << EOF
pipeline:
  query: "bicycle"
  count: 15

quality_loop:
  enabled: true
  validation_method: "visual"

annotation:
  workers: 1
EOF

# Run with custom config
docker-compose run --rm \
    -v $(pwd)/custom_config.yaml:/app/config.yaml:ro \
    foundry --config config.yaml
```

---

## 🐛 Troubleshooting

### Build Failures

**Error:** `failed to solve: process "/bin/sh -c pip install..."`

**Solutions:**
1. **Clear Docker cache:**
```bash
docker-compose build --no-cache
```

2. **Check internet connection** (downloads dependencies)

3. **Increase Docker memory:**
   - Docker Desktop → Settings → Resources → Memory (4GB recommended)

---

### Permission Errors

**Error:** `PermissionError: [Errno 13] Permission denied: '/app/data/output'`

**Solutions:**
1. **Fix directory permissions:**
```bash
chmod -R 777 data/
```

2. **Run as current user:**
```bash
docker-compose run --rm --user $(id -u):$(id -g) foundry --query "dog" --count 5
```

---

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'google.generativeai'`

**Solutions:**
1. **Rebuild image:**
```bash
docker-compose build --no-cache
```

2. **Check requirements.txt** is valid

3. **Verify Python version:**
```bash
docker run foundry:latest python --version
# Should show Python 3.11.x
```

---

### API Key Issues

**Error:** `ValueError: GEMINI_API_KEY not found`

**Solutions:**
1. **Check .env file exists:**
```bash
ls -la .env
cat .env  # Verify keys are present
```

2. **Verify docker-compose mounts:**
```yaml
env_file:
  - .env  # Must be present
```

3. **Test with explicit env vars:**
```bash
docker run --rm \
  -e GEMINI_API_KEY=your_key \
  -e GOOGLE_SEARCH_API_KEY=your_key \
  -e GOOGLE_SEARCH_CX=your_cx \
  -v $(pwd)/data:/app/data \
  foundry:latest --query "dog" --count 3
```

---

### Rate Limit in Docker

**Error:** `429 Resource exhausted`

**Same solutions as local:**
1. Wait 60 seconds between runs
2. Use `workers: 1` in config
3. Use `coordinate` validation

**Docker-specific tip:**
```bash
# Add sleep between runs in scripts
docker-compose run --rm foundry --query "dog" --count 5
sleep 60
docker-compose run --rm foundry --query "cat" --count 5
```

---

## 🚀 Advanced Docker Usage

### Multi-Stage Builds (Optimization)

For smaller images, create a multi-stage build:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libpng16-16 libtiff5 \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Setup
RUN mkdir -p data/raw data/curated data/output
ENTRYPOINT ["python", "pipeline.py"]
CMD ["--help"]
```

---

### Running as a Service

**docker-compose.yml** (daemon mode):
```yaml
version: '3.8'

services:
  foundry-api:
    build: .
    container_name: foundry-service
    env_file: .env
    volumes:
      - ./data:/app/data
    ports:
      - "8080:8080"
    restart: always
    command: ["--serve"]  # Future: API server mode
```

---

### Cloud Deployment

**Google Cloud Run:**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/foundry

# Deploy
gcloud run deploy foundry \
  --image gcr.io/PROJECT_ID/foundry \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your_key \
  --set-env-vars GOOGLE_SEARCH_API_KEY=your_key \
  --set-env-vars GOOGLE_SEARCH_CX=your_cx \
  --memory 2Gi \
  --timeout 900
```

**AWS ECS/Fargate:**
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin ECR_URL
docker build -t foundry:latest .
docker tag foundry:latest ECR_URL/foundry:latest
docker push ECR_URL/foundry:latest

# Deploy via ECS task definition
# (See AWS ECS documentation)
```

---

## 📊 Docker Image Details

### Image Size

**Current:**
- Base image: python:3.11-slim (~120MB)
- Dependencies: ~500MB
- Application: ~10MB
- **Total**: ~630MB

**Optimization tips:**
- Use multi-stage builds (reduces to ~400MB)
- Use Alpine Linux (reduces to ~200MB, but complex setup)

### Build Time

**First build:**
- ~5-10 minutes (downloads & installs dependencies)

**Subsequent builds:**
- ~1-2 minutes (uses cached layers)

---

## 🔍 Inspecting the Container

### View Logs

```bash
# During run
docker-compose run foundry --query "dog" --count 5

# From stopped container
docker logs foundry-pipeline
```

### Enter Container (Debug)

```bash
# Start container with shell
docker-compose run --rm --entrypoint /bin/bash foundry

# Inside container:
ls -la /app
python --version
pip list
env | grep GEMINI
```

### Check Image Contents

```bash
# List files in image
docker run --rm foundry:latest ls -la /app

# Check Python packages
docker run --rm foundry:latest pip list

# Verify health
docker inspect --format='{{.State.Health.Status}}' foundry-pipeline
```

---

## 🎯 Best Practices

### 1. Use .dockerignore

**Current .dockerignore includes:**
- venv/, __pycache__, *.pyc
- data/ (created fresh in container)
- .git/, .vscode/
- Test files
- Logs

**Benefits:**
- Faster builds
- Smaller context
- Security (no sensitive files)

### 2. Environment Variables

**Never hardcode in Dockerfile!**
```dockerfile
# ❌ BAD
ENV GEMINI_API_KEY=AIza...

# ✅ GOOD
# (Use .env file or runtime -e flag)
```

### 3. Volume Mounts

**Always mount data directory:**
```bash
-v $(pwd)/data:/app/data  # Persist outputs
```

### 4. Non-Root User

**Already implemented:**
```dockerfile
USER appuser  # Security best practice
```

### 5. Resource Limits

**In docker-compose.yml:**
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## 📝 Example Workflows

### Workflow 1: Daily Dataset Creation

**Cron job:**
```bash
# crontab -e
0 2 * * * cd /path/to/Foundry && docker-compose run --rm foundry --query "dog" --count 10
```

### Workflow 2: CI/CD Integration

**GitHub Actions:**
```yaml
name: Create Dataset

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  create-dataset:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create .env
        run: |
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" > .env
          echo "GOOGLE_SEARCH_API_KEY=${{ secrets.GOOGLE_SEARCH_API_KEY }}" >> .env
          echo "GOOGLE_SEARCH_CX=${{ secrets.GOOGLE_SEARCH_CX }}" >> .env
      
      - name: Build Docker image
        run: docker-compose build
      
      - name: Run pipeline
        run: docker-compose run --rm foundry --query "dog" --count 10
      
      - name: Upload dataset
        uses: actions/upload-artifact@v3
        with:
          name: coco-dataset
          path: data/output/coco.json
```

---

## 🧪 Testing Docker Setup

### Test 1: Verify Build

```bash
docker build -t foundry:latest .
echo $?  # Should be 0
```

### Test 2: Verify Dependencies

```bash
docker run --rm foundry:latest python -c "
import google.generativeai
import PIL
import imagehash
print('✅ All dependencies OK')
"
```

### Test 3: Verify Entrypoint

```bash
docker run --rm foundry:latest --help
# Should show Foundry help message
```

### Test 4: Quick Pipeline Test

```bash
# Set up .env first
docker-compose run --rm foundry --query "dog" --count 1
# Should create 1 image dataset
```

---

## 🔒 Security Considerations

### 1. API Keys

✅ **DO:**
- Use .env file (excluded from Git)
- Use secrets management in production
- Rotate keys regularly

❌ **DON'T:**
- Hardcode in Dockerfile
- Commit to Git
- Share in logs

### 2. Non-Root User

✅ **Implemented:**
```dockerfile
USER appuser  # UID 1000
```

### 3. Image Scanning

```bash
# Scan for vulnerabilities
docker scan foundry:latest

# Use Trivy
trivy image foundry:latest
```

---

## 🌐 Production Deployment

### Google Cloud Run

**Deploy:**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/foundry

# Deploy with secrets
gcloud run deploy foundry \
  --image gcr.io/PROJECT_ID/foundry \
  --platform managed \
  --region us-central1 \
  --update-secrets=GEMINI_API_KEY=gemini-key:latest \
  --update-secrets=GOOGLE_SEARCH_API_KEY=search-key:latest \
  --update-secrets=GOOGLE_SEARCH_CX=search-cx:latest \
  --memory 2Gi \
  --timeout 900 \
  --max-instances 10
```

### AWS ECS

**Task Definition (JSON):**
```json
{
  "family": "foundry",
  "containerDefinitions": [{
    "name": "foundry",
    "image": "ECR_URL/foundry:latest",
    "memory": 2048,
    "cpu": 1024,
    "essential": true,
    "environment": [],
    "secrets": [
      {"name": "GEMINI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
      {"name": "GOOGLE_SEARCH_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
      {"name": "GOOGLE_SEARCH_CX", "valueFrom": "arn:aws:secretsmanager:..."}
    ]
  }]
}
```

### Kubernetes

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundry
spec:
  replicas: 1
  selector:
    matchLabels:
      app: foundry
  template:
    metadata:
      labels:
        app: foundry
    spec:
      containers:
      - name: foundry
        image: foundry:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: foundry-secrets
              key: gemini-api-key
        - name: GOOGLE_SEARCH_API_KEY
          valueFrom:
            secretKeyRef:
              name: foundry-secrets
              key: search-api-key
        - name: GOOGLE_SEARCH_CX
          valueFrom:
            secretKeyRef:
              name: foundry-secrets
              key: search-cx
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: foundry-data
```

---

## 📚 Additional Resources

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Multi-stage Builds**: https://docs.docker.com/build/building/multi-stage/
- **Foundry GitHub**: https://github.com/mauryantitans/Foundry

---

## ✅ Checklist for Production

- [ ] Build image successfully
- [ ] Test with small dataset (count=3)
- [ ] Verify .env file excluded from Git
- [ ] Set up secrets management
- [ ] Configure resource limits
- [ ] Test volume persistence
- [ ] Set up monitoring/logging
- [ ] Configure health checks
- [ ] Document deployment process
- [ ] Test disaster recovery

---

**Docker deployment is ready! 🐳**

[Back to Main README](../README.md) | [Usage Guide](USAGE.md) | [Examples](EXAMPLES.md)
