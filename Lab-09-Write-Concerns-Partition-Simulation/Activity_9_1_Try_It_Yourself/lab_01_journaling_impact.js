/**
 * ============================================================================
 * Lab 9.1: Activity 9.1 - Try It Yourself (mongosh script)
 * Objective: Measure Impact of Journaling (j:true vs j:false)
 * Student: Kasireddy Meghana (24BTRCL119)
 * Course: NoSQL Databases Using MongoDB
 * ============================================================================
 */

print("================================================================================");
print("  Activity 9.1 (Try It Yourself): Journaling Impact Benchmark (mongosh)");
print("  Student: Kasireddy Meghana (24BTRCL119)");
print("================================================================================");

const DOC_COUNT = 1000;
const dbTest = db.getSiblingDB("cap_journal_benchmark");

const configs = [
    { label: "w:1, j:false", w: 1, j: false },
    { label: "w:1, j:true", w: 1, j: true },
    { label: "w:majority, j:false", w: "majority", j: false },
    { label: "w:majority, j:true", w: "majority", j: true },
    { label: "w:all, j:false", w: 3, j: false },
    { label: "w:all, j:true", w: 3, j: true }
];

const results = [];

configs.forEach(cfg => {
    const collName = "bench_" + cfg.label.replace(/[^a-zA-Z0-9]/g, "_");
    dbTest.getCollection(collName).drop();
    const coll = dbTest.getCollection(collName);
    const wc = { w: cfg.w, j: cfg.j, wtimeout: 10000 };

    print("Testing " + cfg.label + "...");
    const s = new Date();
    for (let i = 0; i < DOC_COUNT; i++) {
        coll.insertOne({ seq: i, ts: new Date() }, { writeConcern: wc });
    }
    const elapsed = new Date() - s;
    const avg = (elapsed / DOC_COUNT).toFixed(2);
    const ops = ((DOC_COUNT / elapsed) * 1000).toFixed(1);

    results.push({
        label: cfg.label,
        total: elapsed,
        avg: avg,
        ops: ops
    });
});

print("\n================================================================================");
print("  CONFIGURATION              DOCS     TOTAL (ms)    AVG (ms)     OPS/SEC");
print("================================================================================");
results.forEach(r => {
    print("  " + r.label.padEnd(26) + ("" + DOC_COUNT).padEnd(9) + ("" + r.total).padEnd(14) + ("" + r.avg).padEnd(13) + r.ops);
});
print("================================================================================");
print("\nConclusion: Journaling (j:true) forces synchronous disk flush (fsync) per write,");
print("adding substantial latency (~2-3ms on SSD, ~10ms on HDD) compared to in-memory buffering.");
