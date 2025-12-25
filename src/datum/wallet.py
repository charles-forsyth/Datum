import base64
import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

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
    # Check if name is a file path first
    path = Path(name)
    if not path.exists():
        path = WALLET_DIR / f"{name}.pem"

    if not path.exists():
        raise FileNotFoundError(f"Wallet '{name}' not found.")

    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )

def load_public_key(path_or_pem: str):
    """Loads a public key from a file path or direct PEM string."""
    if os.path.exists(path_or_pem):
        with open(path_or_pem, "rb") as f:
            return serialization.load_pem_public_key(f.read())
    else:
        return serialization.load_pem_public_key(path_or_pem.encode('utf-8'))

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

# --- HYBRID ENCRYPTION (ECDH + AES-GCM) ---

def encrypt_for_recipient(data: bytes, recipient_pub_pem: str) -> str:
    """
    Encrypts data so only the owner of the private key corresponding
    to `recipient_pub_pem` can read it.
    Returns: Base64 string combining (Ephemeral Pub Key + Nonce + Ciphertext)
    """
    recipient_pub_key = load_public_key(recipient_pub_pem)

    # 1. Generate Ephemeral Keypair
    ephemeral_priv = ec.generate_private_key(ec.SECP256R1())
    ephemeral_pub = ephemeral_priv.public_key()

    # 2. Perform ECDH to get Shared Secret
    shared_key = ephemeral_priv.exchange(ec.ECDH(), recipient_pub_key)

    # 3. Derive AES Key (HKDF)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'datum-protocol-v1',
    ).derive(shared_key)

    # 4. Encrypt Data (AES-GCM)
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    # 5. Pack it all up: Ephemeral Pub Key (PEM) + Nonce + Ciphertext
    # We need the ephemeral public key to decrypt (to derive the same shared secret)
    ephemeral_pub_bytes = ephemeral_pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Simple Length-Prefix framing:
    # [4 bytes len pubkey][pubkey bytes][12 bytes nonce][ciphertext]
    # Actually, simpler: Just base64 encode individually or use a separator.
    # Let's use a simple separator "||" on base64 strings
    b64_pub = base64.b64encode(ephemeral_pub_bytes).decode('utf-8')
    b64_nonce = base64.b64encode(nonce).decode('utf-8')
    b64_cipher = base64.b64encode(ciphertext).decode('utf-8')

    return f"{b64_pub}||{b64_nonce}||{b64_cipher}"

def decrypt_data(packed_data: str, recipient_priv_key) -> bytes:
    """Decrypts data using the recipient's private key."""
    try:
        parts = packed_data.split("||")
        if len(parts) != 3:
            raise ValueError("Invalid encrypted format")

        b64_pub, b64_nonce, b64_cipher = parts

        ephemeral_pub_bytes = base64.b64decode(b64_pub)
        nonce = base64.b64decode(b64_nonce)
        ciphertext = base64.b64decode(b64_cipher)

        ephemeral_pub_key = serialization.load_der_public_key(ephemeral_pub_bytes)

        # 1. Re-derive Shared Secret
        shared_key = recipient_priv_key.exchange(ec.ECDH(), ephemeral_pub_key)

        # 2. Re-derive AES Key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'datum-protocol-v1',
        ).derive(shared_key)

        # 3. Decrypt
        aesgcm = AESGCM(derived_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e
