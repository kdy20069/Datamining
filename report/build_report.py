#!/usr/bin/env python3
"""Build the PDF and DOCX versions of Final_Report.md without changing its source."""
from __future__ import annotations

import html
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as PDFImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table as PDFTable,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
# Correct working-directory-dependent root: the report lives at project/report/,
# so the project root is one level up from report/, not two.
if ROOT.name != "Datamining":
    ROOT = ROOT.parent
SOURCE = ROOT / "report" / "Final_Report.md"
PDF_OUT = ROOT / "report" / "Final_Report.pdf"
DOCX_OUT = ROOT / "report" / "Final_Report.docx"
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FIGURE_CAPTION_RE = re.compile(r"\*\*Figure\s+(\d+)\.\*\*\s*(.*)")
ALT_FIGURE_RE = re.compile(r"Figure\s+(\d+)\.\s*(.*)")


def parse_blocks(text: str):
    """Yield (kind, payload) records from the small Markdown subset in this report."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
                    rows.append(row)
                i += 1
            yield "table", rows
            continue
        image = IMAGE_RE.fullmatch(line)
        if image:
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            caption = ""
            if i < len(lines):
                caption_match = FIGURE_CAPTION_RE.fullmatch(lines[i].strip())
            else:
                caption_match = None
            if caption_match:
                caption = lines[i].strip()
                i += 1
            else:
                # Older report drafts stored the full Figure N caption in image alt text.
                # Alt text is not painted by PDFImage, so promote that text to a caption.
                alt_match = ALT_FIGURE_RE.fullmatch(image.group(1).strip())
                if alt_match:
                    caption = f"**Figure {alt_match.group(1)}.** {alt_match.group(2)}".strip()
            yield "figure", (image.group(1), image.group(2), caption)
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            yield "heading", (level, line[level:].strip())
            i += 1
            continue
        if line.startswith("---"):
            i += 1
            continue
        if line.startswith("- ") or re.match(r"\d+\. ", line):
            kind = "bullet" if line.startswith("- ") else "number"
            if kind == "bullet":
                content = line[2:]
            else:
                match = re.match(r"^(\d+)\.\s+(.*)$", line)
                content = (int(match.group(1)), match.group(2))
            yield kind, content
            i += 1
            continue
        parts = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", "|", "![", "- ")) or re.match(r"\d+\. ", nxt):
                break
            parts.append(nxt)
            i += 1
        yield "paragraph", " ".join(parts)


def split_inline(text: str):
    """Return text/format tuples for the report's bold, code, and link syntax."""
    # Match code before single-star emphasis so allele names such as CYP2C19*2 stay intact.
    token = re.compile(r"(\*\*.*?\*\*|`[^`]+`|(?<![\w*])\*(?!\*).*?(?<!\*)\*(?![\w*])|\[[^\]]+\]\([^)]+\))")
    chunks = []
    pos = 0
    for m in token.finditer(text):
        if m.start() > pos:
            chunks.append((text[pos:m.start()], "normal"))
        value = m.group()
        if value.startswith("**"):
            chunks.append((value[2:-2], "bold"))
        elif value.startswith("`"):
            chunks.append((value[1:-1], "code"))
        elif value.startswith("*"):
            chunks.append((value[1:-1], "italic"))
        else:
            lm = LINK_RE.fullmatch(value)
            label, url = lm.groups()
            chunks.append((url if label == url else f"{label} ({url})", "normal"))
        pos = m.end()
    if pos < len(text):
        chunks.append((text[pos:], "normal"))
    return chunks


def pdf_markup(text: str) -> str:
    # Keep dash separators visibly apart from adjacent URLs in the rendered PDF.
    text = text.replace("µ", "u").replace("→", "->")
    text = re.sub(r"\s*[—–]\s*", " - ", text)
    pieces = []
    for value, style in split_inline(text):
        value = html.escape(value)
        if style == "bold":
            value = f"<b>{value}</b>"
        elif style == "italic":
            value = f"<i>{value}</i>"
        elif style == "code":
            value = f'<font name="Courier" color="#30445a">{value}</font>'
        pieces.append(value)
    return "".join(pieces)


def image_path(raw: str) -> Path:
    # Images are referenced as `experiment/fig1_...`; SOURCE lives at
    # project/report/Final_Report.md, so the project root is SOURCE.parent.parent.
    path = (SOURCE.parent.parent / raw).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Report image is missing: {raw}")
    return path


def make_pdf(blocks):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=colors.HexColor("#18324b"), alignment=TA_LEFT, spaceAfter=5))
    styles.add(ParagraphStyle(name="ReportH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.2, leading=13, textColor=colors.HexColor("#18324b"), spaceBefore=7, spaceAfter=3, keepWithNext=True))
    styles.add(ParagraphStyle(name="ReportH3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=9.4, leading=11, textColor=colors.HexColor("#264b68"), spaceBefore=5, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle(name="ReportBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.4, leading=8.5, spaceAfter=2.0, alignment=TA_LEFT, splitLongWords=True))
    styles.add(ParagraphStyle(name="ReportReference", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.2, leading=6.4, spaceAfter=0.5, alignment=TA_LEFT, splitLongWords=True))
    styles.add(ParagraphStyle(name="ReportSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.7, leading=7.6, spaceAfter=0))
    styles.add(ParagraphStyle(name="ReportCaption", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.0, leading=8, alignment=TA_CENTER, spaceBefore=1, spaceAfter=2))
    story = []
    def heading_flowable(payload):
        level, heading_text = payload
        return Paragraph(pdf_markup(heading_text), styles["ReportTitle"] if level == 1 else styles["ReportH2" if level == 2 else "ReportH3"])

    index = 0
    in_references = False
    references_seen = False
    while index < len(blocks):
        kind, payload = blocks[index]
        if kind == "heading" and payload[0] == 2 and payload[1].strip().lower() == "references":
            if references_seen:
                index += 1
                continue
            references_seen = True
            in_references = True
        if kind == "heading" and payload[0] == 2 and index + 1 < len(blocks):
            next_kind, next_payload = blocks[index + 1]
            if next_kind == "figure" or (next_kind == "table" and len(next_payload) <= 8):
                group = [heading_flowable(payload)]
                if next_kind == "figure":
                    _alt, raw, caption = next_payload
                    img_path = image_path(raw)
                    if not img_path.is_file():
                        raise FileNotFoundError(f"Report image is missing: {raw}")
                    max_w, max_h = A4[0] - 30 * mm, 72 * mm
                    img = PDFImage(str(img_path), width=max_w, height=max_h, kind="proportional")
                    img._restrictSize(max_w, max_h)
                    cap = Paragraph(pdf_markup(caption), styles["ReportCaption"]) if caption else Spacer(1, 1)
                    group.append(KeepTogether([img, cap]))
                else:
                    rows = next_payload
                    data = [[Paragraph(pdf_markup(cell), styles["ReportSmall"]) for cell in row] for row in rows]
                    usable = A4[0] - 30 * mm
                    table = PDFTable(data, colWidths=[usable / max(map(len, rows))] * max(map(len, rows)), repeatRows=1, hAlign="LEFT")
                    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef3")), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b9c5cf")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
                    group.append(table)
                story.append(KeepTogether(group))
                index += 2
                continue
        if kind == "heading":
            level, text = payload
            if level == 1:
                story.append(Paragraph(pdf_markup(text), styles["ReportTitle"]))
            else:
                story.append(Paragraph(pdf_markup(text), styles["ReportH2" if level == 2 else "ReportH3"]))
        elif kind == "paragraph":
            story.append(Paragraph(pdf_markup(payload), styles["ReportReference" if in_references else "ReportBody"]))
        elif kind in ("bullet", "number"):
            if kind == "bullet":
                story.append(Paragraph(f"• {pdf_markup(payload)}", styles["ReportReference" if in_references else "ReportBody"]))
            else:
                number, content = payload
                story.append(Paragraph(f"{number}. {pdf_markup(content)}", styles["ReportReference" if in_references else "ReportBody"]))
        elif kind == "table":
            data = [[Paragraph(pdf_markup(cell), styles["ReportSmall"]) for cell in row] for row in payload]
            usable = A4[0] - 2 * 15 * mm
            ncols = max(map(len, payload))
            widths = [usable / ncols] * ncols
            table = PDFTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#18324b")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b9c5cf")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]))
            story.extend([table, Spacer(1, 3)])
        elif kind == "figure":
            alt, raw, caption = payload
            p = image_path(raw)
            max_w, max_h = A4[0] - 30 * mm, 72 * mm
            img = PDFImage(str(p), width=max_w, height=max_h, kind="proportional")
            img._restrictSize(max_w, max_h)
            caption_p = Paragraph(pdf_markup(caption), styles["ReportCaption"]) if caption else Spacer(1, 1)
            story.append(KeepTogether([img, caption_p]))
        index += 1
    doc = SimpleDocTemplate(str(PDF_OUT), pagesize=A4, rightMargin=11*mm, leftMargin=11*mm, topMargin=10*mm, bottomMargin=10*mm, title="Evidence-Bounded Integrated Audit", author="")
    doc.build(story)


def add_runs(paragraph, text):
    for value, style in split_inline(text):
        run = paragraph.add_run(value)
        if style == "bold":
            run.bold = True
        elif style == "italic":
            run.italic = True
        elif style == "code":
            run.font.name = "Courier New"
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(48, 68, 90)


def make_docx(blocks):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.0
    doc.core_properties.title = "Evidence-Bounded Integrated Audit of a Candidate Insecticide–Benzodiazepine Combination"
    for kind, payload in blocks:
        if kind == "heading":
            level, text = payload
            if level == 1:
                p = doc.add_paragraph(style="Title")
                p.paragraph_format.space_after = Pt(5)
                add_runs(p, text)
            else:
                p = doc.add_heading(level=min(level - 1, 3))
                p.paragraph_format.space_before = Pt(7)
                p.paragraph_format.space_after = Pt(3)
                add_runs(p, text)
        elif kind == "paragraph":
            p = doc.add_paragraph()
            add_runs(p, payload)
        elif kind in ("bullet", "number"):
            if kind == "bullet":
                p = doc.add_paragraph(style="List Bullet")
                add_runs(p, payload)
            else:
                number, content = payload
                p = doc.add_paragraph()
                p.add_run(f"{number}. ")
                add_runs(p, content)
        elif kind == "table":
            cols = max(map(len, payload))
            table = doc.add_table(rows=len(payload), cols=cols)
            table.style = "Light Shading Accent 1"
            table.autofit = True
            for r, row in enumerate(payload):
                for c, value in enumerate(row):
                    cell = table.cell(r, c)
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(1)
                    for part, fmt in split_inline(value):
                        run = p.add_run(part)
                        if fmt == "bold" or r == 0:
                            run.bold = True
                        if fmt == "code":
                            run.font.name = "Courier New"
                            run.font.size = Pt(8)
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.size = Pt(8)
        elif kind == "figure":
            _alt, raw, caption = payload
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.keep_with_next = bool(caption)
            p.add_run().add_picture(str(image_path(raw)), width=Inches(6.15))
            if caption:
                cap = doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap.paragraph_format.space_before = Pt(0)
                cap.paragraph_format.space_after = Pt(5)
                cap.paragraph_format.keep_together = True
                add_runs(cap, caption)
    doc.save(DOCX_OUT)


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    blocks = list(parse_blocks(SOURCE.read_text(encoding="utf-8")))
    make_pdf(blocks)
    make_docx(blocks)
    print(f"Built {PDF_OUT.relative_to(ROOT)} and {DOCX_OUT.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
