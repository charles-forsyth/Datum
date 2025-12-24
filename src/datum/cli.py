import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from datum.config import settings
from datum.core import Blockchain
from datum.demos.hpc import run_hpc_demo
from datum.schemas import Transaction
from datum.utils import hash_file

# Initialize Rich Console
console = Console()

def get_blockchain(chain_file=None) -> Blockchain:
    """Load blockchain, preferring CLI arg over config."""
    path = chain_file or settings.chain_file
    return Blockchain(chain_file=path)

def cmd_info(args):
    """Display information about the current configuration."""
    table = Table(title="Datum Configuration", box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    # Use the resolved chain file from args or settings
    chain_file = args.chain or settings.chain_file

    table.add_row("App Name", settings.app_name)
    table.add_row("Chain File", chain_file)
    table.add_row("Coin Name", args.coin_name)
    table.add_row("Miner Address", settings.miner_address)
    table.add_row("Difficulty", str(settings.difficulty))
    table.add_row("Mining Reward", str(settings.mining_reward))

    console.print(Panel(table, title="System Info", border_style="blue"))

def cmd_notarize(args):
    """Notarize a file."""
    file_path = Path(args.file)
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found.[/red]")
        sys.exit(1)

    file_hash = hash_file(str(file_path))
    if not file_hash:
        console.print("[red]Error calculating file hash.[/red]")
        sys.exit(1)

    bc = get_blockchain(args.chain)
    tx = Transaction(
        type="notarization",
        owner=args.owner,
        file_hash=file_hash,
        filename=file_path.name
    )

    bc.add_transaction(tx)
    bc.save_chain()

    console.print(f"[green]✅ Notarization for '{file_path.name}' added to pending pool.[/green]")
    console.print(f"File Hash: [bold cyan]{file_hash}[/bold cyan]")
    console.print("[yellow]Run 'datum mine' to confirm this transaction.[/yellow]")

def cmd_mine(args):
    """Mine a block."""
    bc = get_blockchain(args.chain)
    miner = args.miner or settings.miner_address

    if not bc.pending_transactions:
        console.print("[yellow]No pending transactions to mine.[/yellow]")
        return

    with console.status(f"[bold green]Mining block for {miner}...[/bold green]"):
        success = bc.mine_pending_transactions(miner)

    if success:
        last_block = bc.get_latest_block()
        console.print(Panel(f"""[green]🎉 Block #{last_block.index} successfully mined![/green]
Hash: [dim]{last_block.hash}[/dim]
Nonce: {last_block.nonce}
Transactions: {len(last_block.transactions)}""", title="Mining Success", border_style="green"))
    else:
        console.print("[red]Mining failed.[/red]")

def cmd_balance(args):
    """Check balance."""
    bc = get_blockchain(args.chain)
    bal = bc.calculate_balance(args.address)
    console.print(Panel(
        f"Address: [bold]{args.address}[/bold]\nBalance: [bold green]{bal} {args.coin_name}[/bold green]",
        title="Wallet Balance"
    ))

def cmd_transfer(args):
    """Transfer currency between addresses."""
    bc = get_blockchain(args.chain)
    sender_bal = bc.calculate_balance(args.sender)

    if sender_bal < args.amount:
        console.print("[red]❌ Insufficient funds.[/red]")
        console.print(f"Sender: {args.sender}")
        console.print(f"Balance: {sender_bal} {args.coin_name}")
        console.print(f"Required: {args.amount} {args.coin_name}")
        sys.exit(1)

    tx = Transaction(
        type="currency",
        sender=args.sender,
        recipient=args.recipient,
        amount=args.amount,
        timestamp=time.time()
    )

    bc.add_transaction(tx)
    bc.save_chain()

    console.print(Panel(f"""[green]✅ Transaction created![/green]
From: {args.sender}
To: {args.recipient}
Amount: {args.amount} {args.coin_name}""", title="Transfer Queued", border_style="green"))
    console.print("[yellow]Run 'datum mine' to process this transfer.[/yellow]")

def cmd_show(args):
    """Show the blockchain."""
    bc = get_blockchain(args.chain)
    table = Table(title=f"Datum Blockchain (Last {args.n} Blocks)")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Transactions", style="white")
    table.add_column("Hash", style="dim green")

    # Show last n blocks
    for block in bc.chain[-args.n:]:
        tx_summary = f"{len(block.transactions)} txs"
        if len(block.transactions) > 0:
            types = [t.type for t in block.transactions]
            unique_types = sorted(list(set(types)))
            tx_summary += f" ({', '.join(unique_types)})"

        table.add_row(
            str(block.index),
            str(block.timestamp),
            tx_summary,
            block.hash[:10] + "..."
        )

    console.print(table)

def cmd_verify(args):
    """Verify a file."""
    file_path = Path(args.file)
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found.[/red]")
        sys.exit(1)

    file_hash = hash_file(str(file_path))
    bc = get_blockchain(args.chain)

    result = bc.find_transaction_by_file_hash(file_hash)
    if result:
        block, tx = result
        console.print(Panel(f"""[green]✅ File Verified![/green]
File: {tx.filename}
Owner: {tx.owner}
Block: #{block.index}
Date: {tx.timestamp}
Hash: {tx.file_hash}""", title="Verification Result", border_style="green"))
    else:
        console.print(Panel(
            f"[red]❌ File not found in blockchain.[/red]\nHash: {file_hash}",
            title="Verification Failed",
            border_style="red"
        ))

def cmd_demo(args):
    """Run an interactive demo."""
    if args.type == "hpc":
        run_hpc_demo()
    else:
        console.print("[red]Unknown demo type.[/red]")

class RichHelpFormatter(argparse.RawTextHelpFormatter):
    """A custom formatter that adds a bit of style to help output."""
    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)
        return ", ".join(action.option_strings)

def main():
    parser = argparse.ArgumentParser(
        prog="datum",
        description="Datum: Professional Blockchain & Data Integrity Tool",
        formatter_class=RichHelpFormatter,
        add_help=False, # We handle help manually for better styling
        epilog='''
--------------------------------------------------------------------------------
🔎 EXAMPLES & WORKFLOWS
--------------------------------------------------------------------------------

1. Start by checking the system info:
   $ datum info

2. Notarize a critical document (Proof of Existence):
   $ datum notarize --owner "Dr. Vance" --file ./research_data.pdf
   > This adds the file's hash to the "mempool" (pending transactions).

3. Confirm the transaction by mining a block:
   $ datum mine --miner "Lab_Workstation_1"
   > This performs the Proof-of-Work and permanently saves the transaction.

4. Verify the document later (Integrity Check):
   $ datum verify --file ./research_data.pdf
   > Datum will calculate the hash and search the ledger for a match.

5. Check your Mining Rewards:
   $ datum balance --address "Lab_Workstation_1"

6. Transfer funds (Pay for Compute):
   $ datum transfer --from "Lab_Workstation_1" --to "HPC_Scheduler" --amount 50

7. Run the HPC Simulation Demo:
   $ datum demo hpc

--------------------------------------------------------------------------------
'''
    )

    # Global Arguments (Must come before subcommands)
    parser.add_argument('--chain', type=str, default=None, help='Blockchain file to use (overrides config)')
    parser.add_argument('--coin-name', type=str, default='Datum', help='Name of the currency unit (display only)')
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')

    subparsers = parser.add_subparsers(dest='command', help='Available commands', metavar='COMMAND')

    # INFO
    parser_info = subparsers.add_parser(
        'info', help='Display configuration and status', formatter_class=RichHelpFormatter
    )
    parser_info.set_defaults(func=cmd_info)

    # NOTARIZE
    parser_notarize = subparsers.add_parser(
        'notarize', help='Notarize a file (add to pending pool)', formatter_class=RichHelpFormatter
    )
    parser_notarize.add_argument('--owner', type=str, required=True, help='The name of the file owner (e.g., "Alice")')
    parser_notarize.add_argument('--file', type=str, required=True, help='Path to the file to notarize')
    parser_notarize.set_defaults(func=cmd_notarize)

    # MINE
    parser_mine = subparsers.add_parser(
        'mine', help='Mine a new block to confirm pending transactions', formatter_class=RichHelpFormatter
    )
    parser_mine.add_argument(
        '--miner', type=str, default=None, help='Address to receive mining rewards (defaults to config)'
    )
    parser_mine.set_defaults(func=cmd_mine)

    # BALANCE
    parser_balance = subparsers.add_parser(
        'balance', help='Check the balance of an address', formatter_class=RichHelpFormatter
    )
    parser_balance.add_argument('--address', type=str, required=True, help='The address to check')
    parser_balance.set_defaults(func=cmd_balance)

    # TRANSFER
    parser_transfer = subparsers.add_parser(
        'transfer', help='Transfer currency between addresses', formatter_class=RichHelpFormatter
    )
    parser_transfer.add_argument('--from', dest='sender', required=True, help='Address sending funds')
    parser_transfer.add_argument('--to', dest='recipient', required=True, help='Address receiving funds')
    parser_transfer.add_argument('--amount', type=float, required=True, help='Amount to transfer')
    parser_transfer.set_defaults(func=cmd_transfer)

    # SHOW
    parser_show = subparsers.add_parser('show', help='Show the blockchain', formatter_class=RichHelpFormatter)
    parser_show.add_argument('--n', type=int, default=5, help='Number of recent blocks to show')
    parser_show.set_defaults(func=cmd_show)

    # VERIFY
    parser_verify = subparsers.add_parser(
        'verify', help='Verify if a file is in the blockchain', formatter_class=RichHelpFormatter
    )
    parser_verify.add_argument('--file', type=str, required=True, help='Path to the file to verify')
    parser_verify.set_defaults(func=cmd_verify)

    # DEMO
    parser_demo = subparsers.add_parser('demo', help='Run interactive demos', formatter_class=RichHelpFormatter)
    parser_demo.add_argument('type', choices=['hpc'], help='The type of demo to run')
    parser_demo.set_defaults(func=cmd_demo)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
