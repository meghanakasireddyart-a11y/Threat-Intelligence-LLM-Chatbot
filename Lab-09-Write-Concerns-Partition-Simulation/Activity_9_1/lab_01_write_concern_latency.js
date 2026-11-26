/**
 * ============================================================================
 * Lab 9.1: Measure Write Concern Latency (mongosh script)
 * Student: Kasireddy Meghana (24BTRCL119)
 * Course: NoSQL Databases Using MongoDB
 * ============================================================================
 */

print("================================================================================");
print("  Lab 9.1: Write Concern Latency Benchmark (mongosh)");
print("  Student: Kasireddy Meghana (24BTRCL119)");
print("================================================================================");

const DOC_COUNT = 1000;
const dbTest = db.getSiblingDB("cap_latency_test");

function benchmarkWriteConcern(wSetting, jSetting, label) {
    const collName = "bench_" + label;
    dbTest.getCollection(collName).drop();
    const coll = dbTest.getCollection(collName);
    const wc = { w: wSetting, j: jSetting, wtimeout: 10000 };

    print("Running benchmark for " + label + " (" + DOC_COUNT + " documents)...");
    const startTime = new Date();

    for (let i = 0; i < DOC_COUNT; i++) {
        coll.insertOne(
            { seq: i, timestamp: new Date(), label: label },
            { writeConcern: wc }
        );
    }

    const elapsedMs = new Date() - startTime;
    const avgLatencyMs = (elapsedMs / DOC_COUNT).toFixed(2);
    const opsSec = ((DOC_COUNT / elapsedMs) * 1000).toFixed(1);

    return {
        label: label,
        totalMs: elapsedMs,
        avgMs: avgLatencyMs,
        opsSec: opsSec
    };
}

const resW1 = benchmarkWriteConcern(1, false, "w1");
const resWMaj = benchmarkWriteConcern("majority", false, "w_majority");
const resWAll = benchmarkWriteConcern(3, false, "w_all");

print("\n================================================================================");
print("  CONFIGURATION              DOCS     TOTAL (ms)    AVG (ms)     OPS/SEC");
print("================================================================================");
[resW1, resWMaj, resWAll].forEach(r => {
    print("  " + r.label.padEnd(26) + ("" + DOC_COUNT).padEnd(9) + ("" + r.totalMs).padEnd(14) + ("" + r.avgMs).padEnd(13) + r.opsSec);
});
print("================================================================================");
print("\nConclusion: w:1 is fastest because it completes on Primary in-memory WiredTiger cache.");
print("w:majority requires replication to at least 1 secondary, adding network RTT.");
print("w:all waits for every node, making it sensitive to tail latency.");
