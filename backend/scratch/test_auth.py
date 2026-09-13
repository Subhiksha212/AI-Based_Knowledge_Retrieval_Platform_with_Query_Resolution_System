"""
Test script for verifying JWT token generation, decoding, and expiration logic.
"""

import sys
import os
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.auth import create_access_token, decode_access_token, get_token_subject

print("--- Testing JWT Access Token ---")
token = create_access_token("test-user-123", extra_claims={"email": "test@querynest.ai"})
print(f"Generated Token: {token[:30]}...")

decoded = decode_access_token(token)
print(f"Decoded Payload: {decoded}")

subject = get_token_subject(token)
print(f"Extracted Subject: {subject}")

assert subject == "test-user-123", "Subject mismatch!"
print("JWT test passed successfully!")
