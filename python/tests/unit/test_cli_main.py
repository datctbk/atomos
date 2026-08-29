import pytest
from typer.testing import CliRunner

from atomos.cli.main import app

runner = CliRunner()


def test_cli_help_flag() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Atomos" in result.stdout
    assert "--local" in result.stdout
    assert "--model" in result.stdout
    assert "--workspace" in result.stdout


def test_cli_missing_api_key_exits_with_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = runner.invoke(app, ["Hello", "-w", "."])
    assert result.exit_code == 1
    assert "Missing API Key" in result.stdout
