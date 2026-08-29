# Requirements Verification Questions

Please review and fill in the `[Answer]:` tags for the questions below to guide the Requirements Analysis for your work on `deepseek-harness`.

---

## Question 1: Primary Objective / Scope of Work
What specific task, feature, or change would you like to implement in `deepseek-harness`?

A) Add a new Plugin / Tool capability (e.g., custom tool, MCP integration, or sandbox adapter)

B) Enhance Agent Loop / Turn orchestration or System Prompt assembly (`packages/core/*`)

C) Web UI / CLI / SDK enhancement or configuration update (`apps/*`, `packages/sdk`, `packages/bundle/*`)

D) General codebase exploration, refactoring, or running & fixing tests

X) Other (please describe after [Answer]: tag below)

[Answer]: I want to reimplement deepseek harness with python

---

## Question 2: Target Subsystem / Package
Which package(s) or layer do you expect to modify?

A) Core framework (`packages/core/agent-loop`, `packages/core/session`, `packages/core/tools`, etc.)

B) Application bundles or launchers (`packages/bundle/*`, `apps/cli`, `apps/web`)

C) Tooling / Runtime integrations (`packages/fs`, `packages/shell`, `packages/sandbox`, `packages/mcp`)

D) Whole repository / Undetermined yet (need AI recommendation based on objective)

X) Other (please describe after [Answer]: tag below)

[Answer]: I want to reimplement deepseek harness with python

---

## Question 3: Security Extension Opt-In
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 4: Resiliency Baseline Opt-In
Should the resiliency baseline be applied to this project?

**What this extension is:** Enabling it applies a set of **directional, design-time best practices** for building resilient systems, derived from the **AWS Well-Architected Framework (Reliability Pillar)** and resilience-review guidance. It steers requirements, design, and code toward fault tolerance, high availability, observability, and recoverability — covering 15 practice areas across business goals, change management, observability, high availability, disaster recovery, and continuous improvement.

**What this extension is NOT:** Enabling it does **not** make your workload production-ready, nor does it certify or guarantee any availability, RTO, or RPO target. It is a **starting point** that scaffolds good resiliency decisions early — it is not a substitute for a formal **AWS Well-Architected Review** of the built system.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads, as an informed starting point that you can validate and harden before go-live)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 5: Property-Based Testing Extension Opt-In
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

X) Other (please describe after [Answer]: tag below)

[Answer]: A
