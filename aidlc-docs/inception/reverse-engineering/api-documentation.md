# API Documentation

## CLI Interfaces

### `dsh web`
- **Command**: `dsh web [--port <port>] [--no-open]`
- **Purpose**: Starts the Web UI server and serves the browser frontend.
- **Default Port**: `3080` (binds to `127.0.0.1`).

### `dsh --profile <name>`
- **Command**: `dsh --profile <headless|sdk|acp|sdk-minimal>`
- **Purpose**: Launches specific execution modes (batch runner, SDK JSON-RPC daemon, or ACP automation).

## REST & WebSocket APIs (Web App Backend)

### Session Management
- **`GET /api/sessions`**: List all saved sessions.
- **`POST /api/sessions`**: Create a new session.
- **`GET /api/sessions/:id`**: Fetch session details and event history.
- **`DELETE /api/sessions/:id`**: Delete a session.

### Live Session WebSocket
- **Endpoint**: `/ws/sessions/:id`
- **Protocol**: Bidirectional event streaming (`turn/start`, `assistant/chunk`, `tool/call`, `tool/result`, `user/message`).

## Internal APIs (Cordis Context Services)

### `ctx.sessions` (`packages/core/session`)
- **`get(id: string): Session | undefined`**: Retrieve session by ID.
- **`create(options?: SessionOptions): Session`**: Create a new session instance.
- **`appendEvent(sessionId: string, event: SessionEvent): Promise<void>`**: Append an event to the session stream.

### `ctx.agentLoop` (`packages/core/agent-loop`)
- **`startTurn(agent: Agent, input: UserInput): Promise<TurnResult>`**: Execute an agent turn.
- **`stopTurn(agent: Agent, reason?: string): Promise<void>`**: Signal turn termination.

### `ctx.tools` (`packages/core/tools`)
- **`register(tool: ToolDefinition): Disposable`**: Register a tool in the active scope.
- **`execute(name: string, args: Record<string, unknown>, context: ToolContext): Promise<ToolResult>`**: Execute a tool through the pre/post interceptor pipeline.

### `ctx.llm` (`packages/llm/llm`)
- **`stream(messages: LLMMessage[], options?: StreamOptions): AsyncIterable<LLMChunk>`**: Stream model generation chunks.

## Data Models

### `SessionEvent`
```typescript
interface SessionEvent {
  id: string;
  sessionId: string;
  type: string; // e.g. "turn/start", "user/message", "tool/call", "tool/result", "turn/end"
  timestamp: number;
  payload: Record<string, unknown>;
}
```

### `ToolDefinition`
```typescript
interface ToolDefinition {
  name: string;
  description: string;
  parameters: JSONSchema;
  execute: (args: Record<string, unknown>, ctx: ToolContext) => Promise<unknown>;
}
```
