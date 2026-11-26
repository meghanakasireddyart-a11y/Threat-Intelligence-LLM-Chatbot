"""
Package the lab submission into the required zip file format.
"""

import os
import zipfile

ZIP_NAME = "NoSQL_Lab3_Submission.zip"

FILES_TO_INCLUDE = [
    # DOCX Report
    ("NoSQL_Lab3_Report.docx", "NoSQL_Lab3_Report.docx"),

    # Activity 3.1
    ("Activity_3_1/activity_3_1.py", "Activity_3_1/activity_3_1.py"),
    ("Activity_3_1/courses.json", "Activity_3_1/courses.json"),
    ("Activity_3_1/screenshot_activity_3_1.png", "Activity_3_1/screenshot_activity_3_1.png"),

    # Activity 3.1 Try It Yourself
    ("Activity_3_1_Try_It_Yourself/activity_3_1_try_it_yourself.py", "Activity_3_1_Try_It_Yourself/activity_3_1_try_it_yourself.py"),
    ("Activity_3_1_Try_It_Yourself/courses_with_prerequisites.json", "Activity_3_1_Try_It_Yourself/courses_with_prerequisites.json"),
    ("Activity_3_1_Try_It_Yourself/screenshot_activity_3_1_try_it_yourself.png", "Activity_3_1_Try_It_Yourself/screenshot_activity_3_1_try_it_yourself.png"),

    # Activity 3.2
    ("Activity_3_2/activity_3_2.py", "Activity_3_2/activity_3_2.py"),
    ("Activity_3_2/posts_embedded.json", "Activity_3_2/posts_embedded.json"),
    ("Activity_3_2/posts_referenced.json", "Activity_3_2/posts_referenced.json"),
    ("Activity_3_2/comments.json", "Activity_3_2/comments.json"),
    ("Activity_3_2/screenshot_activity_3_2.png", "Activity_3_2/screenshot_activity_3_2.png"),

    # Activity 3.2 Try It Yourself
    ("Activity_3_2_Try_It_Yourself/activity_3_2_try_it_yourself.py", "Activity_3_2_Try_It_Yourself/activity_3_2_try_it_yourself.py"),
    ("Activity_3_2_Try_It_Yourself/viral_post_alternative_design.json", "Activity_3_2_Try_It_Yourself/viral_post_alternative_design.json"),
    ("Activity_3_2_Try_It_Yourself/screenshot_activity_3_2_try_it_yourself.png", "Activity_3_2_Try_It_Yourself/screenshot_activity_3_2_try_it_yourself.png"),
]

def main():
    print(f"Creating submission zip: {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in FILES_TO_INCLUDE:
            if os.path.exists(src):
                zf.write(src, arcname)
                print(f"  + Added: {arcname}")
            else:
                print(f"  ! Missing file: {src}")

    file_size = os.path.getsize(ZIP_NAME)
    print(f"\n[OK] Successfully created '{ZIP_NAME}' ({file_size:,} bytes).")

if __name__ == "__main__":
    main()
