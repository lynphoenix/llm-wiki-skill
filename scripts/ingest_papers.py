#!/usr/bin/env python3
"""
Batch Ingest Papers Script

Scans a directory for PDF files and generates a summary report.
Used to prepare paper lists for ingestion into the LLM Wiki.

Usage:
    python scripts/ingest_papers.py --dir ~/papers/2024

Requirements:
    pip install pypdf tqdm
"""

import argparse
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from pypdf import PdfReader
except ImportError:
    print("Installing pypdf...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "-q"])
    from pypdf import PdfReader


def extract_pdf_info(pdf_path: Path) -> dict:
    """Extract basic info from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        info = reader.metadata or {}

        return {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "pages": len(reader.pages),
            "title": info.get("/Title", pdf_path.stem),
            "author": info.get("/Author", "Unknown"),
        }
    except Exception as e:
        return {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "error": str(e),
        }


def scan_directory(directory: Path, extensions=[".pdf"]) -> list:
    """Scan directory for PDF files."""
    pdf_files = []
    for ext in extensions:
        pdf_files.extend(directory.rglob(f"*{ext}"))
    return sorted(pdf_files)


def main():
    parser = argparse.ArgumentParser(description="Scan and summarize PDF papers")
    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="Directory to scan for PDFs"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for the report (default: print to stdout)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    args = parser.parse_args()

    directory = Path(args.dir).expanduser().resolve()

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Scanning: {directory}")
    pdf_files = scan_directory(directory)

    if not pdf_files:
        print("No PDF files found.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF files")

    # Extract info in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(extract_pdf_info, f): f for f in pdf_files}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"[{i}/{len(pdf_files)}] {result['filename']}")

    # Generate report
    report_lines = [
        "# Paper Scan Report",
        f"",
        f"**Directory:** {directory}",
        f"**Total PDFs:** {len(pdf_files)}",
        f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        "---",
        f"",
        "## Papers",
        f"",
    ]

    for r in sorted(results, key=lambda x: x.get("filename", "")):
        if "error" in r:
            report_lines.append(f"### {r['filename']}")
            report_lines.append(f"**ERROR:** {r['error']}")
        else:
            report_lines.append(f"### {r.get('title', r['filename'])}")
            report_lines.append(f"- **File:** {r['filename']}")
            report_lines.append(f"- **Pages:** {r.get('pages', 'N/A')}")
            report_lines.append(f"- **Author:** {r.get('author', 'Unknown')}")
            report_lines.append(f"- **Path:** `{r['path']}`")
        report_lines.append("")

    report = "\n".join(report_lines)

    # Output
    if args.output:
        Path(args.output).write_text(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    import pandas as pd
    main()
