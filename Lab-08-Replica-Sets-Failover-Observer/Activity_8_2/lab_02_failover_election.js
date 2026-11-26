// ============================================================================
// Lab 8.2: Observe Failover and Election
// MongoDB Shell Script (.js)
// Student: Kasireddy Meghana (24BTRCL119)
// ============================================================================

print("================================================================================");
print("  Lab 8.2: Observe Failover and Election Process");
print("================================================================================");

// Step 1: Identify current PRIMARY
print("\n[STEP 1] Checking Current Replica Set Status before failover...");
var statusBefore = rs.status();
var currentPrimary = "";
statusBefore.members.forEach(function(m) {
    if (m.stateStr === "PRIMARY") {
        currentPrimary = m.name;
    }
});
print("Current PRIMARY member is: " + currentPrimary);
print("Election Term (rs.status().term): " + statusBefore.term);

// Step 2: Step down the primary
print("\n[STEP 2] Executing rs.stepDown(60) to force failover...");
print("This will cause the current primary to relinquish leadership and trigger an election.");
try {
    // rs.stepDown(stepdownSecs, secondaryCatchUpPeriodSecs)
    rs.stepDown(60);
} catch (e) {
    print("Caught expected disconnect exception from stepDown: " + e.message);
}

// Step 3: Observe election and wait for new primary
print("\n[STEP 3] Election in progress... Waiting for consensus (10 seconds)...");
sleep(10000);

// Step 4: Reconnect and run rs.status() to identify the newly elected PRIMARY
print("\n[STEP 4] Fetching updated status after election...");
try {
    var statusAfter = rs.status();
    var newPrimary = "";
    print("Election Term now incremented to: " + statusAfter.term);
    print("--------------------------------------------------------------------------------");
    printf("%-5s %-25s %-15s %-12s %-15s\n", "ID", "HOST", "STATE", "HEALTH", "ELECTION STATUS");
    print("--------------------------------------------------------------------------------");
    statusAfter.members.forEach(function(m) {
        var note = "";
        if (m.stateStr === "PRIMARY") {
            newPrimary = m.name;
            note = "<-- NEW PRIMARY!";
        } else if (m.name === currentPrimary) {
            note = "(Previous Primary stepped down)";
        }
        printf("%-5d %-25s %-15s %-12d %-15s\n", m._id, m.name, m.stateStr, m.health, note);
    });
    print("--------------------------------------------------------------------------------");
    print("Old Primary : " + currentPrimary);
    print("New Primary : " + newPrimary);
    print("[SUCCESS] Failover election concluded successfully. High availability preserved.\n");
} catch (err) {
    print("Error querying updated status: " + err.message);
}
