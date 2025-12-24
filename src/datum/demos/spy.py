# Spy vs. Spy Demo Logic
import hashlib
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

def setup_spy_chain(chain_file: str):
    """Initializes the secure comms channel."""
    bc = Blockchain(chain_file=chain_file)
    # Ensure chain exists and has genesis
    if not bc.chain:
        bc.create_genesis_block()
    return bc

def render_ui(layout, state, chain_file, agent_fox, agent_crow):
    """Updates the UI layout based on current state."""
    # Header
    header_style = "bold white on blue"
    if state["alert_level"] == "HIGH":
        header_style = "bold white on red"

    layout["header"].update(Panel(
        Align.center(f"🛰️  OPERATION: NIGHTFALL | SECURE CHANNEL: {chain_file}"),
        style=header_style
    ))

    # Fox Panel
    fox_content = f"[bold cyan]{agent_fox}[/bold cyan]\n\nStatus: {state['fox_status']}\n\n"
    if state["phase"] in ["ENCRYPTING", "UPLOADING"]:
            fox_content += "Payload: [dim]***********[/dim]\n"
            fox_content += "Encryption: AES-256 [green]ACTIVE[/green]\n"
    layout["fox"].update(Panel(fox_content, title="Uplink Alpha", border_style="cyan"))

    # Crow Panel
    crow_content = f"[bold green]{agent_crow}[/bold green]\n\nStatus: {state['crow_status']}\n\n"
    for m in state["messages"]:
        crow_content += f"> {m}\n"
    layout["crow"].update(Panel(crow_content, title="Downlink Beta", border_style="green"))

    # Ledger Panel
    ledger_table = Table(title="Blockchain Activity", box=None, show_header=False)
    for log in state["ledger_logs"]:
        ledger_table.add_row(log)
    layout["ledger"].update(Panel(ledger_table, border_style="white"))

    # Status Bar
    alert_color = "green" if state["alert_level"] == "LOW" else "red"
    latency = random.randint(20, 150)
    status_text = f"THREAT LEVEL: [{alert_color}]{state['alert_level']}[/{alert_color}] | NETWORK LATENCY: {latency}ms"
    layout["status"].update(Panel(Align.center(status_text), style="on black"))

    return layout

def run_simulation_sequence(bc, state, live, update_ui_func, agent_fox):
    """Executes the scripted demo sequence."""

    def log_ledger(msg):
        state["ledger_logs"].append(msg)
        if len(state["ledger_logs"]) > 6:
            state["ledger_logs"].pop(0)

    # Phase 1: Establish Connection
    state["fox_status"] = "Handshaking..."
    time.sleep(1)
    state["crow_status"] = "Authenticating..."
    time.sleep(1)
    state["fox_status"] = "Secure Tunnel Established"
    state["crow_status"] = "Waiting for Payload"
    live.update(update_ui_func())
    time.sleep(1)

    # Phase 2: Fox Prepares Data
    state["phase"] = "ENCRYPTING"
    state["fox_status"] = "Encrypting Payload..."

    secret_data = "BLUEPRINT_OMEGA_V2"
    # Simulate processing time
    for i in range(1, 4):
        state["fox_status"] = f"Encrypting Payload... {i*33}%%"
        time.sleep(0.5)
        live.update(update_ui_func())

    encrypted_hash = hashlib.sha256(secret_data.encode()).hexdigest()
    state["fox_status"] = "Payload Encrypted."
    time.sleep(1)

    # Phase 3: The Drop (Notarize)
    state["phase"] = "UPLOADING"
    state["fox_status"] = "Notarizing to Chain..."

    tx = Transaction(
        type="notarization",
        owner=agent_fox,
        filename="drop_package.enc",
        file_hash=encrypted_hash
    )
    bc.add_transaction(tx)
    bc.save_chain()
    log_ledger(f"[yellow]PENDING:[/yellow] Notarization from {agent_fox}")
    time.sleep(1)

    # Phase 4: Mining (The Wait)
    state["alert_level"] = "ELEVATED"
    log_ledger("[bold red]! NETWORK SPIKE DETECTED ![/bold red]")
    time.sleep(1)

    state["fox_status"] = "Waiting for Confirmation..."
    state["crow_status"] = "Scanning Mempool..."

    # Dramatic mining pause
    for _ in range(3):
        log_ledger("[dim]Mining block... hashing...[/dim]")
        time.sleep(0.8)
        live.update(update_ui_func())

    bc.mine_pending_transactions("Network_Node_01")
    last_block = bc.get_latest_block()
    log_ledger(f"[bold green]BLOCK #{last_block.index} MINED[/bold green] | Hash: {last_block.hash[:10]}...")
    state["alert_level"] = "LOW"
    time.sleep(1)

    # Phase 5: Verification
    state["phase"] = "VERIFYING"
    state["crow_status"] = "Block Received. Verifying..."
    time.sleep(1)

    # Crow "finds" the transaction
    block, found_tx = bc.find_transaction_by_file_hash(encrypted_hash)

    if found_tx:
        state["crow_status"] = "Target Acquired."
        state["messages"].append("[green]Hash Match Confirmed[/green]")
        time.sleep(0.5)
        state["messages"].append(f"Owner: {found_tx.owner}")
        time.sleep(0.5)
        state["messages"].append("Decrypting...")
        time.sleep(1)
        state["messages"].append(f"[bold white]SECRET: {secret_data}[/bold white]")
        state["fox_status"] = "Mission Complete. Disconnecting."

    live.update(update_ui_func())
    time.sleep(3)

def run_spy_demo():
    """Runs the cinematic Spy vs. Spy demo."""
    chain_file = "spy_network.json"
    bc = setup_spy_chain(chain_file)

    agent_fox = "Agent_Fox"
    agent_crow = "Agent_Crow"
    # CounterIntel logic removed for simplicity in this version, but concept remains

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=2),
        Layout(name="ledger", size=8),
        Layout(name="status", size=3)
    )
    layout["main"].split_row(
        Layout(name="fox", ratio=1),
        Layout(name="crow", ratio=1)
    )

    state = {
        "phase": "INIT",
        "fox_status": "Idle",
        "crow_status": "Listening",
        "alert_level": "LOW",
        "messages": [],
        "ledger_logs": [],
        "progress": 0
    }

    # Wrapper to pass state to the renderer
    def update_ui():
        return render_ui(layout, state, chain_file, agent_fox, agent_crow)

    # The Narrative Loop
    with Live(update_ui(), refresh_per_second=4) as live:
        run_simulation_sequence(bc, state, live, update_ui, agent_fox)
