"""Generate terminal window screenshots for Lab 6 activities.
Uses Pillow to create high-resolution dark-mode terminal captures.
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 6
"""

import os
import sys
import textwrap
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"
FONT_SIZE = 16
LINE_HEIGHT = 24
PADDING_X = 24
PADDING_TOP = 36
PADDING_BOTTOM = 24
WINDOW_TITLE_HEIGHT = 38
MAX_COLS = 110


def render_terminal_screenshot(text_content, output_image_path, title="Terminal - PyMongo Execution"):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    bold_font = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE)
    title_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)

    raw_lines = text_content.strip().split("\n")
    wrapped_lines = []
    for line in raw_lines:
        if len(line) > MAX_COLS and not any(line.startswith(c) for c in ["┌", "├", "└", "│", "===", "---"]):
            parts = textwrap.wrap(line, width=MAX_COLS, subsequent_indent="     ")
            wrapped_lines.extend(parts)
        else:
            wrapped_lines.append(line)

    char_width = 9.8
    max_line_len = min(MAX_COLS, max((len(l) for l in wrapped_lines), default=70))
    img_width = int(max(1050, max_line_len * char_width + PADDING_X * 2))
    img_height = WINDOW_TITLE_HEIGHT + PADDING_TOP + len(wrapped_lines) * LINE_HEIGHT + PADDING_BOTTOM

    bg_color = (20, 22, 28)         # Deep slate #14161C
    title_bar_color = (32, 35, 45)  # #20232D
    text_color = (220, 225, 235)    # #DCE1EB

    image = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(image)

    # Title Bar
    draw.rectangle([(0, 0), (img_width, WINDOW_TITLE_HEIGHT)], fill=title_bar_color)
    draw.line([(0, WINDOW_TITLE_HEIGHT), (img_width, WINDOW_TITLE_HEIGHT)], fill=(50, 55, 70), width=1)

    # Window Control Dots (macOS style)
    dot_radius = 6
    dot_y = WINDOW_TITLE_HEIGHT // 2
    draw.ellipse([(16, dot_y - dot_radius), (16 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 95, 86))
    draw.ellipse([(38, dot_y - dot_radius), (38 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 189, 46))
    draw.ellipse([(60, dot_y - dot_radius), (60 + 2 * dot_radius, dot_y + dot_radius)], fill=(39, 201, 63))

    # Window Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_w) // 2, 9), title, font=title_font, fill=(180, 188, 205))

    # Text rendering with syntax highlighting
    curr_y = WINDOW_TITLE_HEIGHT + 16
    for line in wrapped_lines:
        col = text_color
        f = font

        if "[OK]" in line or "[SUCCESS]" in line or "[PASS]" in line or "VERIFIED" in line or "[GOOD INDEX" in line:
            col = (72, 218, 160)   # Mint green
        elif "[ERROR]" in line or "[REJECTED]" in line or "FAIL" in line or "[BAD INDEX" in line or "COLLSCAN" in line:
            col = (255, 105, 105)  # Soft red / coral
        elif line.startswith("===") or line.startswith("---") or "Lab 6" in line:
            col = (90, 175, 255)   # Sky blue
            f = bold_font
        elif "Stage:" in line or "Docs examined:" in line or "Index:" in line or "Speedup" in line:
            col = (250, 210, 120)  # Warm yellow
            f = bold_font
        elif "Author:" in line or "Course:" in line or "Student:" in line:
            col = (210, 170, 245)  # Lavender
        elif any(c in line for c in ["┌", "├", "└", "│"]):
            col = (130, 200, 255)  # Cyan table borders

        draw.text((PADDING_X, curr_y), line, font=f, fill=col)
        curr_y += LINE_HEIGHT

    image.save(output_image_path, "PNG", quality=95)
    print(f"[OK] Generated screenshot: {output_image_path} ({img_width}x{img_height})")


def run_and_capture(cmd, cwd=None):
    print(f"[*] Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    return proc.stdout


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    py_exec = sys.executable

    targets = [
        {
            "script": os.path.join(base_dir, "Activity_6_1", "activity_6_1.py"),
            "img": os.path.join(base_dir, "Activity_6_1", "screenshot_activity_6_1.png"),
            "title": "Terminal - Activity 6.1: Index Design for Query Workload",
            "cwd": os.path.join(base_dir, "Activity_6_1")
        },
        {
            "script": os.path.join(base_dir, "Activity_6_1_Try_It_Yourself", "activity_6_1_try_it_yourself.py"),
            "img": os.path.join(base_dir, "Activity_6_1_Try_It_Yourself", "screenshot_activity_6_1_try_it_yourself.png"),
            "title": "Terminal - Activity 6.1 Try-It-Yourself: Prefix Rule & Phone Book Analogy",
            "cwd": os.path.join(base_dir, "Activity_6_1_Try_It_Yourself")
        },
        {
            "script": os.path.join(base_dir, "Activity_6_2", "activity_6_2.py"),
            "img": os.path.join(base_dir, "Activity_6_2", "screenshot_activity_6_2.png"),
            "title": "Terminal - Activity 6.2: Compare Index Strategies (Writes vs Reads)",
            "cwd": os.path.join(base_dir, "Activity_6_2")
        },
        {
            "script": os.path.join(base_dir, "Activity_6_2_Try_It_Yourself", "activity_6_2_try_it_yourself.py"),
            "img": os.path.join(base_dir, "Activity_6_2_Try_It_Yourself", "screenshot_activity_6_2_try_it_yourself.png"),
            "title": "Terminal - Activity 6.2 Try-It-Yourself: Covered Payloads & ESR Sort",
            "cwd": os.path.join(base_dir, "Activity_6_2_Try_It_Yourself")
        }
    ]

    for t in targets:
        output_txt = run_and_capture([py_exec, t["script"]], cwd=t["cwd"])
        render_terminal_screenshot(output_txt, t["img"], title=t["title"])

    print("\n[SUCCESS] All activity screenshots generated successfully!")


if __name__ == "__main__":
    main()
