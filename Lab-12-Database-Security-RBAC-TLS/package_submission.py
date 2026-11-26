"""
Package all completed Lab 12 artifacts into submission zip files.
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
Chapter: Chapter 12 - Database Security, RBAC & TLS Encryption
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_USN = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_Lab12_NoSQL.zip")
ZIP_GENERIC = os.path.join(BASE_DIR, "NoSQL_Lab12_Submission.zip")

FILES_TO_INCLUDE = [
    "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_12.docx",
    "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_12.pdf",
    "NoSQL_Lab12_Report.docx",
    "NoSQL_Lab12_Report.pdf",
    "lab_01_rbac_setup.py",
    "lab_01_rbac_setup.sh",
    "lab_02_tls_setup.py",
    "lab_02_tls_setup.sh",
    "rbac_field_redaction.py",
    "Dockerfile",
    "docker-compose.yml",
    "docker_push_guide.md",
    "deploy_docker.bat",
    "start_website.bat",
    "requirements.txt",
    "generate_screenshots.py",
    "build_lab12_report.py",
]

DIRS_TO_INCLUDE = [
    "config",
    "website",
    "screenshots",
    "tls",
]

def make_zip(out_path):
    print(f"[*] Creating archive: {out_path}...")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in FILES_TO_INCLUDE:
            fpath = os.path.join(BASE_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, fname)
                print(f"  + Added: {fname}")

        for dname in DIRS_TO_INCLUDE:
            dpath = os.path.join(BASE_DIR, dname)
            if os.path.exists(dpath):
                for root, _, files in os.walk(dpath):
                    if "__pycache__" in root:
                        continue
                    for f in files:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        zf.write(full_p, rel_p)
                        print(f"  + Added: {rel_p}")
    print(f"[OK] Created archive: {out_path} ({os.path.getsize(out_path):,} bytes)")

def main():
    make_zip(ZIP_USN)
    make_zip(ZIP_GENERIC)
    print("\n[SUCCESS] Lab 12 packages successfully assembled.")

if __name__ == "__main__":
    main()
