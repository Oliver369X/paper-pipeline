"""paper-web / server_cli."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from paper_pipeline import server_cli


def test_server_cli_main() -> None:
    assert callable(server_cli.main)


@patch("paper_pipeline.server_cli.uvicorn.run")
def test_server_cli_invokes_uvicorn(mock_run: MagicMock) -> None:
    with patch("sys.argv", ["paper-web", "--host", "0.0.0.0", "--port", "9000"]):
        server_cli.main()
    mock_run.assert_called_once()
    call_kw = mock_run.call_args[1]
    assert call_kw["host"] == "0.0.0.0"
    assert call_kw["port"] == 9000
    assert call_kw["reload"] is False
