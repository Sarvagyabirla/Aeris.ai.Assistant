# Aeris AI Assistant

Aeris is a modular, autonomous AI assistant. 

This repository currently implements **PART 1: Core Foundation**.

## Current Roadmap
- **PART 1 → Core Foundation (COMPLETE)**
- PART 2 → Computer Control (FUTURE)
- PART 3 → Autonomous Agent (FUTURE)
- PART 4 → Intelligence + Memory (FUTURE)
- PART 5 → Advanced Aeris Ecosystem (FUTURE)

## Architecture (Part 1)
The application is structured into clearly separated modules to ensure future extensibility:
- `core`: Coordinates application logic, context management, and pub/sub events.
- `ai`: Abstracts the AI provider (currently `google-genai` for Gemini).
- `config`: Handles environment settings safely.
- `security`: Ensures secrets are not leaked in logs or memory.
- `memory`: Foundation for tracking session history.
- `tools`: Registry for future tool definitions.
- `ui`: A CustomTkinter asynchronous desktop interface.
- `logging`: Filtered structured logging.

## Installation
1. Install Python 3.10+
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`

## Configuration
1. Copy `.env.example` to `.env`.
2. Add your AI API key (e.g., `AERIS_API_KEY`).
3. Set the model name if desired.

## Usage
Run the application:
```bash
python -m aeris
```

## Security
- API keys are never printed in logs.
- `.env` is ignored by Git.
- Provider errors are handled gracefully in the UI without crashing the application.
