#!/usr/bin/env python3
import argparse
import random
import re
import subprocess
import time

# Configuration
# We assume this script is running from the same directory as blockchain.py
BLOCKCHAIN_SCRIPT = "./blockchain.py"
CHAIN_FILE = "hpc_campus.dat"
COIN_NAME = "HPCCredit"
ADMIN_ADDRESS = "HPC_Core"

# Pricing Model (Credits per unit-hour)
PRICE_CPU_CORE = 10
PRICE_GPU = 100
PRICE_MEM = 2

def run_blockchain_cmd(args):
    """Wrapper to call the blockchain tool."""
    cmd = [BLOCKCHAIN_SCRIPT, "--chain", CHAIN_FILE, "--coin-name", COIN_NAME] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def get_balance(user):
    """Gets the user's balance by parsing the tool output."""
    res = run_blockchain_cmd(["balance", "--address", user])
    if res.returncode != 0:
        return 0
    try:
        # Output format: "💰 The balance for address 'User' is: 123 HPCCredit"
        # We look for the number immediately preceding "HPCCredit"
        match = re.search(r"(\d+)\s+HPCCredit", res.stdout)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Debug: Error parsing balance: {e}")
    return 0

def submit_job(user, cpu_cores, gpus, mem, hours, script_name):
    print("\n--- 📋 HPC Job Submission System ---")

    # 1. Calculate Cost
    hourly_rate = (cpu_cores * PRICE_CPU_CORE) + (gpus * PRICE_GPU) + (mem * PRICE_MEM)
    total_cost = int(hourly_rate * hours)

    # Minimum charge of 1 credit
    if total_cost < 1:
        total_cost = 1

    print(f"User:      {user}")
    print(f"Job:       {script_name}")
    print(f"Resources: {cpu_cores} CPU cores, {gpus} GPUs, {mem} GB RAM")
    print(f"Duration:  {hours} Hours")
    print("-----------------------------------")
    print(f"💵 Rate:          {hourly_rate} {COIN_NAME}/hr")
    print(f"💰 TOTAL COST:    {total_cost} {COIN_NAME}")

    # 2. Check Balance
    balance = get_balance(user)
    print(f"💳 Wallet Balance: {balance} {COIN_NAME}")

    if balance < total_cost:
        print(f"❌ REJECTED: Insufficient funds. You are short {total_cost - balance} credits.")
        return

    # 3. Process Payment (User -> Admin)
    print(f"\n[1/3] 💸 Processing payment to {ADMIN_ADDRESS}...")
    res = run_blockchain_cmd(["transfer", "--from", user, "--to", ADMIN_ADDRESS, "--amount", str(total_cost)])
    if res.returncode != 0:
        print(f"❌ Payment failed: {res.stderr}")
        return
    else:
        print("      ✅ Payment transaction broadcast.")

    # 4. Run "Job" (Simulated)
    job_id = f"job_{int(time.time())}_{random.randint(1000,9999)}"
    log_file = f"{job_id}.out"
    print(f"[2/3] ⚙️  Allocating resources & running job (ID: {job_id})...")

    # Simulate work
    time.sleep(1.5)

    # Create dummy output file
    with open(log_file, "w") as f:
        f.write("--- HPC JOB REPORT ---\n")
        f.write(f"Job ID: {job_id}\n")
        f.write(f"User: {user}\n")
        f.write(f"Script: {script_name}\n")
        f.write(f"Resources: {cpu_cores}C / {gpus}G / {mem}M\n")
        f.write("Result: SUCCESS\n")
        f.write(f"Scientific Data: {random.randint(10000000, 99999999)}\n")

    print(f"      ✅ Job completed. Output saved to '{log_file}'.")

    # 5. Notarize Result (Proof of Research)
    print("[3/3] 🔏 Notarizing result on blockchain...")
    run_blockchain_cmd(["notarize", "--owner", user, "--file", log_file])
    print("      ✅ Notarization transaction broadcast.")

    # 6. Mine Block (Confirm Payment + Notarization)
    # In a real system, the miner is separate. Here, we trigger it to confirm immediately.
    print("\n[System] ⛏️  Mining block to confirm transactions...")
    run_blockchain_cmd(["mine", "--miner", ADMIN_ADDRESS, "--reward", "0"])

    print(f"\n🎉 SUCCESS! Job '{job_id}' is paid for, executed, and immutable.")

def main():
    parser = argparse.ArgumentParser(description="HPC Smart Scheduler Simulator")
    parser.add_argument("--user", required=True, help="User submitting the job")
    parser.add_argument("--cpu-cores", type=int, default=1, help="Number of CPU cores")
    parser.add_argument("--gpus", type=int, default=0, help="Number of GPUs")
    parser.add_argument("--mem", type=int, default=4, help="Memory in GB")
    parser.add_argument("--time", type=float, default=1.0, help="Duration in hours")
    parser.add_argument("script", help="Script name to run")

    args = parser.parse_args()

    submit_job(args.user, args.cpu_cores, args.gpus, args.mem, args.time, args.script)

if __name__ == "__main__":
    main()
