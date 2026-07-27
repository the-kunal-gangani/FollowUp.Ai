import json
import re
import ollama
import groq

EXTRACTION_SYSTEM_PROMPT = """You extract action items from meeting transcripts.

Read the transcript and identify every concrete action item, task, or commitment mentioned.

Respond with ONLY a JSON array, no other text, no markdown code fences, no explanation. Each element must have exactly these fields:
- "task": a short, clear description of what needs to be done
- "owner": the person responsible, or "Unassigned" if not mentioned
- "deadline": the deadline mentioned in the transcript (e.g. "Friday", "next week", "March 5"), or "Not specified" if none given
- "priority": one of "High", "Medium", "Low" based on urgency language used

If there are no clear action items, respond with an empty JSON array: []
"""


def _strip_code_fences(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_array(text):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    return match.group(0) if match else text


def _parse_and_validate(raw_text):
    cleaned = _strip_code_fences(raw_text)
    cleaned = _extract_json_array(cleaned)

    try:
        items = json.loads(cleaned)
    except json.JSONDecodeError:
        return None, f"Could not parse the model's response as JSON:\n{raw_text[:300]}"

    if not isinstance(items, list):
        return None, "Model response was not a list of action items."

    valid_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        valid_items.append({
            "task": str(item.get("task", "")).strip() or "Unnamed task",
            "owner": str(item.get("owner", "Unassigned")).strip() or "Unassigned",
            "deadline": str(item.get("deadline", "Not specified")).strip() or "Not specified",
            "priority": str(item.get("priority", "Medium")).strip() or "Medium",
        })

    return valid_items, None


def check_ollama_available(host="http://localhost:11434"):
    try:
        client = ollama.Client(host=host)
        client.list()
        return True, None
    except Exception as exc:
        return False, str(exc)


def check_groq_available(api_key):
    if not api_key or not api_key.strip():
        return False, "No Groq API key set."
    try:
        client = groq.Groq(api_key=api_key)
        client.models.list()
        return True, None
    except groq.AuthenticationError:
        return False, "Invalid Groq API key."
    except Exception as exc:
        return False, str(exc)


def _extract_local(transcript, model, host):
    try:
        client = ollama.Client(host=host)
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
        )
    except ollama.ResponseError as exc:
        if "not found" in str(exc).lower():
            return [], (
                f"Model '{model}' isn't installed. Run this in a terminal first:\n\n"
                f"ollama pull {model}"
            )
        return [], f"Ollama error: {exc}"
    except Exception as exc:
        return [], (
            f"Could not reach Ollama at {host}.\n\n"
            f"Make sure the Ollama app is installed and running, then try again.\n\n"
            f"Details: {exc}"
        )

    raw_text = response["message"]["content"]
    items, error = _parse_and_validate(raw_text)
    if error:
        return [], error
    return items, None


def _extract_cloud(transcript, api_key, model):
    if not api_key or not api_key.strip():
        return [], "No Groq API key set. Add one in Settings first."

    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
        )
    except groq.AuthenticationError:
        return [], "Invalid Groq API key. Check your key in Settings."
    except groq.APIConnectionError:
        return [], "Could not connect to Groq's API. Check your internet connection."
    except Exception as exc:
        return [], f"Groq request failed: {exc}"

    raw_text = response.choices[0].message.content
    items, error = _parse_and_validate(raw_text)
    if error:
        return [], error
    return items, None


def extract_action_items(transcript, backend="local",
                          ollama_model="llama3.2", ollama_host="http://localhost:11434",
                          groq_api_key="", groq_model="llama-3.3-70b-versatile"):
    if not transcript or not transcript.strip():
        return [], "Transcript is empty — nothing to extract."

    if backend == "cloud":
        return _extract_cloud(transcript, api_key=groq_api_key, model=groq_model)
    return _extract_local(transcript, model=ollama_model, host=ollama_host)