from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


SRC = Path("CV.md")
OUT = Path("Huaqing_Tu_CV.pdf")


def clean_md(text: str) -> str:
    text = text.replace("**", "")
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    return text


def format_para(text: str) -> str:
    text = clean_md(text).replace("<sup>", "<super>").replace("</sup>", "</super>")
    escaped = escape(text)
    escaped = escaped.replace("&lt;super&gt;", "<super>")
    escaped = escaped.replace("&lt;/super&gt;", "</super>")
    return escaped


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="Name",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="Contact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111111"),
        spaceBefore=8,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="PubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=13.5,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=3,
    )
)


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    story = []
    current_list = None
    in_pubs = False

    def flush_list() -> None:
        nonlocal current_list
        if current_list:
            story.append(
                ListFlowable(current_list, bulletType="bullet", start="circle", leftIndent=14)
            )
            story.append(Spacer(1, 4))
            current_list = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_list()
            continue

        if line.startswith("# "):
            flush_list()
            story.append(Paragraph(format_para(line[2:].strip()), styles["Name"]))
            continue

        if line.startswith("## "):
            flush_list()
            title = line[3:].strip()
            in_pubs = title == "Selected Publications"
            story.append(Spacer(1, 4))
            story.append(Paragraph(format_para(title), styles["Section"]))
            continue

        if line.startswith("### "):
            flush_list()
            story.append(Paragraph(format_para(line[4:].strip()), styles["Body"]))
            continue

        if line.startswith("- "):
            if current_list is None:
                current_list = []
            current_list.append(
                ListItem(Paragraph(format_para(line[2:].strip()), styles["Body"]))
            )
            continue

        if in_pubs and line[:2].isdigit() and ". " in line[:4]:
            flush_list()
            story.append(Paragraph(format_para(line), styles["PubTitle"]))
            continue

        flush_list()
        if len(story) <= 4:
            story.append(Paragraph(format_para(line), styles["Contact"]))
        else:
            story.append(Paragraph(format_para(line), styles["Body"]))

    flush_list()

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()
