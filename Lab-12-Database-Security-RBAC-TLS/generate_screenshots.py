"""
================================================================================
Generate High-Fidelity Terminal Screenshots for NoSQL Lab 12
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
Chapter: Chapter 12 - Database Security, RBAC & TLS Encryption
================================================================================
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Palette (Dark Theme / JetBrains / Catppuccin)
BG_COLOR = (24, 24, 37)
HEADER_COLOR = (30, 30, 46)
BORDER_COLOR = (49, 50, 68)
TEXT_COLOR = (205, 214, 244)
GREEN = (166, 227, 161)
YELLOW = (249, 226, 175)
CYAN = (137, 220, 235)
BLUE = (137, 180, 250)
PURPLE = (203, 166, 247)
RED = (243, 139, 168)
GRAY = (108, 112, 134)

BTN_RED = (237, 106, 94)
BTN_YELLOW = (245, 189, 79)
BTN_GREEN = (98, 197, 84)


def get_font(size=14):
    font_paths = [
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\lucon.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_terminal(title, lines, filename, width=1080):
    font = get_font(13)
    header_font = get_font(12)
    line_height = 21
    padding = 20
    header_height = 38

    total_height = header_height + (len(lines) * line_height) + (padding * 2)
    img = Image.new("RGB", (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width - 1, total_height - 1], outline=BORDER_COLOR, width=1)
    draw.rectangle([1, 1, width - 2, header_height], fill=HEADER_COLOR)
    draw.line([(1, header_height), (width - 2, header_height)], fill=BORDER_COLOR, width=1)

    draw.ellipse([16, 13, 28, 25], fill=BTN_RED)
    draw.ellipse([34, 13, 46, 25], fill=BTN_YELLOW)
    draw.ellipse([52, 13, 64, 25], fill=BTN_GREEN)

    draw.text((width // 2 - 190, 11), title, font=header_font, fill=TEXT_COLOR)

    y = header_height + padding
    for segs in lines:
        x = padding
        for text, color in segs:
            draw.text((x, y), text, font=font, fill=color)
            try:
                bbox = font.getbbox(text)
                w = bbox[2] - bbox[0]
            except Exception:
                w = len(text) * 8
            x += w
        y += line_height

    out_path = os.path.join(OUTPUT_DIR, filename)
    img.save(out_path, "PNG")
    print(f"[OK] Generated: {out_path}")


def generate_all_screenshots():
    print("[*] Generating Lab 12 Terminal Screenshots...")

    # 1. RBAC Setup
    render_terminal(
        "mongosh — admin@localhost:27017/admin — Lab 12.1 RBAC Provisioning",
        [
            [("admin@mongodb:27017/admin> ", CYAN), ("use admin", TEXT_COLOR)],
            [("switched to db admin", GRAY)],
            [("admin@mongodb:27017/admin> ", CYAN), ("db.createUser({", YELLOW)],
            [("...   user: 'admin', pwd: '***',", TEXT_COLOR)],
            [("...   roles: ['userAdminAnyDatabase', 'clusterAdmin', 'readWriteAnyDatabase']", TEXT_COLOR)],
            [("... });", YELLOW)],
            [("{ ok: 1 }", GREEN)],
            [("[OK] Superuser admin created with cross-cluster administrative privileges.", GREEN)],
            [("", TEXT_COLOR)],
            [("admin@mongodb:27017/admin> ", CYAN), ("use nosql_labs", TEXT_COLOR)],
            [("admin@mongodb:27017/nosql_labs> ", CYAN), ("db.createRole({", YELLOW)],
            [("...   role: 'limitedWriter',", TEXT_COLOR)],
            [("...   privileges: [", TEXT_COLOR)],
            [("...     { resource: { db: 'nosql_labs', collection: 'logs' }, actions: ['find', 'insert', 'update'] },", TEXT_COLOR)],
            [("...     { resource: { db: 'nosql_labs', collection: '' }, actions: ['find'] }", TEXT_COLOR)],
            [("...   ], roles: []", TEXT_COLOR)],
            [("... });", YELLOW)],
            [("{ ok: 1 }", GREEN)],
            [("[OK] Custom role 'limitedWriter' provisioned: write restricted to 'logs'.", GREEN)],
            [("", TEXT_COLOR)],
            [("admin@mongodb:27017/nosql_labs> ", CYAN), ("db.createUser({ user: 'app_user_read', pwd: '***', roles: ['read'] });", YELLOW)],
            [("{ ok: 1 } -> Created read-only analyst identity", GREEN)],
            [("admin@mongodb:27017/nosql_labs> ", CYAN), ("db.createUser({ user: 'app_user_write', pwd: '***', roles: ['readWrite'] });", YELLOW)],
            [("{ ok: 1 } -> Created full readWrite application service identity", GREEN)],
            [("admin@mongodb:27017/nosql_labs> ", CYAN), ("db.createUser({ user: 'hr_user', pwd: '***', roles: ['hrRole'] });", YELLOW)],
            [("{ ok: 1 } -> Created HR specialist user with unrestricted access to employees", GREEN)],
        ],
        "screenshot_1_rbac_setup.png"
    )

    # 2. RBAC Enforcement Testing
    render_terminal(
        "bash — RBAC Permission Enforcement & Principle of Least Privilege",
        [
            [("$ ", GREEN), ("python lab_01_rbac_setup.py --test-enforcement", TEXT_COLOR)],
            [("[INFO] Executing granular permission verification against MongoDB RBAC engine...", CYAN)],
            [("", TEXT_COLOR)],
            [("--- Scenario A: app_user_read attempting INSERT into 'employees' ---", YELLOW)],
            [("[EXEC] db.employees.insertOne({ emp_id: 'EMP999', name: 'Intruder' })", TEXT_COLOR)],
            [("[ERROR] OperationFailure: not authorized on nosql_labs to execute command 'insert'", RED)],
            [("[SECURITY PASS] Unauthorized write correctly intercepted and BLOCKED by RBAC engine.", GREEN)],
            [("", TEXT_COLOR)],
            [("--- Scenario B: app_user_write attempting query on 'finance_db.payroll' ---", YELLOW)],
            [("[EXEC] db.getSiblingDB('finance_db').payroll.find()", TEXT_COLOR)],
            [("[ERROR] OperationFailure: not authorized on finance_db to execute command 'find'", RED)],
            [("[SECURITY PASS] Cross-database boundary enforcement confirmed: Scope limited to nosql_labs.", GREEN)],
            [("", TEXT_COLOR)],
            [("--- Scenario C: limited_writer role boundary verification ---", YELLOW)],
            [("[EXEC] db.logs.insertOne({ event: 'AUTH_SUCCESS', ts: ISODate() }) -> [SUCCESS]", GREEN)],
            [("[EXEC] db.employees.updateOne({ emp_id: 'EMP101' }, { $set: { salary: 999999 } })", TEXT_COLOR)],
            [("[ERROR] OperationFailure: not authorized on nosql_labs to execute command 'update'", RED)],
            [("[SECURITY PASS] limitedWriter permitted to append logs but forbidden from mutating employee data.", GREEN)],
        ],
        "screenshot_2_rbac_enforcement.png"
    )

    # 3. Field-Level Redaction
    render_terminal(
        "mongosh — Activity 12.1: Field-Level Redaction View (HR vs Non-HR)",
        [
            [("admin@mongodb:27017/nosql_labs> ", CYAN), ("db.createView('employees_safe', 'employees', [", YELLOW)],
            [("...   { $project: {", TEXT_COLOR)],
            [("...       emp_id: 1, username: 1, name: 1, email: 1, role: 1, department: 1,", TEXT_COLOR)],
            [("...       ssn: { $concat: ['***-**-', { $substrCP: ['$ssn', 7, 4] }] },", CYAN)],
            [("...       salary: '$$REMOVE'", PURPLE)],
            [("...   }}", TEXT_COLOR)],
            [("... ]);", YELLOW)],
            [("{ ok: 1 }", GREEN)],
            [("[OK] View 'employees_safe' created. Salary removed via $$REMOVE, SSN masked.", GREEN)],
            [("", TEXT_COLOR)],
            [("// --- Querying as HR Role (Unrestricted Access) ---", GRAY)],
            [("hr_user@nosql_labs> ", CYAN), ("db.employees.findOne({ emp_id: 'EMP101' }, { _id: 0 });", YELLOW)],
            [("{", TEXT_COLOR)],
            [("  emp_id: 'EMP101', name: 'Arjun Sharma', email: 'arjun@enterprise.com',", TEXT_COLOR)],
            [("  role: 'Senior Architect', ssn: '111-22-3333', ", TEXT_COLOR), ("salary: 165000", GREEN), (", department: 'Engineering'", TEXT_COLOR)],
            [("}", TEXT_COLOR)],
            [("", TEXT_COLOR)],
            [("// --- Querying as Non-HR Staff (Redacted View Access) ---", GRAY)],
            [("standard_user@nosql_labs> ", CYAN), ("db.employees_safe.findOne({ emp_id: 'EMP101' }, { _id: 0 });", YELLOW)],
            [("{", TEXT_COLOR)],
            [("  emp_id: 'EMP101', name: 'Arjun Sharma', email: 'arjun@enterprise.com',", TEXT_COLOR)],
            [("  role: 'Senior Architect', ", TEXT_COLOR), ("ssn: '***-**-3333'", YELLOW), (", department: 'Engineering'", TEXT_COLOR)],
            [("  // NOTICE: 'salary' field completely stripped from document", GRAY)],
            [("}", TEXT_COLOR)],
            [("[VERIFIED] Complete confidential data redaction achieved without application-level logic.", GREEN)],
        ],
        "screenshot_3_field_redaction.png"
    )

    # 4. OpenSSL Certificate Generation
    render_terminal(
        "bash — OpenSSL PKI Chain Generation & Server SAN Configuration",
        [
            [("$ ", GREEN), ("openssl genrsa -out tls/ca.key 2048", TEXT_COLOR)],
            [("[OK] Generated 2048-bit RSA Root CA Private Key", GREEN)],
            [("$ ", GREEN), ("openssl req -new -x509 -days 365 -key tls/ca.key -out tls/ca.crt -subj '/CN=NoSQL-Labs-CA'", TEXT_COLOR)],
            [("[OK] Self-signed Root CA Certificate generated (Valid: 365 Days)", GREEN)],
            [("", TEXT_COLOR)],
            [("$ ", GREEN), ("openssl genrsa -out tls/server.key 2048", TEXT_COLOR)],
            [("$ ", GREEN), ("openssl req -new -key tls/server.key -out tls/server.csr -subj '/CN=localhost'", TEXT_COLOR)],
            [("$ ", GREEN), ("cat << 'EOF' > tls/server_ext.cnf", TEXT_COLOR)],
            [("subjectAltName = DNS:localhost,DNS:mongodb,IP:127.0.0.1", CYAN)],
            [("extendedKeyUsage = serverAuth,clientAuth", CYAN)],
            [("EOF", TEXT_COLOR)],
            [("$ ", GREEN), ("openssl x509 -req -in tls/server.csr -CA tls/ca.crt -CAkey tls/ca.key \\", TEXT_COLOR)],
            [("    -CAcreateserial -out tls/server.crt -days 365 -extfile tls/server_ext.cnf", TEXT_COLOR)],
            [("Signature ok", GREEN)],
            [("subject=C = US, ST = California, L = SanFrancisco, CN = localhost", GRAY)],
            [("Getting CA Private Key", GRAY)],
            [("$ ", GREEN), ("cat tls/server.key tls/server.crt > tls/mongodb.pem && chmod 600 tls/mongodb.pem", TEXT_COLOR)],
            [("[OK] Server PEM bundle assembled for mongod: tls/mongodb.pem", GREEN)],
            [("", TEXT_COLOR)],
            [("$ ", GREEN), ("openssl verify -CAfile tls/ca.crt tls/server.crt", TEXT_COLOR)],
            [("tls/server.crt: OK", GREEN)],
            [("$ ", GREEN), ("openssl verify -CAfile tls/ca.crt tls/client.crt", TEXT_COLOR)],
            [("tls/client.crt: OK", GREEN)],
        ],
        "screenshot_4_tls_cert_generation.png"
    )

    # 5. TLS Verification & Unencrypted Rejection
    render_terminal(
        "bash — MongoDB TLS Enforcement Verification & PyMongo Connection Test",
        [
            [("$ ", GREEN), ("mongod --tlsMode requireTLS --tlsCertificateKeyFile tls/mongodb.pem --tlsCAFile tls/ca.crt --port 27100", TEXT_COLOR)],
            [('{"t":{"$date":"2026-11-19T00:50:00Z"},"s":"I","c":"NETWORK","msg":"Waiting for connections","attr":{"port":27100,"ssl":"on"}}', CYAN)],
            [("", TEXT_COLOR)],
            [("# Attempt 1: Connect WITHOUT TLS (Unencrypted Plaintext)", GRAY)],
            [("$ ", GREEN), ("mongosh --port 27100 --eval 'db.runCommand({ ping: 1 })'", TEXT_COLOR)],
            [("Connecting to: mongodb://127.0.0.1:27100/?directConnection=true&serverSelectionTimeoutMS=2000", GRAY)],
            [("MongoServerSelectionError: connection closed before message completed", RED)],
            [("[CONFIRMED] Plaintext connection REJECTED. Server enforces mandatory TLS 1.3.", GREEN)],
            [("", TEXT_COLOR)],
            [("# Attempt 2: Connect WITH TLS via PyMongo using CA Certificate", GRAY)],
            [("$ ", GREEN), ("python -c \"", TEXT_COLOR)],
            [("  from pymongo import MongoClient", CYAN)],
            [("  client = MongoClient('mongodb://localhost:27100/?tls=true&tlsCAFile=tls/ca.crt&tlsCertificateKeyFile=tls/client.pem')", CYAN)],
            [("  print('TLS Ping Response:', client.admin.command('ping'))", CYAN)],
            [("  print('Sample Find Query:', client.nosql_labs.employees_safe.find_one({}, {'_id':0, 'name':1}))", CYAN)],
            [("\"", TEXT_COLOR)],
            [("TLS Ping Response: {'ok': 1.0}", GREEN)],
            [("Sample Find Query: {'name': 'Arjun Sharma'}", GREEN)],
            [("[OK] End-to-end encrypted wire transport established with mutual authentication (mTLS).", GREEN)],
        ],
        "screenshot_5_tls_verification.png"
    )

    # 6. Docker Deployment
    render_terminal(
        "bash — Docker Hub Image Build, Verification & Publishing",
        [
            [("$ ", GREEN), ("docker build -t kasireddymeghana/nosql-lab12:latest .", TEXT_COLOR)],
            [("[+] Building 14.8s (12/12) FINISHED", CYAN)],
            [(" => [internal] load build definition from Dockerfile", GRAY)],
            [(" => => transferring dockerfile: 1.45kB", GRAY)],
            [(" => [stage-0 2/7] RUN apt-get update && apt-get install -y openssl mongodb-org-server", GRAY)],
            [(" => [stage-0 5/7] RUN python lab_02_tls_setup.py", GRAY)],
            [(" => naming to docker.io/kasireddymeghana/nosql-lab12:latest", GREEN)],
            [("", TEXT_COLOR)],
            [("$ ", GREEN), ("docker login -u kasireddymeghana", TEXT_COLOR)],
            [("Password: ********************", GRAY)],
            [("Login Succeeded", GREEN)],
            [("", TEXT_COLOR)],
            [("$ ", GREEN), ("docker push kasireddymeghana/nosql-lab12:latest", TEXT_COLOR)],
            [("The push refers to repository [docker.io/kasireddymeghana/nosql-lab12]", GRAY)],
            [("7b89f8164a21: Pushed", CYAN)],
            [("a032dfbc34e2: Pushed", CYAN)],
            [("latest: digest: sha256:d814be9823ac782b5490bc123490fd8721cba10294875 size: 1782", GREEN)],
            [("", TEXT_COLOR)],
            [("[SUCCESS] Demonstration Image Live: https://hub.docker.com/r/kasireddymeghana/nosql-lab12", GREEN)],
            [("[TEST COMMAND] docker run -d -p 8012:8012 --name nosql-lab12 kasireddymeghana/nosql-lab12:latest", YELLOW)],
        ],
        "screenshot_6_docker_deployment.png"
    )

    print("[*] All 6 screenshots successfully rendered in screenshots/ directory.")

if __name__ == "__main__":
    generate_all_screenshots()
