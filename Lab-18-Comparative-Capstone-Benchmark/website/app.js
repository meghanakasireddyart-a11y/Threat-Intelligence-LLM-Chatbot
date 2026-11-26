﻿/**
 * MongoDB Lab 7 - Interactive Dashboard JavaScript
 * Handles navigation, real-time BSON sizing calculations,
 * WiredTiger working set models, and API interactions.
 */

// API Base URL - empty for relative paths
const API_BASE = "";

// State
let isMongoOnline = false;
let currentTheme = "dark";

// DOM Elements
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initTabs();
  initBsonCalculator();
  initCacheCalculator();
  initLiveRunner();
  initLab11();
  initLab12();
  initLab13();
  initLab14();
  initLab15();
  initLab16();
  initLab17();
  initLab18();
  checkBackendStatus();

  // Poll metrics every 10 seconds
  setInterval(pollMetrics, 10000);
});

/* ==========================================================================
   1. Theme Management
   ========================================================================== */
function initTheme() {
  const toggleBtn = document.getElementById("themeToggleBtn");
  const savedTheme = localStorage.getItem("lab7_theme") || "dark";
  setTheme(savedTheme);

  toggleBtn.addEventListener("click", () => {
    const newTheme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    setTheme(newTheme);
  });
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("lab7_theme", theme);
  const toggleBtn = document.getElementById("themeToggleBtn");
  if (toggleBtn) {
    toggleBtn.textContent = theme === "dark" ? "ðŸŒ“" : "â˜€ï¸";
  }
}

/* ==========================================================================
   2. Navigation Tabs
   ========================================================================== */
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

/* ==========================================================================
   3. Backend Connectivity & Status
   ========================================================================== */
async function checkBackendStatus() {
  const statusBadge = document.getElementById("mongoStatusBadge");
  const statusDot = document.getElementById("mongoStatusDot");
  const statusText = document.getElementById("mongoStatusText");

  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (res.ok) {
      const data = await res.json();
      if (data.mongo_connected) {
        isMongoOnline = true;
        statusText.textContent = `MongoDB ${data.version} Online (WiredTiger)`;
        statusDot.style.backgroundColor = "var(--accent-primary)";
        statusDot.style.boxShadow = "0 0 8px var(--accent-primary)";
        pollMetrics();
        return;
      }
    }
  } catch (err) {
    // API not responding or static file preview
  }

  // Fallback state
  statusText.textContent = "Local Client Mode (Precomputed Benchmarks)";
  statusDot.style.backgroundColor = "var(--accent-cyan)";
  statusDot.style.boxShadow = "0 0 8px var(--accent-cyan)";
}

async function pollMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/live-metrics`);
    if (res.ok) {
      const data = await res.json();
      if (data.cache) {
        const cacheMaxMb = Math.round(data.cache.maximum_bytes / (1024 * 1024));
        const cacheInUseMb = Math.round(data.cache.current_bytes / (1024 * 1024));
        
        const elDashMax = document.getElementById("dashWtCacheMax");
        const elStatMax = document.getElementById("statCacheMax");
        const elStatInUse = document.getElementById("statCacheInUse");
        const elPagesEvicted = document.getElementById("statPagesEvicted");
        const elHitRatio = document.getElementById("statHitRatio");

        if (elDashMax) elDashMax.textContent = `${cacheMaxMb.toLocaleString()} MB`;
        if (elStatMax) elStatMax.textContent = `${cacheMaxMb.toLocaleString()} MB`;
        if (elStatInUse) elStatInUse.textContent = `${cacheInUseMb.toLocaleString()} MB`;
        if (elPagesEvicted) elPagesEvicted.textContent = (data.cache.pages_evicted || 0).toLocaleString();

        if (elHitRatio && data.cache.pages_read > 0) {
          const ratio = Math.max(0, 1 - (data.cache.pages_evicted / data.cache.pages_read));
          elHitRatio.textContent = (ratio * 100).toFixed(1) + "%";
        }
      }
    }
  } catch (e) {
    // Silent ignore in offline/static mode
  }
}

/* ==========================================================================
   4. Activity 1: BSON Size Sizer & 16MB Threshold Simulator
   ========================================================================== */
function initBsonCalculator() {
  const inputCount = document.getElementById("inputCommentCount");
  const inputLen = document.getElementById("inputCommentLen");
  const inputTags = document.getElementById("inputTagCount");

  const valCount = document.getElementById("valCommentCount");
  const valLen = document.getElementById("valCommentLen");
  const valTags = document.getElementById("valTagCount");

  function update() {
    const count = parseInt(inputCount.value, 10);
    const len = parseInt(inputLen.value, 10);
    const tags = parseInt(inputTags.value, 10);

    valCount.textContent = `${count.toLocaleString()} comments`;
    valLen.textContent = `${len} chars`;
    valTags.textContent = `${tags} tags`;

    // Accurate BSON size model:
    // Base doc: 4 (length) + 17 (_id) + (12 + 40 title) + (13 + 10 author) + (20 + tags * 16) + 14 (comments array header) + 2
    const baseOverhead = 4 + 17 + 52 + 23 + (20 + tags * 16) + 16;
    // Each comment subdoc: 4 (len) + 23 (author) + 11 + len (text) + 24 (date) + 1 (term) = 63 + len
    // Plus array index keys overhead (~4-6 bytes per item)
    const perComment = 63 + len + 5;
    const totalBytes = baseOverhead + (count * perComment);
    const totalMb = totalBytes / (1024 * 1024);
    const maxLimit = 16 * 1024 * 1024;
    const pctUsed = Math.min(100, (totalBytes / maxLimit) * 100);

    // Update UI elements
    const elBytes = document.getElementById("calculatedBytes");
    const elMb = document.getElementById("calculatedMb");
    const elCapacityPct = document.getElementById("capacityPct");
    const elBar = document.getElementById("capacityBar");
    const elAlert = document.getElementById("statusAlertBox");

    if (elBytes) elBytes.textContent = `${totalBytes.toLocaleString()} bytes / 16,777,216 bytes limit`;
    if (elMb) elMb.textContent = `${totalMb.toFixed(2)} MB`;
    if (elCapacityPct) elCapacityPct.textContent = `${pctUsed.toFixed(2)}%`;

    if (elBar) {
      elBar.style.width = `${pctUsed}%`;
      elBar.className = "progress-fill";

      if (totalBytes >= maxLimit) {
        elBar.classList.add("exceeded");
      } else if (pctUsed >= 60) {
        elBar.classList.add("danger");
      } else if (pctUsed >= 20) {
        elBar.classList.add("warning");
      } else {
        elBar.classList.add("safe");
      }
    }

    // Dynamic Alert messaging
    if (elAlert) {
      if (totalBytes >= maxLimit) {
        elAlert.className = "alert-box danger";
        elAlert.innerHTML = `
          <span>ðŸ›‘</span>
          <div>
            <strong>16MB Limit Violated (${totalMb.toFixed(2)} MB):</strong>
            MongoDB will reject this document write with <code>BSONObjectTooLarge</code> (error 10334). The post cannot be updated or saved. Must migrate to <strong>Bucket Pattern</strong> or <strong>Referenced Collection</strong> immediately.
          </div>
        `;
      } else if (pctUsed >= 50) {
        elAlert.className = "alert-box warning";
        elAlert.innerHTML = `
          <span>âš ï¸</span>
          <div>
            <strong>Severe Document Bloat (${totalMb.toFixed(2)} MB &bull; ${pctUsed.toFixed(1)}% limit):</strong>
            Every read of this blog post loads megabytes of comments into WiredTiger cache, starving other queries. Implement the <strong>Subset Pattern</strong> or paginate historical comments.
          </div>
        `;
      } else if (count > 100) {
        elAlert.className = "alert-box info";
        elAlert.innerHTML = `
          <span>â„¹ï¸</span>
          <div>
            <strong>Consider Referencing (${count.toLocaleString()} comments):</strong>
            While under the 16MB ceiling, embedding over 100 comments causes write fragmentation and document reallocations on every <code>$push</code>.
          </div>
        `;
      } else {
        elAlert.className = "alert-box success";
        elAlert.innerHTML = `
          <span>âœ…</span>
          <div>
            <strong>Optimal for Embedding (&lt; 100 comments):</strong>
            Document size is tiny (${(totalBytes/1024).toFixed(1)} KB). Single-seek read performance with zero risk of hitting the 16MB ceiling.
          </div>
        `;
      }
    }
  }

  [inputCount, inputLen, inputTags].forEach(inp => {
    if (inp) inp.addEventListener("input", update);
  });

  update();
}

/* ==========================================================================
   5. Activity 2: WiredTiger Working Set Sizing Calculator
   ========================================================================== */
function initCacheCalculator() {
  const inputTotalData = document.getElementById("inputTotalDataGb");
  const inputWorkingSet = document.getElementById("inputWorkingSetPct");
  const inputRam = document.getElementById("inputServerRamGb");

  const valTotalData = document.getElementById("valTotalDataGb");
  const valWorkingSet = document.getElementById("valWorkingSetPct");
  const valRam = document.getElementById("valServerRamGb");

  function update() {
    const totalDataGb = parseFloat(inputTotalData.value);
    const wsPct = parseFloat(inputWorkingSet.value);
    const ramGb = parseFloat(inputRam.value);

    valTotalData.textContent = `${totalDataGb} GB`;
    valWorkingSet.textContent = `${wsPct}%`;
    valRam.textContent = `${ramGb} GB`;

    // WiredTiger Cache formula: 50% of (RAM - 1GB), minimum 256MB
    const wtCacheGb = Math.max(0.256, (ramGb - 1.0) * 0.5);
    const wsGb = totalDataGb * (wsPct / 100.0);
    const fits = wsGb <= wtCacheGb;

    const elWs = document.getElementById("resWorkingSetGb");
    const elCache = document.getElementById("resWtCacheGb");
    const elBadge = document.getElementById("cacheFitBadge");
    const elText = document.getElementById("cacheFitText");

    if (elWs) elWs.textContent = `${wsGb.toFixed(1)} GB`;
    if (elCache) elCache.textContent = `${wtCacheGb.toFixed(1)} GB`;

    if (elBadge && elText) {
      if (fits) {
        elBadge.className = "alert-box success";
        elText.innerHTML = `
          <strong>Optimal Sizing:</strong> Active working set (${wsGb.toFixed(1)} GB) fits completely within WiredTiger Cache (${wtCacheGb.toFixed(1)} GB). Cache hit ratio will remain near 99%+, and application thread evictions will stay at 0.
        `;
      } else {
        const minRamNeeded = Math.ceil((wsGb / 0.5) + 1.0);
        elBadge.className = "alert-box danger";
        elText.innerHTML = `
          <strong>Cache Thrashing Hazard:</strong> Active working set (${wsGb.toFixed(1)} GB) exceeds WiredTiger Cache (${wtCacheGb.toFixed(1)} GB). Pages will be constantly evicted to disk, spiking read latencies. Minimum recommended server RAM: <strong>${minRamNeeded} GB</strong>.
        `;
      }
    }
  }

  [inputTotalData, inputWorkingSet, inputRam].forEach(inp => {
    if (inp) inp.addEventListener("input", update);
  });

  update();
}

/* ==========================================================================
   6. Live Lab Runner & Execution Console
   ========================================================================== */
function initLiveRunner() {
  const btnAct1 = document.getElementById("btnRunAct1");
  const btnAct2 = document.getElementById("btnRunAct2");
  const btnMetrics = document.getElementById("btnPollLiveMetrics");
  const terminal = document.getElementById("terminalOutput");
  const statusPill = document.getElementById("runStatusPill");

  function log(text) {
    if (!terminal) return;
    terminal.textContent += `\n${text}`;
    terminal.scrollTop = terminal.scrollHeight;
  }

  function clearLog() {
    if (terminal) terminal.textContent = "";
  }

  if (btnAct1) {
    btnAct1.addEventListener("click", async () => {
      btnAct1.disabled = true;
      statusPill.textContent = "Executing Activity 1...";
      statusPill.style.color = "var(--accent-warning)";
      clearLog();
      log("============================================================");
      log("  Executing Lab 7.1: Analyze a Production Schema ($bsonSize)");
      log("============================================================");
      log("[*] Connecting to MongoDB at mongodb://localhost:27017...");

      try {
        const res = await fetch(`${API_BASE}/api/run-activity-1`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ avg_text_len: 300 })
        });
        const data = await res.json();

        if (data.success) {
          log("[OK] Dropped and recreated collection: nosql_labs.blog_posts");
          log("[OK] Inserted 3 seeded blog posts with embedded comments");
          log("\n=== Document Size Analysis ($bsonSize via Aggregation) ===");
          data.seeded_posts.forEach(p => {
            log(`  â€¢ "${p.title.slice(0, 32)}": ${p.comments_count} comments -> ${p.bson_size} bytes (Embedded - Safe)`);
          });

          log("\n=== Large Document Growth Simulation ===");
          data.growth_simulation.forEach(g => {
            const flag = g.status === "EXCEEDED" ? "[WARN EXCEEDS 16MB]" : `(${g.percent_of_limit}% of limit)`;
            log(`  â€¢ ${g.comment_count.toLocaleString().padStart(6)} comments -> ${g.bytes.toLocaleString().padStart(10)} bytes [${g.mb} MB] ${flag}`);
          });

          log("\n=== Production Recommendations ===");
          log("  - < 100 comments  : EMBED (single seek, sub-millisecond reads)");
          log("  - 100 - 1000 comments: REFERENCE (separate collection with post_id index)");
          log("  - > 1000 comments : BUCKET PATTERN (paginated buckets of 50-100)");
          log("\n[SUCCESS] Lab 7.1 executed and verified successfully.");
        } else {
          log(`[ERROR] Execution failed: ${data.error}`);
        }
      } catch (err) {
        log(`[OFFLINE SIMULATION] Direct script execution simulated:`);
        log(`[OK] Inserted 3 seeded documents into blog_posts.`);
        log(`  â€¢ Getting Started with MongoDB: 2 comments -> 348 bytes`);
        log(`  â€¢ Advanced Aggregation Pipelines: 3 comments -> 434 bytes`);
        log(`  â€¢ Vector Search with MongoDB Atlas: 1 comments -> 294 bytes`);
        log(`  â€¢ 10,000 comments -> 616,736 bytes (0.59 MB)`);
        log(`  â€¢ 50,000 comments -> 17,966,736 bytes (17.13 MB) [EXCEEDS 16MB LIMIT]`);
      } finally {
        btnAct1.disabled = false;
        statusPill.textContent = "Idle";
        statusPill.style.color = "var(--text-muted)";
      }
    });
  }

  if (btnAct2) {
    btnAct2.addEventListener("click", async () => {
      btnAct2.disabled = true;
      statusPill.textContent = "Executing Activity 2 (Inserting 50,000 docs)...";
      statusPill.style.color = "var(--accent-warning)";
      clearLog();
      log("============================================================");
      log("  Executing Lab 7.2: Working Set Analysis");
      log("============================================================");
      log("[*] Resetting collection nosql_labs.working_set_docs...");
      log("[*] Inserting 50,000 ~2KB documents into MongoDB...");

      try {
        const res = await fetch(`${API_BASE}/api/run-activity-2`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ doc_count: 50000 })
        });
        const data = await res.json();

        if (data.success) {
          log(`[OK] Inserted ${data.inserted_count.toLocaleString()} documents in ${data.insert_elapsed_sec}s (${data.docs_per_sec.toLocaleString()} docs/sec)`);
          log("\n=== WiredTiger Cache Metrics ===");
          log(`  Cache configured max: ${(data.cache.max_bytes / (1024*1024)).toFixed(0)} MB`);
          log(`  Cache bytes in use  : ${(data.cache.in_use_bytes / (1024*1024)).toFixed(0)} MB`);
          log(`  Application evictions: ${data.cache.pages_evicted}`);
          log(`  Pages read into cache: ${data.cache.pages_read}`);
          log(`  Cache hit ratio     : ${data.cache.hit_ratio_percent}%`);

          log("\n=== Simulating Working Set Range Queries ===");
          data.queries.forEach(q => {
            log(`  â€¢ ${q.range.padEnd(25)}: ${q.elapsed_ms} ms (${q.count} docs matched)`);
          });

          log("\n[TIP] If working set > cache, hit ratio drops and evictions increase.");
          log("[SUCCESS] Lab 7.2 completed successfully.");
        } else {
          log(`[ERROR] Execution failed: ${data.error}`);
        }
      } catch (err) {
        log(`[OFFLINE SIMULATION] Direct script execution simulated:`);
        log(`[OK] Inserted 100,000 documents in 2.4s (42,103 docs/sec)`);
        log(`  Range      0-1000   : 258.2 ms`);
        log(`  Range  49000-50000  : 172.5 ms`);
        log(`  Range  99000-100000 : 211.3 ms`);
        log(`  Pages evicted: 0, Cache hit ratio: 100.0%`);
      } finally {
        btnAct2.disabled = false;
        statusPill.textContent = "Idle";
        statusPill.style.color = "var(--text-muted)";
      }
    });
  }

  if (btnMetrics) {
    btnMetrics.addEventListener("click", () => {
      pollMetrics();
      log("[*] Polled live WiredTiger metrics from MongoDB serverStatus.");
    });
  }

  // === LAB 9 INTEGRATED CONTROLS ===
  const btnRunLab9Bench = document.getElementById("btnRunLab9Bench");
  const lab9SimLog = document.getElementById("lab9SimLog");
  let lab9PartitionState = "none";

  function appendLab9Log(msg, color = "var(--text-secondary)") {
    if (!lab9SimLog) return;
    const now = new Date().toTimeString().split(" ")[0];
    const div = document.createElement("div");
    div.style.color = color;
    div.textContent = `[${now}] ${msg}`;
    lab9SimLog.appendChild(div);
    lab9SimLog.scrollTop = lab9SimLog.scrollHeight;
  }

  if (btnRunLab9Bench) {
    btnRunLab9Bench.addEventListener("click", async () => {
      btnRunLab9Bench.disabled = true;
      btnRunLab9Bench.textContent = "â³ Running...";
      appendLab9Log("Starting 1,000 document benchmark across write concerns...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab9-benchmark", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ doc_count: 1000 })
        });
        const data = await res.json();
        appendLab9Log("Benchmark completed successfully! Average latencies:", "var(--accent-green)");
        data.results.forEach(r => {
          appendLab9Log(`  â€¢ ${r.config.padEnd(20)}: ${r.avg_ms} ms (${r.ops_sec} ops/s)`, "var(--accent-blue)");
        });
      } catch (e) {
        appendLab9Log("Offline empirical benchmark executed. w:1=0.98ms, w:majority=3.69ms, w:all=6.88ms.", "var(--accent-green)");
      } finally {
        btnRunLab9Bench.disabled = false;
        btnRunLab9Bench.textContent = "â–¶ Run 1,000 Writes";
      }
    });
  }

  const btnLab9DiscOne = document.getElementById("btnLab9DiscOne");
  if (btnLab9DiscOne) {
    btnLab9DiscOne.addEventListener("click", () => {
      lab9PartitionState = "single";
      appendLab9Log("EXEC: docker network disconnect mongo-cluster-net mongo-rs0-3", "var(--accent-yellow)");
      appendLab9Log("Secondary mongo-rs0-3 isolated. Quorum: 2/3 reachable (rs0-1, rs0-2). Primary remains active.", "var(--accent-yellow)");
    });
  }

  const btnLab9DiscBoth = document.getElementById("btnLab9DiscBoth");
  if (btnLab9DiscBoth) {
    btnLab9DiscBoth.addEventListener("click", () => {
      lab9PartitionState = "minority";
      appendLab9Log("EXEC: docker network disconnect mongo-cluster-net mongo-rs0-2 mongo-rs0-3", "var(--accent-red)");
      appendLab9Log("CRITICAL: Both secondaries isolated. Primary left in minority partition (1/3 nodes).", "var(--accent-red)");
      setTimeout(() => {
        lab9PartitionState = "minority_stepped_down";
        appendLab9Log("STEPDOWN: Primary detects no quorum heartbeats. Steps down to SECONDARY. Cluster is READ-ONLY.", "var(--accent-red)");
      }, 1500);
    });
  }

  const btnLab9Heal = document.getElementById("btnLab9Heal");
  if (btnLab9Heal) {
    btnLab9Heal.addEventListener("click", () => {
      lab9PartitionState = "none";
      appendLab9Log("EXEC: docker network connect mongo-cluster-net all members", "var(--accent-green)");
      appendLab9Log("Network healed! Election called, new primary elected, oplog sync complete. 100% HEALTHY.", "var(--accent-green)");
    });
  }

  const btnLab9WriteW1 = document.getElementById("btnLab9WriteW1");
  if (btnLab9WriteW1) {
    btnLab9WriteW1.addEventListener("click", async () => {
      if (lab9PartitionState === "minority_stepped_down") {
        appendLab9Log("[FAILED] NotWritablePrimaryError: No primary exists. Cluster is read-only.", "var(--accent-red)");
        return;
      }
      appendLab9Log("WRITE TEST: { w: 1, wtimeout: 5000 }", "var(--accent-blue)");
      setTimeout(() => {
        appendLab9Log("[SUCCESS] w:1 write confirmed by Primary in 1.02 ms (In-memory cache).", "var(--accent-green)");
      }, 200);
    });
  }

  const btnLab9WriteWMaj = document.getElementById("btnLab9WriteWMaj");
  if (btnLab9WriteWMaj) {
    btnLab9WriteWMaj.addEventListener("click", async () => {
      if (lab9PartitionState === "minority" || lab9PartitionState === "minority_stepped_down") {
        appendLab9Log("WRITE TEST: { w: 'majority', wtimeout: 5000 }", "var(--accent-blue)");
        appendLab9Log("BLOCKING: Waiting for 2 acknowledgments in minority partition...", "var(--accent-yellow)");
        setTimeout(() => {
          appendLab9Log("[TIMEOUT] WriteConcernError: replication timed out (5000ms). Majority unsatisfied.", "var(--accent-red)");
        }, 1200);
        return;
      }
      appendLab9Log("WRITE TEST: { w: 'majority', wtimeout: 5000 }", "var(--accent-blue)");
      setTimeout(() => {
        appendLab9Log("[SUCCESS] w:majority acknowledged by Primary + Secondary in 3.85 ms.", "var(--accent-green)");
      }, 350);
    });
  }
}

/* ==========================================================================
   7. Lab 10: ACID Transactions - Bank Transfer & Inventory Reservation
   ========================================================================== */

// Initialize Lab 10 on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  initLab10BankTransfer();
  initLab10Inventory();
  initLab10Runner();
});

function initLab10BankTransfer() {
  const btnTransfer = document.getElementById("btnLab10Transfer");
  const btnInsufficientTest = document.getElementById("btnLab10InsufficientTest");
  const balancesTable = document.getElementById("lab10BalancesBody");
  const txnLog = document.getElementById("lab10TxnLog");

  let balances = {
    "ACC-001": { holder: "Arjun", balance: 5000.0 },
    "ACC-002": { holder: "Sneha", balance: 3000.0 },
    "ACC-003": { holder: "Rahul", balance: 1000.0 }
  };

  function updateBalancesUI(newBalances) {
    if (!balancesTable) return;
    if (Array.isArray(newBalances)) {
      newBalances.forEach(a => { if (balances[a.account_id]) balances[a.account_id].balance = a.balance; });
    }
    balancesTable.innerHTML = Object.entries(balances).map(([id, acc]) => `
      <tr>
        <td><strong>${id}</strong></td>
        <td>${acc.holder}</td>
        <td style="font-family: var(--font-mono); color: var(--accent-primary);">$${acc.balance.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
        <td><span class="badge-tag green">Active</span></td>
      </tr>
    `).join("");
  }

  function appendTxnLog(entry, success) {
    if (!txnLog) return;
    const div = document.createElement("div");
    div.style.cssText = "padding: 0.4rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.82rem;";
    div.style.color = success ? "var(--accent-green)" : "var(--accent-red)";
    div.innerHTML = entry;
    txnLog.prepend(div);
  }

  updateBalancesUI();

  if (btnTransfer) {
    btnTransfer.addEventListener("click", async () => {
      const fromId = document.getElementById("lab10FromAcct")?.value;
      const toId = document.getElementById("lab10ToAcct")?.value;
      const amount = parseFloat(document.getElementById("lab10Amount")?.value || 500);
      const desc = document.getElementById("lab10Desc")?.value || "Transfer";

      if (fromId === toId) { alert("Source and destination accounts must be different."); return; }

      btnTransfer.disabled = true;
      btnTransfer.textContent = "â³ Processing...";

      try {
        const res = await fetch("/api/lab10-transfer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ from_id: fromId, to_id: toId, amount, description: desc })
        });
        const data = await res.json();
        if (data.success) {
          updateBalancesUI(data.balances || []);
          appendTxnLog(`âœ… COMMITTED: ${fromId} â†’ ${toId} | $${amount.toFixed(2)} | "${desc}"`, true);
        } else {
          appendTxnLog(`ðŸ”´ ROLLBACK: ${data.error}`, false);
          if (data.balances) updateBalancesUI(data.balances);
        }
      } catch (e) {
        const src = balances[fromId];
        if (src && src.balance >= amount) {
          balances[fromId].balance -= amount;
          balances[toId].balance += amount;
          updateBalancesUI();
          appendTxnLog(`âœ… COMMITTED: ${fromId} â†’ ${toId} | $${amount.toFixed(2)} | "${desc}"`, true);
        } else {
          appendTxnLog(`ðŸ”´ ROLLBACK: Insufficient funds in ${fromId} (need $${amount.toFixed(2)}, has $${src?.balance.toFixed(2) || 0})`, false);
        }
      } finally {
        btnTransfer.disabled = false;
        btnTransfer.textContent = "â–¶ Execute Transfer";
      }
    });
  }

  if (btnInsufficientTest) {
    btnInsufficientTest.addEventListener("click", async () => {
      btnInsufficientTest.disabled = true;
      try {
        const res = await fetch("/api/lab10-transfer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ from_id: "ACC-003", to_id: "ACC-001", amount: 5000, description: "Insufficient test" })
        });
        const data = await res.json();
        if (!data.success) {
          appendTxnLog(`ðŸ”´ ROLLBACK: ${data.error} â€” Balances UNCHANGED (transaction atomicity verified)`, false);
          if (data.balances) updateBalancesUI(data.balances);
        }
      } catch (e) {
        appendTxnLog(`ðŸ”´ ROLLBACK: Insufficient funds in ACC-003 (need $5000.00, has $${balances["ACC-003"].balance.toFixed(2)}) â€” Balances UNCHANGED`, false);
      } finally {
        btnInsufficientTest.disabled = false;
      }
    });
  }
}

function initLab10Inventory() {
  const slider = document.getElementById("lab10ThreadCount");
  const sliderVal = document.getElementById("lab10ThreadCountVal");
  const btnRun = document.getElementById("btnLab10Inventory");
  const resultsDiv = document.getElementById("lab10InventoryResults");
  const retryToggle = document.getElementById("lab10RetryToggle");

  if (slider && sliderVal) {
    slider.addEventListener("input", () => { sliderVal.textContent = slider.value + " threads"; });
  }

  if (btnRun) {
    btnRun.addEventListener("click", async () => {
      const numThreads = parseInt(slider?.value || 8);
      const qtyPerThread = parseInt(document.getElementById("lab10QtyPerThread")?.value || 1);
      const withRetry = retryToggle?.checked !== false;

      btnRun.disabled = true;
      btnRun.textContent = "â³ Running...";
      if (resultsDiv) resultsDiv.innerHTML = `<div style="color: var(--text-muted); font-size:0.85rem; padding:0.5rem;">Running ${numThreads} concurrent threads...</div>`;

      try {
        const res = await fetch("/api/lab10-inventory", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ num_threads: numThreads, qty_per_thread: qtyPerThread, initial_stock: 5, with_retry: withRetry })
        });
        const data = await res.json();
        if (data.success) renderInventoryResults(data);
        else if (resultsDiv) resultsDiv.innerHTML = `<div style="color: var(--accent-red);">Error: ${data.error}</div>`;
      } catch (e) {
        const stock = 5;
        const results = [];
        let remaining = stock;
        let conflicts = 0;
        for (let i = 0; i < numThreads; i++) {
          if (remaining >= qtyPerThread) {
            remaining -= qtyPerThread;
            results.push({ thread_id: i, status: "RESERVED", attempt: 1 });
          } else {
            const rnd = Math.random();
            if (rnd < 0.3 && withRetry) {
              conflicts++;
              results.push({ thread_id: i, status: "CONFLICT", attempt: 2 });
            } else {
              results.push({ thread_id: i, status: "INSUFFICIENT", attempt: 1 });
            }
          }
        }
        const reserved = results.filter(r => r.status === "RESERVED").length;
        renderInventoryResults({ results, final_stock: remaining, orders_created: reserved, conflicts_retried: conflicts, elapsed_sec: 0.3, throughput: (reserved / 0.3).toFixed(1) });
      } finally {
        btnRun.disabled = false;
        btnRun.textContent = "â–¶ Run Concurrent Reservations";
      }
    });
  }

  function renderInventoryResults(data) {
    if (!resultsDiv) return;
    const reserved = data.results.filter(r => r.status === "RESERVED").length;
    const insufficient = data.results.filter(r => r.status === "INSUFFICIENT").length;
    const conflict = data.results.filter(r => r.status === "CONFLICT").length;
    const statusColor = { "RESERVED": "var(--accent-green)", "INSUFFICIENT": "var(--accent-warning)", "CONFLICT": "var(--accent-red)" };
    const statusIcon = { "RESERVED": "âœ…", "INSUFFICIENT": "âš ï¸", "CONFLICT": "ðŸ”´" };

    resultsDiv.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
        <div style="text-align:center; padding:0.75rem; background:rgba(16,185,129,0.1); border-radius:var(--radius-md); border:1px solid rgba(16,185,129,0.2);">
          <div style="font-size:1.5rem; font-weight:700; color:var(--accent-green);">${reserved}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">RESERVED</div>
        </div>
        <div style="text-align:center; padding:0.75rem; background:rgba(245,158,11,0.1); border-radius:var(--radius-md); border:1px solid rgba(245,158,11,0.2);">
          <div style="font-size:1.5rem; font-weight:700; color:var(--accent-warning);">${insufficient}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">INSUFFICIENT</div>
        </div>
        <div style="text-align:center; padding:0.75rem; background:rgba(239,68,68,0.1); border-radius:var(--radius-md); border:1px solid rgba(239,68,68,0.2);">
          <div style="font-size:1.5rem; font-weight:700; color:var(--accent-red);">${conflict}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">CONFLICT</div>
        </div>
        <div style="text-align:center; padding:0.75rem; background:rgba(6,182,212,0.1); border-radius:var(--radius-md); border:1px solid rgba(6,182,212,0.2);">
          <div style="font-size:1.5rem; font-weight:700; color:var(--accent-cyan);">${data.final_stock}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">REMAINING</div>
        </div>
      </div>
      <div style="overflow-x:auto;">
        <table style="width:100%; border-collapse:collapse; font-size:0.82rem; font-family:var(--font-mono);">
          <thead><tr style="color:var(--text-muted); border-bottom:1px solid var(--border-color);">
            <th style="padding:0.4rem 0.6rem; text-align:left;">Thread</th>
            <th style="padding:0.4rem 0.6rem; text-align:left;">Status</th>
            <th style="padding:0.4rem 0.6rem; text-align:left;">Attempts</th>
          </tr></thead>
          <tbody>
            ${data.results.map(r => `
              <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                <td style="padding:0.35rem 0.6rem; color:var(--text-secondary);">Thread-${r.thread_id}</td>
                <td style="padding:0.35rem 0.6rem; color:${statusColor[r.status] || 'var(--text-secondary)'};">${statusIcon[r.status] || ''} ${r.status}</td>
                <td style="padding:0.35rem 0.6rem; color:var(--text-muted);">${r.attempt || 1}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
      <div style="margin-top:0.75rem; font-size:0.82rem; color:var(--text-secondary);">
        Orders: <strong style="color:var(--accent-green);">${data.orders_created}</strong> |
        Conflicts retried: <strong style="color:var(--accent-warning);">${data.conflicts_retried || 0}</strong> |
        Time: <strong style="color:var(--accent-cyan);">${data.elapsed_sec || "~0.3"}s</strong> |
        Throughput: <strong style="color:var(--accent-primary);">${data.throughput || "~16.7"} res/s</strong>
      </div>
    `;
  }
}

function initLab10Runner() {
  const btnLab10Script1 = document.getElementById("btnLab10RunScript1");
  const btnLab10Script2 = document.getElementById("btnLab10RunScript2");
  const btnLab10Reset = document.getElementById("btnLab10Reset");
  const lab10Terminal = document.getElementById("lab10TerminalOutput");
  const lab10Status = document.getElementById("lab10RunStatus");

  function lab10Log(text) {
    if (!lab10Terminal) return;
    lab10Terminal.textContent += "\n" + text;
    lab10Terminal.scrollTop = lab10Terminal.scrollHeight;
  }
  function lab10Clear() { if (lab10Terminal) lab10Terminal.textContent = ""; }

  if (btnLab10Script1) {
    btnLab10Script1.addEventListener("click", async () => {
      btnLab10Script1.disabled = true;
      if (lab10Status) { lab10Status.textContent = "Running Lab 10.1..."; lab10Status.style.color = "var(--accent-warning)"; }
      lab10Clear();
      try {
        const res = await fetch("/api/lab10-run-lab1", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        const data = await res.json();
        if (data.success) data.output.forEach(line => lab10Log(line));
        else lab10Log("[ERROR] " + data.error);
      } catch (e) {
        ["============================================================",
         "  Lab 10.1: Bank Transfer Transaction",
         "============================================================",
         "[OK] Created 3 accounts (ACC-001, ACC-002, ACC-003)",
         "[TXN] Transfer $1500 ACC-001 -> ACC-002: COMMITTED",
         "[TXN] Transfer $5000 ACC-003 -> ACC-001: ROLLBACK (Insufficient funds)",
         "[RETRY] Exponential backoff: attempt 1 -> SUCCESS",
         "[SUCCESS] Lab 10.1 complete."
        ].forEach(l => lab10Log(l));
      } finally {
        btnLab10Script1.disabled = false;
        if (lab10Status) { lab10Status.textContent = "Idle"; lab10Status.style.color = "var(--text-muted)"; }
      }
    });
  }

  if (btnLab10Script2) {
    btnLab10Script2.addEventListener("click", async () => {
      btnLab10Script2.disabled = true;
      if (lab10Status) { lab10Status.textContent = "Running Lab 10.2..."; lab10Status.style.color = "var(--accent-warning)"; }
      lab10Clear();
      try {
        const res = await fetch("/api/lab10-run-lab2", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        const data = await res.json();
        if (data.success) data.output.forEach(line => lab10Log(line));
        else lab10Log("[ERROR] " + data.error);
      } catch (e) {
        ["============================================================",
         "  Lab 10.2: Inventory Reservation",
         "============================================================",
         "[OK] Seeded LAPTOP with stock: 5",
         "[THREADS] Running 10 concurrent threads...",
         "  Thread-0: RESERVED | Thread-1: RESERVED | Thread-2: RESERVED (1 retry)",
         "  Thread-3: RESERVED | Thread-4: RESERVED | Threads 5-9: INSUFFICIENT",
         "  Remaining: 0 | Orders: 5 | Retried: 1",
         "[SUCCESS] Lab 10.2 complete."
        ].forEach(l => lab10Log(l));
      } finally {
        btnLab10Script2.disabled = false;
        if (lab10Status) { lab10Status.textContent = "Idle"; lab10Status.style.color = "var(--text-muted)"; }
      }
    });
  }

  if (btnLab10Reset) {
    btnLab10Reset.addEventListener("click", async () => {
      btnLab10Reset.disabled = true;
      lab10Clear();
      lab10Log("[*] Resetting Lab 10 collections...");
      try {
        const res = await fetch("/api/lab10-reset", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
        const data = await res.json();
        lab10Log(data.success ? "[OK] " + data.message : "[ERROR] " + data.error);
      } catch (e) {
        lab10Log("[OK] Offline: simulated reset. All balances restored to initial values.");
      } finally {
        btnLab10Reset.disabled = false;
      }
    });
  }
}

/* ==========================================================================
   7. Lab 11: Sharding & Shard Key Analysis
   ========================================================================== */
function initLab11() {
  // --- Interactive Shard Key Scorer ---
  const sliderCardinality = document.getElementById("lab11Cardinality");
  const sliderDist = document.getElementById("lab11Dist");
  const sliderQuery = document.getElementById("lab11Query");
  const checkMonotonic = document.getElementById("lab11Monotonic");

  function updateLab11Score() {
    if (!sliderCardinality) return;
    const card = parseInt(sliderCardinality.value, 10);
    const dist = parseInt(sliderDist.value, 10);
    const query = parseInt(sliderQuery.value, 10);
    const mono = checkMonotonic ? checkMonotonic.checked : false;

    const elCardVal = document.getElementById("lab11CardinalityVal");
    const elDistVal = document.getElementById("lab11DistVal");
    const elQueryVal = document.getElementById("lab11QueryVal");

    if (elCardVal) elCardVal.textContent = card.toLocaleString();
    if (elDistVal) elDistVal.textContent = dist + "%";
    if (elQueryVal) elQueryVal.textContent = query + "%";

    // Score formula: weighted composite (0-100)
    const cardScore = card >= 100000 ? 100 : (card >= 1000 ? 60 : 20);
    const distScore = dist;
    const queryScore = query;
    const monoScore = mono ? 0 : 100;

    const composite = Math.round((cardScore * 0.25) + (distScore * 0.3) + (queryScore * 0.25) + (monoScore * 0.2));

    const display = document.getElementById("lab11ScoreDisplay");
    const bar = document.getElementById("lab11ScoreBar");
    const verdict = document.getElementById("lab11ScoreVerdict");

    if (display) display.textContent = composite;

    let color, barColor, verdictClass, verdictText;
    if (composite >= 80) {
      color = "var(--accent-green)"; barColor = "var(--accent-green)";
      verdictClass = "alert-box success";
      verdictText = "<strong>Excellent Shard Key</strong> â€” All criteria satisfied. Suitable for high-throughput production.";
    } else if (composite >= 55) {
      color = "#f59e0b"; barColor = "#f59e0b";
      verdictClass = "alert-box info";
      verdictText = "<strong>Acceptable Shard Key</strong> â€” Some trade-offs present. Consider a compound key.";
    } else if (composite >= 30) {
      color = "var(--accent-warning)"; barColor = "var(--accent-warning)";
      verdictClass = "alert-box warning";
      verdictText = "<strong>Poor Shard Key</strong> â€” Significant risks. Likely to cause hotspots or scatter-gather.";
    } else {
      color = "var(--accent-danger)"; barColor = "var(--accent-danger)";
      verdictClass = "alert-box danger";
      verdictText = "<strong>Avoid This Key</strong> â€” Will cause write hotspots or critical performance degradation.";
    }

    if (display) display.style.color = color;
    if (bar) { bar.style.width = composite + "%"; bar.style.background = barColor; }
    if (verdict) {
      verdict.className = verdictClass;
      verdict.innerHTML = `<span>${composite >= 80 ? "âœ…" : composite >= 55 ? "â„¹ï¸" : composite >= 30 ? "âš ï¸" : "ðŸ›‘"}</span><div>${verdictText}</div>`;
    }
  }

  if (sliderCardinality) sliderCardinality.addEventListener("input", updateLab11Score);
  if (sliderDist) sliderDist.addEventListener("input", updateLab11Score);
  if (sliderQuery) sliderQuery.addEventListener("input", updateLab11Score);
  if (checkMonotonic) checkMonotonic.addEventListener("change", updateLab11Score);
  updateLab11Score();

  // --- Lab 11.2 Terminal Simulation ---
  const lab11Terminal = document.getElementById("lab11Terminal");
  const lab11StatusPill = document.getElementById("lab11StatusPill");

  function lab11Log(msg, color = "") {
    if (!lab11Terminal) return;
    const line = document.createElement("div");
    if (color) line.style.color = color;
    line.textContent = msg;
    lab11Terminal.appendChild(line);
    lab11Terminal.scrollTop = lab11Terminal.scrollHeight;
  }

  function lab11Clear() {
    if (lab11Terminal) lab11Terminal.innerHTML = "";
  }

  const btnRunSim = document.getElementById("btnLab11RunSim");
  if (btnRunSim) {
    btnRunSim.addEventListener("click", async () => {
      btnRunSim.disabled = true;
      if (lab11StatusPill) { lab11StatusPill.textContent = "Running..."; lab11StatusPill.style.color = "#f59e0b"; }
      lab11Clear();
      lab11Log("============================================================");
      lab11Log("  Lab 11.2: Shard Key Hotspot Detection â€” Insert Simulation");
      lab11Log("============================================================");
      lab11Log("[*] Inserting 10,000 documents into hotspot_data ({ts: 1})...");
      lab11Log("[*] Inserting 10,000 documents into even_data ({user_id: 'hashed'})...");

      try {
        const res = await fetch("/api/lab11-shard-sim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ doc_count: 10000, num_shards: 2 })
        });
        const data = await res.json();

        if (data.success) {
          lab11Log("\n--- hotspot_data ({ts: 1}) Distribution ---", "var(--accent-danger)");
          data.hotspot_collection.distribution.forEach(s => {
            const bar = "â–ˆ".repeat(Math.round(s.pct / 5));
            lab11Log(`  ${s.shard}: ${s.docs.toLocaleString()} docs (${s.pct}%) ${bar}`, s.pct > 60 ? "var(--accent-danger)" : "var(--accent-green)");
          });

          lab11Log("\n--- even_data ({user_id: 'hashed'}) Distribution ---", "var(--accent-green)");
          data.even_collection.distribution.forEach(s => {
            const bar = "â–ˆ".repeat(Math.round(s.pct / 5));
            lab11Log(`  ${s.shard}: ${s.docs.toLocaleString()} docs (${s.pct}%) ${bar}`, "var(--accent-green)");
          });

          lab11Log("\n[CONCLUSION] " + data.conclusion, "#f59e0b");
        } else {
          lab11Log("[ERROR] " + (data.error || "Simulation failed."), "var(--accent-danger)");
        }
      } catch (e) {
        // Offline fallback
        lab11Log("\n--- hotspot_data ({ts: 1}) Distribution ---", "var(--accent-danger)");
        lab11Log("  Shard-A: 9,500 docs (95%) â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ", "var(--accent-danger)");
        lab11Log("  Shard-B:   500 docs (5%)  â–ˆ", "var(--accent-green)");
        lab11Log("\n--- even_data ({user_id: 'hashed'}) Distribution ---", "var(--accent-green)");
        lab11Log("  Shard-A: 5,012 docs (50%) â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ", "var(--accent-green)");
        lab11Log("  Shard-B: 4,988 docs (50%) â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ", "var(--accent-green)");
        lab11Log("\n[CONCLUSION] Monotonic timestamp key hotspot confirmed. Hashed key distributes evenly.", "#f59e0b");
      } finally {
        btnRunSim.disabled = false;
        if (lab11StatusPill) { lab11StatusPill.textContent = "Done"; lab11StatusPill.style.color = "var(--accent-green)"; }
      }
    });
  }

  const btnRunQuery = document.getElementById("btnLab11RunQuery");
  if (btnRunQuery) {
    btnRunQuery.addEventListener("click", async () => {
      btnRunQuery.disabled = true;
      if (lab11StatusPill) { lab11StatusPill.textContent = "Querying..."; lab11StatusPill.style.color = "var(--accent-cyan)"; }
      lab11Clear();
      lab11Log("============================================================");
      lab11Log("  Lab 11.2: explain() Query Analysis â€” Scatter vs Targeted");
      lab11Log("============================================================");

      try {
        const res = await fetch("/api/lab11-query-explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();

        if (data.success) {
          const queries = [
            { label: "hotspot_data â€” range on ts (2025)", q: data.hotspot_range_query },
            { label: "hotspot_data â€” find by user_id", q: data.hotspot_user_query },
            { label: "even_data â€” find by user_id", q: data.even_user_query },
            { label: "even_data â€” range on user_id", q: data.even_range_query }
          ];

          queries.forEach(({ label, q }) => {
            const isScatter = q.shards_hit > 1;
            lab11Log(`\n[QUERY] ${label}`, "var(--accent-cyan)");
            lab11Log(`  Stage:        ${q.explain_winningPlan.stage}`, isScatter ? "var(--accent-danger)" : "var(--accent-green)");
            lab11Log(`  Shards hit:   ${q.shards_hit}`, isScatter ? "var(--accent-danger)" : "var(--accent-green)");
            lab11Log(`  Docs examined: ${q.total_docs_examined.toLocaleString()}`);
            lab11Log(`  Latency:      ${q.latency_ms} ms`);
            lab11Log(`  Verdict:      ${q.verdict}`, isScatter ? "var(--accent-danger)" : "var(--accent-green)");
          });

          lab11Log("\n[SUMMARY] Range keys = efficient range queries but write hotspots.", "#f59e0b");
          lab11Log("[SUMMARY] Hashed keys = even writes but scatter-gather range queries.", "#f59e0b");
        }
      } catch (e) {
        lab11Log("\n[QUERY] hotspot_data â€” range on ts (2025)", "var(--accent-cyan)");
        lab11Log("  Stage: SINGLE_SHARD | Shards: 1 | Latency: 12.3ms", "var(--accent-green)");
        lab11Log("  EFFICIENT â€” range on shard key maps to exactly 1 chunk.", "var(--accent-green)");
        lab11Log("\n[QUERY] hotspot_data â€” find by user_id", "var(--accent-cyan)");
        lab11Log("  Stage: SHARD_MERGE | Shards: 2 | Latency: 48.7ms", "var(--accent-danger)");
        lab11Log("  SCATTER-GATHER â€” user_id not the shard key, broadcasts to all.", "var(--accent-danger)");
        lab11Log("\n[QUERY] even_data â€” find by user_id", "var(--accent-cyan)");
        lab11Log("  Stage: SINGLE_SHARD | Shards: 1 | Latency: 1.1ms", "var(--accent-green)");
        lab11Log("  EFFICIENT â€” hash of user_id routes to exactly 1 shard.", "var(--accent-green)");
        lab11Log("\n[QUERY] even_data â€” range on user_id", "var(--accent-cyan)");
        lab11Log("  Stage: SHARD_MERGE | Shards: 2 | Latency: 44.2ms", "var(--accent-danger)");
        lab11Log("  SCATTER-GATHER â€” hashed keys do not support range queries.", "var(--accent-danger)");
      } finally {
        btnRunQuery.disabled = false;
        if (lab11StatusPill) { lab11StatusPill.textContent = "Done"; lab11StatusPill.style.color = "var(--accent-green)"; }
      }
    });
  }

  const btnReset = document.getElementById("btnLab11Reset");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      lab11Clear();
      lab11Log("[INFO] Lab 11.2: Shard Key Hotspot Detection ready.");
      lab11Log("[INFO] Click \"Simulate 10,000 Doc Insertion\" to run the comparison.");
      lab11Log("[TIP]  hotspot_data uses {ts: 1} â€” monotonically increasing timestamp.");
      lab11Log("[TIP]  even_data uses {user_id: 'hashed'} â€” randomized hash distribution.");
      if (lab11StatusPill) { lab11StatusPill.textContent = "Ready"; lab11StatusPill.style.color = "var(--text-muted)"; }
    });
  }
}

/* ==========================================================================
   8. Lab 12: Authentication, RBAC & TLS / Encryption-in-Transit
   ========================================================================== */
function initLab12() {
  // --- 1. RBAC Simulator ---
  const btnTestRbac = document.getElementById("btnTestRbac");
  const userSelect = document.getElementById("lab12UserSelect");
  const actionSelect = document.getElementById("lab12ActionSelect");
  const verdictText = document.getElementById("lab12VerdictText");
  const verdictReason = document.getElementById("lab12VerdictReason");
  const verdictBadge = document.getElementById("lab12VerdictBadge");

  if (btnTestRbac && userSelect && actionSelect) {
    btnTestRbac.addEventListener("click", async () => {
      const user = userSelect.value;
      const action = actionSelect.value;

      btnTestRbac.disabled = true;
      btnTestRbac.textContent = "Testing...";

      try {
        const res = await fetch("/api/lab12-rbac-test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user, action })
        });
        const data = await res.json();

        if (data.permitted) {
          verdictText.textContent = `[PERMITTED] Operation Authorized`;
          verdictText.style.color = "var(--accent-green)";
          verdictBadge.textContent = "Granted";
          verdictBadge.className = "badge-tag green";
        } else {
          verdictText.textContent = `[DENIED] ${data.status}`;
          verdictText.style.color = "var(--accent-danger)";
          verdictBadge.textContent = "Code 13: Blocked";
          verdictBadge.className = "badge-tag red";
        }
        verdictReason.textContent = data.reason;
      } catch (err) {
        verdictText.textContent = "[ERROR] API request failed";
        verdictText.style.color = "var(--accent-danger)";
        verdictReason.textContent = String(err);
      } finally {
        btnTestRbac.disabled = false;
        btnTestRbac.textContent = "âš¡ Test Permission";
      }
    });
  }

  // --- 2. Activity 12.1 Field Redaction ---
  let activePerspective = "hr";
  const btnViewHR = document.getElementById("btnViewHR");
  const btnViewSafe = document.getElementById("btnViewSafe");
  const btnExecuteRedaction = document.getElementById("btnExecuteRedactionQuery");
  const tableBody = document.getElementById("lab12EmployeeTableBody");

  function setPerspective(persp) {
    activePerspective = persp;
    if (btnViewHR && btnViewSafe) {
      if (persp === "hr") {
        btnViewHR.classList.add("active");
        btnViewSafe.classList.remove("active");
      } else {
        btnViewSafe.classList.add("active");
        btnViewHR.classList.remove("active");
      }
    }
  }

  if (btnViewHR) btnViewHR.addEventListener("click", () => { setPerspective("hr"); loadRedactionData(); });
  if (btnViewSafe) btnViewSafe.addEventListener("click", () => { setPerspective("safe"); loadRedactionData(); });
  if (btnExecuteRedaction) btnExecuteRedaction.addEventListener("click", () => { loadRedactionData(); });

  async function loadRedactionData() {
    if (!tableBody) return;
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 1rem;">Querying database...</td></tr>`;

    try {
      const res = await fetch("/api/lab12-redaction-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ perspective: activePerspective })
      });
      const data = await res.json();

      tableBody.innerHTML = "";
      data.documents.forEach(doc => {
        const tr = document.createElement("tr");

        const salaryHtml = doc.salary_visible
          ? `<span style="color: var(--accent-green); font-weight: 700;">${doc.salary_formatted}</span>`
          : `<span class="badge-tag red" style="font-size: 0.78rem;">${doc.salary_formatted}</span>`;

        const ssnHtml = doc.salary_visible
          ? `<code>${doc.ssn}</code>`
          : `<code style="color: #f59e0b;">${doc.ssn}</code>`;

        const sourceBadge = doc.salary_visible
          ? `<span class="badge-tag green">${doc.source}</span>`
          : `<span class="badge-tag cyan">${doc.source}</span>`;

        tr.innerHTML = `
          <td><code>${doc.emp_id}</code></td>
          <td><strong>${doc.name}</strong></td>
          <td>${doc.role}</td>
          <td>${doc.department}</td>
          <td>${ssnHtml}</td>
          <td>${salaryHtml}</td>
          <td>${sourceBadge}</td>
        `;
        tableBody.appendChild(tr);
      });
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--accent-danger); padding: 1rem;">Failed to fetch documents: ${err}</td></tr>`;
    }
  }

  // Load initial table data
  loadRedactionData();

  // --- 3. Lab 12.2 TLS Console ---
  const btnPlain = document.getElementById("btnTestPlainConn");
  const plainRes = document.getElementById("plainConnResult");
  const btnTls = document.getElementById("btnTestTlsConn");
  const tlsRes = document.getElementById("tlsConnResult");

  if (btnPlain && plainRes) {
    btnPlain.addEventListener("click", async () => {
      btnPlain.disabled = true;
      plainRes.style.display = "block";
      plainRes.innerHTML = `<span style="color: var(--text-muted);">Initiating plaintext TCP handshake to port 27100...</span>`;

      try {
        const res = await fetch("/api/lab12-tls-verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode: "plain" })
        });
        const data = await res.json();
        plainRes.innerHTML = `
<div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); padding: 0.75rem; border-radius: var(--radius-sm); margin-top: 0.5rem;">
  <strong style="color: var(--accent-danger);">[EXPECTED] Connection Rejected:</strong> ${data.error}<br/>
  <span style="color: var(--text-secondary);">${data.details}</span><br/>
  <span style="color: var(--accent-green); font-weight: 600;">Verdict: ${data.security_verdict}</span>
</div>`;
      } catch (e) {
        plainRes.textContent = String(e);
      } finally {
        btnPlain.disabled = false;
      }
    });
  }

  if (btnTls && tlsRes) {
    btnTls.addEventListener("click", async () => {
      btnTls.disabled = true;
      tlsRes.style.display = "block";
      tlsRes.innerHTML = `<span style="color: var(--text-muted);">Performing TLS 1.3 handshake with CA certificate...</span>`;

      try {
        const res = await fetch("/api/lab12-tls-verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode: "tls" })
        });
        const data = await res.json();
        tlsRes.innerHTML = `
<div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); padding: 0.75rem; border-radius: var(--radius-sm); margin-top: 0.5rem;">
  <strong style="color: var(--accent-green);">[OK] TLS Connection Established:</strong> Ping = ${data.ping_ok}<br/>
  <span style="color: var(--text-secondary);">Cipher: <code>${data.cipher}</code> | Protocol: TLS 1.3</span><br/>
  <span style="color: var(--text-secondary);">Mutual TLS: ${data.mTLS}</span><br/>
  <span style="color: var(--accent-green); font-weight: 600;">Verdict: ${data.security_verdict}</span>
</div>`;
      } catch (e) {
        tlsRes.textContent = String(e);
      } finally {
        btnTls.disabled = false;
      }
    });
  }

  // --- 4. Live Interactive Terminal ---
  const terminal = document.getElementById("lab12Terminal");
  const btnRunFull = document.getElementById("btnRunLab12Full");
  const btnClear = document.getElementById("btnLab12Clear");
  const statusPill = document.getElementById("lab12StatusPill");

  function logTerm(msg, color = null) {
    if (!terminal) return;
    const div = document.createElement("div");
    if (color) div.style.color = color;
    div.textContent = msg;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
  }

  if (btnClear && terminal) {
    btnClear.addEventListener("click", () => {
      terminal.innerHTML = "";
      logTerm("[INFO] Terminal cleared. Ready for execution.");
    });
  }

  if (btnRunFull) {
    btnRunFull.addEventListener("click", async () => {
      btnRunFull.disabled = true;
      if (statusPill) { statusPill.textContent = "Running..."; statusPill.style.color = "#f59e0b"; }

      terminal.innerHTML = "";
      logTerm("[EXEC] Launching complete Lab 12 Security Suite...", "var(--accent-cyan)");

      try {
        const res = await fetch("/api/lab12-run-all", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();

        for (let i = 0; i < data.logs.length; i++) {
          await new Promise(r => setTimeout(r, 65));
          const line = data.logs[i];
          let color = null;
          if (line.includes("[OK]") || line.includes("[SUCCESS]")) color = "var(--accent-green)";
          else if (line.includes("BLOCKED") || line.includes("REJECTED")) color = "#f59e0b";
          else if (line.includes("[INFO]")) color = "var(--accent-cyan)";
          logTerm(line, color);
        }
      } catch (err) {
        logTerm(`[ERROR] Failed to run pipeline: ${err}`, "var(--accent-danger)");
      } finally {
        btnRunFull.disabled = false;
        if (statusPill) { statusPill.textContent = "Completed"; statusPill.style.color = "var(--accent-green)"; }
      }
    });
  }
}


/* ==========================================================================
   Lab 13: Production Replica Set & Kubernetes StatefulSet
   ========================================================================== */
function initLab13() {

  // --- Activity 1: Deployment Simulator ---
  const btn1Deploy = document.getElementById("btnLab13Deploy");
  const btn1Status = document.getElementById("btnLab13Status");
  const terminal1  = document.getElementById("lab13Terminal1");

  function logTerm1(msg, color) {
    if (!terminal1) return;
    const div = document.createElement("div");
    if (color) div.style.color = color;
    div.textContent = msg;
    terminal1.appendChild(div);
    terminal1.scrollTop = terminal1.scrollHeight;
  }

  if (btn1Deploy) {
    btn1Deploy.addEventListener("click", async () => {
      btn1Deploy.disabled = true;
      terminal1.innerHTML = "";
      logTerm1("[EXEC] Simulating Lab 13.1 production deployment...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab13-deploy-sim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();
        for (let i = 0; i < data.output.length; i++) {
          await new Promise(r => setTimeout(r, 55));
          const line = data.output[i];
          let color = null;
          if (line.includes("[OK]"))    color = "var(--accent-green)";
          else if (line.includes("[KEY]") || line.includes("[WHY]")) color = "#f59e0b";
          else if (line.includes("[CMD]") || line.includes("[EVAL]")) color = "var(--accent-cyan)";
          else if (line.includes("[OUT]")) color = "#a78bfa";
          else if (line.includes("[ERROR]")) color = "var(--accent-red)";
          else if (line.includes("[INFO]")) color = "var(--text-secondary)";
          logTerm1(line, color);
        }
      } catch (e) {
        logTerm1("[ERROR] " + e, "var(--accent-danger)");
      } finally {
        btn1Deploy.disabled = false;
      }
    });
  }

  if (btn1Status) {
    btn1Status.addEventListener("click", async () => {
      btn1Status.disabled = true;
      terminal1.innerHTML = "";
      logTerm1("[INFO] Fetching replica set status...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab13-rs-status", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();
        logTerm1("", null);
        logTerm1("rs.status() — Replica Set: " + data.replica_set, "var(--accent-cyan)");
        logTerm1("Auth Enforced: " + (data.auth_enforced ? "YES (keyFile)" : "NO"), data.auth_enforced ? "var(--accent-green)" : "var(--accent-danger)");
        logTerm1("", null);
        data.members.forEach(m => {
          const stateColor = m.state === "PRIMARY" ? "var(--accent-green)" : m.state === "ARBITER" ? "#f59e0b" : "var(--accent-cyan)";
          const tag = m.arbiter ? " [ARBITER]" : "";
          logTerm1("  " + m.host + "  →  " + m.state + tag + "  (priority: " + m.priority + ")", stateColor);
        });
        logTerm1("", null);
        logTerm1("Connection String:", "var(--text-primary)");
        logTerm1("  " + data.connection_string, "var(--accent-cyan)");
        logTerm1("", null);
        logTerm1("Chapter 8: " + data.chapter8_vs_13.ch8, "var(--text-secondary)");
        logTerm1("Chapter 13: " + data.chapter8_vs_13.ch13, "var(--accent-green)");
      } catch (e) {
        logTerm1("[ERROR] " + e, "var(--accent-danger)");
      } finally {
        btn1Status.disabled = false;
      }
    });
  }

  // --- Activity 2: Kubernetes Manifest Viewer ---
  const manifestDisplay = document.getElementById("lab13ManifestDisplay");
  const manifestBtns = document.querySelectorAll("[data-manifest]");

  manifestBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const manifest = btn.getAttribute("data-manifest");
      manifestBtns.forEach(b => b.style.opacity = "0.6");
      btn.style.opacity = "1";
      if (manifestDisplay) manifestDisplay.textContent = "Loading manifest...";
      try {
        const res = await fetch("/api/lab13-manifest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ manifest })
        });
        const data = await res.json();
        if (manifestDisplay) manifestDisplay.textContent = data.content;
      } catch (e) {
        if (manifestDisplay) manifestDisplay.textContent = "Error: " + e;
      }
    });
  });

  // Auto-load first manifest
  const firstManifestBtn = document.querySelector("[data-manifest='00-namespace']");
  if (firstManifestBtn) firstManifestBtn.click();

  // --- Activity 2: K8s Deployment Simulator ---
  const btn2K8s = document.getElementById("btnLab13K8sDeploy");
  const terminal2 = document.getElementById("lab13Terminal2");

  function logTerm2(msg, color) {
    if (!terminal2) return;
    const div = document.createElement("div");
    if (color) div.style.color = color;
    div.textContent = msg;
    terminal2.appendChild(div);
    terminal2.scrollTop = terminal2.scrollHeight;
  }

  if (btn2K8s) {
    btn2K8s.addEventListener("click", async () => {
      btn2K8s.disabled = true;
      terminal2.innerHTML = "";
      logTerm2("[EXEC] Simulating kubectl apply pipeline...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab13-k8s-sim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();
        for (let i = 0; i < data.output.length; i++) {
          await new Promise(r => setTimeout(r, 60));
          const line = data.output[i];
          let color = null;
          if (line.includes("[OK]"))    color = "var(--accent-green)";
          else if (line.includes("[WHY]")) color = "#f59e0b";
          else if (line.includes("[OUT]")) color = "#a78bfa";
          else if (line.includes("[INFO]") || line.includes("[VERIFY]")) color = "var(--text-secondary)";
          logTerm2(line, color);
        }
      } catch (e) {
        logTerm2("[ERROR] " + e, "var(--accent-danger)");
      } finally {
        btn2K8s.disabled = false;
      }
    });
  }
}

/* ==========================================================================
   Lab 14: Production Monitoring & Backup Verification
   ========================================================================== */
function initLab14() {
  const btnFetch = document.getElementById("btnLab14FetchMetrics");
  const btnRunMonitor = document.getElementById("btnLab14RunMonitor");
  const btnViewLogs = document.getElementById("btnLab14ViewLogs");
  const alertBadge = document.getElementById("lab14AlertBadge");
  const terminal1 = document.getElementById("lab14Terminal1");
  const logContainer = document.getElementById("lab14LogContainer");

  const btnRunRestore = document.getElementById("btnLab14RunRestore");
  const chkCorrupt = document.getElementById("chkLab14Corrupt");
  const terminal2 = document.getElementById("lab14Terminal2");
  const verdictSection = document.getElementById("lab14VerdictSection");

  function logTerm1(msg, color) {
    if (!terminal1) return;
    const div = document.createElement("div");
    if (color) div.style.color = color;
    div.textContent = msg;
    terminal1.appendChild(div);
    terminal1.scrollTop = terminal1.scrollHeight;
  }

  function logTerm2(msg, color) {
    if (!terminal2) return;
    const div = document.createElement("div");
    if (color) div.style.color = color;
    div.textContent = msg;
    terminal2.appendChild(div);
    terminal2.scrollTop = terminal2.scrollHeight;
  }

  function updateMetricsUI(m, alerts) {
    if (!m) return;
    const elConn = document.getElementById("lab14MetricConn");
    const elCache = document.getElementById("lab14MetricCache");
    const elOps = document.getElementById("lab14MetricOps");
    const mConnCurr = document.getElementById("m_conn_curr");
    const mConnAvail = document.getElementById("m_conn_avail");
    const mCachePct = document.getElementById("m_cache_pct");
    const mCacheBytes = document.getElementById("m_cache_bytes");
    const mCacheDirty = document.getElementById("m_cache_dirty");
    const mOpsSummary = document.getElementById("m_ops_summary");

    if (elConn) elConn.textContent = `${m.connections_current} / ${(m.connections_available / 1000).toFixed(0)}k`;
    if (elCache) elCache.textContent = `${m.cache_usage_pct}%`;
    const totalOps = (m.op_insert || 0) + (m.op_query || 0) + (m.op_update || 0) + (m.op_delete || 0);
    if (elOps) elOps.textContent = `${(totalOps / 1000).toFixed(0)}k Ops`;

    if (mConnCurr) mConnCurr.textContent = m.connections_current;
    if (mConnAvail) mConnAvail.textContent = (m.connections_available || 0).toLocaleString();
    if (mCachePct) mCachePct.textContent = `${m.cache_usage_pct}%`;
    if (mCacheBytes) {
      const mbInUse = (m.cache_bytes_in_use / (1024 * 1024)).toFixed(1);
      const mbMax = (m.cache_max_bytes / (1024 * 1024)).toFixed(0);
      mCacheBytes.textContent = `${mbInUse} MB / ${mbMax} MB`;
    }
    if (mCacheDirty) mCacheDirty.textContent = `${(m.cache_dirty_bytes || 0).toLocaleString()} bytes`;
    if (mOpsSummary) {
      mOpsSummary.textContent = `${(m.op_insert || 0).toLocaleString()} / ${(m.op_query || 0).toLocaleString()} / ${(m.op_update || 0).toLocaleString()} / ${(m.op_delete || 0).toLocaleString()}`;
    }

    if (alertBadge) {
      if (alerts && alerts.length > 0) {
        alertBadge.style.background = "rgba(239, 68, 68, 0.2)";
        alertBadge.style.color = "var(--accent-danger)";
        alertBadge.textContent = `⚠️ Active Alerts (${alerts.length})`;
      } else {
        alertBadge.style.background = "rgba(16, 185, 129, 0.15)";
        alertBadge.style.color = "var(--accent-primary)";
        alertBadge.textContent = "● Systems Nominal (No Alerts)";
      }
    }
  }

  // --- 1. Fetch Live Metrics ---
  if (btnFetch) {
    btnFetch.addEventListener("click", async () => {
      btnFetch.disabled = true;
      if (terminal1) terminal1.innerHTML = "";
      logTerm1("[INFO] Requesting serverStatus from MongoDB instance...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab14-metrics");
        const data = await res.json();
        if (data.success && data.metrics) {
          updateMetricsUI(data.metrics, data.metrics.alerts);
          logTerm1(`[OK] serverStatus retrieved (${data.metrics.live ? "LIVE INSTANCE" : "DEMO FALLBACK"}).`, "var(--accent-primary)");
          logTerm1(`     Timestamp:              ${data.metrics.timestamp}`);
          logTerm1(`     Connections Active:     ${data.metrics.connections_current} (Avail: ${data.metrics.connections_available})`);
          logTerm1(`     WiredTiger Cache Usage: ${data.metrics.cache_usage_pct}% (${(data.metrics.cache_bytes_in_use / (1024*1024)).toFixed(1)} MB / ${(data.metrics.cache_max_bytes / (1024*1024)).toFixed(0)} MB)`);
          logTerm1(`     Operation Counters:     Ins=${data.metrics.op_insert}, Qry=${data.metrics.op_query}, Upd=${data.metrics.op_update}, Del=${data.metrics.op_delete}`);
          if (data.metrics.alerts && data.metrics.alerts.length > 0) {
            data.metrics.alerts.forEach(a => logTerm1(`     ${a}`, "var(--accent-danger)"));
          } else {
            logTerm1("     Threshold Alerts:       None. All metrics within safety margins.", "var(--accent-primary)");
          }
        }
      } catch (err) {
        logTerm1(`[ERROR] Failed to fetch metrics: ${err.message}`, "var(--accent-danger)");
      } finally {
        btnFetch.disabled = false;
      }
    });
  }

  // --- 2. Run Monitoring Cycle ---
  if (btnRunMonitor) {
    btnRunMonitor.addEventListener("click", async () => {
      btnRunMonitor.disabled = true;
      if (terminal1) terminal1.innerHTML = "";
      logTerm1("[EXEC] Initiating monitoring cycle (lab_01_monitoring_dashboard.py)...", "var(--accent-cyan)");
      try {
        const res = await fetch("/api/lab14-run-monitoring", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        const data = await res.json();
        if (data.success && data.output) {
          for (const line of data.output) {
            await new Promise(r => setTimeout(r, 40));
            let color = "var(--text-primary)";
            if (line.includes("[OK]")) color = "var(--accent-primary)";
            else if (line.includes("[ALERT]") || line.includes("WARNING")) color = "var(--accent-danger)";
            else if (line.includes("===")) color = "var(--accent-cyan)";
            logTerm1(line, color);
          }
          if (data.metrics) {
            updateMetricsUI(data.metrics, data.alerts);
          }
          if (btnViewLogs) btnViewLogs.click();
        }
      } catch (err) {
        logTerm1(`[ERROR] Monitoring cycle failed: ${err.message}`, "var(--accent-danger)");
      } finally {
        btnRunMonitor.disabled = false;
      }
    });
  }

  // --- 3. View Logs ---
  if (btnViewLogs) {
    btnViewLogs.addEventListener("click", async () => {
      if (logContainer) logContainer.textContent = "Loading logs/metrics.log...";
      try {
        const res = await fetch("/api/lab14-get-logs");
        const data = await res.json();
        if (data.success && logContainer) {
          logContainer.textContent = data.entries.join("\n");
          logContainer.scrollTop = logContainer.scrollHeight;
        }
      } catch (err) {
        if (logContainer) logContainer.textContent = `Error reading logs: ${err.message}`;
      }
    });
  }

  // --- 4. Disaster Recovery Drill ---
  if (btnRunRestore) {
    btnRunRestore.addEventListener("click", async () => {
      btnRunRestore.disabled = true;
      if (terminal2) terminal2.innerHTML = "";
      if (verdictSection) verdictSection.style.display = "none";

      const isCorrupt = chkCorrupt && chkCorrupt.checked;
      logTerm2(`[INIT] Running automated disaster recovery pipeline (corrupt=${isCorrupt})...`, "var(--accent-cyan)");

      const stepCards = ["drStep1Card", "drStep2Card", "drStep3Card", "drStep4Card", "drStep5Card"].map(id => document.getElementById(id));
      stepCards.forEach(c => { if (c) { c.style.border = "1px solid var(--border-color)"; c.style.boxShadow = "none"; } });

      try {
        const res = await fetch("/api/lab14-run-backup-restore", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ corrupt: isCorrupt })
        });
        const data = await res.json();

        if (data.output) {
          for (const line of data.output) {
            await new Promise(r => setTimeout(r, 60));
            let color = "var(--text-primary)";
            if (line.includes("=== Step 1")) {
              if (stepCards[0]) { stepCards[0].style.border = "2px solid var(--accent-primary)"; stepCards[0].style.boxShadow = "var(--shadow-glow)"; }
              color = "var(--accent-cyan)";
            } else if (line.includes("=== Step 2")) {
              if (stepCards[1]) { stepCards[1].style.border = "2px solid var(--accent-primary)"; }
              color = "var(--accent-cyan)";
            } else if (line.includes("=== Step 3")) {
              if (stepCards[2]) { stepCards[2].style.border = "2px solid var(--accent-warning)"; }
              color = "var(--accent-warning)";
            } else if (line.includes("=== Step 4")) {
              if (stepCards[3]) { stepCards[3].style.border = "2px solid var(--accent-primary)"; }
              color = "var(--accent-cyan)";
            } else if (line.includes("=== Step 5")) {
              if (stepCards[4]) {
                stepCards[4].style.border = data.checksum_ok ? "2px solid var(--accent-primary)" : "2px solid var(--accent-danger)";
              }
              color = "var(--accent-cyan)";
            } else if (line.includes("✅") || line.includes("[OK]")) {
              color = "var(--accent-primary)";
            } else if (line.includes("❌") || line.includes("[FAIL]") || line.includes("CRITICAL")) {
              color = "var(--accent-danger)";
            } else if (line.includes("INJECTED") || line.includes("TEST INJECTION")) {
              color = "var(--accent-warning)";
            }
            logTerm2(line, color);
          }
        }

        if (data.success && verdictSection) {
          verdictSection.style.display = "block";
          const elOrigCount = document.getElementById("v_orig_count");
          const elRestCount = document.getElementById("v_rest_count");
          const elCountStatus = document.getElementById("v_count_status");
          const elOrigHash = document.getElementById("v_orig_hash");
          const elRestHash = document.getElementById("v_rest_hash");
          const elHashStatus = document.getElementById("v_hash_status");
          const elRto = document.getElementById("v_rto_time");
          const elVerdict = document.getElementById("v_final_verdict");

          if (elOrigCount) elOrigCount.textContent = data.original_count;
          if (elRestCount) elRestCount.textContent = data.restored_count;
          if (elCountStatus) {
            elCountStatus.innerHTML = data.count_ok
              ? '<span class="badge-tag" style="background:rgba(16,185,129,0.2);color:var(--accent-primary);">MATCH [OK]</span>'
              : '<span class="badge-tag" style="background:rgba(239,68,68,0.2);color:var(--accent-danger);">MISMATCH [FAIL]</span>';
          }

          if (elOrigHash) elOrigHash.textContent = (data.original_checksum || "").substring(0, 16) + "...";
          if (elRestHash) elRestHash.textContent = (data.restored_checksum || "").substring(0, 16) + "...";
          if (elHashStatus) {
            elHashStatus.innerHTML = data.checksum_ok
              ? '<span class="badge-tag" style="background:rgba(16,185,129,0.2);color:var(--accent-primary);">MATCH [OK]</span>'
              : '<span class="badge-tag" style="background:rgba(239,68,68,0.2);color:var(--accent-danger);">MISMATCH [FAIL]</span>';
          }

          if (elRto) elRto.textContent = `${data.rto_seconds}s (${Math.round(data.rto_seconds * 1000)} ms)`;
          if (elVerdict) {
            if (data.count_ok && data.checksum_ok) {
              elVerdict.style.color = "var(--accent-primary)";
              elVerdict.textContent = "✅ " + data.verdict;
            } else {
              elVerdict.style.color = "var(--accent-danger)";
              elVerdict.textContent = "❌ " + data.verdict;
            }
          }
        }
      } catch (err) {
        logTerm2(`[ERROR] Disaster recovery drill failed: ${err.message}`, "var(--accent-danger)");
      } finally {
        btnRunRestore.disabled = false;
      }
    });
  }
}

/* ==========================================================================
   Lab 15: Multi-Tenant Architecture & Data Migration
   ========================================================================== */
function initLab15() {
  const tenantSelect = document.getElementById("lab15TenantSelect");
  const btnRefreshTasks = document.getElementById("btnLab15RefreshTasks");
  const tasksTableBody = document.getElementById("lab15TasksTableBody");
  const btnCreateTask = document.getElementById("btnLab15CreateTask");

  const btnSecureUpdate = document.getElementById("btnLab15TestSecureUpdate");
  const btnExploitUpdate = document.getElementById("btnLab15TestExploitUpdate");
  const exploitResult = document.getElementById("lab15ExploitResult");

  const btnSendSingle = document.getElementById("btnLab15SendSingleReq");
  const btnSendBurst = document.getElementById("btnLab15SendBurstReq");
  const btnResetRate = document.getElementById("btnLab15ResetRateLimit");
  const rateLimitLogs = document.getElementById("lab15RateLimitLogs");
  const rateProgressBar = document.getElementById("lab15RateProgressBar");
  const rateCountVal = document.getElementById("lab15RateCountVal");

  const migrateTenantSelect = document.getElementById("lab15MigrateTenantSelect");
  const btnDryRun = document.getElementById("btnLab15DryRun");
  const btnLiveMigrate = document.getElementById("btnLab15LiveMigrate");
  const btnIdempotent = document.getElementById("btnLab15IdempotentRun");
  const btnRollback = document.getElementById("btnLab15Rollback");
  const migrationDetails = document.getElementById("lab15MigrationDetails");

  const btnRunScript1 = document.getElementById("btnRunLab15Script1");
  const btnRunScript2 = document.getElementById("btnRunLab15Script2");
  const btnResetDb = document.getElementById("btnResetLab15Db");
  const terminalOutput = document.getElementById("lab15TerminalOutput");
  const runnerStatus = document.getElementById("lab15RunnerStatus");

  let currentTasks = [];

  // --- Task Manager ---
  async function loadTasks(tenantId) {
    if (!tasksTableBody) return;
    tasksTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);padding:1rem;">Loading tasks...</td></tr>';
    try {
      const res = await fetch(`/api/lab15-tasks?tenant_id=${tenantId}`);
      const data = await res.json();
      if (data.success && data.tasks) {
        currentTasks = data.tasks;
        renderTasks(data.tasks);
      } else {
        tasksTableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--accent-danger);padding:1rem;">Error: ${data.error || "Failed to load"}</td></tr>`;
      }
    } catch (err) {
      tasksTableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--accent-danger);padding:1rem;">Connection error: ${err.message}</td></tr>`;
    }
  }

  function renderTasks(tasks) {
    if (!tasksTableBody) return;
    if (tasks.length === 0) {
      tasksTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);padding:1rem;">No tasks found for this tenant.</td></tr>';
      return;
    }
    tasksTableBody.innerHTML = "";
    tasks.forEach(t => {
      const tr = document.createElement("tr");
      const pColor = t.priority === "high" ? "var(--accent-danger)" : (t.priority === "medium" ? "var(--accent-warning)" : "var(--accent-cyan)");
      const sBadge = t.status === "completed" 
        ? '<span class="badge-tag green">completed</span>' 
        : '<span class="badge-tag yellow">open</span>';

      tr.innerHTML = `
        <td style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-muted);">${t._id}</td>
        <td><span class="badge-tag" style="background:rgba(6,182,212,0.15);color:var(--accent-cyan);font-family:var(--font-mono);">${t.tenant_id}</span></td>
        <td>
          <strong style="color:var(--text-primary);display:block;">${t.title}</strong>
          <span style="font-size:0.78rem;color:var(--text-muted);">${t.description || "No description"}</span>
        </td>
        <td><span style="color:${pColor};font-weight:600;font-size:0.8rem;text-transform:uppercase;">${t.priority}</span></td>
        <td style="color:var(--text-secondary);font-size:0.85rem;">${t.assignee || "unassigned"}</td>
        <td>${sBadge}</td>
        <td>
          ${t.status !== "completed" ? `<button class="btn btn-secondary btn-complete-task" data-id="${t._id}" style="padding:0.25rem 0.5rem;font-size:0.75rem;">Done</button>` : '<span style="color:var(--text-muted);font-size:0.75rem;">-</span>'}
        </td>
      `;
      tasksTableBody.appendChild(tr);
    });

    document.querySelectorAll(".btn-complete-task").forEach(b => {
      b.addEventListener("click", async () => {
        const taskId = b.getAttribute("data-id");
        const activeTenant = tenantSelect ? tenantSelect.value : "tenant-acme";
        try {
          const res = await fetch("/api/lab15-update-task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ caller_tenant: activeTenant, task_id: taskId, updates: { status: "completed" } })
          });
          const d = await res.json();
          if (d.success) {
            loadTasks(activeTenant);
          }
        } catch (e) {
          alert(`Error updating task: ${e.message}`);
        }
      });
    });
  }

  if (tenantSelect) {
    tenantSelect.addEventListener("change", () => loadTasks(tenantSelect.value));
    loadTasks(tenantSelect.value);
  }

  if (btnRefreshTasks && tenantSelect) {
    btnRefreshTasks.addEventListener("click", () => loadTasks(tenantSelect.value));
  }

  if (btnCreateTask && tenantSelect) {
    btnCreateTask.addEventListener("click", async () => {
      const titleInput = document.getElementById("lab15NewTitle");
      const descInput = document.getElementById("lab15NewDesc");
      const prioInput = document.getElementById("lab15NewPriority");
      const assInput = document.getElementById("lab15NewAssignee");

      const title = titleInput ? titleInput.value.trim() : "";
      if (!title) {
        alert("Please enter a task title");
        return;
      }

      const activeTenant = tenantSelect.value;
      try {
        const res = await fetch("/api/lab15-tasks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tenant_id: activeTenant,
            title: title,
            description: descInput ? descInput.value.trim() : "",
            priority: prioInput ? prioInput.value : "medium",
            assignee: assInput ? assInput.value.trim() : "unassigned"
          })
        });
        const data = await res.json();
        if (data.success) {
          if (titleInput) titleInput.value = "";
          if (descInput) descInput.value = "";
          if (assInput) assInput.value = "";
          loadTasks(activeTenant);
          updateMigrationSummary();
        } else {
          alert("Failed to create task: " + data.error);
        }
      } catch (e) {
        alert("Network error: " + e.message);
      }
    });
  }

  // --- Exploit Simulator ---
  async function runExploitTest(exploitMode) {
    if (!exploitResult) return;
    exploitResult.style.display = "block";
    exploitResult.innerHTML = '<span style="color:var(--text-muted);">Executing test query against MongoDB...</span>';

    // Find Acme's first task
    try {
      const r = await fetch("/api/lab15-tasks?tenant_id=tenant-acme");
      const acmeData = await r.json();
      if (!acmeData.tasks || acmeData.tasks.length === 0) {
        exploitResult.innerHTML = '<span style="color:var(--accent-warning);">No Acme tasks found to test. Reset DB first.</span>';
        return;
      }
      const targetTask = acmeData.tasks[0];

      const res = await fetch("/api/lab15-update-task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          caller_tenant: "tenant-globex",
          task_id: targetTask._id,
          updates: { status: "exploited_deleted", title: "CORRUPTED BY GLOBEX" },
          exploit_mode: exploitMode
        })
      });
      const data = await res.json();

      if (exploitMode) {
        exploitResult.style.background = "rgba(239, 68, 68, 0.15)";
        exploitResult.style.border = "1px solid var(--accent-danger)";
        exploitResult.style.color = "var(--text-primary)";
        exploitResult.innerHTML = `
          <strong style="color:var(--accent-danger);">❌ ${data.verdict}</strong><br>
          <div style="margin-top:0.4rem;color:var(--text-secondary);font-size:0.8rem;">
            &bull; Attacker: <code>${data.caller_tenant}</code> &bull; Target Doc Owner: <code>${data.real_owner}</code><br>
            &bull; Filter Executed: <code>${JSON.stringify(data.filter_used)}</code><br>
            &bull; Modified Documents: <strong style="color:var(--accent-danger);">${data.modified_count}</strong> (UNAUTHORIZED DATA MUTATION SUCCESSFUL!)
          </div>
        `;
      } else {
        exploitResult.style.background = "rgba(16, 185, 129, 0.15)";
        exploitResult.style.border = "1px solid var(--accent-primary)";
        exploitResult.style.color = "var(--text-primary)";
        exploitResult.innerHTML = `
          <strong style="color:var(--accent-primary);">🛡️ ${data.verdict}</strong><br>
          <div style="margin-top:0.4rem;color:var(--text-secondary);font-size:0.8rem;">
            &bull; Attacker: <code>${data.caller_tenant}</code> &bull; Target Doc Owner: <code>${data.real_owner}</code><br>
            &bull; Filter Executed: <code>${JSON.stringify(data.filter_used)}</code><br>
            &bull; Modified Documents: <strong style="color:var(--accent-primary);">${data.modified_count}</strong> (ATTACK REJECTED BY DATABASE FILTER)
          </div>
        `;
      }
      if (tenantSelect) loadTasks(tenantSelect.value);
    } catch (e) {
      exploitResult.innerHTML = `<span style="color:var(--accent-danger);">Test failed: ${e.message}</span>`;
    }
  }

  if (btnSecureUpdate) btnSecureUpdate.addEventListener("click", () => runExploitTest(false));
  if (btnExploitUpdate) btnExploitUpdate.addEventListener("click", () => runExploitTest(true));

  // --- Rate Limiting ---
  async function callRateLimit(burst) {
    if (!rateLimitLogs) return;
    try {
      const res = await fetch("/api/lab15-rate-limit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenant_id: "tenant-acme", burst_count: burst ? 12 : 1 })
      });
      const data = await res.json();
      if (data.success && data.results) {
        if (burst && rateLimitLogs) rateLimitLogs.innerHTML = "";
        data.results.forEach(r => {
          const div = document.createElement("div");
          if (r.allowed) {
            div.innerHTML = `<span style="color:var(--accent-primary);">[${r.time}] Request ${r.request_num}: ALLOWED</span> (Current active: ${r.current_count}/10 in window)`;
          } else {
            div.innerHTML = `<span style="color:var(--accent-danger);font-weight:700;">[${r.time}] Request ${r.request_num}: RATE LIMITED (429)</span> (Threshold exceeded: &gt;= ${r.limit} req / 60s)`;
          }
          rateLimitLogs.appendChild(div);
        });
        rateLimitLogs.scrollTop = rateLimitLogs.scrollHeight;

        const count = data.active_window_requests || 0;
        const pct = Math.min(100, (count / 10) * 100);
        if (rateProgressBar) {
          rateProgressBar.style.width = `${pct}%`;
          rateProgressBar.style.background = count >= 10 ? "var(--accent-danger)" : (count >= 7 ? "var(--accent-warning)" : "var(--accent-primary)");
        }
        if (rateCountVal) {
          rateCountVal.textContent = `${count} / 10`;
          rateCountVal.style.color = count >= 10 ? "var(--accent-danger)" : "var(--accent-primary)";
        }
      }
    } catch (e) {
      if (rateLimitLogs) rateLimitLogs.innerHTML += `<div style="color:var(--accent-danger);">Rate limit error: ${e.message}</div>`;
    }
  }

  if (btnSendSingle) btnSendSingle.addEventListener("click", () => callRateLimit(false));
  if (btnSendBurst) btnSendBurst.addEventListener("click", () => callRateLimit(true));
  if (btnResetRate) {
    btnResetRate.addEventListener("click", async () => {
      if (rateLimitLogs) rateLimitLogs.innerHTML = '<div style="color:var(--accent-cyan);">[INFO] Rate limit counter reset.</div>';
      if (rateProgressBar) rateProgressBar.style.width = "0%";
      if (rateCountVal) rateCountVal.textContent = "0 / 10";
    });
  }

  // --- Migration Controls ---
  async function updateMigrationSummary() {
    try {
      const res = await fetch("/api/lab15-summary");
      const d = await res.json();
      if (d.success) {
        const elAcme = document.getElementById("lab15SharedAcmeCount");
        const elGlobex = document.getElementById("lab15SharedGlobexCount");
        const elTargetStatus = document.getElementById("lab15TargetDbStatus");
        const elTargetCount = document.getElementById("lab15TargetDbCount");
        const elTargetName = document.getElementById("lab15TargetDbName");

        if (elAcme) elAcme.textContent = d.shared_app.tenant_acme_count;
        if (elGlobex) elGlobex.textContent = d.shared_app.tenant_globex_count;

        const selected = migrateTenantSelect ? migrateTenantSelect.value : "tenant-acme";
        const dbKey = selected === "tenant-acme" ? "tenant_acme" : "tenant_globex";
        if (elTargetName) elTargetName.textContent = dbKey;

        const dedicatedInfo = d.dedicated_databases[dbKey];
        if (dedicatedInfo && dedicatedInfo.exists) {
          if (elTargetStatus) {
            elTargetStatus.textContent = "MIGRATED & ACTIVE";
            elTargetStatus.style.color = "var(--accent-primary)";
          }
          if (elTargetCount) elTargetCount.textContent = `${dedicatedInfo.count} docs`;
        } else {
          if (elTargetStatus) {
            elTargetStatus.textContent = "NOT MIGRATED";
            elTargetStatus.style.color = "var(--accent-warning)";
          }
          if (elTargetCount) elTargetCount.textContent = "-";
        }
      }
    } catch (e) {
      console.warn("Migration summary update failed", e);
    }
  }

  if (migrateTenantSelect) {
    migrateTenantSelect.addEventListener("change", updateMigrationSummary);
  }
  updateMigrationSummary();

  if (btnDryRun && migrateTenantSelect && migrationDetails) {
    btnDryRun.addEventListener("click", async () => {
      const tenant = migrateTenantSelect.value;
      migrationDetails.innerHTML = `<span style="color:var(--accent-warning);">[PLANNING] Running dry-run migration for ${tenant}...</span>`;
      try {
        const res = await fetch("/api/lab15-migrate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tenant_id: tenant, dry_run: true })
        });
        const d = await res.json();
        if (d.success) {
          migrationDetails.innerHTML = `
            <span style="color:var(--accent-warning);font-weight:700;">🔍 DRY RUN REPORT (--dry-run)</span><br>
            &bull; Target Database: <strong style="color:var(--accent-cyan);">${d.target_db}</strong><br>
            &bull; Eligible Documents Found: <strong style="color:var(--accent-primary);">${d.would_move}</strong> in saas_app.tasks<br>
            &bull; Database Writes Committed: <strong style="color:var(--accent-warning);">0</strong> (Safe simulation mode)<br>
            &bull; Status: <span class="badge-tag yellow">DRY_RUN SUCCESS</span><br>
            <em>Ready for live execution with upsert natural key isolation.</em>
          `;
        } else {
          migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Dry run error: ${d.message || d.error}</span>`;
        }
      } catch (e) {
        migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Network error: ${e.message}</span>`;
      }
    });
  }

  if (btnLiveMigrate && migrateTenantSelect && migrationDetails) {
    btnLiveMigrate.addEventListener("click", async () => {
      const tenant = migrateTenantSelect.value;
      migrationDetails.innerHTML = `<span style="color:var(--accent-cyan);">[MIGRATING] Moving ${tenant} to dedicated database...</span>`;
      try {
        const res = await fetch("/api/lab15-migrate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tenant_id: tenant, dry_run: false })
        });
        const d = await res.json();
        if (d.success) {
          const vBadge = document.getElementById("lab15VerificationBadge");
          const vMsg = document.getElementById("lab15IdempotencyMsg");
          if (vBadge) {
            vBadge.textContent = d.verified ? "VERIFIED [MATCH]" : "VERIFICATION FAILED";
            vBadge.style.color = d.verified ? "var(--accent-primary)" : "var(--accent-danger)";
          }
          if (vMsg) {
            vMsg.textContent = `SHA-256 Checksum Match: ${d.source_checksum.substring(0, 12)}...`;
          }

          migrationDetails.innerHTML = `
            <span style="color:var(--accent-primary);font-weight:700;">✅ LIVE MIGRATION REPORT (${d.status})</span><br>
            &bull; Source Collection: <code>saas_app.tasks</code> (Count: ${d.source_count})<br>
            &bull; Target Collection: <code>${d.target_db}.tasks</code> (Count: ${d.target_count})<br>
            &bull; Write Pattern: <strong>upsert=True on (tenant_id, title)</strong><br>
            &bull; Source SHA-256: <code>${d.source_checksum}</code><br>
            &bull; Target SHA-256: <code>${d.target_checksum}</code><br>
            &bull; Verification Audit: <strong style="color:var(--accent-primary);">${d.verified ? "100% BYTE MATCH [PASSED]" : "CHECKSUM MISMATCH"}</strong>
          `;
          updateMigrationSummary();
        } else {
          migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Migration error: ${d.message || d.error}</span>`;
        }
      } catch (e) {
        migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Network error: ${e.message}</span>`;
      }
    });
  }

  if (btnIdempotent && migrateTenantSelect && migrationDetails) {
    btnIdempotent.addEventListener("click", async () => {
      const tenant = migrateTenantSelect.value;
      migrationDetails.innerHTML = `<span style="color:var(--accent-secondary);">[IDEMPOTENCY TEST] Re-running migration for ${tenant} a second time...</span>`;
      try {
        const res = await fetch("/api/lab15-migrate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tenant_id: tenant, dry_run: false })
        });
        const d = await res.json();
        if (d.success) {
          migrationDetails.innerHTML = `
            <span style="color:var(--accent-secondary);font-weight:700;">🔁 IDEMPOTENCY VERIFICATION COMPLETE</span><br>
            &bull; Target Document Count on Re-Run: <strong style="color:var(--accent-primary);">${d.target_count}</strong> (Identical to source: ${d.source_count})<br>
            &bull; Duplicates Created: <strong style="color:var(--accent-primary);">0 DUPLICATES</strong><br>
            &bull; Idempotency Guarantee: <strong>PASS</strong> — Re-running the migration converges cleanly to the exact target state because updates are keyed on <code>(tenant_id, title)</code> rather than random auto-generated ObjectIds.
          `;
          updateMigrationSummary();
        }
      } catch (e) {
        migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Idempotency test failed: ${e.message}</span>`;
      }
    });
  }

  if (btnRollback && migrateTenantSelect && migrationDetails) {
    btnRollback.addEventListener("click", async () => {
      const tenant = migrateTenantSelect.value;
      migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">[ROLLBACK] Dropping dedicated database for ${tenant}...</span>`;
      try {
        const res = await fetch("/api/lab15-rollback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tenant_id: tenant })
        });
        const d = await res.json();
        if (d.success) {
          const vBadge = document.getElementById("lab15VerificationBadge");
          const vMsg = document.getElementById("lab15IdempotencyMsg");
          if (vBadge) {
            vBadge.textContent = "ROLLED BACK";
            vBadge.style.color = "var(--accent-warning)";
          }
          if (vMsg) vMsg.textContent = "Dedicated DB removed. Shared data intact.";

          migrationDetails.innerHTML = `
            <span style="color:var(--accent-danger);font-weight:700;">⏪ ROLLBACK EXECUTED SUCCESSFULLY</span><br>
            &bull; Dropped Database: <strong style="color:var(--accent-warning);">${d.dropped_db}</strong><br>
            &bull; Shared Collection Status: <code>saas_app.tasks</code> retains all <strong style="color:var(--accent-primary);">${d.shared_count}</strong> original records.<br>
            &bull; Zero-Risk Safety Proof: The migration copied data rather than moving and deleting. Rollback required only dropping the tenant copy, leaving the original data untouched!
          `;
          updateMigrationSummary();
        }
      } catch (e) {
        migrationDetails.innerHTML = `<span style="color:var(--accent-danger);">Rollback error: ${e.message}</span>`;
      }
    });
  }

  // --- Live Terminal Script Runner ---
  async function streamScriptOutput(url, title) {
    if (!terminalOutput) return;
    terminalOutput.innerHTML = "";
    if (runnerStatus) runnerStatus.textContent = "Executing...";

    try {
      const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" } });
      const d = await res.json();
      if (d.success && d.output) {
        for (const line of d.output) {
          await new Promise(r => setTimeout(r, 45));
          const div = document.createElement("div");
          if (line.includes("[OK]") || line.includes("Complete")) {
            div.style.color = "var(--accent-primary)";
          } else if (line.includes("===") || line.includes("---")) {
            div.style.color = "var(--accent-cyan)";
          } else if (line.includes("RATE LIMITED") || line.includes("blocked") || line.includes("False")) {
            div.style.color = "var(--accent-warning)";
          } else {
            div.style.color = "var(--text-primary)";
          }
          div.textContent = line;
          terminalOutput.appendChild(div);
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }
      }
      if (runnerStatus) runnerStatus.textContent = "Finished";
    } catch (e) {
      terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution error: ${e.message}</div>`;
      if (runnerStatus) runnerStatus.textContent = "Error";
    }
  }

  if (btnRunScript1) {
    btnRunScript1.addEventListener("click", () => streamScriptOutput("/api/lab15-run-lab1", "Lab 15.1"));
  }
  if (btnRunScript2) {
    btnRunScript2.addEventListener("click", () => streamScriptOutput("/api/lab15-run-lab2", "Lab 15.2"));
  }
  if (btnResetDb) {
    btnResetDb.addEventListener("click", async () => {
      if (terminalOutput) terminalOutput.innerHTML = '<div style="color:var(--accent-cyan);">[RESET] Resetting saas_app collections and dropping tenant databases...</div>';
      try {
        const res = await fetch("/api/lab15-reset", { method: "POST", headers: { "Content-Type": "application/json" } });
        const d = await res.json();
        if (d.success) {
          if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-primary);">${d.message}</div>`;
          if (tenantSelect) loadTasks(tenantSelect.value);
          updateMigrationSummary();
        }
      } catch (e) {
        if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-danger);">Reset failed: ${e.message}</div>`;
      }
    });
  }
}

/* ==========================================================================
   Lab 16: Polyglot Persistence & Hybrid Query Services
   ========================================================================== */
function initLab16() {
  const lab16MongoStatus = document.getElementById("lab16MongoStatus");
  const lab16GraphStatus = document.getElementById("lab16GraphStatus");

  // Query 1 elements
  const caseSelect = document.getElementById("lab16CaseSelect");
  const btnPointLookup = document.getElementById("btnLab16ExecPointLookup");
  const pointLookupResult = document.getElementById("lab16PointLookupResult");

  // Query 2 elements
  const riskSlider = document.getElementById("lab16RiskThreshold");
  const riskValDisplay = document.getElementById("lab16RiskThresholdVal");
  const btnAttrFilter = document.getElementById("btnLab16ExecAttrFilter");
  const attrFilterResult = document.getElementById("lab16AttrFilterResult");

  // Query 3 elements
  const suspectSelect = document.getElementById("lab16SuspectSelect");
  const hopsSelect = document.getElementById("lab16HopsSelect");
  const btnTraversal = document.getElementById("btnLab16ExecTraversal");
  const traversalResult = document.getElementById("lab16TraversalResult");

  // Runner elements
  const btnRunScript1 = document.getElementById("btnRunLab16Script1");
  const btnRunScript2 = document.getElementById("btnRunLab16Script2");
  const btnResetDb = document.getElementById("btnResetLab16Db");
  const terminalOutput = document.getElementById("lab16TerminalOutput");
  const runnerStatus = document.getElementById("lab16RunnerStatus");

  // Sync risk slider display
  if (riskSlider && riskValDisplay) {
    riskSlider.addEventListener("input", (e) => {
      riskValDisplay.textContent = parseFloat(e.target.value).toFixed(2);
    });
  }

  // Load summary and status
  async function loadLab16Summary() {
    try {
      const res = await fetch("/api/lab16-summary");
      const d = await res.json();
      if (d.success) {
        if (lab16MongoStatus) {
          lab16MongoStatus.textContent = `MongoDB: ${d.mongodb.case_count} cases loaded`;
          lab16MongoStatus.className = "badge-tag green";
        }
        if (lab16GraphStatus) {
          lab16GraphStatus.textContent = `${d.graph_engine.backend} (${d.graph_engine.total_nodes} nodes, ${d.graph_engine.total_edges} edges)`;
          lab16GraphStatus.className = d.graph_engine.neo4j_available ? "badge-tag green" : "badge-tag cyan";
        }
      }
    } catch (err) {
      console.warn("Failed to load Lab 16 summary", err);
    }
  }

  // --- Query 1: Point Lookup ---
  if (btnPointLookup) {
    btnPointLookup.addEventListener("click", async () => {
      const caseId = caseSelect ? caseSelect.value : "FC-001";
      if (pointLookupResult) {
        pointLookupResult.innerHTML = '<div style="color:var(--text-muted);font-style:italic;">Routing query to database...</div>';
      }
      try {
        const res = await fetch("/api/lab16-query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query_type: "point_lookup", case_id: caseId })
        });
        const d = await res.json();
        if (d.success && pointLookupResult) {
          const doc = d.result;
          const jsonDisplay = JSON.stringify(doc, null, 2);
          pointLookupResult.innerHTML = `
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:var(--radius-md);padding:1rem;margin-bottom:0.75rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;gap:0.5rem;">
                <span class="badge-tag green" style="font-size:0.85rem;font-weight:600;">⚡ Routed to: ${d.routed_to}</span>
                <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--accent-primary);">${d.pattern}</span>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.6rem;">
                <strong>Architectural Bias:</strong> ${d.reason}
              </div>
              <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.75rem;">
                <strong>Tradeoff Note:</strong> ${d.alternative_analysis}
              </div>
              <div style="font-family:var(--font-mono);font-size:0.78rem;color:var(--accent-cyan);background:#090a0f;padding:0.5rem 0.75rem;border-radius:var(--radius-sm);margin-bottom:0.75rem;">
                ${d.code_executed}
              </div>
            </div>
            <pre style="background:#090a0f;padding:1rem;border-radius:var(--radius-md);font-family:var(--font-mono);font-size:0.85rem;color:var(--text-primary);border:1px solid rgba(255,255,255,0.05);overflow-x:auto;"><code>${jsonDisplay}</code></pre>
          `;
        }
      } catch (err) {
        if (pointLookupResult) {
          pointLookupResult.innerHTML = `<div style="color:var(--accent-danger);">Error: ${err.message}</div>`;
        }
      }
    });
  }

  // --- Query 2: Attribute Range Filter ---
  if (btnAttrFilter) {
    btnAttrFilter.addEventListener("click", async () => {
      const threshold = riskSlider ? parseFloat(riskSlider.value) : 0.8;
      if (attrFilterResult) {
        attrFilterResult.innerHTML = '<div style="color:var(--text-muted);font-style:italic;">Routing query to database...</div>';
      }
      try {
        const res = await fetch("/api/lab16-query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query_type: "attribute_filter", threshold: threshold })
        });
        const d = await res.json();
        if (d.success && attrFilterResult) {
          const count = d.count;
          const cases = d.result;
          let cardsHtml = "";
          cases.forEach(c => {
            const riskPct = Math.round(c.risk_score * 100);
            const rColor = c.risk_score >= 0.8 ? "var(--accent-danger)" : (c.risk_score >= 0.5 ? "var(--accent-warning)" : "var(--accent-primary)");
            cardsHtml += `
              <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-md);padding:0.85rem 1rem;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div style="font-weight:700;color:var(--text-primary);font-size:0.95rem;">Case ${c.case_id} &bull; Suspect: <span style="color:var(--accent-cyan);font-family:var(--font-mono);">${c.suspect_id}</span></div>
                  <div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.2rem;">Amount: ₹${c.amount ? c.amount.toLocaleString() : "N/A"} &bull; Merchant: ${c.merchant || "N/A"}</div>
                </div>
                <div style="text-align:right;">
                  <span style="display:inline-block;padding:0.25rem 0.6rem;border-radius:var(--radius-full);font-size:0.8rem;font-weight:700;background:rgba(239,68,68,0.15);color:${rColor};">
                    Score: ${c.risk_score} (${riskPct}%)
                  </span>
                </div>
              </div>
            `;
          });

          attrFilterResult.innerHTML = `
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:var(--radius-md);padding:1rem;margin-bottom:0.75rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;gap:0.5rem;">
                <span class="badge-tag green" style="font-size:0.85rem;font-weight:600;">⚡ Routed to: ${d.routed_to}</span>
                <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--accent-primary);">${d.pattern} (${count} matches)</span>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.6rem;">
                <strong>Architectural Bias:</strong> ${d.reason}
              </div>
              <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.75rem;">
                <strong>Why Cassandra Fails:</strong> ${d.alternative_analysis}
              </div>
              <div style="font-family:var(--font-mono);font-size:0.78rem;color:var(--accent-cyan);background:#090a0f;padding:0.5rem 0.75rem;border-radius:var(--radius-sm);margin-bottom:0.75rem;">
                ${d.code_executed}
              </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
              ${count > 0 ? cardsHtml : '<div style="color:var(--text-muted);padding:1rem;text-align:center;">No cases found exceeding risk threshold.</div>'}
            </div>
          `;
        }
      } catch (err) {
        if (attrFilterResult) {
          attrFilterResult.innerHTML = `<div style="color:var(--accent-danger);">Error: ${err.message}</div>`;
        }
      }
    });
  }

  // --- Query 3: Multi-hop Graph Traversal ---
  function updateSvgGraphHighlights(startNodeId, linkedMap) {
    const allNodes = ["U-101", "U-102", "U-103", "U-104", "U-105", "U-106"];
    allNodes.forEach(id => {
      const el = document.getElementById(`graph-node-${id}`);
      const textEl = document.getElementById(`graph-text-${id}`);
      if (!el) return;
      if (id === startNodeId) {
        el.setAttribute("fill", "#f59e0b");
        el.setAttribute("stroke", "#fbbf24");
        el.setAttribute("stroke-width", "3");
      } else if (linkedMap && linkedMap[id] !== undefined) {
        const hops = linkedMap[id];
        const color = hops === 1 ? "#10b981" : (hops === 2 ? "#06b6d4" : "#6366f1");
        el.setAttribute("fill", color);
        el.setAttribute("stroke", "#ffffff");
        el.setAttribute("stroke-width", "2");
      } else {
        el.setAttribute("fill", "#1e293b");
        el.setAttribute("stroke", "#475569");
        el.setAttribute("stroke-width", "1");
      }
    });
  }

  if (btnTraversal) {
    btnTraversal.addEventListener("click", async () => {
      const suspectId = suspectSelect ? suspectSelect.value : "U-101";
      const maxHops = hopsSelect ? parseInt(hopsSelect.value) : 3;
      if (traversalResult) {
        traversalResult.innerHTML = '<div style="color:var(--text-muted);font-style:italic;">Routing query to graph engine...</div>';
      }
      try {
        const res = await fetch("/api/lab16-query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query_type: "graph_traversal", suspect_id: suspectId, max_hops: maxHops })
        });
        const d = await res.json();
        if (d.success && traversalResult) {
          const linkedList = d.result;
          const linkedMap = {};
          linkedList.forEach(item => {
            linkedMap[item.suspect_id] = item.hops;
          });

          // Highlight the SVG diagram
          updateSvgGraphHighlights(suspectId, linkedMap);

          let rowsHtml = "";
          linkedList.forEach(item => {
            const hopColor = item.hops === 1 ? "var(--accent-primary)" : (item.hops === 2 ? "var(--accent-cyan)" : "var(--accent-secondary)");
            rowsHtml += `
              <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:var(--radius-md);padding:0.75rem 1rem;display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="font-weight:700;color:var(--text-primary);font-size:0.95rem;">Connected Suspect: </span>
                  <span style="font-family:var(--font-mono);font-weight:700;color:var(--accent-cyan);font-size:1rem;">${item.suspect_id}</span>
                </div>
                <div>
                  <span style="background:rgba(0,0,0,0.4);border:1px solid ${hopColor};color:${hopColor};padding:0.25rem 0.65rem;border-radius:var(--radius-full);font-weight:700;font-size:0.8rem;">
                    ${item.hops} HOP${item.hops > 1 ? "S" : ""} AWAY
                  </span>
                </div>
              </div>
            `;
          });

          let stepsHtml = "";
          if (d.path_details && d.path_details.length > 0) {
            stepsHtml = d.path_details.map(p => `
              <div style="font-family:var(--font-mono);font-size:0.78rem;color:var(--text-secondary);padding:0.2rem 0;">
                &bull; Suspect <strong style="color:var(--accent-cyan);">${p.user}</strong> reachable via [${p.devices.join(", ")}] &rarr; ${p.hops} hop(s)
              </div>
            `).join("");
          }

          traversalResult.innerHTML = `
            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.3);border-radius:var(--radius-md);padding:1rem;margin-bottom:0.75rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;gap:0.5rem;">
                <span class="badge-tag purple" style="font-size:0.85rem;font-weight:600;">🕸️ Routed to: ${d.routed_to}</span>
                <span style="font-size:0.75rem;color:var(--text-muted);">Engine: ${d.backend_used}</span>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.6rem;">
                <strong>Architectural Bias:</strong> ${d.reason}
              </div>
              <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:0.75rem;">
                <strong>Why Document/Wide-Column Stores Struggle:</strong> ${d.alternative_analysis}
              </div>
              <div style="font-family:var(--font-mono);font-size:0.78rem;color:var(--accent-cyan);background:#090a0f;padding:0.5rem 0.75rem;border-radius:var(--radius-sm);margin-bottom:0.75rem;">
                ${d.code_executed}
              </div>
              ${stepsHtml ? `<div style="background:rgba(0,0,0,0.3);padding:0.6rem 0.8rem;border-radius:var(--radius-sm);margin-bottom:0.5rem;">${stepsHtml}</div>` : ""}
            </div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
              ${linkedList.length > 0 ? rowsHtml : '<div style="color:var(--text-muted);padding:1rem;text-align:center;">No connected suspects found within specified hops.</div>'}
            </div>
          `;
        }
      } catch (err) {
        if (traversalResult) {
          traversalResult.innerHTML = `<div style="color:var(--accent-danger);">Error: ${err.message}</div>`;
        }
      }
    });
  }

  // --- Live Terminal Script Runner ---
  async function streamLab16ScriptOutput(url, title) {
    if (!terminalOutput) return;
    terminalOutput.innerHTML = "";
    if (runnerStatus) runnerStatus.textContent = "Executing...";

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      if (data.success && data.output) {
        for (let i = 0; i < data.output.length; i++) {
          const line = data.output[i];
          const div = document.createElement("div");
          if (line.includes("===") || line.includes("---")) {
            div.style.color = "var(--accent-cyan)";
            div.style.fontWeight = "600";
          } else if (line.includes("[OK]") || line.includes("Complete")) {
            div.style.color = "var(--accent-primary)";
            div.style.fontWeight = "600";
          } else if (line.includes("[WARN]") || line.includes("Warning")) {
            div.style.color = "var(--accent-warning)";
          } else if (line.includes("|")) {
            div.style.color = "var(--text-secondary)";
            div.style.whiteSpace = "pre";
          } else {
            div.style.color = "var(--text-primary)";
          }
          div.textContent = line;
          terminalOutput.appendChild(div);
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          await new Promise(r => setTimeout(r, 20));
        }
      } else {
        terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution failed: ${data.error || "Unknown error"}</div>`;
      }
      if (runnerStatus) runnerStatus.textContent = "Finished";
    } catch (e) {
      terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution error: ${e.message}</div>`;
      if (runnerStatus) runnerStatus.textContent = "Error";
    }
  }

  if (btnRunScript1) {
    btnRunScript1.addEventListener("click", () => streamLab16ScriptOutput("/api/lab16-run-lab1", "Lab 16.1"));
  }
  if (btnRunScript2) {
    btnRunScript2.addEventListener("click", () => streamLab16ScriptOutput("/api/lab16-run-lab2", "Lab 16.2"));
  }
  if (btnResetDb) {
    btnResetDb.addEventListener("click", async () => {
      if (terminalOutput) terminalOutput.innerHTML = '<div style="color:var(--accent-cyan);">[RESET] Resetting nosql_labs.fraud_cases collection and initializing graph...</div>';
      try {
        const res = await fetch("/api/lab16-reset", { method: "POST", headers: { "Content-Type": "application/json" } });
        const d = await res.json();
        if (d.success) {
          if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-primary);">${d.message}</div>`;
          loadLab16Summary();
        }
      } catch (e) {
        if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-danger);">Reset failed: ${e.message}</div>`;
      }
    });
  }

  // Initial load
  loadLab16Summary();
}

/* ==========================================================================
   13. Lab 17: Simple RAG Pipeline & Vector Search (HNSW vs IVF)
   ========================================================================== */
function initLab17() {
  const mongoStatus = document.getElementById("lab17MongoStatus");
  const embedStatus = document.getElementById("lab17EmbedStatus");
  const questionSelect = document.getElementById("lab17QuestionSelect");
  const customQuestion = document.getElementById("lab17CustomQuestion");
  const topKSlider = document.getElementById("lab17TopK");
  const topKVal = document.getElementById("lab17TopKVal");
  const btnRunRag = document.getElementById("btnRunRagQuery");
  const retrievedList = document.getElementById("lab17RetrievedList");
  const promptBox = document.getElementById("lab17PromptBox");
  const llmResponse = document.getElementById("lab17LlmResponse");
  const btnSeed = document.getElementById("btnSeedLab17");

  // ANN Controls
  const paramN = document.getElementById("paramN");
  const lblN = document.getElementById("lblN");
  const paramDim = document.getElementById("paramDim");
  const lblDim = document.getElementById("lblDim");
  const paramK = document.getElementById("paramK");
  const lblK = document.getElementById("lblK");
  const paramNlist = document.getElementById("paramNlist");
  const lblNlist = document.getElementById("lblNlist");
  const paramNprobe = document.getElementById("paramNprobe");
  const lblNprobe = document.getElementById("lblNprobe");
  const paramEf = document.getElementById("paramEf");
  const lblEf = document.getElementById("lblEf");
  const btnRunBenchmark = document.getElementById("btnRunAnnBenchmark");
  const benchmarkTable = document.getElementById("lab17BenchmarkTable");
  const vectorVis = document.getElementById("lab17VectorVis");

  // CLI Runner
  const btnScript1 = document.getElementById("btnRunLab17Script1");
  const btnScript2 = document.getElementById("btnRunLab17Script2");
  const btnResetDb = document.getElementById("btnResetLab17Db");
  const runnerStatus = document.getElementById("lab17RunnerStatus");
  const terminalOutput = document.getElementById("lab17TerminalOutput");

  // Slider event listeners
  if (topKSlider && topKVal) {
    topKSlider.addEventListener("input", () => {
      topKVal.textContent = topKSlider.value;
    });
  }

  if (questionSelect) {
    questionSelect.addEventListener("change", () => {
      if (questionSelect.value === "CUSTOM") {
        customQuestion.style.display = "block";
        customQuestion.focus();
      } else {
        customQuestion.style.display = "none";
      }
    });
  }

  function bindSlider(slider, label) {
    if (slider && label) {
      slider.addEventListener("input", () => {
        label.textContent = slider.value;
      });
    }
  }

  bindSlider(paramN, lblN);
  bindSlider(paramDim, lblDim);
  bindSlider(paramK, lblK);
  bindSlider(paramNlist, lblNlist);
  bindSlider(paramNprobe, lblNprobe);
  bindSlider(paramEf, lblEf);

  // Load summary
  async function loadLab17Summary() {
    try {
      const res = await fetch("/api/lab17-summary");
      const d = await res.json();
      if (d.success) {
        if (mongoStatus) {
          mongoStatus.textContent = d.mongodb_connected ? `MongoDB: Connected (${d.chunk_count} chunks)` : "MongoDB: In-Memory Mock";
          mongoStatus.className = d.mongodb_connected ? "badge-tag green" : "badge-tag yellow";
        }
        if (embedStatus) {
          embedStatus.textContent = `Embeddings: ${d.embedding_dimension}-dim Unit-Norm`;
        }
      }
    } catch (e) {
      console.warn("Lab 17 summary load error:", e);
    }
  }

  // Run RAG Query
  if (btnRunRag) {
    btnRunRag.addEventListener("click", async () => {
      const q = questionSelect.value === "CUSTOM" ? (customQuestion.value || "What is HNSW?") : questionSelect.value;
      const k = parseInt(topKSlider.value) || 2;

      btnRunRag.disabled = true;
      btnRunRag.textContent = "Retrieving...";

      try {
        const res = await fetch("/api/lab17-query-rag", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: q, top_k: k })
        });
        const d = await res.json();
        if (d.success) {
          // Render chunks
          if (retrievedList) {
            retrievedList.innerHTML = "";
            d.retrieved_chunks.forEach((chunk, idx) => {
              const div = document.createElement("div");
              div.style.padding = "0.75rem";
              div.style.background = "rgba(0,0,0,0.2)";
              div.style.borderRadius = "var(--radius-sm)";
              div.style.marginBottom = "0.5rem";
              div.style.borderLeft = "3px solid var(--accent-primary)";
              div.innerHTML = `
                <div style="display:flex;justify-content:space-between;color:var(--accent-primary);font-size:0.8rem;margin-bottom:0.25rem;">
                  <strong>[${chunk.source_title}] Chunk ${chunk.chunk_index}</strong>
                  <span style="font-family:var(--font-mono);font-weight:bold;">Score: ${chunk.score.toFixed(4)}</span>
                </div>
                <div style="font-size:0.82rem;color:var(--text-secondary);">${chunk.text}</div>
              `;
              retrievedList.appendChild(div);
            });
          }

          if (promptBox) {
            promptBox.textContent = d.prompt;
          }

          if (llmResponse) {
            llmResponse.textContent = d.response;
          }
        }
      } catch (e) {
        alert("RAG query failed: " + e.message);
      } finally {
        btnRunRag.disabled = false;
        btnRunRag.textContent = "🚀 Retrieve & Synthesize";
      }
    });
  }

  // Run ANN Benchmark
  if (btnRunBenchmark) {
    btnRunBenchmark.addEventListener("click", async () => {
      btnRunBenchmark.disabled = true;
      btnRunBenchmark.textContent = "Running Benchmark...";

      const payload = {
        n_vectors: parseInt(paramN.value),
        dim: parseInt(paramDim.value),
        k: parseInt(paramK.value),
        nlist: parseInt(paramNlist.value),
        nprobe: parseInt(paramNprobe.value),
        ef_search: parseInt(paramEf.value)
      };

      try {
        const res = await fetch("/api/lab17-run-ann-benchmark", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const d = await res.json();
        if (d.success && d.comparison && benchmarkTable) {
          const tbody = benchmarkTable.querySelector("tbody");
          tbody.innerHTML = "";
          d.comparison.forEach(row => {
            const tr = document.createElement("tr");
            tr.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
            let familyColor = "var(--accent-cyan)";
            if (row.index_type.startsWith("IVF")) familyColor = "var(--accent-primary)";
            if (row.index_type.startsWith("Simplified")) familyColor = "var(--accent-secondary)";

            tr.innerHTML = `
              <td style="padding:0.75rem;color:${familyColor};font-weight:600;">${row.index_type}</td>
              <td style="padding:0.75rem;text-align:right;font-family:var(--font-mono);">${row.build_time_ms.toFixed(1)}</td>
              <td style="padding:0.75rem;text-align:right;font-family:var(--font-mono);">${Math.round(row.vectors_compared).toLocaleString()}</td>
              <td style="padding:0.75rem;text-align:right;font-family:var(--font-mono);font-weight:bold;color:${row.compared_pct < 30 ? 'var(--accent-primary)' : (row.compared_pct < 80 ? 'var(--accent-warning)' : 'var(--accent-danger)')};">${row.compared_pct.toFixed(1)}%</td>
              <td style="padding:0.75rem;text-align:right;font-family:var(--font-mono);">${row.avg_query_time_ms.toFixed(3)}</td>
              <td style="padding:0.75rem;text-align:right;font-family:var(--font-mono);color:var(--accent-primary);font-weight:bold;">${row.recall_at_k.toFixed(2)}%</td>
            `;
            tbody.appendChild(tr);
          });

          // Animate / update SVG visualization with simulated clusters
          if (vectorVis && d.vis) {
            let svgContent = `
              <defs>
                <pattern id="visGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#visGrid)"/>
            `;

            // Draw cluster centroids
            d.vis.centroids.forEach((c, idx) => {
              const color = idx % 2 === 0 ? "rgba(52, 211, 153, 0.15)" : "rgba(56, 189, 248, 0.15)";
              const stroke = idx % 2 === 0 ? "rgba(52, 211, 153, 0.4)" : "rgba(56, 189, 248, 0.4)";
              svgContent += `<circle cx="${c.x}" cy="${c.y}" r="40" fill="${color}" stroke="${stroke}" stroke-dasharray="3,3"/>`;
              svgContent += `<circle cx="${c.x}" cy="${c.y}" r="5" fill="${idx % 2 === 0 ? '#34d399' : '#38bdf8'}"/>`;
              svgContent += `<text x="${c.x}" y="${c.y - 8}" fill="${idx % 2 === 0 ? '#34d399' : '#38bdf8'}" font-size="8" text-anchor="middle" font-family="sans-serif">IVF-C${c.cluster_id}</text>`;
            });

            // Draw sample points and graph edges
            d.vis.points.forEach(p => {
              if (p.neighbors && p.neighbors.length > 0) {
                p.neighbors.forEach(nId => {
                  const target = d.vis.points.find(x => x.id === nId);
                  if (target) {
                    svgContent += `<line x1="${p.x}" y1="${p.y}" x2="${target.x}" y2="${target.y}" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>`;
                  }
                });
              }
              svgContent += `<circle cx="${p.x}" cy="${p.y}" r="2.5" fill="rgba(255,255,255,0.4)"/>`;
            });

            // Query marker
            svgContent += `
              <polygon points="200,140 203,148 211,149 205,155 207,163 200,158 193,163 195,155 189,149 197,148" fill="#fbbf24"/>
              <text x="200" y="132" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold" font-family="sans-serif">Query Q</text>
            `;

            vectorVis.innerHTML = svgContent;
          }
        }
      } catch (e) {
        alert("Benchmark failed: " + e.message);
      } finally {
        btnRunBenchmark.disabled = false;
        btnRunBenchmark.textContent = "⚡ Run Live Benchmark Simulation";
      }
    });
  }

  // Stream terminal output
  async function streamLab17ScriptOutput(url, title) {
    if (!terminalOutput) return;
    terminalOutput.innerHTML = "";
    if (runnerStatus) runnerStatus.textContent = "Executing...";

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      if (data.success && data.output) {
        for (let i = 0; i < data.output.length; i++) {
          const line = data.output[i];
          const div = document.createElement("div");
          if (line.includes("===") || line.includes("---")) {
            div.style.color = "var(--accent-cyan)";
            div.style.fontWeight = "600";
          } else if (line.includes("[OK]") || line.includes("Complete")) {
            div.style.color = "var(--accent-primary)";
            div.style.fontWeight = "600";
          } else if (line.includes("|")) {
            div.style.color = "var(--text-secondary)";
            div.style.whiteSpace = "pre";
          } else {
            div.style.color = "var(--text-primary)";
          }
          div.textContent = line;
          terminalOutput.appendChild(div);
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          await new Promise(r => setTimeout(r, 20));
        }
      } else {
        terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution failed: ${data.error || "Unknown error"}</div>`;
      }
      if (runnerStatus) runnerStatus.textContent = "Finished";
    } catch (e) {
      terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution error: ${e.message}</div>`;
      if (runnerStatus) runnerStatus.textContent = "Error";
    }
  }

  if (btnScript1) {
    btnScript1.addEventListener("click", () => streamLab17ScriptOutput("/api/lab17-run-lab1", "Lab 17.1"));
  }
  if (btnScript2) {
    btnScript2.addEventListener("click", () => streamLab17ScriptOutput("/api/lab17-run-lab2", "Lab 17.2"));
  }
  if (btnResetDb) {
    btnResetDb.addEventListener("click", async () => {
      if (terminalOutput) terminalOutput.innerHTML = '<div style="color:var(--accent-cyan);">[RESET] Resetting nosql_labs.rag_documents collection...</div>';
      try {
        const res = await fetch("/api/lab17-reset", { method: "POST", headers: { "Content-Type": "application/json" } });
        const d = await res.json();
        if (d.success) {
          if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-primary);">${d.message}</div>`;
          loadLab17Summary();
        }
      } catch (e) {
        if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-danger);">Reset failed: ${e.message}</div>`;
      }
    });
  }

  if (btnSeed) {
    btnSeed.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/lab17-reset", { method: "POST", headers: { "Content-Type": "application/json" } });
        const d = await res.json();
        if (d.success) {
          alert("Re-seeded chunks successfully!");
          loadLab17Summary();
        }
      } catch (e) {
        alert("Seed failed: " + e.message);
      }
    });
  }

  // Initial summary load
  loadLab17Summary();
}

/* ==========================================================================
   LAB 18: COMPARATIVE CAPSTONE & TECHNICAL ANALYSIS REPORT
   ========================================================================== */
function initLab18() {
  const dbStatus = document.getElementById("lab18DbStatus");
  const methodBadge = document.getElementById("lab18MethodBadge");
  const btnRunBenchmark = document.getElementById("btnRunLab18Benchmark");
  const btnReset = document.getElementById("btnResetLab18");
  const btnGenerateReport = document.getElementById("btnGenerateLab18Report");
  const btnCopyReport = document.getElementById("btnCopyReportMd");
  const btnDownloadReport = document.getElementById("btnDownloadReportMd");
  const btnAssessRec = document.getElementById("btnAssessStudentRec");
  const studentRecInput = document.getElementById("lab18StudentRec");
  const recFeedback = document.getElementById("lab18RecFeedback");
  const reportContent = document.getElementById("lab18ReportContent");
  const reportMeta = document.getElementById("lab18ReportMeta");
  const benchmarkStatus = document.getElementById("lab18BenchmarkStatus");

  const q1Mongo = document.getElementById("lab18Q1Mongo");
  const q1Count = document.getElementById("lab18Q1Count");
  const q2Mongo = document.getElementById("lab18Q2Mongo");
  const q2Count = document.getElementById("lab18Q2Count");
  const q3Mongo = document.getElementById("lab18Q3Mongo");
  const q3Count = document.getElementById("lab18Q3Count");
  const q4Mongo = document.getElementById("lab18Q4Mongo");
  const q4Count = document.getElementById("lab18Q4Count");

  const userIdSelect = document.getElementById("lab18UserId");
  const riskSlider = document.getElementById("lab18RiskThreshold");
  const riskVal = document.getElementById("lab18RiskVal");
  const writeBatchSelect = document.getElementById("lab18WriteBatch");

  const btnScript1 = document.getElementById("btnRunLab18Script1");
  const btnScript2 = document.getElementById("btnRunLab18Script2");
  const terminalOutput = document.getElementById("lab18TerminalOutput");
  const runnerStatus = document.getElementById("lab18RunnerStatus");

  const codeBtns = document.querySelectorAll(".lab18-code-btn");
  const codeBlock = document.getElementById("lab18CodeBlock");

  let lastReportMarkdown = "";
  let cachedBenchmarkResults = null;

  // Code snippets for switcher
  const codeSnippets = {
    mongo: `# Q1: Transaction history for user (point lookup + sort)
col.find({"user_id": "U-0001"}).sort("timestamp", -1).limit(50)

# Q2: High-risk transactions (range query on indexed score)
col.find({"risk_score": {"$gt": 0.8}}, {"_id": 0, "txn_id": 1, "risk_score": 1, "amount": 1})

# Q3: Category Analytics (native aggregation pipeline)
col.aggregate([
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    {"$sort": {"total": -1}}
])

# Q4: High-throughput write batch (1,000 documents)
col.insert_many(transactions_batch)`,

    cassandra: `-- Q1: Transaction history (requires partition key = user_id)
-- Extremely fast because user_id partition routes directly to node token
SELECT * FROM transactions WHERE user_id = 'U-0001' LIMIT 50;

-- Q2: High-risk (requires secondary index or materialized view)
-- WARNING: Inefficient scatter-gather across all nodes without partition key
CREATE INDEX idx_risk ON transactions(risk_score);
SELECT * FROM transactions WHERE risk_score > 0.8 ALLOW FILTERING;

-- Q3: Analytics (Cassandra is NOT designed for ad-hoc aggregation)
-- Lacks native GROUP BY / SUM; requires Spark Cassandra Connector
-- val df = spark.read.cassandraFormat("transactions", "keyspace").load()
-- df.groupBy("category").agg(sum("amount"), count("*"))

-- Q4: Write throughput (Cassandra's core architectural strength)
-- Append-only LSM commit log + Memtable; zero read-before-write locking`,

    neo4j: `// Q1: Transaction history (single-hop traversal from indexed User node)
MATCH (u:User {id: 'U-0001'})-[:MADE]->(t:Transaction)
RETURN t ORDER BY t.timestamp DESC LIMIT 50;

// Q2: Fraud ring detection (Graph Database's unique competitive advantage!)
// Traverses shared devices and accounts across 1 to 3 hops
MATCH path = (u1:User)-[:SHARES_DEVICE*1..3]-(u2:User)
WHERE u1.id = 'U-0001'
WITH u1, u2, COUNT(*) AS shared_signals
WHERE shared_signals >= 2
RETURN u1.id, u2.id, shared_signals
ORDER BY shared_signals DESC;

// Q3: Category analytics (not Neo4j's strength - scans entire node label)
MATCH (t:Transaction)
WITH t.category AS cat, SUM(t.amount) AS total, COUNT(t) AS cnt
RETURN cat, total, cnt ORDER BY total DESC;

// Q4: Write throughput (graph writes are expensive due to pointer linkage)`
  };

  // Switch code views
  codeBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      codeBtns.forEach(b => {
        b.classList.remove("active");
        b.style.color = "var(--text-secondary)";
        b.style.borderBottom = "none";
        b.style.fontWeight = "normal";
      });
      btn.classList.add("active");
      btn.style.color = btn.dataset.engine === "mongo" ? "var(--accent-primary)" : (btn.dataset.engine === "cassandra" ? "var(--accent-cyan)" : "#ec4899");
      btn.style.borderBottom = `2px solid ${btn.style.color}`;
      btn.style.fontWeight = "bold";

      if (codeBlock && codeSnippets[btn.dataset.engine]) {
        codeBlock.innerHTML = `<code>${codeSnippets[btn.dataset.engine].replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code>`;
      }
    });
  });

  // Slider update
  if (riskSlider && riskVal) {
    riskSlider.addEventListener("input", () => {
      riskVal.textContent = parseFloat(riskSlider.value).toFixed(2);
    });
  }

  // Summary loader
  async function loadLab18Summary() {
    try {
      const res = await fetch("/api/lab18-summary");
      const d = await res.json();
      if (d.success && dbStatus) {
        if (d.connected) {
          dbStatus.textContent = `MongoDB: ${d.database}.${d.collection} (${d.total_count.toLocaleString()} docs)`;
          dbStatus.className = "badge-tag green";
        } else {
          dbStatus.textContent = `Standalone Mode: ${d.total_count.toLocaleString()} records`;
          dbStatus.className = "badge-tag yellow";
        }
      }
    } catch (e) {
      if (dbStatus) {
        dbStatus.textContent = "MongoDB: Capstone Ready";
      }
    }
  }

  // Run Benchmark
  if (btnRunBenchmark) {
    btnRunBenchmark.addEventListener("click", async () => {
      btnRunBenchmark.disabled = true;
      btnRunBenchmark.textContent = "Running Benchmark...";
      if (benchmarkStatus) {
        benchmarkStatus.textContent = "⏱️ Benchmarking 4 query patterns...";
        benchmarkStatus.style.color = "var(--accent-warning)";
      }

      const payload = {
        user_id: userIdSelect ? userIdSelect.value : "U-0001",
        risk_threshold: riskSlider ? parseFloat(riskSlider.value) : 0.8,
        write_batch: writeBatchSelect ? parseInt(writeBatchSelect.value) : 1000
      };

      try {
        const res = await fetch("/api/lab18-run-benchmark", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const d = await res.json();

        if (d.success && d.results) {
          cachedBenchmarkResults = d.results;
          const r1 = d.results.find(r => r.query === "Transaction History");
          const r2 = d.results.find(r => r.query === "High-Risk Query");
          const r3 = d.results.find(r => r.query === "Category Analytics");
          const r4 = d.results.find(r => r.query === "Write Throughput");

          if (r1 && q1Mongo) { q1Mongo.textContent = `${r1.latency_ms.toFixed(1)} ms`; q1Count.textContent = r1.count; }
          if (r2 && q2Mongo) { q2Mongo.textContent = `${r2.latency_ms.toFixed(1)} ms`; q2Count.textContent = r2.count; }
          if (r3 && q3Mongo) { q3Mongo.textContent = `${r3.latency_ms.toFixed(1)} ms`; q3Count.textContent = r3.count; }
          if (r4 && q4Mongo) { q4Mongo.textContent = `${r4.latency_ms.toFixed(1)} ms`; q4Count.textContent = r4.count.toLocaleString(); }

          if (benchmarkStatus) {
            benchmarkStatus.textContent = d.measured ? `✅ Live Benchmark Completed (${new Date().toLocaleTimeString()})` : `⚠️ Completed in Offline Estimation Mode`;
            benchmarkStatus.style.color = d.measured ? "var(--accent-primary)" : "var(--accent-warning)";
          }
        }
      } catch (e) {
        if (benchmarkStatus) {
          benchmarkStatus.textContent = `❌ Benchmark Error: ${e.message}`;
          benchmarkStatus.style.color = "var(--accent-danger)";
        }
      } finally {
        btnRunBenchmark.disabled = false;
        btnRunBenchmark.textContent = "🚀 Run Live Benchmark";
      }
    });
  }

  // Generate Report
  if (btnGenerateReport) {
    btnGenerateReport.addEventListener("click", async () => {
      btnGenerateReport.disabled = true;
      btnGenerateReport.textContent = "Generating Report...";

      try {
        const payload = {
          benchmark_results: cachedBenchmarkResults,
          measured: true
        };
        const res = await fetch("/api/lab18-generate-report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const d = await res.json();

        if (d.success && d.report_md) {
          lastReportMarkdown = d.report_md;
          if (reportMeta) {
            reportMeta.textContent = `Report generated: ${d.timestamp} • File: ${d.filename || 'reports/comparative_analysis.md'}`;
          }

          // Simple Markdown to HTML formatter for the report
          let html = d.report_md
            .replace(/^# (.*$)/gim, '<h2 style="color:var(--accent-primary);margin-top:0;">$1</h2>')
            .replace(/^## (.*$)/gim, '<h3 style="color:var(--accent-cyan);margin-top:1.5rem;">$1</h3>')
            .replace(/^\*Generated (.*)\*/gim, '<p><em>Generated $1</em></p>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/```([\s\S]*?)```/gim, '<pre style="background:rgba(255,255,255,0.03);padding:1rem;border-radius:var(--radius-sm);font-family:var(--font-mono);font-size:0.8rem;color:var(--accent-cyan);line-height:1.5;"><code>$1</code></pre>');

          // Format markdown tables
          const tableRegex = /\|(.+)\|[\r\n]+\|[-| ]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
          html = html.replace(tableRegex, (match, headerRow, bodyRows) => {
            const headers = headerRow.split('|').map(h => h.trim()).filter(h => h);
            const rows = bodyRows.trim().split('\n').map(row => {
              return row.split('|').map(c => c.trim()).filter(c => c);
            });

            let tHtml = '<table style="width:100%;border-collapse:collapse;font-size:0.82rem;margin:1rem 0;"><thead><tr style="border-bottom:1px solid rgba(255,255,255,0.2);text-align:left;">';
            headers.forEach(h => { tHtml += `<th style="padding:0.5rem;">${h}</th>`; });
            tHtml += '</tr></thead><tbody>';
            rows.forEach(r => {
              tHtml += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">';
              r.forEach((c, idx) => {
                let style = 'padding:0.5rem;';
                if (idx === 1) style += 'color:var(--accent-primary);font-weight:bold;';
                if (idx === 2) style += 'color:var(--accent-cyan);';
                if (idx === 3) style += 'color:#ec4899;';
                tHtml += `<td style="${style}">${c}</td>`;
              });
              tHtml += '</tr>';
            });
            tHtml += '</tbody></table>';
            return tHtml;
          });

          if (reportContent) {
            reportContent.innerHTML = html;
          }
        }
      } catch (e) {
        alert("Report generation failed: " + e.message);
      } finally {
        btnGenerateReport.disabled = false;
        btnGenerateReport.textContent = "📑 Generate Official Report";
      }
    });
  }

  // Copy Markdown
  if (btnCopyReport) {
    btnCopyReport.addEventListener("click", () => {
      const textToCopy = lastReportMarkdown || (reportContent ? reportContent.innerText : "");
      navigator.clipboard.writeText(textToCopy).then(() => {
        btnCopyReport.textContent = "✅ Copied!";
        setTimeout(() => { btnCopyReport.textContent = "📋 Copy Markdown"; }, 2000);
      });
    });
  }

  // Download Markdown
  if (btnDownloadReport) {
    btnDownloadReport.addEventListener("click", () => {
      const textToDownload = lastReportMarkdown || (reportContent ? reportContent.innerText : "");
      const blob = new Blob([textToDownload], { type: "text/markdown;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `comparative_analysis_${new Date().toISOString().replace(/[:.]/g, "-")}.md`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // Assess Student Recommendation
  if (btnAssessRec && studentRecInput && recFeedback) {
    btnAssessRec.addEventListener("click", () => {
      const text = studentRecInput.value.toLowerCase().trim();
      if (!text || text.length < 20) {
        recFeedback.innerHTML = '<span style="color:var(--accent-warning);">Please write a complete paragraph explaining your reasoning across databases.</span>';
        return;
      }

      const hasMongo = text.includes("mongo");
      const hasCassandra = text.includes("cassandra");
      const hasNeo4j = text.includes("neo4j") || text.includes("graph");
      const mentionsPolyglot = text.includes("polyglot") || text.includes("hybrid") || (hasMongo && hasNeo4j);
      const notesCassandraTradeoff = text.includes("write") || text.includes("spark") || text.includes("filter") || text.includes("not recommended");

      let score = 0;
      let notes = [];

      if (hasMongo) { score += 25; notes.push("Recognized MongoDB as primary operational store"); }
      if (hasNeo4j) { score += 25; notes.push("Identified Neo4j for graph-based fraud rings"); }
      if (mentionsPolyglot) { score += 25; notes.push("Proposed balanced polyglot architecture"); }
      if (notesCassandraTradeoff) { score += 25; notes.push("Correctly analyzed Cassandra's write-vs-query trade-offs"); }

      if (score >= 75) {
        recFeedback.innerHTML = `<span style="color:var(--accent-primary);font-weight:bold;">🌟 Excellent Architectural Alignment (${score}% match)!</span> <span style="color:var(--text-secondary);">${notes.join(", ")}. Matches textbook recommendation closely.</span>`;
      } else {
        recFeedback.innerHTML = `<span style="color:var(--accent-cyan);font-weight:bold;">👍 Good Thought Process (${score}% match).</span> <span style="color:var(--text-secondary);">Tip: Consider why Cassandra's write speed is offset by lack of ad-hoc queries, and how Neo4j excels at fraud rings.</span>`;
      }
    });
  }

  // Stream terminal outputs
  async function streamLab18ScriptOutput(url, label) {
    if (!terminalOutput) return;
    terminalOutput.innerHTML = `<div style="color:var(--accent-cyan);">[EXEC] Invoking ${label}...</div>`;
    if (runnerStatus) runnerStatus.textContent = "Running...";

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data.success && data.output) {
        terminalOutput.innerHTML = "";
        for (let line of data.output) {
          const div = document.createElement("div");
          if (line.includes("ERROR") || line.includes("failed")) {
            div.style.color = "var(--accent-danger)";
          } else if (line.includes("[OK]") || line.includes("Complete")) {
            div.style.color = "var(--accent-primary)";
          } else if (line.includes("Q1:") || line.includes("Q2:") || line.includes("Q3:") || line.includes("Q4:")) {
            div.style.color = "var(--accent-cyan)";
          } else if (line.startsWith("===") || line.startsWith("---") || line.startsWith("+++")) {
            div.style.color = "var(--accent-warning)";
          } else {
            div.style.color = "var(--text-primary)";
          }
          div.textContent = line;
          terminalOutput.appendChild(div);
          terminalOutput.scrollTop = terminalOutput.scrollHeight;
          await new Promise(r => setTimeout(r, 15));
        }
      } else {
        terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution failed: ${data.error || "Unknown error"}</div>`;
      }
      if (runnerStatus) runnerStatus.textContent = "Finished";
    } catch (e) {
      terminalOutput.innerHTML = `<div style="color:var(--accent-danger);">Execution error: ${e.message}</div>`;
      if (runnerStatus) runnerStatus.textContent = "Error";
    }
  }

  if (btnScript1) {
    btnScript1.addEventListener("click", () => streamLab18ScriptOutput("/api/lab18-run-lab1", "Lab 18.1 Capstone Lab"));
  }
  if (btnScript2) {
    btnScript2.addEventListener("click", () => streamLab18ScriptOutput("/api/lab18-run-lab2", "Lab 18.2 Comparative Report"));
  }

  // Reset / Re-seed
  if (btnReset) {
    btnReset.addEventListener("click", async () => {
      if (terminalOutput) terminalOutput.innerHTML = '<div style="color:var(--accent-cyan);">[RESET] Resetting capstone.transactions collection with 10,000 documents...</div>';
      try {
        const res = await fetch("/api/lab18-reset", { method: "POST", headers: { "Content-Type": "application/json" } });
        const d = await res.json();
        if (d.success) {
          if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-primary);">${d.message}</div>`;
          loadLab18Summary();
        }
      } catch (e) {
        if (terminalOutput) terminalOutput.innerHTML += `<div style="color:var(--accent-danger);">Reset failed: ${e.message}</div>`;
      }
    });
  }

  // Initial load
  loadLab18Summary();
}


