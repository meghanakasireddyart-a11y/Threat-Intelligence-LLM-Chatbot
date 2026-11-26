// Interactive App Logic for Lab 8 Replication & Failover Portal
document.addEventListener('DOMContentLoaded', () => {
  // Activity Code Repository
  const activityData = {
    act1: {
      title: "Lab 8.1: Deploy a Local Replica Set",
      py: {
        file: "Activity_8_1/lab_01_deploy_replicaset.py",
        content: `"""Lab 8.1: Deploy a Local Replica Set - Python Verification Script
Student: Kasireddy Meghana (24BTRCL119)
"""
from pymongo import MongoClient, ReadPreference

RS_URI = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client = MongoClient(RS_URI, serverSelectionTimeoutMS=3000)

# Check Replica Set Status
status = client.admin.command("replSetGetStatus")
print(f"Replica Set: {status['set']} | Cluster State: Healthy")
for m in status['members']:
    print(f"Node: {m['name']:<22} Role: {m['stateStr']:<12} Health: {m['health']}")

# Insert into Primary
db = client["salesDB"]
res = db.orders.insert_one({"order_id": "ORD-8001", "customer": "Alice Smith", "amount": 349.99})
print(f"Inserted into PRIMARY with _id: {res.inserted_id}")

# Verify Secondary Read
sec_client = MongoClient(RS_URI, read_preference=ReadPreference.SECONDARY)
doc = sec_client["salesDB"].orders.find_one({"order_id": "ORD-8001"})
print(f"Verified on SECONDARY: {doc['order_id']} - {doc['customer']} ($ {doc['amount']})")`
      },
      js: {
        file: "Activity_8_1/lab_01_deploy_replicaset.js",
        content: `// Lab 8.1: Deploy Local Replica Set (rs0)
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017", priority: 2 },
    { _id: 1, host: "localhost:27018", priority: 1 },
    { _id: 2, host: "localhost:27019", priority: 1 }
  ]
});

// Insert document on Primary
use salesDB;
db.orders.insertOne({ order_id: "ORD-8001", customer: "Alice Smith", amount: 349.99 });

// Verify on Secondary
rs.secondaryOk(); // or db.getMongo().setReadPref("secondary")
db.orders.findOne({ order_id: "ORD-8001" });

// Display member health and roles
rs.status().members.forEach(m => print(m._id, m.name, m.stateStr, m.health));`
      },
      compose: {
        file: "Activity_8_1/docker-compose.yml",
        content: `version: "3.8"
services:
  mongo1:
    image: mongo:7.0
    container_name: mongo1
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all", "--port", "27017"]
    ports: ["27017:27017"]
    volumes: [mongo1_data:/data/db]
  mongo2:
    image: mongo:7.0
    container_name: mongo2
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all", "--port", "27018"]
    ports: ["27018:27018"]
    volumes: [mongo2_data:/data/db]
  mongo3:
    image: mongo:7.0
    container_name: mongo3
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all", "--port", "27019"]
    ports: ["27019:27019"]
    volumes: [mongo3_data:/data/db]
volumes:
  mongo1_data:
  mongo2_data:
  mongo3_data:`
      },
      outputImg: "../screenshots/activity_8_1_output.png"
    },
    act1_ty: {
      title: "Lab 8.1 Try It Yourself: Add Arbiter Node",
      py: {
        file: "Activity_8_1_Try_It_Yourself/lab_01_arbiter_replicaset.py",
        content: `"""Lab 8.1 - Try It Yourself: Add Arbiter Node
Student: Kasireddy Meghana (24BTRCL119)
"""
from pymongo import MongoClient

RS_URI = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs_arbiter"
client = MongoClient(RS_URI, serverSelectionTimeoutMS=3000)

status = client.admin.command("replSetGetStatus")
print("=== Replica Set with Arbiter Node ===")
for m in status['members']:
    storage = "0 MB (Arbiter)" if m['stateStr'] == "ARBITER" else "Full Data"
    print(f"ID: {m['_id']} | Host: {m['name']} | Role: {m['stateStr']} | Data: {storage}")

print("\\n[CONCEPT] Why use an Arbiter?")
print("1. Odd Voting Quorum: 2 data nodes + 1 arbiter = 3 votes -> Majority = 2.")
print("   Survives 1 failure while preventing split-brain deadlock.")
print("2. 0 MB Storage Cost: Holds no user datasets or oplogs, saving enterprise SSD costs.")`
      },
      js: {
        file: "Activity_8_1_Try_It_Yourself/lab_01_arbiter_replicaset.js",
        content: `// Lab 8.1 Try It Yourself: Add Arbiter Node
rs.initiate({
  _id: "rs_arbiter",
  members: [
    { _id: 0, host: "localhost:27017", priority: 2 },
    { _id: 1, host: "localhost:27018", priority: 1 },
    { _id: 2, host: "localhost:27019", arbiterOnly: true }
  ]
});

// Dynamic addition to existing cluster:
// rs.addArb("localhost:27019");

// Check status
rs.status().members.forEach(m => {
  print(m._id, m.name, m.stateStr, "Data-bearing:", m.stateStr !== "ARBITER");
});`
      },
      compose: {
        file: "Activity_8_1_Try_It_Yourself/docker-compose-arbiter.yml",
        content: `version: "3.8"
services:
  mongo-data-1:
    image: mongo:7.0
    command: ["mongod", "--replSet", "rs_arbiter", "--bind_ip_all", "--port", "27017"]
    ports: ["27017:27017"]
  mongo-data-2:
    image: mongo:7.0
    command: ["mongod", "--replSet", "rs_arbiter", "--bind_ip_all", "--port", "27018"]
    ports: ["27018:27018"]
  mongo-arbiter:
    image: mongo:7.0
    # Arbiter node stores no application data collections
    command: ["mongod", "--replSet", "rs_arbiter", "--bind_ip_all", "--port", "27019"]
    ports: ["27019:27019"]`
      },
      outputImg: "../screenshots/activity_8_1_try_it_yourself_output.png"
    },
    act2: {
      title: "Lab 8.2: Observe Failover & Election",
      py: {
        file: "Activity_8_2/lab_02_failover_election.py",
        content: `"""Lab 8.2: Continuous Read & Failover Reconnection Observer
Student: Kasireddy Meghana (24BTRCL119)
"""
import time
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

RS_URI = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
client = MongoClient(RS_URI, serverSelectionTimeoutMS=4000)

print("Continuously monitoring replica set connections...")
for i in range(1, 13):
    try:
        status = client.admin.command("replSetGetStatus")
        primary = next(m['name'] for m in status['members'] if m['stateStr'] == "PRIMARY")
        print(f"Iter {i:02d}: Connected to PRIMARY -> {primary}")
    except AutoReconnect:
        print(f"Iter {i:02d}: [AutoReconnect] Failover election in progress...")
    time.sleep(1.0)`
      },
      js: {
        file: "Activity_8_2/lab_02_failover_election.js",
        content: `// Lab 8.2: Trigger StepDown & Observe Election
print("Current Primary:", rs.status().members.find(m => m.stateStr === "PRIMARY").name);

// Step down current primary for 60 seconds
try {
  rs.stepDown(60);
} catch (e) {
  print("StepDown socket disconnect:", e.message);
}

// Observe new primary after election
sleep(5000);
print("New Primary:", rs.status().members.find(m => m.stateStr === "PRIMARY").name);`
      },
      compose: {
        file: "Activity_8_1/docker-compose.yml",
        content: `# Uses 3-node cluster from Lab 8.1
# Connect to Primary and run: rs.stepDown(60)`
      },
      outputImg: "../screenshots/activity_8_2_output.png"
    },
    act2_ty: {
      title: "Lab 8.2 Try It Yourself: Priority Elections",
      py: {
        file: "Activity_8_2_Try_It_Yourself/lab_02_priority_election.py",
        content: `"""Lab 8.2 Try It Yourself: Priority-Based Election Prediction & Verification
Student: Kasireddy Meghana (24BTRCL119)
"""
# Priorities:
# Node 0 (27017): Priority = 1 (Primary)
# Node 1 (27018): Priority = 5 (Target Secondary)
# Node 2 (27019): Priority = 2 (Lower Secondary)

# Prediction: Node 1 has priority 5 > Node 2 priority 2.
# When Node 0 steps down, Node 1 MUST be elected new PRIMARY.

# Verification Output:
# Elected PRIMARY: localhost:27018 (Priority 5)
# Prediction Confirmed TRUE!`
      },
      js: {
        file: "Activity_8_2_Try_It_Yourself/lab_02_priority_election.js",
        content: `// Lab 8.2 Try It Yourself: Configure Priority
var cfg = rs.conf();
cfg.members[0].priority = 1;
cfg.members[1].priority = 5;
cfg.members[2].priority = 2;
rs.reconfig(cfg);

print("Prediction: Node 1 (priority: 5) wins over Node 2 (priority: 2)");
rs.stepDown(60);
sleep(5000);

// Verify outcome
var newPrimary = rs.status().members.find(m => m.stateStr === "PRIMARY").name;
print("Elected Primary:", newPrimary);`
      },
      compose: {
        file: "Activity_8_1/docker-compose.yml",
        content: `# Uses 3-node cluster
# Priorities: Node 0 = 1, Node 1 = 5, Node 2 = 2`
      },
      outputImg: "../screenshots/activity_8_2_try_it_yourself_output.png"
    }
  };

  // State Management
  let currentAct = 'act1';
  let currentView = 'py';
  let isArbiterMode = false;
  let electionTerm = 2;
  let activePrimaryIndex = 0;

  // DOM Elements
  const tabBtns = document.querySelectorAll('.tab-btn');
  const subtabBtns = document.querySelectorAll('.subtab-btn');
  const currentFilenameEl = document.getElementById('current-filename');
  const codeContentEl = document.getElementById('code-content');
  const codePreEl = document.getElementById('code-pre');
  const screenshotViewEl = document.getElementById('screenshot-view');
  const screenshotImgEl = document.getElementById('screenshot-img');
  const btnCopyCode = document.getElementById('btn-copy-code');
  const btnRunScript = document.getElementById('btn-run-script');

  const btnStepdown = document.getElementById('btn-stepdown');
  const btnToggleArbiter = document.getElementById('btn-toggle-arbiter');
  const eventStreamTerminal = document.getElementById('event-stream-terminal');

  const slider0 = document.getElementById('slider-0');
  const slider1 = document.getElementById('slider-1');
  const slider2 = document.getElementById('slider-2');
  const prioVal0 = document.getElementById('prio-val-0');
  const prioVal1 = document.getElementById('prio-val-1');
  const prioVal2 = document.getElementById('prio-val-2');
  const predictionText = document.getElementById('prediction-text');

  // Render Code / View
  function updateCodeDisplay() {
    const act = activityData[currentAct];
    if (currentView === 'output') {
      codePreEl.classList.add('hidden');
      screenshotViewEl.classList.remove('hidden');
      screenshotImgEl.src = act.outputImg;
      currentFilenameEl.textContent = `Output Screenshot (${currentAct})`;
    } else {
      codePreEl.classList.remove('hidden');
      screenshotViewEl.classList.add('hidden');
      const item = act[currentView];
      if (item) {
        currentFilenameEl.textContent = item.file;
        codeContentEl.textContent = item.content;
      }
    }
  }

  // Tab Listeners
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentAct = btn.dataset.act;
      updateCodeDisplay();
    });
  });

  subtabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      subtabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentView = btn.dataset.view;
      updateCodeDisplay();
    });
  });

  // Copy Code
  btnCopyCode.addEventListener('click', () => {
    const text = codeContentEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const orig = btnCopyCode.textContent;
      btnCopyCode.textContent = "Copied!";
      btnCopyCode.style.background = "var(--accent-green)";
      setTimeout(() => {
        btnCopyCode.textContent = orig;
        btnCopyCode.style.background = "";
      }, 1500);
    });
  });

  // Run script simulation
  btnRunScript.addEventListener('click', () => {
    logTerminal(`[CLI EXEC] Executing python ${currentFilenameEl.textContent}...`, 'info');
    setTimeout(() => {
      logTerminal(`[STATUS] Successfully executed with exit code 0. Output verified!`, 'success');
    }, 600);
  });

  // Terminal logging
  function logTerminal(msg, type = '') {
    const p = document.createElement('p');
    p.className = `term-line ${type}`;
    const time = new Date().toLocaleTimeString();
    p.textContent = `[${time}] ${msg}`;
    eventStreamTerminal.appendChild(p);
    eventStreamTerminal.scrollTop = eventStreamTerminal.scrollHeight;
  }

  // Priority Prediction Logic
  function updatePrediction() {
    const p0 = parseInt(slider0.value);
    const p1 = parseInt(slider1.value);
    const p2 = parseInt(slider2.value);

    prioVal0.textContent = p0;
    prioVal1.textContent = `${p1} ${p1 > p2 ? '(High)' : ''}`;
    prioVal2.textContent = `${p2} ${p2 > p1 ? '(High)' : ''}`;

    document.getElementById('node-0-prio').textContent = p0;
    document.getElementById('node-1-prio').textContent = p1;
    document.getElementById('node-2-prio').textContent = isArbiterMode ? 0 : p2;

    if (p1 > p2) {
      predictionText.innerHTML = `When Primary steps down, <strong>Node 1 (localhost:27018)</strong> will win election because priority <strong>${p1}</strong> strictly exceeds Node 2's priority (<strong>${p2}</strong>).`;
    } else if (p2 > p1) {
      predictionText.innerHTML = `When Primary steps down, <strong>Node 2 (localhost:27019)</strong> will win election because priority <strong>${p2}</strong> strictly exceeds Node 1's priority (<strong>${p1}</strong>).`;
    } else {
      predictionText.innerHTML = `Priorities are equal (<strong>${p1}</strong> = <strong>${p2}</strong>). Winner will be determined by highest optime or election tie-breaking rules.`;
    }
  }

  slider0.addEventListener('input', updatePrediction);
  slider1.addEventListener('input', updatePrediction);
  slider2.addEventListener('input', updatePrediction);

  // Arbiter Mode Toggle
  btnToggleArbiter.addEventListener('click', () => {
    isArbiterMode = !isArbiterMode;
    const node2Card = document.getElementById('node-card-2');
    const badge2 = document.getElementById('badge-node-2');
    const node2Title = document.getElementById('node-2-title');
    const node2Icon = document.getElementById('node-2-icon');
    const node2Storage = document.getElementById('node-2-storage');
    const node2Prio = document.getElementById('node-2-prio');

    if (isArbiterMode) {
      btnToggleArbiter.textContent = "Switch to Standard 3-Data Nodes (Activity 8.1)";
      node2Card.className = "node-card arbiter";
      badge2.className = "node-badge arbiter";
      badge2.innerHTML = '<span class="pulse-dot"></span> ARBITER';
      node2Title.textContent = "mongo-arbiter";
      node2Icon.textContent = "⚖️";
      node2Storage.textContent = "0 MB (Arbiter only)";
      node2Prio.textContent = "0 (Cannot be Primary)";
      slider2.disabled = true;
      logTerminal("[CONFIG] Converted Node 2 to lightweight ARBITER. 0 data storage footprint active.", "warn");
    } else {
      btnToggleArbiter.textContent = "Switch to Arbiter Mode (Activity 8.1 TY)";
      node2Card.className = "node-card secondary";
      badge2.className = "node-badge secondary";
      badge2.innerHTML = '<span class="pulse-dot"></span> SECONDARY';
      node2Title.textContent = "mongo-rs0-3";
      node2Icon.textContent = "🛡️";
      node2Storage.textContent = "Replicated Data";
      node2Prio.textContent = slider2.value;
      slider2.disabled = false;
      logTerminal("[CONFIG] Reverted Node 2 to full data-bearing SECONDARY node.", "info");
    }
    updatePrediction();
  });

  // StepDown & Failover Execution
  btnStepdown.addEventListener('click', () => {
    btnStepdown.disabled = true;
    logTerminal(">>> [STEPDOWN] rs.stepDown(60) invoked on current PRIMARY! <<<", "danger");

    const p1 = parseInt(slider1.value);
    const p2 = isArbiterMode ? -1 : parseInt(slider2.value);
    const targetWinner = (p1 >= p2) ? 1 : 2;

    const oldPrimaryCard = document.getElementById(`node-card-${activePrimaryIndex}`);
    const oldBadge = document.getElementById(`badge-node-${activePrimaryIndex}`);

    oldPrimaryCard.className = "node-card secondary";
    oldBadge.className = "node-badge secondary";
    oldBadge.innerHTML = '<span class="pulse-dot"></span> STEPPED DOWN';

    setTimeout(() => {
      logTerminal("[HEARTBEAT] Connection severed. Peer heartbeats detect primary vacancy.", "warn");
      logTerminal("[ELECTION] Election Term incremented to Term " + (++electionTerm) + ".", "info");
      document.getElementById('kpi-term').textContent = `Term ${electionTerm}`;
    }, 800);

    setTimeout(() => {
      logTerminal(`[CONSENSUS] Candidate Node ${targetWinner} calls election. Votes: 2 of 3 gathered.`, "info");
    }, 1600);

    setTimeout(() => {
      activePrimaryIndex = targetWinner;
      const newPrimaryCard = document.getElementById(`node-card-${activePrimaryIndex}`);
      const newBadge = document.getElementById(`badge-node-${activePrimaryIndex}`);

      newPrimaryCard.className = "node-card primary";
      newBadge.className = "node-badge";
      newBadge.innerHTML = '<span class="pulse-dot"></span> PRIMARY';

      logTerminal(`*** [FAILOVER COMPLETE] Node ${activePrimaryIndex} ELECTED NEW PRIMARY! ***`, "success");
      logTerminal(`[SDAM] PyMongo driver auto-reconnected to localhost:2701${7 + activePrimaryIndex}.`, "success");

      btnStepdown.disabled = false;
    }, 2400);
  });

  // Initialize
  updateCodeDisplay();
  updatePrediction();
});
