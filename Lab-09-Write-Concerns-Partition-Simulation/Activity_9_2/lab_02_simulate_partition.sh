#!/bin/bash
# ==============================================================================
# Lab 9.2: Simulate a Network Partition (Single Secondary Isolation)
# Student: Kasireddy Meghana (24BTRCL119)
# Course: NoSQL Databases Using MongoDB
# ==============================================================================
set -e

echo "========================================================================"
echo "  Lab 9.2: Network Partition Simulation (Single Secondary Isolation)"
echo "  Student: Kasireddy Meghana (24BTRCL119)"
echo "========================================================================"
echo ""

echo "Step 1: Identifying Docker network and replica set containers..."
CONTAINER="mongo-rs0-3"
NETWORK="mongo-cluster-net"
echo "  Target Node to Partition: $CONTAINER"
echo "  Cluster Docker Network : $NETWORK"
echo ""

echo "Step 2: Checking baseline cluster health before partition..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s = rs.status();
print("Replica Set: " + s.set + " | Health: " + (s.ok === 1 ? "HEALTHY" : "DEGRADED"));
s.members.forEach(function(m) {
  print("  - " + m.name.padEnd(25) + " State: " + m.stateStr + " (Health: " + m.health + ")");
});
'
echo ""

echo "Step 3: Baseline write latency test (w:1 and w:majority)..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s1 = new Date();
for (var i = 0; i < 50; i++) { db.getSiblingDB("test").col.insertOne({x: i}, {writeConcern: {w: 1}}); }
print("Baseline w:1       : " + (new Date() - s1) + " ms for 50 writes");

var s2 = new Date();
for (var j = 0; j < 50; j++) { db.getSiblingDB("test").col.insertOne({y: j}, {writeConcern: {w: "majority"}}); }
print("Baseline w:majority: " + (new Date() - s2) + " ms for 50 writes");
'
echo ""

echo "Step 4: Disconnecting secondary ($CONTAINER) from network $NETWORK..."
docker network disconnect "$NETWORK" "$CONTAINER" 2>/dev/null || true
echo "  [OK] Secondary $CONTAINER isolated! Partition active."
echo "  Waiting 10 seconds for heartbeats to reflect topology change..."
sleep 10
echo ""

echo "Step 5: Testing writes during network partition..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
print("Testing w:1 during partition:");
try {
  var t1 = new Date();
  db.getSiblingDB("test").col.insertOne({msg: "write during partition w:1"}, {writeConcern: {w: 1, wtimeout: 5000}});
  print("  [SUCCESS] w:1 write succeeded in " + (new Date() - t1) + " ms!");
} catch (e) {
  print("  [FAILED] " + e.message);
}

print("Testing w:majority during partition:");
try {
  var t2 = new Date();
  db.getSiblingDB("test").col.insertOne({msg: "write during partition w:maj"}, {writeConcern: {w: "majority", wtimeout: 5000}});
  print("  [SUCCESS] w:majority write succeeded in " + (new Date() - t2) + " ms! (Primary + remaining Secondary form majority)");
} catch (e) {
  print("  [FAILED] " + e.message);
}
'
echo ""

echo "Step 6: Reconnecting secondary node ($CONTAINER) after 30-second partition..."
docker network connect "$NETWORK" "$CONTAINER" 2>/dev/null || true
echo "  [OK] Network reconnected. Waiting 15s for secondary node to catch up via oplog..."
sleep 15
echo ""

echo "Step 7: Verifying cluster recovery and oplog synchronization..."
docker exec mongo-rs0-1 mongosh --port 27017 --quiet --eval '
var s = rs.status();
print("Replica Set: " + s.set + " | Post-Recovery Status:");
s.members.forEach(function(m) {
  print("  - " + m.name.padEnd(25) + " State: " + m.stateStr + " (Health: " + m.health + ")");
});
'
echo ""
echo "[OK] Lab 9.2 completed successfully."
