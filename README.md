# FollowUp.AI

A desktop app that turns messy meeting transcripts — typed or spoken — into a clean, structured list of action items. Choose between running entirely free and private on your own machine, or a free cloud backend when your PC needs the extra speed.

---

## Problem

Meetings end, and half of what was agreed gets forgotten within a day — who owns what, and by when. Manually re-reading a transcript to extract tasks is tedious and something people just don't do consistently. FollowUp.AI reads the transcript for you and hands back a clear list: task, owner, deadline, priority.

---

## Features

### Input
- **Paste a transcript directly**, or **upload an audio recording** — both supported
- Offline audio transcription via Whisper (`faster-whisper`), optimized for speed:
  - English-only model variants used by default (smaller, faster, more accurate for English speech)
  - Silence-skipping (VAD) so pauses in the recording don't waste processing time
  - Automatic fallback pass if silence-detection misjudges real speech as quiet
  - Confidence-based filtering that rejects Whisper "hallucinations" — when fed music or unclear audio, Whisper can confidently invent plausible-sounding fake text instead of admitting it couldn't understand anything. FollowUp.AI checks Whisper's own confidence signal per segment and drops anything it isn't sure about, rather than presenting fabricated text as a real transcript
  - Live progress feedback during transcription (not just a spinner)

### Extraction
- **Two backend options, switchable anytime in Settings:**
  - **Local (Ollama)** — completely free, fully private, runs on your own machine, no internet required once set up
  - **Cloud (Groq)** — free tier, much faster, needs an internet connection and a free API key
  - A "Test Connection" button for whichever backend is active, so you can confirm it's reachable before running anything
- Each action item is broken into **task, owner, deadline, and priority**, shown as color-coded cards
- Handles the messy reality of LLM output — extracts the structured result even when the model wraps it in explanation text or markdown fences instead of clean JSON

### Output
- **Export to CSV** for sharing or importing into a task tracker

---

## Tech Stack

Python · customtkinter · Ollama (local LLM inference) · Groq API (cloud LLM inference) · faster-whisper (offline speech-to-text)

---

## Project Structure

```
followup-ai/
├── gui.py              # Desktop app — main entry point, all UI/layout
├── extractor.py         # Sends transcript to Ollama or Groq, parses structured action items
├── transcriber.py        # Offline audio → text via faster-whisper, with hallucination filtering
├── settings.py           # Local backend choice, Ollama/Groq config, Whisper preferences
├── icon.ico              # App icon
└── requirements.txt
```

---

## Setup

**1. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**2. Choose a backend:**

**Option A — Local (free, private, needs your own PC to run the model):**
- Install Ollama: https://ollama.com
- Pull a model:
```bash
ollama pull llama3.2
```

**Option B — Cloud (free tier, faster, needs internet):**
- Get a free API key: https://console.groq.com/keys
- Add it in the app's Settings once it's running

**3. Run it:**
```bash
python gui.py
```

---

## Usage

1. Paste a transcript into the text box, or click **Upload Audio** to transcribe a recording first
2. Open **Settings** to pick Local or Cloud, add your Groq key if using Cloud, and hit **Test Connection** to confirm it's reachable
3. Click **Extract Action Items**
4. Review the generated task cards — each shows the task, owner, deadline, and priority
5. Click **Export CSV** to save the list

---

## Why this design

**Local-first by default.** Meeting content is often sensitive — client details, internal decisions, personnel discussions. Running extraction entirely on-device means nothing gets sent to a third party, at zero ongoing cost. The cloud option exists for when your machine simply can't run a local model comfortably, without giving up the choice.

**Confidence, not just output.** Most transcription tools treat any text the model returns as correct. Whisper's own uncertainty signal is used to catch and discard likely-fabricated text instead of presenting it as a genuine transcript.

---

## Roadmap

- Speaker labels for multi-person recordings
- Direct export to Notion / Google Tasks
- Package as a standalone `.exe`
- One-click model download from within the app (skip the terminal step)