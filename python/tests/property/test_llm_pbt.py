import json
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from atomos.llm.base import ToolCallAccumulator, ToolCallFragment


@st.composite
def json_tool_calls(draw: Any) -> tuple[str, str, str]:
    call_id: str = draw(st.uuids()).hex
    func_name: str = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=3, max_size=15))
    args_dict = draw(
        st.dictionaries(
            keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=10),
            values=st.one_of(st.text(max_size=20), st.integers(), st.booleans()),
            max_size=5,
        )
    )
    args_json = json.dumps(args_dict)
    return call_id, func_name, args_json


@given(data=json_tool_calls())
def test_prop_tool_fragment_accumulation(data: tuple[str, str, str]) -> None:
    """PBT-01: Fragmented tool argument chunks reassemble into the exact original payload."""
    call_id, func_name, args_json = data
    accumulator = ToolCallAccumulator()

    # Split JSON into 1 to 4 arbitrary fragments
    chunk_size = max(1, len(args_json) // 3)
    fragments = [args_json[i : i + chunk_size] for i in range(0, len(args_json), chunk_size)]

    for idx, frag in enumerate(fragments):
        accumulator.add_fragment(
            ToolCallFragment(
                index=0,
                id=call_id if idx == 0 else None,
                name=func_name if idx == 0 else None,
                arguments=frag,
            )
        )

    tool_calls = accumulator.get_tool_calls()
    assert len(tool_calls) == 1
    assert tool_calls[0]["id"] == call_id
    assert tool_calls[0]["function"]["name"] == func_name
    assert tool_calls[0]["function"]["arguments"] == args_json
    assert json.loads(tool_calls[0]["function"]["arguments"]) == json.loads(args_json)
