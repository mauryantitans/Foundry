# Google Search API Setup

## Required Credentials

The MinerAgent uses Google Custom Search API to find images. You need:

1. **Google Search API Key** (`GOOGLE_SEARCH_API_KEY`)
2. **Custom Search Engine ID** (`GOOGLE_SEARCH_CX`)

## Setup Instructions

### 1. Get API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Custom Search API"
4. Go to Credentials → Create Credentials → API Key
5. Copy the API key

### 2. Create Custom Search Engine
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" to create new search engine
3. Under "Sites to search", add: `www.google.com`
4. Enable "Search the entire web"
5. Enable "Image search"
6. Copy the Search Engine ID (cx)

### 3. Add to .env File

```bash
# Add these to your .env file
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_CX=your_search_engine_id_here
```

## Verify Setup

Run this to check if credentials are configured:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else '❌ MISSING'); print('✅ GOOGLE_SEARCH_API_KEY:', 'SET' if os.getenv('GOOGLE_SEARCH_API_KEY') else '❌ MISSING'); print('✅ GOOGLE_SEARCH_CX:', 'SET' if os.getenv('GOOGLE_SEARCH_CX') else '❌ MISSING')"
```

## Test Search

```python
from tools.search_tool import google_search_images

result = google_search_images("dog", num_images=2)
print(f"Status: {result['status']}")
print(f"Found: {result['count']} images")
if result['data']:
    print(f"First URL: {result['data'][0]}")
```

## Troubleshooting

### "API key not found"
- Check .env file exists in project root
- Verify keys are set correctly (no quotes, no spaces)
- Restart terminal/IDE after adding keys

### "Search API error"
- Verify API is enabled in Google Cloud Console
- Check API key has Custom Search API access
- Verify Search Engine ID is correct
- Check API quota (100 free searches/day)

### "No images found"
- Try broader search terms
- Check Custom Search Engine settings
- Verify "Image search" is enabled
- Try different queries

## Alternative: Mock Mode (for testing)

If you don't want to set up Google API, you can test with mock data:

```python
# In tools/search_tool.py, add this at the top of google_search_images():
# return {"status": "success", "data": ["https://example.com/dog1.jpg", "https://example.com/dog2.jpg"], "count": 2, "next_index": 3}
```

This returns fake URLs for testing the pipeline flow.
