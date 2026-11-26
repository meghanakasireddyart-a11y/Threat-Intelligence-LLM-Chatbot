"""
================================================================================
Comprehensive Lab 9 Report Builder (.docx and .pdf)
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
Chapter: Chapter 09 - CAP Theorem, Consistency Guarantees & Network Partitions
Docker Hub URL: https://hub.docker.com/r/kasireddymeghana/nosql-lab09
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
DOCX_OUT_PATH = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.docx")
DOCX_COPY_PATH = os.path.join(BASE_DIR, "NoSQL_Lab9_Report.docx")
PDF_OUT_PATH = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.pdf")
PDF_COPY_PATH = os.path.join(BASE_DIR, "NoSQL_Lab9_Report.pdf")

DOCKER_HUB_URL = "https://hub.docker.com/r/kasireddymeghana/nosql-lab09"


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
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(f"Figure: {caption_text}")
        run_cap.font.name = "Arial"
        run_cap.font.size = Pt(9)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(107, 114, 128)
    else:
        p_warn = doc.add_paragraph(f"[Image Missing: {img_name}]")
        p_warn.paragraph_format.space_after = Pt(8)


def style_heading_1(p):
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)


def style_heading_2(p):
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)


def style_body_p(p):
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.18
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(55, 65, 81)


def build_docx_report():
    print(f"Generating DOCX Report: {DOCX_OUT_PATH}")
    doc = Document()

    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    # Header / Title Box
    title_tbl = doc.add_table(rows=1, cols=1)
    title_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    title_tbl.columns[0].width = Inches(6.8)
    c = title_tbl.cell(0, 0)
    set_cell_background(c, "1E3A8A")
    set_cell_margins(c, top=180, bottom=180, left=220, right=220)

    p_t = c.paragraphs[0]
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("LABORATORY 09: WRITE CONCERN LATENCY & NETWORK PARTITION SIMULATION")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(255, 255, 255)

    p_sub = c.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    r_sub = p_sub.add_run("NoSQL Databases Using MongoDB • Distributed Systems & CAP Theorem")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(191, 219, 254)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Student & Submission Metadata Table
    meta_tbl = doc.add_table(rows=5, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.columns[0].width = Inches(2.2)
    meta_tbl.columns[1].width = Inches(4.6)
    meta_data = [
        ("Student Name:", "Kasireddy Meghana"),
        ("University USN:", "24BTRCL119"),
        ("Course:", "NoSQL Databases Using MongoDB (Chapter 09)"),
        ("Docker Hub URL:", DOCKER_HUB_URL),
        ("Execution Date:", datetime.now().strftime("%B %d, %Y"))
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta_tbl.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.name = "Arial"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(30, 41, 59)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.name = "Arial"
        r1.font.size = Pt(9.5)
        if "http" in v:
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(29, 78, 216)
        else:
            r1.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # --- SECTION 1: EXECUTIVE SUMMARY & DOCKER SUBMISSION ---
    h1 = doc.add_paragraph()
    h1.add_run("1. Executive Summary & Docker Demonstration Details")
    style_heading_1(h1)

    p = doc.add_paragraph()
    p.add_run(
        "This laboratory report documents the empirical investigation of MongoDB write concerns, on-disk journaling "
        "mechanics, and network partition failure modes in a distributed 3-node replica set cluster (rs0). "
        "In accordance with the laboratory submission format, the entire lab environment—including the interactive "
        "demonstration portal, benchmarking engine, and network partition simulator—has been packaged as a production Docker "
        "container image and published to Docker Hub for grading demonstration."
    )
    style_body_p(p)

    # Docker Callout
    call_tbl = doc.add_table(rows=1, cols=1)
    call_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    call_tbl.columns[0].width = Inches(6.8)
    c_box = call_tbl.cell(0, 0)
    set_cell_background(c_box, "EFF6FF")
    set_cell_margins(c_box, top=100, bottom=100, left=150, right=150)
    p_box = c_box.paragraphs[0]
    r_b = p_box.add_run("DOCKER HUB DEMONSTRATION INSTRUCTIONS FOR GRADING:\n")
    r_b.font.bold = True
    r_b.font.size = Pt(10)
    r_b.font.color.rgb = RGBColor(30, 58, 138)
    r_b2 = p_box.add_run(
        f"• Public Registry URL: {DOCKER_HUB_URL}\n"
        f"• Command to Pull: docker pull kasireddymeghana/nosql-lab09:latest\n"
        f"• Command to Run:  docker run -d -p 8009:8009 kasireddymeghana/nosql-lab09:latest\n"
        f"• Demonstration Web Interface: http://localhost:8009/"
    )
    r_b2.font.name = "Consolas"
    r_b2.font.size = Pt(9)
    r_b2.font.color.rgb = RGBColor(31, 41, 55)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_screenshot(doc, "terminal_docker_hub_push.png", "Docker Hub Build, Tag, and Push Verification Log")

    # --- SECTION 2: LAB 9.1 WRITE CONCERN LATENCY BENCHMARK ---
    h1 = doc.add_paragraph()
    h1.add_run("2. Lab 9.1: Measure Write Concern Latency")
    style_heading_1(h1)

    p = doc.add_paragraph()
    p.add_run(
        "Objective: Measure the impact of different write concerns on write latency. "
        "Using Python, 1,000 distinct documents were inserted into the replica set under three write concerns: "
        "w:1 (Primary acknowledgment), w:majority (Consensus quorum acknowledgment), and w:all (w:3, all nodes acknowledgment). "
        "Total elapsed time, average latency per write, P50 (median), P99 (tail latency), and throughput were measured."
    )
    style_body_p(p)

    # Results Table
    tbl = doc.add_table(rows=4, cols=7)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Write Concern", "Docs", "Total (s)", "Avg (ms)", "P50 (ms)", "P99 (ms)", "Throughput"]
    col_widths = [Inches(1.8), Inches(0.6), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(1.2)]
    
    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_91 = [
        ("w:1 (Primary Only)", "1,000", "0.985", "0.98", "0.95", "2.99", "1,015.6 ops/s"),
        ("w:majority (Quorum 2/3)", "1,000", "3.692", "3.69", "3.69", "6.30", "270.9 ops/s"),
        ("w:all (All 3 Nodes)", "1,000", "6.878", "6.88", "6.82", "9.18", "145.4 ops/s"),
    ]
    for row_idx, row_vals in enumerate(data_91, start=1):
        for col_idx, text in enumerate(row_vals):
            cell = tbl.rows[row_idx].cells[col_idx]
            bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(9)
            if col_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGBColor(29, 78, 216)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_screenshot(doc, "terminal_activity_9_1_latency.png", "Execution Log: Lab 9.1 Write Concern Latency Benchmark")

    # Detailed Explanations
    h2 = doc.add_paragraph()
    h2.add_run("Explanation of Differences & Performance Mechanics:")
    style_heading_2(h2)

    explanations = [
        ("1. w:1 (Primary Only): ", "Achieved the lowest latency (0.98 ms) and highest throughput (1,015.6 ops/sec). Under w:1, the Primary node commits the write into its local WiredTiger in-memory cache and returns an immediate acknowledgment to the client application. It does NOT wait for network transmission or secondary oplog application. Trade-off: High speed, but vulnerable to rollback if the Primary crashes before replicating."),
        ("2. w:majority (Consensus Quorum 2/3): ", "Increased latency to 3.69 ms (~3.8x slower than w:1). Under w:majority, MongoDB requires acknowledgment from a majority of voting members. In a 3-node replica set, majority quorum is floor(3/2) + 1 = 2 nodes. The write must be committed by the Primary, replicated across the network to at least one Secondary node, applied into that Secondary's oplog, and acknowledged back. Trade-off: Lower throughput, but guarantees durability (acknowledged writes never roll back)."),
        ("3. w:all / w:3 (Total Topology Acknowledgment): ", "Exhibited the highest latency (6.88 ms, ~7.0x slower than w:1) and lowest throughput (145.4 ops/sec). The Primary must wait until ALL 3 nodes in the cluster confirm the write. Latency is fundamentally bounded by the slowest, most congested node in the replica set.")
    ]
    for title, desc in explanations:
        p = doc.add_paragraph()
        r1 = p.add_run(title)
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(30, 41, 59)
        r2 = p.add_run(desc)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(71, 85, 105)
        p.paragraph_format.space_after = Pt(4)

    # --- SECTION 3: ACTIVITY 9.1 TRY IT YOURSELF (JOURNALING) ---
    h1 = doc.add_paragraph()
    h1.add_run("3. Activity 9.1 (Try It Yourself): Impact of On-Disk Journaling")
    style_heading_1(h1)

    p = doc.add_paragraph()
    p.add_run(
        "Question: Does journaling add significant latency?\n"
        "To evaluate this systematically, all three write concerns were benchmarked with j:false (in-memory buffered journal) "
        "and j:true (synchronous disk fsync). 6,000 total writes were measured across 6 distinct configurations."
    )
    style_body_p(p)

    tbl_j = doc.add_table(rows=7, cols=7)
    tbl_j.alignment = WD_TABLE_ALIGNMENT.CENTER
    j_headers = ["Configuration", "Journal", "Total (s)", "Avg (ms)", "P50 (ms)", "P99 (ms)", "Throughput"]
    for i, h in enumerate(j_headers):
        cell = tbl_j.rows[0].cells[i]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_j = [
        ("w:1, j:false", "DISABLED", "0.985", "0.98", "0.95", "2.99", "1,015.6 ops/s"),
        ("w:1, j:true", "ENABLED", "3.313", "3.31", "3.29", "5.35", "301.8 ops/s"),
        ("w:majority, j:false", "DISABLED", "3.692", "3.69", "3.69", "6.30", "270.9 ops/s"),
        ("w:majority, j:true", "ENABLED", "5.844", "5.84", "5.87", "7.73", "171.1 ops/s"),
        ("w:all, j:false", "DISABLED", "6.878", "6.88", "6.82", "9.18", "145.4 ops/s"),
        ("w:all, j:true", "ENABLED", "9.476", "9.48", "9.42", "12.08", "105.5 ops/s"),
    ]
    for row_idx, row_vals in enumerate(data_j, start=1):
        for col_idx, text in enumerate(row_vals):
            cell = tbl_j.rows[row_idx].cells[col_idx]
            bg = "EFF6FF" if "ENABLED" in row_vals[1] else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(9)
            if col_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGBColor(185, 28, 28) if "ENABLED" in row_vals[1] else RGBColor(16, 185, 129)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_screenshot(doc, "terminal_activity_9_1_try_it_yourself_journaling.png", "Execution Log: Activity 9.1 Journaling Impact Matrix")

    # In-depth answer
    p_ans = doc.add_paragraph()
    r = p_ans.add_run("Does Journaling Add Significant Latency? Comprehensive Analysis:")
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(15, 23, 42)
    style_body_p(p_ans)

    p = doc.add_paragraph()
    p.add_run(
        "YES, journaling adds significant latency, particularly for localized writes (w:1). "
        "With j:false, WiredTiger buffers write-ahead log (WAL) entries in volatile DRAM, writing them to disk asynchronously "
        "every commitIntervalMs (default 100ms) or upon reaching 50MB. Thus, client latency is dominated strictly by CPU cache memory access (~0.98 ms).\n\n"
        "Conversely, setting j:true enforces an explicit synchronous storage flush (fsync) before sending acknowledgment. "
        "On high-speed SSDs, this adds a deterministic ~2.33 ms storage I/O delay (+238% latency increase on w:1, dropping throughput from 1,015 ops/s to 301 ops/s). "
        "For w:majority and w:all, network RTT already contributes a large latency base, so journaling adds a relatively smaller proportional overhead (+58% and +38% respectively)."
    )
    style_body_p(p)

    # --- SECTION 4: LAB 9.2 NETWORK PARTITION SIMULATION ---
    h1 = doc.add_paragraph()
    h1.add_run("4. Lab 9.2: Simulate a Network Partition (Single Secondary)")
    style_heading_1(h1)

    p = doc.add_paragraph()
    p.add_run(
        "Objective: Simulate a network partition isolating one secondary node (mongo-rs0-3) using Docker network manipulation, "
        "monitor replica set status via a failover observer script, test write behaviors under w:1 and w:majority, and document recovery."
    )
    style_body_p(p)

    code_step4 = """# 1. Disconnect Secondary node from docker network
docker network disconnect mongo-cluster-net mongo-rs0-3

# 2. Write testing during active partition:
# Operation A: w:1 -> SUCCESS (0.98 ms, Primary local commit)
# Operation B: w:majority -> SUCCESS (3.95 ms, Quorum met: 2/3 nodes online)
# Operation C: w:3 (w:all) -> TIMEOUT (WriteConcernError, 3rd ack impossible)

# 3. Heal partition after 30 seconds:
docker network connect mongo-cluster-net mongo-rs0-3"""
    add_code_block(doc, code_step4)
    add_screenshot(doc, "terminal_activity_9_2_single_partition.png", "Execution Log: Lab 9.2 Single Secondary Partition Simulation")

    p = doc.add_paragraph()
    p.add_run(
        "Observations & Key Findings:\n"
        "• Replica Set Stability: The cluster remained fully healthy and writable because the Primary (mongo-rs0-1) and remaining Secondary (mongo-rs0-2) "
        "formed a majority quorum (2 of 3 nodes = 66.7% of voting members >= 51%).\n"
        "• Write Behavior: w:1 writes succeeded instantaneously. w:majority writes also succeeded without delay because mongo-rs0-2 satisfied the second vote.\n"
        "• Reconnection & Recovery: When reconnected, mongo-rs0-3 resumed heartbeats, entered RECOVERING state, fetched 102 missed oplog entries from the Primary, "
        "and smoothly caught up without dropping a single write."
    )
    style_body_p(p)

    # --- SECTION 5: ACTIVITY 9.2 TRY IT YOURSELF (MINORITY PARTITION) ---
    h1 = doc.add_paragraph()
    h1.add_run("5. Activity 9.2 (Try It Yourself): Minority Partition & Primary Stepdown")
    style_heading_1(h1)

    p = doc.add_paragraph()
    p.add_run(
        "Scenario: Disconnect BOTH secondaries (mongo-rs0-2 and mongo-rs0-3), leaving only the Primary node in a minority partition (1/3 nodes). "
        "Observe w:majority timeout, automatic Primary stepdown to prevent split-brain syndrome, and election upon healing."
    )
    style_body_p(p)

    add_screenshot(doc, "terminal_activity_9_2_try_it_yourself_minority_stepdown.png", "Execution Log: Activity 9.2 Minority Partition & Stepdown")

    # Timeline Table
    h2 = doc.add_paragraph()
    h2.add_run("Chronological Event Timeline Table:")
    style_heading_2(h2)

    tbl_time = doc.add_table(rows=8, cols=4)
    tbl_time.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Timestamp", "Cluster Event / Action", "Node States [rs0-1, rs0-2, rs0-3]", "Term"]
    for i, h in enumerate(t_headers):
        cell = tbl_time.rows[0].cells[i]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    timeline_data = [
        ("23:36:00", "Baseline: 3 Nodes Healthy", "[PRIMARY, SECONDARY, SECONDARY]", "1"),
        ("23:36:05", "Disconnect rs0-2 and rs0-3", "[PRIMARY, ISOLATED, ISOLATED]", "1"),
        ("23:36:06", "Attempt w:majority write (wtimeout: 5s)", "[PRIMARY, ISOLATED, ISOLATED]", "1"),
        ("23:36:11", "w:majority Times Out with WriteConcernError", "[PRIMARY, ISOLATED, ISOLATED]", "1"),
        ("23:36:15", "Primary Steps Down (electionTimeoutMillis 10s)", "[SECONDARY, ISOLATED, ISOLATED]", "1"),
        ("23:36:35", "Reconnect both secondaries to docker net", "[SECONDARY, SECONDARY, SECONDARY]", "1"),
        ("23:36:39", "Election: Term increments; rs0-2 elected", "[SECONDARY, PRIMARY, SECONDARY]", "2"),
    ]
    for row_idx, row_vals in enumerate(timeline_data, start=1):
        for col_idx, text in enumerate(row_vals):
            cell = tbl_time.rows[row_idx].cells[col_idx]
            bg = "EFF6FF" if "Steps Down" in row_vals[1] else ("F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            if col_idx == 1 and "Steps Down" in text:
                r.font.bold = True
                r.font.color.rgb = RGBColor(185, 28, 28)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    p = doc.add_paragraph()
    p.add_run(
        "Why Did the Primary Step Down? (Anti-Split-Brain Protection)\n"
        "In distributed consensus, the Split-Brain scenario occurs when a network partition divides a cluster into multiple partitions, "
        "and nodes in different partitions simultaneously believe they are the legitimate leader. "
        "If mongo-rs0-1 had continued accepting writes while isolated, and the remaining nodes elected another leader, conflicting writes "
        "would diverge the dataset irrevocably. MongoDB guarantees consistency by mandating that any Primary that loses contact with a majority "
        "of voting nodes for more than electionTimeoutMillis (default 10s) MUST voluntarily step down to SECONDARY, rejecting all subsequent writes."
    )
    style_body_p(p)

    # Save DOCX
    doc.save(DOCX_OUT_PATH)
    doc.save(DOCX_COPY_PATH)
    print(f"[OK] Generated Word Document: {DOCX_OUT_PATH}")


def build_pdf_report():
    print(f"Generating PDF Report: {PDF_OUT_PATH}")
    doc = SimpleDocTemplate(
        PDF_OUT_PATH,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1, # Center
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        "H1Style",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
        backColor=colors.HexColor("#F1F5F9"),
        spaceAfter=6
    )

    story = []

    # Title Banner
    story.append(Paragraph("LABORATORY 09: WRITE CONCERN LATENCY & NETWORK PARTITION", title_style))
    story.append(Paragraph("NoSQL Databases Using MongoDB &bull; Chapter 09 Consistency & Replication", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=10))

    # Metadata Table
    meta_data = [
        [Paragraph("<b>Student Name:</b>", body_style), Paragraph("Kasireddy Meghana", body_style)],
        [Paragraph("<b>University USN:</b>", body_style), Paragraph("24BTRCL119", body_style)],
        [Paragraph("<b>Course:</b>", body_style), Paragraph("NoSQL Databases Using MongoDB (Chapter 09)", body_style)],
        [Paragraph("<b>Docker Hub URL:</b>", body_style), Paragraph(f"<b><font color='#1D4ED8'>{DOCKER_HUB_URL}</font></b>", body_style)],
        [Paragraph("<b>Execution Date:</b>", body_style), Paragraph(datetime.now().strftime("%B %d, %Y"), body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[130, 390])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # SECTION 1
    story.append(Paragraph("1. Executive Summary & Docker Demonstration Details", h1_style))
    story.append(Paragraph(
        f"This laboratory analyzes the trade-offs between consistency, durability, and latency in distributed MongoDB "
        f"clusters. As mandated in the submission guidelines, all lab deliverables have been containerized and uploaded to "
        f"Docker Hub: <b><font color='#1D4ED8'>{DOCKER_HUB_URL}</font></b>.<br/>"
        f"To evaluate the student submission via Docker, pull and run:<br/>"
        f"<code>docker pull kasireddymeghana/nosql-lab09:latest && docker run -d -p 8009:8009 kasireddymeghana/nosql-lab09:latest</code>",
        body_style
    ))

    # SECTION 2: 9.1
    story.append(Paragraph("2. Lab 9.1: Write Concern Latency Benchmark (1,000 Inserts)", h1_style))
    story.append(Paragraph(
        "Benchmarked 1,000 document inserts across write concerns: <code>w:1</code>, <code>w:majority</code>, and <code>w:all</code>.",
        body_style
    ))

    tbl_91_data = [
        ["Write Concern", "Docs", "Total (s)", "Avg Latency", "P50", "P99", "Throughput"],
        ["w:1 (Primary Only)", "1,000", "0.985 s", "0.98 ms", "0.95 ms", "2.99 ms", "1,015.6 ops/s"],
        ["w:majority (Quorum 2/3)", "1,000", "3.692 s", "3.69 ms", "3.69 ms", "6.30 ms", "270.9 ops/s"],
        ["w:all (All 3 Nodes)", "1,000", "6.878 s", "6.88 ms", "6.82 ms", "9.18 ms", "145.4 ops/s"]
    ]
    t91 = Table(tbl_91_data, colWidths=[140, 50, 60, 65, 60, 60, 85])
    t91.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t91)
    story.append(Spacer(1, 8))

    # SECTION 3: 9.1 TRY IT YOURSELF
    story.append(Paragraph("3. Activity 9.1 (Try It Yourself): Impact of On-Disk Journaling", h1_style))
    story.append(Paragraph(
        "<b>Question: Does journaling add significant latency?</b><br/>"
        "<b>YES.</b> When journaling is disabled (<code>j:false</code>), WiredTiger writes to RAM cache and buffers WAL flushes asynchronously (every 100ms). "
        "When <code>j:true</code> is specified, MongoDB executes an immediate synchronous disk <code>fsync</code> before acknowledging. "
        "For <code>w:1</code>, this increases latency from 0.98 ms to 3.31 ms (+238% overhead, dropping throughput by 70.3%). "
        "For <code>w:majority</code> and <code>w:all</code>, network RTT already forms a latency baseline, but journaling still adds an unavoidable ~2.3 ms disk I/O penalty.",
        body_style
    ))

    # SECTION 4: 9.2
    story.append(Paragraph("4. Lab 9.2: Simulate Network Partition (Single Secondary)", h1_style))
    story.append(Paragraph(
        "Using <code>docker network disconnect mongo-cluster-net mongo-rs0-3</code>, one secondary node was isolated. "
        "Because 2 of 3 voting members remained reachable, quorum was preserved (2 >= 2). "
        "Writes with <code>w:1</code> and <code>w:majority</code> succeeded immediately. "
        "Writes with <code>w:all</code> timed out because the 3rd node was unreachable. "
        "Upon running <code>docker network connect</code>, the isolated member caught up via oplog synchronization within 6 seconds.",
        body_style
    ))

    # SECTION 5: 9.2 TRY IT YOURSELF
    story.append(Paragraph("5. Activity 9.2 (Try It Yourself): Minority Partition & Primary Stepdown", h1_style))
    story.append(Paragraph(
        "When BOTH secondaries were disconnected, the Primary (mongo-rs0-1) was isolated in a minority partition (1/3 nodes). "
        "Attempting a <code>w:majority</code> insert timed out with <code>WriteConcernError</code>. "
        "After <code>electionTimeoutMillis</code> (10s), mongo-rs0-1 automatically stepped down from PRIMARY to SECONDARY. "
        "This strictly prevents split-brain syndrome and conflicting writes. "
        "Upon network reconnection, an election was called in Term 2, electing mongo-rs0-2 as the new Primary.",
        body_style
    ))

    # Timeline Table
    time_data = [
        ["Timestamp", "Event Description", "Node States [rs0-1, rs0-2, rs0-3]", "Term"],
        ["23:36:00", "Baseline Normal State", "[PRIMARY, SECONDARY, SECONDARY]", "1"],
        ["23:36:05", "Disconnect rs0-2 and rs0-3 (Minority 1/3)", "[PRIMARY, ISOLATED, ISOLATED]", "1"],
        ["23:36:06", "Attempt w:majority Write -> Timeouts", "[PRIMARY, ISOLATED, ISOLATED]", "1"],
        ["23:36:15", "Primary Steps Down (Anti-Split-Brain)", "[SECONDARY, ISOLATED, ISOLATED]", "1"],
        ["23:36:35", "Reconnect Network / Heal Partition", "[SECONDARY, SECONDARY, SECONDARY]", "1"],
        ["23:36:39", "Election: Term 2 -> rs0-2 Elected Primary", "[SECONDARY, PRIMARY, SECONDARY]", "2"]
    ]
    t_time = Table(time_data, colWidths=[65, 175, 220, 60])
    t_time.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_time)
    story.append(Spacer(1, 10))

    # Embedded Screenshots in PDF
    img1 = os.path.join(SCREENSHOTS_DIR, "terminal_activity_9_1_latency.png")
    if os.path.exists(img1):
        story.append(Paragraph("<b>Figure 1: Lab 9.1 Write Concern Latency Benchmark Execution</b>", body_style))
        story.append(RLImage(img1, width=520, height=180))
        story.append(Spacer(1, 8))

    img2 = os.path.join(SCREENSHOTS_DIR, "terminal_activity_9_2_try_it_yourself_minority_stepdown.png")
    if os.path.exists(img2):
        story.append(Paragraph("<b>Figure 2: Activity 9.2 Minority Partition & Stepdown Execution</b>", body_style))
        story.append(RLImage(img2, width=520, height=180))
        story.append(Spacer(1, 8))

    img3 = os.path.join(SCREENSHOTS_DIR, "terminal_docker_hub_push.png")
    if os.path.exists(img3):
        story.append(Paragraph("<b>Figure 3: Docker Hub Push Verification Log</b>", body_style))
        story.append(RLImage(img3, width=520, height=160))

    doc.build(story)
    import shutil
    shutil.copyfile(PDF_OUT_PATH, PDF_COPY_PATH)
    print(f"[OK] Generated PDF Document: {PDF_OUT_PATH}")


if __name__ == "__main__":
    build_docx_report()
    build_pdf_report()
