
import pytest

from datum.config import Settings
from datum.core import Blockchain


@pytest.fixture
def premine_chain(tmp_path, monkeypatch):
    chain_file = tmp_path / "premine_chain.json"

    # Mock settings with a premine and custom message
    monkeypatch.setenv("DATUM_GENESIS_MESSAGE", "Test Genesis")
    monkeypatch.setenv("DATUM_PREMINE", '{"Alice": 500.0, "Bob": 250.0}')

    # We need to reload settings or just patch the singleton instance logic if we could,
    # but BaseSettings loads env on init.
    # A cleaner way for this test is to modify the global 'settings' object in core.py
    # OR re-instantiate Blockchain which reads 'settings' from 'datum.config'.

    # Let's monkeypatch the settings object imported in datum.core
    from datum import core

    new_settings = Settings()
    new_settings.genesis_message = "Test Genesis"
    new_settings.premine = {"Alice": 500.0, "Bob": 250.0}
    new_settings.chain_file = str(chain_file)

    monkeypatch.setattr(core, 'settings', new_settings)

    return Blockchain(chain_file=str(chain_file))

def test_genesis_message(premine_chain):
    genesis_block = premine_chain.chain[0]
    # The first tx is always the metadata one
    assert genesis_block.transactions[0].type == "genesis"
    assert genesis_block.transactions[0].message == "Test Genesis"

def test_genesis_premine(premine_chain):
    # Check if balances exist immediately
    assert premine_chain.calculate_balance("Alice") == 500.0
    assert premine_chain.calculate_balance("Bob") == 250.0

    # Verify the transactions in block 0
    genesis_block = premine_chain.chain[0]
    # We expect 3 transactions: 1 metadata + 2 allocations
    assert len(genesis_block.transactions) == 3

    # Check specific tx details
    allocations = [tx for tx in genesis_block.transactions if tx.type == "currency"]
    assert len(allocations) == 2
    assert allocations[0].sender == "Genesis"
