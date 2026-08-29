import sys

from docx import Document

doc = Document(sys.argv[1])
for i, p in enumerate(doc.paragraphs[:20]):
    style = p.style.name
    txt = p.text[:30]
    align = p.alignment
    indent = p.paragraph_format.first_line_indent
    print(f"P{i}: Style='{style}', Text='{txt}...', Align={align}, Indent={indent}")
