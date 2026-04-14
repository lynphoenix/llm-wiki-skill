#!/usr/bin/env python3
"""
Code Repository Ingest Script for LLM Wiki

Scans a codebase, extracts metadata about source files, and prepares
them for LLM analysis and indexing into the Wiki.

Usage:
    python scripts/ingest_repo.py --dir /path/to/project --ext .py .js .ts
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

def get_ignore_patterns(repo_dir: Path) -> list:
    ignore_patterns = [".git", "node_modules", "__pycache__", "venv", "env", ".DS_Store", "dist", "build"]
    gitignore = repo_dir / ".gitignore"
    if gitignore.exists():
        with open(gitignore, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    clean_pattern = line.replace("/", "").replace("*", "")
                    if clean_pattern:
                        ignore_patterns.append(clean_pattern)
    return ignore_patterns

def should_ignore(path: Path, repo_dir: Path, ignore_patterns: list) -> bool:
    try:
        rel_path = path.relative_to(repo_dir).parts
        for part in rel_path:
            for pattern in ignore_patterns:
                if pattern in part or part == pattern:
                    return True
    except ValueError:
        pass
    return False

def scan_codebase(repo_dir: Path, extensions: list, ignore_patterns: list) -> list:
    code_files = []
    for file_path in repo_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in extensions:
            if not should_ignore(file_path, repo_dir, ignore_patterns):
                code_files.append(file_path)
    return sorted(code_files)

def generate_report(code_files: list, repo_dir: Path, output_file: str = None):
    report_lines = [
        "# Codebase Scan Report",
        "",
        f"**Repository:** `{repo_dir.absolute()}`",
        f"**Total Files Scanned:** {len(code_files)}",
        f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Files Ready for Ingestion",
        ""
    ]
    
    files_by_dir = {}
    for f in code_files:
        rel_dir = str(f.parent.relative_to(repo_dir))
        if rel_dir == ".":
            rel_dir = "(root)"
        if rel_dir not in files_by_dir:
            files_by_dir[rel_dir] = []
        files_by_dir[rel_dir].append(f)
        
    for d in sorted(files_by_dir.keys()):
        report_lines.append(f"### Directory: `{d}`")
        for f in files_by_dir[d]:
            try:
                size_kb = f.stat().st_size / 1024
                report_lines.append(f"- `{f.name}` ({size_kb:.1f} KB)")
            except Exception as e:
                report_lines.append(f"- `{f.name}` (Error reading size)")
        report_lines.append("")

    report = "\n".join(report_lines)
    
    if output_file:
        Path(output_file).write_text(report)
        print(f"\nReport saved to: {output_file}")
    else:
        print("\n" + report)
        
    return report

def main():
    parser = argparse.ArgumentParser(description="Scan codebase for LLM Wiki ingestion")
    parser.add_argument("--dir", type=str, default=".", help="Repository root directory")
    parser.add_argument("--ext", nargs="+", default=[".py", ".js", ".ts", ".go", ".java", ".cpp", ".h", ".md", ".json", ".yaml", ".toml"], help="File extensions to scan")
    parser.add_argument("--output", type=str, default=None, help="Output report file")
    
    args = parser.parse_args()
    repo_dir = Path(args.dir).expanduser().resolve()
    
    if not repo_dir.exists() or not repo_dir.is_dir():
        print(f"Error: Invalid directory: {repo_dir}")
        sys.exit(1)
        
    print(f"Scanning repository: {repo_dir}")
    print(f"Looking for extensions: {', '.join(args.ext)}")
    
    ignore_patterns = get_ignore_patterns(repo_dir)
    code_files = scan_codebase(repo_dir, args.ext, ignore_patterns)
    
    if not code_files:
        print("No matching code files found.")
        sys.exit(0)
        
    generate_report(code_files, repo_dir, args.output)
    
    chinese_msg = "\u4e0b\u4e00\u6b65: \u8bb0\u5f97\u8ddf Claude \u8bf4\uff1a\u628a\u8fd9\u4e9b\u4ee3\u7801\u6587\u4ef6\u5403\u8fdb\u5230 wiki \u4e2d"
    print(chinese_msg)

if __name__ == "__main__":
    main()
