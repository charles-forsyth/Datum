import time
from typing import Optional

from pydantic import BaseModel, Field


class Provenance(BaseModel):
    repo_url: str
    commit_hash: str

class Transaction(BaseModel):
    type: str = Field(default="currency", description="Type of transaction: currency, notarization, reward, genesis")
    sender: Optional[str] = None
    recipient: Optional[str] = None
    amount: float = 0.0
    timestamp: float = Field(default_factory=time.time)

    # Notarization specific
    owner: Optional[str] = None
    file_hash: Optional[str] = None
    filename: Optional[str] = None

    # Genesis specific
    message: Optional[str] = None
    provenance: Optional[Provenance] = None

    # Crypto Identity
    signature: Optional[str] = None
    public_key: Optional[str] = None

    # Secure Messaging
    encrypted_payload: Optional[str] = None

    def calculate_data_hash(self) -> str:
        """Calculates hash of transaction data for signing (excludes signature/pubkey)."""
        import hashlib
        import json
        # Dump data excluding signature fields to create a stable hash for signing
        data = self.model_dump(exclude={'signature', 'public_key'})
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

class Block(BaseModel):
    index: int
    timestamp: float
    transactions: list[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block content.
        We use the JSON representation of the block (excluding the hash itself) for consistency.
        """
        import hashlib
        import json

        # Create a dictionary of the block data, excluding the hash
        block_data = self.model_dump(exclude={'hash'})

        # Sort keys to ensure consistent hashing
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
