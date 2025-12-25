import json
import os
import time
from typing import Optional

from datum.config import settings
from datum.schemas import Block, Provenance, Transaction
from datum.utils import get_git_provenance
from datum.wallet import verify_signature


class Blockchain:
    def __init__(self, chain_file: Optional[str] = None, genesis_message: Optional[str] = None):
        self.chain_file = chain_file or settings.chain_file
        self.genesis_message = genesis_message or settings.genesis_message
        self.pending_transactions: list[Transaction] = []
        self.chain: list[Block] = []
        self.difficulty = settings.difficulty
        self.mining_reward = settings.mining_reward

        if os.path.exists(self.chain_file):
            self.load_chain()
        else:
            self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block in the chain with premine and custom message."""
        prov_data = get_git_provenance()
        provenance = Provenance(
            repo_url=prov_data.get('repo_url', 'N/A'),
            commit_hash=prov_data.get('commit_hash', 'N/A')
        )

        transactions = []

        # 1. The Genesis Metadata Transaction
        genesis_tx = Transaction(
            type="genesis",
            message=self.genesis_message,
            provenance=provenance
        )
        transactions.append(genesis_tx)

        # 2. Premine Transactions
        for address, amount in settings.premine.items():
            premine_tx = Transaction(
                type="currency",
                sender="Genesis",
                recipient=address,
                amount=float(amount),
                timestamp=time.time()
            )
            transactions.append(premine_tx)

        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=transactions,
            previous_hash="0",
            hash="" # Will be calculated
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        self.save_chain()

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Adds a transaction to the mempool.
        Returns True if accepted, False if rejected (e.g. invalid signature).
        """
        # Cryptographic Verification
        if transaction.signature and transaction.public_key:
            # 1. Calculate the hash of the data that was signed
            data_hash = transaction.calculate_data_hash()

            # 2. Verify the signature against that hash
            is_valid = verify_signature(data_hash, transaction.signature, transaction.public_key)

            if not is_valid:
                print("❌ Transaction Rejected: Invalid Signature.")
                return False

            # TODO: Future - Verify sender address matches public key derivation

        self.pending_transactions.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address: str) -> bool:
        if not self.pending_transactions:
            return False

        reward_tx = Transaction(
            type="reward",
            recipient=miner_address,
            amount=self.mining_reward,
            timestamp=time.time()
        )

        # Create new block with pending txs + reward
        transactions_to_mine = self.pending_transactions[:] + [reward_tx]

        last_block = self.get_latest_block()
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            transactions=transactions_to_mine,
            previous_hash=last_block.hash,
            hash=""
        )

        self.mine_block(new_block)
        self.chain.append(new_block)

        # Reset pending transactions and save
        self.pending_transactions = []
        self.save_chain()
        return True

    def mine_block(self, block: Block):
        """Performs Proof-of-Work"""
        prefix = '0' * self.difficulty
        while not block.hash.startswith(prefix):
            block.nonce += 1
            block.hash = block.calculate_hash()

    def calculate_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def find_transaction_by_file_hash(self, file_hash: str) -> Optional[tuple[Block, Transaction]]:
        for block in self.chain:
            for tx in block.transactions:
                if tx.type == 'notarization' and tx.file_hash == file_hash:
                    return block, tx
        return None

    def find_transactions_by_filename(self, filename: str) -> list[tuple[Block, Transaction]]:
        """Finds all notarization transactions for a given filename."""
        results = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.type == 'notarization' and tx.filename == filename:
                    results.append((block, tx))
        return results

    def save_chain(self):
        """Saves the blockchain and pending transactions to a JSON file."""
        data = {
            "chain": [block.model_dump() for block in self.chain],
            "pending_transactions": [tx.model_dump() for tx in self.pending_transactions]
        }
        with open(self.chain_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load_chain(self):
        """Loads the blockchain from a JSON file."""
        try:
            with open(self.chain_file) as f:
                data = json.load(f)
                # Handle legacy or simple list format if migration needed (optional, but good for safety)
                if isinstance(data, list):
                    # Old format or simple chain list
                    self.chain = [Block.model_validate(b) for b in data]
                    self.pending_transactions = []
                elif isinstance(data, dict):
                    self.chain = [Block.model_validate(b) for b in data.get("chain", [])]
                    self.pending_transactions = [
                        Transaction.model_validate(t) for t in data.get("pending_transactions", [])
                    ]
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Error loading chain from {self.chain_file}. Starting fresh.")
            self.create_genesis_block()
