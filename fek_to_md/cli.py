from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .converter import convert_pdf_to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fek-to-md",
        description="Convert Greek FEK PDF files to Markdown suitable for custom GPT knowledge bases.",
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="+",
        help="PDF file(s) or directory/directories containing PDFs.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .md file for one PDF, or output directory for multiple PDFs.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search directories recursively for .pdf files.",
    )
    parser.add_argument(
        "--no-page-markers",
        action="store_true",
        help="Do not include HTML page markers like <!-- Page 1 -->.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Only clean extracted text; do not add Markdown headings for FEK structure.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing Markdown files.",
    )
    return parser


def find_pdfs(inputs: list[Path], *, recursive: bool) -> list[Path]:
    pdfs: list[Path] = []
    for input_path in inputs:
        if input_path.is_file():
            if input_path.suffix.lower() != ".pdf":
                raise ValueError(f"Not a PDF file: {input_path}")
            pdfs.append(input_path)
            continue

        if input_path.is_dir():
            pattern = "**/*.pdf" if recursive else "*.pdf"
            pdfs.extend(sorted(input_path.glob(pattern)))
            continue

        raise FileNotFoundError(f"Input not found: {input_path}")

    return sorted(dict.fromkeys(path.resolve() for path in pdfs))


def output_path_for(pdf_path: Path, *, output: Path | None, multiple: bool) -> Path:
    if output is None:
        return pdf_path.with_suffix(".md")

    if multiple:
        return output / f"{pdf_path.stem}.md"

    if output.suffix.lower() == ".md":
        return output

    return output / f"{pdf_path.stem}.md"


def convert_one(
    pdf_path: Path,
    md_path: Path,
    *,
    include_page_markers: bool,
    apply_structure: bool,
    overwrite: bool,
) -> str:
    if md_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists, use --overwrite: {md_path}")

    result = convert_pdf_to_markdown(
        pdf_path,
        include_page_markers=include_page_markers,
        apply_structure=apply_structure,
    )

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(result.markdown, encoding="utf-8")

    warning = ""
    if result.stats.low_text_pages:
        pages = ", ".join(str(page) for page in result.stats.low_text_pages[:10])
        suffix = "..." if len(result.stats.low_text_pages) > 10 else ""
        warning = f" [warning: little/no selectable text on pages {pages}{suffix}]"

    return f"Created {md_path} ({result.stats.pages} pages, {result.stats.characters} chars){warning}"


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        pdfs = find_pdfs(args.input, recursive=args.recursive)
        if not pdfs:
            parser.error("No PDF files found.")

        multiple = len(pdfs) > 1
        if multiple and args.output is not None and args.output.suffix.lower() == ".md":
            parser.error("--output must be a directory when converting multiple PDFs.")

        for pdf_path in pdfs:
            md_path = output_path_for(pdf_path, output=args.output, multiple=multiple)
            message = convert_one(
                pdf_path,
                md_path,
                include_page_markers=not args.no_page_markers,
                apply_structure=not args.plain,
                overwrite=args.overwrite,
            )
            print(message)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()

