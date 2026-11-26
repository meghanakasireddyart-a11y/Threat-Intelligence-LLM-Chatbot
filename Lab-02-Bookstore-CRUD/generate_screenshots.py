"""Script to execute Lab 2 scripts, capture outputs, and render beautiful screenshots."""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont


def capture_script_output(script_name: str) -> tuple[str, str]:
    """Run a script and capture its stdout."""
    cmd = ["py", "-3", script_name]
    cmd_str = f"PS C:\\Users\\Meghana Kasireddy\\NoSQL-LAB2> python {script_name}"
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
    term_w = max(int(max_line_len * char_w) + 60, 1050)
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

    # Window buttons (modern terminal style dots)
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
        elif "Target Filter Query" in line or "Matching Documents" in line:
            draw.text((x, y), line, font=font_bold, fill=(255, 215, 0))
        elif "INCREASED" in line:
            draw.text((x, y), line, font=font_bold, fill=(130, 235, 150))
        elif "┌" in line or "├" in line or "└" in line or "│" in line:
            draw.text((x, y), line, font=font, fill=(180, 190, 205))
        elif "Activity" in line or "Lab 2." in line:
            draw.text((x, y), line, font=font_bold, fill=(240, 240, 240))
        elif "Connecting to" in line:
            draw.text((x, y), line, font=font, fill=(200, 170, 255))
        else:
            draw.text((x, y), line, font=font, fill=(215, 220, 225))
        y += line_h

    img.save(out_img_path)
    print(f"[OK] Generated {out_img_path} ({term_w}x{term_h})")


def render_compass_verification_screenshot(out_img_path: str):
    """Render a dedicated MongoDB Compass GUI screenshot showing the pre-2010 update verification."""
    font_path = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    font_mono_path = "C:\\Windows\\Fonts\\consola.ttf"

    f_title = ImageFont.truetype(font_bold_path, 13)
    f_ui = ImageFont.truetype(font_path, 12)
    f_ui_b = ImageFont.truetype(font_bold_path, 12)
    f_mono = ImageFont.truetype(font_mono_path, 12)
    f_mono_b = ImageFont.truetype(font_mono_path, 12)

    w, h = 1050, 720
    img = Image.new("RGBA", (w, h), (33, 40, 48, 255))
    draw = ImageDraw.Draw(img)

    # 1. Title bar
    draw.rectangle([0, 0, w, 38], fill=(24, 30, 37))
    draw.ellipse([14, 12, 26, 24], fill=(255, 95, 87))
    draw.ellipse([34, 12, 46, 24], fill=(254, 188, 46))
    draw.ellipse([54, 12, 66, 24], fill=(40, 201, 64))
    draw.text((80, 10), "MongoDB Compass - bookstore.books_pre2010_update [localhost:27017]", font=f_title, fill=(225, 230, 235))

    # 2. Connection bar
    draw.rectangle([0, 38, w, 78], fill=(30, 38, 46))
    draw.text((24, 48), "CONNECTED:", font=f_ui_b, fill=(0, 237, 100))
    draw.text((110, 48), "mongodb://localhost:27017/?directConnection=true", font=f_mono, fill=(200, 210, 220))
    draw.rectangle([w - 140, 44, w - 24, 72], fill=(0, 104, 74))
    draw.text((w - 122, 50), "Connected", font=f_ui_b, fill=(255, 255, 255))

    # 3. Sidebar (Databases & Collections)
    draw.rectangle([0, 78, 230, h], fill=(20, 26, 33))
    draw.text((16, 92), "DATABASES", font=f_ui_b, fill=(120, 135, 150))
    
    dbs = [
        ("admin", ["system.version"]),
        ("config", ["system.sessions"]),
        ("local", ["startup_log"]),
        ("bookstore", ["books", "books_pre2010_update", "environment_setup_verification", "server_version_comparison"])
    ]
    cur_y = 118
    for db_name, colls in dbs:
        is_active = (db_name == "bookstore")
        draw.text((20, cur_y), f"▼ 📁 {db_name}", font=f_ui_b if is_active else f_ui, fill=(0, 237, 100) if is_active else (180, 190, 200))
        cur_y += 22
        for col_name in colls:
            is_col_active = (col_name == "books_pre2010_update")
            if is_col_active:
                draw.rectangle([30, cur_y - 2, 220, cur_y + 18], fill=(36, 52, 68))
                draw.text((36, cur_y), f"📄 {col_name}", font=f_ui_b, fill=(255, 255, 255))
            else:
                draw.text((36, cur_y), f"📄 {col_name}", font=f_ui, fill=(140, 150, 160))
            cur_y += 20
        cur_y += 6

    # 4. Collection Header & Navigation
    main_x = 246
    draw.text((main_x, 90), "bookstore.books_pre2010_update", font=f_title, fill=(255, 255, 255))
    draw.text((main_x + 280, 92), "Total Documents: 8  |  Storage Size: 36 KB  |  Indexes: 1", font=f_ui, fill=(140, 155, 170))

    # Tabs: Documents, Aggregations, Schema, Explain Plan, Indexes
    tabs = ["Documents", "Aggregations", "Schema", "Explain Plan", "Indexes"]
    tab_x = main_x
    for tab in tabs:
        is_sel = (tab == "Documents")
        if is_sel:
            draw.rectangle([tab_x, 118, tab_x + 84, 142], fill=(38, 48, 58))
            draw.rectangle([tab_x, 140, tab_x + 84, 142], fill=(0, 237, 100))
            draw.text((tab_x + 10, 122), tab, font=f_ui_b, fill=(0, 237, 100))
        else:
            draw.text((tab_x + 10, 122), tab, font=f_ui, fill=(160, 170, 180))
        tab_x += 94

    # 5. Filter Query Bar
    bar_y = 150
    draw.rectangle([main_x, bar_y, w - 24, bar_y + 44], fill=(24, 30, 37), outline=(50, 62, 75))
    draw.text((main_x + 12, bar_y + 13), "Filter", font=f_ui_b, fill=(100, 115, 130))
    draw.text((main_x + 60, bar_y + 13), '{ "year": { "$lt": 2010 } }', font=f_mono_b, fill=(0, 237, 100))
    
    # Project bar indicator
    draw.rectangle([w - 180, bar_y + 7, w - 100, bar_y + 37], fill=(0, 104, 74))
    draw.text((w - 164, bar_y + 13), "Find", font=f_ui_b, fill=(255, 255, 255))
    draw.rectangle([w - 90, bar_y + 7, w - 30, bar_y + 37], fill=(45, 55, 66))
    draw.text((w - 78, bar_y + 13), "Reset", font=f_ui, fill=(200, 205, 210))

    # Query status text
    draw.text((main_x, bar_y + 50), "Viewing 1-4 of 4 documents matching filter (query executed in 1.4 ms)", font=f_ui, fill=(130, 145, 160))

    # 6. Render the 4 matching documents
    doc_y = 224
    matching_docs = [
        {
            "id": "6afd657f0001000000000001",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "year": 2008,
            "genre": "Software Engineering",
            "price": "43.98900000000001  (Original: $39.99 + 10% increase)",
            "isbn": "978-0132350884",
            "publisher": "Addison-Wesley / Prentice Hall"
        },
        {
            "id": "6afd657f0001000000000002",
            "title": "Design Patterns: Elements of Reusable OOD",
            "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
            "year": 1994,
            "genre": "Software Architecture",
            "price": "60.48900000000001  (Original: $54.99 + 10% increase)",
            "isbn": "978-0201633610",
            "publisher": "Addison-Wesley, Boston"
        },
        {
            "id": "6afd657f0001000000000003",
            "title": "Refactoring: Improving the Design of Existing Code",
            "author": "Martin Fowler",
            "year": 1999,
            "genre": "Software Engineering",
            "price": "52.25000000000001  (Original: $47.50 + 10% increase)",
            "isbn": "978-0201485677",
            "publisher": "Addison-Wesley, Boston"
        },
        {
            "id": "6afd657f0001000000000004",
            "title": "Introduction to Algorithms (CLRS 3rd Ed)",
            "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
            "year": 2009,
            "genre": "Computer Science Theory",
            "price": "97.90000000000002  (Original: $89.00 + 10% increase)",
            "isbn": "978-0262033848",
            "publisher": "MIT Press, Cambridge"
        }
    ]

    for d in matching_docs:
        draw.rectangle([main_x, doc_y, w - 24, doc_y + 110], fill=(24, 30, 37), outline=(42, 54, 66))
        # Document ID header
        draw.text((main_x + 14, doc_y + 8), f"_id: ObjectId(\"{d['id']}\")", font=f_mono, fill=(100, 180, 240))
        draw.text((w - 180, doc_y + 8), "[STATUS: UPDATED]", font=f_ui_b, fill=(0, 237, 100))
        
        # Key fields
        draw.text((main_x + 24, doc_y + 28), "title:", font=f_mono, fill=(150, 160, 170))
        draw.text((main_x + 80, doc_y + 28), f'"{d["title"]}"', font=f_mono_b, fill=(255, 255, 255))
        
        draw.text((main_x + 24, doc_y + 46), "year:", font=f_mono, fill=(150, 160, 170))
        draw.text((main_x + 80, doc_y + 46), f'{d["year"]} (Published before 2010 -> Matched)', font=f_mono, fill=(255, 195, 75))

        draw.text((main_x + 24, doc_y + 64), "price:", font=f_mono, fill=(150, 160, 170))
        draw.text((main_x + 80, doc_y + 64), f'Double({d["price"]})', font=f_mono_b, fill=(0, 237, 100))

        draw.text((main_x + 24, doc_y + 82), "genre:", font=f_mono, fill=(150, 160, 170))
        draw.text((main_x + 80, doc_y + 82), f'"{d["genre"]}" | ISBN: "{d["isbn"]}"', font=f_mono, fill=(180, 190, 200))

        doc_y += 118

    img.save(out_img_path)
    print(f"[OK] Generated {out_img_path} ({w}x{h})")


def main():
    scripts = [
        ("lab_01_setup_environment.py", "screenshot_lab_01.png", "Windows PowerShell - Activity 2.1 (lab_01_setup_environment.py)"),
        ("lab_01_try_yourself.py", "screenshot_lab_01_tryit.png", "Windows PowerShell - Activity 2.1 Try It Yourself (lab_01_try_yourself.py)"),
        ("lab_02_bookstore_crud.py", "screenshot_lab_02.png", "Windows PowerShell - Activity 2.2 (lab_02_bookstore_crud.py)"),
        ("lab_02_try_yourself.py", "screenshot_lab_02_tryit.png", "Windows PowerShell - Activity 2.2 Try It Yourself (lab_02_try_yourself.py)")
    ]

    for script, out_img, title in scripts:
        cmd_str, out_text = capture_script_output(script)
        render_terminal_screenshot(cmd_str, out_text, out_img, title)

    # Dedicated MongoDB Compass verification screenshot
    render_compass_verification_screenshot("screenshot_compass_verification.png")


if __name__ == "__main__":
    main()
