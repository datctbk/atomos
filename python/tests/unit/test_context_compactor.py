from atomos.agent.loop import ContextCompactor
from atomos.core.session import SessionEvent, SessionEventType
from atomos.llm.base import LLMRole


def test_context_compactor_preserves_system_prompt() -> None:
    events = [
        SessionEvent(session_id="s1", seq=1, type=SessionEventType.USER_MESSAGE, payload={"text": "hi 1"}),
        SessionEvent(session_id="s1", seq=2, type=SessionEventType.ASSISTANT_MESSAGE, payload={"text": "reply 1"}),
        SessionEvent(session_id="s1", seq=3, type=SessionEventType.USER_MESSAGE, payload={"text": "hi 2"}),
        SessionEvent(session_id="s1", seq=4, type=SessionEventType.ASSISTANT_MESSAGE, payload={"text": "reply 2"}),
        SessionEvent(session_id="s1", seq=5, type=SessionEventType.USER_MESSAGE, payload={"text": "hi 3"}),
        SessionEvent(session_id="s1", seq=6, type=SessionEventType.ASSISTANT_MESSAGE, payload={"text": "reply 3"}),
    ]

    # Compact down to max 4 messages (1 system + 3 latest)
    messages = ContextCompactor.compact_history(
        events=events,
        max_messages=4,
        system_prompt="You are Atomos",
    )

    assert len(messages) == 4
    assert messages[0].role == LLMRole.SYSTEM
    assert messages[0].content == "You are Atomos"

    # Should retain the latest 3 messages
    assert messages[1].content == "reply 2"
    assert messages[2].content == "hi 3"
    assert messages[3].content == "reply 3"


def test_context_compactor_within_budget() -> None:
    events = [
        SessionEvent(session_id="s1", seq=1, type=SessionEventType.USER_MESSAGE, payload={"text": "hello"}),
        SessionEvent(session_id="s1", seq=2, type=SessionEventType.ASSISTANT_MESSAGE, payload={"text": "world"}),
    ]

    messages = ContextCompactor.compact_history(
        events=events,
        max_messages=10,
        system_prompt="System instructions",
    )

    assert len(messages) == 3
    assert messages[0].role == LLMRole.SYSTEM
    assert messages[1].role == LLMRole.USER
    assert messages[2].role == LLMRole.ASSISTANT
