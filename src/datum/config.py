import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# XDG Standard Directories
XDG_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
XDG_CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

APP_DATA_DIR = XDG_DATA_HOME / "datum"
APP_CONFIG_DIR = XDG_CONFIG_HOME / "datum"

# Ensure directories exist
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    app_name: str = "Datum"

    # Default chain location is now central
    chain_file: str = Field(
        str(APP_DATA_DIR / "ledger.json"),
        description="The default file to store the blockchain"
    )

    miner_address: str = Field("default_miner", description="Default address/name for mining rewards")
    difficulty: int = Field(4, description="Mining difficulty (number of leading zeros)")
    mining_reward: float = Field(100.0, description="Reward for mining a block")

    # Genesis Configuration
    genesis_message: str = Field(
        "Genesis Block - Datum Project",
        description="Custom message embedded in the first block"
    )
    premine: dict[str, float] = Field(
        default_factory=dict,
        description="Initial allocation of funds {address: amount}"
    )

    # Environment variable config
    model_config = SettingsConfigDict(
        env_prefix="DATUM_",
        # Load form local .env OR global config
        env_file=[str(APP_CONFIG_DIR / ".env"), ".env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
