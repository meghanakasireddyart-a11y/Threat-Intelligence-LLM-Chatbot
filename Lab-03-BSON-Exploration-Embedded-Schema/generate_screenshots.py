"""
Script to capture outputs of all lab activities and render them as terminal screenshots using Pillow with text wrapping.
"""

import os
import textwrap
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"
FONT_SIZE = 17
LINE_HEIGHT = 25
PADDING_X = 25
PADDING_TOP = 40
PADDING_BOTTOM = 25
WINDOW_TITLE_HEIGHT = 38
MAX_COLS = 105

def render_terminal_screenshot(text_content, output_image_path, title="Terminal - PyMongo Execution"):
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    bold_font = ImageFont.truetype(FONT_BOLD_PATH, FONT_SIZE)
    title_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)

    raw_lines = text_content.strip().split("\n")
    wrapped_lines = []
    for line in raw_lines:
        if len(line) > MAX_COLS and not line.startswith("+--") and not line.startswith("==="):
            # Wrap long line nicely with indent
            parts = textwrap.wrap(line, width=MAX_COLS, subsequent_indent="     ")
            wrapped_lines.extend(parts)
        else:
            wrapped_lines.append(line)

    char_width = 10.2
    max_line_len = min(MAX_COLS, max((len(l) for l in wrapped_lines), default=60))
    img_width = int(max(1050, max_line_len * char_width + PADDING_X * 2))
    img_height = WINDOW_TITLE_HEIGHT + PADDING_TOP + len(wrapped_lines) * LINE_HEIGHT + PADDING_BOTTOM

    # Background colors
    bg_color = (24, 24, 30)         # Modern Dark Slate #18181E
    title_bar_color = (36, 36, 44)  # #24242C
    text_color = (220, 222, 230)    # #DCDFE6

    image = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(image)

    # Draw Title Bar
    draw.rectangle([(0, 0), (img_width, WINDOW_TITLE_HEIGHT)], fill=title_bar_color)
    draw.line([(0, WINDOW_TITLE_HEIGHT), (img_width, WINDOW_TITLE_HEIGHT)], fill=(55, 55, 65), width=1)

    # Draw Mac/Linux-style window controls
    dot_radius = 6
    dot_y = WINDOW_TITLE_HEIGHT // 2
    # Red (close)
    draw.ellipse([(16, dot_y - dot_radius), (16 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 95, 86))
    # Yellow (minimize)
    draw.ellipse([(38, dot_y - dot_radius), (38 + 2 * dot_radius, dot_y + dot_radius)], fill=(255, 189, 46))
    # Green (maximize)
    draw.ellipse([(60, dot_y - dot_radius), (60 + 2 * dot_radius, dot_y + dot_radius)], fill=(39, 201, 63))

    # Draw Title text
    draw.text((img_width // 2 - 140, 9), title, font=title_font, fill=(180, 185, 195))

    # Draw text lines with syntax highlighting accents
    curr_y = WINDOW_TITLE_HEIGHT + 18
    for line in wrapped_lines:
        col = text_color
        f = font
        # Color cues based on prefix
        if "[OK]" in line or "[SUCCESS]" in line or "[PASS]" in line:
            col = (78, 215, 175)   # Mint Green #4ED7AF
        elif "[ERROR]" in line or "[REJECTED]" in line or "CRITICAL" in line:
            col = (255, 107, 107)  # Coral Red #FF6B6B
        elif line.startswith("===") or line.startswith("---") or line.startswith("+--"):
            col = (90, 170, 245)   # Sky Blue #5AAAF5
            f = bold_font
        elif line.strip().startswith("*") or line.strip().startswith("->"):
            col = (235, 160, 120)  # Peach #EBA078
        elif "Query" in line or "Step" in line or "PART" in line:
            col = (245, 215, 130)  # Golden Yellow #F5D782
            f = bold_font

        draw.text((PADDING_X, curr_y), line, font=f, fill=col)
        curr_y += LINE_HEIGHT

    image.save(output_image_path, "PNG", quality=95)
    print(f"[OK] Generated screenshot: {output_image_path} ({img_width}x{img_height})")

def main():
    activities = [
        {
            "name": "Activity 3.1",
            "script": "Activity_3_1/activity_3_1.py",
            "screenshot": "Activity_3_1/screenshot_activity_3_1.png",
            "title": "PowerShell - python Activity_3_1/activity_3_1.py"
        },
        {
            "name": "Activity 3.1 Try It Yourself",
            "script": "Activity_3_1_Try_It_Yourself/activity_3_1_try_it_yourself.py",
            "screenshot": "Activity_3_1_Try_It_Yourself/screenshot_activity_3_1_try_it_yourself.png",
            "title": "PowerShell - python Activity_3_1_Try_It_Yourself/activity_3_1_try_it_yourself.py"
        },
        {
            "name": "Activity 3.2",
            "script": "Activity_3_2/activity_3_2.py",
            "screenshot": "Activity_3_2/screenshot_activity_3_2.png",
            "title": "PowerShell - python Activity_3_2/activity_3_2.py"
        },
        {
            "name": "Activity 3.2 Try It Yourself",
            "script": "Activity_3_2_Try_It_Yourself/activity_3_2_try_it_yourself.py",
            "screenshot": "Activity_3_2_Try_It_Yourself/screenshot_activity_3_2_try_it_yourself.png",
            "title": "PowerShell - python Activity_3_2_Try_It_Yourself/activity_3_2_try_it_yourself.py"
        }
    ]

    for act in activities:
        print(f"\nRunning {act['name']}...")
        result = subprocess.run(["py", "-3", act["script"]], capture_output=True, text=True)
        stdout = result.stdout
        if result.stderr:
            stdout += "\n" + result.stderr
        render_terminal_screenshot(stdout, act["screenshot"], act["title"])

if __name__ == "__main__":
    main()
