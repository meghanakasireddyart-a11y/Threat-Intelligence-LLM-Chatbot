"""
Configuration and connection utilities for NoSQL Lab 9: Write Concern & Network Partitions
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
"""

import os
import sys

# Default MongoDB Replica Set URI
DEFAULT_RS_URI = os.getenv(
    "REPLICA_SET_URI",
    "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&serverSelectionTimeoutMS=5000"
)

# Docker internal URI for cross-container networking
DOCKER_RS_URI = "mongodb://host.docker.internal:27017,host.docker.internal:27018,host.docker.internal:27019/?replicaSet=rs0&serverSelectionTimeoutMS=5000"

STUDENT_INFO = {
    "name": "Kasireddy Meghana",
    "usn": "24BTRCL119",
    "course": "NoSQL Databases Using MongoDB",
    "chapter": "Chapter 09 - CAP Theorem, Consistency Guarantees & Network Partitions",
    "lab_title": "Lab 9: Measure Write Concern Latency & Simulate Network Partition",
    "docker_hub_repo": "https://hub.docker.com/r/kasireddymeghana/nosql-lab09"
}

def banner(title):
    print("=" * 76)
    print(f"  {title}")
    print("=" * 76)

def section(title):
    print(f"\n--- {title} ---")
