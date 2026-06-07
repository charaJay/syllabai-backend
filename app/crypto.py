import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = bytes.fromhex(os.environ["ENCRYPTION_KEY"])


def encrypt(plaintext: str) -> str:
    iv = secrets.token_bytes(12)
    aesgcm = AESGCM(KEY)
    encrypted = aesgcm.encrypt(iv, plaintext.encode(), None)
    return iv.hex() + ":" + encrypted.hex()


def decrypt(stored: str) -> str:
    iv_hex, encrypted_hex = stored.split(":")
    iv = bytes.fromhex(iv_hex)
    encrypted = bytes.fromhex(encrypted_hex)
    aesgcm = AESGCM(KEY)
    return aesgcm.decrypt(iv, encrypted, None).decode()