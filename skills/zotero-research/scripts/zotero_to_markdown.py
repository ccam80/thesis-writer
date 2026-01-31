#!/usr/bin/env python3
"""
Convert Zotero PDF attachments to line-numbered Markdown for deep research.

This script:
1. Takes a Zotero item key
2. Finds the PDF attachment in Zotero storage
3. Converts to Markdown using MarkItDown
4. Adds line numbers for citation references
5. Saves to a cache directory

Usage:
    python zotero_to_markdown.py <item_key> [--output-dir <dir>]

Example:
    python zotero_to_markdown.py DCXE5HJ7
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Default Zotero storage location (Windows)
ZOTERO_STORAGE = Path(os.environ.get('ZOTERO_STORAGE',
                      Path.home() / 'Zotero' / 'storage'))

# Default output directory for converted papers
DEFAULT_OUTPUT_DIR = Path(os.environ.get('THESIS_PAPER_CACHE',
                          Path.home() / '.claude' / 'paper_cache'))


def find_pdf_in_storage(item_key: str, storage_path: Path = ZOTERO_STORAGE) -> Optional[Path]:
    """
    Find a PDF file in Zotero storage by item key.

    Zotero stores attachments in: storage/<item_key>/<filename>.pdf
    """
    item_dir = storage_path / item_key

    if not item_dir.exists():
        # Try searching all storage directories for this key
        for subdir in storage_path.iterdir():
            if subdir.is_dir():
                pdfs = list(subdir.glob("*.pdf"))
                if pdfs and subdir.name == item_key:
                    return pdfs[0]
        return None

    pdfs = list(item_dir.glob("*.pdf"))
    return pdfs[0] if pdfs else None


def convert_pdf_to_numbered_markdown(pdf_path: Path, output_path: Path) -> bool:
    """
    Convert PDF to Markdown with line numbers.

    Returns True on success, False on failure.
    """
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("Error: markitdown not installed. Run: pip install markitdown[pdf]")
        return False

    print(f"Converting: {pdf_path.name}")

    # Convert PDF to Markdown
    md = MarkItDown()
    result = md.convert(str(pdf_path))

    # Split into lines and add line numbers
    lines = result.text_content.split('\n')
    numbered_lines = []

    for i, line in enumerate(lines, start=1):
        # Format: "  123 | content" with fixed-width line numbers
        numbered_lines.append(f"{i:5d} | {line}")

    # Create header with metadata
    header = f"""# {pdf_path.stem}

**Source**: {pdf_path.name}
**Zotero Key**: {pdf_path.parent.name}
**Total Lines**: {len(lines)}

---
## How to cite lines from this document

When referencing content, use the format:
- **Lines 67-84**: For a range of lines
- **Line 126**: For a single line

The line numbers appear at the start of each line below.

---

"""

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write('\n'.join(numbered_lines))

    print(f"[OK] Saved to: {output_path}")
    print(f"  Total lines: {len(lines)}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert Zotero PDF to line-numbered Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Convert by Zotero item key (attachment key)
    python zotero_to_markdown.py IQE5V5BK

    # Specify output directory
    python zotero_to_markdown.py IQE5V5BK --output-dir ./papers

    # Use custom Zotero storage location
    python zotero_to_markdown.py IQE5V5BK --zotero-storage D:/Zotero/storage
        """
    )

    parser.add_argument('item_key', help='Zotero attachment item key')
    parser.add_argument('--output-dir', '-o', type=Path, default=DEFAULT_OUTPUT_DIR,
                        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--zotero-storage', '-z', type=Path, default=ZOTERO_STORAGE,
                        help=f'Zotero storage path (default: {ZOTERO_STORAGE})')

    args = parser.parse_args()

    # Find PDF
    pdf_path = find_pdf_in_storage(args.item_key, args.zotero_storage)

    if not pdf_path:
        print(f"Error: No PDF found for item key '{args.item_key}'")
        print(f"Searched in: {args.zotero_storage}")
        sys.exit(1)

    # Set output path
    output_path = args.output_dir / f"{args.item_key}.md"

    # Convert
    success = convert_pdf_to_numbered_markdown(pdf_path, output_path)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
