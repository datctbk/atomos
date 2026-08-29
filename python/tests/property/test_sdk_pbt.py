import pytest
from hypothesis import given
from hypothesis import strategies as st

from atomos.sdk.client import AtomosClient


@given(
    model_name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz-0123456789", min_size=2, max_size=15),
    is_local_flag=st.booleans(),
    system_text=st.text(min_size=0, max_size=20),
)
@pytest.mark.asyncio
async def test_prop_sdk_lifecycle_cleanup(
    tmp_path_factory: pytest.TempPathFactory,
    model_name: str,
    is_local_flag: bool,
    system_text: str,
) -> None:
    """PBT-01: Verifies SDK lifecycle leaves zero dangling state across randomized configurations."""
    test_dir = tmp_path_factory.mktemp("sdk_pbt")
    client = AtomosClient(
        workspace=test_dir,
        sessions_dir=test_dir,
        model=model_name,
        is_local=is_local_flag,
        system_prompt=system_text,
    )

    async with client:
        assert client.context is not None
        assert client.session is not None
        assert client.loop is not None

    # Guaranteed clean disposal on exit
    assert client.context is None
    assert client.session is None
    assert client.loop is None
