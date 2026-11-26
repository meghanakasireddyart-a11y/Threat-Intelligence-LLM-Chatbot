"""
Package the final ZIP submission archives for Lab 9 according to required format.
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_NAME_STUDENT = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_Lab9_NoSQL.zip")
ZIP_NAME_GENERIC = os.path.join(BASE_DIR, "NoSQL_Lab9_Submission.zip")

DIRS_TO_INCLUDE = [
    "Activity_9_1",
    "Activity_9_1_Try_It_Yourself",
    "Activity_9_2",
    "Activity_9_2_Try_It_Yourself",
    "config",
    "screenshots",
    "website"
]

FILES_TO_INCLUDE = [
    "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.docx",
    "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.pdf",
    "NoSQL_Lab9_Report.docx",
    "NoSQL_Lab9_Report.pdf",
    "lab_01_write_concern_latency.py",
    "lab_02_simulate_partition.py",
    "lab_02_simulate_partition.sh",
    "docker-compose-replicaset.yml",
    "Dockerfile",
    "requirements.txt",
    "docker_push_guide.md",
    "deploy_docker.bat",
    "start_website.bat"
]


def create_submission_zip(output_path):
    print(f"Creating submission ZIP: {output_path}")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add directories
        for d in DIRS_TO_INCLUDE:
            dir_path = os.path.join(BASE_DIR, d)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    if "__pycache__" in root:
                        continue
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        zf.write(full_p, rel_p)
                        print(f"  + Added: {rel_p}")

        # Add root files
        for f in FILES_TO_INCLUDE:
            full_p = os.path.join(BASE_DIR, f)
            if os.path.exists(full_p):
                zf.write(full_p, f)
                print(f"  + Added: {f}")

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[OK] Created {output_path} ({size_kb:.2f} KB)\n")


if __name__ == "__main__":
    create_submission_zip(ZIP_NAME_STUDENT)
    create_submission_zip(ZIP_NAME_GENERIC)
