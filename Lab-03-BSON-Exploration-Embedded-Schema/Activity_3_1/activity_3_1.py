"""
Lab 3.1: Design an Embedded Document Schema
Objective: Design and implement an embedded document schema for a realistic use case.

Instructions:
1. Design a document schema for a university course enrollment system. Each course
   document should embed its roster of students (name, ID, grade) and its schedule
   (days, times, room). Write the PyMongo code to create the collection, insert at
   least 3 course documents, and query for all courses that meet on Monday.
2. Add schema validation to the courses collection that requires title, code (e.g., CS401),
   instructor, and schedule fields.
3. Write a query that finds all students enrolled in courses taught by a specific instructor.
4. Export the collection to courses.json.
"""

import os
import json
from pymongo import MongoClient
from bson import json_util

def banner(text, char="=", width=65):
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width + "\n")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nosql_labs_3_1"

# Course Schema Validator using JSON Schema
COURSE_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "code", "instructor", "schedule"],
        "properties": {
            "title": {
                "bsonType": "string",
                "description": "Course title is required and must be a string"
            },
            "code": {
                "bsonType": "string",
                "pattern": r"^[A-Z]{2,4}\d{3}$",
                "description": "Course code format e.g., CS401, AIML101"
            },
            "instructor": {
                "bsonType": "string",
                "description": "Instructor name is required"
            },
            "credits": {
                "bsonType": "int",
                "minimum": 1,
                "maximum": 6,
                "description": "Credits must be an integer between 1 and 6"
            },
            "schedule": {
                "bsonType": "object",
                "required": ["days", "times", "room"],
                "properties": {
                    "days": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Meeting days array (e.g., ['Monday', 'Wednesday'])"
                    },
                    "times": {
                        "bsonType": "string",
                        "description": "Class timing string (e.g., '10:00-11:30')"
                    },
                    "room": {
                        "bsonType": "string",
                        "description": "Assigned classroom"
                    }
                }
            },
            "enrolled_students": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["student_id", "name"],
                    "properties": {
                        "student_id": {
                            "bsonType": "string",
                            "description": "Unique student identifier"
                        },
                        "name": {
                            "bsonType": "string",
                            "description": "Student full name"
                        },
                        "grade": {
                            "bsonType": ["string", "null"],
                            "description": "Letter grade or null if in progress"
                        }
                    }
                }
            }
        }
    }
}

# 3 Comprehensive Course Documents with Embedded Schedules and Student Rosters
COURSES_DATA = [
    {
        "title": "Machine Learning Foundations",
        "code": "CS401",
        "instructor": "Dr. Priya Sharma",
        "credits": 4,
        "schedule": {
            "days": ["Monday", "Wednesday"],
            "times": "10:00-11:30",
            "room": "Lecture Hall 201"
        },
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": "A"},
            {"student_id": "STU102", "name": "Sneha Reddy", "grade": "B+"},
            {"student_id": "STU103", "name": "Rahul Kumar", "grade": "A-"},
            {"student_id": "STU104", "name": "Divya Patel", "grade": "B"}
        ]
    },
    {
        "title": "Distributed Cloud Systems",
        "code": "CS402",
        "instructor": "Dr. Anil Gupta",
        "credits": 3,
        "schedule": {
            "days": ["Tuesday", "Thursday"],
            "times": "14:00-15:30",
            "room": "Room 305"
        },
        "enrolled_students": [
            {"student_id": "STU101", "name": "Arjun Mehta", "grade": None},
            {"student_id": "STU105", "name": "Kavya Nair", "grade": "A"},
            {"student_id": "STU106", "name": "Vikram Singh", "grade": "A+"}
        ]
    },
    {
        "title": "Natural Language Processing",
        "code": "CS403",
        "instructor": "Dr. Priya Sharma",
        "credits": 3,
        "schedule": {
            "days": ["Monday", "Wednesday", "Friday"],
            "times": "09:00-10:00",
            "room": "Lecture Hall 102"
        },
        "enrolled_students": [
            {"student_id": "STU102", "name": "Sneha Reddy", "grade": "B+"},
            {"student_id": "STU103", "name": "Rahul Kumar", "grade": None},
            {"student_id": "STU107", "name": "Neha Gupta", "grade": "A"}
        ]
    }
]

def export_to_json(collection, output_path):
    """Export MongoDB collection documents to a formatted JSON file."""
    docs = list(collection.find())
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"[OK] Exported {len(docs)} documents to: {output_path}")

def main():
    banner("LAB 3.1: EMBEDDED DOCUMENT SCHEMA DESIGN")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"[OK] Connected to MongoDB database: '{DB_NAME}'")

    # Step 1 & 2: Setup collection with JSON Schema Validation
    if "courses" in db.list_collection_names():
        db.drop_collection("courses")
        print("[OK] Dropped existing 'courses' collection for clean run.")

    db.create_collection("courses", validator=COURSE_VALIDATOR)
    col = db["courses"]
    print("[OK] Created 'courses' collection with JSON Schema Validation enforcing:")
    print("     - Required fields: title, code, instructor, schedule")
    print("     - Embedded schedule: days (array), times, room")
    print("     - Embedded enrolled_students: student_id, name, grade")

    # Insert documents
    insert_result = col.insert_many(COURSES_DATA)
    print(f"\n[OK] Successfully inserted {len(insert_result.inserted_ids)} course documents.")

    # Query 1: Find all courses that meet on Monday
    banner("Query 1: Courses that meet on Monday (schedule.days = 'Monday')")
    monday_courses = col.find(
        {"schedule.days": "Monday"},
        {"_id": 0, "title": 1, "code": 1, "instructor": 1, "schedule": 1}
    )
    for c in monday_courses:
        days_str = ", ".join(c["schedule"]["days"])
        print(f"  * [{c['code']}] {c['title']}")
        print(f"    Instructor: {c['instructor']}")
        print(f"    Schedule  : {days_str} @ {c['schedule']['times']} in {c['schedule']['room']}\n")

    # Query 2: Find all students enrolled in courses taught by Dr. Priya Sharma
    target_instructor = "Dr. Priya Sharma"
    banner(f"Query 2: Students enrolled in courses taught by '{target_instructor}'")
    instructor_courses = col.find(
        {"instructor": target_instructor},
        {"_id": 0, "title": 1, "code": 1, "enrolled_students": 1}
    )
    all_students_found = []
    for c in instructor_courses:
        print(f"  Course: {c['code']} - {c['title']}")
        for s in c.get("enrolled_students", []):
            print(f"    - Student ID: {s['student_id']:<8} | Name: {s['name']:<15} | Grade: {s['grade']}")
            all_students_found.append(s)
        print()

    # Step: Demonstrate Schema Validation Enforcement
    banner("Testing Schema Validation Enforcement")
    invalid_doc = {
        "title": "Invalid Incomplete Course",
        "instructor": "Dr. Unknown"
        # Missing required 'code' and 'schedule' fields
    }
    print("Attempting to insert an invalid course document missing 'code' and 'schedule'...")
    try:
        col.insert_one(invalid_doc)
        print("  [ERROR] Validation failed to reject invalid document!")
    except Exception as e:
        print("  [SUCCESS] MongoDB Schema Validator correctly rejected invalid document!")
        print(f"  Validation Error: {getattr(e, 'details', str(e))}")

    # Export to JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_json = os.path.join(script_dir, "courses.json")
    export_to_json(col, output_json)

    banner("Lab 3.1 Completed Successfully")

if __name__ == "__main__":
    main()
