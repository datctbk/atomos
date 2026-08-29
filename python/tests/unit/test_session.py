from pathlib import Path

from atomos.core.session import SessionEventType, SessionStore


def test_session_creation_and_persistence(tmp_path: Path) -> None:
    store = SessionStore(base_dir=tmp_path)
    session = store.create_session("sess_123")

    assert session.session_id == "sess_123"
    assert session.get_next_seq() == 1

    e1 = session.append_event(SessionEventType.USER_MESSAGE, {"text": "hello"})
    assert e1.seq == 1
    assert e1.type == SessionEventType.USER_MESSAGE

    e2 = session.append_event(SessionEventType.ASSISTANT_MESSAGE, {"text": "hi there"})
    assert e2.seq == 2
    assert len(session.events) == 2

    session.close()

    # Recovery from disk
    recovered_session = store.get_or_load_session("sess_123")
    assert len(recovered_session.events) == 2
    assert recovered_session.events[0].payload["text"] == "hello"
    assert recovered_session.events[1].payload["text"] == "hi there"
    assert recovered_session.get_next_seq() == 3
