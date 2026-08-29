# Unit 2 NFR Requirements Plan: LLM Adapter & Streaming Engine

## Purpose
Assess and define the non-functional requirements, resilience baselines (`RES-01`), timeout policies, and security constraints (`SECURITY-07`) for **Unit 2: LLM Adapter & Streaming Engine** in `atomos`.

---

## Execution Checklist

- [x] **Step 1: Collect User NFR Preferences for Unit 2** (Completed with user answers: A, A, A + Local LLM support requested)
- [x] **Step 2: Analyze Answers for Ambiguities & Refine** (Completed: Incorporated Local LLM OpenAI-compatible support)
- [x] **Step 3: Generate Unit 2 NFR Requirements Document** (`aidlc-docs/construction/unit-2-llm-adapter/nfr-requirements/nfr-requirements.md`)
- [x] **Step 4: Generate Unit 2 Tech Stack Decisions Document** (`aidlc-docs/construction/unit-2-llm-adapter/nfr-requirements/tech-stack-decisions.md`)
- [ ] **Step 5: User Approval of Unit 2 NFR Requirements**

---

## Mandatory Artifacts to Generate
- `nfr-requirements.md`: Specific timeout thresholds, retry with exponential backoff and jitter constraints (`RES-01`), and secure credential isolation (`SECURITY-07`).
- `tech-stack-decisions.md`: HTTP library choices (`httpx.AsyncClient` with streaming response iterators).

---

## NFR Planning Questions for Unit 2

Please answer the following questions to establish the non-functional specifications for Unit 2.

### Question 1: Connection & Streaming Timeout Configuration
What timeout thresholds should be configured for LLM API calls?

A) **Granular HTTP Timeouts (Connect: 10s, Read/Stream: 60s, Write: 10s, Pool: 10s)** (Recommended for reliable long token generation)

B) **Single Uniform Timeout (30s)**

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Resilience Retry Policy on Disconnects & Rate Limits (RES-01)
How should exponential backoff and retry behavior be executed on HTTP 429 / 5xx / connection drops?

A) **Exponential Backoff with Full Jitter (Max 3 retries, base delay 1.0s, max delay 10.0s)** (Recommended: $delay = \text{random}(0, \min(\text{max\_delay}, \text{base} \cdot 2^{\text{attempt}}))$)

B) **Linear Backoff without Jitter (Fixed 2.0s delay)**

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Mocking Strategy for Unit Tests & Offline Execution
How should LLM streaming responses be mocked during automated testing without consuming live API tokens?

A) **Deterministic Async Mock Adapter (`MockLLMAdapter`) & HTTPX Transport Mocking** (Recommended for 100% offline reproducible test runs)

B) **Live API Token with VCR.py cassette recording**

X) Other (please describe after [Answer]: tag below)

[Answer]: A
