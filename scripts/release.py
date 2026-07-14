#!/usr/bin/env python3
"""Set a release version, rebuild both vendors, and run the complete validator."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from build_plugin import DEFAULT_MCP_ROOT, ROOT


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--mcp-root", type=Path, default=DEFAULT_MCP_ROOT)
    parser.add_argument("--skip-claude-cli", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(
        r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?",
        args.version,
    ):
        raise SystemExit(f"invalid semantic version: {args.version}")
    metadata_path = ROOT / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["version"] = args.version
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    command = [sys.executable, str(ROOT / "scripts" / "validate_all.py"), "--mcp-root", str(args.mcp_root.resolve())]
    if args.skip_claude_cli:
        command.append("--skip-claude-cli")
    subprocess.run(command, check=True)
    print(f"Release {args.version} is built and validated. Commit metadata.json and generated dist/ together, then tag the commit.")


if __name__ == "__main__":
    main()
