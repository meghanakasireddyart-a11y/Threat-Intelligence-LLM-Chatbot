// ============================================================================
// Lab 8.2 - Try It Yourself: Configure Priority Values & Election Prediction
// MongoDB Shell Script (.js)
// Student: Kasireddy Meghana (24BTRCL119)
// ============================================================================

print("================================================================================");
print("  Lab 8.2 - Try It Yourself: Priority-Based Elections and Prediction");
print("================================================================================");

// Step 1: Read current configuration
print("\n[STEP 1] Fetching current replica set configuration (rs.conf())...");
var cfg = rs.conf();

// Step 2: Configure asymmetric priority values
print("\n[STEP 2] Modifying member priority settings:");
print("  - Node 0 (localhost:27017): Setting Priority = 1 (Current Primary)");
print("  - Node 1 (localhost:27018): Setting Priority = 5 (Target High Priority Secondary)");
print("  - Node 2 (localhost:27019): Setting Priority = 2 (Lower Priority Secondary)");

cfg.members[0].priority = 1;
cfg.members[1].priority = 5;
cfg.members[2].priority = 2;

// Apply reconfiguration
print("\nApplying rs.reconfig(cfg)...");
try {
    var reconfigRes = rs.reconfig(cfg);
    printjson(reconfigRes);
} catch (e) {
    print("Reconfig status: " + e.message);
}

// Step 3: State the Hypothesis and Prediction
print("\n================================================================================");
print("  THEORETICAL PREDICTION BEFORE STEPDOWN");
print("================================================================================");
print("Current Primary: Node 0 (localhost:27017)");
print("Eligible Secondaries:");
print("  * Node 1 (localhost:27018) -> Priority: 5");
print("  * Node 2 (localhost:27019) -> Priority: 2");
print("");
print("PREDICTION: When Node 0 steps down, MongoDB's Raft-based consensus protocol");
print("requires candidates to prioritize the highest configured priority value");
print("(Priority 5 > Priority 2). Node 1 will call an election immediately, receive");
print("votes from Node 2 and Node 0, and MUST BE ELECTED NEW PRIMARY.");
print("================================================================================\n");

// Step 4: Force StepDown on current primary
print("[STEP 3] Executing rs.stepDown(60) on Node 0...");
try {
    rs.stepDown(60);
} catch (err) {
    print("Caught expected disconnect exception: " + err.message);
}

// Step 5: Wait for election to resolve
print("\n[STEP 4] Election in progress... Waiting for heartbeats and votes (10 seconds)...");
sleep(10000);

// Step 6: Verify Outcome against Prediction
print("\n[STEP 5] Verifying Elected Primary (rs.status()):");
try {
    var status = rs.status();
    var electedPrimary = "";
    print("--------------------------------------------------------------------------------");
    printf("%-5s %-25s %-12s %-15s %-15s\n", "ID", "HOST", "PRIORITY", "STATE", "OUTCOME");
    print("--------------------------------------------------------------------------------");
    status.members.forEach(function(m) {
        var prio = (m._id === 0) ? 1 : (m._id === 1 ? 5 : 2);
        var outcome = "";
        if (m.stateStr === "PRIMARY") {
            electedPrimary = m.name;
            outcome = "<-- WON ELECTION!";
        } else {
            outcome = "Secondary";
        }
        printf("%-5d %-25s %-12d %-15s %-15s\n", m._id, m.name, prio, m.stateStr, outcome);
    });
    print("--------------------------------------------------------------------------------");
    print("\nElected PRIMARY: " + electedPrimary);
    if (electedPrimary.indexOf("27018") !== -1) {
        print("[VERIFIED] PREDICTION CONFIRMED TRUE: Node 1 (priority: 5) won election over Node 2 (priority: 2)!");
    } else {
        print("Result: " + electedPrimary);
    }
} catch (e2) {
    print("Status error: " + e2.message);
}
print("\n[SUCCESS] Activity 8.2 Try It Yourself Complete.\n");
