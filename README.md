# Datum: Professional Blockchain & Data Integrity Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Datum** is a modernized, professional-grade blockchain tool designed for educational purposes and practical data integrity verification. It serves as the "Atomic Unit of Truth" for your local data ecosystem.

Built with a modern Python stack:
*   **[uv](https://github.com/astral-sh/uv)** for blazing fast dependency management.
*   **[Pydantic V2](https://docs.pydantic.dev/)** for strict data validation and schema management.
*   **[Rich](https://github.com/Textualize/rich)** for a beautiful, robust CLI and TUI.
*   **[Ruff](https://docs.astral.sh/ruff/)** for strict linting and formatting.

## Installation

### System-Wide Installation (Recommended)

You can install Datum directly from the repository using `uv` to use it as a global CLI tool:

```bash
uv tool install git+https://github.com/charles-forsyth/Datum.git
```

To update to the latest version:
```bash
uv tool upgrade datum
```

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:charles-forsyth/Datum.git
    cd Datum
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Run the CLI:**
    ```bash
    uv run datum --help
    ```

## Usage

Once installed, the `datum` command is available globally.

### Data & Configuration
Datum follows XDG standards for file storage:
*   **Ledger:** `~/.local/share/datum/ledger.json` (Default blockchain)
*   **Config:** `~/.config/datum/.env` (Global settings)

You can override these defaults using environment variables or a `.env` file in your current directory.

**Example `~/.config/datum/.env`:**
```ini
# Customize your identity
DATUM_MINER_ADDRESS="Chuck_Workstation"

# Genesis Block Settings (Applied when creating a NEW chain)
DATUM_GENESIS_MESSAGE="Welcome to the Datum Network - Est. 2025"
DATUM_PREMINE='{"Chuck": 1000000, "DAO_Treasury": 500000}'
```

### Common Commands

**Notarize a File**
Record the existence of a file on the blockchain.
```bash
datum notarize --owner "Alice" /path/to/document.pdf
```

**Mine a Block**
Confirm pending transactions (like notarizations) by mining a new block.
```bash
datum mine
```

**Transfer Funds**
Send currency to another address.
```bash
datum transfer --from "Alice" --to "Bob" --amount 50.0
```

**Verify a File**
Check if a file's current hash matches a notarized record in the blockchain.
```bash
datum verify /path/to/document.pdf
```

**Manage Multiple Chains**
Work with an isolated ledger for a specific project.
```bash
datum --chain secret_project.json --coin-name "SecretCoin" balance --address "Agent_007"
```

## Interactive Demos

Datum includes several built-in demos to showcase its capabilities.

**1. HPC Simulation (`datum demo hpc`)**
Simulates a high-performance computing environment where researchers pay for compute jobs using tokens. Features a real-time TUI dashboard tracking job queues and wallet balances.

**2. Spy vs. Spy (`datum demo spy`)**
A cinematic narrative experience simulating a secure "dead drop" protocol between agents using the blockchain for encrypted communication.

**3. The Bazaar (`datum demo bazaar`)**
A high-frequency trading simulation involving three parallel blockchains (Gold, Spice, Intel) and automated trading bots executing atomic swaps.

## Development Workflow ("Skywalker" Standard)

We strictly adhere to the following workflow for all changes. **Direct pushes to main are forbidden.**

### 1. Branch & Bump
Start a new feature branch and **immediately bump the version** in `pyproject.toml`.
```bash
git checkout -b feature/my-feature
# Edit pyproject.toml: version = "0.x.y" -> "0.x.z"
```

### 2. The Local Gauntlet
Iterate until these pass:
```bash
uv run ruff check . --fix
PYTHONPATH=src uv run pytest
```

### 3. Push & PR
```bash
git push -u origin feature/my-feature
gh pr create --fill
```

### 4. The Gatekeeper (CI)
Wait for GitHub Actions to pass.
```bash
gh pr checks --watch
```

### 5. Merge
```bash
gh pr merge --merge --delete-branch
```

### 6. Release & Sync
Back on `main`, pull the changes and create the release tag.
```bash
git checkout main && git pull
# Create release tag matching pyproject.toml version
gh release create v0.x.z --generate-notes
# Update local tool
uv tool upgrade datum
```
