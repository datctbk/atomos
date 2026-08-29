# Build Instructions: Atomos

This document provides complete instructions for building, packaging, and configuring `atomos` (with binary alias `atimos`).

---

## 1. Prerequisites
- **Python**: `>= 3.11` (Python 3.12+ recommended)
- **Package & Environment Manager**: `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **System Requirements**: macOS, Linux, or Windows (POSIX features like process group isolation use platform-native fallback on Windows).

---

## 2. Environment Setup

```bash
# Clone or navigate to the workspace
cd atomos/python

# Create virtual environment and install dependencies in editable mode
uv sync --extra dev
```

---

## 3. Environment Variables

| Variable | Description | Required? | Default |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek Cloud API Key | Required for Cloud DeepSeek | `""` |
| `OPENAI_API_KEY` | OpenAI Cloud API Key | Required for Cloud OpenAI | `""` |
| `ATOMOS_LOCAL_LLM_URL` | Local LLM endpoint URL | Optional for `--local` mode | `http://localhost:11434/v1` |

---

## 4. Verification & Testing

```bash
# Run code formatter and linter
uv run --extra dev ruff check .

# Run static type checking
uv run --extra dev mypy atomos tests

# Run all 44 unit and property-based tests
uv run --extra dev pytest -v
```

---

## 5. CLI Execution Examples

```bash
# Show CLI Help
uv run atomos --help
uv run atimos --help

# Run with Local Ollama model (no API key needed!)
uv run atomos --local "Summarize the files in this directory"

# Interactive REPL session with local model
uv run atomos -l
```
