# Technology Stack

## Programming Languages
- **TypeScript**: `~5.7.x` - Primary language across all core packages, apps, and bundles.
- **JavaScript / Node.js**: Node `^22.19.0 || >=24.0.0` - Target runtime engine.
- **Python**: Python 3.10+ - Python SDK client wrapper (`python/`).
- **Rust / C**: Native landlock sandboxing binaries (`native/landlock-run`).

## Frameworks & Libraries
- **Cordis**: `^3.x` - Micro-kernel inversion-of-control and plugin framework.
- **Vite / Vue / React**: Frontend web interface components.
- **Fastify / WS / HTTP**: Server runtime for web and ACP protocols.

## Infrastructure & Runtime
- **pnpm**: `v11.7.0` - Monorepo workspace package manager.
- **Linux Landlock**: Unprivileged sandboxing mechanism on Linux.
- **E2B**: Cloud execution containers.

## Build Tools
- **tsdown**: High-speed TypeScript packager for host/client faces.
- **tsx**: TypeScript runtime execution for scripts and build pipelines.
- **tsc**: Typechecker via TypeScript Project References (`tsconfig.base.json`).

## Testing & Quality Tools
- **Vitest**: `v3.x` - Unit, integration, snapshot, and e2e test suite.
- **Oxlint**: High-performance Rust-based JavaScript/TypeScript linter.
- **JSCPD**: Code duplication detector.
- **Knip**: Unused code and dependency scanner.
