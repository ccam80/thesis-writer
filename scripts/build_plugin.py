#!/usr/bin/env python3
"""Build complete Claude and Codex plugin distributions from shared source."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MARKER = "<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->"
FRAGMENT_RE = re.compile(r"<!-- vendor:([a-z0-9-]+) -->")
DEFAULT_MCP_ROOT = Path(r"C:\local_working_projects\zotero_citation_mcp")


def read_skill_metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        key, value = line.split(":", 1)
        if key not in {"name", "description"}:
            raise ValueError(f"unsupported shared frontmatter key {key!r} in {path}")
        result[key] = json.loads(value.strip())
    if set(result) != {"name", "description"}:
        raise ValueError(f"shared frontmatter must contain exactly name and description: {path}")
    return result


def load_fragments(vendor: str) -> dict[str, str]:
    directory = ROOT / "vendors" / vendor / "fragments"
    return {
        path.stem: path.read_text(encoding="utf-8").strip()
        for path in sorted(directory.glob("*.md"))
    }


def render_fragments(text: str, fragments: dict[str, str], used: set[str], source: Path) -> str:
    names = FRAGMENT_RE.findall(text)
    for name in names:
        if name not in fragments:
            raise ValueError(f"missing vendor fragment {name!r} required by {source}")
        text = text.replace(f"<!-- vendor:{name} -->", fragments[name])
        used.add(name)
    unresolved = FRAGMENT_RE.findall(text)
    if unresolved:
        raise ValueError(f"unresolved vendor fragments in {source}: {unresolved}")
    return text


def ensure_all_fragments_used(fragments: dict[str, str], used: set[str], vendor: str) -> None:
    unused = sorted(set(fragments) - used)
    if unused:
        raise ValueError(f"unused {vendor} vendor fragments: {unused}")


def skill_text(metadata: dict[str, str], body: str, allowed_tools: list[str] | None) -> str:
    lines = ["---", f"name: {metadata['name']}", f"description: {json.dumps(metadata['description'], ensure_ascii=False)}"]
    if allowed_tools is not None:
        lines.append("allowed-tools: [" + ", ".join(allowed_tools) + "]")
    lines.extend(["---", "", MARKER, "", body.rstrip(), ""])
    return "\n".join(lines)


def copy_companions(source: Path, target: Path, vendor: str) -> None:
    cache_dir = ".claude" if vendor == "claude" else ".codex"
    for path in sorted(source.rglob("*")):
        if (
            not path.is_file()
            or path.name in {"skill.yaml", "body.md"}
            or "__pycache__" in path.parts
            or path.suffix == ".pyc"
        ):
            continue
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in {".py", ".md", ".txt"}:
            text = path.read_text(encoding="utf-8").replace("__THESIS_WRITER_CACHE_VENDOR__", cache_dir)
            destination.write_text(text, encoding="utf-8", newline="\n")
        else:
            shutil.copy2(path, destination)


def build_manifest(vendor: str, plugin_root: Path, metadata: dict[str, object]) -> None:
    common = {
        "name": metadata["name"],
        "version": metadata["version"],
        "description": metadata["description"],
        "author": metadata["author"],
        "homepage": metadata["homepage"],
        "repository": metadata["repository"],
        "license": metadata["license"],
        "keywords": metadata["keywords"],
    }
    if vendor == "claude":
        manifest = common
        location = plugin_root / ".claude-plugin" / "plugin.json"
    else:
        manifest = {
            **common,
            "skills": "./skills/",
            "interface": {
                "displayName": "Thesis Writer",
                "shortDescription": metadata["description"],
                "longDescription": metadata["longDescription"],
                "developerName": metadata["author"]["name"],
                "category": metadata["category"],
                "capabilities": ["Interactive", "Write", "Research"],
                "websiteURL": metadata["homepage"],
                "defaultPrompt": [
                    "Plan a thesis chapter with Zotero evidence.",
                    "Write an approved thesis section in LaTeX.",
                    "Review a chapter against its approved plan."
                ]
            }
        }
        location = plugin_root / ".codex-plugin" / "plugin.json"
    location.parent.mkdir(parents=True, exist_ok=True)
    location.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_marketplace(
    vendor: str,
    metadata: dict[str, object],
    dist_root: Path,
    repository_output_root: Path,
) -> None:
    if vendor == "claude":
        marketplace = {
            "name": "thesis-writer-marketplace",
            "metadata": {
                "description": metadata["description"],
                "version": metadata["version"]
            },
            "owner": metadata["author"],
            "plugins": [{
                "name": metadata["name"],
                "description": metadata["description"],
                "source": "./dist/claude/thesis-writer",
                "version": metadata["version"],
                "author": metadata["author"],
                "homepage": metadata["homepage"],
                "category": "authoring",
                "keywords": metadata["keywords"]
            }]
        }
        location = repository_output_root / ".claude-plugin" / "marketplace.json"
    else:
        marketplace = {
            "name": "personal",
            "interface": {"displayName": "Personal"},
            "plugins": [{
                "name": metadata["name"],
                "source": {"source": "local", "path": "./plugins/thesis-writer"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": metadata["category"]
            }]
        }
        location = dist_root / "codex" / "personal-marketplace.json"
    location.parent.mkdir(parents=True, exist_ok=True)
    location.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(
    vendor: str,
    dist_root: Path = DIST,
    repository_output_root: Path = ROOT,
) -> Path:
    metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    vendor_root = dist_root / vendor
    if vendor_root.exists():
        shutil.rmtree(vendor_root)
    plugin_root = vendor_root / str(metadata["name"])
    plugin_root.mkdir(parents=True)

    fragments = load_fragments(vendor)
    used: set[str] = set()
    allowed_by_skill = json.loads((ROOT / "vendors" / vendor / "skills.json").read_text(encoding="utf-8"))
    source_skills = ROOT / "src" / "skills"
    for source in sorted(path for path in source_skills.iterdir() if path.is_dir()):
        skill_metadata = read_skill_metadata(source / "skill.yaml")
        body = render_fragments((source / "body.md").read_text(encoding="utf-8"), fragments, used, source / "body.md")
        allowed = allowed_by_skill.get(source.name) if vendor == "claude" else None
        if vendor == "claude" and allowed is None:
            raise ValueError(f"Claude allowed-tools overlay missing for {source.name}")
        target = plugin_root / "skills" / source.name
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(skill_text(skill_metadata, body, allowed), encoding="utf-8", newline="\n")
        copy_companions(source, target, vendor)

    if vendor == "codex":
        init = ROOT / "vendors" / "codex" / "init-skill"
        target = plugin_root / "skills" / "thesis-writer-init"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            skill_text(read_skill_metadata(init / "skill.yaml"), (init / "body.md").read_text(encoding="utf-8"), None),
            encoding="utf-8", newline="\n"
        )
    else:
        command_target = plugin_root / "commands" / "thesis-writer-init.md"
        command_target.parent.mkdir(parents=True)
        command = (ROOT / "vendors" / "claude" / "commands" / "thesis-writer-init.md").read_text(encoding="utf-8")
        command_target.write_text(command.replace("---\n\n#", f"---\n\n{MARKER}\n\n#", 1), encoding="utf-8", newline="\n")

    template = render_fragments(
        (ROOT / "src" / "templates" / "thesis-instructions.md").read_text(encoding="utf-8"),
        fragments, used, ROOT / "src" / "templates" / "thesis-instructions.md"
    )
    template_name = "CLAUDE.thesis-writer.md" if vendor == "claude" else "AGENTS.thesis-writer.md"
    template_target = plugin_root / "templates" / template_name
    template_target.parent.mkdir(parents=True)
    template_target.write_text(f"{MARKER}\n\n{template.rstrip()}\n", encoding="utf-8", newline="\n")

    ensure_all_fragments_used(fragments, used, vendor)
    build_manifest(vendor, plugin_root, metadata)
    build_marketplace(vendor, metadata, dist_root, repository_output_root)

    if vendor == "codex":
        example = {
            "mcpServers": {
                "deep-zotero": {
                    "command": "<generated-at-install-time>",
                    "args": ["-m", "deep_zotero.server"]
                }
            }
        }
        (plugin_root / ".mcp.json.example").write_text(
            json.dumps(example, indent=2) + "\n", encoding="utf-8"
        )

    return plugin_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor", choices=["all", "claude", "codex"], default="all")
    args = parser.parse_args()
    vendors = ["claude", "codex"] if args.vendor == "all" else [args.vendor]
    for vendor in vendors:
        print(build(vendor))


if __name__ == "__main__":
    main()
