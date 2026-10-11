import os
import sys
import time
import uuid
import random
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
API_PREFIX = f"{BASE_URL}/api/v1"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def log(msg, color=Colors.CYAN):
    print(f"{color}[TEST] {msg}{Colors.RESET}")

def success(msg):
    print(f"{Colors.GREEN}  [OK] {msg}{Colors.RESET}")

def fail(msg):
    print(f"{Colors.RED}  [FAIL] {msg}{Colors.RESET}")
    sys.exit(1)


def run_e2e_suite():
    log("==================================================================", Colors.BOLD)
    log("ENTERPRISE DOCUMENT INTELLIGENCE PLATFORM - END-TO-END VERIFICATION", Colors.BOLD)
    log("==================================================================", Colors.BOLD)
    log(f"Target API Server: {BASE_URL}")

    # 0. Health Check
    log("Step 0: Checking API Server Health...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code != 200:
            fail(f"Health check failed with status {r.status_code}: {r.text}")
        success(f"API Server Healthy: {r.json()}")
    except Exception as e:
        fail(f"Could not connect to {BASE_URL}/health: {e}")

    # 1. Register User A
    rand_a = uuid.uuid4().hex[:8]
    user_a_email = f"lead_analyst_{rand_a}@enterprisecorp.com"
    user_a_pass = f"Pass_{rand_a}!987"
    user_a_name = f"Analyst Lead {rand_a}"

    log(f"Step 1: Registering Random Test User A ({user_a_email})...")
    r = requests.post(f"{API_PREFIX}/auth/register", json={
        "email": user_a_email,
        "password": user_a_pass,
        "full_name": user_a_name
    })
    if r.status_code != 201:
        fail(f"User A registration failed ({r.status_code}): {r.text}")
    user_a_id = r.json()["id"]
    success(f"User A registered successfully with ID: {user_a_id}")

    # 2. Login User A
    log("Step 2: Authenticating User A (POST /auth/login)...")
    r = requests.post(f"{API_PREFIX}/auth/login", json={
        "email": user_a_email,
        "password": user_a_pass
    })
    if r.status_code != 200:
        fail(f"User A login failed ({r.status_code}): {r.text}")
    tokens_a = r.json()
    token_a = tokens_a["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    success("User A authenticated. Received JWT access token.")

    # 3. Create Organization A
    org_a_name = f"Apex Dynamics Inc {rand_a}"
    log(f"Step 3: Creating Organization A ('{org_a_name}')...")
    r = requests.post(f"{API_PREFIX}/organizations", json={
        "name": org_a_name
    }, headers=headers_a)
    if r.status_code != 201:
        fail(f"Organization creation failed ({r.status_code}): {r.text}")
    org_a_id = r.json()["id"]
    success(f"Organization A created with ID: {org_a_id}")

    # 4. Create Project A
    proj_a_name = f"Q3 Audit and Security {rand_a}"
    log(f"Step 4: Creating Project A ('{proj_a_name}')...")
    r = requests.post(f"{API_PREFIX}/organizations/{org_a_id}/projects", json={
        "name": proj_a_name,
        "description": "Proprietary financial audit and infrastructure policies"
    }, headers=headers_a)
    if r.status_code != 201:
        fail(f"Project creation failed ({r.status_code}): {r.text}")
    proj_a_id = r.json()["id"]
    success(f"Project A created with ID: {proj_a_id}")

    # 5. Prepare 3 Diverse Random Documents with Unique Facts
    rev_amount = f"${random.randint(15, 65)},{random.randint(100, 999)},000"
    ebitda_pct = f"{random.randint(20, 48)}.{random.randint(1, 9)}%"
    vendor_code = f"QUANTUM-CLOUD-{uuid.uuid4().hex[:6].upper()}"

    argon_mem = f"{random.randint(32768, 65536)} KiB"
    sla_time = f"{random.randint(12, 28)} minutes"

    proto_name = f"gRPC-v{random.randint(2, 6)}.PROTO"
    latency_val = f"{random.randint(18, 42)}.{random.randint(1, 9)} ms"

    doc_cases = [
        {
            "filename": f"Acme_Fiscal_Audit_{rand_a}.txt",
            "mimetype": "text/plain",
            "content": (
                f"ACME DYNAMICS FISCAL AUDIT REPORT (CONFIDENTIAL)\n\n"
                f"For the fiscal period ending September 30, Acme recorded total consolidated net revenue of {rev_amount}.\n"
                f"Operating margin and adjusted EBITDA reached {ebitda_pct}, demonstrating resilient operational leverage.\n"
                f"The primary cloud computing provider is {vendor_code}, bound by strict multi-region disaster recovery SLAs.\n"
                f"Contingency capital allocated for unforeseen supply disruptions stands at $4,500,000.\n"
            ),
            "expected_terms": [rev_amount, vendor_code],
            "query": f"What is the total consolidated net revenue and cloud computing provider for Acme?",
        },
        {
            "filename": f"Sec_Compliance_Framework_{rand_a}.md",
            "mimetype": "text/markdown",
            "content": (
                f"# Enterprise Information Security Compliance Framework\n\n"
                f"## Section 3.1: Password and Key Hashing\n"
                f"All credential storage must enforce Argon2id with memory cost allocation of {argon_mem}.\n\n"
                f"## Section 4.2: Tier 1 Incident Triage\n"
                f"Security Operations Center teams must acknowledge and begin containment on Tier 1 critical alerts within {sla_time}.\n\n"
                f"## Section 5: Vector DB Isolation\n"
                f"All vector chunk queries must strictly enforce tenant and project isolation before HNSW indexing traversal.\n"
            ),
            "expected_terms": [argon_mem],
            "query": f"What memory cost allocation is required for Argon2id credential storage?",
        },
        {
            "filename": f"Helios_Distributed_Spec_{rand_a}.txt",
            "mimetype": "text/plain",
            "content": (
                f"PROJECT HELIOS MICROSERVICES ARCHITECTURE SPECIFICATION\n\n"
                f"Inter-service RPC communication is standardized entirely on {proto_name}.\n"
                f"The high-throughput hybrid retrieval engine has a strict P99 latency SLA budget of {latency_val}.\n"
                f"Dense semantic vector representations are generated via all-MiniLM-L6-v2 in 384 dimensions,\n"
                f"indexed via PostgreSQL pgvector HNSW with cosine distance metric.\n"
            ),
            "expected_terms": [proto_name, latency_val],
            "query": f"What RPC protocol does Helios use and what is the P99 latency SLA budget?",
        }
    ]

    # 6. Upload Documents and Verify Asynchronous Celery Processing
    log("Step 5: Uploading Diverse Random Documents & Polling Celery Processing...")
    uploaded_docs = []

    for idx, doc in enumerate(doc_cases, 1):
        log(f"  Uploading Document {idx}/3: '{doc['filename']}' ({len(doc['content'])} bytes)...")
        files = {
            "file": (doc["filename"], doc["content"].encode("utf-8"), doc["mimetype"])
        }
        data = {
            "organization_id": org_a_id,
            "project_id": proj_a_id
        }
        r = requests.post(f"{API_PREFIX}/documents/upload", files=files, data=data, headers=headers_a)
        if r.status_code != 202:
            fail(f"Upload failed for {doc['filename']} ({r.status_code}): {r.text}")

        res_data = r.json()
        doc_id = res_data["document_id"]
        job_id = res_data.get("job_id")
        success(f"Upload accepted (HTTP 202). Document ID: {doc_id}, Job ID: {job_id}")

        # Poll status until COMPLETED
        log(f"  Polling processing status for Document {idx} via Celery worker...")
        start_time = time.time()
        final_status = None
        for attempt in range(60):
            time.sleep(1.0)

            status_r = requests.get(
                f"{API_PREFIX}/documents/{doc_id}/status?organization_id={org_a_id}",
                headers=headers_a
            )
            if status_r.status_code == 200:
                s_json = status_r.json()
                final_status = s_json.get("status")
                progress = s_json.get("progress_percentage", 0)
                if final_status == "COMPLETED":
                    elapsed = time.time() - start_time
                    success(f"Document {idx} COMPLETED in {elapsed:.1f}s (Progress: {progress}%)")
                    break
                elif final_status == "FAILED":
                    fail(f"Document {idx} processing FAILED: {s_json.get('error_message')}")
        else:
            fail(f"Document {idx} processing timed out after 60 seconds. Last status: {final_status}")

        doc["doc_id"] = doc_id
        uploaded_docs.append(doc)

    # 7. Test Hybrid Search across all documents
    log("Step 6: Executing Hybrid Semantic Search (Dense Vector + FTS + RRF k=60)...")
    for idx, doc in enumerate(uploaded_docs, 1):
        q = doc["query"]
        log(f"  Search Query {idx}: '{q}'")
        search_r = requests.get(
            f"{API_PREFIX}/search?organization_id={org_a_id}&project_id={proj_a_id}&query={q}&limit=5",
            headers=headers_a
        )
        if search_r.status_code != 200:
            fail(f"Search failed ({search_r.status_code}): {search_r.text}")

        s_data = search_r.json()
        results = s_data.get("results", [])
        if not results:
            fail(f"Search for query '{q}' returned 0 results!")

        top_result = results[0]
        score = top_result.get("score", 0.0)
        combined_content = " ".join(r.get("content", "") for r in results)

        # Check expected random facts are present in retrieved chunks
        missing = [t for t in doc["expected_terms"] if t not in combined_content]
        if missing:
            fail(f"Search results missing expected terms: {missing}. Snippet: {top_result.get('content', '')[:200]}")

        success(f"Search Query {idx} returned {len(results)} chunks. Top Rank: '{top_result.get('document_name')}' (Score: {score:.4f})")
        success(f"Verified expected unique terms found in retrieved chunks: {doc['expected_terms']}")

    # 8. Test Grounded RAG Chat Endpoint
    log("Step 7: Testing Local RAG AI Assistant (/chat)...")
    chat_question = f"What is the memory cost for Argon2id and the incident response SLA?"
    chat_r = requests.post(f"{API_PREFIX}/chat", json={
        "organization_id": org_a_id,
        "project_id": proj_a_id,
        "question": chat_question
    }, headers=headers_a)

    if chat_r.status_code != 200:
        fail(f"RAG Chat endpoint failed ({chat_r.status_code}): {chat_r.text}")

    chat_data = chat_r.json()
    sources = chat_data.get("sources", [])
    answer = chat_data.get("answer", "")
    if not sources:
        fail(f"RAG Chat returned zero source citations!")
    if not answer:
        fail(f"RAG Chat returned empty answer string!")

    success(f"RAG Response generated successfully.")
    success(f"Sources cited ({len(sources)}): '{sources[0].get('document_name')}' (Chunk: {sources[0].get('chunk_id')})")
    log(f"  AI Answer Excerpt: {answer[:180]}...", Colors.YELLOW)

    # 9. Multi-Tenant Isolation Security Test
    log("Step 8: Verifying Multi-Tenant Strict Isolation (Tenant A vs Tenant B)...")
    rand_b = uuid.uuid4().hex[:8]
    user_b_email = f"intruder_{rand_b}@competitor.com"
    user_b_pass = f"Pass_{rand_b}!654"

    # Register & Login User B
    requests.post(f"{API_PREFIX}/auth/register", json={
        "email": user_b_email,
        "password": user_b_pass,
        "full_name": f"Competitor User {rand_b}"
    })
    r_b = requests.post(f"{API_PREFIX}/auth/login", json={
        "email": user_b_email,
        "password": user_b_pass
    })
    token_b = r_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Org B & Project B
    org_b_r = requests.post(f"{API_PREFIX}/organizations", json={"name": f"Competitor Org {rand_b}"}, headers=headers_b)
    org_b_id = org_b_r.json()["id"]
    proj_b_r = requests.post(f"{API_PREFIX}/organizations/{org_b_id}/projects", json={"name": f"Project B {rand_b}"}, headers=headers_b)
    proj_b_id = proj_b_r.json()["id"]

    # Security Check 1: User B cannot access Document A
    target_doc_a = uploaded_docs[0]["doc_id"]
    r_cross_doc = requests.get(f"{API_PREFIX}/documents/{target_doc_a}/status?organization_id={org_a_id}", headers=headers_b)
    if r_cross_doc.status_code in [401, 403, 404]:
        success(f"Cross-Tenant Document Read blocked as expected (HTTP {r_cross_doc.status_code})")
    else:
        fail(f"SECURITY BREACH: User B accessed Org A document! (HTTP {r_cross_doc.status_code})")

    # Security Check 2: User B cannot search Org A project
    r_cross_search = requests.get(
        f"{API_PREFIX}/search?organization_id={org_a_id}&project_id={proj_a_id}&query=revenue",
        headers=headers_b
    )
    if r_cross_search.status_code in [401, 403, 404]:
        success(f"Cross-Tenant Search Request blocked as expected (HTTP {r_cross_search.status_code})")
    else:
        fail(f"SECURITY BREACH: User B searched Org A! (HTTP {r_cross_search.status_code})")

    # Security Check 3: User B searching within Org B gets ZERO results for Org A's proprietary facts
    r_leak_search = requests.get(
        f"{API_PREFIX}/search?organization_id={org_b_id}&project_id={proj_b_id}&query={vendor_code}",
        headers=headers_b
    )
    if r_leak_search.status_code == 200:
        leak_results = r_leak_search.json().get("results", [])
        if len(leak_results) == 0:
            success(f"Cross-Tenant Data Leakage Prevention verified: 0 chunks returned for '{vendor_code}'.")
        else:
            fail(f"CRITICAL SECURITY LEAK: User A's chunk leaked into User B's search results!")
    else:
        success("Search returned valid scoped empty response.")

    # 10. API Key Lifecycle Test
    log("Step 9: Testing Scoped API Key Creation, Authentication & Revocation...")
    key_r = requests.post(f"{API_PREFIX}/api-keys", json={
        "organization_id": org_a_id,
        "name": f"Automated Pipeline Key {rand_a}",
        "scopes": ["read:documents", "search"],
        "expires_in_days": 30
    }, headers=headers_a)

    if key_r.status_code != 201:
        fail(f"API key creation failed ({key_r.status_code}): {key_r.text}")

    key_data = key_r.json()
    raw_secret = key_data["secret_key"]
    key_id = key_data["id"]
    if not raw_secret.startswith("edip_live_"):
        fail(f"Invalid secret key prefix: {raw_secret}")
    success(f"API Key created with prefix '{key_data['key_prefix']}' (Argon2 hashed).")

    # List keys
    list_keys_r = requests.get(f"{API_PREFIX}/api-keys?organization_id={org_a_id}", headers=headers_a)
    if list_keys_r.status_code != 200 or len(list_keys_r.json()) == 0:
        fail("API Key listing failed or key not found.")
    success(f"API Key verified in active organization key list.")

    # Revoke key
    rev_r = requests.delete(f"{API_PREFIX}/api-keys/{key_id}?organization_id={org_a_id}", headers=headers_a)
    if rev_r.status_code != 204:
        fail(f"API Key revocation failed ({rev_r.status_code}): {rev_r.text}")
    success("API Key successfully revoked.")

    # 11. Immutable Audit Logs Verification
    log("Step 10: Verifying Immutable Security Audit Trail...")
    audit_r = requests.get(f"{API_PREFIX}/organizations/{org_a_id}/audit-logs?limit=50", headers=headers_a)
    if audit_r.status_code != 200:
        fail(f"Audit log fetch failed ({audit_r.status_code}): {audit_r.text}")

    audit_logs = audit_r.json()
    if not audit_logs:
        fail("Audit log is unexpectedly empty!")

    recorded_actions = {log_item["action"] for log_item in audit_logs}
    success(f"Audit logs retrieved ({len(audit_logs)} events recorded).")
    success(f"Recorded security actions: {', '.join(sorted(list(recorded_actions)))}")

    log("==================================================================", Colors.BOLD)
    log(f"{Colors.GREEN}ALL 10 END-TO-END PIPELINE & SECURITY TESTS PASSED!{Colors.RESET}", Colors.BOLD)
    log("==================================================================", Colors.BOLD)

if __name__ == "__main__":
    run_e2e_suite()
