"""
LLM-based application code generation
"""

import logging
import openai
import anthropic
import json

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self, config):
        self.config = config
        self.provider = config.LLM_PROVIDER

        if self.provider == 'openai':
            openai.api_key = config.LLM_API_KEY
        elif self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=config.LLM_API_KEY)

    def generate_app(self, brief, task_name):
        """Generate application code based on brief"""
        logger.info(f"Generating app for: {task_name}")

        prompt = self._create_prompt(brief, task_name)

        if self.provider == 'openai':
            return self._generate_with_openai(prompt)
        elif self.provider == 'anthropic':
            return self._generate_with_anthropic(prompt)
        else:
            return self._generate_simple_app(brief, task_name)

    def _create_prompt(self, brief, task_name):
        return f"""Generate a complete, minimal web application based on this brief:

{brief}

Requirements:
1. Create a single-page application using HTML, CSS, and JavaScript
2. Make it functional and visually appealing
3. Use only vanilla JavaScript (no frameworks)
4. Include all code inline (no external dependencies)
5. Make it responsive and mobile-friendly
6. Keep it simple but professional

Return ONLY a JSON object with this structure:
{{
    "index.html": "<complete HTML code with inline CSS and JS>"
}}

Important: The HTML must be complete and self-contained. Include all styles in a <style> tag and all JavaScript in a <script> tag.
"""

    def _generate_with_openai(self, prompt):
        try:
            response = openai.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert web developer. Generate clean, professional code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content
            return self._parse_llm_response(content)

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_simple_app(prompt, "fallback")

    def _generate_with_anthropic(self, prompt):
        try:
            response = self.client.messages.create(
                model=self.config.LLM_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            return self._parse_llm_response(content)

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return self._generate_simple_app(prompt, "fallback")

    def _parse_llm_response(self, content):
        """Parse LLM response and extract code"""
        try:
            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)

            # If no JSON found, wrap content as HTML
            return {"index.html": content}

        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from LLM response")
            # Return content as HTML
            if '<html' in content.lower():
                return {"index.html": content}
            else:
                return self._generate_simple_app("fallback", "error")

    def _generate_simple_app(self, brief, task_name):
        """Generate a simple fallback app"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{task_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 100%;
        }}

        h1 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2em;
        }}

        .content {{
            margin: 20px 0;
        }}

        .input-group {{
            margin: 20px 0;
        }}

        input, textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}

        input:focus, textarea:focus {{
            outline: none;
            border-color: #667eea;
        }}

        button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }}

        button:hover {{
            background: #764ba2;
        }}

        .result {{
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
            display: none;
        }}

        .result.show {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{task_name}</h1>
        <div class="content">
            <p><strong>Task Brief:</strong> {brief[:200]}...</p>
        </div>

        <div class="input-group">
            <input type="text" id="userInput" placeholder="Enter something...">
        </div>

        <button onclick="processInput()">Submit</button>

        <div class="result" id="result"></div>
    </div>

    <script>
        function processInput() {{
            const input = document.getElementById('userInput').value;
            const result = document.getElementById('result');

            if (input.trim() === '') {{
                result.textContent = 'Please enter something!';
                result.style.background = '#ffe0e0';
            }} else {{
                result.textContent = 'Processed: ' + input;
                result.style.background = '#e0ffe0';
            }}

            result.classList.add('show');
        }}

        document.getElementById('userInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                processInput();
            }}
        }});
    </script>
</body>
</html>
"""
        return {"index.html": html}
