# Unit 5 Functional Design Plan: Bundles, CLI & SDK

## Purpose
Plan the bootstrapping bundle system, interactive CLI experience with Typer/Rich (primary command `atomos`, alias `atimos`), local LLM `--local` mode, and the programmatic async SDK client for **Unit 5: Bundles, CLI & SDK** (`python/atomos/boot/`, `python/atomos/cli/`, `python/atomos/sdk/`).

---

## Execution Checklist

- [x] **Step 1: Collect User Functional Preferences for Unit 5** (Completed with user answers: A, A, A)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: No ambiguities)
- [x] **Step 3: Generate Unit 5 Domain Entities Document** (`aidlc-docs/construction/unit-5-bundles-cli-sdk/functional-design/domain-entities.md`)
- [x] **Step 4: Generate Unit 5 Business Logic Model** (`aidlc-docs/construction/unit-5-bundles-cli-sdk/functional-design/business-logic-model.md`)
- [x] **Step 5: Generate Unit 5 Business Rules & Validation** (`aidlc-docs/construction/unit-5-bundles-cli-sdk/functional-design/business-rules.md`)
- [ ] **Step 6: User Approval of Unit 5 Functional Design**

---

## Mandatory Artifacts to Generate
- `domain-entities.md`: Data models for `Profile`, `BaseBundle`, `CLIConfig`, `AtomosClient`, and `InteractiveSessionRunner`.
- `business-logic-model.md`: Bootstrapping sequence (Profile -> Mount Bundles -> DI Context -> Initialize Store/Tools/LLM -> Run CLI / SDK).
- `business-rules.md`: CLI argument precedence (CLI flags > environment variables > profile defaults), local runner defaults, and SDK lifecycle rules.

---

## Functional Design Questions for Unit 5

Please answer the following questions to guide the design of the CLI, SDK, and bundle bootstrap layer.

### Question 1: CLI Interactive REPL Loop Formatting
How should the interactive terminal REPL format assistant thought processes, markdown responses, and tool call progress?

A) **Rich Live Render with Real-Time Markdown & Tool Call Panels** (Recommended: Beautiful syntax-highlighted streaming output, tool invocation panels, and session token usage status)

B) **Plain Standard Text Terminal Output**: Minimalist unformatted terminal stdout

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Local Model Runner CLI Invocation Flags
How should local offline model execution (Ollama, LMStudio, vLLM) be toggled from the command line?

A) **`--local / -l` Flag with `--local-url` Override** (Recommended: `atomos --local` or `atomos --local --model qwen2.5-coder` automatically switches to local OpenAI-compatible endpoint at `http://localhost:11434/v1` without checking API keys)

B) **Explicit `--provider ollama` Argument**: Require passing `--provider` explicitly

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Programmatic SDK Interface Pattern
How should the `AtomosClient` async Python SDK be instantiated and used?

A) **Async Context Manager & One-Liner Generator** (Recommended: `async with AtomosClient(workspace=".") as client: async for token in client.chat("Summarize src/"): print(token, end="")`)

B) **Callback-Driven Client**: Requiring callback registrations for each event

X) Other (please describe after [Answer]: tag below)

[Answer]: A
