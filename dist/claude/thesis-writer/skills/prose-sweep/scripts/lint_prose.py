#!/usr/bin/env python3
"""Flag thesis-prose patterns banned by report-guidelines.md and prose-style.md.

Every finding is a candidate for the sweep to judge in context, not a verdict.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def words(*items: str) -> str:
    """Join phrases into one alternation that matches whole words only.

    Hyphens count as word characters, so "many" does not match "many-core".
    """
    body = "|".join(re.escape(item).replace(r"\ ", r"\s+") for item in items)
    return rf"(?<![\w-])(?:{body})(?![\w-])"


GAUCHERIES: dict[str, str] = {
    "a variety of different": "a variety of",
    "actual fact": "fact",
    "adept at": "adept in",
    "approximation of": "approximation to",
    "at the conclusion of": "after",
    "at the present time": "at present",
    "at this point in time": "now",
    "can be found": "is found",
    "compensate for": "compensate",
    "compensating for": "compensating",
    "connect up": "connect",
    "correct for": "correct",
    "correcting for": "correcting",
    "due to the fact that": "because",
    "during the course of": "during",
    "during the time that": "while",
    "in the course of": "during",
    "in order to": "to",
    "in the vicinity of": "about",
    "in the neighbourhood of": "near",
    "in this day and age": "today",
    "instant of time": "instant",
    "instant in time": "instant",
    "in the event that": "if",
    "irregardless": "regardless",
    "join together": "join",
    "known as": "called",
    "most unique": "unique",
    "very unique": "unique",
    "new and innovative": "innovative",
    "prior to": "before",
    "the reason why": "because",
    "to begin with": "to begin",
    "whether or not": "whether",
}

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("em-dash", re.compile(r"---")),
    ("sentence-adverb", re.compile(r"(?i)(?:^|[.!?]\s+)(?:crucially|importantly|interestingly|notably|essentially|fundamentally|ultimately|arguably|of course)\s*,")),
    ("filler-move", re.compile(r"(?i)\b(?:it is important to note that|it is worth mentioning|the reality is|at its core|in essence|when it comes to|a testament to|underscores the importance of)\b")),
    ("contrast-scaffold", re.compile(r"(?i)\b(?:not (?:just|merely|only)\b.{0,80}\bbut\b|it(?:'s| is) not\b.{0,80}\bit(?:'s| is)\b)")),
    ("meta-narration", re.compile(r"(?i)\b(?:this section (?:discusses|covers|examines|explores)|having established\b|we now turn to\b|as will become clear\b|recall that\b)")),
    ("kill-list", re.compile(r"(?i)\b(?:delv(?:e|es|ed|ing)|harness(?:es|ed|ing)?|unlock(?:s|ed|ing)?|showcas(?:e|es|ed|ing)|seamless|holistic|tapestry|cutting-edge)\b")),
    ("importance-modifier", re.compile("(?i)" + words("rather", "really", "particularly", "highly", "crucial", "essential", "vital", "pivotal"))),
    ("weasel", re.compile("(?i)" + words(
        "some people", "experts", "it is well known", "many", "somewhat", "in most respects",
        "various", "fairly", "several", "extremely", "exceedingly", "quite", "remarkably", "few",
        "mostly", "largely", "huge", "tiny", "a number of", "excellent", "significantly",
        "substantially", "incredibly", "clearly", "vast", "relatively", "completely", "very",
    ))),
    ("weakening-adverb", re.compile("(?i)" + words(
        "often", "probably", "possibly", "truly", "actually", "basically", "surprisingly",
    ))),
    ("hidden-authority", re.compile(r"(?i)\bit (?:is|has been|was) (?:said|believed|known|thought|claimed|shown|reported|suggested|argued)\b")),
    ("gaucherie", re.compile("(?i)" + words(*GAUCHERIES))),
    ("contraction", re.compile(r"(?i)\b(?:\w+n't|\w+'(?:re|ve|ll|d|m)|(?:it|that|there|here|what|let)'s)\b")),
    ("relative-reference", re.compile(r"(?i)\b(?:the (?:figure|table|equation|section|chapter|listing) (?:above|below)|(?:see|shown|described|discussed|mentioned|given|listed) (?:above|below)|the (?:above|below) (?:figure|table|equation|section))\b")),
    ("future-tense", re.compile(r"(?i)\bwill be (?:discussed|presented|shown|described|considered|introduced|covered|explained|examined|given|detailed|explored|outlined)\b")),
    ("placeholder", re.compile(r"\[\[|\[cite\]|\(cite:")),
    ("rhetorical-question", re.compile(r"\?")),
)

PARAGRAPH_OPENER = re.compile(r"(?i)^\s*(?:however|furthermore|moreover|hence|thus|therefore|additionally|nevertheless|consequently|also)\b")
STRUCTURAL = re.compile(r"\\(?:(?:sub)*section|chapter|paragraph|label|begin|end|caption|centering|includegraphics|input|include|subfile|documentclass|usepackage|FloatBarrier|newpage|clearpage|printbibliography|bibliography)\b")
INLINE_MATH =re.compile(r"(?<!\\)\$([^$]+)(?<!\\)\$")
COMMENT = re.compile(r"(?<!\\)%.*")


def finding(line: int, column: int, rule: str, text: str, suggestion: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"line": line, "column": column, "rule": rule, "text": text}
    if suggestion is not None:
        result["suggestion"] = suggestion
    return result


def lint_text(text: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    # A paragraph starts at the top of the file and after a blank line or a
    # structural command line such as \section{...} or \end{figure}. We skip
    # structural lines entirely; other lines that open with a command, such as
    # \Cref{...} shows, are prose.
    paragraph_start = True
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = COMMENT.sub("", raw)
        stripped = line.strip()
        if not stripped:
            if not raw.strip():
                paragraph_start = True
            continue
        if STRUCTURAL.match(stripped):
            paragraph_start = True
            continue
        if paragraph_start:
            opener = PARAGRAPH_OPENER.match(line)
            if opener:
                findings.append(finding(line_number, opener.start() + 1, "paragraph-opener", opener.group(0).strip()))
            paragraph_start = False
        for rule, pattern in PATTERNS:
            for match in pattern.finditer(line):
                suggestion = None
                if rule == "gaucherie":
                    phrase = " ".join(match.group(0).lower().split())
                    suggestion = GAUCHERIES.get(phrase)
                findings.append(finding(line_number, match.start() + 1, rule, match.group(0), suggestion))
        for math in INLINE_MATH.finditer(line):
            if "*" in math.group(1):
                findings.append(finding(line_number, math.start() + 1, "star-multiplication", math.group(0)))
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
            hint = f" -> {item['suggestion']}" if "suggestion" in item else ""
            print(f"{args.path}:{item['line']}:{item['column']}: {item['rule']}: {item['text']}{hint}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
