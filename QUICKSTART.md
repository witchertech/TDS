# Quick Start Guide

## Fastest way to get running:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Test it:**
   ```bash
   curl http://localhost:5000/health
   ```

## Minimal .env configuration:

```env
SHARED_SECRET=your-secret-here
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your-username
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
```

## Test request:

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "task": "test-app-123",
    "round": 1,
    "nonce": "abc-123",
    "secret": "your-secret-here",
    "brief": "Create a simple todo list app",
    "evaluation": {
      "url": "https://httpbin.org/post"
    }
  }'
```

This will:
1. Validate your secret
2. Generate a todo list app
3. Create a GitHub repo
4. Enable GitHub Pages
5. Submit evaluation

Check logs/api.log for details!
