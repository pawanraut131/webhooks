import hmac
import hashlib
from fastapi import HTTPException

def verify_github_signature(secret: str, payload_body: bytes, signature_header: str) -> bool:
    """
    Verifies the HMAC signature sent by GitHub in the X-Hub-Signature-256 header.
    
    Args:
        secret: The GITHUB_WEBHOOK_SECRET defined in your environment/settings.
        payload_body: The raw bytes of the request body.
        signature_header: The value of the 'X-Hub-Signature-256' header from GitHub.
        
    Returns:
        bool: True if the signature is valid, False otherwise.
        
    Raises:
        HTTPException: If the signature is missing or invalid.
    """
    if not signature_header:
        # If the header is entirely missing, we reject the request immediately.
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 header is missing.")

    # GitHub prefixes the signature with 'sha256='
    # E.g., 'sha256=1234567890abcdef...'
    # We split by '=' to extract just the hash value
    parts = signature_header.split("=")
    if len(parts) != 2 or parts[0] != "sha256":
        raise HTTPException(status_code=401, detail="Invalid signature format. Expected 'sha256=...'")
    
    github_hash = parts[1]

    # Create our own HMAC using the secret and the raw payload body
    # We use SHA-256 because GitHub's X-Hub-Signature-256 uses it.
    mac = hmac.new(secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    
    # Calculate our expected hash
    expected_hash = mac.hexdigest()

    # Compare the expected hash with the one provided by GitHub.
    # We use hmac.compare_digest instead of `==` to prevent timing attacks.
    if not hmac.compare_digest(expected_hash, github_hash):
        raise HTTPException(status_code=401, detail="Signature verification failed.")
        
    return True
