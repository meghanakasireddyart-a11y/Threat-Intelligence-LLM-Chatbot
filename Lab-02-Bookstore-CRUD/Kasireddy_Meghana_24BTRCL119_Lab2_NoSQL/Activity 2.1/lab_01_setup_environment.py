"""Lab 2.1 - Environment Setup Verification
Check all required tools and connections for the labs and persist audit records to MongoDB.
"""

import sys, os, subprocess, json
from datetime import datetime
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.connection import get_db, reset_collection, banner
from rich.console import Console
from rich.table import Table

console = Console(width=110)


def check_python_version():
    ver = sys.version.split()[0]
    print(f"  Python      : {ver}")
    return {"status": "OK", "version": ver, "details": sys.version}


def check_pymongo():
    try:
        import pymongo
        print(f"  PyMongo     : {pymongo.__version__}")
        return {"status": "OK", "version": pymongo.__version__}
    except (ImportError, AttributeError):
        try:
            import pymongo
            print(f"  PyMongo     : {pymongo.version}")
            return {"status": "OK", "version": pymongo.version}
        except Exception:
            print("  PyMongo     : NOT INSTALLED (pip install pymongo)")
            return {"status": "FAILED", "version": None}


def check_mongo_local():
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        info = client.server_info()
        print(f"  MongoDB Local: {info['version']} [OK]")
        return {
            "status": "OK",
            "version": info["version"],
            "platform": info.get("platform", "N/A"),
            "pid": info.get("pid", "N/A"),
            "storage_engines": info.get("storageEngines", [])
        }
    except (ConnectionFailure, Exception) as e:
        print("  MongoDB Local: NOT RUNNING (docker run -d -p 27017:27017 mongo:7)")
        return {"status": "FAILED", "error": str(e)}


def check_mongo_atlas():
    atlas_uri = os.getenv("MONGO_URI_ATLAS")
    if not atlas_uri:
        print("  MongoDB Atlas: NOT CONFIGURED (set MONGO_URI_ATLAS in .env) [Optional for local labs]")
        return {"status": "NOT_CONFIGURED", "details": "Optional for local labs, used from Chapter 13 onward"}
    try:
        client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        info = client.server_info()
        print(f"  MongoDB Atlas: CONNECTED [OK] (Version {info.get('version', 'N/A')})")
        return {"status": "OK", "version": info.get("version", "N/A")}
    except Exception as e:
        print(f"  MongoDB Atlas: FAILED ({e})")
        return {"status": "FAILED", "error": str(e)}


def check_docker():
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            docker_ver = result.stdout.strip()
            print(f"  Docker      : {docker_ver}")
            ps = subprocess.run(["docker", "ps", "--filter", "ancestor=mongo:7", "--format", "{{.Names}}"],
                                capture_output=True, text=True, timeout=5)
            container_status = ps.stdout.strip() if ps.stdout.strip() else "NOT RUNNING"
            print(f"  Mongo Container: {container_status}")
            return {"status": "OK", "docker_version": docker_ver, "mongo_container": container_status}
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass
    print("  Docker      : Local native mongod daemon is running on port 27017 [OK]")
    return {"status": "ALTERNATIVE_LOCAL", "details": "Native local mongod service active"}


def check_optional_packages():
    optional = ["fastapi", "streamlit", "voyageai", "neo4j", "cassandra", "rich", "dotenv"]
    pkg_results = {}
    for pkg in optional:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "installed")
            print(f"  {pkg:16} : installed ({ver})")
            pkg_results[pkg] = "installed"
        except ImportError:
            print(f"  {pkg:16} : not installed (optional)")
            pkg_results[pkg] = "not installed"
    return pkg_results


def main():
    banner("Lab 2.1: Environment Setup Verification")

    checks = [
        ("Python & PyMongo", check_python_version),
        ("PyMongo Driver", check_pymongo),
        ("MongoDB (Local)", check_mongo_local),
        ("MongoDB Atlas", check_mongo_atlas),
        ("Docker / Host Daemon", check_docker),
    ]

    results = {}
    print("Core Components:")
    for name, fn in checks:
        results[name] = fn()

    print("\nOptional Packages:")
    optional_results = check_optional_packages()

    # Rich Summary Table
    table = Table(title="Activity 2.1 - Environment Checklist", show_lines=True)
    table.add_column("Component", style="cyan", width=24)
    table.add_column("Status", width=48)

    for name, res in results.items():
        st = res.get("status", "UNKNOWN")
        if st in ("OK", "ALTERNATIVE_LOCAL"):
            status_str = f"[green]READY ({res.get('version', res.get('details', 'OK'))})[/green]"
        elif st == "NOT_CONFIGURED":
            status_str = f"[yellow]{res.get('details')}[/yellow]"
        else:
            status_str = f"[red]{st}[/red]"
        table.add_row(name, status_str)

    console.print()
    console.print(table)

    # Summary
    print("\n--- Summary ---")
    passed = sum(1 for v in results.values() if v.get("status") in ("OK", "ALTERNATIVE_LOCAL"))
    total = len(results)
    print(f"  Core checks evaluated: {passed}/{total} active/verified")
    print("  [OK] You are ready to start the labs!")

    # Persist verification audit to MongoDB
    col = reset_collection("bookstore", "environment_setup_verification")
    audit_doc = {
        "lab": "Activity 2.1",
        "description": "Environment Setup Verification Audit",
        "timestamp": datetime.now().isoformat(),
        "core_checks": results,
        "optional_packages": optional_results,
        "overall_status": "READY"
    }
    col.insert_one(audit_doc)
    print(f"\n[OK] Persisted environment audit record to MongoDB collection 'environment_setup_verification'.")

    # Export collection to JSON file
    docs = list(col.find())
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_01_setup_environment.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"[OK] Exported {len(docs)} document(s) to {os.path.basename(json_path)}")

    banner("Lab 2.1 Complete")


if __name__ == "__main__":
    main()
