"""
Capture live terminal execution outputs for all Lab 4 activities and
render them as high-resolution dark-mode terminal window screenshots using Pillow.
"""

import os
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
        if len(line) > MAX_COLS and not line.startswith("+--") and not line.startswith("===") and not line.startswith("---"):
            parts = textwrap.wrap(line, width=MAX_COLS, subsequent_indent="     ")
            wrapped_lines.extend(parts)
        else:
            wrapped_lines.append(line)

    char_width = 9.8
    max_line_len = min(MAX_COLS, max((len(l) for l in wrapped_lines), default=70))
    img_width = int(max(1050, max_line_len * char_width + PADDING_X * 2))
    img_height = WINDOW_TITLE_HEIGHT + PADDING_TOP + len(wrapped_lines) * LINE_HEIGHT + PADDING_BOTTOM

    # Background colors (VS Code / Terminal Dark Slate)
    bg_color = (20, 22, 28)         # Deep slate #14161C
    title_bar_color = (32, 35, 45)  # #20232D
    text_color = (220, 225, 235)    # #DCE1EB

    image = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(image)

    # Draw Title Bar
    draw.rectangle([(0, 0), (img_width, WINDOW_TITLE_HEIGHT)], fill=title_bar_color)
    draw.line([(0, WINDOW_TITLE_HEIGHT), (img_width, WINDOW_TITLE_HEIGHT)], fill=(50, 55, 70), width=1)

    # Draw Window Control Dots (macOS / Linux style)
    dot_radius = 6
    dot_y = WINDOW_TITLE_HEIGHT // 2
    # Red (Close)
    draw.ellipse([(16, dot_y - dot_radius), (16 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 95, 86))
    # Yellow (Minimize)
    draw.ellipse([(38, dot_y - dot_radius), (38 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 189, 46))
    # Green (Maximize)
    draw.ellipse([(60, dot_y - dot_radius), (60 + 2 * dot_radius, dot_y + dot_radius)], fill=(39, 201, 63))

    # Window title text centered
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((img_width - title_w) // 2, 9), title, font=title_font, fill=(180, 188, 205))

    # Draw Text Lines with Syntax Coloring
    curr_y = WINDOW_TITLE_HEIGHT + 16
    for line in wrapped_lines:
        col = text_color
        f = font

        # Syntax color heuristics
        if "[OK]" in line or "[SUCCESS]" in line or "[PASS]" in line or "VERIFIED" in line:
            col = (72, 218, 160)   # Mint green
        elif "[ERROR]" in line or "[REJECTED]" in line or "FAIL" in line:
            col = (255, 105, 105)  # Soft red
        elif line.startswith("===") or line.startswith("---"):
            col = (90, 175, 255)   # Sky blue
            f = bold_font
        elif line.startswith(">>>") or line.startswith("SKU "):
            col = (250, 210, 120)  # Warm yellow
            f = bold_font
        elif "Case " in line or "Instruction" in line or "RUN " in line or "Test " in line:
            col = (255, 205, 100)  # Amber
            f = bold_font
        elif "Student:" in line or "Pattern Searched:" in line or "Requirement:" in line:
            col = (210, 170, 245)  # Lavender

        draw.text((PADDING_X, curr_y), line, font=f, fill=col)
        curr_y += LINE_HEIGHT

    # Save output
    image.save(output_image_path, "PNG", quality=95)
    print(f"[OK] Generated screenshot: {output_image_path} ({img_width}x{img_height})")


def run_and_capture(cmd, cwd=None):
    """Run command and capture stdout/stderr."""
    print(f"[*] Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    return proc.stdout


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    tasks = [
        {
            "name": "Activity 4.1",
            "script": os.path.join(base_dir, "Activity_4_1", "activity_4_1.py"),
            "screenshot": os.path.join(base_dir, "Activity_4_1", "screenshot_activity_4_1.png"),
            "title": "PowerShell - python Activity_4_1/activity_4_1.py"
        },
        {
            "name": "Activity 4.1 Try It Yourself",
            "script": os.path.join(base_dir, "Activity_4_1_Try_It_Yourself", "activity_4_1_try_it_yourself.py"),
            "screenshot": os.path.join(base_dir, "Activity_4_1_Try_It_Yourself", "screenshot_activity_4_1_try_it_yourself.png"),
            "title": "PowerShell - python Activity_4_1_Try_It_Yourself/activity_4_1_try_it_yourself.py"
        },
        {
            "name": "Activity 4.2",
            "script": os.path.join(base_dir, "Activity_4_2", "activity_4_2.py"),
            "screenshot": os.path.join(base_dir, "Activity_4_2", "screenshot_activity_4_2.png"),
            "title": "PowerShell - python Activity_4_2/activity_4_2.py"
        },
        {
            "name": "Activity 4.2 Try It Yourself",
            "script": os.path.join(base_dir, "Activity_4_2_Try_It_Yourself", "activity_4_2_try_it_yourself.py"),
            "screenshot": os.path.join(base_dir, "Activity_4_2_Try_It_Yourself", "screenshot_activity_4_2_try_it_yourself.png"),
            "title": "PowerShell - python Activity_4_2_Try_It_Yourself/activity_4_2_try_it_yourself.py"
        }
    ]

    for task in tasks:
        output_text = run_and_capture(["py", "-3", task["script"]], cwd=base_dir)
        render_terminal_screenshot(output_text, task["screenshot"], title=task["title"])

    print("\n[SUCCESS] All activity screenshots generated successfully.")


if __name__ == "__main__":
    main()
