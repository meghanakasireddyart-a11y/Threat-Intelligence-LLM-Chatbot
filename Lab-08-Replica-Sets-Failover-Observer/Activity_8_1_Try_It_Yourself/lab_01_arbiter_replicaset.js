// ============================================================================
// Lab 8.1 - Try It Yourself: Add an Arbiter Node to Replica Set
// MongoDB Shell Script (.js)
// Student: Kasireddy Meghana (24BTRCL119)
// ============================================================================

print("================================================================================");
print("  Lab 8.1 - Try It Yourself: Deploy Replica Set with an ARBITER Node");
print("================================================================================");

// Step 1: Initialize Replica Set with 2 Data-bearing nodes + 1 Arbiter
print("\n[STEP 1] Initializing replica set 'rs_arbiter' with 2 data nodes + 1 arbiter...");
try {
    var initConfig = {
        _id: "rs_arbiter",
        members: [
            { _id: 0, host: "localhost:27017", priority: 2 },
            { _id: 1, host: "localhost:27018", priority: 1 },
            { _id: 2, host: "localhost:27019", arbiterOnly: true }
        ]
    };
    var res = rs.initiate(initConfig);
    printjson(res);
} catch (e) {
    print("Initiate result: " + e.message);
}

// Alternatively, adding an arbiter dynamically to an existing replica set:
// rs.addArb("localhost:27019");

print("\n[STEP 2] Waiting for primary election (10 seconds)...");
sleep(10000);

// Step 3: Inspect Arbiter node characteristics
print("\n[STEP 3] Inspecting Arbiter Node Configuration:");
var status = rs.status();
print("Replica Set Name: " + status.set);
print("--------------------------------------------------------------------------------");
printf("%-5s %-25s %-15s %-12s %-12s\n", "ID", "HOST", "STATE", "VOTES", "DATA-BEARING");
print("--------------------------------------------------------------------------------");
status.members.forEach(function(m) {
    var isDataBearing = (m.stateStr !== "ARBITER") ? "YES" : "NO (0 data)";
    printf("%-5d %-25s %-15s %-12d %-12s\n", m._id, m.name, m.stateStr, (m.votes !== undefined ? m.votes : 1), isDataBearing);
});
print("--------------------------------------------------------------------------------");

// Step 4: Write verification on Primary vs Arbiter
print("\n[STEP 4] Verifying writes on Primary and examining Arbiter database...");
var dbPrim = db.getSiblingDB("inventory");
dbPrim.items.insertOne({ sku: "SKU-9901", item: "High-Capacity Server RAM", qty: 32 });
print("Document inserted into PRIMARY inventory.items collection.");

try {
    var arbConn = new Mongo("localhost:27019");
    var arbDBs = arbConn.getDBNames();
    print("Databases present on Arbiter: " + arbDBs.join(", "));
    print("Confirmed: Arbiter node DOES NOT store application data or replica oplogs!");
} catch (err) {
    print("Arbiter check: " + err.message);
}

print("\n================================================================================");
print("  CONCEPTUAL EXPLANATION: WHY USE AN ARBITER NODE?");
print("================================================================================");
print("1. BREAKING TIES IN ELECTIONS (VOTING BENEFIT):");
print("   - High availability requires an ODD number of voting members (e.g., 3, 5) to");
print("     reliably achieve a majority quorum (Majority = floor(N/2) + 1).");
print("   - With only 2 data nodes, if one fails, only 1 node remains (50% < 66.7% majority),");
print("     causing the cluster to become read-only and unable to elect a primary.");
print("   - Adding an Arbiter gives 3 total votes. If 1 data node fails, 2 votes remain");
print("     (1 data node + 1 arbiter = 2/3 votes > 50%), successfully electing a PRIMARY.");
print("");
print("2. ZERO STORAGE COST & RESOURCE SAVINGS:");
print("   - A full data-bearing secondary requires 100% data replication, dedicated NVMe/SSD");
print("     storage, RAM for indexes/WiredTiger cache, and continuous disk I/O.");
print("   - An Arbiter node stores ZERO application datasets, holds NO oplog, and requires");
print("     negligible memory and CPU. It acts purely as a lightweight heartbeat voter.");
print("================================================================================\n");
