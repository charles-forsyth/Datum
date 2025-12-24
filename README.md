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

## Development

We enforce strict code quality standards.

### Running Tests
```bash
pytest
```

### Linting
```bash
ruff check .
```

### Git Hooks
A pre-push hook is configured to ensure no broken code is pushed to the repository.
