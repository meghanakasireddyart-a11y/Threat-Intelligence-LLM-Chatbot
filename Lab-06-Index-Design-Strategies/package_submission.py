"""Script to package the NoSQL Lab 6 submission into the required ZIP archive structure.
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University
"""

import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_PKG_NAME = "Kasireddy_Meghana_24BTRCL119_Lab6_NoSQL"
STANDARD_PKG_NAME = "NoSQL_Lab6_Submission"

ZIP_TARGETS = [
    f"{STUDENT_PKG_NAME}.zip",
    f"{STANDARD_PKG_NAME}.zip"
]

STAGING_DIR = os.path.join(BASE_DIR, "_submission_staging")


def create_package():
    print("[*] Preparing Lab 6 submission packaging...")
    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    os.makedirs(STAGING_DIR, exist_ok=True)

    # Activity directories
    act_6_1 = os.path.join(STAGING_DIR, "Activity_6_1")
    act_6_1_try = os.path.join(STAGING_DIR, "Activity_6_1_Try_It_Yourself")
    act_6_2 = os.path.join(STAGING_DIR, "Activity_6_2")
    act_6_2_try = os.path.join(STAGING_DIR, "Activity_6_2_Try_It_Yourself")

    for d in [act_6_1, act_6_1_try, act_6_2, act_6_2_try]:
        os.makedirs(d, exist_ok=True)

    # Copy Activity 6.1 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1", "activity_6_1.py"), act_6_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1", "index_design_output.json"), act_6_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1", "screenshot_activity_6_1.png"), act_6_1)

    # Copy Activity 6.1 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1_Try_It_Yourself", "activity_6_1_try_it_yourself.py"), act_6_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1_Try_It_Yourself", "compound_prefix_analysis.json"), act_6_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_1_Try_It_Yourself", "screenshot_activity_6_1_try_it_yourself.png"), act_6_1_try)

    # Copy Activity 6.2 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2", "activity_6_2.py"), act_6_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2", "index_strategies_output.json"), act_6_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2", "screenshot_activity_6_2.png"), act_6_2)

    # Copy Activity 6.2 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2_Try_It_Yourself", "activity_6_2_try_it_yourself.py"), act_6_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2_Try_It_Yourself", "covered_esr_deepdive.json"), act_6_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_6_2_Try_It_Yourself", "screenshot_activity_6_2_try_it_yourself.png"), act_6_2_try)

    # Copy config directory
    shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(STAGING_DIR, "config"), dirs_exist_ok=True)

    # Copy root scripts and report
    shutil.copy2(os.path.join(BASE_DIR, "lab_01_index_design.py"), STAGING_DIR)
    shutil.copy2(os.path.join(BASE_DIR, "lab_02_index_strategies.py"), STAGING_DIR)
    shutil.copy2(os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_06.docx"), STAGING_DIR)

    # Build ZIP Archives
    for zip_filename in ZIP_TARGETS:
        zip_path = os.path.join(BASE_DIR, zip_filename)
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(STAGING_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, STAGING_DIR)
                    zipf.write(file_path, rel_path)

        size_kb = os.path.getsize(zip_path) / 1024
        print(f"[SUCCESS] Created submission package: {zip_filename} ({size_kb:,.1f} KB)")

    # Clean up staging directory
    shutil.rmtree(STAGING_DIR)
    print("[*] Staging directory removed. Packaging complete!")


if __name__ == "__main__":
    create_package()
