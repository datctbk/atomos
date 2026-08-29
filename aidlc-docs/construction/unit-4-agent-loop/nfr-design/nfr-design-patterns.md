# Unit 4 NFR Design Patterns: Agent Loop & Turn Driver

This document details the concrete design patterns for token streaming, event bus lifecycle dispatch, sliding window compaction, and turn cancellation.

---

## 1. Streaming Token & Turn Execution Pattern

```python
class AgentLoop:
    """Multi-turn conversation engine orchestrating streaming LLM completions, tool execution, and session event sourcing."""

    async def run_turn(
        self,
        user_prompt: str,
        options: TurnOptions | None = None,
    ) -> AsyncIterator[str]:
        """Execute a full turn, yielding token strings in real time."""
        opts = options or TurnOptions()
        # 1. Persist User Message
        self.session.append_event(SessionEventType.USER_MESSAGE, {"text": user_prompt})
        await self.context.emit("agent/turn_start", {"session_id": self.session.session_id, "prompt": user_prompt})

        iteration = 0
        try:
            while iteration < opts.max_iterations:
                iteration += 1
                messages = self.compactor.compact_history(
                    self.session.events,
                    max_messages=opts.max_history_messages,
                    system_prompt=opts.system_prompt,
                )
                tools = self.tool_registry.get_openai_tools()
                accumulator = ToolCallAccumulator()
                full_text = ""

                async for chunk in self.llm_adapter.stream(messages, tools if tools else None):
                    if chunk.delta_content:
                        full_text += chunk.delta_content
                        await self.context.emit("agent/token", {"delta": chunk.delta_content})
                        yield chunk.delta_content

                    for frag in chunk.delta_tool_calls:
                        accumulator.add_fragment(frag)

                tool_calls = accumulator.get_tool_calls()
                # Persist Assistant Message
                self.session.append_event(
                    SessionEventType.ASSISTANT_MESSAGE,
                    {"text": full_text, "tool_calls": tool_calls if tool_calls else None},
                )

                if not tool_calls:
                    break

                # Execute requested tools sequentially
                for tc in tool_calls:
                    call_id = tc["id"]
                    func = tc["function"]
                    func_name = func["name"]
                    func_args = func["arguments"]

                    await self.context.emit("agent/tool_start", {"id": call_id, "name": func_name})
                    res = await self.tool_registry.execute_tool(func_name, func_args)
                    self.session.append_event(
                        SessionEventType.TOOL_RESULT,
                        {"tool_call_id": call_id, "name": func_name, "result": res.to_dict()},
                    )
                    await self.context.emit("agent/tool_end", {"id": call_id, "result": res.to_dict()})

        except asyncio.CancelledError:
            self.session.append_event(SessionEventType.AGENT_INTERRUPT, {"reason": "Cancelled by user"})
            await self.context.emit("agent/turn_cancelled", {"session_id": self.session.session_id})
            raise
        finally:
            await self.context.emit("agent/turn_end", {"session_id": self.session.session_id, "iterations": iteration})
```

---

## 2. Sliding Window Context Compactor Pattern

```python
class ContextCompactor:
    """Maintains message context within budget while preserving system instructions."""

    @staticmethod
    def compact_history(
        events: list[SessionEvent],
        max_messages: int = 50,
        system_prompt: str = "",
    ) -> list[LLMMessage]:
        raw_messages: list[LLMMessage] = []
        if system_prompt:
            raw_messages.append(LLMMessage(role=LLMRole.SYSTEM, content=system_prompt))

        for ev in events:
            if ev.type == SessionEventType.USER_MESSAGE:
                raw_messages.append(LLMMessage(role=LLMRole.USER, content=ev.payload.get("text", "")))
            elif ev.type == SessionEventType.ASSISTANT_MESSAGE:
                raw_messages.append(
                    LLMMessage(
                        role=LLMRole.ASSISTANT,
                        content=ev.payload.get("text", ""),
                        tool_calls=ev.payload.get("tool_calls"),
                    )
                )
            elif ev.type == SessionEventType.TOOL_RESULT:
                raw_messages.append(
                    LLMMessage(
                        role=LLMRole.TOOL,
                        name=ev.payload.get("name"),
                        tool_call_id=ev.payload.get("tool_call_id"),
                        content=ev.payload.get("result", {}).get("output")
                        or str(ev.payload.get("result", {}).get("error")),
                    )
                )

        if len(raw_messages) <= max_messages:
            return raw_messages

        # Sliding window: keep system prompt (index 0) + last (max_messages - 1)
        system_msg = raw_messages[0] if raw_messages and raw_messages[0].role == LLMRole.SYSTEM else None
        non_system = [m for m in raw_messages if m.role != LLMRole.SYSTEM]
        trimmed = non_system[-(max_messages - 1) :]
        return ([system_msg] if system_msg else []) + trimmed
```
