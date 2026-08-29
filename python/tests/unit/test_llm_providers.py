from atomos.llm.providers.deepseek import DeepSeekAdapter
from atomos.llm.providers.openai import OpenAIAdapter


def test_deepseek_adapter_initialization() -> None:
    adapter = DeepSeekAdapter(model="deepseek-coder", api_key="sk-test-key")
    assert adapter.model == "deepseek-coder"
    assert adapter.api_key == "sk-test-key"
    assert adapter.base_url == "https://api.deepseek.com/v1"


def test_openai_adapter_cloud_initialization() -> None:
    adapter = OpenAIAdapter(model="gpt-4o", api_key="sk-openai-key")
    assert adapter.model == "gpt-4o"
    assert adapter.api_key == "sk-openai-key"
    assert adapter.base_url == "https://api.openai.com/v1"
    assert not adapter.is_local


def test_openai_adapter_local_initialization() -> None:
    adapter = OpenAIAdapter(model="deepseek-r1:7b", is_local=True)
    assert adapter.model == "deepseek-r1:7b"
    assert adapter.is_local
    assert adapter.base_url == "http://localhost:11434/v1"
    assert adapter.api_key == "local-no-key"
