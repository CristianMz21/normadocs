import sys

from docx import Document

doc = Document(sys.argv[1])
for i, p in enumerate(doc.paragraphs[:20]):
    print(
        f"P{i}: Style='{p.style.name}', Text='{p.text[:30]}...', Align={p.alignment}, Indent={p.paragraph_format.first_line_indent}"
    )
