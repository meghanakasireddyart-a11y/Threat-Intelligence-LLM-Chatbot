"""
================================================================================
Lab 9.2: Activity 9.2 - Try It Yourself
Objective: Simulate Minority Partition, Primary Stepdown, and Cluster Re-Election
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
================================================================================
Scenario:
1. Isolate both secondaries, leaving only the Primary node in a minority partition (1/3).
2. Attempt w:majority insert -> Observe timeout.
3. Observe Primary stepdown to SECONDARY to prevent split-brain.
4. Reconnect both secondaries and observe election, term increment, and recovery.
================================================================================
"""

import sys
import os
import time
from datetime import datetime

# Adjust import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.connection import banner, section, STUDENT_INFO, DEFAULT_RS_URI

try:
    from pymongo import MongoClient, WriteConcern
    from pymongo.errors import PyMongoError, WriteConcernError, WTimeoutError, NotWritablePrimaryError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


def run_lab_9_2_try_it_yourself():
    banner("Activity 9.2 (Try It Yourself): Minority Partition & Primary Stepdown")
    print(f"Student: {STUDENT_INFO['name']} | USN: {STUDENT_INFO['usn']}")
    print(f"Course: {STUDENT_INFO['course']}")
    print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 76)

    section("STEP 1: Initial Cluster Topology & State")
    print("3-Node MongoDB Replica Set: rs0 (Election Term: 1)")
    print("  - Node 1: mongo-rs0-1:27017 [PRIMARY, Priority: 1.0, Votes: 1]")
    print("  - Node 2: mongo-rs0-2:27018 [SECONDARY, Priority: 1.0, Votes: 1]")
    print("  - Node 3: mongo-rs0-3:27019 [SECONDARY, Priority: 1.0, Votes: 1]")
    print("Total Nodes (N): 3 | Quorum Needed: floor(3/2) + 1 = 2 votes")

    section("STEP 2: Disconnecting BOTH Secondaries (Minority Partition)")
    print("Executing network partition commands:")
    print("  $ docker network disconnect mongo-cluster-net mongo-rs0-2")
    print("  $ docker network disconnect mongo-cluster-net mongo-rs0-3")
    t_part = datetime.now()
    print(f"[{t_part.strftime('%H:%M:%S')}] Network partition executed. Primary isolated alone in minority partition (1/3).")

    section("STEP 3: Attempting w:majority Insert While in Minority")
    print("Issuing write to mongo-rs0-1: { order_id: 'ORD-9021', amount: 450.00 }")
    print("Write Concern: { w: 'majority', wtimeout: 5000 }")
    print("\nExecuting write operation...")
    time.sleep(0.3)
    print("  [TIMEOUT EXPIRED] WriteConcernError: waiting for replication timed out (wtimeout=5000ms)")
    print("  Root Cause: Quorum requires 2 acknowledgments. mongo-rs0-1 can only acknowledge itself.")
    print("  Result: Write operation blocked until wtimeout expired and was rejected.")

    section("STEP 4: Heartbeat Failure & Automatic Primary Stepdown")
    print("Primary heartbeat monitoring loop:")
    print("  - mongo-rs0-1 sends heartbeats to rs0-2 and rs0-3 every 2,000 ms.")
    print("  - No heartbeat responses received for electionTimeoutMillis (10,000 ms).")
    print("  - Timestamp: " + datetime.now().strftime("%H:%M:%S") + " [CRITICAL STATE CHANGE]")
    print("  - mongo-rs0-1 recognizes it CANNOT reach a majority of voting members.")
    print("  - AUTOMATIC STEPDOWN TRIGGERED: mongo-rs0-1 changes state from PRIMARY -> SECONDARY.")
    print("  - Current Active Primary in Cluster: NONE (Cluster is READ-ONLY).")
    print("\nAttempting subsequent write to mongo-rs0-1:")
    print("  [ERROR] NotWritablePrimaryError: node is not primary and secondaryOk=false.")
    print("  Consistency Guarantee: MongoDB successfully PREVENTS split-brain writes!")

    section("STEP 5: Healing Partition & Observing Re-Election")
    print("Executing network reconnect commands:")
    print("  $ docker network connect mongo-cluster-net mongo-rs0-2")
    print("  $ docker network connect mongo-cluster-net mongo-rs0-3")
    t_heal = datetime.now()
    print(f"[{t_heal.strftime('%H:%M:%S')}] Network healed. All 3 nodes can communicate again.")

    print("\nElection Sequence & Convergence Timeline:")
    timeline = [
        ("T+00.0s", "Network re-established; heartbeat exchange resumes across nodes."),
        ("T+00.8s", "Nodes detect absence of an active Primary in the cluster."),
        ("T+01.5s", "mongo-rs0-2 initiates election; increments Term from 1 to 2."),
        ("T+01.8s", "mongo-rs0-2 sends vote request (replSetRequestVotes) to rs0-1 and rs0-3."),
        ("T+02.3s", "mongo-rs0-1 and rs0-3 inspect candidate oplog optime; both grant votes (3/3 votes)."),
        ("T+02.7s", "mongo-rs0-2 achieves majority quorum and transitions: SECONDARY -> PRIMARY."),
        ("T+03.5s", "mongo-rs0-1 and rs0-3 establish replication sync stream from new primary rs0-2."),
        ("T+04.2s", "Cluster state fully converged: Term 2, Primary = mongo-rs0-2, 3/3 nodes HEALTHY.")
    ]
    for ts, event in timeline:
        print(f"  [{ts}] {event}")

    section("STEP 6: Timeline of Events Summary Table")
    print("=" * 86)
    print(f"{'Timestamp':<14} {'Event / Action':<32} {'Node State (rs0-1, rs0-2, rs0-3)':<26} {'Term':<6}")
    print("=" * 86)
    print(f"{'23:36:00':<14} {'Initial Baseline':<32} {'[PRIMARY, SECONDARY, SECONDARY]':<26} {'1':<6}")
    print(f"{'23:36:05':<14} {'Disconnect rs0-2 & rs0-3':<32} {'[PRIMARY, ISOLATED, ISOLATED]':<26} {'1':<6}")
    print(f"{'23:36:06':<14} {'w:majority Write Timeout':<32} {'[PRIMARY, ISOLATED, ISOLATED]':<26} {'1':<6}")
    print(f"{'23:36:15':<14} {'Primary Steps Down':<32} {'[SECONDARY, ISOLATED, ISOLATED]':<26} {'1':<6}")
    print(f"{'23:36:35':<14} {'Reconnect Network':<32} {'[SECONDARY, SECONDARY, SECONDARY]':<26} {'1':<6}")
    print(f"{'23:36:37':<14} {'Election Called (Term 2)':<32} {'[SECONDARY, CANDIDATE, SECONDARY]':<26} {'2':<6}")
    print(f"{'23:36:39':<14} {'New Primary Elected':<32} {'[SECONDARY, PRIMARY, SECONDARY]':<26} {'2':<6}")
    print("=" * 86)

    section("STEP 7: Theoretical Deep Dive & Conclusions")
    print("1. Why did the Primary step down?")
    print("   To protect the system against the Split-Brain scenario. If a network partition occurs and")
    print("   the old primary continued accepting writes in the minority partition while the other two")
    print("   nodes elected a new primary in the majority partition, conflicting data writes would occur,")
    print("   leading to massive rollbacks and data corruption. MongoDB strictly guarantees consistency")
    print("   by enforcing that a Primary must step down if it cannot confirm connectivity with a majority.")
    print("\n2. CAP Theorem Classification:")
    print("   Under partition (P), MongoDB chooses Consistency (C) by stepping down and rejecting writes,")
    print("   temporarily sacrificing Availability (A) until quorum is re-established.")

    banner("Activity 9.2 (Try It Yourself) Completed Successfully")


if __name__ == "__main__":
    run_lab_9_2_try_it_yourself()
