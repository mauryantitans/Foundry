# Foundry Quick Start Guide

**GitHub Repository:** https://github.com/mauryantitans/Foundry

Get started with Foundry in 5 minutes!

---

## Prerequisites

- Python 3.10 or higher
- Google API keys (Gemini + Custom Search)

---

## 5-Minute Setup

### Step 1: Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/mauryantitans/Foundry.git
cd Foundry

# Create virtual environment
python -m venv venv

# Activate (choose your OS)
venv\Scripts\activate          # Windows
source venv/bin/activate        # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (2 minutes)

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_SEARCH_API_KEY=your_search_key_here
GOOGLE_SEARCH_CX=your_search_engine_id_here
```

**Get API Keys:**
- [Gemini API](https://ai.google.dev/) - Free tier: 15 req/min
- [Custom Search](https://developers.google.com/custom-search/v1/overview) - Free: 100/day
- [Search Engine](https://programmablesearchengine.google.com/) - Create custom engine

### Step 3: Run (1 minute)

```bash
# Your first dataset!
python pipeline.py --query "dog" --count 5
```

**Output:**
```
✅ Images Collected: 5/5
✅ Dataset saved to: data/output/coco.json
📊 Ready for training!
```

---

## First Commands

### Interactive Mode (Recommended)
```bash
python pipeline.py
```
Then type: `"create 5 images of dogs"`

### Command Line Mode
```bash
# Basic
python pipeline.py --query "dog" --count 10

# Multi-object
python pipeline.py --query "person,guitar" --count 5

# With quality loop
python pipeline.py --query "bicycle" --count 8 --enable-quality-loop

# Your own images
python pipeline.py --dir "C:\photos" --query "cat"
```

---

## Output

**COCO Format JSON:**
```
kaggle_capstone/
└── data/
    └── output/
        └── coco.json  ← Your dataset
```

**Visualize:**
```bash
python visualize_results.py
```

---

## Common Issues

### Module Not Found?
```bash
# Make sure venv is activated!
venv\Scripts\activate  # You should see (venv) prefix
```

### Rate Limit Error (429)?
```bash
# Wait 60 seconds, then:
python pipeline.py --query "dog" --count 3
```

**Or optimize for free tier:**
```yaml
# config.yaml
annotation:
  workers: 1  # Important!
```

### No Images Found?
- Check `.env` file has correct API keys
- Verify keys start with "AIza"
- Check [Google Cloud Console](https://console.cloud.google.com/) quotas

---

## Next Steps

### Learn More
- **[README.md](README.md)** - Full documentation
- **[USAGE.md](docs/USAGE.md)** - All options explained
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Real-world examples

### Try Advanced Features
```bash
# Multi-object detection
python pipeline.py --query "person,guitar,microphone" --count 10

# High quality with validation
python pipeline.py --query "bicycle" --count 15 \
  --enable-quality-loop \
  --validation-method visual \
  --show-metrics

# Natural language
python pipeline.py
> "I need 20 images of dogs and cats playing, annotate both"
```

### Configuration
Edit `config.yaml` for your preferences:
```yaml
quality_loop:
  enabled: true
  validation_method: "coordinate"  # Fast & free-tier friendly

annotation:
  workers: 1  # Set to 1 for free tier
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Create dataset** | `python pipeline.py --query "dog" --count 10` |
| **Multi-object** | `python pipeline.py --query "dog,cat" --count 5` |
| **High quality** | Add `--enable-quality-loop` |
| **Your images** | `python pipeline.py --dir "./photos" --query "cat"` |
| **Help** | `python pipeline.py --help` |
| **Visualize** | `python visualize_results.py` |

---

## Tips

✅ **Start small**: Test with `--count 3` first  
✅ **Use specific queries**: "dog" better than "small brown dog"  
✅ **Enable quality loop**: Better annotations  
✅ **Check metrics**: Use `--show-metrics` to track performance  
✅ **Wait between runs**: Free tier rate limits reset every 60s  

---

## Get Help

- **Issues**: [GitHub Issues](https://github.com/mauryantitans/Foundry/issues)
- **Documentation**: [Full Docs](README.md)
- **Examples**: [See EXAMPLES.md](docs/EXAMPLES.md)

---

**Ready to create datasets! 🚀**

[Full Documentation](README.md) | [Troubleshooting](README.md#troubleshooting) | [Examples](docs/EXAMPLES.md)
