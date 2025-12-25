# The Bazaar: Multi-Chain Trading Demo
import random
import time

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from datum.core import Blockchain
from datum.schemas import Transaction

console = Console()

def setup_economy(chain_file: str, currency: str, admin: str):
    """Initializes a specific economy."""
    bc = Blockchain(chain_file=chain_file)
    if not bc.chain:
        bc.create_genesis_block()

    # Ensure Admin has funds to start the economy
    if bc.calculate_balance(admin) < 50000:
        # Mint 100,000 coins for the admin directly
        bc.add_transaction(Transaction(
            type="currency",
            sender="Genesis",
            recipient=admin,
            amount=100000.0,
            timestamp=time.time()
        ))
        bc.mine_pending_transactions(admin)
    return bc

def render_bazaar_ui(layout, chains, actors, logs):
    """Updates the Bazaar UI."""
    # Header
    layout["header"].update(Panel(
        Align.center("💰 THE BAZAAR | INTER-CHAIN TRADING FLOOR"),
        style="bold white on purple"
    ))

    # Market Columns
    markets = [("Gold", "yellow"), ("Spice", "red"), ("Intel", "blue")]

    for currency, color in markets:
        bc = chains[currency]
        table = Table(title=f"{currency} Ledger", box=None, expand=True)
        table.add_column("Holder", style="white")
        table.add_column("Balance", style=color, justify="right")

        # Calculate balances for all actors
        for actor in actors:
            bal = bc.calculate_balance(actor)
            table.add_row(actor, f"{bal:.1f}")

        layout[currency.lower()].update(Panel(table, border_style=color))

    # Ticker / Logs
    log_text = "\n".join(logs[-8:])
    layout["ticker"].update(Panel(log_text, title="Live Market Ticker", border_style="green"))

    return layout

def execute_random_trade(chains, traders, log):
    """Attempts to execute a random atomic swap between two traders."""
    buyer = random.choice(traders)
    seller = random.choice(traders)
    if buyer == seller:
        return

    # Decide trade pair (e.g., Buy Spice with Gold)
    want = random.choice(["Gold", "Spice", "Intel"])
    pay_with = random.choice(["Gold", "Spice", "Intel"])
    if want == pay_with:
        return

    amount_want = random.randint(10, 50)
    # Exchange rates (Fixed for demo: 1 Gold = 2 Spice = 5 Intel)
    rates = {"Gold": 10, "Spice": 5, "Intel": 2}
    amount_pay = (amount_want * rates[want]) / rates[pay_with]

    # Execute Atomic Swap (Simulated)
    # 1. Buyer sends 'pay_with' to Seller
    bc_pay = chains[pay_with]
    if bc_pay.calculate_balance(buyer) >= amount_pay:
        bc_pay.add_transaction(Transaction(sender=buyer, recipient=seller, amount=amount_pay))

        # 2. Seller sends 'want' to Buyer
        bc_want = chains[want]
        if bc_want.calculate_balance(seller) >= amount_want:
            bc_want.add_transaction(Transaction(sender=seller, recipient=buyer, amount=amount_want))

            log(f"[bold]{buyer}[/bold] bought [cyan]{amount_want} {want}[/cyan] "
                f"from [bold]{seller}[/bold] for [magenta]{amount_pay:.1f} {pay_with}[/magenta]")
        else:
            # Rollback (Simulated failure - in real app would need complex rollback)
            # For demo, we just don't mine the first part
            bc_pay.pending_transactions = []

def perform_mining(chains, admin, log):
    """Mines blocks on all chains if they have pending transactions."""
    for _name, bc in chains.items():
        if bc.pending_transactions:
            bc.mine_pending_transactions(admin)
    log("[dim]-- Blocks Mined --[/dim]")

def run_bazaar_simulation(chains, actors, live, update_ui, logs):
    """Main trading loop."""

    def log(msg):
        logs.append(msg)

    # Distribute Initial Wealth
    log("[dim]Distributing initial capital...[/dim]")
    admin = actors[0] # The Mint
    traders = actors[1:]

    for _currency, bc in chains.items():
        for trader in traders:
            if bc.calculate_balance(trader) < 100:
                bc.add_transaction(Transaction(sender=admin, recipient=trader, amount=500.0))
        bc.mine_pending_transactions(admin)

    live.update(update_ui())
    time.sleep(1)

    step = 0
    while step < 50:
        step += 1
        time.sleep(0.5)

        execute_random_trade(chains, traders, log)

        # Mining (High Frequency)
        if step % 4 == 0:
            perform_mining(chains, admin, log)

        live.update(update_ui())

    log("[bold white]Market Closed.[/bold white]")
    live.update(update_ui())
    time.sleep(3)

def run_bazaar_demo():
    """Runs the Bazaar multi-currency simulation."""

    # 1. Setup Three Chains
    chains = {
        "Gold": setup_economy("chain_gold.json", "Gold", "The_Mint"),
        "Spice": setup_economy("chain_spice.json", "Spice", "The_Mint"),
        "Intel": setup_economy("chain_intel.json", "Intel", "The_Mint")
    }

    actors = ["The_Mint", "Merchant_A", "Smuggler_B", "Broker_C", "Tycoon_D"]
    logs = []

    # 2. Setup Layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="market_floor", ratio=3),
        Layout(name="ticker", size=10)
    )

    layout["market_floor"].split_row(
        Layout(name="gold"),
        Layout(name="spice"),
        Layout(name="intel")
    )

    def update_ui():
        return render_bazaar_ui(layout, chains, actors, logs)

    with Live(update_ui(), refresh_per_second=5) as live:
        run_bazaar_simulation(chains, actors, live, update_ui, logs)
