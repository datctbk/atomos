from pathlib import Path

import pytest

from atomos.llm.base import BaseLLMAdapter
from atomos.llm.mock import MockLLMAdapter
from atomos.sdk.client import AtomosClient


@pytest.mark.asyncio
async def test_sdk_client_context_manager_and_chat(tmp_path: Path) -> None:
    async with AtomosClient(
        workspace=tmp_path,
        sessions_dir=tmp_path,
        is_local=True,
    ) as client:
        assert client.context is not None
        assert client.session is not None
        assert client.loop is not None

        # Override with Mock adapter for offline testing
        mock_adapter = MockLLMAdapter(canned_text="Atomos SDK online")
        client.context.provide(BaseLLMAdapter, mock_adapter)
        client.loop.llm_adapter = mock_adapter

        tokens = []
        async for token in client.chat("Hello"):
            tokens.append(token)

        assert "".join(tokens) == "Atomos SDK online"

    # Verify cleanup on exit
    assert client.context is None
    assert client.session is None
    assert client.loop is None
