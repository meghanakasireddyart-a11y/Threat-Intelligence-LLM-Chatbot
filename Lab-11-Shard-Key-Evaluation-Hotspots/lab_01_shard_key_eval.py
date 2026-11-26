"""Lab 11.1 - Evaluate Shard Key Choices
Decision matrix for selecting shard keys in an e-commerce system.

This is a design/analysis lab. Run it to see the decision framework.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import banner
from rich.table import Table
from rich.console import Console

console = Console()


def evaluate_shard_key(name, cardinality, distribution, query_targeting, monotonic, verdict):
    """Evaluate and print a shard key candidate."""
    scores = {
        "High Cardinality": "+" if cardinality > 100000 else ("~" if cardinality > 1000 else "-"),
        "Even Distribution": "+" if distribution > 0.8 else ("~" if distribution > 0.5 else "-"),
        "Query Targeting": "+" if query_targeting > 0.8 else ("~" if query_targeting > 0.5 else "-"),
        "Not Monotonic": "+" if not monotonic else "-",
    }
    total_plus = sum(1 for v in scores.values() if v == "+")
    return {"name": name, "scores": scores, "total_plus": total_plus, "verdict": verdict}


def main():
    banner("Lab 11.1: Shard Key Evaluation Matrix")

    candidates = [
        evaluate_shard_key(
            name="order_id", cardinality=5000000, distribution=0.95,
            query_targeting=0.4, monotonic=False,
            verdict="Good for order writes, but customer queries broadcast to all shards (scatter-gather)"
        ),
        evaluate_shard_key(
            name="customer_id", cardinality=1000000, distribution=0.6,
            query_targeting=0.95, monotonic=False,
            verdict="High query targeting, but VIP customers cause write skew (chunk hotspots)"
        ),
        evaluate_shard_key(
            name="order_date", cardinality=3650, distribution=0.2,
            query_targeting=0.5, monotonic=True,
            verdict="AVOID - Monotonically increasing. 100% of new inserts route to latest chunk on 1 shard"
        ),
        evaluate_shard_key(
            name="hashed customer_id", cardinality=1000000, distribution=0.98,
            query_targeting=0.90, monotonic=False,
            verdict="RECOMMENDED - Randomizes chunk distribution evenly while targeting customer-scoped queries"
        ),
    ]

    # Decision matrix table
    table = Table(title="Shard Key Decision Matrix", show_lines=True)
    table.add_column("Candidate", style="cyan", width=22)
    table.add_column("Cardinality", justify="center", width=12)
    table.add_column("Distribution", justify="center", width=12)
    table.add_column("Query Target", justify="center", width=12)
    table.add_column("Not Mono?", justify="center", width=10)
    table.add_column("Score", justify="center", width=8)
    table.add_column("Verdict", width=50)

    for c in candidates:
        s = c["scores"]
        score_str = f"{c['total_plus']}/4"
        table.add_row(
            c["name"],
            s["High Cardinality"],
            s["Even Distribution"],
            s["Query Targeting"],
            s["Not Monotonic"],
            score_str,
            c["verdict"]
        )

    console.print(table)

    print("\n=== Shard Key Selection Rules ===")
    print("  1. HIGH CARDINALITY  - enough unique values to spread data")
    print("  2. EVEN DISTRIBUTION - similar doc count per shard")
    print("  3. QUERY TARGETING   - most queries should target 1 shard (not scatter-gather)")
    print("  4. NOT MONOTONIC    - avoid keys like timestamps that increase over time")
    print("")
    print("  Best practice for e-commerce: compound shard key")
    print("    { user_id: 1, order_date: 1 }  -- targets by user, spreads by time")

    banner("Lab 11.1 Complete")


if __name__ == "__main__":
    main()