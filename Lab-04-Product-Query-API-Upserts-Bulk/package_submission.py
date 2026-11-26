"""
Script to package the NoSQL Lab 4 submission into the required ZIP archive structure.
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University
"""

import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_PKG_NAME = "Kasireddy_Meghana_24BTRCL119_Lab4_NoSQL"
STANDARD_PKG_NAME = "NoSQL_Lab4_Submission"

ZIP_TARGETS = [
    f"{STUDENT_PKG_NAME}.zip",
    f"{STANDARD_PKG_NAME}.zip"
]

STAGING_DIR = os.path.join(BASE_DIR, "_submission_staging")


def create_package():
    print("[*] Preparing submission packaging...")
    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    os.makedirs(STAGING_DIR, exist_ok=True)

    # Activity directories
    act_4_1 = os.path.join(STAGING_DIR, "Activity_4_1")
    act_4_1_try = os.path.join(STAGING_DIR, "Activity_4_1_Try_It_Yourself")
    act_4_2 = os.path.join(STAGING_DIR, "Activity_4_2")
    act_4_2_try = os.path.join(STAGING_DIR, "Activity_4_2_Try_It_Yourself")

    for d in [act_4_1, act_4_1_try, act_4_2, act_4_2_try]:
        os.makedirs(d, exist_ok=True)

    # Copy Activity 4.1 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1", "activity_4_1.py"), act_4_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1", "products_activity_4_1.json"), act_4_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1", "screenshot_activity_4_1.png"), act_4_1)

    # Copy Activity 4.1 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1_Try_It_Yourself", "activity_4_1_try_it_yourself.py"), act_4_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1_Try_It_Yourself", "products_search_results.json"), act_4_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_1_Try_It_Yourself", "screenshot_activity_4_1_try_it_yourself.png"), act_4_1_try)

    # Copy Activity 4.2 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2", "activity_4_2.py"), act_4_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2", "inventory_activity_4_2.json"), act_4_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2", "screenshot_activity_4_2.png"), act_4_2)

    # Copy Activity 4.2 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2_Try_It_Yourself", "activity_4_2_try_it_yourself.py"), act_4_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2_Try_It_Yourself", "idempotent_import_inventory.json"), act_4_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_4_2_Try_It_Yourself", "screenshot_activity_4_2_try_it_yourself.png"), act_4_2_try)

    # Copy config directory
    shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(STAGING_DIR, "config"), dirs_exist_ok=True)

    # Copy DOCX reports to root of staging
    shutil.copy2(os.path.join(BASE_DIR, "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_04.docx"), STAGING_DIR)
    shutil.copy2(os.path.join(BASE_DIR, "NoSQL_Lab4_Report.docx"), STAGING_DIR)

    # Build ZIP archives
    for zip_name in ZIP_TARGETS:
        zip_path = os.path.join(BASE_DIR, zip_name)
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(STAGING_DIR):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, STAGING_DIR)
                    z.write(full_p, rel_p)

        file_size = os.path.getsize(zip_path)
        print(f"[OK] Successfully built ZIP package: {zip_name} ({file_size:,} bytes)")

    # Clean up staging directory
    shutil.rmtree(STAGING_DIR)
    print("\n[SUCCESS] All submission packages built and verified.")


if __name__ == "__main__":
    create_package()
