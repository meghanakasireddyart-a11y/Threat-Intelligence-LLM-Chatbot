"""
Shared MongoDB connection utility for all lab scripts.
"""

import os
import json
from pymongo import MongoClient
from bson import json_util

_client = None

def get_client(uri=None):
    """Return a singleton MongoClient."""
    global _client
    if _client is None:
        connection_uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client = MongoClient(connection_uri, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        print(f"[OK] Connected to MongoDB at {connection_uri}")
    return _client

def get_db(db_name=None):
    """Return a database handle."""
    client = get_client()
    name = db_name or os.getenv("MONGO_DB", "bank")
    return client[name]

def close_client():
    """Close the singleton connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("[OK] MongoDB connection closed.")

def reset_collection(db_name, collection_name):
    """Drop and recreate a collection."""
    db = get_db(db_name)
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"[OK] Dropped collection: {db_name}.{collection_name}")
    return db[collection_name]

def print_json(data):
    """Pretty-print a document or list of documents."""
    print(json.dumps(data, indent=2, default=json_util.default))

def banner(text, char="=", width=60):
    """Print a section banner."""
    print()
    print(char * width)
    print(f"  {text}")
    print(char * width)
    print()
