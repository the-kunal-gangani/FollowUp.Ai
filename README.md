# FollowUp.AI

A desktop app that turns messy meeting transcripts — typed or spoken — into a clean list of action items. No cloud API key required; it runs entirely on your own machine using a local LLM.

---

## Problem

Meetings end, and half of what was agreed gets forgotten within a day — who owns what, and by when. Manually re-reading a transcript to extract tasks is tedious and something people just don't do consistently. FollowUp.AI reads the transcript for you and hands back a clear, structured list: task, owner, deadline, priority.

---

## Features

- **Paste a transcript directly**, or **upload an audio recording** — both are supported
- **Offline audio transcription** via Whisper (`faster-whisper`) — no internet needed once the model is downloaded
- **Local AI extraction** via Ollama — runs entirely on your machine, completely free, no API key, no data leaving your computer
- Each action item is broken down into **task, owner, deadline, and priority**, shown as color-coded cards
- **Export to CSV** for sharing or importing into a task tracker
- Handles the messy reality of local LLM output — extracts the structured result even when the model adds extra chatty text around it

---

## Tech Stack

Python · customtkinter · Ollama (local LLM inference) · faster-whisper (offline speech-to-text)

---

## Project Structure

```
followup-ai/
├── gui.py              # Desktop app — main entry point, all UI/layout
├── extractor.py         # Sends transcript to a local Ollama model, parses structured action items
├── transcriber.py        # Offline audio → text via faster-whisper
├── settings.py           # Local Ollama host/model + Whisper preferences, saved to settings.json
└── requirements.txt
```

---

## Setup

**1. Install Ollama** (one-time, free): https://ollama.com

**2. Pull a model:**
```bash
ollama pull llama3.2
```

**3. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run it:**
```bash
python gui.py
```

---

## Usage

1. Paste a transcript into the text box, or click **Upload Audio** to transcribe a recording first
2. Click **Extract Action Items**
3. Review the generated task cards — each shows the task, owner, deadline, and priority
4. Click **Export CSV** to save the list

First-time setup: open **Settings** and hit **Test Connection** to confirm Ollama is reachable before extracting.

---

## Why local-first

Meeting content is often sensitive — client details, internal decisions, personnel discussions. Running the extraction entirely on-device means nothing gets sent to a third-party API. It also means zero ongoing cost.

---

## Roadmap

- One-click model download from within the app (skip the terminal step)
- Optional cloud model support (Claude/Gemini) for higher accuracy when available
- Direct export to Notion / Google Tasks