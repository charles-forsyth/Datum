import sys

import pytest

from datum.cli import main


def test_cli_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['datum', '--help'])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "Datum: Professional Blockchain & Data Integrity Tool" in captured.out
    assert "🔎 EXAMPLES & WORKFLOWS" in captured.out
    assert "🚀 ADVANCED: MULTI-CHAIN MANAGEMENT" in captured.out
