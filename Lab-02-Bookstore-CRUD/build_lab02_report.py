"""Script to generate Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_02.docx with professional formatting."""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn


def set_cell_background_and_margins(cell, fill_hex="F4F6F8"):
    """Set cell background shading and internal padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    # shading
    shd_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    tcPr.append(parse_xml(shd_xml))
    
    # borders (subtle gray)
    borders_xml = f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
        <w:left w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
        <w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
    </w:tcBorders>'''
    tcPr.append(parse_xml(borders_xml))

    # cell margins (padding)
    tcMar_xml = f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="140" w:type="dxa"/>
        <w:left w:w="200" w:type="dxa"/>
        <w:bottom w:w="140" w:type="dxa"/>
        <w:right w:w="200" w:type="dxa"/>
    </w:tcMar>'''
    tcPr.append(parse_xml(tcMar_xml))


def add_code_block(doc, code_text):
    """Add a single-cell table containing formatted code."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.rows[0].cells[0]
    set_cell_background_and_margins(cell, "F6F8FA")

    # Clear default paragraph
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05

    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(36, 41, 47)


def build_document():
    doc = docx.Document()

    # Page Margins: 0.75 in
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(40, 40, 40)

    # Document Header
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(2)
    p_title.paragraph_format.line_spacing = 1.15
    r_main_title = p_title.add_run("NoSQL Database Lab 2\n")
    r_main_title.bold = True
    r_main_title.font.name = 'Calibri'
    r_main_title.font.size = Pt(20)
    r_main_title.font.color.rgb = RGBColor(16, 44, 87)

    r_author = p_title.add_run("Kasireddy Meghana\n")
    r_author.bold = True
    r_author.font.size = Pt(13)
    r_author.font.color.rgb = RGBColor(30, 41, 59)

    r_info = p_title.add_run("USN: 24BTRCL119  |  Branch: CSE (AIML), Section B\nFaculty of Engineering & Technology, Jain (Deemed-to-be) University\nAcademic Year: 2026")
    r_info.font.size = Pt(9.5)
    r_info.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # 1. Lab 2.1: Environment Setup Verification
    # -------------------------------------------------------------
    h1 = doc.add_heading("1. Lab 2.1: Environment Setup Verification", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    for r in h1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.bold = True
        r.font.color.rgb = RGBColor(16, 44, 87)

    p_obj1 = doc.add_paragraph()
    p_obj1.paragraph_format.space_after = Pt(6)
    r_obj_label = p_obj1.add_run("Objective: ")
    r_obj_label.bold = True
    p_obj1.add_run(
        "Validate the core Python interpreter environment, PyMongo driver installation, local MongoDB "
        "daemon connectivity, Docker container status, and MongoDB Atlas configuration before executing database "
        "workloads. Display a structured Rich verification checklist, persist an end-to-end environment audit log "
        "into MongoDB collection 'environment_setup_verification' (database 'bookstore'), and export the resulting "
        "records into 'lab_01_setup_environment.json'."
    )

    h1_1 = doc.add_heading("1.1 Python Implementation (lab_01_setup_environment.py)", level=2)
    h1_1.paragraph_format.space_before = Pt(8)
    h1_1.paragraph_format.space_after = Pt(4)
    for r in h1_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_01_setup_environment.py", "r", encoding="utf-8") as f:
        code_lab01 = f.read()
    add_code_block(doc, code_lab01)

    h1_2 = doc.add_heading("1.2 Execution Output Screenshot", level=2)
    h1_2.paragraph_format.space_before = Pt(10)
    h1_2.paragraph_format.space_after = Pt(6)
    for r in h1_2.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    if os.path.exists("screenshot_lab_01.png"):
        doc.add_picture("screenshot_lab_01.png", width=Inches(6.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # 2. Activity for Lab 2.1: Try It Yourself
    # -------------------------------------------------------------
    h2 = doc.add_heading("2. Activity for Lab 2.1: Dual MongoDB Instance Version Comparison (Atlas vs. Docker/Local) (Try It Yourself)", level=1)
    h2.paragraph_format.space_before = Pt(16)
    h2.paragraph_format.space_after = Pt(4)
    for r in h2.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.bold = True
        r.font.color.rgb = RGBColor(16, 44, 87)

    p_obj2 = doc.add_paragraph()
    p_obj2.paragraph_format.space_after = Pt(6)
    r_obj2_label = p_obj2.add_run("Objective & Technical Discussion:\n")
    r_obj2_label.bold = True
    p_obj2.add_run(
        "Establish concurrent live connections to both MongoDB Atlas and Docker/Local MongoDB instances and systematically "
        "compare their server version information and low-level engine parameters using the server_info() command.\n"
        "• Concurrent Connectivity & Latency Measurement: Simultaneously opens MongoClient sessions to both local daemon and cloud Atlas endpoints, calculating round-trip ping latencies.\n"
        "• Deep server_info() Extraction: Queries and parses server version arrays, Git commit revisions, host operating system environments, bit architecture (64-bit), max BSON object size (16MB), and supported storage engines (WiredTiger, devnull).\n"
        "• Architectural Comparison: Contrasts a local containerized deployment (zero-cost, fast local feedback loop, single-node daemon) with MongoDB Atlas managed cloud infrastructure (multi-node replica sets, cross-AZ failover, automated patching, TLS encryption).\n"
        "• Persistence & Export: Stores the structured dual-instance version comparison audit into collection 'server_version_comparison' and exports the JSON file 'lab_01_try_yourself.json'."
    )

    h2_1 = doc.add_heading("2.1 Python Implementation (lab_01_try_yourself.py)", level=2)
    h2_1.paragraph_format.space_before = Pt(8)
    h2_1.paragraph_format.space_after = Pt(4)
    for r in h2_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_01_try_yourself.py", "r", encoding="utf-8") as f:
        code_lab01_tryit = f.read()
    add_code_block(doc, code_lab01_tryit)

    h2_2 = doc.add_heading("2.2 Execution Output Screenshot", level=2)
    h2_2.paragraph_format.space_before = Pt(10)
    h2_2.paragraph_format.space_after = Pt(6)
    for r in h2_2.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    if os.path.exists("screenshot_lab_01_tryit.png"):
        doc.add_picture("screenshot_lab_01_tryit.png", width=Inches(6.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # 3. Lab 2.2: Bookstore CRUD Operations
    # -------------------------------------------------------------
    h3 = doc.add_heading("3. Lab 2.2: Bookstore CRUD Operations", level=1)
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(4)
    for r in h3.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.bold = True
        r.font.color.rgb = RGBColor(16, 44, 87)

    p_obj3 = doc.add_paragraph()
    p_obj3.paragraph_format.space_after = Pt(6)
    r_obj3_label = p_obj3.add_run("Objective: ")
    r_obj3_label.bold = True
    p_obj3.add_run(
        "Demonstrate fundamental CRUD (Create, Read, Update, Delete) operations using PyMongo against realistic, "
        "nested technical book documents in collection 'books' (database 'bookstore'). Seed documents with embedded publisher "
        "objects and tag arrays, execute filter queries using MongoDB query operators ($gt, equality, $gte/$lte, array matching), "
        "perform an in-place bulk price modification using $mul, remove a document by title, and export the final collection "
        "documents into 'lab_02_bookstore_crud.json'."
    )

    h3_1 = doc.add_heading("3.1 Python Implementation (lab_02_bookstore_crud.py)", level=2)
    h3_1.paragraph_format.space_before = Pt(8)
    h3_1.paragraph_format.space_after = Pt(4)
    for r in h3_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_02_bookstore_crud.py", "r", encoding="utf-8") as f:
        code_lab02 = f.read()
    add_code_block(doc, code_lab02)

    h3_2 = doc.add_heading("3.2 Execution Output Screenshot", level=2)
    h3_2.paragraph_format.space_before = Pt(10)
    h3_2.paragraph_format.space_after = Pt(6)
    for r in h3_2.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    if os.path.exists("screenshot_lab_02.png"):
        doc.add_picture("screenshot_lab_02.png", width=Inches(6.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # 4. Activity for Lab 2.2: Try It Yourself
    # -------------------------------------------------------------
    h4 = doc.add_heading("4. Activity for Lab 2.2: Targeted Price Escalation for Pre-2010 Publications & Compass Verification (Try It Yourself)", level=1)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(4)
    for r in h4.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.bold = True
        r.font.color.rgb = RGBColor(16, 44, 87)

    p_obj4 = doc.add_paragraph()
    p_obj4.paragraph_format.space_after = Pt(6)
    r_obj4_label = p_obj4.add_run("Objective & Technical Discussion:\n")
    r_obj4_label.bold = True
    p_obj4.add_run(
        "Implement a targeted update operation in PyMongo to escalate the price of books published strictly before 2010 by 10% "
        "using the atomic $mul operator, verify price integrity across the catalog, and visually validate the results in MongoDB Compass.\n"
        "• Expanded Catalog Partitioning: Seeds 8 technical books in collection 'books_pre2010_update', creating an explicit partition between pre-2010 classics (Clean Code 2008, Design Patterns 1994, Refactoring 1999, CLRS 2009) and post-2010 modern publications.\n"
        "• Targeted Atomic Update: Executes update_many() with filter {'year': {'$lt': 2010}} and update operator {'$mul': {'price': 1.10}}, ensuring that only qualified vintage publications undergo price multiplication without touching subsequent editions.\n"
        "• Catalog Integrity Audit: Performs pre- and post-update reconciliation, validating that exactly 4 pre-2010 titles received the 10% increment while all 4 post-2010 publications retained their initial pricing.\n"
        "• MongoDB Compass Verification Procedure: Documents step-by-step GUI inspection in MongoDB Compass with explicit filter and projection parameters.\n"
        "• Data Export: Serializes the updated collection state into 'lab_02_try_yourself.json'."
    )

    h4_1 = doc.add_heading("4.1 Python Implementation (lab_02_try_yourself.py)", level=2)
    h4_1.paragraph_format.space_before = Pt(8)
    h4_1.paragraph_format.space_after = Pt(4)
    for r in h4_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_02_try_yourself.py", "r", encoding="utf-8") as f:
        code_lab02_tryit = f.read()
    add_code_block(doc, code_lab02_tryit)

    h4_2 = doc.add_heading("4.2 Execution Output Screenshot", level=2)
    h4_2.paragraph_format.space_before = Pt(10)
    h4_2.paragraph_format.space_after = Pt(6)
    for r in h4_2.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    if os.path.exists("screenshot_lab_02_tryit.png"):
        doc.add_picture("screenshot_lab_02_tryit.png", width=Inches(6.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Compass Verification Subsection
    h4_3 = doc.add_heading("4.3 MongoDB Compass Visual Verification", level=2)
    h4_3.paragraph_format.space_before = Pt(10)
    h4_3.paragraph_format.space_after = Pt(6)
    for r in h4_3.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    p_compass_desc = doc.add_paragraph()
    p_compass_desc.paragraph_format.space_after = Pt(6)
    p_compass_desc.add_run(
        "Verification in MongoDB Compass confirms the successful execution of the targeted update operation. "
        "Connecting to mongodb://localhost:27017 and navigating to database 'bookstore' -> collection 'books_pre2010_update', "
        "the filter query { \"year\": { \"$lt\": 2010 } } isolates the 4 matching documents. "
        "As displayed in the Compass interface screenshot below, the updated price fields reflect the 10% increase:\n"
        "• Clean Code (2008): $39.99 → $43.99\n"
        "• Design Patterns: Elements of Reusable OOD (1994): $54.99 → $60.49\n"
        "• Refactoring: Improving the Design of Existing Code (1999): $47.50 → $52.25\n"
        "• Introduction to Algorithms (2009): $89.00 → $97.90"
    )

    if os.path.exists("screenshot_compass_verification.png"):
        doc.add_picture("screenshot_compass_verification.png", width=Inches(6.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc_out = "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_02.docx"
    doc.save(doc_out)
    print(f"[OK] Successfully built {doc_out} ({os.path.getsize(doc_out)} bytes)")


if __name__ == "__main__":
    build_document()
