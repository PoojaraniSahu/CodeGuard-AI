import google.generativeai as genai
import json
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

# Use the latest gemini model
MODEL_NAME = "gemini-2.5-flash"

PROMPT_TEMPLATE = """
You are a senior code reviewer. Analyze the following complete file content from a repository.

- Find bugs (Logic errors, edge case issues, bad patterns)
- Suggest improvements (Code readability, style)
- Detect security risks (Hardcoded secrets, SQL injection risks, unsafe APIs)

Provide your response in raw JSON format exactly like this, no markdown wrappers, no extra text:
[
  {{
    "issue_type": "bug|security|style",
    "severity": "high|medium|low",
    "message": "Detailed description of the issue and how to fix it.",
    "file_path": "path/to/file.py",
    "line_number": 0 // if applicable, otherwise omit or set to 0
  }}
]

File content for {filename}:

{content}
"""

def analyze_full_file(filename: str, content: str) -> list:
    if not content or not content.strip():
        return []

    model = genai.GenerativeModel(MODEL_NAME)
    prompt = PROMPT_TEMPLATE.format(filename=filename, content=content)
    
    response = model.generate_content(prompt)
    
    try:
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
            
        parsed_json = json.loads(raw_text)
        return parsed_json
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw Response was: {response.text}")
        return []
