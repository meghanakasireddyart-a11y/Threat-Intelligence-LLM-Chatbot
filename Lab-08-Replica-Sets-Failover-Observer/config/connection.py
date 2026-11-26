"""
Configuration and connection utilities for NoSQL Lab 8: Replication and Failover
"""

import os

# Default MongoDB Replica Set URI
DEFAULT_RS_URI = os.getenv(
    "REPLICA_SET_URI",
    "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&serverSelectionTimeoutMS=5000"
)

# Docker internal URI
DOCKER_RS_URI = "mongodb://host.docker.internal:27017,host.docker.internal:27018,host.docker.internal:27019/?replicaSet=rs0"

STUDENT_INFO = {
    "name": "Kasireddy Meghana",
    "usn": "24BTRCL119",
    "course": "NoSQL Databases Using MongoDB",
    "chapter": "Chapter 08 - Replication, High Availability & Elections",
    "lab": "Lab 8: Deploy Local Replica Set & Observe Failover"
}

def banner(title):
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)

def section(title):
    print(f"\n--- {title} ---")
