#!/usr/bin/env python3
"""
LLM Code Deployment API Endpoint
Accepts POST requests, generates apps using LLM, creates GitHub repos, and submits evaluations
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import threading

from config import Config
from github_manager import GitHubManager
from llm_generator import LLMGenerator
from evaluator import Evaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = Config()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route('/api-endpoint', methods=['POST'])
def api_endpoint():
    """
    Main API endpoint that handles incoming requests
    Expected JSON format:
    {
        "email": "student@example.com",
        "task": "captcha-solver-xyz",
        "round": 1,
        "nonce": "ab12-cd34",
        "secret": "shared_secret",
        "brief": "Create a simple captcha solver...",
        "evaluation": {
            "url": "https://evaluation-endpoint.com/submit"
        }
    }
    """
    try:
        # Parse incoming JSON
        data = request.get_json()

        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data provided"}), 400

        # Log the request (without sensitive data)
        logger.info(f"Received request for task: {data.get('task', 'unknown')}")

        # Validate required fields
        required_fields = ['email', 'task', 'round', 'nonce', 'secret', 'brief']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400

        # Check secret
        if data['secret'] != config.SHARED_SECRET:
            logger.warning(f"Invalid secret for task: {data['task']}")
            return jsonify({"error": "Invalid secret"}), 403

        # Send immediate 200 response
        response_data = {
            "status": "accepted",
            "message": "Request received and processing started",
            "task": data['task'],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Process the request asynchronously
        thread = threading.Thread(
            target=process_request_async,
            args=(data,)
        )
        thread.start()

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

def process_request_async(data):
    """
    Process the request asynchronously:
    1. Generate app using LLM
    2. Create GitHub repo
    3. Push code
    4. Enable GitHub Pages
    5. Submit evaluation
    """
    try:
        logger.info(f"Starting async processing for task: {data['task']}")

        # Initialize managers
        llm_gen = LLMGenerator(config)
        github_mgr = GitHubManager(config)
        evaluator = Evaluator(config)

        # 1. Generate app code using LLM
        logger.info("Generating app code using LLM...")
        app_code = llm_gen.generate_app(data['brief'], data['task'])

        # 2. Create unique repo name based on task
        repo_name = f"{data['task']}"
        logger.info(f"Creating GitHub repo: {repo_name}")

        # 3. Create repo and push code
        repo_url, commit_sha, pages_url = github_mgr.create_and_push_repo(
            repo_name=repo_name,
            app_code=app_code,
            task_brief=data['brief']
        )

        logger.info(f"Repo created: {repo_url}")
        logger.info(f"Commit SHA: {commit_sha}")
        logger.info(f"Pages URL: {pages_url}")

        # 4. Prepare evaluation data
        eval_data = {
            "email": data['email'],
            "task": data['task'],
            "round": data['round'],
            "nonce": data['nonce'],
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }

        # 5. Submit evaluation with retry logic
        evaluation_url = data.get('evaluation', {}).get('url')
        if evaluation_url:
            logger.info(f"Submitting evaluation to: {evaluation_url}")
            success = evaluator.submit_evaluation(evaluation_url, eval_data)

            if success:
                logger.info(f"Evaluation submitted successfully for task: {data['task']}")
            else:
                logger.error(f"Failed to submit evaluation for task: {data['task']}")
        else:
            logger.warning("No evaluation URL provided")

    except Exception as e:
        logger.error(f"Error in async processing: {str(e)}", exc_info=True)

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
