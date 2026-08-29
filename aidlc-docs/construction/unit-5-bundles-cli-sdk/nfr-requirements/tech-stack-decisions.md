# Unit 5 Tech Stack Decisions: Bundles, CLI & SDK

This document records the technology selections and packaging specifications for Unit 5.

---

## 1. Technology Choices & Libraries

| Capability | Selected Approach | Version | Rationale |
|---|---|---|---|
| **CLI Application Framework** | `typer` | `>=0.12.0` | Strongly-typed CLI commands with automatic shell autocompletion and help synthesis. |
| **Terminal UI & Styling** | `rich` | `>=13.7.0` | Live Markdown streaming, panels, spinners, and theme formatting. |
| **Packaging & Entrypoints** | `pyproject.toml` (`[project.scripts]`) | PEP 621 | Dual command script registration (`atomos` and `atimos`). |

---

## 2. Directory & Packaging Specifications
- **Package Path**:
  - `python/atomos/boot/profile.py`: `Profile` configuration model and bootstrap coordinator.
  - `python/atomos/boot/bundles/base.py`: `BaseBundle`, `CoreBundle`, `ToolsBundle`, `LLMBundle`.
  - `python/atomos/cli/main.py`: Typer CLI application (`atomos` and `atimos`).
  - `python/atomos/sdk/client.py`: `AtomosClient` programmatic Python async SDK.
