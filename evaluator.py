"""
Evaluation submission with retry logic
"""

import logging
import requests
import time

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self, config):
        self.config = config

    def submit_evaluation(self, evaluation_url, eval_data):
        """
        Submit evaluation with exponential backoff retry

        Args:
            evaluation_url: URL to POST evaluation data
            eval_data: Dictionary containing evaluation data

        Returns:
            bool: True if successful, False otherwise
        """
        max_retries = self.config.MAX_RETRIES
        delay = self.config.INITIAL_RETRY_DELAY

        for attempt in range(max_retries):
            try:
                logger.info(f"Submitting evaluation (attempt {attempt + 1}/{max_retries})")

                response = requests.post(
                    evaluation_url,
                    json=eval_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )

                if response.status_code == 200:
                    logger.info("Evaluation submitted successfully!")
                    return True
                else:
                    logger.warning(f"Evaluation submission failed: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")

            # If not the last attempt, wait and retry
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff: 1, 2, 4, 8, ...

        logger.error("Failed to submit evaluation after all retries")
        return False
