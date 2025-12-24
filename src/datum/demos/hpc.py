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
    if bc.calculate_balance(admin) < 1000:
        # Create initial wealth
        for _ in range(10):
            bc.add_transaction(Transaction(sender="Genesis", recipient=admin, amount=0))
            bc.mine_pending_transactions(admin)
    return bc

def run_hpc_demo():
    """Runs an interactive HPC simulation using Rich Live display."""
    chain_file = "hpc_demo_chain.json"
    coin_name = "HPCCredit"
    admin = "HPC_Admin"
    users = ["Alice_Res", "Bob_Lab", "Charlie_AI"]

    bc = setup_demo_chain(chain_file, admin)

    # State tracking for the UI
    active_jobs = []
    logs = []

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="log", size=10)
    )
    layout["body"].split_row(Layout(name="left"), Layout(name="right"))

    def log(msg):
        logs.append(msg)
        if len(logs) > 8:
            logs.pop(0)

    def generate_dashboard():
        # Header
        layout["header"].update(Panel(f"🚀 Datum HPC Simulation | Chain: {chain_file}", style="bold white on blue"))

        # Left: Job Queue
        job_table = Table(title="Active Jobs", expand=True)
        job_table.add_column("User", style="cyan")
        job_table.add_column("Job ID", style="white")
        job_table.add_column("Cost", style="red")
        job_table.add_column("Status", style="bold green")

        for j in active_jobs[-15:]:
            job_table.add_row(j['user'], j['id'], str(j['cost']), j['status'])

        # Right: Wallet Balances
        bal_table = Table(title=f"Wallet Balances ({coin_name})", expand=True)
        bal_table.add_column("User", style="yellow")
        bal_table.add_column("Balance", style="green")
        for u in [admin] + users:
            b = bc.calculate_balance(u)
            bal_table.add_row(u, f"{b:.1f}")

        layout["log"].update(Panel("\n".join(logs), title="System Logs", border_style="cyan"))
        layout["body"]["left"].update(Panel(job_table))
        layout["body"]["right"].update(Panel(bal_table))
        return layout

    run_simulation_loop(bc, admin, users, active_jobs, log, generate_dashboard)

def run_simulation_loop(bc, admin, users, active_jobs, log_func, dashboard_func):
    """Main loop for the simulation."""
    with Live(dashboard_func(), refresh_per_second=4) as live:
        step = 0
        while step < 40: # Run for 40 steps
            live.update(dashboard_func())
            time.sleep(0.8)
            step += 1

            # 1. Random Job Submission
            if step % 3 == 0:
                user = random.choice(users)
                cost = random.randint(10, 50)
                job_id = f"J-{step:03d}"

                if bc.calculate_balance(user) < cost:
                    log_func(f"[yellow]Funding {user}...[/yellow]")
                    bc.add_transaction(Transaction(type="currency", sender=admin, recipient=user, amount=100.0))
                    bc.save_chain()
                else:
                    log_func(f"[cyan]{user} submitted {job_id}[/cyan]")
                    active_jobs.append({"user": user, "id": job_id, "cost": cost, "status": "Queued"})
                    bc.add_transaction(Transaction(type="currency", sender=user, recipient=admin, amount=float(cost)))
                    bc.add_transaction(Transaction(
                        type="notarization", owner=user, filename=job_id, file_hash=f"h-{step}"
                    ))
                    bc.save_chain()

            # 2. Block Mining
            if step % 7 == 0 and bc.pending_transactions:
                log_func("[bold green]⛏️  Mining Block...[/bold green]")
                bc.mine_pending_transactions(admin)
                # Update all queued jobs to completed
                for j in active_jobs:
                    if j["status"] == "Queued":
                        j["status"] = "Completed"
                log_func(f"[green]Block #{bc.get_latest_block().index} mined![/green]")

        log_func("[bold white]Demo complete.[/bold white]")
        live.update(dashboard_func())
        time.sleep(2)
