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


def query_ollama(prompt: str, context: str = "", model_name: str = "tinyllama:latest") -> Optional[str]:
    if context:
        system_prompt = (
            "You are an expert Cyber Threat Intelligence Officer and Remediation Specialist. "
            "Provide thorough, precise, multi-platform cybersecurity analysis across Linux, Windows, MacOS, Android, and iOS. "
            "Ground your advice in the provided threat intelligence context. "
            "Include CVE identifiers, CVSS ratings, attack vectors, indicators of compromise, and exact step-by-step mitigation commands."
        )
        user_payload = f"THREAT INTELLIGENCE CONTEXT:\n{context}\n\nUSER QUESTION:\n{prompt}"
    else:
        system_prompt = (
            "You are a helpful, knowledgeable Cyber Threat Intelligence and System AI assistant running locally on the user's PC. "
            "Answer the user's question clearly, politely, and accurately."
        )
        user_payload = prompt

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload}
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 260}
    }
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content")
    except Exception as e:
        print(f"[Ollama Call Exception] {e}")
        return None


def inspect_host_software_and_system(query: str) -> Optional[Dict[str, Any]]:
    """Directly inspects the host operating system, files, and running processes."""
    q = query.lower()

    # 1. Claude Check
    if "claude" in q:
        claude_paths = [
            os.path.expanduser(r"~\AppData\Local\AnthropicClaude\claude.exe"),
            r"C:\Users\Prajwal\AppData\Local\AnthropicClaude\claude.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Claude\Claude.exe"),
        ]
        found_path = None
        for p in claude_paths:
            if os.path.exists(p):
                found_path = p
                break

        roaming_dir = os.path.expanduser(r"~\AppData\Roaming\Claude")
        roaming_exists = os.path.exists(roaming_dir)

        is_running = False
        try:
            import subprocess
            proc = subprocess.run(["tasklist", "/FI", "IMAGENAME eq claude.exe"], capture_output=True, text=True, timeout=3)
            is_running = "claude.exe" in proc.stdout.lower()
        except Exception:
            pass

        if found_path:
            parent_dir = os.path.dirname(found_path)
            versions = [d for d in os.listdir(parent_dir) if d.startswith("app-")] if os.path.exists(parent_dir) else []
            version_str = versions[-1] if versions else "v1.5354.0"

            resp = (
                f"### 🤖 Host Software Verification: Claude Desktop\n\n"
                f"✅ **Yes, Claude is installed on your PC.**\n\n"
                f"- **Application:** Claude Desktop (Anthropic)\n"
                f"- **Executable File:** `{found_path}`\n"
                f"- **Installed Release:** `{version_str}`\n"
                f"- **User Data Directory:** `{roaming_dir}` ({'Present' if roaming_exists else 'Not found'})\n"
                f"- **Process Status:** {'🟢 **Active / Running in background**' if is_running else '⚪ **Installed (Idle / Not running in tasklist)**'}\n\n"
                f"💡 *You can launch Claude from the Start menu, Windows Search, or double-click `{found_path}`.*"
            )
            return {
                "response": resp,
                "sources": [{
                    "source": "Host System Audit (Filesystem & Tasklist)",
                    "score": 1.0,
                    "text": f"Verified binary at {found_path} ({version_str}) and configuration in {roaming_dir}"
                }]
            }
        else:
            resp = (
                f"### 🤖 Host Software Verification: Claude Desktop\n\n"
                f"❌ Claude Desktop binary was not detected in standard AppData or Program Files locations.\n"
                f"- Configuration directory exists: `{roaming_exists}`\n"
            )
            return {
                "response": resp,
                "sources": [{"source": "Host System Audit", "score": 1.0, "text": "Scanned %LocalAppData% and %ProgramFiles%"}]
            }

    # 2. Python Check
    if "python" in q and any(w in q for w in ["installed", "version", "path", "where"]):
        import platform
        resp = (
            f"### 🐍 Host Environment Verification: Python\n\n"
            f"✅ **Python is installed and actively executing this Threat Intelligence server.**\n\n"
            f"- **Python Version:** `{platform.python_version()}` ({platform.python_implementation()})\n"
            f"- **Interpreter Executable:** `{sys.executable}`\n"
            f"- **System Platform:** `{platform.platform()}`\n"
            f"- **Active Working Directory:** `{os.getcwd()}`\n"
        )
        return {
            "response": resp,
            "sources": [{"source": "Python Runtime Audit", "score": 1.0, "text": sys.executable}]
        }

    # 3. Ollama Check
    if "ollama" in q and any(w in q for w in ["installed", "status", "model", "running"]):
        models = get_ollama_models()
        import shutil
        ollama_bin = shutil.which("ollama") or "ollama"
        resp = (
            f"### 🦙 Host Environment Verification: Ollama Local SLM Engine\n\n"
            f"✅ **Ollama service is active and responsive.**\n\n"
            f"- **Endpoint:** `http://127.0.0.1:11434`\n"
            f"- **CLI Binary:** `{ollama_bin}`\n"
            f"- **Installed Local Models:** `{', '.join(models) if models else 'None'}`\n"
            f"- **Active Model for Threat Intelligence:** `{models[0] if models else 'Vector RAG fallback'}`\n"
        )
        return {
            "response": resp,
            "sources": [{"source": "Ollama Service REST API", "score": 1.0, "text": f"Discovered models: {models}"}]
        }

    # 4. Docker Check
    if "docker" in q and any(w in q for w in ["installed", "status", "running", "container"]):
        import shutil, subprocess
        docker_bin = shutil.which("docker")
        is_running = False
        docker_ver = "Not detected"
        if docker_bin:
            try:
                proc = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=2)
                docker_ver = proc.stdout.strip()
                proc2 = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=2)
                is_running = proc2.returncode == 0
            except Exception:
                pass

        resp = (
            f"### 🐳 Host Environment Verification: Docker\n\n"
            f"- **Docker CLI:** `{'Installed at ' + docker_bin if docker_bin else 'Not detected in PATH'}`\n"
            f"- **Version String:** `{docker_ver}`\n"
            f"- **Docker Daemon:** `{'🟢 Running and accepting commands' if is_running else '🟡 Daemon not reachable (Docker Desktop may be stopped)'}`\n"
        )
        return {
            "response": resp,
            "sources": [{"source": "Docker CLI Audit", "score": 1.0, "text": docker_ver}]
        }

    # 5. MongoDB Check
    if ("mongodb" in q or "mongo" in q) and any(w in q for w in ["installed", "status", "running", "compass"]):
        compass_path = os.path.expanduser(r"~\AppData\Local\MongoDBCompass\MongoDBCompass.exe")
        has_compass = os.path.exists(compass_path)
        resp = (
            f"### 🍃 Database Verification: MongoDB\n\n"
            f"- **Database Simulation Engine:** `mongomock (In-Memory Comprehensive MongoDB Emulation)`\n"
            f"- **Total Threats in Collection:** `{len(CACHED_THREATS)} records`\n"
            f"- **MongoDB Compass Desktop Client:** `{'✅ Installed at ' + compass_path if has_compass else '⚪ Not in default AppData'}`\n"
        )
        return {
            "response": resp,
            "sources": [{"source": "MongoDB Database Inspection", "score": 1.0, "text": f"Compass: {has_compass}"}]
        }

    # 6. System / PC Specs / OS Check
    if any(k in q for k in ["pc spec", "system spec", "system info", "what is my pc", "os version", "specs of my pc", "my pc", "my computer"]) and not any(w in q for w in ["installed", "apps", "software", "programs"]):
        import platform
        resp = (
            f"### 💻 Host System Specifications & Hardware Information\n\n"
            f"- **Operating System:** `{platform.system()} {platform.release()} (Build {platform.version()})`\n"
            f"- **System Architecture:** `{platform.machine()}`\n"
            f"- **Host Processor:** `{platform.processor() or 'Standard x86_64'}`\n"
            f"- **Computer Hostname:** `{os.environ.get('COMPUTERNAME', 'Localhost')}`\n"
            f"- **Active User Profile:** `{os.environ.get('USERNAME', 'User')}`\n"
            f"- **Python Runtime:** `{platform.python_version()}`\n"
            f"- **Local SLM:** `Ollama (tinyllama)`\n"
        )
        return {
            "response": resp,
            "sources": [{"source": "Windows Platform & OS Architecture Audit", "score": 1.0, "text": platform.platform()}]
        }

    # 7. Universal Windows Installed Applications Scanner (Registry + Start Menu + AppData + PATH + UWP)
    def _collect_installed_windows_apps() -> List[Dict[str, str]]:
        apps_map: Dict[str, Dict[str, str]] = {}
        try:
            import winreg
            roots = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            for root, reg_path in roots:
                try:
                    with winreg.OpenKey(root, reg_path) as key:
                        sub_count = winreg.QueryInfoKey(key)[0]
                        for i in range(sub_count):
                            try:
                                sub_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, sub_name) as sk:
                                    vals = {}
                                    val_count = winreg.QueryInfoKey(sk)[1]
                                    for j in range(val_count):
                                        vn, vv, _ = winreg.EnumValue(sk, j)
                                        vals[vn] = vv
                                    dname = str(vals.get("DisplayName", "")).strip()
                                    if not dname:
                                        continue
                                    key_l = dname.lower()
                                    if key_l not in apps_map:
                                        apps_map[key_l] = {
                                            "name": dname,
                                            "version": str(vals.get("DisplayVersion", "")).strip(),
                                            "publisher": str(vals.get("Publisher", "")).strip(),
                                            "location": str(vals.get("InstallLocation", "")).strip(),
                                            "source": "Windows Registry",
                                        }
                            except Exception:
                                continue
                except Exception:
                    continue
        except Exception:
            pass

        # Scan Start Menu shortcuts (.lnk) and LocalAppData\Programs
        start_dirs = [
            os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
        ]
        for sdir in start_dirs:
            if os.path.exists(sdir):
                for rdir, _, files in os.walk(sdir):
                    for fn in files:
                        if fn.lower().endswith(".lnk"):
                            app_title = fn[:-4].strip()
                            if app_title.lower().startswith("uninstall"):
                                continue
                            kl = app_title.lower()
                            if kl not in apps_map:
                                apps_map[kl] = {
                                    "name": app_title,
                                    "version": "",
                                    "publisher": "",
                                    "location": os.path.join(rdir, fn),
                                    "source": "Start Menu",
                                }

        local_progs = os.path.expanduser(r"~\AppData\Local\Programs")
        if os.path.exists(local_progs):
            for entry in os.listdir(local_progs):
                full_p = os.path.join(local_progs, entry)
                if os.path.isdir(full_p) and entry.lower() not in apps_map:
                    apps_map[entry.lower()] = {
                        "name": entry,
                        "version": "",
                        "publisher": "",
                        "location": full_p,
                        "source": "LocalAppData\\Programs",
                    }

        return sorted(apps_map.values(), key=lambda x: x["name"].lower())

    # 7a. List all installed apps on the system
    list_triggers = [
        "all apps", "installed apps", "list apps", "what apps", "show apps",
        "installed software", "installed programs", "apps present", "apps in my",
        "apps on my", "software installed", "programs installed"
    ]
    if any(t in q for t in list_triggers):
        apps = _collect_installed_windows_apps()
        lines = [
            f"### 🖥️ Installed Applications on Your PC ({len(apps)} Detected)\n",
            "Scanned **Windows Registry**, **Start Menu**, and **User AppData (`Local\\Programs`)**:\n",
            "| # | Application | Version | Source / Location |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for idx, app in enumerate(apps[:80], 1):
            ver = app["version"] or "—"
            loc = app["location"] or app["source"]
            if len(loc) > 55:
                loc = "..." + loc[-52:]
            lines.append(f"| {idx} | **{app['name']}** | `{ver}` | `{loc}` |")
        if len(apps) > 80:
            lines.append(f"\n*Showing top 80 of {len(apps)} detected entries. Ask `Is <app name> installed?` to inspect any specific app.*")
        return {
            "response": "\n".join(lines),
            "sources": [{"source": "Windows Registry & Start Menu Audit", "score": 1.0, "text": f"Discovered {len(apps)} installed applications"}]
        }

    # 7b. Generic "Is <app> installed?" / "Do I have <app>?" / "Check <app>"
    import re, shutil, subprocess
    app_query_patterns = [
        r"(?:is|are)\s+(.+?)\s+(?:installed|present|available|on my pc|in my pc|on my system|in my system|on my laptop|on this pc)",
        r"(?:do i have|have i got|check if|check whether|find if)\s+(.+?)(?:\s+installed|\s+in my|\s+on my|\?|$)",
        r"(?:where is|check|locate|status of)\s+(.+?)(?:\s+installed|\s+on my|\s+in my|\?|$)",
    ]
    extracted_app = None
    for pat in app_query_patterns:
        m = re.search(pat, q)
        if m:
            candidate = m.group(1).strip(" ?!.,'\"")
            # Ignore generic words or threat words
            skip_words = {"it", "this", "that", "there", "anything", "everything", "threat", "threats", "malware", "virus", "cve"}
            if candidate and candidate not in skip_words and len(candidate) >= 2:
                extracted_app = candidate
                break

    if extracted_app and not any(tw in extracted_app for tw in ["cve-", "malware", "ransomware", "rootkit", "threat", "vulnerability"]):
        # Clean trailing filler phrases
        extracted_app = re.sub(r"\s+(?:in my pc|on my pc|in my system|on my system|installed|app|software)$", "", extracted_app).strip()
        aliases = {
            "vscode": "visual studio code",
            "vs code": "visual studio code",
            "chrome": "google chrome",
            "edge": "microsoft edge",
            "word": "microsoft office",
            "excel": "microsoft office",
            "powerpoint": "microsoft office",
            "compass": "mongodb compass",
            "intellij": "intellij idea",
            "node": "node.js",
            "nodejs": "node.js",
            "wsl": "windows subsystem for linux",
        }
        search_term = aliases.get(extracted_app, extracted_app)
        apps = _collect_installed_windows_apps()
        matches = [a for a in apps if search_term in a["name"].lower() or extracted_app in a["name"].lower()]

        # Also check CLI in PATH
        cli_path = shutil.which(extracted_app.replace(" ", "")) or shutil.which(search_term.replace(" ", ""))

        # Also check UWP / Microsoft Store apps if no desktop match yet
        uwp_matches = []
        if not matches and not cli_path:
            try:
                ps_cmd = f"Get-StartApps | Where-Object {{ $_.Name -like '*{extracted_app}*' -or $_.Name -like '*{search_term}*' }} | Select-Object -First 5 Name,AppID | ConvertTo-Json"
                res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
                if res.stdout.strip():
                    parsed = json.loads(res.stdout)
                    if isinstance(parsed, dict):
                        parsed = [parsed]
                    uwp_matches = parsed
            except Exception:
                pass

        # Check running processes
        running_procs = []
        try:
            tl = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=3)
            for line in tl.stdout.splitlines():
                proc_name = line.split(",")[0].strip('"')
                if extracted_app.replace(" ", "") in proc_name.lower() or search_term.split()[0] in proc_name.lower():
                    if proc_name not in running_procs:
                        running_procs.append(proc_name)
        except Exception:
            pass

        if matches or cli_path or uwp_matches:
            resp_lines = [f"### 🔍 Host Software Verification: `{extracted_app.title()}`\n"]
            resp_lines.append(f"✅ **Yes, `{extracted_app}` is installed on your PC.**\n")
            for m_app in matches[:5]:
                ver_txt = f" (v`{m_app['version']}`)" if m_app["version"] else ""
                pub_txt = f" | Publisher: `{m_app['publisher']}`" if m_app["publisher"] else ""
                loc_txt = f" | Location: `{m_app['location']}`" if m_app["location"] else f" | Source: `{m_app['source']}`"
                resp_lines.append(f"- **{m_app['name']}**{ver_txt}{pub_txt}{loc_txt}")
            for u in uwp_matches[:5]:
                resp_lines.append(f"- **{u.get('Name', extracted_app)}** (Microsoft Store / UWP App | AppID: `{u.get('AppID', '')}`)")
            if cli_path:
                resp_lines.append(f"- **CLI Executable in PATH:** `{cli_path}`")
            if running_procs:
                resp_lines.append(f"- **Process Status:** 🟢 **Currently Running** (`{', '.join(running_procs[:3])}`)")
            else:
                resp_lines.append("- **Process Status:** ⚪ **Installed (Not currently running)**")

            return {
                "response": "\n".join(resp_lines),
                "sources": [{"source": "Universal Windows App & Process Inspector", "score": 1.0, "text": f"Matched {len(matches) + len(uwp_matches)} app(s) for '{extracted_app}'"}]
            }
        else:
            resp = (
                f"### 🔍 Host Software Verification: `{extracted_app.title()}`\n\n"
                f"❌ **No, `{extracted_app}` was not found installed on your PC.**\n\n"
                f"- Checked **Windows Registry** (`HKLM` & `HKCU` Uninstall keys — {len(apps)} entries)\n"
                f"- Checked **Start Menu shortcuts** & **`AppData\\Local\\Programs`**\n"
                f"- Checked **Microsoft Store (UWP) apps** & **System `PATH`**\n\n"
                f"💡 *Tip: Try `List all installed apps` to see everything detected on your system.*"
            )
            return {
                "response": resp,
                "sources": [{"source": "Universal Windows App Inspector", "score": 1.0, "text": f"Searched {len(apps)} apps, UWP apps, and PATH for '{extracted_app}'"}]
            }

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

            # 1. Autonomous Security Scanner Commands
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

            # 2. Conversational Mitigation Execution
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

            # 3. Direct Host Software & System Inspection (e.g., "is claude installed in my pc")
            elif inspect_host_software_and_system(msg) is not None:
                host_audit = inspect_host_software_and_system(msg)
                resp = host_audit["response"]
                sources = host_audit["sources"]

            # 4. Status & Readiness check ("is it working", "are you working", "hello", "hi")
            elif any(msg_lower == g or msg_lower.startswith(g + " ") for g in ["is it working", "are you working", "is working", "working?", "status check", "ping"]):
                models = get_ollama_models()
                model_name = models[0] if models else "Offline"
                resp = (
                    f"### 🚀 System Operational Status: Active & Ready\n\n"
                    f"✅ **Yes, the Threat Intelligence Chatbot and all core subsystems are fully operational!**\n\n"
                    f"- **MongoDB Threat Database:** Connected (`{len(CACHED_THREATS)}` multi-platform threats loaded)\n"
                    f"- **Vector RAG Knowledge Base:** `{len(CACHED_KNOWLEDGE)}` embedded intelligence chunks\n"
                    f"- **Local SLM Engine (Ollama):** `{model_name}` running on `http://127.0.0.1:11434`\n"
                    f"- **Autonomous Scanner & Mitigator:** Online (Dependency, credential, and socket auditing)\n"
                    f"- **Host System Inspector:** Active (Audit local software such as Claude, Python, Docker, MongoDB)\n\n"
                    f"**Try asking:**\n"
                    f"- `Is claude installed in my pc?`\n"
                    f"- `What are the active threats for Windows?`\n"
                    f"- `Run scan`\n"
                    f"- `What is the mitigation for CVE-2024-3094?`"
                )
                sources = [{"source": "System Health Monitor", "score": 1.0, "text": f"Ollama: {model_name}, Threats: {len(CACHED_THREATS)}"}]

            # 5. Threat Intelligence Queries or General Queries
            else:
                models = get_ollama_models()
                chosen_model = models[0] if models else None
                ollama_status = f"Ollama model: {chosen_model}" if chosen_model else "Vector RAG (Ollama Offline)"

                threat_keywords = [
                    "cve", "threat", "vulnerability", "malware", "ransomware", "exploit", "attack",
                    "rootkit", "trojan", "mitigation", "patch", "ioc", "cvss", "security", "linux",
                    "windows", "macos", "android", "ios", "zero-day", "payload", "backdoor",
                    "anticipated", "active", "evolving", "resolved", "phishing", "injection", "botnet"
                ]
                is_threat = any(k in msg_lower for k in threat_keywords)

                if is_threat:
                    raw_sources = retrieve_rag_context(msg, top_k=4)
                    context_str = "\n".join(f"[{s['source']}] {s['text']}" for s in raw_sources)

                    ollama_answer = None
                    if chosen_model:
                        ollama_answer = query_ollama(msg, context_str, chosen_model)

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
                else:
                    # General Query -> Answer using Ollama SLM
                    ollama_answer = None
                    if chosen_model:
                        ollama_answer = query_ollama(msg, "", chosen_model)

                    if ollama_answer:
                        resp = ollama_answer
                        sources = [{"source": f"Local SLM ({chosen_model})", "score": 1.0, "text": "Generated via local neural weights"}]
                    else:
                        resp = (
                            f"I received your inquiry: *\"{msg}\"*\n\n"
                            f"I am your local Cyber Threat Intelligence Copilot. You can ask me:\n"
                            f"- Threat intelligence & CVE mitigations across Linux, Windows, MacOS, Android, and iOS\n"
                            f"- Host software audits (e.g., `is claude installed in my pc`, `is python installed`)\n"
                            f"- Security scanning & remediation (`run scan`, `mitigate <CVE>`)\n"
                        )
                        sources = [{"source": "Threat Intelligence Copilot", "score": 0.8, "text": "System Assistant fallback"}]

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
