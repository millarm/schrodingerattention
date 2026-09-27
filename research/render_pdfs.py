"""Render the two reviewed research Markdown files as shareable PDFs.

This is a presentation renderer, not a scientific-content editor. Relative
repository links are printed with their targets so the PDF remains useful when
shared without a working local checkout.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
FONT_DIR = Path(
    "/Users/gmh-company/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/"
    "Contents/Resources/fonts/truetype"
)

for name, suffix in (
    ("Noto", "Regular"),
    ("Noto-Bold", "Bold"),
    ("Noto-Italic", "Italic"),
    ("Noto-BoldItalic", "BoldItalic"),
):
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f"NotoSans-{suffix}.ttf")))
pdfmetrics.registerFontFamily(
    "Noto", normal="Noto", bold="Noto-Bold", italic="Noto-Italic", boldItalic="Noto-BoldItalic"
)
pdfmetrics.registerFont(TTFont("DejaVuMath", str(FONT_DIR / "DejaVuSans.ttf")))

INK = colors.HexColor("#17243A")
MUTED = colors.HexColor("#4B5B70")
BLUE = colors.HexColor("#164D76")
RULE = colors.HexColor("#CBD5E1")
PALE = colors.HexColor("#F2F6FA")
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 54
TOP = 62
BOTTOM = 54
CONTENT_W = PAGE_W - LEFT - RIGHT

STYLES = {
    "title": ParagraphStyle(
        "title", fontName="Noto-Bold", fontSize=20, leading=27,
        textColor=INK, spaceAfter=13, allowWidows=0, allowOrphans=0,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", fontName="Noto", fontSize=11, leading=16,
        textColor=BLUE, spaceAfter=16,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Noto-Bold", fontSize=12.4, leading=17,
        textColor=INK, spaceBefore=15, spaceAfter=7,
        keepWithNext=True,
    ),
    "h3": ParagraphStyle(
        "h3", fontName="Noto-Bold", fontSize=10.1, leading=14,
        textColor=BLUE, spaceBefore=11, spaceAfter=5,
        keepWithNext=True,
    ),
    "body": ParagraphStyle(
        "body", fontName="Noto", fontSize=9.1, leading=13.7,
        textColor=INK, spaceAfter=8, splitLongWords=True,
        allowWidows=0, allowOrphans=0,
    ),
    "list": ParagraphStyle(
        "list", fontName="Noto", fontSize=9.1, leading=13.7,
        textColor=INK, leftIndent=19, firstLineIndent=-13,
        spaceAfter=5, splitLongWords=True,
    ),
    "equation": ParagraphStyle(
        "equation", fontName="DejaVuMath", fontSize=9.1, leading=15,
        textColor=INK, leftIndent=12, rightIndent=12,
        spaceBefore=4, spaceAfter=10,
    ),
    "cardkey": ParagraphStyle(
        "cardkey", fontName="Noto-Bold", fontSize=7.6, leading=11,
        textColor=BLUE, splitLongWords=True,
    ),
    "cardvalue": ParagraphStyle(
        "cardvalue", fontName="Noto", fontSize=8, leading=11.5,
        textColor=INK, splitLongWords=True,
    ),
}


def math_text(raw: str) -> str:
    """Typeset the small, fixed TeX vocabulary used in these documents."""
    s = raw.strip()
    substitutions = [
        (r"\operatorname{softmax}", "softmax"),
        (r"\mathbb{R}", "ℝ"),
        (r"\Delta", "Δ"),
        (r"\gamma", "γ"),
        (r"\psi", "ψ"),
        (r"\odot", "⊙"),
        (r"\qquad", "    "),
        (r"\sqrt", "√"),
        (r"\times", "×"),
        (r"\in", "∈"),
        (r"\exp", "exp"),
        (r"\frac", "frac"),
        (r"\,", ""),
        (r"\left", ""),
        (r"\right", ""),
    ]
    for source, target in substitutions:
        s = s.replace(source, target)
    # The two display equations merit an unambiguous reader-friendly rendering.
    if s.startswith("H ="):
        return "H = (S + Sᵀ) / (2√L);    U = exp(−i Δt H)."
    if s.startswith("ψ_0"):
        return "ψ₀ = √softmax(S) ⊙ exp(i γ S);    ψ₁ = ψ₀ Uᵀ;    A = |ψ₁|²."
    if s.startswith("|√"):
        return "|√softmax(S) exp(i γ S)|² = softmax(S)"
    s = s.replace("^{L× L}", "^(L×L)").replace("^{L×L}", "^(L×L)")
    s = s.replace("_{valid}", "₍valid₎").replace("_{novel}", "₍novel₎")
    s = s.replace("^2", "²").replace("^T", "ᵀ")
    s = s.replace("{", "").replace("}", "")
    return s


TOKEN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\\\((.*?)\\\)|\*\*(.+?)\*\*|(?<!\*)\*([^*]+)\*(?!\*)")


def inline(text: str, *, show_paths: bool = True) -> str:
    """Translate only the inline Markdown forms present in the source."""
    result = []
    pos = 0
    for match in TOKEN.finditer(text):
        result.append(html.escape(text[pos : match.start()]))
        label, target, code, math, bold, italic = match.groups()
        if label is not None:
            visible = inline(label, show_paths=False)
            if target.startswith(("https://", "http://")):
                result.append(f'<link href="{html.escape(target, quote=True)}" color="#164D76">{visible}</link>')
            elif show_paths:
                result.append(f'{visible} <font color="#4B5B70">[repo: {html.escape(target)}]</font>')
            else:
                result.append(visible)
        elif code is not None:
            result.append(f'<font color="#164D76">{html.escape(code)}</font>')
        elif math is not None:
            result.append(f'<font name="DejaVuMath">{html.escape(math_text(math))}</font>')
        elif bold is not None:
            result.append(f"<b>{inline(bold, show_paths=show_paths)}</b>")
        elif italic is not None:
            result.append(f"<i>{inline(italic, show_paths=show_paths)}</i>")
        pos = match.end()
    result.append(html.escape(text[pos:]))
    return "".join(result)


def flush_paragraph(lines: list[str], story: list) -> None:
    if lines:
        story.append(Paragraph(inline(" ".join(x.strip() for x in lines)), STYLES["body"]))
        lines.clear()


def add_table(lines: list[str], story: list) -> None:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    headers = rows[0]
    for row in rows[2:]:
        pairs = []
        for key, value in zip(headers, row):
            pairs.append([
                Paragraph(inline(key, show_paths=False), STYLES["cardkey"]),
                Paragraph(inline(value), STYLES["cardvalue"]),
            ])
        card = Table(pairs, colWidths=[107, CONTENT_W - 107], hAlign="LEFT")
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PALE),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, -1), (-1, -1), 0.5, RULE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(KeepTogether([card, Spacer(1, 7)]))


def make_story(source: Path) -> list:
    lines = source.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []
    index = 0
    first_h2 = True
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph(paragraph, story)
            index += 1
            continue
        if stripped.startswith("\\["):
            flush_paragraph(paragraph, story)
            math_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("\\]"):
                math_lines.append(lines[index].strip())
                index += 1
            story.append(Paragraph(html.escape(math_text(" ".join(math_lines))), STYLES["equation"]))
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].lstrip().startswith("|---"):
            flush_paragraph(paragraph, story)
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            add_table(table_lines, story)
            continue
        if stripped.startswith("#"):
            flush_paragraph(paragraph, story)
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            style = "title" if level == 1 else "subtitle" if level == 2 and first_h2 else "h2" if level == 2 else "h3"
            if level == 2:
                first_h2 = False
            story.append(Paragraph(inline(title), STYLES[style]))
            index += 1
            continue
        list_match = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if list_match:
            flush_paragraph(paragraph, story)
            bullet = "•" if list_match.group(2) in ("-", "*") else list_match.group(2)
            content = [list_match.group(3)]
            index += 1
            while index < len(lines) and lines[index].startswith("   "):
                content.append(lines[index].strip())
                index += 1
            story.append(Paragraph(f"{bullet}  {inline(' '.join(content))}", STYLES["list"]))
            continue
        paragraph.append(line)
        index += 1
    flush_paragraph(paragraph, story)
    return story


def draw_page(canvas, doc, short_title: str) -> None:
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(LEFT, PAGE_H - 39, PAGE_W - RIGHT, PAGE_H - 39)
    canvas.setFont("Noto", 7.3)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, PAGE_H - 31, short_title)
    canvas.line(LEFT, 40, PAGE_W - RIGHT, 40)
    canvas.drawString(LEFT, 27, "Research record · PDF presentation copy")
    canvas.drawRightString(PAGE_W - RIGHT, 27, str(doc.page))
    canvas.restoreState()


def render(source_name: str, pdf_name: str, short_title: str) -> Path:
    source = ROOT / "research" / source_name
    destination = OUTPUT / pdf_name
    frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)
    doc = BaseDocTemplate(str(destination), pagesize=A4, title=source.stem.replace("_", " "),
                          author="Schrödinger attention research project")
    doc.addPageTemplates(PageTemplate(id="normal", frames=frame,
                                      onPage=lambda canvas, doc: draw_page(canvas, doc, short_title)))
    doc.build(make_story(source))
    return destination


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for args in (
        ("schrodinger_attention_research_paper.md", "schrodinger_attention_research_paper.pdf", "Exact Schrödinger Attention · Research paper"),
        ("next_research_steps.md", "next_research_steps.pdf", "Exact Schrödinger Attention · Next research steps"),
    ):
        print(render(*args))
