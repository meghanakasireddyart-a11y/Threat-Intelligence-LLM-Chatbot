"""Script to execute lab scripts, capture output, and render beautiful Windows Terminal screenshots."""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont


def capture_script_output(script_name: str) -> tuple[str, str]:
    """Run a script and capture its stdout."""
    cmd = ["py", "-3", script_name]
    cmd_str = f"PS C:\\Users\\Meghana Kasireddy\\NoSQL-LAB1> python {script_name}"
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    return cmd_str, res.stdout


def render_terminal_screenshot(cmd_str: str, output_text: str, out_img_path: str, title: str):
    """Render terminal screenshot using PIL with dark theme and Consolas font."""
    font_path = "C:\\Windows\\Fonts\\consola.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\consolab.ttf"
    
    font_size = 14
    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype(font_bold_path, font_size)
    title_font = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 12)

    # Prepare lines
    lines = [cmd_str, ""] + output_text.splitlines()

    # Calculate dimensions
    char_w = 8.5
    line_h = 20
    max_line_len = max(len(l) for l in lines) if lines else 80
    term_w = max(int(max_line_len * char_w) + 60, 950)
    title_bar_h = 36
    term_h = title_bar_h + (len(lines) * line_h) + 40

    img = Image.new("RGBA", (term_w, term_h), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)

    # Terminal background
    bg_color = (18, 18, 18, 255)
    draw.rectangle([0, title_bar_h, term_w, term_h], fill=bg_color)

    # Title bar background
    title_bar_color = (36, 36, 36, 255)
    draw.rectangle([0, 0, term_w, title_bar_h], fill=title_bar_color)

    # Window buttons (mac/modern terminal style dots)
    draw.ellipse([14, 11, 26, 23], fill=(255, 95, 87))   # close (red)
    draw.ellipse([34, 11, 46, 23], fill=(254, 188, 46))  # minimize (yellow)
    draw.ellipse([54, 11, 66, 23], fill=(40, 201, 64))   # maximize (green)

    # Title text
    draw.text((80, 10), title, font=title_font, fill=(200, 200, 200))

    # Render lines
    y = title_bar_h + 16
    for i, line in enumerate(lines):
        x = 24
        if i == 0:
            # Prompt line
            draw.text((x, y), line, font=font_bold, fill=(80, 220, 100))
        elif "[OK]" in line:
            # Success line
            draw.text((x, y), line, font=font, fill=(100, 230, 120))
        elif line.startswith("===") or line.startswith("---"):
            draw.text((x, y), line, font=font_bold, fill=(90, 180, 250))
        elif "Expected answers:" in line or "Expected answers" in line:
            draw.text((x, y), line, font=font_bold, fill=(255, 215, 0))
        elif "[MATCH VALIDATED]" in line:
            draw.text((x, y), line, font=font, fill=(130, 235, 150))
        elif "┌" in line or "├" in line or "└" in line or "│" in line:
            draw.text((x, y), line, font=font, fill=(180, 190, 205))
        elif "Activity" in line or "Lab 1." in line:
            draw.text((x, y), line, font=font_bold, fill=(240, 240, 240))
        else:
            draw.text((x, y), line, font=font, fill=(215, 220, 225))
        y += line_h

    img.save(out_img_path)
    print(f"[OK] Generated {out_img_path} ({term_w}x{term_h})")


def main():
    scripts = [
        ("lab_01_classify_databases.py", "screenshot_lab_01.png", "Windows PowerShell - Activity 1.1 (lab_01_classify_databases.py)"),
        ("lab_01_try_yourself.py", "screenshot_lab_01_tryit.png", "Windows PowerShell - Activity 1.1 Try It Yourself (lab_01_try_yourself.py)"),
        ("lab_02_map_application.py", "screenshot_lab_02.png", "Windows PowerShell - Activity 1.2 (lab_02_map_application.py)"),
        ("lab_02_try_yourself.py", "screenshot_lab_02_tryit.png", "Windows PowerShell - Activity 1.2 Try It Yourself (lab_02_try_yourself.py)")
    ]

    for script, out_img, title in scripts:
        cmd_str, out_text = capture_script_output(script)
        render_terminal_screenshot(cmd_str, out_text, out_img, title)


if __name__ == "__main__":
    main()
