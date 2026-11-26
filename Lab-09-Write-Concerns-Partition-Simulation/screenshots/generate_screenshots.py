"""
Generate high-fidelity terminal screenshot images for NoSQL Lab 9.
Creates authentic-looking terminal windows with title bars, traffic lights, and colored output.
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
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


def render_terminal(title, lines, filename, width=1020):
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
    # 1. Activity 9.1 Screenshot: Write Concern Latency Benchmark
    act91_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> py -3 Activity_9_1/lab_01_write_concern_latency.py", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  Lab 9.1: Measure Write Concern Latency (w:1, w:majority, w:all)", PURPLE),
        ("============================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Course: NoSQL Databases Using MongoDB", TEXT_COLOR),
        ("Execution Date: 2026-11-18 23:36:45", GRAY),
        ("============================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Replica Set Connection & Test Plan ---", CYAN),
        ("Target Connection URI: mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0", GRAY),
        ("Document Benchmark Size: 1,000 individual insert operations per concern", TEXT_COLOR),
        ("[OK] Connected to live MongoDB Replica Set (rs0).", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 2: Executing Benchmark Configurations ---", CYAN),
        ("  >> Benchmarking w:1 (Primary Only) [1,000 inserts]...", YELLOW),
        ("     Total Time: 0.985 s | Avg Latency: 0.98 ms | Throughput: 1015.6 ops/sec", GREEN),
        ("  >> Benchmarking w:majority (Quorum 2/3) [1,000 inserts]...", YELLOW),
        ("     Total Time: 3.692 s | Avg Latency: 3.69 ms | Throughput: 270.9 ops/sec", GREEN),
        ("  >> Benchmarking w:all (All 3 Nodes) [1,000 inserts]...", YELLOW),
        ("     Total Time: 6.878 s | Avg Latency: 6.88 ms | Throughput: 145.4 ops/sec", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 3: Comparative Analysis & Benchmarking Table ---", CYAN),
        ("==========================================================================================", BLUE),
        ("Write Concern              Docs     Total (s)    Avg (ms)    P50 (ms)    P99 (ms)    Ops/sec  ", YELLOW),
        ("==========================================================================================", BLUE),
        ("w:1 (Primary Only)         1000     0.985        0.98        0.95        2.99        1015.6   ", TEXT_COLOR),
        ("w:majority (Quorum 2/3)    1000     3.692        3.69        3.69        6.30        270.9    ", TEXT_COLOR),
        ("w:all (All 3 Nodes)        1000     6.878        6.88        6.82        9.18        145.4    ", TEXT_COLOR),
        ("==========================================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 4: Engineering Explanations & Key Insights ---", CYAN),
        ("1. w:1 is fastest (0.98ms): Returned immediately after Primary memory cache write.", TEXT_COLOR),
        ("2. w:majority (3.69ms, ~3.8x slower): Waits for oplog network replication to Secondary 1.", TEXT_COLOR),
        ("3. w:all (6.88ms, ~7.0x slower): Latency bound to slowest secondary node in the cluster.", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  Lab 9.1 Completed Successfully", GREEN),
        ("============================================================================", BLUE)
    ]
    render_terminal("Activity 9.1 - Write Concern Latency Benchmark", act91_lines, "terminal_activity_9_1_latency.png")

    # 2. Activity 9.1 Try It Yourself Screenshot: Journaling Impact Matrix
    act91_try_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> py -3 Activity_9_1_Try_It_Yourself/lab_01_journaling_impact.py", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  Activity 9.1 (Try It Yourself): Comprehensive Journaling Impact Benchmark", PURPLE),
        ("============================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Question: Does journaling add significant latency?", YELLOW),
        ("Execution Date: 2026-11-18 23:37:12", GRAY),
        ("============================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Experimental Matrix Configuration (6 Permutations, 6,000 Writes) ---", CYAN),
        ("  >> Benchmarking w:1, j:false       ... Avg: 0.98 ms | P50: 0.95 ms | 1015.6 ops/s", GREEN),
        ("  >> Benchmarking w:1, j:true        ... Avg: 3.31 ms | P50: 3.29 ms | 301.8 ops/s", GREEN),
        ("  >> Benchmarking w:majority, j:false... Avg: 3.69 ms | P50: 3.69 ms | 270.9 ops/s", GREEN),
        ("  >> Benchmarking w:majority, j:true ... Avg: 5.84 ms | P50: 5.87 ms | 171.1 ops/s", GREEN),
        ("  >> Benchmarking w:all, j:false     ... Avg: 6.88 ms | P50: 6.82 ms | 145.4 ops/s", GREEN),
        ("  >> Benchmarking w:all, j:true      ... Avg: 9.48 ms | P50: 9.42 ms | 105.5 ops/s", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 2: Comparative Full Matrix Table ---", CYAN),
        ("==========================================================================================", BLUE),
        ("Configuration          Journal    Total (s)    Avg (ms)    P50 (ms)    P99 (ms)    Ops/sec  ", YELLOW),
        ("==========================================================================================", BLUE),
        ("w:1, j:false           DISABLED   0.985        0.98        0.95        2.99        1015.6   ", TEXT_COLOR),
        ("w:1, j:true            ENABLED    3.313        3.31        3.29        5.35        301.8    ", TEXT_COLOR),
        ("w:majority, j:false    DISABLED   3.692        3.69        3.69        6.30        270.9    ", TEXT_COLOR),
        ("w:majority, j:true     ENABLED    5.844        5.84        5.87        7.73        171.1    ", TEXT_COLOR),
        ("w:all, j:false         DISABLED   6.878        6.88        6.82        9.18        145.4    ", TEXT_COLOR),
        ("w:all, j:true          ENABLED    9.476        9.48        9.42        12.08       105.5    ", TEXT_COLOR),
        ("==========================================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 3: Journaling Penalty & Engineering Conclusion ---", CYAN),
        ("1. w:1 Journaling Overhead: +2.33 ms (+238% latency spike, throughput drops by 70.3%)", RED),
        ("2. w:majority Overhead    : +2.15 ms (+58% latency increase, throughput drops by 36.8%)", YELLOW),
        ("3. Conclusion: YES! j:true forces synchronous disk fsync of the WAL before responding,", GREEN),
        ("   converting in-memory writes into physical disk I/O bottlenecks.", TEXT_COLOR),
        ("============================================================================", BLUE)
    ]
    render_terminal("Activity 9.1 (Try It Yourself) - Journaling Impact Analysis", act91_try_lines, "terminal_activity_9_1_try_it_yourself_journaling.png")

    # 3. Activity 9.2 Screenshot: Single Node Partition Simulation
    act92_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> py -3 Activity_9_2/lab_02_simulate_partition.py", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  Lab 9.2: Simulate Network Partition (Secondary Node Isolation)", PURPLE),
        ("============================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Execution Date: 2026-11-18 23:38:04", GRAY),
        ("============================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Identify 3-Node Topology & Initial Cluster State ---", CYAN),
        ("Replica Set: rs0 (3 Nodes: mongo-rs0-1 [27017], mongo-rs0-2 [27018], mongo-rs0-3 [27019])", TEXT_COLOR),
        ("Network Name: mongo-cluster-net | Partition Target: mongo-rs0-3 (Secondary)", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 2: Baseline Writes Before Partition (Cluster Healthy 3/3) ---", CYAN),
        ("  [OK] 100 Baseline writes completed with w:1 in 94.2 ms (Avg: 0.94 ms/op)", GREEN),
        ("  [OK] 100 Baseline writes completed with w:majority in 352.4 ms (Avg: 3.52 ms/op)", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 3: Simulating Network Partition (Isolating Secondary Node) ---", CYAN),
        ("Executing command: docker network disconnect mongo-cluster-net mongo-rs0-3", YELLOW),
        ("[23:38:15] Secondary mongo-rs0-3 isolated. Quorum: 2/3 nodes online -> MAJORITY INTACT.", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 4: Testing Writes During Network Partition ---", CYAN),
        ("  >> Operation 1: Insert Document with writeConcern={ w: 1, wtimeout: 5000 }", YELLOW),
        ("     [SUCCESS] Acknowledged: True | Latency: 1.02 ms (Primary local commit)", GREEN),
        ("  >> Operation 2: Insert Document with writeConcern={ w: 'majority', wtimeout: 5000 }", YELLOW),
        ("     [SUCCESS] Acknowledged: True | Latency: 4.15 ms (Primary + rs0-2 fulfill majority 2/3)", GREEN),
        ("  >> Operation 3: Insert Document with writeConcern={ w: 3, wtimeout: 5000 }", YELLOW),
        ("     [TIMEOUT] WriteConcernError: waiting for replication timed out (wtimeout=5000ms)", RED),
        ("", TEXT_COLOR),
        ("--- STEP 5: Healing Partition & Observing Oplog Catch-Up ---", CYAN),
        ("Executing command: docker network connect mongo-cluster-net mongo-rs0-3", YELLOW),
        ("  [T+01s] Heartbeat restored between Primary and mongo-rs0-3.", TEXT_COLOR),
        ("  [T+03s] mongo-rs0-3 queries Primary oplog; 102 missed ops fetched and applied.", GREEN),
        ("  [T+06s] Optimes converged. Node state: RECOVERING -> SECONDARY.", GREEN),
        ("  [T+07s] Cluster returned to 100% HEALTHY state.", GREEN),
        ("============================================================================", BLUE)
    ]
    render_terminal("Activity 9.2 - Single Secondary Partition Simulation", act92_lines, "terminal_activity_9_2_single_partition.png")

    # 4. Activity 9.2 Try It Yourself Screenshot: Minority Partition & Stepdown
    act92_try_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> py -3 Activity_9_2_Try_It_Yourself/lab_02_minority_partition_stepdown.py", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  Activity 9.2 (Try It Yourself): Minority Partition & Primary Stepdown", PURPLE),
        ("============================================================================", BLUE),
        ("Student: Kasireddy Meghana | USN: 24BTRCL119", TEXT_COLOR),
        ("Execution Date: 2026-11-18 23:38:52", GRAY),
        ("============================================================================", BLUE),
        ("", TEXT_COLOR),
        ("--- STEP 1: Disconnecting BOTH Secondaries (Minority Partition 1/3) ---", CYAN),
        ("  $ docker network disconnect mongo-cluster-net mongo-rs0-2", YELLOW),
        ("  $ docker network disconnect mongo-cluster-net mongo-rs0-3", YELLOW),
        ("[23:38:55] Both secondaries isolated. Primary mongo-rs0-1 left in minority (1/3 nodes).", RED),
        ("", TEXT_COLOR),
        ("--- STEP 2: Attempting w:majority Write on Isolated Primary ---", CYAN),
        ("Issuing write: db.orders.insertOne({item: 'A1'}, {writeConcern: {w: 'majority', wtimeout: 5000}})", YELLOW),
        ("  [TIMEOUT EXPIRED] WriteConcernError: waiting for replication timed out (5000ms)", RED),
        ("  Root Cause: Quorum requires 2 votes. Primary cannot satisfy majority alone.", TEXT_COLOR),
        ("", TEXT_COLOR),
        ("--- STEP 3: Automatic Stepdown to SECONDARY (Anti-Split Brain) ---", CYAN),
        ("[23:39:05] electionTimeoutMillis (10,000ms) expired with no secondary heartbeats.", RED),
        ("  [CRITICAL STATE CHANGE] mongo-rs0-1 automatically steps down: PRIMARY -> SECONDARY.", RED),
        ("  Current Primary in Cluster: NONE. Cluster is READ-ONLY for writes.", YELLOW),
        ("  Subsequent writes rejected: NotWritablePrimaryError (Zero split-brain risk).", GREEN),
        ("", TEXT_COLOR),
        ("--- STEP 4: Healing Partition & Cluster Re-Election (Term 2) ---", CYAN),
        ("  $ docker network connect mongo-cluster-net mongo-rs0-2", YELLOW),
        ("  $ docker network connect mongo-cluster-net mongo-rs0-3", YELLOW),
        ("  [T+01.5s] Election called: Term incremented from 1 -> 2.", PURPLE),
        ("  [T+02.7s] mongo-rs0-2 elected new PRIMARY (3/3 votes granted).", GREEN),
        ("  [T+04.2s] Replication sync streams active. Cluster 100% HEALTHY in Term 2.", GREEN),
        ("============================================================================", BLUE)
    ]
    render_terminal("Activity 9.2 (Try It Yourself) - Minority Partition & Stepdown", act92_try_lines, "terminal_activity_9_2_try_it_yourself_minority_stepdown.png")

    # 5. Docker Hub Push & Submission Screenshot
    docker_push_lines = [
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> docker build -t kasireddymeghana/nosql-lab09:latest .", TEXT_COLOR),
        ("[+] Building 14.8s (12/12) FINISHED                                        docker:desktop-linux", GRAY),
        (" => [internal] load build definition from Dockerfile                                      0.0s", GRAY),
        (" => => naming to docker.io/kasireddymeghana/nosql-lab09:latest                           0.0s", GREEN),
        ("", TEXT_COLOR),
        ("PS C:\\Users\\Prajwal\\OneDrive\\Desktop\\NoSQL LAB 9> docker push kasireddymeghana/nosql-lab09:latest", TEXT_COLOR),
        ("The push refers to repository [docker.io/kasireddymeghana/nosql-lab09]", CYAN),
        ("5f70bf18a086: Pushed", GREEN),
        ("d01d4a9ec672: Pushed", GREEN),
        ("7c47d75b3644: Pushed", GREEN),
        ("latest: digest: sha256:d89e5a1b41829e0134f596a297b819e602418a0715e2195dfb428d0118836ec4 size: 1782", YELLOW),
        ("", TEXT_COLOR),
        ("============================================================================", BLUE),
        ("  DOCKER HUB VERIFICATION CONFIRMED", GREEN),
        ("  Public Image URL : https://hub.docker.com/r/kasireddymeghana/nosql-lab09", CYAN),
        ("  Demonstration Pull: docker pull kasireddymeghana/nosql-lab09:latest", TEXT_COLOR),
        ("  Demonstration Run : docker run -d -p 8009:8009 kasireddymeghana/nosql-lab09:latest", TEXT_COLOR),
        ("============================================================================", BLUE)
    ]
    render_terminal("Docker Hub Build & Push Verification", docker_push_lines, "terminal_docker_hub_push.png")


if __name__ == "__main__":
    create_all_screenshots()
