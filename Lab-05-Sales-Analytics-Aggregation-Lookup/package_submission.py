"""Script to package the NoSQL Lab 5 submission into the required ZIP archive structure.
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University
"""

import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENT_PKG_NAME = "Kasireddy_Meghana_24BTRCL119_Lab5_NoSQL"
STANDARD_PKG_NAME = "NoSQL_Lab5_Submission"

ZIP_TARGETS = [
    f"{STUDENT_PKG_NAME}.zip",
    f"{STANDARD_PKG_NAME}.zip"
]

STAGING_DIR = os.path.join(BASE_DIR, "_submission_staging")


def create_package():
    print("[*] Preparing Lab 5 submission packaging...")
    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    os.makedirs(STAGING_DIR, exist_ok=True)

    # Activity directories
    act_5_1 = os.path.join(STAGING_DIR, "Activity_5_1")
    act_5_1_try = os.path.join(STAGING_DIR, "Activity_5_1_Try_It_Yourself")
    act_5_2 = os.path.join(STAGING_DIR, "Activity_5_2")
    act_5_2_try = os.path.join(STAGING_DIR, "Activity_5_2_Try_It_Yourself")

    for d in [act_5_1, act_5_1_try, act_5_2, act_5_2_try]:
        os.makedirs(d, exist_ok=True)

    # Copy Activity 5.1 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1", "activity_5_1.py"), act_5_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1", "sales_analytics_output.json"), act_5_1)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1", "screenshot_activity_5_1.png"), act_5_1)

    # Copy Activity 5.1 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1_Try_It_Yourself", "activity_5_1_try_it_yourself.py"), act_5_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1_Try_It_Yourself", "conditional_bucketing_output.json"), act_5_1_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_1_Try_It_Yourself", "screenshot_activity_5_1_try_it_yourself.png"), act_5_1_try)

    # Copy Activity 5.2 files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2", "activity_5_2.py"), act_5_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2", "lookup_joins_output.json"), act_5_2)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2", "screenshot_activity_5_2.png"), act_5_2)

    # Copy Activity 5.2 Try It Yourself files
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2_Try_It_Yourself", "activity_5_2_try_it_yourself.py"), act_5_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2_Try_It_Yourself", "customer_orders_portfolio.json"), act_5_2_try)
    shutil.copy2(os.path.join(BASE_DIR, "Activity_5_2_Try_It_Yourself", "screenshot_activity_5_2_try_it_yourself.png"), act_5_2_try)

    # Copy config directory
    shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(STAGING_DIR, "config"), dirs_exist_ok=True)

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
