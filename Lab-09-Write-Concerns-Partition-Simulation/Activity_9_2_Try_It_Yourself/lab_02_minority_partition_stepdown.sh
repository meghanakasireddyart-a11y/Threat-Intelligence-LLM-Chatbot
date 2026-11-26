#!/bin/bash
# ==============================================================================
# Lab 9.2: Activity 9.2 - Try It Yourself (Bash Automation)
# Minority Partition, Primary Stepdown & Re-Election
# Student: Kasireddy Meghana (24BTRCL119)
# Course: NoSQL Databases Using MongoDB
# ==============================================================================
set -e

echo "========================================================================"
echo "  Activity 9.2: Minority Partition & Primary Stepdown Simulation"
echo "  Student: Kasireddy Meghana (24BTRCL119)"
echo "========================================================================"
echo ""

NETWORK="mongo-cluster-net"

echo "Step 1: Check initial cluster status (Term 1)..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s = rs.status();
print("Term: " + s.term + " | Health: " + (s.ok === 1 ? "HEALTHY" : "DEGRADED"));
s.members.forEach(function(m) {
  print("  - " + m.name.padEnd(25) + " State: " + m.stateStr);
});
'
echo ""

echo "Step 2: Disconnecting BOTH secondaries (mongo-rs0-2 and mongo-rs0-3)..."
docker network disconnect "$NETWORK" mongo-rs0-2 2>/dev/null || true
docker network disconnect "$NETWORK" mongo-rs0-3 2>/dev/null || true
echo "  [OK] Both secondaries disconnected! mongo-rs0-1 is alone in minority (1/3)."
echo ""

echo "Step 3: Attempting w:majority write on isolated Primary (mongo-rs0-1)..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
print("Issuing insert with { w: \"majority\", wtimeout: 5000 }...");
var s = new Date();
try {
  db.getSiblingDB("test").col.insertOne({msg: "isolated minority write"}, {writeConcern: {w: "majority", wtimeout: 5000}});
  print("  [ERROR] Should not succeed in minority!");
} catch (e) {
  print("  [EXPECTED TIMEOUT] Write timed out in " + (new Date() - s) + " ms: " + e.message);
}
'
echo ""

echo "Step 4: Waiting 12 seconds for electionTimeoutMillis to trigger stepdown..."
sleep 12

docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s = rs.status();
print("Post-timeout state of mongo-rs0-1: " + s.members[0].stateStr);
if (s.members[0].stateStr === "SECONDARY") {
  print("  [OK] Primary successfully stepped down to SECONDARY to protect consistency!");
}
'
echo ""

echo "Step 5: Reconnecting both secondaries to restore quorum..."
docker network connect "$NETWORK" mongo-rs0-2 2>/dev/null || true
docker network connect "$NETWORK" mongo-rs0-3 2>/dev/null || true
echo "  [OK] Network healed. Waiting 15s for election and convergence..."
sleep 15
echo ""

echo "Step 6: Verifying new cluster leadership and state..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s = rs.status();
print("New Term: " + s.term);
s.members.forEach(function(m) {
  print("  - " + m.name.padEnd(25) + " State: " + m.stateStr);
});
'
echo ""
echo "[OK] Activity 9.2 (Try It Yourself) completed successfully."
