import http.server
import json
import os
import re
import signal
import socketserver
import subprocess
import sys

# Configuration
PORT = 8000
BLOCKCHAIN_SCRIPT = "./blockchain.py"
CHAIN_FILE = "hpc_campus.dat"
COIN_NAME = "HPCCredit"
LOG_FILE = "sim_output.log"
SIM_SCRIPT = "./hpc_arcade.sh"

# Global variable to hold the simulation process
sim_process = None

class BlockchainHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # 1. Get Blockchain Stats
            try:
                cmd = [BLOCKCHAIN_SCRIPT, "--chain", CHAIN_FILE, "--coin-name", COIN_NAME, "stats"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                # Output is like: {"height": 12, ...}
                bc_stats = json.loads(result.stdout.strip())
            except:
                bc_stats = {"height": 0, "tx_count": 0, "last_hash": "N/A"}

            # 2. Parse Simulation Log for Economy Stats
            jobs_completed = 0
            credits_spent = 0
            active_users = set()
            recent_logs = []

            if os.path.exists(LOG_FILE):
                with open(LOG_FILE) as f:
                    lines = f.readlines()
                    # Get last 20 lines for log view
                    recent_logs = [l.strip() for l in lines[-20:]]

                    for line in lines:
                        if "Job completed" in line:
                            jobs_completed += 1

                        # Extract Cost: "💰 TOTAL COST:    112 HPCCredit"
                        cost_match = re.search(r"TOTAL COST:\s+(\d+)", line)
                        if cost_match:
                            credits_spent += int(cost_match.group(1))

                        # Extract User: "User:      Bob"
                        user_match = re.search(r"User:\s+(\w+)", line)
                        if user_match:
                            active_users.add(user_match.group(1))

            data = {
                "blockchain": bc_stats,
                "economy": {
                    "jobs_completed": jobs_completed,
                    "credits_spent": credits_spent,
                    "active_users": len(active_users),
                    "user_list": list(active_users)
                },
                "logs": recent_logs
            }

            self.wfile.write(json.dumps(data).encode())
        else:
            # Serve static files (index.html)
            super().do_GET()

def run_simulation():
    global sim_process
    print("🚀 Starting Simulation Background Process...")
    # Clear log
    with open(LOG_FILE, 'w') as f:
        f.write("--- Simulation Started ---\n")

    # Start script
    sim_process = subprocess.Popen([SIM_SCRIPT, "auto"], stdout=open(LOG_FILE, 'a'), stderr=subprocess.STDOUT)

def cleanup(signum, frame):
    print("\n🛑 Stopping Simulation...")
    if sim_process:
        sim_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Change dir to script location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Trap Ctrl+C
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    run_simulation()

    print(f"🌍 Dashboard running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")

    with socketserver.TCPServer(("", PORT), BlockchainHandler) as httpd:
        httpd.serve_forever()
