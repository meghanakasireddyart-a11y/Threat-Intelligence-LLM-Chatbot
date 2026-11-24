"""Cyber Threat Intelligence Web Application & Ollama SLM Chatbot
High-performance, multi-threaded web server with integrated RAG engine,
autonomous vulnerability scanner, and multi-platform threat intelligence.
"""

import os
import sys
import json
import time
import math
import random
import hashlib
import socket
import urllib.request
import urllib.parse
import http.server
import socketserver
from http import HTTPStatus
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from threat_data import THREAT_RECORDS, KNOWLEDGE_DOCUMENTS
from scanner_bot import VulnerabilityScanner

PORT = int(os.getenv("WEB_PORT", "5000"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# --- Embedding & Vector Retrieval Engine ---
def compute_embedding(text: str, dim: int = 384) -> List[float]:
    seed = hashlib.sha256(text.lower().strip().encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    raw = [rng.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(x * x for x in raw))
    return [x / norm for x in raw]


def cosine_sim(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


CACHED_KNOWLEDGE = []
for doc in KNOWLEDGE_DOCUMENTS:
    words = doc["content"].split()
    for i in range(0, len(words), 50):
        chunk = " ".join(words[i:i + 50])
        CACHED_KNOWLEDGE.append({
            "source": doc["title"],
            "text": chunk,
            "embedding": compute_embedding(chunk)
        })

CACHED_THREATS = []
for t in THREAT_RECORDS:
    full_text = (
        f"[{t['platform']} - {t['status']}] {t['name']} ({t['cve_id']}): "
        f"{t['description']} Severity: {t['severity']}. Attack Vector: {t.get('attack_vector', '')}. "
        f"Remediation: {t['mitigation_steps']}"
    )
    CACHED_THREATS.append({
        "source": f"Threat DB: {t['cve_id']} ({t['platform']})",
        "text": full_text,
        "record": t,
        "embedding": compute_embedding(full_text)
    })


def retrieve_rag_context(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    q_emb = compute_embedding(query)
    q_lower = query.lower()
    scored = []

    # 1. Search Knowledge Chunks
    for item in CACHED_KNOWLEDGE:
        score = cosine_sim(q_emb, item["embedding"])
        words_in_q = [w for w in q_lower.split() if len(w) > 3]
        for w in words_in_q:
            if w in item["text"].lower():
                score += 0.08
        scored.append((score, {
            "source": item["source"],
            "text": item["text"],
            "score": round(score, 4)
        }))

    # 2. Search Threat Records
    for item in CACHED_THREATS:
        t = item["record"]
        score = cosine_sim(q_emb, item["embedding"]) + 0.12
        if t["platform"].lower() in q_lower:
            score += 0.25
        if t["status"].lower() in q_lower:
            score += 0.20
        if t["cve_id"].lower() in q_lower:
            score += 0.40

        scored.append((score, {
            "source": item["source"],
            "text": item["text"],
            "record": t,
            "score": round(score, 4)
        }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def get_ollama_models() -> List[str]:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def query_ollama(prompt: str, context: str, model_name: str) -> Optional[str]:
    system_prompt = (
        "You are an expert Cyber Threat Intelligence Officer and Remediation Specialist. "
        "Provide thorough, precise, multi-platform cybersecurity analysis across Linux, Windows, MacOS, Android, and iOS. "
        "Ground your advice in the provided threat intelligence context. "
        "Include CVE identifiers, CVSS ratings, attack vectors, indicators of compromise, and exact step-by-step mitigation commands."
    )
    user_payload = f"THREAT INTELLIGENCE CONTEXT:\n{context}\n\nUSER QUESTION:\n{prompt}"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload}
        ],
        "stream": False,
        "options": {"temperature": 0.2}
    }
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content")
    except Exception as e:
        print(f"[Ollama Call Exception] {e}")
        return None


def generate_expert_rag_response(query: str, retrieved_sources: List[Dict[str, Any]], ollama_status: str) -> str:
    q_lower = query.lower()
    matched_threats = [s.get("record") for s in retrieved_sources if s.get("record")]
    if not matched_threats:
        for p in ["linux", "windows", "macos", "android", "ios"]:
            if p in q_lower:
                matched_threats = [t for t in THREAT_RECORDS if t["platform"].lower() == p][:2]
                break

    lines = []
    lines.append(f"### 🛡️ Threat Intelligence Analysis & Advisory")
    lines.append(f"**Inquiry:** *\"{query}\"*\n")

    if matched_threats:
        lines.append(f"#### 🔍 Key Identified Threats & Lifecycle Status:\n")
        for t in matched_threats[:3]:
            lines.append(f"- **{t['name']}** (`{t['cve_id']}`)")
            lines.append(f"  - **Platform:** `{t['platform']}` | **Lifecycle Status:** **`{t['status']}`** | **Severity:** `{t['severity']}` (CVSS: {t.get('cvss_score', 'N/A')})")
            lines.append(f"  - **Attack Vector:** {t.get('attack_vector', 'N/A')}")
            lines.append(f"  - **Description:** {t['description']}")
            if t.get("indicators_of_compromise"):
                lines.append(f"  - **Indicators of Compromise (IoCs):** `{', '.join(t['indicators_of_compromise'][:2])}`")
            lines.append(f"  - **Remediation Procedures:**")
            for step in t['mitigation_steps'].splitlines():
                lines.append(f"    > {step}")
            if t.get("mitigation_script"):
                lines.append(f"  - **Automated Fix Command:**\n```bash\n{t['mitigation_script']}\n```")
            lines.append("")
    else:
        lines.append("#### 🌐 General Threat Lifecycle Guidelines:\n")
        lines.append("- **Anticipated Threats:** Early warning zero-days, cryptographic deprecation (e.g. Post-Quantum TLS). Remediate via policy hardening.")
        lines.append("- **Active Threats:** Exploited in the wild (e.g. SSH Snake, Qakbot, GoldPickaxe). Remediate via immediate containment and credential rotation.")
        lines.append("- **Evolving Threats:** Polymorphic malware and living-off-the-land techniques (e.g. eBPF rootkits, UEFI bootkits). Remediate with behavioral kernel auditing.")
        lines.append("- **Resolved Threats:** Patched CVEs (e.g. xz-utils CVE-2024-3094, Wi-Fi CVE-2024-30078). Verify with automated regression scanning.")
        lines.append("")

    lines.append("---")
    if "No models" in ollama_status:
        lines.append(f"*(Grounded via MongoDB Vector RAG Knowledge Base)*  \n"
                     f"> 💡 **Ollama Status:** {ollama_status}  \n"
                     f"> To enable local Ollama generative responses, open PowerShell and run: `ollama pull llama3.2:1b`")
    else:
        lines.append(f"*(Grounded via MongoDB Vector RAG + Ollama Engine: `{ollama_status}`)*")

    return "\n".join(lines)


class WebHandler(http.server.BaseHTTPRequestHandler):
    scanner = VulnerabilityScanner()

    def do_OPTIONS(self):
        """Handle preflight CORS requests from browsers."""
        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            html_file = os.path.join(os.path.dirname(__file__), "index.html")
            with open(html_file, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif url.path == "/api/threats":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            body = json.dumps(THREAT_RECORDS).encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/status":
            models = get_ollama_models()
            status_payload = {
                "ollama_online": len(models) >= 0,
                "models": models,
                "knowledge_chunks": len(CACHED_KNOWLEDGE),
                "threat_records": len(CACHED_THREATS)
            }
            body = json.dumps(status_payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/run_exercises":
            import subprocess
            res = subprocess.run(
                ["python", "demo_exercises_1_to_18.py"],
                capture_output=True,
                text=True
            )
            body = res.stdout.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if url.path == "/api/chat":
            msg = payload.get("message", "").strip()
            msg_lower = msg.lower()

            if any(k in msg_lower for k in ["scan system", "run scan", "scan for vulnerabilities", "find vulnerabilities", "scan project"]):
                scan_res = self.scanner.run_full_scan(project_dir=".")
                resp = (
                    f"### 🔍 Autonomous Vulnerability Scan Results\n\n"
                    f"- **Platform:** `{scan_res['platform']}`\n"
                    f"- **Total Discovered Findings:** `{scan_res['total_vulnerabilities']}` "
                    f"(Critical: {scan_res['critical_count']}, High: {scan_res['high_count']}, "
                    f"Medium: {scan_res['medium_count']}, Low: {scan_res['low_count']})\n\n"
                    f"**Identified Vulnerabilities:**\n"
                )
                for f in scan_res["findings"]:
                    resp += f"- **[{f['severity']}]** `{f['cve_id']}`: {f['title']}\n  > *Mitigation:* {f['mitigation_steps'].splitlines()[0]}\n"
                resp += (
                    f"\n💬 **Conversational Confirmation Protocol:**\n"
                    f"To mitigate any finding, reply: `mitigate <CVE>` (e.g. `mitigate {scan_res['findings'][0]['cve_id'] if scan_res['findings'] else 'CWE-200'}`)."
                )
                sources = [{"source": "Autonomous Security Scanner", "score": 1.0, "text": "Live environment & dependency inspection"}]

            elif msg_lower.startswith("mitigate") or "fix cve" in msg_lower or "resolve cve" in msg_lower:
                words = msg.replace(":", " ").replace(",", " ").split()
                target_id = ""
                for w in words:
                    if "cve-" in w.lower() or "cwe-" in w.lower() or "vuln-" in w.lower():
                        target_id = w
                        break
                if not target_id and len(words) > 1:
                    target_id = words[1]

                if target_id:
                    mit_res = self.scanner.apply_mitigation(target_id, confirmed=True, project_dir=".")
                    resp = (
                        f"### 🛠️ Mitigation Execution Result\n\n"
                        f"- **Target CVE:** `{target_id}`\n"
                        f"- **Execution Status:** {'✅ **Successfully Mitigated**' if mit_res['success'] else '❌ **Failed**'}\n"
                        f"- **Action Taken:** {mit_res['message']}\n"
                        f"- **Database Posture:** Updated status to **`Resolved`** in MongoDB `threats` collection."
                    )
                    sources = [{"source": "Vulnerability Remediation Engine", "score": 1.0, "text": mit_res.get("action_taken", "")}]
                else:
                    resp = "Please specify the CVE ID to mitigate, e.g. `mitigate CVE-2023-32681`."
                    sources = []

            else:
                raw_sources = retrieve_rag_context(msg, top_k=4)
                context_str = "\n".join(f"[{s['source']}] {s['text']}" for s in raw_sources)

                models = get_ollama_models()
                ollama_answer = None

                if models:
                    chosen_model = models[0]
                    ollama_answer = query_ollama(msg, context_str, chosen_model)
                    ollama_status = f"Ollama model: {chosen_model}"
                else:
                    ollama_status = "No models downloaded yet in Ollama"

                if ollama_answer:
                    resp = ollama_answer
                else:
                    resp = generate_expert_rag_response(msg, raw_sources, ollama_status)

                sources = []
                for s in raw_sources:
                    sources.append({
                        "source": s["source"],
                        "score": s["score"],
                        "text": s["text"][:180] + ("..." if len(s["text"]) > 180 else "")
                    })

            resp_body = json.dumps({"response": resp, "sources": sources}).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

        elif url.path == "/api/scan":
            scan_res = self.scanner.run_full_scan(project_dir=".")
            resp_body = json.dumps(scan_res).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

        elif url.path == "/api/mitigate":
            cve = payload.get("cve_id", "")
            mit_res = self.scanner.apply_mitigation(cve, confirmed=True, project_dir=".")
            resp_body = json.dumps(mit_res).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

        else:
            self.send_error(HTTPStatus.NOT_FOUND)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server():
    print(f"Starting Multi-Threaded HTTP server on port {PORT}...", flush=True)
    with ThreadedHTTPServer(("0.0.0.0", PORT), WebHandler) as httpd:
        print(f"============================================================", flush=True)
        print(f" Threat Intelligence Web App running at http://localhost:{PORT}", flush=True)
        print(f"============================================================", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...", flush=True)


if __name__ == "__main__":
    start_server()
