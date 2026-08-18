# Aeris AI Assistant

Aeris is a powerful, modular, secure, and extensible personal AI assistant designed for
real-world interaction, computer operation, file management, and autonomous multi-step
task execution — powered by Google Gemini.

---

## Requirements

- **Python 3.10+** (developed on Python 3.13)
- Google Gemini API key ([get one free at Google AI Studio](https://aistudio.google.com))
- Windows 10/11 (computer control tools use Windows APIs)

---

## Setup

```powershell
# 1. Clone the repository
git clone https://github.com/youruser/aeris-ai-assistant.git
cd aeris-ai-assistant

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
copy .env.example .env
# Edit .env and set AERIS_API_KEY=your_key_here

# 5. Run Aeris
python -m aeris
```

---

## Running the Application

```powershell
$env:PYTHONPATH="."
python -m aeris
```

---

## Key Capabilities

| Capability | Status |
|-----------|--------|
| AI Conversation (Gemini) | ✅ Implemented |
| Computer: Keyboard control | ✅ Implemented |
| Computer: Mouse control | ✅ Implemented |
| Computer: Window management | ✅ Implemented |
| Computer: Filesystem (read/write) | ✅ Implemented |
| Computer: Clipboard | ✅ Implemented |
| Computer: Screenshot | ✅ Implemented |
| Computer: Shell commands (allowlist) | ✅ Implemented |
| Computer: Browser (open URLs) | ✅ Implemented |
| Persistent Memory | ✅ Implemented |
| Session Memory | ✅ Implemented |
| Autonomous Agent Loop | ✅ Implemented |
| Flow System (CodingFlow) | ✅ Implemented |
| Kill Switch (emergency stop) | ✅ Implemented |
| Dry Run mode (simulate actions) | ✅ Implemented |
| System Metrics (CPU/RAM/GPU) | ✅ Implemented |
| Secret Redaction in Logs | ✅ Implemented |
| Voice Control | ❌ Not Implemented |
| Web Search | ❌ Not Implemented |
| Direct File Downloads | ❌ Not Implemented |

---

## Security Model

Aeris is built with security as a first principle:

- **Permission Levels**: Every tool is rated SAFE / LOW_RISK / MEDIUM_RISK / HIGH_RISK / SENSITIVE.  
  HIGH_RISK tools (e.g., `command_execution`) require explicit user confirmation before running.
- **Kill Switch**: Instantly halts all computer-control operations. Available in the UI (Security tab).
- **Dry Run Mode**: When enabled, Aeris describes what it *would* do without actually doing it.  
  Safe for testing or demonstration.
- **Filesystem Sandboxing**: `fs_control` and `screen_control` only operate within `AERIS_ALLOWED_PATHS`.  
  Attempts to access outside these paths are rejected.
- **Command Allowlist**: `command_execution` only runs commands explicitly listed in `AERIS_COMMAND_ALLOWLIST`.
- **Secret Redaction**: API keys and registered secrets are automatically redacted in all logs.

---

## Known Limitations

- **AI API Quotas**: Free-tier Gemini API keys may return `429 RESOURCE_EXHAUSTED` under heavy use.  
  Aeris handles this gracefully by entering degraded offline mode.
- **Windows Only**: Computer control tools (mouse, keyboard, window management) use Windows APIs.  
  The AI conversation layer is cross-platform.
- **Voice Control**: Speech-to-Text / Text-to-Speech is **not implemented**. Use the text interface.
- **Web Search**: Aeris cannot search the web autonomously (only open URLs via the browser tool).
- **File Downloads**: Aeris cannot autonomously download files from the internet.

---

## Running Tests

```powershell
$env:PYTHONPATH="."

# Run all automated tests
venv\Scripts\python.exe -m pytest tests\ -v

# Run only unit tests (excludes integration and computer tests)
venv\Scripts\python.exe -m pytest tests\ -v -m "not integration and not computer"

# Run integration tests
venv\Scripts\python.exe -m pytest tests\ -v -m "integration"

# Run computer control tests (use dry_run — no real system interaction)
venv\Scripts\python.exe -m pytest tests\ -v -m "computer"

# Run the manual UI smoke test (opens a real window)
python tests\smoke_test.py
```

---

## Architecture Overview

```
aeris/
├── __main__.py          # Application entry point
├── core/
│   ├── application.py   # AerisCore: startup, shutdown, message routing
│   ├── agent.py         # AerisAgent: autonomous tool-calling loop
│   ├── conversation.py  # Conversation history management
│   ├── context.py       # System instruction + memory context builder
│   └── events.py        # Global pub/sub event system
├── ai/
│   ├── gemini_provider.py  # Gemini API integration (send, stream, validate)
│   └── types.py            # AIRequest, AIResponse dataclasses
├── tools/
│   ├── registry.py         # Tool registration and lookup
│   ├── security.py         # KillSwitch, PermissionManager, PermissionLevel
│   └── computer/           # All computer control tools
│       ├── mouse.py        # Mouse movement and clicking
│       ├── keyboard.py     # Keyboard typing and key presses
│       ├── app.py          # Process/application listing and management
│       ├── window.py       # Window focus, minimize, maximize, close
│       ├── fs.py           # Filesystem read/write/delete/list
│       ├── clipboard.py    # Clipboard read/write/clear
│       ├── screen.py       # Screenshot, screen dimensions
│       ├── browser.py      # Open URLs in browser
│       ├── command.py      # Shell command execution (allowlisted)
│       └── system.py       # Volume, brightness, system info
├── memory/
│   ├── interface.py        # SessionMemory (in-memory per session)
│   └── persistent.py      # PersistentMemory (JSON-backed, survives restarts)
├── flows/
│   ├── base.py             # BaseFlow: tool filtering + instruction override
│   └── coding.py           # CodingFlow: filesystem+command focus
├── config/
│   └── settings.py         # All settings loaded from .env
├── security/
│   └── secrets.py          # SecretManager: registers and redacts secrets
└── ui/
    ├── main_window.py      # Main CustomTkinter window
    ├── state.py            # UIState: reactive state for UI updates
    ├── monitor.py          # SystemMonitor: real-time CPU/RAM/GPU metrics
    ├── components/
    │   └── sidebar.py      # Navigation sidebar
    └── views/
        ├── chat.py         # Chat interface
        ├── system.py       # System metrics view
        ├── tasks.py        # Task management view
        └── security.py     # Security controls (kill switch, dry run)
```
