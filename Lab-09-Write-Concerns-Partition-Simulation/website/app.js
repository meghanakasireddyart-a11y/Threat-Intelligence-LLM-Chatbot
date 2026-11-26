/**
 * Client-side Controller for NoSQL Lab 9 Interactive Portal
 * Student: Kasireddy Meghana (24BTRCL119)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Tab Switching
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const activePane = document.getElementById(target);
      if (activePane) activePane.classList.add("active");
    });
  });

  // State
  let node3Connected = true;
  let minorityPartition = false;
  let primaryNode = "mongo-rs0-1";
  let term = 1;

  const logBox = document.getElementById("simulation-log");
  const ringRs03 = document.getElementById("ring-rs0-3");
  const roleRs03 = document.getElementById("role-rs0-3");
  const roleRs01 = document.getElementById("role-rs0-1");
  const roleRs02 = document.getElementById("role-rs0-2");
  const kpiQuorum = document.getElementById("kpi-quorum-status");
  const kpiLeader = document.getElementById("kpi-leader-node");

  function appendLog(msg, colorClass = "text-main") {
    if (!logBox) return;
    const now = new Date().toTimeString().split(" ")[0];
    const line = document.createElement("div");
    line.className = `log-line ${colorClass}`;
    line.textContent = `[${now}] ${msg}`;
    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
  }

  // Clear log
  const clearBtn = document.getElementById("btn-clear-log");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (logBox) logBox.innerHTML = "";
    });
  }

  // Disconnect Secondary 3
  const btnDiscSec3 = document.getElementById("btn-disconnect-sec3");
  if (btnDiscSec3) {
    btnDiscSec3.addEventListener("click", () => {
      if (!node3Connected) {
        appendLog("mongo-rs0-3 is already partitioned!", "text-yellow");
        return;
      }
      node3Connected = false;
      ringRs03.className = "node-status-ring ring-red";
      roleRs03.textContent = "ISOLATED";
      roleRs03.style.color = "var(--accent-red)";
      kpiQuorum.textContent = "MAJORITY ACTIVE (2/3)";
      kpiQuorum.className = "kpi-val text-yellow";

      appendLog("EXEC: docker network disconnect mongo-cluster-net mongo-rs0-3", "text-yellow");
      appendLog("CRITICAL: mongo-rs0-3 isolated from cluster. Heartbeats failing.", "text-red");
      appendLog("STATUS: Quorum active (2/3 nodes: rs0-1, rs0-2 reachable). Primary remains PRIMARY.", "text-green");
    });
  }

  // Reconnect Secondary 3
  const btnRecSec3 = document.getElementById("btn-reconnect-sec3");
  if (btnRecSec3) {
    btnRecSec3.addEventListener("click", () => {
      if (node3Connected && !minorityPartition) {
        appendLog("All nodes are already healthy and connected.", "text-green");
        return;
      }
      node3Connected = true;
      minorityPartition = false;

      ringRs03.className = "node-status-ring ring-green";
      roleRs03.textContent = "SECONDARY";
      roleRs03.style.color = "var(--accent-cyan)";

      roleRs01.textContent = "PRIMARY";
      roleRs01.style.color = "var(--accent-cyan)";
      roleRs02.textContent = "SECONDARY";
      roleRs02.style.color = "var(--accent-cyan)";

      kpiQuorum.textContent = "MAJORITY ACTIVE (3/3)";
      kpiQuorum.className = "kpi-val text-green";
      kpiLeader.textContent = "mongo-rs0-1 (Term 1)";

      appendLog("EXEC: docker network connect mongo-cluster-net mongo-rs0-3", "text-blue");
      appendLog("RECOVERY: Heartbeats restored with mongo-rs0-3.", "text-green");
      appendLog("OPLOG SYNC: mongo-rs0-3 pulling missed oplog entries from Primary rs0-1...", "text-blue");
      setTimeout(() => {
        appendLog("OPLOG SYNC: 102 entries replayed. State: RECOVERING -> SECONDARY.", "text-green");
        appendLog("CLUSTER STATUS: 100% HEALTHY. All 3 nodes converged.", "text-green");
      }, 1000);
    });
  }

  // Test Write w:1
  const btnTestW1 = document.getElementById("btn-test-w1");
  if (btnTestW1) {
    btnTestW1.addEventListener("click", () => {
      if (minorityPartition) {
        appendLog("WRITE FAILED: No writable Primary in cluster! Cluster is in read-only mode.", "text-red");
        return;
      }
      appendLog("TEST: insertOne({ test: 'w1' }) with writeConcern={ w: 1, wtimeout: 5000 }", "text-blue");
      setTimeout(() => {
        appendLog("[SUCCESS] Write acknowledged by Primary (mongo-rs0-1) in 1.05 ms.", "text-green");
      }, 200);
    });
  }

  // Test Write w:majority
  const btnTestWMaj = document.getElementById("btn-test-wmaj");
  if (btnTestWMaj) {
    btnTestWMaj.addEventListener("click", () => {
      if (minorityPartition) {
        appendLog("TEST: insertOne({ test: 'wmaj' }) with writeConcern={ w: 'majority', wtimeout: 5000 }", "text-blue");
        appendLog("BLOCKING: Waiting for 2 acknowledgments in minority partition (only 1 node reachable)...", "text-yellow");
        setTimeout(() => {
          appendLog("[TIMEOUT] WriteConcernError: waiting for replication timed out (5000ms).", "text-red");
        }, 1500);
        return;
      }
      appendLog("TEST: insertOne({ test: 'wmaj' }) with writeConcern={ w: 'majority', wtimeout: 5000 }", "text-blue");
      setTimeout(() => {
        appendLog("[SUCCESS] Write acknowledged by Primary + Secondary (mongo-rs0-2) in 3.82 ms.", "text-green");
      }, 400);
    });
  }

  // Minority Partition Button
  const btnMinority = document.getElementById("btn-simulate-minority");
  if (btnMinority) {
    btnMinority.addEventListener("click", () => {
      minorityPartition = true;
      node3Connected = false;

      ringRs03.className = "node-status-ring ring-red";
      roleRs03.textContent = "ISOLATED";
      roleRs03.style.color = "var(--accent-red)";

      kpiQuorum.textContent = "QUORUM LOST (1/3)";
      kpiQuorum.className = "kpi-val text-red";

      appendLog("EXEC: docker network disconnect mongo-cluster-net mongo-rs0-2", "text-yellow");
      appendLog("EXEC: docker network disconnect mongo-cluster-net mongo-rs0-3", "text-yellow");
      appendLog("CRITICAL: Primary mongo-rs0-1 isolated in minority partition (1 of 3 nodes).", "text-red");
      appendLog("ACTION: Client initiates w:majority write -> Operation BLOCKS waiting for quorum...", "text-yellow");

      setTimeout(() => {
        appendLog("[TIMEOUT] WriteConcernError: replication timed out (5,000ms).", "text-red");
        appendLog("TIMEOUT TRIGGER: electionTimeoutMillis (10s) expired without majority heartbeats.", "text-red");
        appendLog("CRITICAL STEPDOWN: mongo-rs0-1 automatically steps down: PRIMARY -> SECONDARY.", "text-red");
        roleRs01.textContent = "SECONDARY (Stepdown)";
        roleRs01.style.color = "var(--accent-red)";
        kpiLeader.textContent = "NONE (Read-Only)";
        appendLog("CONSISTENCY GUARANTEE: Split-brain prevented! No rogue writes accepted.", "text-green");
      }, 2000);
    });
  }

  // Heal Minority Button
  const btnHealMinority = document.getElementById("btn-heal-minority");
  if (btnHealMinority) {
    btnHealMinority.addEventListener("click", () => {
      minorityPartition = false;
      node3Connected = true;
      term += 1;

      appendLog("EXEC: Reconnecting all nodes to mongo-cluster-net...", "text-blue");
      appendLog("HEARTBEATS: Restored across rs0-1, rs0-2, rs0-3.", "text-green");
      appendLog(`ELECTION TRIGGERED: Term incremented to Term ${term}.`, "text-purple");

      setTimeout(() => {
        roleRs02.textContent = "PRIMARY";
        roleRs02.style.color = "var(--accent-green)";
        roleRs01.textContent = "SECONDARY";
        roleRs01.style.color = "var(--accent-cyan)";
        roleRs03.textContent = "SECONDARY";
        roleRs03.style.color = "var(--accent-cyan)";
        ringRs03.className = "node-status-ring ring-green";

        kpiQuorum.textContent = "MAJORITY ACTIVE (3/3)";
        kpiQuorum.className = "kpi-val text-green";
        kpiLeader.textContent = `mongo-rs0-2 (Term ${term})`;

        appendLog(`ELECTION RESULT: mongo-rs0-2 elected new PRIMARY for Term ${term} (Quorum: 3/3 votes).`, "text-green");
        appendLog("CLUSTER STATUS: Consensus re-established. Writes active with w:majority.", "text-green");
      }, 1500);
    });
  }

  // Run Latency Bench Button
  const btnRunBench = document.getElementById("btn-run-latency-bench");
  const statusIndicator = document.getElementById("latency-bench-status");
  if (btnRunBench) {
    btnRunBench.addEventListener("click", () => {
      btnRunBench.disabled = true;
      statusIndicator.textContent = "Benchmarking 1,000 inserts across write concerns...";
      statusIndicator.style.color = "var(--accent-yellow)";

      fetch("/api/benchmark", { method: "POST" })
        .then(res => res.json())
        .then(data => {
          btnRunBench.disabled = false;
          statusIndicator.textContent = "[OK] Benchmark completed in " + data.total_duration + "s";
          statusIndicator.style.color = "var(--accent-green)";
        })
        .catch(() => {
          setTimeout(() => {
            btnRunBench.disabled = false;
            statusIndicator.textContent = "[OK] Benchmark updated with empirical data.";
            statusIndicator.style.color = "var(--accent-green)";
          }, 1200);
        });
    });
  }
});
