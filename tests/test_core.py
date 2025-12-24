
import pytest

from datum.core import Blockchain
from datum.schemas import Transaction


@pytest.fixture
def clean_blockchain(tmp_path):
    chain_file = tmp_path / "test_chain.json"
    bc = Blockchain(chain_file=str(chain_file))
    return bc

def test_genesis_block(clean_blockchain):
    assert len(clean_blockchain.chain) == 1
    assert clean_blockchain.chain[0].index == 0
    assert clean_blockchain.chain[0].transactions[0].type == "genesis"

def test_add_transaction(clean_blockchain):
    tx = Transaction(sender="Alice", recipient="Bob", amount=10.0)
    clean_blockchain.add_transaction(tx)
    assert len(clean_blockchain.pending_transactions) == 1
    assert clean_blockchain.pending_transactions[0].sender == "Alice"

def test_mining(clean_blockchain):
    tx = Transaction(sender="Alice", recipient="Bob", amount=10.0)
    clean_blockchain.add_transaction(tx)

    # Lower difficulty for test speed
    clean_blockchain.difficulty = 1

    success = clean_blockchain.mine_pending_transactions(miner_address="Miner1")

    assert success is True
    assert len(clean_blockchain.chain) == 2
    assert len(clean_blockchain.pending_transactions) == 0

    # Check reward
    last_block = clean_blockchain.get_latest_block()
    assert last_block.transactions[-1].type == "reward"
    assert last_block.transactions[-1].recipient == "Miner1"

def test_persistence(tmp_path):
    chain_file = tmp_path / "test_persist.json"
    bc1 = Blockchain(chain_file=str(chain_file))
    bc1.difficulty = 1
    bc1.add_transaction(Transaction(sender="A", recipient="B", amount=5))
    bc1.mine_pending_transactions("MinerA")

    # Reload in new instance
    bc2 = Blockchain(chain_file=str(chain_file))
    assert len(bc2.chain) == 2
    assert bc2.chain[-1].hash == bc1.chain[-1].hash
