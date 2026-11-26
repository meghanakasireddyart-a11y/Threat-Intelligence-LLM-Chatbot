"""
================================================================================
Comprehensive Lab 12 Report Builder (.docx and .pdf)
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
Chapter: Chapter 12 - Database Security, RBAC & TLS Encryption-in-Transit
Docker Hub URL: https://hub.docker.com/r/kasireddymeghana/nosql-lab12
================================================================================
"""

import os
import sys
from datetime import datetime

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCX_OUT_PATH = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_12.docx")
DOCX_COPY_PATH = os.path.join(BASE_DIR, "NoSQL_Lab12_Report.docx")
PDF_OUT_PATH = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_12.pdf")
PDF_COPY_PATH = os.path.join(BASE_DIR, "NoSQL_Lab12_Report.pdf")

DOCKER_HUB_URL = "https://hub.docker.com/r/kasireddymeghana/nosql-lab12"


def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)

    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="D1D5DB"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(31, 41, 55)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_screenshot(doc, img_name, caption_text):
    img_path = os.path.join(SCREENSHOTS_DIR, img_name)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(6.2))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(f"Figure: {caption_text}")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(107, 114, 128)


def build_docx_report():
    print("[*] Generating DOCX Report for Lab 12...")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Document Title Block
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("NoSQL Databases Lab Report: Lab 12")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(17, 24, 39)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("MongoDB Authentication, Role-Based Access Control (RBAC), Field-Level Redaction & TLS Encryption")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12.5)
    r_sub.font.color.rgb = RGBColor(79, 70, 229)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(2.2)
    meta_table.columns[1].width = Inches(4.3)

    meta_data = [
        ("Student Name:", "Kasireddy Meghana"),
        ("University Seat No (USN):", "24BTRCL119"),
        ("Course & Department:", "NoSQL Databases Using MongoDB | CSE (AIML), Sec B"),
        ("Submission Docker URL:", DOCKER_HUB_URL)
    ]

    for idx, (lbl, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        set_cell_background(cell_lbl, "F3F4F6")
        set_cell_background(cell_val, "FFFFFF")
        set_cell_margins(cell_lbl, 60, 60, 100, 100)
        set_cell_margins(cell_val, 60, 60, 100, 100)

        p0 = cell_lbl.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(lbl)
        r0.font.bold = True
        r0.font.size = Pt(9.5)

        p1 = cell_val.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.5)
        if "http" in val:
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(37, 99, 235)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section 1: Executive Overview
    h1 = doc.add_heading("1. Executive Overview & Database Security Foundations", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)

    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.line_spacing = 1.15
    p_intro.paragraph_format.space_after = Pt(8)
    p_intro.add_run(
        "Database security is governed by the classic CIA Triad (Confidentiality, Integrity, and Availability). "
        "In production enterprise deployments, MongoDB mandates two critical, non-negotiable security layers:\n"
        "1. Role-Based Access Control (RBAC): Enforces authentication and granular authorization, ensuring users and "
        "applications operate strictly within the Principle of Least Privilege (PoLP).\n"
        "2. Transport Layer Security (TLS/SSL): Enforces end-to-end wire encryption for all client-to-server and intra-cluster "
        "traffic, protecting sensitive credentials and payload data from eavesdropping and man-in-the-middle (MITM) attacks.\n\n"
        "This laboratory exercises the complete security lifecycle: configuring administrative and scoped application users, "
        "authoring custom privilege roles, implementing database-level field redaction via aggregation views to conceal "
        "sensitive compensation figures, and establishing a self-signed X.509 Public Key Infrastructure (PKI) with Subject Alternative "
        "Names (SAN) for mandatory TLS enforcement."
    )

    # Section 2: Lab 12.1 Authentication & RBAC
    h2 = doc.add_heading("2. Lab 12.1: Authentication & Role-Based Access Control (RBAC)", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)

    p_rbac = doc.add_paragraph()
    p_rbac.paragraph_format.line_spacing = 1.15
    p_rbac.paragraph_format.space_after = Pt(8)
    p_rbac.add_run(
        "By default, MongoDB instances run with authentication disabled for development convenience. In production, "
        "the daemon must be started with the '--auth' flag (or 'security.authorization: enabled' in mongod.conf). "
        "Once enabled, every connection must authenticate against a specific database before issuing commands.\n\n"
        "The following administrative and application identities were provisioned in MongoDB:\n"
        "• admin: Superuser with userAdminAnyDatabase, clusterAdmin, and readWriteAnyDatabase roles on the admin db.\n"
        "• app_user_read: Analyst user with 'read' role restricted to nosql_labs.\n"
        "• app_user_write: Application backend identity with 'readWrite' privileges on nosql_labs.\n"
        "• limited_writer: Custom user assigned the 'limitedWriter' role, granting find on the entire database but "
        "limiting write operations (insert, update) strictly to the 'logs' collection.\n"
        "• hr_user: Human Resources officer granted full access to raw employee records including salary and SSN.\n"
        "• standard_user: General employee granted access only to the sanitized 'employees_safe' view."
    )

    add_screenshot(doc, "screenshot_1_rbac_setup.png", "MongoDB Admin Shell Provisioning Admin and Scoped RBAC Users")

    add_code_block(doc, """// MongoDB Shell: Creating Admin and Granular Custom Roles
use admin;
db.createUser({
  user: "admin",
  pwd: "AdminSecurePassword123!",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "clusterAdmin", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
});

use nosql_labs;
db.createRole({
  role: "limitedWriter",
  privileges: [
    { resource: { db: "nosql_labs", collection: "logs" }, actions: ["find", "insert", "update"] },
    { resource: { db: "nosql_labs", collection: "" }, actions: ["find"] }
  ],
  roles: []
});

db.createUser({
  user: "limited_writer",
  pwd: "LogPassword123!",
  roles: [{ role: "limitedWriter", db: "nosql_labs" }]
});""")

    # RBAC Matrix Table
    p_tbl_lbl = doc.add_paragraph()
    p_tbl_lbl.paragraph_format.space_after = Pt(4)
    r_tl = p_tbl_lbl.add_run("Table 12.1: Granular Privilege Assignment & Enforcement Matrix")
    r_tl.font.bold = True
    r_tl.font.size = Pt(10)

    rbac_tbl = doc.add_table(rows=6, cols=5)
    rbac_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    rbac_tbl.autofit = False
    col_w = [Inches(1.3), Inches(1.2), Inches(1.3), Inches(1.3), Inches(1.4)]
    for r in rbac_tbl.rows:
        for idx, w in enumerate(col_w):
            r.cells[idx].width = w

    headers_rbac = ["User Identity", "Role Assigned", "Database Scope", "Permitted Actions", "Restricted Actions"]
    for idx, text in enumerate(headers_rbac):
        cell = rbac_tbl.rows[0].cells[idx]
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    rbac_data = [
        ("admin", "clusterAdmin / readWriteAny", "Cluster-Wide", "All administrative & CRUD commands", "None (Superuser)"),
        ("app_user_read", "read", "nosql_labs", "find, count on all collections", "insert, update, delete (Denied)"),
        ("app_user_write", "readWrite", "nosql_labs", "find, insert, update, delete", "Cross-DB access (e.g., finance_db)"),
        ("limited_writer", "limitedWriter (Custom)", "nosql_labs", "insert/update on 'logs', find elsewhere", "write/update on 'employees' (Denied)"),
        ("hr_user", "hrRole (Custom)", "nosql_labs.employees", "find, insert, update, remove on employees", "Modifying system schemas"),
    ]

    for r_idx, row_vals in enumerate(rbac_data, start=1):
        bg = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_vals):
            cell = rbac_tbl.rows[r_idx].cells[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Permission Enforcement Verification
    h2b = doc.add_heading("2.1 RBAC Enforcement Verification & Violation Interception", level=2)
    h2b.paragraph_format.space_before = Pt(10)
    h2b.paragraph_format.space_after = Pt(4)

    p_enf = doc.add_paragraph()
    p_enf.paragraph_format.line_spacing = 1.15
    p_enf.paragraph_format.space_after = Pt(8)
    p_enf.add_run(
        "To rigorously prove that MongoDB's RBAC engine operates correctly, negative test suites were executed "
        "where authenticated users attempted operations outside their privilege boundaries. Every unauthorized operation "
        "was intercepted and blocked with code 13 ('Unauthorized' / 'OperationFailure: not authorized'):\n"
        "• app_user_read attempted an insert into 'employees': Immediately rejected.\n"
        "• app_user_write attempted to query 'finance_db.payroll': Blocked by cross-database authorization isolation.\n"
        "• limited_writer attempted to mutate 'employees.salary': Blocked, while insert into 'logs' was permitted."
    )

    add_screenshot(doc, "screenshot_2_rbac_enforcement.png", "Permission Violation Interception (Unauthorized Write and Cross-DB Access Denied)")

    # Section 3: Activity 12.1 Field-Level Redaction via Views
    h3 = doc.add_heading("3. Activity 12.1: Field-Level Redaction via Views", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)

    p_redact = doc.add_paragraph()
    p_redact.paragraph_format.line_spacing = 1.15
    p_redact.paragraph_format.space_after = Pt(8)
    p_redact.add_run(
        "In many real-world enterprise architectures, a single document contains both public staff metadata (name, email, role) "
        "and highly sensitive personal identifiable information (PII) or compensation data (SSN, base salary). "
        "Relying on application code to omit sensitive fields creates grave vulnerability risks if an unvetted service or "
        "SQL/NoSQL injection queries the database directly.\n\n"
        "MongoDB resolves this natively using Database Views ('db.createView()'). A view is a read-only alias defined over an "
        "underlying collection with a built-in aggregation pipeline. For Activity 12.1, a view named 'employees_safe' was created "
        "with a '$project' stage that:\n"
        "1. Strips the 'salary' field entirely using '$$REMOVE'.\n"
        "2. Partially masks the 'ssn' field using '$substrCP' to expose only the final 4 digits ('***-**-XXXX').\n"
        "3. Grants general users read privileges only to 'employees_safe', while granting the 'hrRole' direct read/write to 'employees'."
    )

    add_screenshot(doc, "screenshot_3_field_redaction.png", "Field-Level Redaction View Creation and Query Comparison (HR vs Safe View)")

    add_code_block(doc, """// Activity 12.1: Native Database View with Aggregation Redaction Pipeline
db.createView("employees_safe", "employees", [
  {
    $project: {
      emp_id: 1,
      username: 1,
      name: 1,
      email: 1,
      role: 1,
      department: 1,
      ssn: { $concat: ["***-**-", { $substrCP: ["$ssn", 7, 4] }] },
      salary: "$$REMOVE"  // Redacts field entirely from unprivileged callers
    }
  }
]);

// HR User queries underlying collection directly:
// -> Sees: { emp_id: 'EMP101', name: 'Arjun', ssn: '111-22-3333', salary: 165000 }

// General User queries safe view:
// -> Sees: { emp_id: 'EMP101', name: 'Arjun', ssn: '***-**-3333' } (salary is absent)""")

    # Section 4: Lab 12.2 TLS / Encryption-in-Transit Setup
    h4 = doc.add_heading("4. Lab 12.2: TLS / Encryption-in-Transit PKI Implementation", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(4)

    p_tls = doc.add_paragraph()
    p_tls.paragraph_format.line_spacing = 1.15
    p_tls.paragraph_format.space_after = Pt(8)
    p_tls.add_run(
        "Transport Layer Security (TLS 1.3) protects MongoDB communications from packet sniffing, network interception, "
        "and man-in-the-middle attacks. To establish TLS encryption, a three-tier Public Key Infrastructure (PKI) was "
        "generated using OpenSSL:\n"
        "1. Root Certificate Authority (CA): A self-signed 2048-bit RSA key and X.509 certificate ('ca.key', 'ca.crt') serving "
        "as the local trust anchor.\n"
        "2. Server Certificate with SAN: A server private key and certificate signed by the Root CA. Crucially, modern MongoDB "
        "versions strictly mandate Subject Alternative Names (SAN) conforming to RFC 5280. A custom extension file ('server_ext.cnf') "
        "was created declaring 'DNS:localhost, DNS:mongodb, IP:127.0.0.1'.\n"
        "3. Server PEM Bundle: mongod expects the private key and server certificate concatenated into a single PEM file ('mongodb.pem').\n"
        "4. Client Certificate for Mutual TLS (mTLS): A dedicated client key and certificate ('client.pem') signed by the CA to allow "
        "bidirectional cryptographic verification between PyMongo and the MongoDB server."
    )

    add_screenshot(doc, "screenshot_4_tls_cert_generation.png", "OpenSSL PKI Generation: Root CA, Server Certificate with SAN, and Client Bundle")

    add_code_block(doc, """# OpenSSL PKI Generation Commands:
# 1. Generate Root CA:
openssl genrsa -out tls/ca.key 2048
openssl req -new -x509 -days 365 -key tls/ca.key -out tls/ca.crt -subj '/CN=NoSQL-Labs-CA'

# 2. Server Key & CSR with Subject Alternative Name (SAN):
openssl genrsa -out tls/server.key 2048
openssl req -new -key tls/server.key -out tls/server.csr -subj '/CN=localhost'

# 3. Sign Server Certificate with CA including SAN extension:
openssl x509 -req -in tls/server.csr -CA tls/ca.crt -CAkey tls/ca.key -CAcreateserial \\
  -out tls/server.crt -days 365 -extfile tls/server_ext.cnf -extensions v3_req

# 4. Concatenate Server Key and Certificate into PEM:
cat tls/server.key tls/server.crt > tls/mongodb.pem && chmod 600 tls/mongodb.pem

# 5. Verify Certificate Chain Validity:
openssl verify -CAfile tls/ca.crt tls/server.crt   # Result: OK
openssl verify -CAfile tls/ca.crt tls/client.crt   # Result: OK""")

    # Section 5: TLS Enforcement Verification
    h5 = doc.add_heading("5. TLS Enforcement Verification & PyMongo Connectivity", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(4)

    p_tls_test = doc.add_paragraph()
    p_tls_test.paragraph_format.line_spacing = 1.15
    p_tls_test.paragraph_format.space_after = Pt(8)
    p_tls_test.add_run(
        "To verify that unencrypted connections are categorically rejected, MongoDB was configured with:\n"
        "  mongod --tlsMode requireTLS --tlsCertificateKeyFile tls/mongodb.pem --tlsCAFile tls/ca.crt --port 27100\n\n"
        "Two connection scenarios were executed:\n"
        "• Unencrypted Plaintext Attempt: A client connecting without TLS ('tls=False') immediately fails with "
        "'ServerSelectionTimeoutError' and 'connection closed before message completed'. This proves that no plaintext "
        "traffic can penetrate the database perimeter.\n"
        "• TLS-Encrypted PyMongo Connection: Connecting with 'tls=true', 'tlsCAFile=ca.crt', and 'tlsCertificateKeyFile=client.pem' "
        "successfully performs the cryptographic TLS 1.3 handshake. The driver successfully executes ping and find commands "
        "over AES-256-GCM encrypted transport."
    )

    add_screenshot(doc, "screenshot_5_tls_verification.png", "TLS Enforcement Testing: Plaintext Rejection vs Secure PyMongo Encrypted Handshake")

    add_code_block(doc, """# PyMongo TLS Connection Implementation:
from pymongo import MongoClient

# Attempt 1: Unencrypted connection to TLS-enforced port (FAILS):
try:
    c_fail = MongoClient('mongodb://localhost:27100/?serverSelectionTimeoutMS=2000')
    c_fail.admin.command('ping')
except Exception as e:
    print("[REJECTED] Plaintext connection refused by TLS endpoint:", type(e).__name__)

# Attempt 2: TLS Encrypted Connection with Mutual TLS Verification (SUCCEEDS):
secure_uri = (
    "mongodb://localhost:27100/?"
    "tls=true&"
    "tlsCAFile=tls/ca.crt&"
    "tlsCertificateKeyFile=tls/client.pem&"
    "tlsAllowInvalidHostnames=true"
)
client = MongoClient(secure_uri)
print("TLS Ping Status:", client.admin.command('ping'))  # {'ok': 1.0}
print("Encrypted Query:", client.nosql_labs.employees_safe.find_one({}, {'_id': 0, 'name': 1}))""")

    # Section 6: Comprehensive Viva Q&A
    h6 = doc.add_heading("6. Comprehensive Lab Q&A and Viva Discussion", level=1)
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(4)

    qa_list = [
        (
            "Q1: Why is field-level redaction implemented via database views preferred over application-level filtering?",
            "Implementing redaction at the database layer enforces security at the data source. If filtering is performed "
            "solely in application code, raw sensitive documents (including salaries and SSNs) still traverse the network from "
            "the database to the application server. Furthermore, any developer writing an ad-hoc query, report, or new microservice "
            "could inadvertently bypass application filters and leak confidential data. A database view ensures that the database engine "
            "never transmits the redacted fields to unauthorized users, guaranteeing security by design regardless of client code."
        ),
        (
            "Q2: What is the difference between mongod flags '--tlsMode allowTLS' and '--tlsMode requireTLS'?",
            "'--tlsMode allowTLS' allows mixed-mode connections: clients can connect either using unencrypted plaintext or over TLS. "
            "This mode is primarily intended as a temporary migration stepping-stone while upgrading legacy clients. In contrast, "
            "'--tlsMode requireTLS' strictly forbids any non-TLS connection. Any plaintext connection attempt is rejected immediately "
            "during the initial socket handshake, ensuring zero possibility of unencrypted wire transmission."
        ),
        (
            "Q3: Why does MongoDB require Subject Alternative Names (SAN) in TLS certificates instead of relying solely on Common Name (CN)?",
            "RFC 2818 and RFC 5280 deprecated the use of the Common Name (CN) field for identity verification due to its lack of precision "
            "and inability to support multiple hostnames or IP addresses securely. Modern TLS implementations (including Go, Node.js, and Python) "
            "strictly enforce SAN checking. If a MongoDB client connects to 'localhost' or an IP like '127.0.0.1' and the server certificate only "
            "lists CN='localhost' without corresponding SAN entries ('DNS:localhost, IP:127.0.0.1'), the TLS handshake fails with hostname "
            "verification errors."
        ),
        (
            "Q4: How does MongoDB's internal replica set authentication differ from client-to-database authentication?",
            "Client authentication validates external users against database roles using SCRAM-SHA-256 or X.509 client certificates. "
            "Internal cluster authentication governs the secure communication between nodes (mongod replica set members and mongos routers). "
            "This can be configured using a shared Keyfile (minimum 6-1024 base64 characters) via '--keyFile', or using internal X.509 "
            "member certificates via '--clusterAuthMode x509', which validates that each cluster member's certificate was signed by the cluster CA."
        ),
        (
            "Q5: What are the trade-offs of using Client-Side Field Level Encryption (CSFLE) compared to Views?",
            "While Views mask fields on read, the underlying document is stored in plaintext on disk (unless Encrypted Storage Engine is active). "
            "CSFLE / In-Use Encryption encrypts individual fields (e.g. SSN) on the client side before sending them over the wire; the MongoDB server "
            "only ever sees ciphertext blobs and cannot read the plaintext even if compromised. The trade-off is higher client-side CPU overhead, "
            "inability to perform arbitrary range queries on encrypted fields, and complex Key Management Interoperability Protocol (KMIP/AWS KMS) setup."
        )
    ]

    for q_text, a_text in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        rq = p_q.add_run(q_text)
        rq.font.bold = True
        rq.font.size = Pt(9.5)
        rq.font.color.rgb = RGBColor(30, 41, 59)

        p_a = doc.add_paragraph()
        p_a.paragraph_format.line_spacing = 1.15
        p_a.paragraph_format.space_after = Pt(6)
        ra = p_a.add_run(a_text)
        ra.font.size = Pt(9)
        ra.font.color.rgb = RGBColor(75, 85, 99)

    # Section 7: Docker Submission Block
    h7 = doc.add_heading("7. Docker Container Demonstration for Grading", level=1)
    h7.paragraph_format.space_before = Pt(14)
    h7.paragraph_format.space_after = Pt(4)

    p_dock = doc.add_paragraph()
    p_dock.paragraph_format.line_spacing = 1.15
    p_dock.paragraph_format.space_after = Pt(6)
    p_dock.add_run(
        "In strict compliance with the submission guidelines, the complete Lab 12 solution—including MongoDB authentication, "
        "custom RBAC roles, the field-level redaction view, OpenSSL PKI certificate generation, PyMongo TLS testing, and the "
        "integrated interactive web dashboard—has been containerized and published to Docker Hub."
    )

    add_screenshot(doc, "screenshot_6_docker_deployment.png", "Docker Image Build, Push, and Hub Verification")

    add_code_block(doc, f"""# Docker Hub Demonstration Repository:
# URL: {DOCKER_HUB_URL}

# 1. Pull the official demonstration image:
docker pull kasireddymeghana/nosql-lab12:latest

# 2. Run the interactive web platform on port 8012:
docker run -d -p 8012:8012 --name nosql-lab12 kasireddymeghana/nosql-lab12:latest

# 3. Access the live platform in your browser:
# http://localhost:8012""")

    # Save DOCX
    doc.save(DOCX_OUT_PATH)
    doc.save(DOCX_COPY_PATH)
    print(f"[OK] Generated: {DOCX_OUT_PATH}")
    print(f"[OK] Generated: {DOCX_COPY_PATH}")


def build_pdf_report():
    print("[*] Generating PDF Report for Lab 12...")
    doc = SimpleDocTemplate(
        PDF_OUT_PATH,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#111827'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=11,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor('#1F2937')
    )
    cap_style = ParagraphStyle(
        'CapStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#6B7280'),
        alignment=1,
        spaceAfter=7
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("NoSQL Databases Lab Report: Lab 12", title_style))
    story.append(Paragraph("MongoDB Authentication, Role-Based Access Control (RBAC), Field-Level Redaction & TLS Encryption", subtitle_style))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Student Name:</b>", body_style), Paragraph("Kasireddy Meghana", body_style)],
        [Paragraph("<b>University Seat No (USN):</b>", body_style), Paragraph("24BTRCL119", body_style)],
        [Paragraph("<b>Course & Department:</b>", body_style), Paragraph("NoSQL Databases Using MongoDB | CSE (AIML), Sec B", body_style)],
        [Paragraph("<b>Docker Hub URL:</b>", body_style), Paragraph(f'<font color="#2563EB"><b>{DOCKER_HUB_URL}</b></font>', body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[150, 380])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # 1. Overview
    story.append(Paragraph("1. Executive Overview & Database Security Foundations", h1_style))
    story.append(Paragraph(
        "Database security in MongoDB relies upon two core pillars of the CIA Triad: Authentication/RBAC (ensuring "
        "only identified users execute authorized operations) and TLS Encryption (protecting data in transit from eavesdropping). "
        "This laboratory deploys a production-grade security architecture: configuring authentication with the --auth flag, "
        "establishing granular custom roles, creating field-level redaction views for sensitive compensation data, and "
        "implementing an OpenSSL PKI infrastructure for mandatory TLS wire encryption.",
        body_style
    ))

    # 2. Lab 12.1 RBAC
    story.append(Paragraph("2. Lab 12.1: Authentication & Role-Based Access Control (RBAC)", h1_style))
    story.append(Paragraph(
        "MongoDB's RBAC model grants privileges to roles, which are subsequently assigned to users. Identities provisioned include: "
        "an administrative superuser (admin), a read-only analyst (app_user_read), an application service (app_user_write), "
        "and a custom limited log appender (limited_writer). All unauthorized write or cross-database read attempts were "
        "strictly blocked by the authorization engine.",
        body_style
    ))

    img1 = os.path.join(SCREENSHOTS_DIR, "screenshot_1_rbac_setup.png")
    if os.path.exists(img1):
        story.append(RLImage(img1, width=510, height=210))
        story.append(Paragraph("Figure 12.1: MongoDB Admin Shell Provisioning Admin and Scoped RBAC Users", cap_style))

    img2 = os.path.join(SCREENSHOTS_DIR, "screenshot_2_rbac_enforcement.png")
    if os.path.exists(img2):
        story.append(RLImage(img2, width=510, height=195))
        story.append(Paragraph("Figure 12.2: Permission Violation Interception (Unauthorized Operations Blocked)", cap_style))

    # 3. Activity 12.1 Field Redaction
    story.append(Paragraph("3. Activity 12.1: Field-Level Redaction via Views", h1_style))
    story.append(Paragraph(
        "To protect confidential salaries and SSNs without complex application-level filters, a MongoDB View ('employees_safe') "
        "was created using an aggregation pipeline with $project, $$REMOVE, and $substrCP masking. Non-HR staff query the view "
        "and see masked identities without salary data, while HR personnel query the underlying collection directly.",
        body_style
    ))

    img3 = os.path.join(SCREENSHOTS_DIR, "screenshot_3_field_redaction.png")
    if os.path.exists(img3):
        story.append(RLImage(img3, width=510, height=210))
        story.append(Paragraph("Figure 12.3: Activity 12.1 Field-Level Redaction Query Comparison (HR vs Safe View)", cap_style))

    # 4. Lab 12.2 TLS Setup
    story.append(Paragraph("4. Lab 12.2: TLS / Encryption-in-Transit PKI Implementation", h1_style))
    story.append(Paragraph(
        "An X.509 PKI chain was generated using OpenSSL: a self-signed Root CA, a server certificate configured with "
        "Subject Alternative Names (DNS:localhost, IP:127.0.0.1) as required by RFC 5280, concatenated server PEM bundle, "
        "and a client certificate for mutual TLS authentication. Certificates were verified using 'openssl verify'.",
        body_style
    ))

    img4 = os.path.join(SCREENSHOTS_DIR, "screenshot_4_tls_cert_generation.png")
    if os.path.exists(img4):
        story.append(RLImage(img4, width=510, height=210))
        story.append(Paragraph("Figure 12.4: OpenSSL PKI Generation: Root CA, Server Certificate with SAN, and Client Bundle", cap_style))

    # 5. TLS Enforcement Testing
    story.append(Paragraph("5. TLS Enforcement Verification & PyMongo Connectivity", h1_style))
    story.append(Paragraph(
        "Starting MongoDB with '--tlsMode requireTLS' guaranteed that all unencrypted plaintext connections were immediately rejected. "
        "PyMongo successfully established an encrypted session using tls=true, tlsCAFile, and tlsCertificateKeyFile, performing "
        "secure queries over TLS 1.3.",
        body_style
    ))

    img5 = os.path.join(SCREENSHOTS_DIR, "screenshot_5_tls_verification.png")
    if os.path.exists(img5):
        story.append(RLImage(img5, width=510, height=200))
        story.append(Paragraph("Figure 12.5: TLS Enforcement Testing: Plaintext Rejection vs Secure PyMongo Encrypted Handshake", cap_style))

    # 6. Docker Submission
    story.append(Paragraph("6. Docker Hub Container Demonstration for Grading", h1_style))
    story.append(Paragraph(
        f"The complete demonstration suite is published to Docker Hub at <b>{DOCKER_HUB_URL}</b>. "
        "Evaluators can pull and run the container with:<br/>"
        "<code>docker pull kasireddymeghana/nosql-lab12:latest</code><br/>"
        "<code>docker run -d -p 8012:8012 --name nosql-lab12 kasireddymeghana/nosql-lab12:latest</code>",
        body_style
    ))

    img6 = os.path.join(SCREENSHOTS_DIR, "screenshot_6_docker_deployment.png")
    if os.path.exists(img6):
        story.append(RLImage(img6, width=510, height=200))
        story.append(Paragraph("Figure 12.6: Docker Image Build, Push, and Hub Verification", cap_style))

    doc.build(story)

    # Copy to standardized filename
    if os.path.exists(PDF_OUT_PATH):
        import shutil
        shutil.copyfile(PDF_OUT_PATH, PDF_COPY_PATH)
        print(f"[OK] Generated: {PDF_OUT_PATH}")
        print(f"[OK] Generated: {PDF_COPY_PATH}")


def main():
    build_docx_report()
    build_pdf_report()
    print("[SUCCESS] All Lab 12 reports generated successfully!")


if __name__ == "__main__":
    main()
