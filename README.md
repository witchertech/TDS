# LLM Code Deployment API Endpoint

A production-ready API endpoint that receives project requests, generates web applications using LLMs, creates GitHub repositories, and submits evaluations automatically.

## 🚀 Features

- **API Endpoint**: Accepts JSON POST requests with project briefs
- **LLM Code Generation**: Generates minimal web applications using OpenAI/Anthropic
- **GitHub Integration**: Automatically creates repositories and pushes code
- **GitHub Pages**: Enables and deploys applications to GitHub Pages
- **Evaluation Submission**: Posts results with exponential backoff retry logic
- **Security**: Secret validation and no secrets in git history
- **Logging**: Comprehensive logging for debugging

## 📋 Requirements

- Python 3.8+
- Git installed and configured
- GitHub account with Personal Access Token
- OpenAI or Anthropic API key
- Secret shared in Google Form

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd llm-code-deployment
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
SHARED_SECRET=your-secret-from-google-form
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_USERNAME=your-github-username
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4
```

#### Getting GitHub Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `delete_repo`, `admin:repo_hook`
4. Copy the token (starts with `ghp_`)

#### Getting OpenAI API Key:

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)

### 4. Create logs directory

```bash
mkdir logs
```

## 🚀 Usage

### Run the server locally

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Test the endpoint

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "task": "captcha-solver-test-123",
    "round": 1,
    "nonce": "ab12-cd34-ef56",
    "secret": "your-secret-from-google-form",
    "brief": "Create a simple calculator web app with basic arithmetic operations",
    "evaluation": {
      "url": "https://evaluation-endpoint.com/submit"
    }
  }'
```

### Health check

```bash
curl http://localhost:5000/health
```

## 📦 Deployment

### Deploy to any cloud platform that supports Python:

**Heroku:**
```bash
heroku create your-app-name
git push heroku main
```

**Railway:**
```bash
railway init
railway up
```

**Render:**
- Connect your GitHub repo
- Set environment variables
- Deploy

**DigitalOcean/AWS/GCP:**
- Use the included `Dockerfile` or deploy as a Python app
- Set environment variables
- Run with gunicorn: `gunicorn app:app`

## 🔧 Code Explanation

### Main Components

#### `app.py`
- Flask web server
- `/api-endpoint` - Main endpoint that accepts POST requests
- `/health` - Health check endpoint
- Validates incoming requests and processes them asynchronously

#### `config.py`
- Configuration management using environment variables
- Validates required settings on startup

#### `github_manager.py`
- Creates GitHub repositories
- Pushes code to GitHub
- Enables GitHub Pages
- Adds MIT LICENSE and comprehensive README

#### `llm_generator.py`
- Generates web application code using LLM APIs
- Supports OpenAI and Anthropic
- Falls back to simple template if API fails

#### `evaluator.py`
- Submits evaluation data to specified URL
- Implements exponential backoff retry (1, 2, 4, 8 seconds)
- Returns success/failure status

### Workflow

1. **Request received** → Validate secret and required fields
2. **Send 200 response** → Immediately acknowledge request
3. **Generate app** → Use LLM to create HTML/CSS/JS code
4. **Create repo** → Initialize GitHub repository
5. **Push code** → Commit and push with LICENSE and README
6. **Enable Pages** → Activate GitHub Pages for the repo
7. **Submit evaluation** → POST results to evaluation URL with retry logic

## 🔒 Security Features

- Secret validation before processing
- Environment variables for sensitive data
- No secrets in git history
- `.gitignore` configured properly
- HTTPS for all external communications

## 📝 License

MIT License - See LICENSE file for details

## 🐛 Troubleshooting

### "Invalid secret" error
- Verify `SHARED_SECRET` in `.env` matches what you submitted in Google Form

### GitHub API errors
- Check `GITHUB_TOKEN` has correct permissions (`repo`, `delete_repo`)
- Verify token is not expired

### LLM API errors
- Check `LLM_API_KEY` is valid
- Verify you have API credits/quota available
- System falls back to simple template if LLM fails

### GitHub Pages not loading
- Wait 2-3 minutes for GitHub Pages to build
- Check repository settings → Pages is enabled
- Verify `index.html` exists in repo root

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [GitHub Pages Guide](https://docs.github.com/en/pages)

## 🤝 Support

For issues or questions:
1. Check the logs in `logs/api.log`
2. Verify all environment variables are set correctly
3. Test individual components separately
4. Review error messages in console output
