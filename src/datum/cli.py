from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from datum.config import settings
from datum.core import Blockchain
from datum.schemas import Transaction
from datum.utils import hash_file

app = typer.Typer(help="Datum: Professional Blockchain & Data Integrity Tool")
console = Console()

def get_blockchain() -> Blockchain:
    return Blockchain()

@app.command()
def info():
    """Display information about the current configuration."""
    table = Table(title="Datum Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("App Name", settings.app_name)
    table.add_row("Chain File", settings.chain_file)
    table.add_row("Miner Address", settings.miner_address)
    table.add_row("Difficulty", str(settings.difficulty))
    table.add_row("Mining Reward", str(settings.mining_reward))

    console.print(table)

@app.command()
def notarize(
    file_path: Path = typer.Argument(..., help="Path to the file to notarize"),
    owner: str = typer.Option(..., help="Owner of the file"),
):
    """Notarize a file by adding its hash to the pending transaction pool."""
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found.[/red]")
        raise typer.Exit(code=1)

    file_hash = hash_file(str(file_path))
    if not file_hash:
        console.print("[red]Error calculating file hash.[/red]")
        raise typer.Exit(code=1)

    bc = get_blockchain()
    tx = Transaction(
        type="notarization",
        owner=owner,
        file_hash=file_hash,
        filename=file_path.name,
        timestamp=0 # Will be set by default factory in schema if 0, but schema says default factory is time.time
    )
    # Re-instantiate to use default time if needed, or just let schema handle it.
    # Actually, schema default is time.time, so just don't pass it if we want current time.
    # But we defined it with default factory.
    tx = Transaction(
        type="notarization",
        owner=owner,
        file_hash=file_hash,
        filename=file_path.name
    )

    bc.add_transaction(tx)
    bc.save_chain() # Pending txs are in memory, but Blockchain.__init__ loads from file.
                    # We need to save the pending txs?
                    # The current Blockchain implementation in core.py saves the chain (blocks),
                    # but it resets pending_transactions on load!
                    # Ideally, pending transactions should be persisted too.
                    # For this simple port, we'll assume 'mine' is called immediately or we need to persist pending.
                    # Let's check core.py...
                    # core.py: save_chain dumps self.chain. It does NOT dump pending_transactions.
                    # This means if we run 'datum notarize' and exit, the tx is lost!
                    # FIX: We should either auto-mine or persist pending.
                    # The legacy script had 'add_transaction' just append to list, then 'mine' would pick it up.
                    # But the legacy script was often run in a REPL or 'sim' mode where memory persisted,
                    # OR in 'tool' mode where it saved to pickle.
                    # In 'tool' mode (cli), the legacy script loaded, added tx, *didn't save pending*, and exited?
                    # Let's re-read legacy blockchain.py...
                    # "if args.command == 'notarize': ... bc.add_transaction(...) ... save_blockchain(bc, ...)"
                    # And 'save_blockchain' pickled the *entire object*, including pending_transactions.
                    # So my JSON serialization needs to save pending_transactions too!

    # I will update core.py to save pending transactions in the JSON structure.
    # For now, I'll finish CLI, then fix core.py.

    console.print(f"[green]✅ Notarization for '{file_path.name}' added to pending pool.[/green]")
    console.print(f"File Hash: [bold cyan]{file_hash}[/bold cyan]")
    console.print("[yellow]Run 'datum mine' to confirm this transaction.[/yellow]")


@app.command()
def mine(miner: str = typer.Option(settings.miner_address, help="Address for mining rewards")):
    """Mine a new block with pending transactions."""
    bc = get_blockchain()
    if not bc.pending_transactions:
        console.print("[yellow]No pending transactions to mine.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Mining block...", total=None)
        success = bc.mine_pending_transactions(miner)

    if success:
        last_block = bc.get_latest_block()
        console.print(f"[green]🎉 Block #{last_block.index} successfully mined![/green]")
        console.print(f"Hash: [dim]{last_block.hash}[/dim]")
        console.print(f"Nonce: {last_block.nonce}")
    else:
        console.print("[red]Mining failed.[/red]")

@app.command()
def balance(address: str):
    """Check the balance of an address."""
    bc = get_blockchain()
    bal = bc.calculate_balance(address)
    console.print(f"Balance for [bold]{address}[/bold]: [green]{bal} Datum[/green]")

@app.command()
def show(n: int = typer.Option(5, help="Number of recent blocks to show")):
    """Show the blockchain."""
    bc = get_blockchain()
    table = Table(title=f"Datum Blockchain (Last {n} Blocks)")
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Transactions", style="white")
    table.add_column("Hash", style="dim green")

    # Show last n blocks
    for block in bc.chain[-n:]:
        tx_summary = f"{len(block.transactions)} txs"
        if len(block.transactions) > 0:
            types = [t.type for t in block.transactions]
            tx_summary += f" ({', '.join(types)})"

        table.add_row(
            str(block.index),
            str(block.timestamp),
            tx_summary,
            block.hash[:10] + "..."
        )

    console.print(table)

@app.command()
def verify(file_path: Path):
    """Verify if a file exists in the blockchain."""
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found.[/red]")
        raise typer.Exit(code=1)

    file_hash = hash_file(str(file_path))
    bc = get_blockchain()

    result = bc.find_transaction_by_file_hash(file_hash)
    if result:
        block, tx = result
        console.print("[green]✅ File verified![/green]")
        console.print(f"Found in Block #{block.index}")
        console.print(f"Owner: {tx.owner}")
        console.print(f"Date: {tx.timestamp}")
    else:
        console.print("[red]❌ File not found in blockchain.[/red]")

if __name__ == "__main__":
    app()
