# Comparative Analysis Report: Fraud Detection Data Platform

*Generated 2026-11-20 00:10 — Lab 18.2, based on the Lab 18.1 capstone dataset*

## Executive Summary

This report compares MongoDB, Cassandra, and Neo4j for a fraud-detection workload combining transaction history lookups, risk-score filtering, category analytics, and relationship-based fraud-ring detection. **No single database wins every query pattern.** The recommendation (see Final Recommendation) is a polyglot architecture: MongoDB as the operational store, with Neo4j added specifically for fraud-ring traversal once that becomes a first-class product requirement.

## System Architecture

```
            +-------------------+
            |   Application /    |
            |   Fraud Review UI  |
            +----------+----------+
                       |
         +-------------+--------------+
         |                             |
 +-------v--------+           +--------v-------+
 |    MongoDB     |           |     Neo4j      |
 | (transactions, |           | (device/account|
 |  risk scores,  |           |  relationship  |
 |  analytics)    |           |  graph, fraud  |
 |                |           |  ring queries) |
 +----------------+           +----------------+

 Cassandra: evaluated but NOT included in this architecture --
 see Data Modeling Analysis for why.
```

## Query Performance Comparison

*(MongoDB figures below were MEASURED against a live database.)*

| Query | MongoDB (ms) | Cassandra (ms, ESTIMATED) | Neo4j (ms, ESTIMATED) | Notes |
|---|---|---|---|---|
| Transaction History | 6.2 | ~2-5 | ~5-15 | Cassandra: Partition-key lookup; very fast if user_id is the partition key. Neo4j: Single relationship traversal from an indexed User node |
| High-Risk Query | 2.7 | ~50-200+ | ~10-50 | Cassandra: Requires ALLOW FILTERING or a secondary index/materialized view; not a native fit. Neo4j: Property filter on Transaction nodes; fine at moderate scale |
| Category Analytics | 15.3 | N/A (needs Spark) | Weak fit | Cassandra: Cassandra has no native aggregation framework. Neo4j: Neo4j is not optimized for whole-graph aggregation |
| Write Throughput | 70.1 | Excellent (linear scale-out) | Moderate | Cassandra: Cassandra's core strength; adding nodes adds write capacity. Neo4j: Each write touches nodes + relationships + indexes; costlier than a document insert |

## Data Modeling Analysis

- **MongoDB**: a single `transactions` document per event, with `user_id` and `risk_score` indexed, models this workload naturally and supports every query pattern except deep relationship traversal.
- **Cassandra**: requires the query pattern to be known upfront and baked into the partition key (`PRIMARY KEY ((user_id), event_time)`). This makes the transaction-history query excellent but the ad-hoc risk-score filter and category analytics awkward or unsupported without a secondary system (Spark).
- **Neo4j**: models users, merchants, and transactions as nodes with `SHARES_DEVICE`/`TRANSFERRED_TO` relationships. This is the only model of the three where 'find everyone within 3 hops of this suspect' is a native, efficient query rather than a workaround.

## Scalability Assessment

| Transactions | MongoDB | Cassandra | Neo4j |
|---|---|---|---|
| 1M | Single replica set; comfortable on standard indexes | Comfortable on a small cluster | Comfortable on a single instance |
| 10M | Sharding likely needed if write-heavy; read replicas help reads | Scales near-linearly by adding nodes | Fine for lookups; ring-detection queries start needing hop-limits |
| 100M | Sharded cluster required; shard key choice (Ch. 11) becomes critical | Cassandra's strongest scale tier; this is its home turf | Needs careful relationship-density management and query hop-limits; consider Neo4j Fabric for sharding across a graph cluster |

## Final Recommendation

Start with **MongoDB alone** — it covers transaction storage, risk-score filtering, and category analytics well, and keeps operational complexity low (one database to run, back up, and secure; see Chapters 12–14). **Add Neo4j** only once fraud-ring / relationship detection becomes a product requirement that MongoDB's `$graphLookup` can no longer serve at acceptable latency (see Lab 16.2's hybrid routing pattern for how the two would coexist). **Cassandra is not recommended for this specific workload**: its write-throughput advantage doesn't offset the loss of ad-hoc querying and native aggregation that this fraud-review workload needs; it would be the right choice for a different workload (e.g. a pure high-volume event-ingestion pipeline with no complex read patterns).

---
*Cassandra and Neo4j figures in this report are architectural estimates, not measurements from a live benchmark. To replace them with real numbers, provision a Cassandra and/or Neo4j instance and extend this script's `get_mongo_benchmark()` pattern with equivalent `get_cassandra_benchmark()` / `get_neo4j_benchmark()` functions.*