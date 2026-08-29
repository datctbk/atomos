import logging

from atomos.core.logging import RedactionFilter, get_logger


def test_redaction_filter_masks_secrets() -> None:
    logger = get_logger("test_redact")
    assert any(isinstance(f, RedactionFilter) for f in logger.filters)

    filter_obj = RedactionFilter()

    record1 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Connecting with key sk-1234567890abcdef1234567890 to API",
        args=(),
        exc_info=None,
    )
    filter_obj.filter(record1)
    assert record1.msg == "Connecting with key ***MASKED*** to API"

    record2 = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Auth header: %s",
        args=("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token123",),
        exc_info=None,
    )
    filter_obj.filter(record2)
    assert record2.args == ("***MASKED***",)
