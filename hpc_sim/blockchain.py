#!/usr/bin/env python3
# MultiCoin: A Multi-Mode Educational Blockchain Tool
#
# This script can be run in three different ways:
# 1. No arguments (`python3 blockchain.py`): Runs a simple, original demo.
# 2. `simulate` command (`python3 blockchain.py simulate`): Runs a currency simulation.
# 3. CLI commands (`notarize`, `mine`, etc.): Acts as a persistent file notary tool.

import sys

# --- Version Check ---
# Enforce a minimum Python version to ensure compatibility.
MIN_PYTHON_VERSION = (3, 6)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(
        "Python %s.%s or newer is required to run this tool."
        % MIN_PYTHON_VERSION
    )

import argparse
import hashlib
import os
import pickle
import subprocess
import time

# --- Helper Functions ---

def get_git_provenance():
    """Gets the Git remote URL and commit hash of the current repository."""
    try:
        # Get the remote URL
        url_result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True, check=True
        )
        url = url_result.stdout.strip()

        # Get the current commit hash
        hash_result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        commit_hash = hash_result.stdout.strip()

        return {'repo_url': url, 'commit_hash': commit_hash}
    except (subprocess.CalledProcessError, FileNotFoundError):
        # This will happen if not in a git repo or git is not installed.
        return {'repo_url': 'N/A', 'commit_hash': 'N/A'}

def hash_file(filename):
    """Calculates the SHA-256 hash of a file."""
    if not os.path.exists(filename):
        print(f"Error: File not found at '{filename}'")
        return None
    hasher = hashlib.sha256()
    try:
        with open(filename, 'rb') as f:
            chunk = f.read(4096)
            while chunk:
                hasher.update(chunk)
                chunk = f.read(4096)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# --- Core Classes (Block and Blockchain) ---
class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Using repr() for a more stable serialization of the transactions dict
        block_string = str(self.index) + str(self.timestamp) + repr(self.transactions) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self, mode='tool', coin_name='MultiCoin'):
        self.pending_transactions = []
        self.chain = []
        self.difficulty = 4
        self.mining_reward = 100
        self.coin_name = coin_name
        # The genesis block is created when the chain is initialized
        self.chain.append(self.create_genesis_block(mode))

    def create_genesis_block(self, mode):
        print(f"Initializing blockchain in '{mode}' mode with currency '{self.coin_name}'...")
        genesis_data = {
            'type': 'genesis',
            'message': f"Genesis Block ({mode} mode)",
            'provenance': get_git_provenance()
        }
        return Block(0, time.time(), genesis_data, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address, custom_reward=None):
        if not self.pending_transactions and (custom_reward is None or custom_reward == 0):
             # Allow mining empty blocks if we are Minting (reward > 0), otherwise skip
             # But wait, if we have pending transactions, we MUST mine them even if reward is 0.
             pass

        if not self.pending_transactions:
            # If no transactions, only proceed if we are force-minting coins (reward > 0)
            if custom_reward is None or custom_reward == 0:
                print("No pending transactions to mine.")
                return False

        print("\n⛏️  Starting the miner...")

        # Determine the reward amount
        reward_amount = custom_reward if custom_reward is not None else self.mining_reward

        transactions_for_new_block = self.pending_transactions[:]

        # Only add a reward transaction if the amount is greater than 0
        if reward_amount > 0:
            reward_transaction = {
                'type': 'reward',
                'recipient': miner_address,
                'amount': reward_amount
            }
            transactions_for_new_block.append(reward_transaction)

        new_block = Block(
            index=self.get_latest_block().index + 1,
            timestamp=time.time(),
            transactions=transactions_for_new_block,
            previous_hash=self.get_latest_block().hash
        )

        self.mine_block(new_block)
        self.chain.append(new_block)
        print(f"🎉 Block #{new_block.index} successfully mined!")
        self.pending_transactions = []
        return True

    def mine_block(self, block):
        prefix = '0' * self.difficulty
        while not block.hash.startswith(prefix):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Proof-of-Work successful! Nonce: {block.nonce}")

    def find_hash(self, file_hash):
        for block in self.chain:
            if isinstance(block.transactions, list):
                for tx in block.transactions:
                    if tx.get('type') == 'notarization' and tx.get('file_hash') == file_hash:
                        return block, tx
        return None, None

    def calculate_balance(self, address):
        balance = 0
        for block in self.chain:
            if not isinstance(block.transactions, list):
                # The genesis block now has a dict, so we handle that
                if isinstance(block.transactions, dict):
                    continue
                continue
            for tx in block.transactions:
                if not isinstance(tx, dict):
                    continue
                if tx.get('type') == 'reward' and tx.get('recipient') == address:
                    balance += tx.get('amount', 0)
                if tx.get('sender') == address:
                    balance -= tx.get('amount', 0)
                if tx.get('recipient') == address and tx.get('type') != 'reward':
                    balance += tx.get('amount', 0)
        return balance

    def print_chain(self):
        print(f"\n--- ⛓️  {self.coin_name} Blockchain ⛓️  ---")
        for block in self.chain:
            print(f"Index: {block.index}")
            print(f"Timestamp: {time.ctime(block.timestamp)}")
            print("Transactions:")

            # Handle Genesis block with provenance
            if isinstance(block.transactions, dict) and block.transactions.get('type') == 'genesis':
                prov = block.transactions.get('provenance', {})
                print(f"  - {block.transactions.get('message')}")
                print("    - Provenance:")
                print(f"      - Repo URL: {prov.get('repo_url', 'N/A')}")
                print(f"      - Commit Hash: {prov.get('commit_hash', 'N/A')}")

            # Handle regular transaction blocks
            elif isinstance(block.transactions, list):
                for tx in block.transactions:
                    if isinstance(tx, dict):
                        if tx.get('type') == 'notarization':
                            print(f"  - [Notary] Owner: {tx['owner']}, File: {tx['filename']}, Hash: {tx['file_hash'][:10]}...")
                        elif tx.get('type') == 'reward':
                            print(f"  - [Reward] To: {tx['recipient']}, Amount: {tx['amount']} {self.coin_name}")
                        else:
                            print(f"  - [Currency] From: {tx['sender']}, To: {tx['recipient']}, Amount: {tx['amount']}")
                    else:
                        print(f"  - {tx}")
            else:
                print(f"  - {block.transactions}")

            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print(f"Nonce: {block.nonce}")
            print("-" * 40)


# --- Persistence Functions ---
def save_blockchain(blockchain, filename):
    with open(filename, 'wb') as f:
        pickle.dump(blockchain, f)
    print(f"\nBlockchain state saved to '{filename}'")

def load_blockchain(filename, coin_name):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return Blockchain(mode='tool', coin_name=coin_name)

# --- Different Workflow Functions ---
def run_original_demo():
    print("--- Running Original Simple Demo ---")
    bc = Blockchain(mode='demo')
    print("\nMining block 1...")
    bc.add_transaction("Transaction Data 1")
    bc.mine_pending_transactions("MinerA")
    bc.print_chain()

def run_simulation_demo():
    print("--- Running MultiCoin Currency Simulation ---")
    gemini_coin = Blockchain(mode='simulate', coin_name='SimCoin')
    print("\n--- Round 1 ---")
    gemini_coin.add_transaction({'sender': 'Alice', 'recipient': 'Bob', 'amount': 50})
    gemini_coin.mine_pending_transactions(miner_address="MinerX")
    print("\n--- Final Balances ---")
    for person in ["Alice", "Bob", "MinerX"]:
        bal = gemini_coin.calculate_balance(person)
        print(f"Balance for {person}: {bal} {gemini_coin.coin_name}")

def run_self_verify():
    """Checks the integrity of the script itself against a trusted hash."""
    print("--- Verifying Script Integrity ---")
    trusted_hash_file = 'trusted_hash.txt'

    # 1. Read the trusted hash from the file.
    try:
        with open(trusted_hash_file) as f:
            # The file format from sha256sum is "HASH  FILENAME", so we split and take the first part.
            trusted_hash = f.read().split()[0]
    except FileNotFoundError:
        print(f"❌ Error: Trusted hash file not found at '{trusted_hash_file}'.")
        print("Cannot verify script integrity.")
        return
    except IndexError:
        print(f"❌ Error: Trusted hash file '{trusted_hash_file}' is empty or malformed.")
        return

    # 2. Calculate the current hash of the running script.
    # __file__ is a special Python variable that holds the path to the current script.
    current_script_hash = hash_file(__file__)

    print(f"Trusted Hash (from file): {trusted_hash}")
    print(f"Current Hash (of running script): {current_script_hash}")

    # 3. Compare and report the result.
    if trusted_hash == current_script_hash:
        print("\n✅ Verification Successful! The script is authentic and has not been modified.")
    else:
        print("\n🚨 WARNING: Verification Failed! The script may have been tampered with.")

# --- Main CLI Function ---
def main():
    if len(sys.argv) == 1:
        run_original_demo()
        return

    parser = argparse.ArgumentParser(
        description='''MultiCoin: A Multi-Mode Educational Blockchain Tool.
This tool demonstrates blockchain concepts through three distinct modes of operation.''',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
--- EXAMPLES ---

**1. Default Mode (Simple Demo):**
   Shows the most basic blockchain concepts. Runs in-memory and does not save data.
   $ ./blockchain.py

**2. Simulation Mode (Currency Simulation):**
   Demonstrates a simple cryptocurrency. Also runs in-memory.
   $ ./blockchain.py simulate

**3. CLI Tool Mode (A Practical Workflow):**
   Use the tool as a persistent file notary. This mode saves its data.
   (First, make the script executable: chmod +x blockchain.py)

   # Notarize a file on the default chain (geminicoin.dat)
   $ ./blockchain.py notarize --owner "$USER" --file my_art.txt

   # Mine a block to add the notarization to the chain
   $ ./blockchain.py mine

   # Check your balance (you just got a mining reward!)
   $ ./blockchain.py balance --address "$USER"

**Advanced CLI Usage (Working with Multiple Chains):**

   # Create and use a NEW chain for your personal files with a custom currency
   $ ./blockchain.py --chain ivxx_chain.dat --coin-name "ivxx's" notarize --owner "ivxx" --file "my_notes.txt"

   # Mine the first block on your new chain
   $ ./blockchain.py --chain ivxx_chain.dat mine --miner "ivxx"

   # Verify the file on your new chain
   $ ./blockchain.py --chain ivxx_chain.dat verify "my_notes.txt"
'''
    )

    # Global arguments that apply to the CLI Tool Mode
    parser.add_argument('--chain', type=str, default='geminicoin.dat',
                        help='The file name for the blockchain. Allows you to maintain multiple, separate chains. Defaults to geminicoin.dat.')
    parser.add_argument('--coin-name', type=str, default='MultiCoin',
                        help='The name for the currency/reward unit. This is only applied when a new blockchain file is created.')

    subparsers = parser.add_subparsers(dest='command', help='Choose a mode of operation or a command for the CLI tool.')

    # --- Mode Commands ---
    subparsers.add_parser('simulate', help='Run the non-persistent MultiCoin currency simulation.')
    subparsers.add_parser('self-verify', help='Verify the integrity of the blockchain.py script itself.')

    # --- CLI Tool Commands ---
    parser_notarize = subparsers.add_parser('notarize', help='(CLI Tool) Add a file to the mempool for notarization.')
    parser_notarize.add_argument('--owner', type=str, required=True, help='The name of the file owner.')
    parser_notarize.add_argument('--file', type=str, required=True, dest='filepath', help='The path to the file to notarize.')

    parser_mine = subparsers.add_parser('mine', help='(CLI Tool) Mine a new block with all pending transactions.')
    parser_mine.add_argument('--miner', type=str, dest='address', default=os.environ.get('USER', 'local_miner'),
                             help='The address to receive the mining reward (defaults to your system username).')
    parser_mine.add_argument('--reward', type=int, default=None, help='Override the default mining reward (use 0 to disable inflation).')

    parser_verify = subparsers.add_parser('verify', help='(CLI Tool) Verify a file by checking its hash against the blockchain.')
    parser_verify.add_argument('filepath', type=str, help='The path to the file to verify.')

    parser_stats = subparsers.add_parser('stats', help='(CLI Tool) Print blockchain statistics in JSON format.')

    parser_print = subparsers.add_parser('print', help='(CLI Tool) Print the entire blockchain.')

    parser_balance = subparsers.add_parser('balance', help='(CLI Tool) Calculate and show the balance of an address.')
    parser_balance.add_argument('--address', type=str, required=True, help='The address to check the balance for.')

    parser_transfer = subparsers.add_parser('transfer', help='(CLI Tool) Transfer coins from one address to another.')
    parser_transfer.add_argument('--from', type=str, required=True, dest='sender', help='The address sending the coins.')
    parser_transfer.add_argument('--to', type=str, required=True, dest='recipient', help='The address receiving the coins.')
    parser_transfer.add_argument('--amount', type=int, required=True, help='The amount of coins to transfer.')

    # Manually handle parsing to allow global args before commands
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'simulate':
        run_simulation_demo()
        return

    if args.command == 'self-verify':
        run_self_verify()
        return

    # For CLI tool commands, load the specified chain
    gemini_coin = load_blockchain(args.chain, args.coin_name)

    if args.command == 'notarize':
        file_hash = hash_file(args.filepath)
        if file_hash:
            gemini_coin.add_transaction({
                'type': 'notarization', 'owner': args.owner, 'file_hash': file_hash,
                'filename': os.path.basename(args.filepath), 'timestamp': time.time()
            })
            print(f"✅ Notarization for '{args.filepath}' added to the mempool.")
    elif args.command == 'mine':
        gemini_coin.mine_pending_transactions(args.address, custom_reward=args.reward)
    elif args.command == 'verify':
        file_hash = hash_file(args.filepath)
        if file_hash:
            block, tx = gemini_coin.find_hash(file_hash)
            if block:
                print(f"\n--- Verification Successful!---\n✅ File hash found on the blockchain in Block #{block.index}.")
            else:
                print("\n--- Verification Failed---\n❌ File hash not found in the blockchain.")
    elif args.command == 'stats':
        tx_count = sum(len(b.transactions) if isinstance(b.transactions, list) else 1 for b in gemini_coin.chain)
        print(f'{{"height": {len(gemini_coin.chain)}, "tx_count": {tx_count}, "last_hash": "{gemini_coin.chain[-1].hash}"}}')
    elif args.command == 'print':
        gemini_coin.print_chain()
    elif args.command == 'balance':
        balance = gemini_coin.calculate_balance(args.address)
        print(f"\n💰 The balance for address '{args.address}' is: {balance} {gemini_coin.coin_name}")
    elif args.command == 'transfer':
        sender_balance = gemini_coin.calculate_balance(args.sender)
        if sender_balance >= args.amount:
            gemini_coin.add_transaction({
                'type': 'currency',
                'sender': args.sender,
                'recipient': args.recipient,
                'amount': args.amount,
                'timestamp': time.time()
            })
            print(f"✅ {args.amount} {gemini_coin.coin_name} transferred from {args.sender} to {args.recipient}. A miner needs to mine this transaction.")
        else:
            print(f"❌ Insufficient funds. {args.sender} has {sender_balance} {gemini_coin.coin_name}, but tried to send {args.amount}.")

    save_blockchain(gemini_coin, args.chain)



if __name__ == "__main__":
    main()
