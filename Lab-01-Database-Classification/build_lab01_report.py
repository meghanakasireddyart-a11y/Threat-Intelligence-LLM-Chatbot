"""Script to generate Prajwal_Reddy_25BTRCL145_NoSQL_Lab_01.docx with professional formatting."""

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
    r_main_title = p_title.add_run("NoSQL Database Lab 1\n")
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
    # 1. Lab 1.1: Classify Database Products
    # -------------------------------------------------------------
    h1 = doc.add_heading("1. Lab 1.1: Classify Database Products", level=1)
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
        "Survey and classify 10 prominent real-world database products into the four core NoSQL families "
        "(Key-Value, Document, Wide-Column, Graph) plus Search/Document and Multi-Model. Insert the database "
        "records into MongoDB collection 'database_products', present a structured Rich comparison table, "
        "execute an aggregation pipeline to group products by family with count metrics, and evaluate access-pattern "
        "hints to classify three mystery database products (DynamoDB, InfluxDB, OrientDB) before verifying expected answers."
    )

    h1_1 = doc.add_heading("1.1 Python Implementation (lab_01_classify_databases.py)", level=2)
    h1_1.paragraph_format.space_before = Pt(8)
    h1_1.paragraph_format.space_after = Pt(4)
    for r in h1_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_01_classify_databases.py", "r", encoding="utf-8") as f:
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
    # 2. Activity for Lab 1.1: Try It Yourself
    # -------------------------------------------------------------
    h2 = doc.add_heading("2. Activity for Lab 1.1: Advanced Database Classification & Automated Evaluation Engine (Try It Yourself)", level=1)
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
        "Expand the database classification exercise into an advanced evaluation engine in MongoDB collection 'database_products_tryit'.\n"
        "• Comprehensive Classification of Mystery & Modern Engines: Formally incorporates the 3 mystery products from Activity 1.1 "
        "(DynamoDB, InfluxDB, OrientDB) along with 5 modern, distributed, or specialized engines (ScyllaDB, ArangoDB, Google Cloud Bigtable, ClickHouse, Firebase Firestore).\n"
        "• Architectural Attributes: Records multi-model support, latency SLA tiers, underlying data structure, and licensing models.\n"
        "• Analytical Aggregations: Runs 3 aggregation pipelines (NoSQL family distribution, single vs. multi-model ratio, and open-source vs. cloud-managed breakdown).\n"
        "• Automated Workload-to-NoSQL Family Validator: Evaluates candidate database engines against explicit real-world latency, throughput, and query requirements."
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
    # 3. Lab 1.2: Map Application Data Domains to NoSQL Families
    # -------------------------------------------------------------
    h3 = doc.add_heading("3. Lab 1.2: Map Application Data Domains to NoSQL Families", level=1)
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
        "Demonstrate Polyglot Persistence by decomposing two large-scale applications (a Ride-Sharing service and a "
        "Social Media Analytics platform) into distinct data domains. Analyze specific read/write access patterns, "
        "throughput requirements, latency tolerances, and data structures to map each domain to its optimal NoSQL family "
        "and concrete database product in MongoDB collection 'app_domain_mapping'."
    )

    h3_1 = doc.add_heading("3.1 Python Implementation (lab_02_map_application.py)", level=2)
    h3_1.paragraph_format.space_before = Pt(8)
    h3_1.paragraph_format.space_after = Pt(4)
    for r in h3_1.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(30, 58, 138)

    with open("lab_02_map_application.py", "r", encoding="utf-8") as f:
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
    # 4. Activity for Lab 1.2: Try It Yourself
    # -------------------------------------------------------------
    h4 = doc.add_heading("4. Activity for Lab 1.2: Enterprise Polyglot Persistence Architecture Mapping (Try It Yourself)", level=1)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(4)
    for r in h4.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(14)
        r.bold = True
        r.font.color.rgb = RGBColor(16, 44, 87)

    p_obj4 = doc.add_paragraph()
    p_obj4.paragraph_format.space_after = Pt(6)
    r_obj4_label = p_obj4.add_run("Polyglot Persistence Architecture & Domain Analysis:\n")
    r_obj4_label.bold = True
    p_obj4.add_run(
        "Extends the architectural mapping to two massive modern enterprise ecosystems stored in 'app_domain_mapping_tryit':\n"
        "1. Global Omnichannel E-Commerce Platform (Amazon / Flipkart scale):\n"
        "   • product_catalog: Document (MongoDB) for polymorphic dynamic attributes without relational schema locks.\n"
        "   • shopping_cart_sessions: Key-Value (Redis) for sub-millisecond in-memory speed with automatic TTL cart expiry.\n"
        "   • checkout_order_ledger: Document (MongoDB with Multi-Document ACID Transactions) guaranteeing financial atomicity.\n"
        "   • recommendation_social_graph: Graph (Neo4j) for index-free adjacency multi-hop co-purchase traversals.\n"
        "   • clickstream_event_logging: Wide-Column (Apache Cassandra) for linearly scalable append-only write throughput.\n"
        "   • product_search_and_discovery: Search Engine (Elasticsearch / Atlas Search) for tokenized fuzzy full-text search.\n"
        "2. Smart Connected Healthcare & Remote Patient Telemetry System:\n"
        "   • patient_health_records: Document (MongoDB) for hierarchical FHIR/HL7 clinical encounter charts.\n"
        "   • vital_signs_iot_telemetry: Wide-Column / Time-Series (Cassandra / InfluxDB) for continuous high-frequency streams.\n"
        "   • emergency_alert_cache: Key-Value (Redis Pub/Sub) for sub-millisecond clinical paging and alert routing.\n"
        "   • epidemiological_contact_tracing: Graph (Neo4j) for infection cluster identification and exposure chain analysis."
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

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc_out = "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_01.docx"
    doc.save(doc_out)
    print(f"[OK] Successfully built {doc_out} ({os.path.getsize(doc_out)} bytes)")


if __name__ == "__main__":
    build_document()
