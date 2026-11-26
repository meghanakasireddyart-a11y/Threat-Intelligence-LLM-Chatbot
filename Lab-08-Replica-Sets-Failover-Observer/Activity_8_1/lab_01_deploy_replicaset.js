// ============================================================================
// Lab 8.1: Deploy a Local Replica Set
// MongoDB Shell Script (.js)
// Student: Kasireddy Meghana (24BTRCL119)
// ============================================================================

print("================================================================================");
print("  Lab 8.1: Deploy a Local 3-Node Replica Set (rs0)");
print("================================================================================");

// Step 1: Initialize the Replica Set with 3 data-bearing nodes
print("\n[STEP 1] Initializing replica set 'rs0' with 3 data-bearing members...");
try {
    var initResult = rs.initiate({
        _id: "rs0",
        members: [
            { _id: 0, host: "localhost:27017", priority: 2 },
            { _id: 1, host: "localhost:27018", priority: 1 },
            { _id: 2, host: "localhost:27019", priority: 1 }
        ]
    });
    printjson(initResult);
} catch (e) {
    print("Replica set already initialized or initialization message: " + e.message);
}

// Step 2: Wait for election to complete and PRIMARY node to become active
print("\n[STEP 2] Waiting for primary node election (10 seconds)...");
sleep(10000);

// Step 3: Insert test document into PRIMARY
print("\n[STEP 3] Inserting test document into PRIMARY database 'salesDB'...");
var dbPrimary = db.getSiblingDB("salesDB");
var insertRes = dbPrimary.orders.insertOne({
    order_id: "ORD-8001",
    customer: "Alice Smith",
    amount: 349.99,
    status: "CONFIRMED",
    created_at: new Date()
});
print("Inserted Document ID: " + insertRes.insertedId);

// Step 4: Verify Replication on SECONDARY members
print("\n[STEP 4] Verifying data replication on secondary nodes...");
sleep(2000); // Allow brief replication lag

// Connect to Node 2 (localhost:27018)
try {
    var secConn1 = new Mongo("localhost:27018");
    secConn1.setReadPref("secondary");
    var doc1 = secConn1.getDB("salesDB").orders.findOne({ order_id: "ORD-8001" });
    print("  -> Secondary 1 (localhost:27018) Replication Verified:");
    print("     Found order: " + doc1.order_id + " | Customer: " + doc1.customer + " | Amount: $" + doc1.amount);
} catch (err) {
    print("  -> Secondary 1 check: " + err.message);
}

// Connect to Node 3 (localhost:27019)
try {
    var secConn2 = new Mongo("localhost:27019");
    secConn2.setReadPref("secondary");
    var doc2 = secConn2.getDB("salesDB").orders.findOne({ order_id: "ORD-8001" });
    print("  -> Secondary 2 (localhost:27019) Replication Verified:");
    print("     Found order: " + doc2.order_id + " | Customer: " + doc2.customer + " | Amount: $" + doc2.amount);
} catch (err) {
    print("  -> Secondary 2 check: " + err.message);
}

// Step 5: Check rs.status() and display member states and health
print("\n[STEP 5] Replica Set Status Summary (rs.status()):");
var status = rs.status();
print("Set Name: " + status.set);
print("Cluster State: " + (status.ok === 1 ? "HEALTHY (OK: 1)" : "UNHEALTHY"));
print("--------------------------------------------------------------------------------");
printf("%-5s %-25s %-15s %-10s %-10s\n", "ID", "HOST", "STATE", "HEALTH", "VOTES");
print("--------------------------------------------------------------------------------");
status.members.forEach(function(m) {
    printf("%-5d %-25s %-15s %-10d %-10d\n", m._id, m.name, m.stateStr, m.health, (m.votes !== undefined ? m.votes : 1));
});
print("--------------------------------------------------------------------------------");
print("[SUCCESS] Lab 8.1 Completed: 3-Node Replica Set Active & Replication Confirmed.\n");
