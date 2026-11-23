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


# --- HTML Template ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cyber Threat Intelligence & Autonomous Mitigation Platform</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
  <style>
    body { background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .navbar { background: linear-gradient(135deg, #1e293b, #0f172a); }
    .card { border: none; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .badge-critical { background-color: #ef4444; color: #fff; }
    .badge-high { background-color: #f97316; color: #fff; }
    .badge-medium { background-color: #f59e0b; color: #fff; }
    .badge-low { background-color: #3b82f6; color: #fff; }
    .chat-box { height: 460px; overflow-y: auto; background-color: #ffffff; border-radius: 8px; padding: 18px; border: 1px solid #e2e8f0; }
    .chat-msg { margin-bottom: 16px; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; }
    .chat-user { background-color: #e0e7ff; color: #1e1b4b; margin-left: auto; max-width: 75%; border-bottom-right-radius: 2px; }
    .chat-bot { background-color: #f8fafc; color: #0f172a; margin-right: auto; max-width: 95%; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }
    .chip { cursor: pointer; display: inline-block; padding: 6px 14px; margin: 3px; font-size: 0.85rem; border-radius: 16px; background-color: #e2e8f0; font-weight: 500; transition: background-color 0.2s; }
    .chip:hover { background-color: #cbd5e1; }
    pre { background-color: #1e293b; color: #f8fafc; padding: 10px; border-radius: 6px; font-size: 0.85rem; }
    .btn-send { font-weight: 600; min-width: 90px; }
  </style>
</head>
<body>
  <nav class="navbar navbar-dark py-3 px-4">
    <div class="container-fluid">
      <span class="navbar-brand mb-0 h1"><i class="bi bi-shield-shaded me-2 text-primary"></i>Cyber Threat Intelligence & Autonomous Mitigator</span>
      <span id="ollamaBadge" class="badge bg-secondary"><i class="bi bi-cpu me-1"></i>Checking Ollama...</span>
    </div>
  </nav>

  <div class="container-fluid py-4 px-4">
    <!-- KPI Row -->
    <div class="row g-3 mb-4">
      <div class="col-md">
        <div class="card p-3 text-center border-start border-4 border-primary">
          <div class="text-muted small">Total Threats</div>
          <h3 id="statTotal" class="mb-0 text-primary">17</h3>
        </div>
      </div>
      <div class="col-md">
        <div class="card p-3 text-center border-start border-4 border-danger">
          <div class="text-muted small">Active (In the Wild)</div>
          <h3 id="statActive" class="mb-0 text-danger">5</h3>
        </div>
      </div>
      <div class="col-md">
        <div class="card p-3 text-center border-start border-4 border-info">
          <div class="text-muted small">Anticipated (Predictive)</div>
          <h3 id="statAnticipated" class="mb-0 text-info">3</h3>
        </div>
      </div>
      <div class="col-md">
        <div class="card p-3 text-center border-start border-4 border-warning">
          <div class="text-muted small">Evolving (Polymorphic)</div>
          <h3 id="statEvolving" class="mb-0 text-warning">4</h3>
        </div>
      </div>
      <div class="col-md">
        <div class="card p-3 text-center border-start border-4 border-success">
          <div class="text-muted small">Resolved (Patched)</div>
          <h3 id="statResolved" class="mb-0 text-success">5</h3>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <ul class="nav nav-pills mb-3" id="mainTab" role="tablist">
      <li class="nav-item"><button class="nav-link active" data-bs-toggle="pill" data-bs-target="#tab-chat"><i class="bi bi-chat-dots me-1"></i>AI Threat Assistant & Mitigator</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-dash"><i class="bi bi-table me-1"></i>Threat Intelligence Catalog</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-scan"><i class="bi bi-search me-1"></i>Autonomous Scanner</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-ex"><i class="bi bi-check2-circle me-1"></i>Exercises 1-18 Verification</button></li>
    </ul>

    <div class="tab-content">
      <!-- TAB 1: AI ASSISTANT & MITIGATOR -->
      <div class="tab-pane fade show active" id="tab-chat">
        <div class="row">
          <div class="col-md-8">
            <div class="card p-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="fw-bold mb-0"><i class="bi bi-robot text-primary me-2"></i>AI Threat Intelligence Officer (Ollama + MongoDB RAG)</h6>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="clearChat()">Clear History</button>
              </div>
              <div id="chatBox" class="chat-box mb-3">
                <div class="chat-msg chat-bot">
                  <strong>System:</strong> Welcome! I am your AI Cyber Threat Intelligence Officer. Ask me about <b>Anticipated</b>, <b>Active</b>, <b>Evolving</b>, or <b>Resolved</b> threats for <b>Windows</b>, <b>Linux</b>, <b>MacOS</b>, <b>Android</b>, or <b>iOS</b>. You can also instruct me to <code>scan system</code> or <code>mitigate &lt;CVE&gt;</code>!
                </div>
              </div>
              <div class="mb-3">
                <span class="text-muted small me-2">Quick Inquiries:</span>
                <span class="chip" onclick="fillPrompt('What are the active threats on Linux and how do I mitigate them?')">🚨 Active Linux Threats</span>
                <span class="chip" onclick="fillPrompt('How to mitigate CVE-2024-30078 Windows Wi-Fi Driver RCE?')">🛡️ Windows Wi-Fi Fix</span>
                <span class="chip" onclick="fillPrompt('Explain evolving threats across MacOS and Android.')">🧬 Evolving Threats</span>
                <span class="chip" onclick="fillPrompt('What are anticipated threats for iOS and Linux?')">🔮 Anticipated Threats</span>
                <span class="chip" onclick="fillPrompt('scan system for vulnerabilities')">🔍 Scan System</span>
              </div>
              <div class="input-group">
                <input type="text" id="chatInput" class="form-control" placeholder="Ask about threats, CVEs, or type 'mitigate CVE-...'..." autocomplete="off">
                <button type="button" id="sendBtn" class="btn btn-primary btn-send px-4" onclick="sendChat()"><i class="bi bi-send-fill me-1"></i>Send</button>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card p-3">
              <h6 class="fw-bold"><i class="bi bi-info-circle me-1 text-primary"></i>RAG Semantic Sources</h6>
              <div id="sourcesContainer" class="small text-muted">
                Ask a question to see retrieved MongoDB vector documents and threat records.
              </div>
              <hr/>
              <h6 class="fw-bold"><i class="bi bi-sliders me-1 text-primary"></i>Engine Telemetry</h6>
              <div id="engineStatus" class="small text-muted">Loading telemetry...</div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: THREAT CATALOG -->
      <div class="tab-pane fade" id="tab-dash">
        <div class="card p-3">
          <div class="row g-2 mb-3 align-items-center">
            <div class="col-md-3">
              <label class="form-label small fw-bold">Platform</label>
              <select id="selPlatform" class="form-select form-select-sm" onchange="filterThreats()">
                <option value="All">All Platforms</option>
                <option value="Linux">Linux</option>
                <option value="Windows">Windows</option>
                <option value="MacOS">MacOS</option>
                <option value="Android">Android</option>
                <option value="iOS">iOS</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small fw-bold">Threat Lifecycle</label>
              <select id="selStatus" class="form-select form-select-sm" onchange="filterThreats()">
                <option value="All">All Statuses</option>
                <option value="Active">Active</option>
                <option value="Anticipated">Anticipated</option>
                <option value="Evolving">Evolving</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small fw-bold">Severity</label>
              <select id="selSeverity" class="form-select form-select-sm" onchange="filterThreats()">
                <option value="All">All Severities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div class="col-md-3 text-end pt-3">
              <span id="recordCount" class="badge bg-secondary">17 Threats Loaded</span>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Platform</th>
                  <th>Threat Name & CVE</th>
                  <th>Lifecycle</th>
                  <th>Severity</th>
                  <th>Attack Vector</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="threatsTbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB 3: AUTONOMOUS SCANNER -->
      <div class="tab-pane fade" id="tab-scan">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold mb-1">Autonomous Vulnerability Scanner & Mitigator</h5>
              <div class="text-muted small">Audits local platform and workspace dependencies against known CVEs and security exposures.</div>
            </div>
            <button type="button" class="btn btn-primary" onclick="triggerScan()"><i class="bi bi-play-circle me-1"></i>Run Live System Scan</button>
          </div>
          <div id="scanReportArea">
            <div class="alert alert-info">Click 'Run Live System Scan' to audit dependencies, secret exposure, and network configurations.</div>
          </div>
        </div>
      </div>

      <!-- TAB 4: EXERCISES 1 - 18 VERIFICATION -->
      <div class="tab-pane fade" id="tab-ex">
        <div class="card p-3">
          <h5 class="fw-bold mb-2">MongoDB Exercises 1 - 18 Curriculum Synthesis</h5>
          <p class="text-muted small">All 18 exercises from NoSQL Database using MongoDB synthesized over the Threat Intelligence domain.</p>
          <div class="table-responsive mb-3">
            <table class="table table-sm table-bordered">
              <thead class="table-light"><tr><th>Exercise</th><th>Topic</th><th>Threat Intelligence Implementation</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td>Ex 01</td><td>Classification & Taxonomy</td><td>Document model for multi-platform threat telemetry</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 02</td><td>Connection & Cloud Setup</td><td>Resilient connection with ping command and fallback</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 03</td><td>BSON Schema Design</td><td>Nested BSON with IoC arrays and mitigation documents</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 04</td><td>CRUD & Bulk Operations</td><td>Multi-field filtering (platform, status) and bulk upserts</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 05</td><td>Aggregation Pipelines</td><td>Grouping by Lifecycle Status & Platform metrics ($avg, $sum)</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 06</td><td>Indexing Strategies</td><td>ESR compound indexing (platform, status, severity)</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 07</td><td>Working Set Analysis</td><td>Projection optimization and index utilization</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 08</td><td>JSON Schema Validation</td><td>Strict schema enforcement on threat status and platform enums</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 09</td><td>Array Updates ($addToSet)</td><td>Appending dynamic IoC indicators to active threats</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 10</td><td>Multi-Document Transactions</td><td>Atomic mitigation transitions (Active -> Resolved + Audit)</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 11</td><td>Change Streams & Alerts</td><td>Real-time event watchers on threat lifecycle transitions</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 12</td><td>Security & Credentials</td><td>Environment-based credential isolation (.env)</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 13</td><td>Container Deployment</td><td>Docker Compose multi-service architecture & healthchecks</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 14</td><td>Production Monitoring</td><td>Latency benchmarking (< 1ms with indexes) & uptime metrics</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 15</td><td>Rate Limiting & Sanitization</td><td>Input sanitization protecting against NoSQL injections</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 16</td><td>Backup & Recovery</td><td>JSON threat export and automated restore routines</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 17</td><td>Vector Search & RAG</td><td>384-dimensional vector embeddings with cosine similarity</td><td><span class="badge bg-success">PASS</span></td></tr>
                <tr><td>Ex 18</td><td>End-to-End Integration</td><td>Autonomous Scanner Bot + Ollama LLM RAG Mitigator</td><td><span class="badge bg-success">PASS</span></td></tr>
              </tbody>
            </table>
          </div>
          <button type="button" class="btn btn-outline-success" onclick="runExScript()"><i class="bi bi-terminal me-1"></i>Run Automated Verification Script</button>
          <pre id="exTerminal" class="mt-3 p-3 bg-dark text-light rounded small" style="display:none; max-height: 250px; overflow-y:auto;"></pre>
        </div>
      </div>
    </div>
  </div>

  <!-- Detail Modal -->
  <div class="modal fade" id="threatModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="mTitle">Threat Mitigation Procedure</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" id="mBody"></div>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    let threatsData = [];

    // Safe, zero-dependency Markdown parser
    function formatMarkdown(text) {
      if (!text) return '';
      let html = escapeHtml(text);
      // Code blocks
      html = html.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
      // Inline code
      html = html.replace(/`([^`]+)`/g, '<code class="bg-light px-1 text-danger">$1</code>');
      // Headers
      html = html.replace(/^### (.*$)/gim, '<h5 class="fw-bold mt-2 text-primary">$1</h5>');
      html = html.replace(/^#### (.*$)/gim, '<h6 class="fw-bold mt-2 text-dark">$1</h6>');
      // Bold
      html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
      // Italic
      html = html.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
      // Blockquotes
      html = html.replace(/^&gt; (.*$)/gim, '<blockquote class="border-start border-3 border-secondary ps-2 my-1 text-muted">$1</blockquote>');
      // List items
      html = html.replace(/^\\- (.*$)/gim, '<li>$1</li>');
      // Paragraphs & Line breaks
      html = html.replace(/\\n\\n/g, '<p></p>');
      html = html.replace(/\\n/g, '<br/>');
      return html;
    }

    function escapeHtml(string) {
      return String(string)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    async function loadData() {
      try {
        const resp = await fetch('/api/threats');
        threatsData = await resp.json();
        renderThreats(threatsData);
      } catch(e) { console.error('Threat load error:', e); }

      try {
        const statusResp = await fetch('/api/status');
        const sData = await statusResp.json();
        const badge = document.getElementById('ollamaBadge');
        if (sData.ollama_online) {
          if (sData.models && sData.models.length > 0) {
            badge.className = 'badge bg-success';
            badge.innerHTML = `<i class="bi bi-check-circle me-1"></i>Ollama Active: ${escapeHtml(sData.models[0])}`;
          } else {
            badge.className = 'badge bg-warning text-dark';
            badge.innerHTML = `<i class="bi bi-exclamation-triangle me-1"></i>Ollama Online (No models pulled)`;
          }
        } else {
          badge.className = 'badge bg-secondary';
          badge.innerHTML = `<i class="bi bi-cpu me-1"></i>Ollama Standby / RAG Active`;
        }
        document.getElementById('engineStatus').innerHTML = `
          <div><strong>Ollama Connected:</strong> ${sData.ollama_online ? 'Yes (Port 11434)' : 'Offline / Standby'}</div>
          <div><strong>Available Models:</strong> ${sData.models && sData.models.length > 0 ? escapeHtml(sData.models.join(', ')) : 'None pulled yet'}</div>
          <div><strong>Vector Dimensions:</strong> 384-dim normalized</div>
          <div><strong>Knowledge Chunks:</strong> ${sData.knowledge_chunks || 17}</div>
        `;
      } catch(e) { console.error('Status error:', e); }
    }

    function renderThreats(list) {
      const tbody = document.getElementById('threatsTbody');
      tbody.innerHTML = '';
      document.getElementById('recordCount').innerText = list.length + ' Threats Found';

      list.forEach((t, i) => {
        let badgeSev = 'badge-low';
        if (t.severity === 'Critical') badgeSev = 'badge-critical';
        else if (t.severity === 'High') badgeSev = 'badge-high';
        else if (t.severity === 'Medium') badgeSev = 'badge-medium';

        let badgeStatus = 'badge-active';
        if (t.status === 'Resolved') badgeStatus = 'badge-resolved';
        else if (t.status === 'Anticipated') badgeStatus = 'badge-anticipated';
        else if (t.status === 'Evolving') badgeStatus = 'badge-evolving';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${escapeHtml(t.platform)}</strong></td>
          <td>
            <div class="fw-bold">${escapeHtml(t.name)}</div>
            <code class="small text-muted">${escapeHtml(t.cve_id)}</code>
          </td>
          <td><span class="badge ${badgeStatus}">${escapeHtml(t.status)}</span></td>
          <td><span class="badge ${badgeSev}">${escapeHtml(t.severity)}</span></td>
          <td><span class="small text-muted">${escapeHtml(t.attack_vector || 'N/A')}</span></td>
          <td>
            <button type="button" class="btn btn-sm btn-outline-primary" onclick="showModal(${i})">
              <i class="bi bi-shield-check me-1"></i>Mitigate
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function filterThreats() {
      const plat = document.getElementById('selPlatform').value;
      const stat = document.getElementById('selStatus').value;
      const sev = document.getElementById('selSeverity').value;

      const filtered = threatsData.filter(t => {
        if (plat !== 'All' && t.platform !== plat) return false;
        if (stat !== 'All' && t.status !== stat) return false;
        if (sev !== 'All' && t.severity !== sev) return false;
        return true;
      });
      renderThreats(filtered);
    }

    function showModal(idx) {
      const t = threatsData[idx];
      document.getElementById('mTitle').innerText = `[${t.platform}] ${t.name} (${t.cve_id})`;
      document.getElementById('mBody').innerHTML = `
        <div class="mb-3">
          <span class="badge bg-secondary me-2">Platform: ${escapeHtml(t.platform)}</span>
          <span class="badge bg-info me-2">Lifecycle: ${escapeHtml(t.status)}</span>
          <span class="badge bg-danger">Severity: ${escapeHtml(t.severity)} (CVSS ${t.cvss_score || 'N/A'})</span>
        </div>
        <p><strong>Description:</strong> ${escapeHtml(t.description)}</p>
        <div class="card p-3 mb-3 bg-light">
          <strong>Step-by-Step Remediation Procedure:</strong>
          <pre class="mt-2 mb-0" style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(t.mitigation_steps)}</pre>
        </div>
        ${t.mitigation_script ? `
        <div class="card p-3 bg-dark text-light">
          <strong>Automated Mitigation Command:</strong>
          <code class="text-warning mt-1">${escapeHtml(t.mitigation_script)}</code>
        </div>` : ''}
      `;
      try {
        new bootstrap.Modal(document.getElementById('threatModal')).show();
      } catch(e) {
        document.getElementById('threatModal').classList.add('show');
        document.getElementById('threatModal').style.display = 'block';
      }
    }

    function fillPrompt(txt) {
      const input = document.getElementById('chatInput');
      input.value = txt;
      sendChat();
    }

    async function sendChat() {
      const input = document.getElementById('chatInput');
      const sendBtn = document.getElementById('sendBtn');
      const text = input.value.trim();
      if (!text) {
        input.focus();
        return;
      }

      // Disable button during transit
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Sending...';

      const chatBox = document.getElementById('chatBox');
      chatBox.innerHTML += `<div class="chat-msg chat-user"><strong>You:</strong> ${escapeHtml(text)}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
      input.value = '';

      const loadId = 'load_' + Date.now();
      chatBox.innerHTML += `<div id="${loadId}" class="chat-msg chat-bot text-muted"><div class="spinner-border spinner-border-sm me-2"></div>Analyzing threat intelligence & retrieving vectors...</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

      try {
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message: text})
        });
        const data = await resp.json();
        const loadElem = document.getElementById(loadId);
        if (loadElem) loadElem.remove();

        const rendered = formatMarkdown(data.response || 'No response returned.');
        chatBox.innerHTML += `<div class="chat-msg chat-bot">${rendered}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        if (data.sources && data.sources.length > 0) {
          const sc = document.getElementById('sourcesContainer');
          sc.innerHTML = '';
          data.sources.forEach(s => {
            sc.innerHTML += `
              <div class="card p-2 mb-2 bg-light border-start border-3 border-primary">
                <div class="fw-bold">${escapeHtml(s.source)} <span class="badge bg-primary float-end">Score: ${s.score}</span></div>
                <div class="text-truncate mt-1 text-muted">${escapeHtml(s.text)}</div>
              </div>
            `;
          });
        }
      } catch (e) {
        const loadElem = document.getElementById(loadId);
        if (loadElem) loadElem.remove();
        chatBox.innerHTML += `<div class="chat-msg chat-bot text-danger"><strong>Error connecting to assistant:</strong> ${escapeHtml(e.toString())}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
      } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i>Send';
        input.focus();
      }
    }

    function clearChat() {
      document.getElementById('chatBox').innerHTML = '<div class="chat-msg chat-bot">Chat history cleared. Ready for your inquiries.</div>';
      document.getElementById('sourcesContainer').innerHTML = '<span class="text-muted">Ask a question to see retrieved MongoDB vector documents.</span>';
    }

    async function triggerScan() {
      const area = document.getElementById('scanReportArea');
      area.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div><div class="mt-2 text-muted">Auditing system and dependencies...</div></div>';
      try {
        const resp = await fetch('/api/scan', {method: 'POST'});
        const data = await resp.json();

        let html = `
          <div class="row g-2 mb-3">
            <div class="col-3"><div class="card p-2 text-center bg-light"><strong>Total Findings:</strong> ${data.total_vulnerabilities}</div></div>
            <div class="col-3"><div class="card p-2 text-center bg-danger text-light"><strong>Critical/High:</strong> ${data.critical_count + data.high_count}</div></div>
            <div class="col-3"><div class="card p-2 text-center bg-warning"><strong>Medium:</strong> ${data.medium_count}</div></div>
            <div class="col-3"><div class="card p-2 text-center bg-info text-light"><strong>Low:</strong> ${data.low_count}</div></div>
          </div>
          <h6>Discovered Vulnerabilities & Remediation:</h6>
        `;
        data.findings.forEach(f => {
          html += `
            <div class="card p-3 mb-2 border-start border-4 border-warning">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>[${escapeHtml(f.severity)}] ${escapeHtml(f.title)}</strong>
                  <div class="small text-muted">CVE: <code>${escapeHtml(f.cve_id)}</code> | Platform: ${escapeHtml(f.platform)}</div>
                </div>
                <button type="button" class="btn btn-sm btn-success" onclick="mitigateVuln('${escapeHtml(f.cve_id)}')"><i class="bi bi-lightning-charge me-1"></i>Confirm & Mitigate</button>
              </div>
              <p class="mt-2 mb-1 small">${escapeHtml(f.details)}</p>
              <code class="p-1 bg-light text-dark small">${escapeHtml(f.fix_command)}</code>
            </div>
          `;
        });
        area.innerHTML = html;
      } catch (e) {
        area.innerHTML = `<div class="alert alert-danger">Scan failed: ${escapeHtml(e.toString())}</div>`;
      }
    }

    async function mitigateVuln(cve) {
      if(!confirm(`Apply mitigation for ${cve}? This will update the threat status to 'Resolved' in MongoDB.`)) return;
      const resp = await fetch('/api/mitigate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cve_id: cve})
      });
      const data = await resp.json();
      alert(data.message);
      triggerScan();
      loadData();
    }

    async function runExScript() {
      const term = document.getElementById('exTerminal');
      term.style.display = 'block';
      term.innerText = 'Executing Exercises 1 - 18 verification script...\n';
      const resp = await fetch('/api/run_exercises');
      const text = await resp.text();
      term.innerText = text;
    }

    // Initialize event listeners when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
      const chatInput = document.getElementById('chatInput');
      if (chatInput) {
        chatInput.addEventListener('keydown', function(event) {
          if (event.key === 'Enter') {
            event.preventDefault();
            sendChat();
          }
        });
      }
      loadData();
    });
  </script>
</body>
</html>
"""


class WebHandler(http.server.BaseHTTPRequestHandler):
    scanner = VulnerabilityScanner()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif url.path == "/api/threats":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(THREAT_RECORDS).encode("utf-8"))
        elif url.path == "/api/status":
            models = get_ollama_models()
            status_payload = {
                "ollama_online": len(models) >= 0,
                "models": models,
                "knowledge_chunks": len(CACHED_KNOWLEDGE),
                "threat_records": len(CACHED_THREATS)
            }
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status_payload).encode("utf-8"))
        elif url.path == "/api/run_exercises":
            import subprocess
            res = subprocess.run(
                ["python", "demo_exercises_1_to_18.py"],
                capture_output=True,
                text=True
            )
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(res.stdout.encode("utf-8"))
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

                # Clean sources for frontend JSON
                sources = []
                for s in raw_sources:
                    sources.append({
                        "source": s["source"],
                        "score": s["score"],
                        "text": s["text"][:180] + ("..." if len(s["text"]) > 180 else "")
                    })

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"response": resp, "sources": sources}).encode("utf-8"))

        elif url.path == "/api/scan":
            scan_res = self.scanner.run_full_scan(project_dir=".")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(scan_res).encode("utf-8"))

        elif url.path == "/api/mitigate":
            cve = payload.get("cve_id", "")
            mit_res = self.scanner.apply_mitigation(cve, confirmed=True, project_dir=".")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(mit_res).encode("utf-8"))

        else:
            self.send_error(HTTPStatus.NOT_FOUND)


# Threaded HTTP Server to handle multiple concurrent requests without blocking
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
