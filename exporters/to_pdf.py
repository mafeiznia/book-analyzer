"""Convert Markdown report to PDF using WeasyPrint."""
from pathlib import Path

import markdown as md_lib

from exporters.to_json import project_dir


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<style>
@page {
    size: A4;
    margin: 2cm 1.8cm;
    @bottom-center {
        content: counter(page);
        font-family: Vazirmatn, sans-serif;
        font-size: 9pt;
        color: #777;
    }
}

body {
    font-family: Vazirmatn, Tahoma, sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #222;
    direction: rtl;
    text-align: right;
}

h1 {
    font-size: 20pt;
    color: #5a6b1f;
    border-bottom: 2px solid #9CAF3F;
    padding-bottom: 6px;
    margin-top: 24px;
}

h2 {
    font-size: 15pt;
    color: #5a6b1f;
    border-right: 4px solid #9CAF3F;
    padding-right: 8px;
    margin-top: 22px;
}

h3 {
    font-size: 13pt;
    color: #444;
    margin-top: 16px;
}

p {
    margin: 8px 0;
    text-align: justify;
}

ul, ol {
    padding-right: 24px;
}

li {
    margin: 4px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #ccc;
    padding: 6px 8px;
    text-align: right;
    vertical-align: top;
}

th {
    background-color: #eef3d8;
    color: #3a4a10;
    font-weight: bold;
}

blockquote {
    border-right: 3px solid #9CAF3F;
    padding: 4px 12px;
    margin: 8px 0;
    color: #555;
    background-color: #fafcf2;
    font-style: italic;
}

code, pre {
    font-family: Consolas, "Courier New", monospace;
    direction: ltr;
    text-align: left;
}

code {
    background-color: #f3f3f3;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9pt;
}

pre {
    background-color: #f6f8f0;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 9pt;
    line-height: 1.5;
    border: 1px solid #e0e5d0;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}

details {
    display: none;
}

strong {
    color: #3a4a10;
}

a {
    color: #5a6b1f;
    text-decoration: none;
}
</style>
</head>
<body>
{content}
</body>
</html>
"""


def build_html(markdown_text: str) -> str:
    """Convert Markdown to HTML wrapped in RTL template."""
    lines = markdown_text.splitlines()
    if lines and lines[0].strip() == "---":
        end = None
        for i, ln in enumerate(lines[1:], start=1):
            if ln.strip() == "---":
                end = i
                break
        if end is not None:
            markdown_text = "\n".join(lines[end + 1:])

    html_body = md_lib.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "nl2br"],
    )
    return HTML_TEMPLATE.replace("{content}", html_body)


def save_pdf(
    project_id: int,
    title: str,
    version: int,
    markdown_text: str,
) -> Path:
    """Convert Markdown text to PDF and save. Returns the file path."""
    base = project_dir(project_id, title) / f"v{version}"
    base.mkdir(parents=True, exist_ok=True)

    html = build_html(markdown_text)

    path = base / "report.pdf"

    from weasyprint import HTML

    HTML(string=html, base_url=str(base)).write_pdf(str(path))
    return path