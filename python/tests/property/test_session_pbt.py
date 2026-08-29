from datetime import UTC
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from atomos.core.session import SessionEvent, SessionEventType, SessionStore


@st.composite
def session_events(draw: Any) -> SessionEvent:
    event_id: str = draw(st.uuids()).hex
    session_id: str = draw(st.uuids()).hex
    seq: int = draw(st.integers(min_value=1, max_value=100000))
    event_type: SessionEventType = draw(st.sampled_from(list(SessionEventType)))
    timestamp = draw(st.datetimes(timezones=st.just(UTC)))
    payload = draw(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=15),
            values=st.one_of(st.text(max_size=30), st.integers(), st.booleans(), st.none()),
            max_size=5,
        )
    )
    return SessionEvent(
        id=event_id,
        session_id=session_id,
        seq=seq,
        type=event_type,
        timestamp=timestamp,
        payload=payload,
    )


@given(event=session_events())
def test_prop_session_event_roundtrip(event: SessionEvent) -> None:
    """PBT-01: Serializing and deserializing a SessionEvent must be lossless."""
    serialized = event.model_dump_json()
    deserialized = SessionEvent.model_validate_json(serialized)
    assert deserialized == event


@given(n=st.integers(min_value=1, max_value=25))
def test_prop_session_seq_monotonic(tmp_path_factory: pytest.TempPathFactory, n: int) -> None:
    """PBT-02: Appending N events to a session must yield strictly monotonic sequence numbers."""
    tmp_dir = tmp_path_factory.mktemp("pbt_sess")
    store = SessionStore(base_dir=tmp_dir)
    session = store.create_session()

    for i in range(1, n + 1):
        evt = session.append_event(SessionEventType.USER_MESSAGE, {"step": i})
        assert evt.seq == i

    assert [e.seq for e in session.events] == list(range(1, n + 1))
    session.close()
