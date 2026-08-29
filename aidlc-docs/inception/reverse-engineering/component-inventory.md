# Component Inventory

## Application Packages
- `apps/cli`: CLI runner binary `@deepseek-ai/dsh-cli`.
- `apps/web`: Browser frontend interface `@deepseek-ai/dsh-web-frontend`.
- `packages/boot/app-boot`: Profile boot sequence and bundle layering.
- `packages/core/agent`: Agent interface and registry.
- `packages/core/agent-loop`: Core execution driver.
- `packages/core/session`: Session event store.
- `packages/core/tools`: Tool registry and execution pipeline.
- `packages/core/system-prompt`: System prompt assembler.
- `packages/llm/llm`: LLM streaming abstraction.
- `packages/fs/fs`: File manipulation tools.
- `packages/shell/shell`: Shell execution engine.
- `packages/mcp/mcp`: MCP client/server bridge.
- `packages/subagent/subagent`: Multi-agent orchestration.
- `packages/workflow/workflow`: Multi-step workflow runner.
- `packages/plan/plan`: Planning and task breakdown service.

## Infrastructure & Sandbox Packages
- `packages/sandbox/sandbox`: Sandbox abstraction layer.
- `packages/e2b/e2b`: E2B Cloud container runtime integration.
- `native/landlock-run`: Linux Landlock syscall isolation binary.

## Bundle Packages (Composition Layers)
- `packages/bundle/base`: Shared base plugin layer (`dsh-base`).
- `packages/bundle/web-app`: Web application composition layer.
- `packages/bundle/headless`: Headless batch execution layer.
- `packages/bundle/sdk-app`: SDK server layer.
- `packages/bundle/acp-app`: Automation ACP server layer.
- `packages/bundle/sdk-minimal`: Standalone minimal SDK bundle.

## Shared & Utility Packages
- `packages/util/util`: Shared utility functions.
- `packages/context/context`: Context window management and compaction.
- `packages/compaction/compaction`: Token compaction strategies.
- `packages/credentials/credentials`: Secret and key management.
- `packages/settings/settings`: User configuration and defaults.
- `packages/storage/storage`: Local persistence adapters.

## Test & Tooling Packages
- `packages/test-support/*`: Shared vitest helpers, mocks, and snapshot validators.
- `scripts/*`: Build, validation, lint, CI gates, and documentation checkers.

## Total Count
- **Total Packages / Apps / Crates**: 55+
- **Application Modules**: ~35
- **Infrastructure / Native Modules**: ~5
- **Shared / Utility Modules**: ~10
- **Test / Script Tooling**: ~10
