from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from atomos.agent.loop import ContextCompactor
from atomos.core.session import SessionEvent, SessionEventType
from atomos.llm.base import LLMRole


@st.composite
def random_session_events(draw: Any) -> list[SessionEvent]:
    num_events = draw(st.integers(min_value=5, max_value=40))
    events: list[SessionEvent] = []
    for seq in range(1, num_events + 1):
        ev_type = draw(st.sampled_from([SessionEventType.USER_MESSAGE, SessionEventType.ASSISTANT_MESSAGE]))
        text_content = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=10))
        events.append(SessionEvent(session_id="pbt_sess", seq=seq, type=ev_type, payload={"text": text_content}))
    return events


@given(
    events=random_session_events(),
    max_budget=st.integers(min_value=4, max_value=20),
    system_text=st.text(min_size=1, max_size=15),
)
def test_prop_context_compaction_invariants(
    events: list[SessionEvent], max_budget: int, system_text: str
) -> None:
    """PBT-01: Compaction strictly enforces budget limit and preserves the initial system prompt."""
    compacted = ContextCompactor.compact_history(
        events=events,
        max_messages=max_budget,
        system_prompt=system_text,
    )

    # 1. System prompt is preserved at index 0
    assert len(compacted) >= 1
    assert compacted[0].role == LLMRole.SYSTEM
    assert compacted[0].content == system_text

    # 2. Total messages <= max_budget
    assert len(compacted) <= max_budget
