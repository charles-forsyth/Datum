from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Datum"
    chain_file: str = Field("datum_chain.json", description="The default file to store the blockchain")
    miner_address: str = Field("default_miner", description="Default address/name for mining rewards")
    difficulty: int = Field(4, description="Mining difficulty (number of leading zeros)")
    mining_reward: float = Field(100.0, description="Reward for mining a block")

    # Environment variable config
    model_config = SettingsConfigDict(
        env_prefix="DATUM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
