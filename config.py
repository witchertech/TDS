"""
Configuration management for the API endpoint
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Server configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))

    # Security
    SHARED_SECRET = os.getenv('SHARED_SECRET', 'your-secret-from-google-form')

    # GitHub configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

    # LLM configuration (using OpenAI as example, can be adapted)
    LLM_API_KEY = os.getenv('LLM_API_KEY')  # OpenAI, Anthropic, etc.
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # openai, anthropic, local

    # Repository settings
    DEFAULT_LICENSE = 'MIT'
    DEFAULT_BRANCH = 'main'

    # Retry settings for evaluation submission
    MAX_RETRIES = 5
    INITIAL_RETRY_DELAY = 1  # seconds

    # Timeout settings
    PROCESSING_TIMEOUT = 600  # 10 minutes

    def validate(self):
        """Validate that all required configuration is present"""
        errors = []

        if not self.SHARED_SECRET or self.SHARED_SECRET == 'your-secret-from-google-form':
            errors.append("SHARED_SECRET not configured")

        if not self.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN not configured")

        if not self.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME not configured")

        if not self.LLM_API_KEY:
            errors.append("LLM_API_KEY not configured")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True
