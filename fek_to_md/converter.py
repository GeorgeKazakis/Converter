from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ARTICLE_RE = re.compile(r"(?mi)^\s*Άρθρο\s+([0-9Α-ΩA-Z]+)\s*(?:[-–—]\s*(.+))?$")
CHAPTER_RE = re.compile(r"(?mi)^\s*(ΚΕΦΑΛΑΙΟ\s+[Α-ΩA-Z0-9]+)\s*$")
PART_RE = re.compile(r"(?mi)^\s*(ΜΕΡΟΣ\s+[Α-ΩA-Z0-9]+)\s*$")
SECTION_RE = re.compile(r"(?mi)^\s*(ΤΜΗΜΑ\s+[Α-ΩA-Z0-9]+)\s*$")
DECISION_RE = re.compile(r"(?mi)^\s*(ΑΠΟΦΑΣΗ|ΝΟΜΟΣ|ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ)\s*$")
PARAGRAPH_RE = re.compile(r"(?m)^(\d+)\.\s+")


@dataclass(frozen=True)
class ConversionStats:
    pages: int
    characters: int
    low_text_pages: tuple[int, ...]


@dataclass(frozen=True)
class ConversionResult:
    markdown: str
    stats: ConversionStats


def extract_text_from_pdf(pdf_path: Path, *, include_page_markers: bool = True) -> tuple[str, ConversionStats]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency PyMuPDF. Install it with: pip install -r requirements.txt"
        ) from exc

    pages: list[str] = []
    low_text_pages: list[int] = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text", sort=True).strip()
            if len(text) < 80:
                low_text_pages.append(page_num)

            if include_page_markers:
                pages.append(f"\n\n<!-- Page {page_num} -->\n\n{text}")
            else:
                pages.append(text)

    raw = "\n".join(pages)
    return raw, ConversionStats(
        pages=len(pages),
        characters=len(raw),
        low_text_pages=tuple(low_text_pages),
    )


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Join hyphenated words split across lines: περιλαμ-\nβανόμενο -> περιλαμβανόμενο.
    text = re.sub(r"([A-Za-zΑ-ΩΆΈΉΊΌΎΏΪΫα-ωάέήίόύώϊϋΐΰ])- *\n *([A-Za-zΑ-ΩΆΈΉΊΌΎΏΪΫα-ωάέήίόύώϊϋΐΰ])", r"\1\2", text)

    # Drop repeated running headers that usually add noise in FEK PDFs.
    text = re.sub(r"(?mi)^\s*ΕΦΗΜΕΡΙΔΑ\s+ΤΗΣ\s+ΚΥΒΕΡΝΗΣΕΩΣ\s*$", "", text)
    text = re.sub(r"(?mi)^\s*Τεύχος\s+[Α-ΩA-Z'΄]+\s+\d+/\d{2}\.\d{2}\.\d{4}\s*$", "", text)

    # Join line wraps inside paragraphs, while preserving structural starts.
    protected_next_line = (
        r"<!-- Page|Άρθρο\b|ΚΕΦΑΛΑΙΟ\b|ΜΕΡΟΣ\b|ΤΜΗΜΑ\b|ΑΠΟΦΑΣΗ\b|ΝΟΜΟΣ\b|"
        r"ΠΡΟΕΔΡΙΚΟ ΔΙΑΤΑΓΜΑ\b|\d+\.\s|[α-ω]\)\s|[ivxlcdm]+\)\s"
    )
    text = re.sub(
        rf"(?<![.:;·!?])\n(?!\n|{protected_next_line})",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def structure_markdown(text: str) -> str:
    text = PART_RE.sub(r"# \1", text)
    text = CHAPTER_RE.sub(r"## \1", text)
    text = SECTION_RE.sub(r"### \1", text)
    text = DECISION_RE.sub(r"# \1", text)

    def article_heading(match: re.Match[str]) -> str:
        number = match.group(1)
        title = (match.group(2) or "").strip()
        return f"## Άρθρο {number}" + (f" - {title}" if title else "")

    text = ARTICLE_RE.sub(article_heading, text)
    text = PARAGRAPH_RE.sub(r"### Παράγραφος \1\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def convert_pdf_to_markdown(
    pdf_path: Path,
    *,
    include_page_markers: bool = True,
    apply_structure: bool = True,
) -> ConversionResult:
    raw, stats = extract_text_from_pdf(pdf_path, include_page_markers=include_page_markers)
    markdown = clean_text(raw)
    if apply_structure:
        markdown = structure_markdown(markdown)
    else:
        markdown = markdown.strip() + "\n"
    return ConversionResult(markdown=markdown, stats=stats)

