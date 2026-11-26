"""
Generate comprehensive Word Document (DOCX) for NoSQL Lab 4.
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


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
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:left w:val="single" w:sz="14" w:space="0" w:color="1B365D"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/></w:tblBorders>')
    tblPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(33, 37, 41)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_callout(doc, title, text, bg_color="EDF4FC", border_color="1B365D"):
    """Add a callout box for key architectural concepts."""
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
    r_title.font.color.rgb = RGBColor(27, 54, 93)

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


def build_document():
    print("[*] Generating comprehensive Word Document report for Lab 4...")
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

    r_main = title_p.add_run("LAB 4: QUERY OPERATORS, UPSERT & BULK OPERATIONS")
    r_main.font.name = "Arial"
    r_main.font.size = Pt(21)
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
    p0.add_run("Kasireddy Meghana")
    p1 = row0[1].paragraphs[0]
    p1.add_run("USN / Roll No: ").bold = True
    p1.add_run("24BTRCL119")

    row1 = meta_table.rows[1].cells
    set_cell_background(row1[0], "F0F4F9")
    set_cell_background(row1[1], "F0F4F9")
    p2 = row1[0].paragraphs[0]
    p2.add_run("Program & Dept: ").bold = True
    p2.add_run("B.Tech CSE (AIML), Section B")
    p3 = row1[1].paragraphs[0]
    p3.add_run("Environment: ").bold = True
    p3.add_run("Python 3.13 / PyMongo 4.20 / MongoDB 8.0")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    h_exec = doc.add_heading("Executive Summary & Laboratory Architecture", level=1)
    h_exec.paragraph_format.space_before = Pt(12)
    h_exec.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "This laboratory report delivers an end-to-end, enterprise-grade implementation of MongoDB Query Operators, "
        "Schema Validation, Upsert semantics, Bulk Operations, and Idempotent Data Ingestion pipelines in Python using PyMongo. "
        "The laboratory comprises four targeted milestones:\n"
        "1. Lab 4.1: Product Query API — Enforcing JSON Schema validation on an e-commerce catalog of 12 items, executing queries across comparison ($gte, $lte, $eq), logical ($or, $and), and array ($all, $size) operators, and implementing deterministic cursor pagination.\n"
        "2. Lab 4.1 (Try It Yourself): Text Search Engine — Engineering a case-insensitive regular expression ($regex) search system supporting substring extraction, anchored prefix/suffix filters, and compound criteria.\n"
        "3. Lab 4.2: Upsert & Bulk Write Operations — Developing a conditional upsert mechanism ($set and $setOnInsert) and executing a 5-operation batch update using PyMongo's bulk_write, followed by strict verification of the BulkWriteResult object.\n"
        "4. Lab 4.2 (Try It Yourself): Idempotent Bulk Ingestion — Building a multi-run re-entrant data ingestion pipeline that guarantees zero duplicate records and verified state convergence across multiple consecutive runs."
    )

    # -------------------------------------------------------------------------
    # SECTION 1: LAB 4.1 - PRODUCT QUERY API
    # -------------------------------------------------------------------------
    h1 = doc.add_heading("1. Lab 4.1: Build a Product Query API", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Implement a comprehensive suite of CRUD query operations for an e-commerce product inventory "
        "using all standard query operator categories, protected by strict database-level JSON Schema validation."
    )

    add_callout(
        doc,
        "Core Architectural Principles: MongoDB Query Operators & Validation",
        "• JSON Schema Validation: Implemented at the collection level via $jsonSchema. Documents are validated on insert and update to guarantee data integrity (positive price, non-negative stock, string array tags).\n"
        "• Comparison Operators ($gte, $lte, $eq): Efficiently filter numeric ranges and discrete states, leveraging B-Tree index scans.\n"
        "• Logical Operators ($or, $and): $or evaluates multiple alternate clauses across fields, while $and combines multiple strict criteria.\n"
        "• Array Operators ($all, $size): $all matches documents containing every specified element regardless of order, while $size matches the exact cardinality of an array field.\n"
        "• Deterministic Pagination: Combines sort(name, 1), skip((page-1)*page_size), and limit(page_size) to deliver predictable data pages for frontend consumption.",
        "F0F7FF",
        "1B365D"
    )

    # Schema Validation Table
    doc.add_heading("1.1 Product Collection Schema Validation Specification", level=2)
    val_table = doc.add_table(rows=1, cols=4)
    style_table(
        val_table,
        [1.3, 1.2, 1.3, 2.7],
        ["Field Name", "BSON Type", "Constraint", "Validation Rule & Purpose"],
        [
            ["name", "string", "Required", "Title of the product; must be non-empty string."],
            ["price", "double / int", "Required, > 0", "minimum: 0.01; prevents negative or free items."],
            ["stock", "int", "Required, >= 0", "minimum: 0; ensures inventory quantity cannot be negative."],
            ["tags", "array of strings", "Required", "items: string; ensures structured categorization."],
            ["sku", "string", "Optional", "Unique stock keeping unit identifier."],
            ["category", "string", "Optional", "Top-level department classification."],
            ["is_active", "bool", "Optional", "Product availability toggle flag."]
        ]
    )

    # Queries Summary Table
    doc.add_heading("1.2 Query Operator Test Matrix & Verification", level=2)
    q_table = doc.add_table(rows=1, cols=4)
    style_table(
        q_table,
        [1.3, 1.5, 2.7, 1.0],
        ["Category", "Operator Used", "Filter Query Expression", "Matches"],
        [
            ["Comparison", "$gte, $lte", '{"price": {"$gte": 20.0, "$lte": 50.0}}', "6 items"],
            ["Comparison", "$eq", '{"stock": {"$eq": 0}} (Out of stock)', "3 items"],
            ["Logical", "$or", '{"$or": [{"stock": 0}, {"price": {"$gt": 100}}]}', "6 items"],
            ["Logical", "$and", '{"$and": [{"stock": {"$gt": 0}}, {"tags": "premium"}]}', "4 items"],
            ["Array", "$all", '{"tags": {"$all": ["electronics", "wireless"]}}', "6 items"],
            ["Array", "$size", '{"tags": {"$size": 2}} (Exactly 2 tags)', "7 items"],
            ["Pagination", "skip / limit", 'sort("name", 1).skip(skip).limit(3)', "4 pages"]
        ]
    )

    doc.add_heading("1.3 Python PyMongo Implementation (activity_4_1.py)", level=2)
    with open("Activity_4_1/activity_4_1.py", "r", encoding="utf-8") as f:
        code_4_1 = f.read()
    add_code_block(doc, code_4_1)

    doc.add_heading("1.4 Execution Output Screenshot (Activity 4.1)", level=2)
    doc.add_paragraph("The screenshot below captures the complete execution output, illustrating schema validation rejection tests, sample product insertion, comparison and logical query results, array query outcomes, and all 4 pages of paginated catalog browsing:")
    doc.add_picture("Activity_4_1/screenshot_activity_4_1.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("1.5 Exported MongoDB Document JSON (products_activity_4_1.json Excerpt)", level=2)
    with open("Activity_4_1/products_activity_4_1.json", "r", encoding="utf-8") as f:
        json_4_1 = f.read()
    json_4_1_preview = "\n".join(json_4_1.split("\n")[:45]) + "\n  ...\n]"
    add_code_block(doc, json_4_1_preview)

    # -------------------------------------------------------------------------
    # SECTION 2: LAB 4.1 TRY IT YOURSELF - REGEX TEXT SEARCH
    # -------------------------------------------------------------------------
    h2 = doc.add_heading("2. Lab 4.1 (Try It Yourself): Text Search with $regex", level=1)
    h2.paragraph_format.space_before = Pt(16)
    h2.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Add text search capability using the MongoDB $regex operator to find products whose name "
        "contains a search string (case-insensitive), prefix anchors, suffix anchors, and compound business filters."
    )

    add_callout(
        doc,
        "Technical Analysis: $regex Evaluation in MongoDB",
        "• Case-Insensitive Flag ($options: 'i'): Allows queries to match uppercase, lowercase, and mixed-case terms identically (e.g., 'usb' matches 'USB-C Fast Charging Cable').\n"
        "• Anchored vs Unanchored Evaluation: Anchored regex patterns such as '^Ultra' allow MongoDB to utilize B-Tree index prefix ranges, executing in O(log N) index time. In contrast, unanchored substring regex queries (e.g., 'wireless') require full collection scans unless combined with indexed prefix conditions or text indexes.\n"
        "• Compound Filtering: Combining $regex with numeric and boolean filters inside $and allows the query optimizer to filter on indexed fields before evaluating regex patterns on candidate documents.",
        "EBF9F1",
        "1E7E34"
    )

    doc.add_heading("2.1 Evaluated Regular Expression Search Patterns", level=2)
    reg_table = doc.add_table(rows=1, cols=4)
    style_table(
        reg_table,
        [1.4, 1.4, 2.7, 1.0],
        ["Search Type", "Target Pattern", "MongoDB Query Expression", "Matches"],
        [
            ["Substring ('i')", "'wireless'", '{"name": {"$regex": "wireless", "$options": "i"}}', "3 items"],
            ["Case-Insensitive", "'usb'", '{"name": {"$regex": "usb", "$options": "i"}}', "2 items"],
            ["Prefix Anchor", "'^Ultra'", '{"name": {"$regex": "^Ultra", "$options": "i"}}', "1 item"],
            ["Suffix Anchor", "'(Watch|Mousepad)$'", '{"name": {"$regex": "(Watch|Mousepad)$", "$options": "i"}}', "2 items"],
            ["Compound Search", "'wireless' + price<=50", '{"$and": [{"name": {"$regex": "wireless", "$options": "i"}}, ...]}', "3 items"],
            ["Multi-Field Search", "'gaming' in name|cat", '{"$or": [{"name": {"$regex": "gaming"}}, {"category": ...}]}', "2 items"]
        ]
    )

    doc.add_heading("2.2 Python PyMongo Implementation (activity_4_1_try_it_yourself.py)", level=2)
    with open("Activity_4_1_Try_It_Yourself/activity_4_1_try_it_yourself.py", "r", encoding="utf-8") as f:
        code_4_1_try = f.read()
    add_code_block(doc, code_4_1_try)

    doc.add_heading("2.3 Execution Output Screenshot (Activity 4.1 Try It Yourself)", level=2)
    doc.add_paragraph("The screenshot below captures the complete execution output, demonstrating all 6 search pattern variations and their resolved document counts:")
    doc.add_picture("Activity_4_1_Try_It_Yourself/screenshot_activity_4_1_try_it_yourself.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("2.4 Exported MongoDB Document JSON (products_search_results.json Excerpt)", level=2)
    with open("Activity_4_1_Try_It_Yourself/products_search_results.json", "r", encoding="utf-8") as f:
        json_4_1_try = f.read()
    json_4_1_try_preview = "\n".join(json_4_1_try.split("\n")[:45]) + "\n  ...\n}"
    add_code_block(doc, json_4_1_try_preview)

    # -------------------------------------------------------------------------
    # SECTION 3: LAB 4.2 - UPSERT AND BULK OPERATIONS
    # -------------------------------------------------------------------------
    h3 = doc.add_heading("3. Lab 4.2: Implement Upsert and Bulk Operations", level=1)
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Leverage upserts and bulk writes to handle conditional inserts and batch modifications in MongoDB, "
        "verifying the structure and properties of the BulkWriteResult return object."
    )

    add_callout(
        doc,
        "Architectural Insights: Upsert Semantics and Network Optimization",
        "• Upsert Mechanism: By setting upsert=True on update_one, MongoDB checks for document existence matching the filter. If found, it applies $set; if not found, it applies both $set and $setOnInsert to construct a brand new document atomically.\n"
        "• $setOnInsert Operator: Essential for defining creation-only attributes (e.g., initial SKU, created_at, default status) that must never be overwritten on subsequent updates.\n"
        "• Bulk Write Network Efficiency: Instead of issuing 5 round-trip network socket operations for 5 individual updates, bulk_write compiles the entire batch into a single OP_MSG command buffer over the wire, cutting latency by 80%.\n"
        "• Ordered vs Unordered: In ordered=True (default), MongoDB halts execution on the first error; in ordered=False, all operations are attempted in parallel and errors are aggregated.",
        "FFF8E7",
        "D97706"
    )

    doc.add_heading("3.1 5-Operation Bulk Write Specification & Result Verification", level=2)
    bulk_table = doc.add_table(rows=1, cols=4)
    style_table(
        bulk_table,
        [1.2, 1.3, 2.5, 1.5],
        ["Operation", "Target SKU", "MongoDB Update Operator Expression", "Execution Impact"],
        [
            ["UpdateOne", "PROD-A", '{"$inc": {"stock": 10}}', "Stock increased from 40 to 50"],
            ["UpdateOne", "PROD-B", '{"$inc": {"stock": 10}}', "Stock increased from 25 to 35"],
            ["UpdateOne", "PROD-C", '{"$inc": {"stock": 10}}', "Stock increased from 15 to 25"],
            ["UpdateOne", "PROD-D", '{"$set": {"is_active": False}}', "Product marked inactive"],
            ["UpdateOne", "PROD-E", '{"$set": {"is_active": False}}', "Product marked inactive"]
        ]
    )

    # BulkWriteResult Verification Table
    doc.add_heading("3.2 BulkWriteResult Object Attribute Verification", level=2)
    res_table = doc.add_table(rows=1, cols=3)
    style_table(
        res_table,
        [1.8, 1.5, 3.2],
        ["Result Attribute", "Observed Value", "Verification & Explanation"],
        [
            ["bulk_result.acknowledged", "True", "Server acknowledged write concern receipt."],
            ["bulk_result.matched_count", "5", "All 5 target SKUs were successfully located."],
            ["bulk_result.modified_count", "5", "All 5 documents had their fields modified."],
            ["bulk_result.upserted_count", "0", "0 new documents inserted (all pre-existed)."],
            ["bulk_result.upserted_ids", "{}", "Empty dictionary as no upserts were triggered."]
        ]
    )

    doc.add_heading("3.3 Python PyMongo Implementation (activity_4_2.py)", level=2)
    with open("Activity_4_2/activity_4_2.py", "r", encoding="utf-8") as f:
        code_4_2 = f.read()
    add_code_block(doc, code_4_2)

    doc.add_heading("3.4 Execution Output Screenshot (Activity 4.2)", level=2)
    doc.add_picture("Activity_4_2/screenshot_activity_4_2.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("3.5 Exported MongoDB Document JSON (inventory_activity_4_2.json Excerpt)", level=2)
    with open("Activity_4_2/inventory_activity_4_2.json", "r", encoding="utf-8") as f:
        json_4_2 = f.read()
    add_code_block(doc, json_4_2)

    # -------------------------------------------------------------------------
    # SECTION 4: LAB 4.2 TRY IT YOURSELF - IDEMPOTENT BULK IMPORT
    # -------------------------------------------------------------------------
    h4 = doc.add_heading("4. Lab 4.2 (Try It Yourself): Idempotent Bulk Import System", level=1)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Implement an idempotent bulk import pipeline that can be executed multiple times without creating "
        "duplicate records, data corruption, or inflated counters, using MongoDB upsert logic and idempotent operators."
    )

    add_callout(
        doc,
        "Distributed Systems Principle: Idempotency in Data Pipelines",
        "• Definition of Idempotence: An operation f(x) is idempotent if f(f(x)) = f(x). Running the bulk import once or ten times leaves the database in the exact same state.\n"
        "• Operator Selection Matters:\n"
        "  - Idempotent Operators: $set, $unset, $addToSet. Setting 'price: 29.99' repeatedly causes 0 unintended state changes.\n"
        "  - Non-Idempotent Operators: $inc, $mul, $push. Re-running an $inc operation doubles or triples values on every network retry.\n"
        "• Network Fault Tolerance: In real-world microservices, network timeouts between the client and MongoDB can occur after the write has committed server-side. Idempotent bulk pipelines allow clients to safely retry failed requests without risk of duplicating rows or corrupting inventory.",
        "FDF2F8",
        "9D174D"
    )

    doc.add_heading("4.1 Multi-Run Idempotency Verification Matrix", level=2)
    idem_table = doc.add_table(rows=1, cols=5)
    style_table(
        idem_table,
        [1.1, 1.1, 1.1, 1.1, 2.1],
        ["Run #", "Upserted", "Matched", "Modified", "Database Total Documents & Result"],
        [
            ["Run 1", "8", "0", "0", "Total: 8 docs (Initial batch imported successfully)"],
            ["Run 2", "0", "8", "0", "Total: 8 docs (0 duplicates created; 100% idempotent)"],
            ["Run 3", "0", "8", "0", "Total: 8 docs (3rd run confirms zero drift)"],
            ["Run 4", "2", "8", "3", "Total: 10 docs (Delta sync: 3 updated, 2 new added)"]
        ]
    )

    doc.add_heading("4.2 Python PyMongo Implementation (activity_4_2_try_it_yourself.py)", level=2)
    with open("Activity_4_2_Try_It_Yourself/activity_4_2_try_it_yourself.py", "r", encoding="utf-8") as f:
        code_4_2_try = f.read()
    add_code_block(doc, code_4_2_try)

    doc.add_heading("4.3 Execution Output Screenshot (Activity 4.2 Try It Yourself)", level=2)
    doc.add_picture("Activity_4_2_Try_It_Yourself/screenshot_activity_4_2_try_it_yourself.png", width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("4.4 Exported MongoDB Document JSON (idempotent_import_inventory.json Excerpt)", level=2)
    with open("Activity_4_2_Try_It_Yourself/idempotent_import_inventory.json", "r", encoding="utf-8") as f:
        json_4_2_try = f.read()
    json_4_2_try_preview = "\n".join(json_4_2_try.split("\n")[:45]) + "\n  ...\n]"
    add_code_block(doc, json_4_2_try_preview)

    # -------------------------------------------------------------------------
    # SECTION 5: CONCLUSION & LEARNING OUTCOMES
    # -------------------------------------------------------------------------
    h5 = doc.add_heading("5. Technical Conclusion & Key Takeaways", level=1)
    h5.paragraph_format.space_before = Pt(16)
    h5.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Through the successful completion of NoSQL Lab 4, the following core engineering competencies were established:\n"
        "1. Schema Validation at Scale: Demonstrated how MongoDB's $jsonSchema enforces rigorous datatype and range constraints (positive prices, non-negative inventory) directly within the database engine, preventing corrupt data entry.\n"
        "2. Query Operator Mastery: Implemented comparison ($gte, $lte, $eq), logical ($or, $and), and array ($all, $size) operators to execute complex real-world queries with sub-millisecond efficiency.\n"
        "3. Regex Search Capabilities: Explored case-insensitive text search ($regex with $options: 'i') alongside prefix/suffix anchoring and compound filter clauses.\n"
        "4. Upsert & Bulk Write Mechanics: Mastered update_one(..., upsert=True) with $setOnInsert for atomic document creation and executed 5-operation batch updates via bulk_write, reducing network round-trip latency.\n"
        "5. Idempotent Pipeline Design: Engineered an idempotent data ingestion engine verified across 4 consecutive execution cycles, demonstrating duplicate-free reliability in distributed environments."
    )

    # Save to both target DOCX names
    out_docx_1 = "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_04.docx"
    out_docx_2 = "NoSQL_Lab4_Report.docx"
    doc.save(out_docx_1)
    doc.save(out_docx_2)
    print(f"[OK] Saved Word Document report to:\n  - {out_docx_1}\n  - {out_docx_2}")


if __name__ == "__main__":
    build_document()
