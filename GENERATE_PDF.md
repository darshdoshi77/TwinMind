# Generating System Design PDF

The system design document (`SYSTEM_DESIGN.md`) needs to be converted to PDF for submission.

## Option 1: Using Pandoc (Recommended)

```bash
# Install pandoc (if not already installed)
# macOS: brew install pandoc
# Linux: apt-get install pandoc
# Windows: Download from https://pandoc.org/installing.html

# Convert to PDF
pandoc SYSTEM_DESIGN.md -o SYSTEM_DESIGN.pdf --pdf-engine=xelatex -V geometry:margin=1in
```

## Option 2: Using VS Code Extension

1. Install "Markdown PDF" extension in VS Code
2. Open `SYSTEM_DESIGN.md`
3. Right-click → "Markdown PDF: Export (pdf)"

## Option 3: Using Online Tools

- Upload `SYSTEM_DESIGN.md` to:
  - https://www.markdowntopdf.com/
  - https://cloudconvert.com/md-to-pdf
  - https://dillinger.io/ (export as PDF)

## Option 4: Print to PDF

1. Open `SYSTEM_DESIGN.md` in a markdown viewer
2. Print → Save as PDF

## Note

The document includes ASCII diagrams which will render correctly in most PDF generators. For best results with diagrams, consider:
- Using Mermaid diagram syntax (can be added)
- Creating separate image files for complex diagrams
- Using tools like draw.io or Excalidraw

