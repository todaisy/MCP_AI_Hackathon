import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

def handle_tool_call(tool_call_json: str) -> str:
    """Main entry point for MCP tool-call interface"""
    try:
        tool_call = json.loads(tool_call_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"})

    tool_name = tool_call.get("tool_call")
    args = tool_call.get("arguments", {})

    if tool_name == "summarize_meeting":
        result = summarize_meeting(args.get("transcript", ""))
    elif tool_name == "extract_tasks":
        result = extract_tasks(args.get("transcript", ""))
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result, ensure_ascii=False, indent=2)


def summarize_meeting(transcript: str) -> dict:
    if not transcript.strip():
        return {"summary": "Нет текста для анализа."}

    prompt = f"""
You are an assistant that summarizes meetings. Read the transcript and summarize it in 2-3 sentences.

Transcript:
{transcript}

Return only the summary as plain text.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    try:
        return {"summary": response.json()["response"].strip()}
    except Exception:
        return {"summary": "Ошибка при генерации."}


def extract_tasks(transcript: str) -> dict:
    if not transcript.strip():
        return {"tasks": []}

    prompt = f"""
You are a helpful assistant that extracts tasks from meeting transcripts.

Transcript:
{transcript}

Extract all actionable tasks and return them as a JSON array:
[
  {{
    "title": "...",
    "description": "...",
    "assignee": "...",
    "deadline": "..."
  }},
  ...
]
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    try:
        raw = response.json()["response"]
        tasks = json.loads(raw)
        return {"tasks": tasks}
    except Exception:
        return {"tasks": []}