# Environment Configuration Guide

## Quick Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```
   
   Or on Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit the `.env` file** and add your API keys

## Required API Keys

### 1. Groq API Key (REQUIRED)

**Why:** Used to generate detailed clinical procedures using Llama models (faster and cheaper than OpenAI).

**How to get it:**
1. Go to https://console.groq.com/
2. Sign up or log in (free account available)
3. Navigate to API Keys: https://console.groq.com/keys
4. Click "Create API Key"
5. Copy the key (it starts with `gsk_`)
6. Paste it in `.env`:
   ```
   GROQ_API_KEY=gsk-your-actual-key-here
   ```

**Note:** Groq offers free tier with generous rate limits. No credit card required for basic usage.

## Optional API Keys

### 2. SerpAPI Key (OPTIONAL but Recommended)

**Why:** Enhances search results with Google Search data for more comprehensive procedure information.

**How to get it:**
1. Go to https://serpapi.com/
2. Sign up for a free account (100 searches/month free)
3. Go to https://serpapi.com/dashboard
4. Copy your API key
5. Paste it in `.env`:
   ```
   SERPAPI_API_KEY=your_serpapi_key_here
   ```

**Note:** Without this, the system will still work but will only use OpenAI for procedure generation.

### 3. LangSmith API Key (OPTIONAL)

**Why:** Provides advanced observability, tracing, and debugging for agent operations.

**How to get it:**
1. Go to https://smith.langchain.com/
2. Sign up for a free account
3. Go to Settings → API Keys
4. Create a new API key
5. Paste it in `.env`:
   ```
   LANGCHAIN_API_KEY=your_langsmith_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=NurseSOP-Live
   ```

**Note:** This is completely optional. The system works fine without it.

## Example .env File

Here's a minimal working `.env` file:

```env
# Required
OPENAI_API_KEY=sk-proj-abc123xyz789...

# Optional but recommended
SERPAPI_API_KEY=abc123def456...

# Optional
LANGCHAIN_API_KEY=lsv2_pt_abc123...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=NurseSOP-Live

# Application settings (defaults work fine)
LOG_LEVEL=INFO
```

## Verification

After setting up your `.env` file, you can verify it's working by:

1. Starting the server:
   ```bash
   python run.py
   ```

2. Making a test request:
   ```bash
   curl -X POST http://localhost:8000/api/v1/procedures \
     -H "Content-Type: application/json" \
     -d '{"user_text": "wound dressing", "setting": "Hospital"}'
   ```

3. Check the logs - if you see errors about missing API keys, double-check your `.env` file.

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to version control
- The `.gitignore` file already excludes `.env` files
- Keep your API keys secret
- If you accidentally commit a key, rotate it immediately in the provider's dashboard

## Troubleshooting

**Issue:** "OpenAI API key not configured"
- Make sure your `.env` file is in the project root directory
- Check that the key starts with `sk-` for OpenAI
- Verify there are no extra spaces or quotes around the key

**Issue:** "Search API not configured" (warning)
- This is normal if you don't have SerpAPI key
- The system will still work using only OpenAI

**Issue:** Environment variables not loading
- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Restart your server after changing `.env` file

