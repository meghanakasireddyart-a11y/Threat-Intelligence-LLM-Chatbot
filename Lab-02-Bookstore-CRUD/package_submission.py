"""Script to package the Lab 2 submission into a clean ZIP archive with 1-directory per activity."""

import os
import shutil
import zipfile

SUBMISSION_NAME = "Kasireddy_Meghana_24BTRCL119_Lab2_NoSQL"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, SUBMISSION_NAME)
ZIP_FILE = os.path.join(BASE_DIR, f"{SUBMISSION_NAME}.zip")

# Remove previous packaging directory if exists
if os.path.exists(PACKAGE_DIR):
    shutil.rmtree(PACKAGE_DIR)

# Create Activity 2.1 and Activity 2.2 directories
act1_dir = os.path.join(PACKAGE_DIR, "Activity 2.1")
act2_dir = os.path.join(PACKAGE_DIR, "Activity 2.2")
os.makedirs(act1_dir, exist_ok=True)
os.makedirs(act2_dir, exist_ok=True)

# Copy files for Activity 2.1
shutil.copy2(os.path.join(BASE_DIR, "lab_01_setup_environment.py"), act1_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_01_setup_environment.json"), act1_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_01_try_yourself.py"), act1_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_01_try_yourself.json"), act1_dir)
shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(act1_dir, "config"), dirs_exist_ok=True)

# Copy files for Activity 2.2
shutil.copy2(os.path.join(BASE_DIR, "lab_02_bookstore_crud.py"), act2_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_02_bookstore_crud.json"), act2_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_02_try_yourself.py"), act2_dir)
shutil.copy2(os.path.join(BASE_DIR, "lab_02_try_yourself.json"), act2_dir)
shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(act2_dir, "config"), dirs_exist_ok=True)

# Copy shared config and docx to root of package
shutil.copytree(os.path.join(BASE_DIR, "config"), os.path.join(PACKAGE_DIR, "config"), dirs_exist_ok=True)
docx_name = "Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_02.docx"
shutil.copy2(os.path.join(BASE_DIR, docx_name), PACKAGE_DIR)

# Also copy docx inside each activity folder for evaluator convenience
shutil.copy2(os.path.join(BASE_DIR, docx_name), act1_dir)
shutil.copy2(os.path.join(BASE_DIR, docx_name), act2_dir)

# Create zip file
if os.path.exists(ZIP_FILE):
    os.remove(ZIP_FILE)

with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PACKAGE_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, BASE_DIR)
            z.write(full_path, rel_path)

print(f"[OK] Created ZIP package: {ZIP_FILE} ({os.path.getsize(ZIP_FILE)} bytes)")

# Print contents of ZIP
print("\nContents of ZIP archive:")
with zipfile.ZipFile(ZIP_FILE, "r") as z:
    for name in z.namelist():
        print("  ", name)
