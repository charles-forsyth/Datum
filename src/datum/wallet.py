import base64
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

WALLET_DIR = Path.home() / ".config" / "datum" / "wallets"

def ensure_wallet_dir():
    WALLET_DIR.mkdir(parents=True, exist_ok=True)

def generate_wallet(name: str):
    """Generates a new ECC private/public key pair and saves them."""
    ensure_wallet_dir()
    private_key_path = WALLET_DIR / f"{name}.pem"
    public_key_path = WALLET_DIR / f"{name}.pub"

    if private_key_path.exists():
        raise FileExistsError(f"Wallet '{name}' already exists.")

    # Generate Private Key (SECP256R1)
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Serialize Private Key
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize Public Key
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Save to disk
    with open(private_key_path, "wb") as f:
        f.write(pem_private)

    with open(public_key_path, "wb") as f:
        f.write(pem_public)

    return str(private_key_path), pem_public.decode('utf-8')

def load_private_key(name: str):
    """Loads a private key from the wallet directory."""
    path = WALLET_DIR / f"{name}.pem"
    if not path.exists():
        # Try finding it as a direct path if provided
        if Path(name).exists():
            path = Path(name)
        else:
            raise FileNotFoundError(f"Wallet '{name}' not found.")

    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )

def get_public_key_string(private_key) -> str:
    """Extracts the public key string (PEM) from a private key object."""
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode('utf-8')

def sign_data(data: str, private_key) -> str:
    """Signs a string message and returns the signature in base64."""
    signature = private_key.sign(
        data.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(data: str, signature_b64: str, public_key_pem: str) -> bool:
    """Verifies a signature against the data and public key."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            data.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except (InvalidSignature, Exception):
        return False
