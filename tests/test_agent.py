import io
import runpy
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

AGENT_PATH = str(Path(__file__).parent.parent / "agent.py")


# --- CLI guard tests (no API calls needed) ---

def test_no_args_exits_with_code_1():
    result = subprocess.run(
        [sys.executable, AGENT_PATH],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_no_args_prints_usage_to_stdout():
    result = subprocess.run(
        [sys.executable, AGENT_PATH],
        capture_output=True,
        text=True,
    )
    assert "Usage:" in result.stdout
    assert "agent.py" in result.stdout


# --- Happy-path tests (LangChain mocked) ---

def _run_with_mocks(argv, mock_output="Answer."):
    """Execute agent.py in-process with LangChain fully mocked."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"output": mock_output}
    stdout = io.StringIO()

    with (
        patch("sys.argv", argv),
        patch("langchain_community.utilities.GoogleSerperAPIWrapper"),
        patch("langchain_openai.ChatOpenAI"),
        patch("langchain_classic.agents.initialize_agent", return_value=mock_agent),
        redirect_stdout(stdout),
    ):
        runpy.run_path(AGENT_PATH)

    return mock_agent, stdout.getvalue()


def test_single_word_query_invokes_agent():
    mock_agent, _ = _run_with_mocks(["agent.py", "python"])
    mock_agent.invoke.assert_called_once()


def test_multi_word_query_is_joined_with_spaces():
    mock_agent, _ = _run_with_mocks(["agent.py", "latest", "python", "version"])
    input_text = mock_agent.invoke.call_args[0][0]["input"]
    assert "latest python version" in input_text


def test_query_prompt_requests_concise_answer():
    mock_agent, _ = _run_with_mocks(["agent.py", "test"])
    input_text = mock_agent.invoke.call_args[0][0]["input"]
    assert "concise" in input_text.lower()


def test_agent_output_is_printed_to_stdout():
    _, output = _run_with_mocks(["agent.py", "test"], mock_output="Short answer here.")
    assert "Short answer here." in output
