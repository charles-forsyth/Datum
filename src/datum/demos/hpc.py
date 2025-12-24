# HPC Demo Logic
import random
import time

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from datum.core import Blockchain
from datum.schemas import Transaction

console = Console()

def setup_demo_chain(chain_file: str, admin: str):
    """Initializes the demo blockchain and funds the admin."""
    bc = Blockchain(chain_file=chain_file)

    # Ensure Admin has funds if fresh chain
    if bc.calculate_balance(admin) < 1000:
        bc.add_transaction(Transaction(sender="Genesis", recipient=admin, amount=0))
        bc.mine_pending_transactions(admin) # Reward 100
        # Mine a few more to be safe
        for _ in range(5):
            bc.mine_pending_transactions(admin)
    return bc

def run_hpc_demo():
    """Runs an interactive HPC simulation using Rich Live display."""

    chain_file = "hpc_demo_chain.json"
    coin_name = "HPCCredit"
    admin = "HPC_Admin"
    users = ["Alice_Res", "Bob_Lab", "Charlie_AI"]

    bc = setup_demo_chain(chain_file, admin)

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="log", size=10)
    )
    layout["body"].split_row(Layout(name="left"), Layout(name="right"))

    logs = []

    def log(msg):
        logs.append(msg)
        if len(logs) > 8:
            logs.pop(0)

    def generate_dashboard():
        # Header
        layout["header"].update(Panel(f"🚀 Datum HPC Simulation | Chain: {chain_file}", style="bold white on blue"))

        # Left: Job Queue / Status
        job_table = Table(title="Active Jobs")
        job_table.add_column("User", style="cyan")
        job_table.add_column("Job", style="white")
        job_table.add_column("Cost", style="red")
        job_table.add_column("Status", style="green")

        # Right: Wallet Balances
        bal_table = Table(title=f"Wallet Balances ({coin_name})")
        bal_table.add_column("User", style="yellow")
        bal_table.add_column("Balance", style="green")

        # Add Balances
        for u in [admin] + users:
            b = bc.calculate_balance(u)
            bal_table.add_row(u, f"{b:.1f}")

        # Logs
        log_text = "\n".join(logs)
        layout["log"].update(Panel(log_text, title="System Logs", border_style="cyan"))

        layout["body"]["left"].update(Panel(job_table))
        layout["body"]["right"].update(Panel(bal_table))

        return layout

    run_simulation_loop(bc, admin, users, log, generate_dashboard)

def run_simulation_loop(bc, admin, users, log_func, dashboard_func):
    """Main loop for the simulation."""
    with Live(dashboard_func(), refresh_per_second=4) as live:
        step = 0
        while True:
            live.update(dashboard_func())
            time.sleep(1)
            step += 1

            # Simulate Activity
            if step % 3 == 0:
                user = random.choice(users)
                cost = random.randint(10, 50)

                # Check balance
                if bc.calculate_balance(user) < cost:
                    # Fund them from Admin if broke
                    log_func(f"[yellow]Funding {user} from Admin...[/yellow]")
                    bc.add_transaction(Transaction(
                        type="currency",
                        sender=admin,
                        recipient=user,
                        amount=100.0
                    ))
                    bc.save_chain()
                else:
                    # Run Job
                    log_func(f"[cyan]{user} submitting job (Cost: {cost})...[/cyan]")
                    bc.add_transaction(Transaction(
                        type="currency",
                        sender=user,
                        recipient=admin,
                        amount=float(cost)
                    ))
                    # Notarize result
                    bc.add_transaction(Transaction(
                        type="notarization",
                        owner=user,
                        filename="job_{step}.out",
                        file_hash="hash_placeholder"
                    ))
                    bc.save_chain()

            if step % 5 == 0:
                # Mine pending
                if bc.pending_transactions:
                    log_func("[bold green]⛏️  Mining Block...[/bold green]")
                    bc.mine_pending_transactions(admin)
                    log_func(f"[green]Block #{bc.get_latest_block().index} mined![/green]")

            if step > 30: # Auto-stop for test/demo
                break
