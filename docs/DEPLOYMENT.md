# Deployment Guide

This guide explains how to deploy Foundry using Docker and Google Cloud Run.

## Prerequisites

- Docker installed
- Google Cloud SDK (`gcloud`) installed
- A Google Cloud Project with billing enabled

## 1. Local Deployment with Docker

### Build the Image

```bash
docker build -t foundry-agent .
```

### Run the Container

You need to pass your environment variables to the container.

```bash
# Create a .env file if you haven't already
# Run with env file
docker run --env-file .env -v $(pwd)/data:/app/data foundry-agent --query "dog" --count 5
```

**Note:** We mount the `data/` directory so you can access the downloaded images and JSON output on your host machine.

## 2. Deploying to Google Cloud Run

Cloud Run allows you to run stateless containers that are invocable via web requests or events. Since Foundry is currently a CLI tool, we can deploy it as a **Job** (for batch processing) or wrap it in a simple web server (for on-demand requests).

### Option A: Cloud Run Job (Batch Processing)

Ideal for running a large dataset creation task.

1.  **Push Image to Artifact Registry**

    ```bash
    # Configure auth
    gcloud auth configure-docker region-docker.pkg.dev

    # Tag and push
    docker tag foundry-agent region-docker.pkg.dev/PROJECT_ID/REPO_NAME/foundry-agent:latest
    docker push region-docker.pkg.dev/PROJECT_ID/REPO_NAME/foundry-agent:latest
    ```

2.  **Create Job**

    ```bash
    gcloud run jobs create foundry-job \
      --image region-docker.pkg.dev/PROJECT_ID/REPO_NAME/foundry-agent:latest \
      --set-env-vars GEMINI_API_KEY=your_key,GOOGLE_SEARCH_API_KEY=your_key,GOOGLE_SEARCH_CX=your_cx \
      --args="--query","cat","--count","100"
    ```

3.  **Execute Job**

    ```bash
    gcloud run jobs execute foundry-job
    ```

### Option B: Cloud Run Service (Web API)

To serve this as an API, you would need to add a simple Flask/FastAPI wrapper in `pipeline.py`.

1.  **Add `main.py` (Example)**

    ```python
    from flask import Flask, request
    from pipeline import FoundryPipeline

    app = Flask(__name__)

    @app.route("/", methods=["POST"])
    def run_pipeline():
        data = request.json
        pipeline = FoundryPipeline(query=data["query"], target_count=data["count"])
        result = pipeline.run()
        return result

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8080)
    ```

2.  **Deploy**

    ```bash
    gcloud run deploy foundry-service \
      --source . \
      --set-env-vars GEMINI_API_KEY=your_key...
    ```

## 3. Environment Variables

Ensure these are set in your deployment environment:

- `GEMINI_API_KEY`
- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_SEARCH_CX`
