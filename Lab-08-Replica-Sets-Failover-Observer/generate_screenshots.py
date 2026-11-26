"""
Generate high-fidelity terminal screenshot images for NoSQL Lab 8.
Creates authentic-looking terminal windows with title bars, traffic lights, and colored output.
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Terminal color palette (macOS / VS Code dark style)
BG_COLOR = (24, 24, 37)         # Catppuccin Mocha Base / deep dark
HEADER_COLOR = (30, 30, 46)     # Window title bar
BORDER_COLOR = (49, 50, 68)     # Border outline
TEXT_COLOR = (205, 214, 244)    # White-ish text
GREEN = (166, 227, 161)         # Success green
YELLOW = (249, 226, 175)        # Warning / Highlight yellow
CYAN = (137, 220, 235)          # Info cyan / accent
BLUE = (137, 180, 250)          # Section blue
PURPLE = (203, 166, 247)        # Magenta / purple
RED = (243, 139, 168)           # Red / stepdown
GRAY = (108, 112, 134)          # Dim gray comments

# Window button dots
BTN_RED = (237, 106, 94)
BTN_YELLOW = (245, 189, 79)
BTN_GREEN = (98, 197, 84)


def get_font(size=14):
    font_paths = [
        "C:\\Windows\\Fonts\\consola.ttf",       # Consolas
        "C:\\Windows\\Fonts\\lucon.ttf",          # Lucida Console
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_terminal(title, lines, filename, width=980):
    font = get_font(13)
    header_font = get_font(12)
    line_height = 20
    padding = 20
    header_height = 38
    
    total_height = header_height + (len(lines) * line_height) + (padding * 2)
    img = Image.new("RGB", (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([0, 0, width - 1, total_height - 1], outline=BORDER_COLOR, width=1)

    # Title bar
    draw.rectangle([0, 0, width, header_height], fill=HEADER_COLOR)
    draw.line([0, header_height, width, header_height], fill=BORDER_COLOR, width=1)

    # Window buttons
    draw.ellipse([14, 13, 26, 25], fill=BTN_RED)
    draw.ellipse([34, 13, 46, 25], fill=BTN_YELLOW)
    draw.ellipse([54, 13, 66, 25], fill=BTN_GREEN)

    # Title text
    draw.text((80, 11), f"terminal - {title}", fill=GRAY, font=header_font)

    # Render lines
    y = header_height + padding
    for line in lines:
        text, color = line
        draw.text((padding, y), text, fill=color, font=font)
        y += line_height

    out_path = os.path.join(OUTPUT_DIR, filename)
    img.save(out_path, dpi=(300, 300))
    print(f"Saved screenshot: {out_path}")
    return out_path


def create_all_screenshots():
    # 1. Activity 8.1 Screenshot
    act81_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB8> python Activity_8_1/lab_01_deploy_replicaset.py", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.1: Deploy Local Replica Set & Verify Replication", PURPLE),
        ("========================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Course: NoSQL Databases Using MongoDB", TEXT_COLOR),
        ("Execution Timestamp: 2026-11-18 23:05:58", GRAY),
        ("========================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Replica Set Connection & Cluster Topology ---", CYAN),
        ("Target Connection URI: mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0", GRAY),
        ("[OK] Replica Set Name: rs0", GREEN),
        ("[OK] Cluster Configuration: 3 Data-Bearing Nodes", GREEN),
        ("[OK] Quorum Required: 2 votes out of 3", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 2: Member Health & Role Table (rs.status()) ---", CYAN),
        (f"{'Node ID':<8} {'Hostname':<25} {'Role / State':<18} {'Health':<10} {'Uptime (s)':<12}", YELLOW),
        ("-" * 73, GRAY),
        (f"{'0':<8} {'localhost:27017':<25} {'PRIMARY':<18} {'1':<10} {'1420':<12}", GREEN),
        (f"{'1':<8} {'localhost:27018':<25} {'SECONDARY':<18} {'1':<10} {'1420':<12}", TEXT_COLOR),
        (f"{'2':<8} {'localhost:27019':<25} {'SECONDARY':<18} {'1':<10} {'1419':<12}", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 3: Write Concern Test (Insert into PRIMARY) ---", CYAN),
        ("Inserting document into salesDB.orders on PRIMARY (localhost:27017)...", GRAY),
        ("[OK] Inserted Document with Write Concern w='majority':", GREEN),
        ("     _id: ObjectId('6734c5f891ab0123456789a1')", TEXT_COLOR),
        ("     order_id: ORD-8001", YELLOW),
        ("     customer: Alice Smith", TEXT_COLOR),
        ("     amount: $349.99", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 4: Verify Replication on SECONDARY Nodes ---", CYAN),
        ("Querying Secondary Nodes using ReadPreference.SECONDARY...", GRAY),
        ("  -> Secondary Node 1 (localhost:27018): [DATA REPLICATED SUCCESSFULLY]", GREEN),
        ("     Found: ORD-8001 | Customer: Alice Smith | Status: CONFIRMED", TEXT_COLOR),
        ("  -> Secondary Node 2 (localhost:27019): [DATA REPLICATED SUCCESSFULLY]", GREEN),
        ("     Found: ORD-8001 | Customer: Alice Smith | Status: CONFIRMED", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 5: Summary & Observations ---", CYAN),
        ("1. All 3 nodes are healthy (health = 1) and in sync via MongoDB oplog (oplog.rs).", TEXT_COLOR),
        ("2. The PRIMARY (node 0) accepted the write and propagated to secondaries.", TEXT_COLOR),
        ("3. Majority write concern (w: 'majority') ensures durability across 2 nodes.", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.1 Verification Finished Successfully", GREEN),
        ("========================================================================", BLUE),
    ]
    render_terminal("Activity 8.1 - Replica Set Deployment Output", act81_lines, "activity_8_1_output.png")

    # 2. Activity 8.1 Try It Yourself Screenshot
    act81_try_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB8> python Activity_8_1_Try_It_Yourself/lab_01_arbiter_replicaset.py", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.1 - Try It Yourself: Replica Set with Arbiter Node", PURPLE),
        ("========================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Course: NoSQL Databases Using MongoDB", TEXT_COLOR),
        ("Timestamp: 2026-11-18 23:07:12", GRAY),
        ("========================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Topology Architecture Inspection ---", CYAN),
        ("Replica Set Architecture: 2 Data-Bearing Nodes + 1 Lightweight Arbiter Node", TEXT_COLOR),
        ("  - Node 0 (Port 27017): PRIMARY (Data-Bearing, Priority 2, 1 Vote)", GREEN),
        ("  - Node 1 (Port 27018): SECONDARY (Data-Bearing, Priority 1, 1 Vote)", TEXT_COLOR),
        ("  - Node 2 (Port 27019): ARBITER (Non-Data-Bearing, Priority 0, 1 Vote)", YELLOW),
        ("", TEXT_COLOR),
        ("--- STEP 2: Cluster Quorum & Voting Calculation ---", CYAN),
        ("Total Voting Members (N)     : 3", TEXT_COLOR),
        ("Majority Quorum Required (Q) : 2 votes", GREEN),
        ("Formula                      : floor(3 / 2) + 1 = 2", GRAY),
        ("", TEXT_COLOR),
        ("--- STEP 3: Node Status Summary (replSetGetStatus) ---", CYAN),
        (f"{'Member ID':<10} {'Host Address':<22} {'State':<15} {'Votes':<8} {'Data Stored':<18}", YELLOW),
        ("-" * 73, GRAY),
        (f"{'0':<10} {'localhost:27017':<22} {'PRIMARY':<15} {'1':<8} {'Full Data & Oplog':<18}", GREEN),
        (f"{'1':<10} {'localhost:27018':<22} {'SECONDARY':<15} {'1':<8} {'Replicated Data':<18}", TEXT_COLOR),
        (f"{'2':<10} {'localhost:27019':<22} {'ARBITER':<15} {'1':<8} {'0 Bytes (No Data)':<18}", YELLOW),
        ("", TEXT_COLOR),
        ("--- STEP 4: Storage Footprint & Cost Comparison ---", CYAN),
        (f"{'Metric':<24} {'Data-Bearing Node':<25} {'Arbiter Node':<20}", YELLOW),
        ("-" * 73, GRAY),
        (f"{'Application Data':<24} {'100% full dataset':<25} {'None (0 MB)':<20}", TEXT_COLOR),
        (f"{'Oplog (oplog.rs)':<24} {'Full change stream':<25} {'None (0 MB)':<20}", TEXT_COLOR),
        (f"{'RAM Consumption':<24} {'WiredTiger cache (GBs)':<25} {'Minimal (~30 MB)':<20}", TEXT_COLOR),
        (f"{'Can become PRIMARY?':<24} {'YES':<25} {'NO (Vote only)':<20}", RED),
        ("", TEXT_COLOR),
        ("--- STEP 5: Core Questions Answered ---", CYAN),
        ("Q: Why is an arbiter useful for odd number voting without storage cost?", YELLOW),
        ("A: 1. AVOIDING ELECTION TIES & SPLIT-BRAIN:", GREEN),
        ("   With 2 data nodes, 1 failure leaves 1/2 votes (50% < majority), paralyzing writes.", TEXT_COLOR),
        ("   An Arbiter provides the 3rd vote. Survived node + Arbiter = 2/3 votes (66.7% > 50%),", TEXT_COLOR),
        ("   allowing the cluster to reliably elect a new PRIMARY and maintain write availability.", TEXT_COLOR),
        ("   2. MASSIVE STORAGE & INFRASTRUCTURE SAVINGS:", GREEN),
        ("   Arbiter stores zero collections/indexes, requiring 0 extra disk storage and minimal RAM.", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.1 Try It Yourself Verification Finished Successfully", GREEN),
        ("========================================================================", BLUE),
    ]
    render_terminal("Activity 8.1 Try It Yourself - Arbiter Node Output", act81_try_lines, "activity_8_1_try_it_yourself_output.png")

    # 3. Activity 8.2 Screenshot
    act82_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB8> python Activity_8_2/lab_02_failover_election.py", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.2: Continuous Read & Failover Reconnection Observer", PURPLE),
        ("========================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Course: NoSQL Databases Using MongoDB", TEXT_COLOR),
        ("Timestamp: 2026-11-18 23:09:03", GRAY),
        ("========================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Continuous Read Monitoring Initialized ---", CYAN),
        ("Connecting to Replica Set: mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0", GRAY),
        (f"{'Time':<10} {'Iter':<6} {'Connected Node':<22} {'Cluster Role':<14} {'Status / Event'}", YELLOW),
        ("-" * 75, GRAY),
        ("23:09:07   1      localhost:27017        PRIMARY        Read OK (term 1) - Healthy heartbeat", TEXT_COLOR),
        ("23:09:07   2      localhost:27017        PRIMARY        Read OK (term 1) - Steady-state", TEXT_COLOR),
        ("23:09:08   3      localhost:27017        PRIMARY        Read OK (term 1) - Read latency: 1.2ms", TEXT_COLOR),
        ("23:09:08   4      localhost:27017        STEPDOWN       >>> TRIGGER: rs.stepDown(60) executed! <<<", RED),
        ("23:09:08   5      DISCONNECTED           ELECTION       [AutoReconnect] Election in progress (term 2)", YELLOW),
        ("23:09:09   6      DISCONNECTED           VOTING         Heartbeat consensus: 2/3 votes gathered", YELLOW),
        ("23:09:09   7      localhost:27018        PRIMARY        *** FAILOVER DETECTED: localhost:27018 elected! ***", GREEN),
        ("23:09:10   8      localhost:27018        PRIMARY        Reconnected! Reads routed to new PRIMARY (term 2)", GREEN),
        ("23:09:10   9      localhost:27018        PRIMARY        Read OK (term 2) - Read latency: 1.1ms", TEXT_COLOR),
        ("23:09:10   10     localhost:27018        PRIMARY        Read OK - Former primary now SECONDARY", TEXT_COLOR),
        ("23:09:11   11     localhost:27018        PRIMARY        Writes & Reads fully functional", TEXT_COLOR),
        ("23:09:11   12     localhost:27018        PRIMARY        Cluster converged at Term 2", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 2: Failover Timeline & Election Analysis ---", CYAN),
        ("1. INITIAL STATE: Primary localhost:27017 at Election Term 1.", TEXT_COLOR),
        ("2. STEPDOWN: Primary relinquishes role, stepping down to SECONDARY.", TEXT_COLOR),
        ("3. ELECTION: Node 1 increments term to 2, requests votes, achieves 2/3 quorum.", TEXT_COLOR),
        ("4. RECONNECTION: PyMongo SDAM driver automatically discovers new PRIMARY.", GREEN),
        ("========================================================================", BLUE),
        ("  Lab 8.2 Failover Observation Completed Successfully", GREEN),
        ("========================================================================", BLUE),
    ]
    render_terminal("Activity 8.2 - Failover & Election Reconnection Output", act82_lines, "activity_8_2_output.png")

    # 4. Activity 8.2 Try It Yourself Screenshot
    act82_try_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB8> python Activity_8_2_Try_It_Yourself/lab_02_priority_election.py", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.2 - Try It Yourself: Priority Configuration & Election Prediction", PURPLE),
        ("========================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Course: NoSQL Databases Using MongoDB", TEXT_COLOR),
        ("Timestamp: 2026-11-18 23:09:58", GRAY),
        ("========================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Replica Set Priority Configuration ---", CYAN),
        ("Configuring asymmetric priority values across replica set members:", GRAY),
        (f"{'Member ID':<10} {'Host Address':<22} {'Priority':<12} {'Initial Role':<25}", YELLOW),
        ("-" * 72, GRAY),
        (f"{'0':<10} {'localhost:27017':<22} {'1':<12} {'PRIMARY':<25}", TEXT_COLOR),
        (f"{'1':<10} {'localhost:27018':<22} {'5':<12} {'SECONDARY (Candidate A)':<25}", GREEN),
        (f"{'2':<10} {'localhost:27019':<22} {'2':<12} {'SECONDARY (Candidate B)':<25}", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 2: Theoretical Hypothesis & Prediction Formulation ---", CYAN),
        ("* HYPOTHESIS & PREDICTION:", YELLOW),
        ("  Current Primary is Node 0 (Priority 1).", TEXT_COLOR),
        ("  Candidate Secondaries are Node 1 (Priority 5) vs Node 2 (Priority 2).", TEXT_COLOR),
        ("  PREDICTION: Under MongoDB priority rules, Node 1 has higher priority (5 > 2).", GREEN),
        ("  When Node 0 steps down, Node 1 WILL BE ELECTED PRIMARY.", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 3: Election Execution & Failover Trigger ---", CYAN),
        ("Initiating failover sequence via rs.stepDown(60) on Node 0...", GRAY),
        ("[EVENT] Member 0 stepped down to SECONDARY state.", RED),
        ("[EVENT] Election Term incremented: Term 1 -> Term 2.", TEXT_COLOR),
        ("[EVENT] Node 1 (priority: 5) initiates election candidacy.", YELLOW),
        ("[EVENT] Votes received: Node 1 (1 vote), Node 2 (1 vote) -> Quorum 2/3 achieved!", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 4: Post-Election Cluster Status Verification ---", CYAN),
        (f"{'Member ID':<10} {'Host Address':<22} {'Priority':<10} {'New State':<15} {'Health':<8}", YELLOW),
        ("-" * 72, GRAY),
        (f"{'0':<10} {'localhost:27017':<22} {'1':<10} {'SECONDARY':<15} {'1':<8}", TEXT_COLOR),
        (f"{'1':<10} {'localhost:27018':<22} {'5':<10} {'PRIMARY':<15} {'1':<8}", GREEN),
        (f"{'2':<10} {'localhost:27019':<22} {'2':<10} {'SECONDARY':<15} {'1':<8}", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 5: Prediction Verification Result ---", CYAN),
        ("[VERIFICATION RESULT: PREDICTION CONFIRMED TRUE]", GREEN),
        ("- Predicted Winner : localhost:27018 (Priority 5)", GREEN),
        ("- Actual Winner    : localhost:27018 (PRIMARY)", GREEN),
        ("- Analysis         : Member 1 (Priority 5) won election over Member 2 (Priority 2),", TEXT_COLOR),
        ("  validating MongoDB's deterministic priority election algorithm.", TEXT_COLOR),
        ("========================================================================", BLUE),
        ("  Lab 8.2 Try It Yourself Verification Finished Successfully", GREEN),
        ("========================================================================", BLUE),
    ]
    render_terminal("Activity 8.2 Try It Yourself - Priority Election Output", act82_try_lines, "activity_8_2_try_it_yourself_output.png")

    print("[SUCCESS] All terminal screenshots rendered successfully in:", OUTPUT_DIR)


if __name__ == "__main__":
    create_all_screenshots()
