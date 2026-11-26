"""
Lab 3.1: Activity - Try It Yourself
Objective: Add a requirement to track prerequisites between courses.
Decide whether to embed or reference the prerequisite relationships and justify your choice.

Architectural Decision:
We decide to REFERENCE the prerequisite courses using an array of course codes (e.g. prerequisites: ["CS101", "MATH101"]).

Justification:
1. Prevents Infinite Recursion & Deep Nesting: Courses form a Directed Acyclic Graph (DAG)
   of prerequisites (e.g., CS501 -> CS401 -> CS201 -> CS101). Embedding full course documents
   would lead to recursive or deeply nested documents.
2. Single Source of Truth & Zero Redundancy: Foundational courses (like CS101) are prerequisites
   for dozens of courses. Referencing ensures CS101 exists in one place.
3. Eliminates Update Anomalies: If a course's syllabus, title, or credit rating changes,
   updating it in one document propagates instantly.
4. Native Graph Querying ($graphLookup): Referencing enables MongoDB's $graphLookup stage
   to traverse the entire dependency tree (finding all direct and indirect prerequisites)
   in a single, high-performance aggregation.
"""

import os
import json
from pymongo import MongoClient
from bson import json_util

def banner(text, char="=", width=65):
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width + "\n")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nosql_labs_3_1_try"

# Schema with prerequisite reference validation
COURSE_PREREQ_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "code", "instructor", "schedule", "prerequisites"],
        "properties": {
            "title": {"bsonType": "string"},
            "code": {"bsonType": "string", "pattern": r"^[A-Z]{2,4}\d{3}$"},
            "instructor": {"bsonType": "string"},
            "credits": {"bsonType": "int", "minimum": 1, "maximum": 6},
            "schedule": {
                "bsonType": "object",
                "required": ["days", "times", "room"],
                "properties": {
                    "days": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "times": {"bsonType": "string"},
                    "room": {"bsonType": "string"}
                }
            },
            "prerequisites": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "pattern": r"^[A-Z]{2,4}\d{3}$",
                    "description": "Referenced course codes representing prerequisites"
                },
                "description": "Array of referenced course codes"
            },
            "enrolled_students": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["student_id", "name"],
                    "properties": {
                        "student_id": {"bsonType": "string"},
                        "name": {"bsonType": "string"},
                        "grade": {"bsonType": ["string", "null"]}
                    }
                }
            }
        }
    }
}

COURSES_WITH_PREREQS = [
    {
        "title": "Introduction to Programming",
        "code": "CS101",
        "instructor": "Dr. Alan Turing",
        "credits": 4,
        "schedule": {"days": ["Monday", "Wednesday"], "times": "08:30-10:00", "room": "LH-101"},
        "prerequisites": [],  # Entry-level course
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": "A"},
            {"student_id": "STU105", "name": "Kavya Nair", "grade": "A"}
        ]
    },
    {
        "title": "Discrete Mathematics",
        "code": "MATH101",
        "instructor": "Dr. John von Neumann",
        "credits": 3,
        "schedule": {"days": ["Tuesday", "Thursday"], "times": "10:00-11:30", "room": "LH-105"},
        "prerequisites": [],  # Entry-level course
        "enrolled_students": [
            {"student_id": "STU102", "name": "Sneha Reddy", "grade": "A-"},
            {"student_id": "STU103", "name": "Rahul Kumar", "grade": "B+"}
        ]
    },
    {
        "title": "Data Structures and Algorithms",
        "code": "CS201",
        "instructor": "Dr. Donald Knuth",
        "credits": 4,
        "schedule": {"days": ["Monday", "Wednesday"], "times": "11:30-13:00", "room": "LH-201"},
        "prerequisites": ["CS101"],  # References CS101
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": "A"},
            {"student_id": "STU103", "name": "Rahul Kumar", "grade": "A-"}
        ]
    },
    {
        "title": "Machine Learning Foundations",
        "code": "CS401",
        "instructor": "Dr. Priya Sharma",
        "credits": 4,
        "schedule": {"days": ["Monday", "Wednesday"], "times": "14:00-15:30", "room": "LH-202"},
        "prerequisites": ["CS201", "MATH101"],  # Requires CS201 and MATH101
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": "A"},
            {"student_id": "STU102", "name": "Sneha Reddy", "grade": "B+"}
        ]
    },
    {
        "title": "Deep Reinforcement Learning",
        "code": "CS501",
        "instructor": "Dr. Geoffrey Hinton",
        "credits": 4,
        "schedule": {"days": ["Friday"], "times": "09:00-12:00", "room": "LH-301"},
        "prerequisites": ["CS401"],  # Requires CS401
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": None}
        ]
    }
]

def export_to_json(collection, output_path):
    docs = list(collection.find())
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"[OK] Exported {len(docs)} documents to: {output_path}")

def main():
    banner("LAB 3.1 (TRY IT YOURSELF): PREREQUISITE RELATIONSHIPS")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"[OK] Connected to MongoDB database: '{DB_NAME}'")

    if "courses" in db.list_collection_names():
        db.drop_collection("courses")

    db.create_collection("courses", validator=COURSE_PREREQ_VALIDATOR)
    col = db["courses"]
    print("[OK] Created 'courses' collection with prerequisites reference validator.")

    col.insert_many(COURSES_WITH_PREREQS)
    print(f"[OK] Inserted {len(COURSES_WITH_PREREQS)} courses with prerequisite relationships.")

    # 1. Query: Direct Prerequisites Resolution using $lookup
    banner("Query 1: Resolve Direct Prerequisites for CS401 using $lookup")
    pipeline_lookup = [
        {"$match": {"code": "CS401"}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "prerequisites",
                "foreignField": "code",
                "as": "prerequisite_details"
            }
        },
        {
            "$project": {
                "_id": 0,
                "code": 1,
                "title": 1,
                "prerequisites": 1,
                "prerequisite_details.code": 1,
                "prerequisite_details.title": 1,
                "prerequisite_details.credits": 1,
                "prerequisite_details.instructor": 1
            }
        }
    ]
    res_lookup = list(col.aggregate(pipeline_lookup))
    if res_lookup:
        target = res_lookup[0]
        print(f"Course: [{target['code']}] {target['title']}")
        print("Direct Prerequisites Resolved via $lookup:")
        for prereq in target["prerequisite_details"]:
            print(f"  * [{prereq['code']}] {prereq['title']} ({prereq['credits']} credits) - {prereq['instructor']}")

    # 2. Query: Transitive Prerequisites using $graphLookup (Dependency Tree)
    banner("Query 2: Full Prerequisite Dependency Tree for CS501 using $graphLookup")
    pipeline_graph = [
        {"$match": {"code": "CS501"}},
        {
            "$graphLookup": {
                "from": "courses",
                "startWith": "$prerequisites",
                "connectFromField": "prerequisites",
                "connectToField": "code",
                "as": "full_prerequisite_tree",
                "depthField": "level"
            }
        },
        {
            "$project": {
                "_id": 0,
                "code": 1,
                "title": 1,
                "full_prerequisite_tree.code": 1,
                "full_prerequisite_tree.title": 1,
                "full_prerequisite_tree.level": 1
            }
        }
    ]
    res_graph = list(col.aggregate(pipeline_graph))
    if res_graph:
        target_course = res_graph[0]
        print(f"Course: [{target_course['code']}] {target_course['title']}")
        print("Complete Prerequisite Chain (Direct & Indirect Transitive Dependencies):")
        # Sort by depth level ascending
        tree = sorted(target_course["full_prerequisite_tree"], key=lambda x: x.get("level", 0))
        for item in tree:
            depth_indicator = "  " * (item.get("level", 0) + 1)
            print(f"{depth_indicator}-> [Depth {item.get('level', 0)}] {item['code']}: {item['title']}")

    # Architectural Discussion Printout
    banner("ARCHITECTURAL DECISION & JUSTIFICATION")
    justification = """
+---------------------------------------------------------------------------------------+
| DECISION: REFERENCE DESIGN (Referencing Prerequisite Course Codes in an Array)       |
+---------------------------------------------------------------------------------------+
| 1. Prevents Circular & Infinite Recursion:                                            |
|    Prerequisites form a directed graph. Embedding full documents would cause          |
|    recursive duplication and risk infinite loops. References cleanly decouple them.   |
|                                                                                       |
| 2. Eliminates Update Anomalies:                                                       |
|    CS101 is required by many advanced courses. Storing it once ensures that if credit |
|    hours, title, or instructor change, updates occur in exactly ONE place.            |
|                                                                                       |
| 3. Prevents Document Bloat:                                                           |
|    Keeps course documents lightweight, well below MongoDB's 16MB document boundary.   |
|                                                                                       |
| 4. Native Graph Traversal:                                                            |
|    MongoDB's $graphLookup natively traverses referenced course codes to effortlessly  |
|    generate student graduation prerequisite check-paths across arbitrary depths.      |
+---------------------------------------------------------------------------------------+
"""
    print(justification)

    # Export to JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_json = os.path.join(script_dir, "courses_with_prerequisites.json")
    export_to_json(col, output_json)

    banner("Lab 3.1 Try It Yourself Completed Successfully")

if __name__ == "__main__":
    main()
