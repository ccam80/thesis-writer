#!/usr/bin/env python3
"""Flag deterministic thesis-prose patterns banned by prose-style.md."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("em-dash", re.compile(r"---")),
    ("sentence-adverb", re.compile(r"(?i)(?:^|[.!?]\s+)(?:crucially|importantly|interestingly|notably|essentially|fundamentally|ultimately|arguably|of course)\s*,")),
    ("filler-move", re.compile(r"(?i)\b(?:it is important to note that|it is worth mentioning|the reality is|at its core|in essence|when it comes to|a testament to|underscores the importance of)\b")),
    ("contrast-scaffold", re.compile(r"(?i)\b(?:not (?:just|merely|only)\b.{0,80}\bbut\b|it(?:'s| is) not\b.{0,80}\bit(?:'s| is)\b)")),
    ("meta-narration", re.compile(r"(?i)\b(?:this section (?:discusses|covers|examines|explores)|having established\b|we now turn to\b|as will become clear\b|recall that\b)")),
    ("kill-list", re.compile(r"(?i)\b(?:delv(?:e|es|ed|ing)|harness(?:es|ed|ing)?|unlock(?:s|ed|ing)?|showcas(?:e|es|ed|ing)|seamless|holistic|tapestry|cutting-edge)\b")),
    ("importance-modifier", re.compile(r"(?i)\b(?:very|quite|rather|fairly|really|particularly|highly|extremely|remarkably|crucial|essential|vital|pivotal)\b")),
    ("rhetorical-question", re.compile(r"\?")),
)


def lint_text(text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("%", 1)[0]
        if not line.strip():
            continue
        for rule, pattern in PATTERNS:
            for match in pattern.finditer(line):
                findings.append({
                    "line": line_number,
                    "column": match.start() + 1,
                    "rule": rule,
                    "text": match.group(0),
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    findings = lint_text(args.path.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
    else:
        for item in findings:
            print(f"{args.path}:{item['line']}:{item['column']}: {item['rule']}: {item['text']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
