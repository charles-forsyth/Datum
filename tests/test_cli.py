import sys

import pytest

from datum.cli import main


def test_cli_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['datum', '--help'])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "Datum: Professional Blockchain & Data Integrity Tool" in captured.out
    # Updated expectation based on simplified help text
    assert "Detailed help available online or via README" in captured.out
