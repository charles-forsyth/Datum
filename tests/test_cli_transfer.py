import sys

import pytest

from datum.cli import main
from datum.core import Blockchain
from datum.schemas import Transaction


@pytest.fixture
def funded_chain(tmp_path):
    chain_file = tmp_path / "funded_chain.json"
    bc = Blockchain(chain_file=str(chain_file))
    bc.difficulty = 1
    # Mine a block to fund 'Miner1'
    bc.add_transaction(Transaction(sender="Genesis", recipient="Miner1", amount=0)) # Dummy tx to trigger mine
    bc.mine_pending_transactions("Miner1")
    return str(chain_file)

def test_cli_transfer(capsys, monkeypatch, funded_chain):
    # Miner1 has 100 Datum (mining reward)
    # Transfer 50 to User2
    args = ['datum', '--chain', funded_chain, 'transfer', '--from', 'Miner1', '--to', 'User2', '--amount', '50.0']
    monkeypatch.setattr(sys, 'argv', args)

    # Run transfer command
    # It creates a pending transaction but doesn't return anything, just prints
    try:
        main()
    except SystemExit:
        pass # argparse might exit, but we catch it if it's 0.
             # Actually our main() calls sys.exit(0) only on no args.
             # cmd_transfer doesn't exit unless error.

    captured = capsys.readouterr()
    assert "Transaction created!" in captured.out

    # Verify transaction is pending
    bc = Blockchain(chain_file=funded_chain)
    assert len(bc.pending_transactions) == 1
    assert bc.pending_transactions[0].sender == "Miner1"
    assert bc.pending_transactions[0].amount == 50.0

def test_cli_global_coin_name(capsys, monkeypatch, funded_chain):
    args = ['datum', '--chain', funded_chain, '--coin-name', 'HPCCredit', 'balance', '--address', 'Miner1']
    monkeypatch.setattr(sys, 'argv', args)

    main()
    captured = capsys.readouterr()
    assert "100.0 HPCCredit" in captured.out
