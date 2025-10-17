# Deployment Guide

## Overview

This guide covers deploying your LLM Code Deployment API to various platforms.

## Prerequisites

- GitHub account with your code pushed
- Required API keys (OpenAI/Anthropic, GitHub)
- Secret from Google Form

---

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Easiest)

Railway offers free tier and automatic deployments from GitHub.

1. **Sign up at [railway.app](https://railway.app)**

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add environment variables:**
   - Go to Variables tab
   - Add all variables from `.env.example`:
     ```
     SHARED_SECRET=your-secret
     GITHUB_TOKEN=ghp_your_token
     GITHUB_USERNAME=your-username
     LLM_PROVIDER=openai
     LLM_API_KEY=sk-your-key
     LLM_MODEL=gpt-4
     PORT=5000
     ```

4. **Deploy:**
   - Railway auto-deploys on git push
   - Get your public URL from settings

5. **Test:**
   ```bash
   curl https://your-app.railway.app/health
   ```

---

### Option 2: Render

Free tier with automatic HTTPS.

1. **Sign up at [render.com](https://render.com)**

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Name: `llm-code-deployment`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Environment Variables:**
   - Add all from `.env.example`

4. **Deploy** - Render builds and deploys automatically

---

### Option 3: Heroku

Classic PaaS with great Python support.

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku

   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Add Procfile:**
   ```bash
   echo "web: gunicorn app:app" > Procfile
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SHARED_SECRET=your-secret
   heroku config:set GITHUB_TOKEN=ghp_your_token
   heroku config:set GITHUB_USERNAME=your-username
   heroku config:set LLM_PROVIDER=openai
   heroku config:set LLM_API_KEY=sk-your-key
   heroku config:set LLM_MODEL=gpt-4
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Open:**
   ```bash
   heroku open
   ```

---

### Option 4: DigitalOcean App Platform

1. **Sign up at [digitalocean.com](https://www.digitalocean.com)**

2. **Create App:**
   - Apps → Create App
   - Connect GitHub repo
   - Choose branch

3. **Configure:**
   - Detected as Python app automatically
   - Add environment variables
   - Choose plan (free available)

4. **Deploy** - Automatic

---

### Option 5: VPS (Ubuntu Server)

For more control, deploy on your own VPS.

1. **SSH into your server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git nginx
   ```

3. **Clone repository:**
   ```bash
   git clone <your-repo-url>
   cd llm-code-deployment
   ```

4. **Setup Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create .env file:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

6. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/llm-api.service
   ```

   Add:
   ```ini
   [Unit]
   Description=LLM Code Deployment API
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/llm-code-deployment
   Environment="PATH=/path/to/llm-code-deployment/venv/bin"
   ExecStart=/path/to/llm-code-deployment/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 600 app:app

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service:**
   ```bash
   sudo systemctl start llm-api
   sudo systemctl enable llm-api
   sudo systemctl status llm-api
   ```

8. **Configure Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/llm-api
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

9. **Enable and restart Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/llm-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 🔒 Security Checklist

Before deploying:

- [ ] All secrets in environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] GitHub token has minimal required permissions
- [ ] HTTPS enabled (most platforms do this automatically)
- [ ] Logs don't contain sensitive information
- [ ] Rate limiting configured (if needed)

---

## 🧪 Testing Your Deployment

After deployment, test with:

```bash
# Health check
curl https://your-app-url.com/health

# Full test
curl https://your-app-url.com/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "task": "test-app-123",
    "round": 1,
    "nonce": "abc-123",
    "secret": "your-secret",
    "brief": "Create a simple calculator",
    "evaluation": {
      "url": "https://httpbin.org/post"
    }
  }'
```

---

## 📊 Monitoring

### View Logs

**Railway:**
- Go to project → Deployments → View Logs

**Render:**
- Go to service → Logs tab

**Heroku:**
```bash
heroku logs --tail
```

**VPS:**
```bash
sudo journalctl -u llm-api -f
```

### Check Application Logs

All platforms will show output from `logs/api.log`

---

## 🐛 Troubleshooting

### "Application Error" or 500 errors
- Check environment variables are set correctly
- View application logs
- Verify all dependencies installed

### GitHub API rate limit
- Use a Personal Access Token (not password)
- Token should have repo permissions

### LLM API errors
- Check API key is valid
- Verify you have credits/quota
- Application falls back to simple template if LLM fails

### Timeout errors
- Increase worker timeout (for gunicorn: `--timeout 600`)
- Check if GitHub Pages enablement is slow

---

## 💰 Cost Considerations

**Free Tiers:**
- Railway: 500 hours/month free
- Render: Free for web services (with limitations)
- Heroku: Free dyno (sleeps after 30 min inactivity)

**API Costs:**
- OpenAI GPT-4: ~$0.03-0.06 per app generation
- Anthropic Claude: ~$0.015-0.03 per app generation
- GitHub API: Free for reasonable usage

---

## 🚀 Production Best Practices

1. **Use gunicorn with multiple workers:**
   ```bash
   gunicorn --workers 4 --timeout 600 app:app
   ```

2. **Enable automatic restarts:**
   - Most platforms do this by default
   - For VPS, use systemd (shown above)

3. **Set up monitoring:**
   - Use platform-provided monitoring
   - Or add external: Sentry, DataDog, etc.

4. **Regular backups:**
   - Keep code in GitHub
   - No local state to backup (repos are on GitHub)

5. **Update dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

---

## 📞 Support

If deployment fails:
1. Check logs first
2. Verify environment variables
3. Test locally with same configuration
4. Check platform-specific documentation

---

**Recommended for students:** Railway or Render (easiest setup, free tier)
