"""
Comprehensive End-to-End Test Suite for QueryNest Authentication & Token Refresh Flow
"""

import sys
import os
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token, decode_access_token, decode_token_for_refresh
from app.core.database import get_db, SessionLocal
from app.core.models import User

client = TestClient(app)


def test_auth_and_refresh_flow():
    print("\n" + "=" * 75)
    print("      AUTOMATED TEST SUITE: AUTHENTICATION & TOKEN REFRESH FLOW      ")
    print("=" * 75 + "\n")

    # Step 1: User Login / Create Token
    db = SessionLocal()
    try:
        user = db.query(User).first()
        assert user is not None, "No users found in database for testing!"
        print(f"[1/6] Selected Test User: {user.email} (ID: {user.id})")

        # Create valid token
        valid_token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
        print(f"      Valid Token Generated: {valid_token[:30]}...")

        # Step 2: Validate GET /auth/me with valid token
        print("\n[2/6] Validating GET /auth/me with Valid Token...")
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {valid_token}"})
        print(f"      Status: {res.status_code}")
        assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}"
        data = res.json()
        print(f"      Profile Email: {data.get('email')}")
        assert data.get("email") == user.email, "Profile email mismatch!"
        print("      [PASS] Valid Token Verification Passed!")

        # Step 3: Validate POST /query with valid token
        print("\n[3/6] Validating POST /query with Valid Token...")
        query_res = client.post(
            "/query",
            json={"query": "What is MCP?", "k": 2},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        print(f"      Status: {query_res.status_code}")
        assert query_res.status_code == 200, f"Expected 200 OK, got {query_res.status_code}"
        q_data = query_res.json()
        assert q_data.get("success") is True, "Query failed!"
        res_dict = q_data.get('response') or {}
        ans_str = str(res_dict.get('answer', '') or '').encode('ascii', errors='ignore').decode('ascii')
        print(f"      RAG Answer Snippet: {ans_str[:100]}...", flush=True)
        print("      [PASS] Valid Token Query Passed!", flush=True)

        # Step 4: Simulate Expired Token & Test 401 Handling
        print("\n[4/6] Simulating Expired Token & Testing 401 Rejection...", flush=True)
        # Create an expired token by setting past expiration claim manually
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from app.core.auth import SECRET_KEY, ALGORITHM

        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expired_payload = {
            "sub": str(user.id),
            "iat": past_time - timedelta(hours=1),
            "exp": past_time,
            "email": user.email,
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        print(f"      Expired Token Created: {expired_token[:30]}...", flush=True)

        # Request /query with expired token
        exp_res = client.post(
            "/query",
            json={"query": "What is MCP?", "k": 2},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        print(f"      Status Code with Expired Token: {exp_res.status_code}", flush=True)
        print(f"      Response Detail: {exp_res.json().get('detail')}", flush=True)
        assert exp_res.status_code == 401, f"Expected 401 Unauthorized, got {exp_res.status_code}"
        assert exp_res.json().get("detail") == "Invalid or expired authentication token.", "Unexpected 401 error message!"
        print("      [PASS] 401 Expired Token Handling Verified!", flush=True)

        # Step 5: Test POST /auth/refresh with Expired Token
        print("\n[5/6] Testing POST /auth/refresh with Expired Token...", flush=True)
        refresh_res = client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        print(f"      Status Code: {refresh_res.status_code}", flush=True)
        assert refresh_res.status_code == 200, f"Expected 200 OK for refresh, got {refresh_res.status_code}"
        ref_data = refresh_res.json()
        new_token = ref_data.get("token")
        assert new_token is not None, "Refresh did not return a new token!"
        print(f"      New Refreshed Token Issued: {new_token[:30]}...", flush=True)
        print("      [PASS] Token Refresh Mechanism Verified!", flush=True)

        # Step 6: Test POST /query with Refreshed Token
        print("\n[6/6] Executing POST /query with Refreshed Token...", flush=True)
        final_res = client.post(
            "/query",
            json={"query": "What are the benefits of MCP?", "k": 2},
            headers={"Authorization": f"Bearer {new_token}"},
        )
        print(f"      Status: {final_res.status_code}", flush=True)
        assert final_res.status_code == 200, f"Expected 200 OK with refreshed token, got {final_res.status_code}"
        final_data = final_res.json()
        assert final_data.get("success") is True, "Query failed after token refresh!"
        final_res_dict = final_data.get('response') or {}
        final_ans_str = str(final_res_dict.get('answer', '') or '').encode('ascii', errors='ignore').decode('ascii')
        print(f"      RAG Answer Snippet: {final_ans_str[:100]}...", flush=True)
        print("      [PASS] RAG Query Execution with Refreshed Token Passed!", flush=True)
        print("      [PASS] RAG Query Execution with Refreshed Token Passed!")

        print("\n" + "=" * 75)
        print("          ALL AUTHENTICATION & REFRESH TESTS PASSED!          ")
        print("=" * 75 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    test_auth_and_refresh_flow()
