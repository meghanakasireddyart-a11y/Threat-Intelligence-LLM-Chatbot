"""Generate comprehensive Word Document (DOCX) for NoSQL Lab 5.
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University
"""

import os
import shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>'
    )
    tcPr.append(tcMar)


def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, "F5F6F8")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/><w:left w:val="single" w:sz="14" w:space="0" w:color="1B365D"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/></w:tblBorders>'
    )
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
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/><w:right w:val="none"/></w:tblBorders>'
    )
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
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="0" w:color="B0C4DE"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="1B365D"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>'
    )
    tblPr.append(borders)


def build_document():
    print("[*] Generating comprehensive Word Document report for Lab 5...")
    doc = Document()

    # Margins
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

    r_main = title_p.add_run("LAB 5: AGGREGATION PIPELINES & $LOOKUP JOINS")
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
    p2.add_run("B.Tech CSE (AIML), Section B - Jain University")
    p3 = row1[1].paragraphs[0]
    p3.add_run("Environment: ").bold = True
    p3.add_run("Python 3.13 / PyMongo 4.20 / MongoDB 8.0")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY & AGGREGATION MENTAL MODEL
    # -------------------------------------------------------------------------
    h_exec = doc.add_heading("Executive Summary & Aggregation Architecture", level=1)
    h_exec.paragraph_format.space_before = Pt(12)
    h_exec.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "This laboratory report presents an exhaustive, production-grade implementation of MongoDB Aggregation Pipelines and Cross-Collection Joins ($lookup) using PyMongo. "
        "The aggregation framework provides an expressive, declarative processing engine modeled as a sequential pipeline of stages: "
        "[{\"$match\": ...}, {\"$group\": ...}, {\"$sort\": ...}, {\"$project\": ...}]. Each stage takes a stream of documents from the preceding stage, applies a set of functional transformations or accumulators, and emits a transformed document stream to the subsequent stage.\n\n"
        "The laboratory investigates two core technical milestones:\n"
        "1. Activity 5.1: Build a Sales Analytics Pipeline (lab_01_sales_analytics.py) — Constructing multi-stage aggregation pipelines for monthly revenue tracking, top customer spend analysis, average order sizing, $bucket numerical bucketing, and conditional order classification ($switch / $cond).\n"
        "2. Activity 5.2: Join Data with $lookup (lab_02_lookup_joins.py) — Orchestrating cross-collection relational joins, flattening subdocuments via $unwind, engineering left outer joins to detect non-matched orphan records ($size: 0), and assembling multi-collection order-invoice portfolios."
    )

    add_callout(
        doc,
        "The Pipeline Mental Model & Architectural Principles",
        "• Declarative Transformation Stream: Unlike imperative looping in client application code, MongoDB pipelines execute directly in the database engine, exploiting server-side concurrency and memory management.\n"
        "• Pipeline Stage Ordering: Multi-stage pipelines build analysis incrementally. Placing $match at the earliest possible stage drastically reduces document working sets before resource-intensive $group or $sort stages.\n"
        "• Accumulator Semantics: In a $group stage, the '_id' field defines the partition key (single field, compound object, or null for global totals). Fields utilize mathematical and set accumulators such as $sum, $avg, $min, $max, $addToSet, and $stdDevPop.\n"
        "• Reshaping & Projection: Post-aggregation stages ($project, $addFields, $unset) strip intermediate fields, compute derived metrics, and format final reporting payloads."
    )

    # -------------------------------------------------------------------------
    # SECTION 1: ACTIVITY 5.1 - SALES ANALYTICS PIPELINE
    # -------------------------------------------------------------------------
    h1 = doc.add_heading("1. Activity 5.1: Build a Sales Analytics Pipeline", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Design, verify, and execute multi-stage aggregation pipelines on an e-commerce 'orders' collection to extract executive business intelligence, revenue metrics, customer expenditure rankings, and automated order size classification."
    )

    h1_pre = doc.add_heading("1.1 Pre-Lab Theoretical Sketch: 3-Stage Category Revenue Pipeline", level=2)
    h1_pre.paragraph_format.space_before = Pt(8)
    h1_pre.paragraph_format.space_after = Pt(2)

    doc.add_paragraph(
        "Requirement Analysis: The task instructs to sketch on paper the stage sequence required to compute 'total revenue per category, highest first'. "
        "The aggregation requires exactly three stages:\n"
        "• Stage 1 ($match): Filters out non-qualifying records (e.g., status == 'completed') so that cancelled and pending orders do not skew revenue figures.\n"
        "• Stage 2 ($group): Partitions orders by category ('_id': '$category') and computes the accumulator sum of order values ('total_revenue': {'$sum': '$total'}).\n"
        "• Stage 3 ($sort): Orders the accumulated groups in descending order of total revenue ('total_revenue': -1)."
    )

    add_code_block(
        doc,
        "# Three-Stage Pipeline Sketch: Total Revenue per Category (Highest First)\n"
        "pipeline_category = [\n"
        "    {\"$match\": {\"status\": \"completed\"}},               # Stage 1: Filter\n"
        "    {\"$group\": {                                          # Stage 2: Aggregate\n"
        "        \"_id\": \"$category\",\n"
        "        \"total_revenue\": {\"$sum\": \"$total\"},\n"
        "        \"order_count\": {\"$sum\": 1},\n"
        "        \"avg_order_value\": {\"$avg\": \"$total\"}\n"
        "    }},\n"
        "    {\"$sort\": {\"total_revenue\": -1}}                   # Stage 3: Sort Descending\n"
        "]"
    )

    h1_impl = doc.add_heading("1.2 Implementation Details & Pipeline Architecture", level=2)
    h1_impl.paragraph_format.space_before = Pt(8)
    h1_impl.paragraph_format.space_after = Pt(2)

    doc.add_paragraph(
        "Activity 5.1 seeds 10 realistic order records encompassing customers (Arjun, Sneha, Rahul, Kavya, Divya), statuses (completed, pending, cancelled), regions (North, South, East, West), and categories (Electronics, Apparel, Appliances, Books). "
        "The script executes six distinct analytics pipelines:\n"
        "1. Monthly Revenue Report: Filters completed orders, extracts year-month substrings using {'$substr': ['$date', 0, 7]}, sums total revenue, computes average order value, collects unique customer sets via $addToSet, and projects rounded metrics.\n"
        "2. Category Revenue Ranking: Implements the exact 3-stage aggregation sketch ($match -> $group -> $sort).\n"
        "3. Top 3 Customers by Spending: Aggregates total spend and units purchased per customer, sorted descending and truncated using $limit: 3.\n"
        "4. Average Order Value by Status: Groups across all order statuses to evaluate fulfillment performance.\n"
        "5. Order Value Buckets: Utilizes MongoDB's native $bucket stage with boundaries [0, 1000, 3000, 5000, 10000] to bin order values.\n"
        "6. Conditional Logic Sizing: Employs $switch inside a $project stage to classify orders into Small (< $2,000), Medium ($2,000 - $4,000), and Large (>= $4,000), subsequently grouping them to compute category revenue distributions."
    )

    h1_scr = doc.add_heading("1.3 Activity 5.1 Verification Screenshot", level=2)
    h1_scr.paragraph_format.space_before = Pt(8)
    h1_scr.paragraph_format.space_after = Pt(4)

    scr_5_1_path = os.path.join(BASE_DIR, "Activity_5_1", "screenshot_activity_5_1.png")
    if os.path.exists(scr_5_1_path):
        doc.add_picture(scr_5_1_path, width=Inches(6.5))
        p_cap = doc.add_paragraph("Figure 5.1: Live Terminal Execution of Sales Analytics Pipeline (Activity 5.1).")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)

    # Table of Category Revenue
    h1_tbl = doc.add_heading("1.4 Tabular Analysis of Results", level=2)
    h1_tbl.paragraph_format.space_before = Pt(8)
    h1_tbl.paragraph_format.space_after = Pt(2)

    cat_headers = ["Category", "Orders Count", "Total Revenue", "Avg Order Value", "Revenue Contribution"]
    cat_data = [
        ["Electronics", "3", "$8,600", "$2,866.67", "37.7%"],
        ["Apparel", "3", "$7,400", "$2,466.67", "32.5%"],
        ["Appliances", "1", "$5,600", "$5,600.00", "24.6%"],
        ["Books", "1", "$1,200", "$1,200.00", "5.2%"],
        ["Total (Completed)", "8", "$22,800", "$2,850.00", "100.0%"]
    ]
    t1 = doc.add_table(rows=1, cols=5)
    style_table(t1, [1.5, 1.1, 1.3, 1.3, 1.3], cat_headers, cat_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------------------
    # SECTION 2: ACTIVITY 5.1 (TRY IT YOURSELF)
    # -------------------------------------------------------------------------
    h1_try = doc.add_heading("2. Activity 5.1 (Try It Yourself): Advanced Aggregations", level=1)
    h1_try.paragraph_format.space_before = Pt(14)
    h1_try.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Extend aggregation capabilities by exploring complex statistical metrics, regional grouping, multi-tier VIP customer loyalty classification using $switch, and dynamic discount simulation using conditional $addFields."
    )

    doc.add_paragraph(
        "Key Architectural Extensions Implemented:\n"
        "• Regional Performance Analysis: Exact 3-stage pipeline ($match -> $group -> $sort) grouping by geographical sales territory (East: $9,100, North: $8,400, South: $6,750, West: $5,600).\n"
        "• Customer Loyalty Tiering: Evaluates cumulative customer spend and categorizes clients into 'VIP Platinum' (>= $6,000), 'Gold Member' (>= $3,000), and 'Standard Silver' (< $3,000).\n"
        "• Statistical Dispersion Analysis: Evaluates variance across product categories computing $min, $max, $avg, and population standard deviation ($stdDevPop).\n"
        "• Dynamic Discount Engine: Simulates tiered promotional discounts (15% for orders >= $5,000, 8% for orders >= $2,500) using nested $cond expressions, computing post-discount net realized revenue."
    )

    scr_5_1_try_path = os.path.join(BASE_DIR, "Activity_5_1_Try_It_Yourself", "screenshot_activity_5_1_try_it_yourself.png")
    if os.path.exists(scr_5_1_try_path):
        doc.add_picture(scr_5_1_try_path, width=Inches(6.5))
        p_cap = doc.add_paragraph("Figure 5.2: Terminal Execution of Advanced Aggregations & Customer Segmentation (Activity 5.1 Try It Yourself).")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------------------
    # SECTION 3: ACTIVITY 5.2 - JOIN DATA WITH $LOOKUP
    # -------------------------------------------------------------------------
    h2 = doc.add_heading("3. Activity 5.2: Join Data with $lookup", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Implement relational joins across normalized MongoDB collections using the $lookup stage, perform left outer joins to identify non-matched orphan entities, unwind joined nested arrays, and synthesize unified invoice payloads."
    )

    h2_pre = doc.add_heading("3.1 Pre-Lab Analysis: Left-Join Non-Match Condition Rationale", level=2)
    h2_pre.paragraph_format.space_before = Pt(8)
    h2_pre.paragraph_format.space_after = Pt(2)

    doc.add_paragraph(
        "Critical Question: What must be true about the $lookup'd array for a product to count as 'never ordered'?\n\n"
        "Theoretical Rationale: In relational SQL, a non-match query is expressed via 'LEFT JOIN orders ON ... WHERE orders.product_id IS NULL'. "
        "In MongoDB, $lookup performs a left outer join by design: for every document in the source collection ('products'), MongoDB probes the target collection ('orders') and populates the resulting output field ('as': 'ordered') with an array of matching documents. "
        "If a product was never included in any order document, the sub-pipeline yields zero matching records. "
        "Consequently, the 'ordered' field is populated as an EMPTY ARRAY ([]). "
        "Therefore, to identify products that were never ordered, the aggregation filter condition must explicitly test for an array length of zero: "
        "{\"$match\": {\"ordered\": {\"$size\": 0}}}. "
        "This perfectly matches the filter condition implemented in the source code."
    )

    add_callout(
        doc,
        "Comparison: SQL Left Join vs. MongoDB Pipeline-Style $lookup",
        "• SQL Equivalent:\n"
        "  SELECT p.* FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id WHERE oi.order_id IS NULL;\n"
        "• MongoDB Aggregation Pipeline:\n"
        "  db.products.aggregate([\n"
        "    { $lookup: {\n"
        "        from: 'orders',\n"
        "        let: { pid: '$product_id' },\n"
        "        pipeline: [\n"
        "          { $unwind: '$product_ids' },\n"
        "          { $match: { $expr: { $eq: ['$product_ids', '$$pid'] } } },\n"
        "          { $limit: 1 }\n"
        "        ],\n"
        "        as: 'ordered'\n"
        "    }},\n"
        "    { $match: { 'ordered': { $size: 0 } } },\n"
        "    { $project: { product_id: 1, name: 1, category: 1, price: 1, _id: 0 } }\n"
        "  ])"
    )

    h2_impl = doc.add_heading("3.2 Implementation & Pipeline Architecture", level=2)
    h2_impl.paragraph_format.space_before = Pt(8)
    h2_impl.paragraph_format.space_after = Pt(2)

    doc.add_paragraph(
        "Activity 5.2 establishes three collections: 'orders_join', 'customers_join', and 'products_join'. "
        "Notice that ORD-204 represents an edge-case order containing zero products ('product_ids': []). "
        "Four pipelines are executed:\n"
        "1. Basic $lookup (Orders + Customers): Performs an equality join on 'customer_id', flattens the single-element customer array using $unwind, and projects customer name, tier, and city alongside order totals.\n"
        "2. Products Never Ordered: Probes 'orders_join' using a pipeline $lookup with 'let' and '$$pid'. Successfully isolates 'P006' (Sensor Pro F, $420) which has zero order associations.\n"
        "3. Order Line Items: Demonstrates array unwinding with 'preserveNullAndEmptyArrays: True' to retain empty orders (such as ORD-204), joining each product ID against 'products_join' to display line-item names and unit prices.\n"
        "4. Customer Spending Portfolio: Joins customers to orders to aggregate total lifetime spend and order history."
    )

    scr_5_2_path = os.path.join(BASE_DIR, "Activity_5_2", "screenshot_activity_5_2.png")
    if os.path.exists(scr_5_2_path):
        doc.add_picture(scr_5_2_path, width=Inches(6.5))
        p_cap = doc.add_paragraph("Figure 5.3: Terminal Execution of $lookup Joins and Non-Match Detection (Activity 5.2).")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------------------
    # SECTION 4: ACTIVITY 5.2 (TRY IT YOURSELF)
    # -------------------------------------------------------------------------
    h2_try = doc.add_heading("4. Activity 5.2 (Try It Yourself): Multi-Collection Invoices", level=1)
    h2_try.paragraph_format.space_before = Pt(14)
    h2_try.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "Objective: Engineer advanced multi-collection join workflows, uniting three collections (Orders, Customers, Products) into consolidated invoice documents, detecting inactive customers, and calculating cross-collection category sales."
    )

    doc.add_paragraph(
        "Technical Highlights:\n"
        "• Double $lookup Architecture: Demonstrates chaining multiple $lookup stages in a single pipeline. Stage 1 joins Customer metadata; Stage 2 joins Product catalogs for all IDs in the 'product_ids' array.\n"
        "• Inactive Customer Detection: Evaluates customer participation by performing a left outer join from Customers into Orders, identifying customer C104 ('Vikram', Chennai) who has placed zero orders ({'$size': 0}).\n"
        "• Product Category Revenue Breakdown: Unwinds order product IDs, joins product metadata, and computes total units sold and estimated revenue grouped by product category (Electronics: $700 across 4 units, Accessories: $300 across 2 units, Tools: $280, Consumables: $200)."
    )

    scr_5_2_try_path = os.path.join(BASE_DIR, "Activity_5_2_Try_It_Yourself", "screenshot_activity_5_2_try_it_yourself.png")
    if os.path.exists(scr_5_2_try_path):
        doc.add_picture(scr_5_2_try_path, width=Inches(6.5))
        p_cap = doc.add_paragraph("Figure 5.4: Terminal Execution of Multi-Collection Joins & Portfolio Analytics (Activity 5.2 Try It Yourself).")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------------------
    # SECTION 5: PERFORMANCE BEST PRACTICES & COMPARISON
    # -------------------------------------------------------------------------
    h_best = doc.add_heading("5. Comparative Analysis & Production Best Practices", level=1)
    h_best.paragraph_format.space_before = Pt(14)
    h_best.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "When engineering analytical queries in high-scale MongoDB deployments, understanding architectural trade-offs between Aggregation Pipelines, MapReduce, and application-level processing is essential."
    )

    comp_headers = ["Evaluation Criteria", "Aggregation Pipeline", "Application-Side Joining", "Legacy MapReduce"]
    comp_data = [
        ["Execution Engine", "Native C++ Server Engine", "Client Application Runtime", "JavaScript V8 Engine"],
        ["Network Overhead", "Minimal (only final output returned)", "Heavy (all raw docs transferred)", "Moderate"],
        ["Index Utilization", "Full support ($match, $sort prefix)", "Indexes on find() only", "Limited index support"],
        ["Memory Constraint", "100 MB per stage (allowDiskUse)", "Limited by application RAM", "Severe memory limits"],
        ["Cross-Collection Join", "Supported via $lookup", "Multiple roundtrips required", "Unsupported"],
        ["Industry Status", "Active Standard (Recommended)", "Discouraged for heavy joins", "Deprecated in MongoDB 5.0+"]
    ]
    t2 = doc.add_table(rows=1, cols=4)
    style_table(t2, [1.5, 1.7, 1.8, 1.5], comp_headers, comp_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    add_callout(
        doc,
        "Production Pipeline Optimization Guidelines",
        "1. Early $match Filtering: Always position $match as the very first stage to leverage existing B-Tree indexes and prune data volumes before downstream grouping.\n"
        "2. Selective $project Stages: Prune unneeded payload fields immediately before and after $lookup to minimize internal RAM memory consumption.\n"
        "3. Indexing Foreign Keys: Ensure the 'foreignField' in the joined collection has an index; unindexed $lookup triggers catastrophic full collection scans.\n"
        "4. Limiting Sub-Pipelines: When testing non-matches in $lookup, append a '$limit: 1' inside the sub-pipeline so the query engine halts evaluation upon finding the first match."
    )

    # -------------------------------------------------------------------------
    # SECTION 6: CONCLUSION & LEARNING OUTCOMES
    # -------------------------------------------------------------------------
    h_conc = doc.add_heading("6. Conclusion & Learning Outcomes", level=1)
    h_conc.paragraph_format.space_before = Pt(14)
    h_conc.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "The successful completion of Laboratory 5 yielded several key technical competencies:\n"
        "1. Mastered declarative aggregation pipeline mechanics, structuring multi-stage pipelines to transform raw transactional data into high-value analytical reports.\n"
        "2. Demonstrated rigorous accumulators ($sum, $avg, $min, $max, $stdDevPop, $addToSet) for multi-dimensional aggregation.\n"
        "3. Implemented conditional branching logic using $switch and $cond to dynamically categorize orders and customers without schema alterations.\n"
        "4. Gained hands-on proficiency in cross-collection relational joins ($lookup), array unwinding ($unwind), and empty array non-match detection ({'$size': 0}) replicating SQL left joins.\n"
        "5. Established a fully automated, reproducible Python testing and reporting harness ensuring consistent verification and documentation."
    )

    doc_path_student = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_05.docx")
    doc_path_std = os.path.join(BASE_DIR, "NoSQL_Lab5_Report.docx")

    doc.save(doc_path_student)
    shutil.copy2(doc_path_student, doc_path_std)
    print(f"[SUCCESS] Generated Word reports:\n  - {doc_path_student}\n  - {doc_path_std}")


if __name__ == "__main__":
    build_document()
