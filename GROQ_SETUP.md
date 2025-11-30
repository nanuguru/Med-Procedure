# Groq API Setup Guide

## Why Groq?

Groq provides:
- **Faster inference** - Up to 10x faster than OpenAI
- **Free tier** - Generous free usage limits
- **No credit card required** - For basic usage
- **Llama models** - High-quality open-source models

## Setup Steps

### 1. Get Your Groq API Key

1. Go to https://console.groq.com/
2. Sign up for a free account (no credit card needed)
3. Navigate to API Keys: https://console.groq.com/keys
4. Click "Create API Key"
5. Copy your API key (starts with `gsk_`)

### 2. Add to .env File

Add this line to your `.env` file:

```env
GROQ_API_KEY=gsk-your-actual-key-here
```

### 3. Available Models

The system uses `llama-3.1-70b-versatile` by default. You can also use:
- `llama-3.1-8b-instant` - Faster, smaller model
- `llama-3.1-70b-versatile` - Better quality (default)
- `mixtral-8x7b-32768` - Alternative high-quality model

To change the model, edit `tools/search_tools.py` and modify the `model` variable in `GroqSearchTool.__init__()`.

### 4. Test Your Setup

Run the test script:

```bash
python test_procedure.py
```

Or make a request to the API - it should work with Groq now!

## Benefits Over OpenAI

- ✅ **Free tier available** - No billing required initially
- ✅ **Faster responses** - Groq's inference is much faster
- ✅ **Lower costs** - More affordable than OpenAI
- ✅ **No quota issues** - Generous free limits

## Troubleshooting

**Error: "Groq API key not configured"**
- Make sure you've added `GROQ_API_KEY` to your `.env` file
- Restart your server after adding the key

**Error: "Rate limit exceeded"**
- Groq has rate limits on free tier
- Wait a few minutes and try again
- Consider upgrading to paid tier for higher limits

**Error: "Model not found"**
- The model name might have changed
- Check available models at https://console.groq.com/docs/models
- Update the model name in `tools/search_tools.py`

