"""
Generate comprehensive Word Document (DOCX) for NoSQL Lab 3.
Includes all Python scripts, screenshots, MongoDB JSON structures, and in-depth technical analyses.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_code_block(doc, code_text):
    """Add a shaded code block with monospace font."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, "F5F6F8")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

    # Add light border to table
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:left w:val="single" w:sz="12" w:space="0" w:color="2B579A"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/></w:tblBorders>')
    tblPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(33, 37, 41)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_callout(doc, title, text, bg_color="EDF4FC", border_color="1B5E20"):
    """Add a callout box for key concepts or justifications."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(f"★ {title}\n")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(10)
    r_title.font.color.rgb = RGBColor(20, 60, 120)

    r_text = p.add_run(text.strip())
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = RGBColor(40, 45, 55)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def style_table(table, col_widths, headers, data):
    """Format and populate a styled data table."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(header_text)
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg = "FFFFFF" if row_idx % 2 == 0 else "F7F9FC"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].width = Inches(col_widths[col_idx])
            set_cell_background(row_cells[col_idx], bg)
            set_cell_margins(row_cells[col_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[col_idx].paragraphs[0]
            run = p.add_run(str(cell_value))
            run.font.name = "Calibri"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(40, 45, 55)

    # Borders
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="0" w:color="B0C4DE"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="1B365D"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def main():
    print("[*] Generating comprehensive Word Document report...")
    doc = Document()

    # Set page margins to standard 0.75 in
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # -------------------------------------------------------------------------
    # DOCUMENT COVER / TITLE HEADER
    # -------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(12)
    title_p.paragraph_format.space_after = Pt(2)
    r_sub = title_p.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nNoSQL DATABASES (MONGODB) LABORATORY\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.bold = True
    r_sub.font.color.rgb = RGBColor(100, 110, 125)

    r_main = title_p.add_run("LAB 3: DOCUMENT SCHEMA DESIGN & MIGRATION")
    r_main.font.name = "Arial"
    r_main.font.size = Pt(22)
    r_main.bold = True
    r_main.font.color.rgb = RGBColor(27, 54, 93)

    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(3.25)
    meta_table.columns[1].width = Inches(3.25)

    row0 = meta_table.rows[0].cells
    set_cell_background(row0[0], "F0F4F9")
    set_cell_background(row0[1], "F0F4F9")
    p0 = row0[0].paragraphs[0]
    p0.add_run("Student Name: ").bold = True
    p0.add_run("M. Prajwal")
    p1 = row0[1].paragraphs[0]
    p1.add_run("Environment: ").bold = True
    p1.add_run("Python 3.13 / PyMongo 4.20 / MongoDB 8.0")

    row1 = meta_table.rows[1].cells
    set_cell_background(row1[0], "F0F4F9")
    set_cell_background(row1[1], "F0F4F9")
    p2 = row1[0].paragraphs[0]
    p2.add_run("Module: ").bold = True
    p2.add_run("Lab 3.1 & 3.2 (with Try It Yourself)")
    p3 = row1[1].paragraphs[0]
    p3.add_run("Status: ").bold = True
    p3.add_run("100% Completed & Verified")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------------------
    # SECTION 1: LAB 3.1 - EMBEDDED DOCUMENT SCHEMA DESIGN
    # -------------------------------------------------------------------------
    h1 = doc.add_heading("1. Lab 3.1: Design an Embedded Document Schema", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Objective: Design and implement a real-world embedded document schema for a university course enrollment system. "
        "Each course document embeds its roster of enrolled students (name, ID, grade) and its meeting schedule (days, times, room). "
        "The collection is strictly governed by MongoDB JSON Schema Validation requiring title, code, instructor, and schedule."
    )

    add_callout(
        doc,
        "Embedded Document Design Pattern in Lab 3.1",
        "• High Locality of Reference: Retrieving a course and its entire student roster / schedule is accomplished in a single disk read without $lookup joins.\n"
        "• Bounded 1-to-N Cardinality: Since classroom capacity is physically bounded (e.g., 30-60 students), embedding the student roster does not risk exceeding the 16MB BSON limit.\n"
        "• Atomic Updates: Enrolling a new student with $push or updating grades with array positional operators ($) executes atomically on a single document.",
        "F0F7FF",
        "2B579A"
    )

    doc.add_heading("1.1 Python PyMongo Implementation (activity_3_1.py)", level=2)
    with open("Activity_3_1/activity_3_1.py", "r", encoding="utf-8") as f:
        code_3_1 = f.read()
    add_code_block(doc, code_3_1)

    doc.add_heading("1.2 Execution Output Screenshot (Activity 3.1)", level=2)
    doc.add_paragraph("The screenshot below captures the complete execution output, showing successful collection initialization, insertion of 3 courses, query resolution for Monday classes, instructor queries, and validator enforcement:")
    doc.add_picture("Activity_3_1/screenshot_activity_3_1.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("1.3 Exported MongoDB Document JSON (courses.json excerpt)", level=2)
    with open("Activity_3_1/courses.json", "r", encoding="utf-8") as f:
        json_3_1 = f.read()
    # Show first 45 lines of JSON
    json_3_1_preview = "\n".join(json_3_1.split("\n")[:48]) + "\n  ...\n]"
    add_code_block(doc, json_3_1_preview)

    # -------------------------------------------------------------------------
    # SECTION 2: LAB 3.1 TRY IT YOURSELF - PREREQUISITE RELATIONSHIPS
    # -------------------------------------------------------------------------
    h2 = doc.add_heading("2. Lab 3.1 (Try It Yourself): Course Prerequisites Architecture", level=1)
    h2.paragraph_format.space_before = Pt(16)
    h2.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Requirement: Extend the university course schema to track prerequisites between courses. "
        "Evaluate the architectural tradeoffs between EMBEDDING vs REFERENCING prerequisite relationships, make a design decision, and justify the choice."
    )

    add_callout(
        doc,
        "Architectural Decision & Justification: REFERENCING DESIGN",
        "DECISION: We choose to REFERENCE prerequisite courses using an array of course codes (e.g., prerequisites: ['CS101', 'MATH101']).\n\n"
        "JUSTIFICATION:\n"
        "1. Prevents Infinite Recursion & Deep Hierarchical Bloat: Prerequisites form a Directed Acyclic Graph (DAG). If courses were embedded within courses, prerequisites of prerequisites would cause unbounded nested recursion.\n"
        "2. Eliminates Update Anomalies (Single Source of Truth): Fundamental courses (e.g., CS101, MATH101) serve as prerequisites for dozens of advanced courses. Referencing ensures course details (credits, syllabus, titles) are updated in exactly one document.\n"
        "3. Prevents BSON 16MB Overflow: Avoids replicating identical course subtrees repeatedly across the database.\n"
        "4. Native Recursive Traversal via $graphLookup: MongoDB's $graphLookup aggregation operator natively traverses referenced course codes, reconstructing the entire prerequisite graduation tree across arbitrary depths in a single lightning-fast database query.",
        "EBF9F1",
        "1E7E34"
    )

    # Prerequisite DAG Diagram Table
    doc.add_heading("2.1 Prerequisite Directed Acyclic Graph (DAG) Structure", level=2)
    dag_headers = ["Course Code", "Course Title", "Direct Prerequisites", "Transitive Prerequisites", "Level"]
    dag_data = [
        ["CS101", "Introduction to Programming", "None (Entry Level)", "None", "Level 0"],
        ["MATH101", "Discrete Mathematics", "None (Entry Level)", "None", "Level 0"],
        ["CS201", "Data Structures & Algorithms", "['CS101']", "CS101", "Level 1"],
        ["CS401", "Machine Learning Foundations", "['CS201', 'MATH101']", "CS201, MATH101, CS101", "Level 2"],
        ["CS501", "Deep Reinforcement Learning", "['CS401']", "CS401, CS201, MATH101, CS101", "Level 3"]
    ]
    dag_table = doc.add_table(rows=1, cols=5)
    style_table(dag_table, [1.1, 1.8, 1.4, 1.4, 0.8], dag_headers, dag_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("2.2 Python PyMongo Implementation (activity_3_1_try_it_yourself.py)", level=2)
    with open("Activity_3_1_Try_It_Yourself/activity_3_1_try_it_yourself.py", "r", encoding="utf-8") as f:
        code_3_1_try = f.read()
    add_code_block(doc, code_3_1_try)

    doc.add_heading("2.3 Execution Output Screenshot (Activity 3.1 Try It Yourself)", level=2)
    doc.add_paragraph("The screenshot below confirms $lookup resolution for direct prerequisites and recursive $graphLookup traversal across depth levels 0, 1, and 2:")
    doc.add_picture("Activity_3_1_Try_It_Yourself/screenshot_activity_3_1_try_it_yourself.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("2.4 Exported MongoDB Document JSON (courses_with_prerequisites.json excerpt)", level=2)
    with open("Activity_3_1_Try_It_Yourself/courses_with_prerequisites.json", "r", encoding="utf-8") as f:
        json_3_1_try = f.read()
    json_3_1_try_preview = "\n".join(json_3_1_try.split("\n")[:45]) + "\n  ...\n]"
    add_code_block(doc, json_3_1_try_preview)

    # -------------------------------------------------------------------------
    # SECTION 3: LAB 3.2 - MIGRATE FROM REFERENCED TO EMBEDDED DESIGN
    # -------------------------------------------------------------------------
    h3 = doc.add_heading("3. Lab 3.2: Migrate from Referenced to Embedded Design", level=1)
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Objective: Convert a normalized referenced blog system (separate posts and comments collections) to a denormalized "
        "embedded design (comments embedded directly as an array inside each post document) and compare query counts and performance characteristics."
    )

    doc.add_heading("3.1 Architectural Comparison: Referenced vs Embedded", level=2)
    comp_headers = ["Architectural Dimension", "Referenced Design (Normalized)", "Embedded Design (Denormalized)"]
    comp_data = [
        ["Collection Structure", "2 collections: posts and comments", "1 unified collection: posts_embedded"],
        ["Display Post with Comments", "2 queries (find post + find comments) or 1 $lookup", "1 query: simple find_one({'_id': id})"],
        ["Join Engine Overhead", "High: Server-side $lookup join processing", "Zero: No server-side join required"],
        ["Read Latency & Throughput", "Higher latency, multiple disk block seeks", "Sub-millisecond single document seek"],
        ["Write Atomicity", "Non-atomic across multiple collections", "Fully atomic single-document updates ($push)"],
        ["Scalability Ceiling", "Virtually unbounded (billions of comments)", "Bounded by 16MB document size limit"],
        ["Ideal Workload Fit", "Unbounded comments (> 1,000 / high write velocity)", "Bounded comments (< 100 / high read ratio)"]
    ]
    comp_table = doc.add_table(rows=1, cols=3)
    style_table(comp_table, [1.8, 2.35, 2.35], comp_headers, comp_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("3.2 Python PyMongo Implementation (activity_3_2.py)", level=2)
    with open("Activity_3_2/activity_3_2.py", "r", encoding="utf-8") as f:
        code_3_2 = f.read()
    add_code_block(doc, code_3_2)

    doc.add_heading("3.3 Execution Output Screenshot (Activity 3.2)", level=2)
    doc.add_paragraph("The screenshot below captures the complete execution output, showing referenced population, $lookup join, aggregation pipeline migration ($out), and verification:")
    doc.add_picture("Activity_3_2/screenshot_activity_3_2.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("3.4 Exported MongoDB Document JSON (posts_embedded.json excerpt)", level=2)
    with open("Activity_3_2/posts_embedded.json", "r", encoding="utf-8") as f:
        json_3_2 = f.read()
    json_3_2_preview = "\n".join(json_3_2.split("\n")[:45]) + "\n  ...\n]"
    add_code_block(doc, json_3_2_preview)

    # -------------------------------------------------------------------------
    # SECTION 4: LAB 3.2 TRY IT YOURSELF - SCALING TO 10,000 COMMENTS
    # -------------------------------------------------------------------------
    h4 = doc.add_heading("4. Lab 3.2 (Try It Yourself): Scaling to 10,000 Comments", level=1)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Scenario: A popular viral blog post receives 10,000 comments. Analyze why a naive embedded design is fundamentally problematic, "
        "and formulate, implement, and benchmark an optimal alternative schema design."
    )

    add_callout(
        doc,
        "Technical Breakdown: Why Full Embedding Breaks Down at 10,000 Comments",
        "1. The 16MB Hard BSON Boundary: MongoDB enforces a strict 16,777,216 byte maximum document size limit. A realistic comment document (with author ID, avatar URL, content, timestamp, likes, and reactions) averages 500 to 1,500 bytes. At 10,000 comments, the document exceeds 10MB to 15MB+, quickly crashing all subsequent $push write operations with fatal DocumentTooLarge errors.\n\n"
        "2. WiredTiger Cache Thrashing & RAM Starvation: MongoDB loads entire BSON documents into the WiredTiger RAM cache. Reading a 15MB post repeatedly forces the engine to evict active indexes and working sets from memory, degrading global database throughput.\n\n"
        "3. Network Overfetching & Mobile Degradation: Readers browsing an article only read the top 5 to 20 comments. Transferring a 15MB payload over HTTP/WebSocket creates massive network latency and unnecessary egress bandwidth costs.\n\n"
        "4. High Write Contention & Document Relocation: Continually pushing comments into an ever-expanding array forces WiredTiger to repeatedly relocate the document on disk, leading to lock contention and storage fragmentation.",
        "FFF3CD",
        "856404"
    )

    doc.add_heading("4.1 Recommended Solution: The Hybrid Subset Pattern", level=2)
    doc.add_paragraph(
        "To achieve both optimal read performance and infinite scalability, we implement the HYBRID SUBSET PATTERN combined with referenced paginated archives:\n"
        "• Core Post Document: Stores post body, an atomic comment counter (comment_count: 10000), and an embedded array of only the TOP 5-10 most recent comments (recent_comments). Initial page render requires exactly 1 query, 0 joins, and transfers < 2 KB.\n"
        "• Comments Archive Collection: Stores all 10,000 comments as individual documents referencing post_id, indexed on (post_id ASC, created_at DESC). When a reader clicks 'Load More', a fast paginated cursor query fetches 10 comments at a time in sub-millisecond time."
    )

    doc.add_heading("4.2 Architecture Tradeoff Matrix", level=2)
    matrix_headers = ["Performance Characteristic", "Naive Full Embedding (Problematic)", "Hybrid Subset Pattern (Optimal)"]
    matrix_data = [
        ["Document Size for 10K Comments", "~10 MB to 15 MB (Risk of exceeding 16MB)", "~2 KB Post + ~1 KB per paginated batch"],
        ["16MB Boundary Risk", "FATAL: Exceeds limit, halting writes", "ZERO RISK: Document size remains bounded"],
        ["Initial Page Render Latency", "High (Seconds: 15MB wire transfer)", "Sub-millisecond (< 1ms: 2KB wire transfer)"],
        ["WiredTiger Cache Footprint", "Severe cache thrashing & page evictions", "Optimal memory footprint, minimal RAM"],
        ["Network Egress Bandwidth", "Severe overfetching (15MB per view)", "Minimal strictly on-demand data transfer"],
        ["Concurrency & Write Locking", "Intense document-level write contention", "Distributed append-only inserts to archive"],
        ["Pagination Implementation", "Costly array slicing inside BSON engine", "Native B-Tree range query with compound index"]
    ]
    matrix_table = doc.add_table(rows=1, cols=3)
    style_table(matrix_table, [1.8, 2.35, 2.35], matrix_headers, matrix_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("4.3 Python PyMongo Implementation (activity_3_2_try_it_yourself.py)", level=2)
    with open("Activity_3_2_Try_It_Yourself/activity_3_2_try_it_yourself.py", "r", encoding="utf-8") as f:
        code_3_2_try = f.read()
    add_code_block(doc, code_3_2_try)

    doc.add_heading("4.4 Execution Output Screenshot (Activity 3.2 Try It Yourself)", level=2)
    doc.add_paragraph("The screenshot below captures the complete execution output, showing BSON size math, Subset Pattern insertion, sub-millisecond initial render, and index-backed pagination:")
    doc.add_picture("Activity_3_2_Try_It_Yourself/screenshot_activity_3_2_try_it_yourself.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("4.5 Exported MongoDB Document JSON (viral_post_alternative_design.json excerpt)", level=2)
    with open("Activity_3_2_Try_It_Yourself/viral_post_alternative_design.json", "r", encoding="utf-8") as f:
        json_3_2_try = f.read()
    add_code_block(doc, json_3_2_try)

    # -------------------------------------------------------------------------
    # CONCLUSION / SUMMARY
    # -------------------------------------------------------------------------
    h_end = doc.add_heading("5. Summary of Key Learnings & Schema Design Rules", level=1)
    h_end.paragraph_format.space_before = Pt(16)
    h_end.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Through Lab 3.1, Lab 3.2, and their respective Try It Yourself activities, the fundamental principles of MongoDB document schema design were proven both theoretically and experimentally:\n\n"
        "1. Favor Embedding for 1-to-Few / Bounded Relationships: When child entities are bounded and consistently retrieved with the parent (e.g., course schedules and student rosters under 60 students), embedding maximizes read throughput and guarantees single-document atomic operations.\n"
        "2. Favor Referencing for 1-to-Many / Unbounded / Graph Relationships: When entities form complex directed graphs (e.g., course prerequisites) or have unbounded growth, referencing prevents recursion, eliminates data duplication, and enables graph traversal with $graphLookup.\n"
        "3. Apply Design Patterns for High-Scale Workloads: When scaling to high cardinalities (e.g., 10,000 comments on a viral post), hybrid patterns like the Subset Pattern marry the best of both worlds—embedding a small bounded subset for instantaneous initial page loads while referencing the complete archive with compound indexes for efficient on-demand pagination."
    )

    output_doc_path = "NoSQL_Lab3_Report.docx"
    doc.save(output_doc_path)
    print(f"[OK] Successfully generated Word Document report: {output_doc_path}")

if __name__ == "__main__":
    main()
