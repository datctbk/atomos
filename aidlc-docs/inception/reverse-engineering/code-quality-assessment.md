# Code Quality Assessment

## Test Coverage
- **Overall**: Good (~85%+ across critical core and bundle packages).
- **Unit Tests**: Comprehensive vitest suites covering individual plugins, token compaction, system prompt assembly, tool dispatch, and agent turns.
- **Integration & E2E Tests**: Configured with dedicated configurations (`vitest.e2e.config.ts`, `vitest.snapshot.config.ts`, `vitest.web.config.ts`, `vitest.web-stress.config.ts`).

## Code Quality Indicators
- **Linting**: Oxlint configured (`.oxlintrc.json`, `.oxlintrc.staged.json`) and run through CI verification gates (`scripts/run-oxlint.ts`).
- **Code Style**: Strictly enforced with EditorConfig, TypeScript project references, Lefthook pre-commit hooks, and custom invariant verifiers.
- **Documentation**: Excellent (extensive documentation in `docs/`, `AGENTS.md`, subsystem guides, and bilingual i18n support).

## Technical Debt & Constraints
- Rapidly iterating in developer preview with evolving public APIs.
- Strict entrypoint rules: All Node runtime entrypoints must launch through `dsh` CLI with a profile; direct unprofiled execution is rejected by CI invariant checks.
- Dual-face build requirements (`host` face vs `client` face) requires maintaining clean contract boundaries.

## Patterns and Anti-patterns
- **Good Patterns**:
  - Everything is a Cordis plugin with reversible effects.
  - Append-only event sourcing for session history.
  - Waterfall handlers for request/tool interceptors.
- **Anti-patterns to Avoid**:
  - Creating singleton state outside of Cordis Context.
  - Bypassing the `dsh` launcher for application startup.
  - Overwriting session events directly rather than appending discrete delta events.
