"""
Package the final ZIP submission for Lab 8 according to the required format.
Student: Kasireddy Meghana (24BTRCL119)
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_NAME_STUDENT = os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_Lab8_NoSQL.zip")
ZIP_NAME_GENERIC = os.path.join(BASE_DIR, "NoSQL_Lab8_Submission.zip")

ACTIVITIES = [
    "Activity_8_1",
    "Activity_8_1_Try_It_Yourself",
    "Activity_8_2",
    "Activity_8_2_Try_It_Yourself"
]

DOCX_FILE = "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_08.docx"


def create_submission_zip(output_path):
    print(f"Creating submission ZIP: {output_path}")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add Activity folders and their files
        for act in ACTIVITIES:
            act_dir = os.path.join(BASE_DIR, act)
            if os.path.exists(act_dir):
                for root, dirs, files in os.walk(act_dir):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        zf.write(full_p, rel_p)
                        print(f"  + Added: {rel_p}")

        # Add the DOCX file
        docx_path = os.path.join(BASE_DIR, DOCX_FILE)
        if os.path.exists(docx_path):
            zf.write(docx_path, DOCX_FILE)
            print(f"  + Added: {DOCX_FILE}")

        # Add screenshots directory for completeness
        screenshots_dir = os.path.join(BASE_DIR, "screenshots")
        if os.path.exists(screenshots_dir):
            for file in os.listdir(screenshots_dir):
                if file.endswith(".png"):
                    full_p = os.path.join(screenshots_dir, file)
                    rel_p = os.path.join("screenshots", file)
                    zf.write(full_p, rel_p)
                    print(f"  + Added: {rel_p}")

    size_kb = os.path.getsize(output_path) / 1024
    print(f"[OK] Created {output_path} ({size_kb:.2f} KB)")


if __name__ == "__main__":
    create_submission_zip(ZIP_NAME_STUDENT)
    create_submission_zip(ZIP_NAME_GENERIC)
