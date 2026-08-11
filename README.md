# Aeris AI Assistant

Aeris is a powerful, modular, secure, and extensible personal AI assistant designed for real-world interaction, computer operation, file management, and autonomous multi-step task execution.

## Current Limitations & Known Issues

- **AI API Quotas**: If you are using a free tier API key (e.g., Gemini Free Tier), you may experience `429 RESOURCE_EXHAUSTED` errors if you exceed requests per minute. Aeris handles this gracefully by reverting to degraded offline mode.
- **Voice Control**: Voice input/output (Speech-to-Text / Text-to-Speech) is currently **NOT IMPLEMENTED**. Text interface must be used.
- **File Downloads**: Direct file downloading from the browser is currently unsupported for security reasons.

## Vision
To act as a capable, real-world personal assistant (inspired by concepts like JARVIS) focusing on modular design, extreme security, robust context management, and systematic testing.

## Key Capabilities
- **Modular Core:** Easy-to-extend flow architectures (`CodingFlow`) alongside configurable context managers.
- **Autonomous Agent Loop:** Dynamic tool execution utilizing LLM `FunctionCalling` with automated error recovery.
- **Computer Operation:** Interacts securely with system elements (Keyboard, Mouse, Screen, FS, Commands) under tightly controlled scopes.
- **Robust Security boundaries:** A `PermissionManager` and global `KillSwitch` control execution safety. Read/Write path boundaries encapsulate tools.
- **Persistent Memory:** Contextual memory separation to maintain user privacy without cross-contamination.

## Comprehensive Test Architecture
The Aeris ecosystem has been systematically evaluated through an extensive unified test suite:
1. **Core Foundation & Security**: Validates unit components, `PermissionManager`, `KillSwitch` boundaries, and performs UI smoke tests.
2. **Computer Control Safety**: Tests that all local computer control actions obey absolute `dry_run` modes and strictly observe permitted file system boundaries (`settings.allowed_paths`).
3. **Agent & Recovery**: Evaluates autonomous tool-loop recovery mechanisms. Simulates catastrophic local exceptions gracefully being returned to the AI for self-correction.
4. **Memory & Context**: Assesses cross-instance memory boundaries preventing data leaks between distinct sessions.
5. **Ecosystem Workflows**: End-to-end regression verifying physical writes strictly within isolated temp boundaries and context flow overrides.

## Running Tests
Run the complete, robust test suite covering all architectural segments using:
```bash
$env:PYTHONPATH="."
pytest tests/
```

You can also run specific subsets of tests using markers:
```bash
pytest -m "integration" tests/
pytest -m "computer" tests/
```

## Running the Application
```bash
$env:PYTHONPATH="."
python -m aeris.main
```
