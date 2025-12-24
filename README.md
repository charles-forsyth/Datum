# Datum: Professional Blockchain & Data Integrity Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Datum** is a modernized, professional-grade blockchain tool designed for educational purposes and practical data integrity verification. It serves as the "Atomic Unit of Truth" for your local data ecosystem.

Built with a modern Python stack:
*   **[uv](https://github.com/astral-sh/uv)** for blazing fast dependency management.
*   **[Pydantic V2](https://docs.pydantic.dev/)** for strict data validation and schema management.
*   **[Typer](https://typer.tiangolo.com/)** & **[Rich](https://github.com/Textualize/rich)** for a beautiful, robust CLI.
*   **[Ruff](https://docs.astral.sh/ruff/)** for strict linting and formatting.

## Installation

### Using uv (Recommended)

You can install Datum directly from the repository using `uv` to use it as a global CLI tool:

```bash
uv tool install git+https://github.com/charles-forsyth/Datum.git
```

To update:
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

### Configuration
Datum loads configuration from environment variables or a `.env` file.
*   `DATUM_MINER_ADDRESS`: Default address for mining rewards.
*   `DATUM_CHAIN_FILE`: File path for the blockchain storage (default: `datum_chain.json`).

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

**Verify a File**
Check if a file's current hash matches a notarized record in the blockchain.
```bash
datum verify /path/to/document.pdf
```

**Check Balance**
```bash
datum balance "Alice"
```

**View Blockchain**
```bash
datum show
```

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