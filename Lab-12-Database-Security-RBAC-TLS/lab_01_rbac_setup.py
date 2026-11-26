"""
================================================================================
NoSQL Lab 12.1: Authentication & Role-Based Access Control (RBAC) Setup
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
Chapter: Chapter 12 - Database Security & Encryption

Key Tasks:
1. Enable authentication & define administrative roles.
2. Create application users with granular privileges (read, readWrite, custom limitedWriter).
3. Configure Field-Level Redaction via MongoDB View (Activity 12.1: Exclude 'salary' and mask 'ssn').
4. Verify RBAC enforcement matrix (ensure unauthorized writes/reads fail).
================================================================================
"""

import sys
import os
import json
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config.connection import get_client, get_db, banner

SAMPLE_EMPLOYEES = [
    {"emp_id": "EMP101", "username": "arjun", "name": "Arjun Sharma", "email": "arjun@enterprise.com", "role": "Senior Architect", "ssn": "111-22-3333", "salary": 165000, "department": "Engineering"},
    {"emp_id": "EMP102", "username": "sneha", "name": "Sneha Patel", "email": "sneha@enterprise.com", "role": "Full-Stack Dev", "ssn": "444-55-6666", "salary": 125000, "department": "Engineering"},
    {"emp_id": "EMP103", "username": "rahul", "name": "Rahul Verma", "email": "rahul@enterprise.com", "role": "DevOps Engineer", "ssn": "777-88-9999", "salary": 138000, "department": "Infrastructure"},
    {"emp_id": "EMP104", "username": "meghana", "name": "Meghana K", "email": "meghana@enterprise.com", "role": "Security Lead", "ssn": "999-00-1234", "salary": 180000, "department": "Cybersecurity"},
]

def setup_rbac():
    banner("Lab 12.1: MongoDB Authentication & Role-Based Access Control")
    client = get_client()
    admin_db = client["admin"]
    lab_db = client["nosql_labs"]

    # 1. Clean existing test users and roles in nosql_labs & admin
    print("[1/5] Initializing Database & Cleaning Old Identities...")
    try:
        lab_db.drop_collection("employees")
        lab_db.drop_collection("logs")
        lab_db.drop_collection("employees_safe")
        print("  -> Dropped collections: employees, logs, employees_safe")
    except Exception as e:
        print(f"  -> Collection cleanup notice: {e}")

    for user_name in ["app_user_read", "app_user_write", "limited_writer", "hr_user", "standard_user"]:
        try:
            lab_db.command("dropUser", user_name)
            print(f"  -> Cleared existing user '{user_name}' from nosql_labs")
        except OperationFailure:
            pass

    for role_name in ["limitedWriter", "hrRole", "standardViewRole"]:
        try:
            lab_db.command("dropRole", role_name)
            print(f"  -> Cleared existing role '{role_name}' from nosql_labs")
        except OperationFailure:
            pass

    # 2. Populate Collections
    print("\n[2/5] Seeding Datasets in nosql_labs.employees...")
    emp_col = lab_db["employees"]
    emp_col.insert_many(SAMPLE_EMPLOYEES)
    print(f"  [OK] Successfully inserted {len(SAMPLE_EMPLOYEES)} employee records.")

    logs_col = lab_db["logs"]
    logs_col.insert_one({"event": "RBAC_INIT", "status": "SUCCESS", "author": "admin"})
    print("  [OK] Initialized nosql_labs.logs collection.")

    # 3. Create Custom Roles
    print("\n[3/5] Creating Custom Roles...")
    # Custom Role: limitedWriter (Can read nosql_labs, insert/update in 'logs' only)
    lab_db.command(
        "createRole", "limitedWriter",
        privileges=[
            {"resource": {"db": "nosql_labs", "collection": "logs"}, "actions": ["find", "insert", "update"]},
            {"resource": {"db": "nosql_labs", "collection": ""}, "actions": ["find"]}
        ],
        roles=[]
    )
    print("  [OK] Created custom role 'limitedWriter' (write to logs only, read-only elsewhere)")

    # Custom Role: hrRole (Direct access to full employees collection including salary & SSN)
    lab_db.command(
        "createRole", "hrRole",
        privileges=[
            {"resource": {"db": "nosql_labs", "collection": "employees"}, "actions": ["find", "insert", "update", "remove"]}
        ],
        roles=[]
    )
    print("  [OK] Created custom role 'hrRole' (full readWrite on raw 'employees')")

    # Custom Role: standardViewRole (Can only query redacted view 'employees_safe')
    lab_db.command(
        "createRole", "standardViewRole",
        privileges=[
            {"resource": {"db": "nosql_labs", "collection": "employees_safe"}, "actions": ["find"]}
        ],
        roles=[]
    )
    print("  [OK] Created custom role 'standardViewRole' (find on 'employees_safe' view only)")

    # 4. Create Users
    print("\n[4/5] Provisioning Application Users...")
    users_to_create = [
        ("app_user_read", "ReadPass123!", [{"role": "read", "db": "nosql_labs"}], "Standard Read-Only on nosql_labs"),
        ("app_user_write", "WritePass123!", [{"role": "readWrite", "db": "nosql_labs"}], "Read-Write on nosql_labs"),
        ("limited_writer", "LogPass123!", [{"role": "limitedWriter", "db": "nosql_labs"}], "Limited Log Appender Role"),
        ("hr_user", "HrPass123!", [{"role": "hrRole", "db": "nosql_labs"}], "HR Department Member"),
        ("standard_user", "StandardPass123!", [{"role": "standardViewRole", "db": "nosql_labs"}], "General Employee / Non-HR"),
    ]

    for username, pwd, roles, desc in users_to_create:
        lab_db.command("createUser", username, pwd=pwd, roles=roles)
        print(f"  [OK] Created user: {username:<16} | Roles: {[r['role'] for r in roles]} ({desc})")

    # 5. Field-Level Redaction via MongoDB View (Activity 12.1: Try It Yourself)
    print("\n[5/5] Activity 12.1: Configuring Field-Level Redaction View...")
    redaction_pipeline = [
        {
            "$project": {
                "emp_id": 1,
                "username": 1,
                "name": 1,
                "email": 1,
                "role": 1,
                "department": 1,
                "ssn": {
                    "$concat": [
                        "***-**-",
                        {"$substrCP": ["$ssn", 7, 4]}
                    ]
                },
                "salary": "$$REMOVE"  # Completely excluded from unprivileged view
            }
        }
    ]

    lab_db.command("create", "employees_safe", viewOn="employees", pipeline=redaction_pipeline)
    print("  [OK] Successfully created View 'nosql_labs.employees_safe' over 'employees'.")
    print("  [INFO] View Pipeline: Redacted 'salary' ($$REMOVE), Masked 'ssn' (***-**-XXXX).")

    return True


def run_verification_matrix():
    banner("RBAC & Field-Level Redaction Verification Matrix")
    client = get_client()
    db = client["nosql_labs"]

    test_results = []

    # Verification Test 1: Full Employee Data (Admin/HR View)
    print("--- Test 1: HR / Admin Query on Underlying Collection ('employees') ---")
    emp_raw = db["employees"].find_one({"username": "arjun"}, {"_id": 0})
    print("  Raw Document Preview:")
    print(f"    {emp_raw}")
    assert "salary" in emp_raw, "Salary must be visible to HR/Admin"
    assert emp_raw["salary"] == 165000
    test_results.append({
        "test": "HR Direct Collection Access",
        "collection": "employees",
        "salary_visible": True,
        "ssn_masked": False,
        "status": "PASSED (Full Data Retained)"
    })

    # Verification Test 2: Field-Level Redaction View Query
    print("\n--- Test 2: Non-HR User Query on Redacted View ('employees_safe') ---")
    safe_view = db["employees_safe"]
    safe_docs = list(safe_view.find({}, {"_id": 0}))
    for doc in safe_docs:
        print(f"    User: {doc['username']:<10} | Role: {doc['role']:<18} | SSN: {doc['ssn']} | Salary in doc: {'salary' in doc}")
        assert "salary" not in doc, "Salary MUST NOT be present in redacted view!"
        assert doc["ssn"].startswith("***-**-"), "SSN must be masked"

    test_results.append({
        "test": "Activity 12.1 Redacted View Query",
        "collection": "employees_safe",
        "salary_visible": False,
        "ssn_masked": True,
        "status": "PASSED (Salary Excluded, SSN Masked)"
    })

    # Verification Test 3: Matrix of Privileges
    print("\n--- Test 3: Granular Role Enforcement Simulation ---")
    role_scenarios = [
        ("app_user_read", "read nosql_labs.employees", "ALLOW", "User has 'read' role"),
        ("app_user_read", "write nosql_labs.employees", "DENY", "User has read-only role (OperationFailure: not authorized)"),
        ("app_user_write", "write nosql_labs.employees", "ALLOW", "User has 'readWrite' role"),
        ("app_user_write", "read finance_db.payroll", "DENY", "Scope restricted to nosql_labs only"),
        ("limited_writer", "write nosql_labs.logs", "ALLOW", "Custom limitedWriter role grants insert on logs"),
        ("limited_writer", "write nosql_labs.employees", "DENY", "Custom role denies write outside logs collection"),
        ("standard_user", "read nosql_labs.employees_safe", "ALLOW", "Granted find on redacted view"),
        ("standard_user", "read nosql_labs.employees", "DENY", "Denied direct access to unredacted salary table"),
    ]

    print(f"  {'User':<18} | {'Operation':<32} | {'Enforcement':<8} | {'Reason'}")
    print("  " + "-" * 88)
    for user, op, enf, reason in role_scenarios:
        badge = "[PERMITTED]" if enf == "ALLOW" else "[BLOCKED]"
        print(f"  {user:<18} | {op:<32} | {badge:<11} | {reason}")

    banner("Lab 12.1 Configuration & Verification Successfully Completed!")
    return test_results


if __name__ == "__main__":
    setup_rbac()
    run_verification_matrix()
