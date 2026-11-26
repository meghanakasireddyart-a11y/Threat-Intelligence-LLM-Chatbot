"""
Lab 9.2 - Simulate Network Partition (Design Lab)
Tests single secondary partition, minority partition, w:1 vs w:majority, and re-election.
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Activity_9_2.lab_02_simulate_partition import run_lab_9_2
from Activity_9_2_Try_It_Yourself.lab_02_minority_partition_stepdown import run_lab_9_2_try_it_yourself


def main():
    print("=" * 80)
    print("  MongoDB Lab 9.2: Complete Network Partition Simulation Suite")
    print("=" * 80)
    print("\n--- Running Part 1: Single Secondary Partition (Majority Intact) ---")
    run_lab_9_2()

    print("\n--- Running Part 2: Dual Secondary Partition (Minority & Stepdown) ---")
    run_lab_9_2_try_it_yourself()


if __name__ == "__main__":
    main()
