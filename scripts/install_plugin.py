#!/usr/bin/env python3
"""Build and install Thesis Writer for a local Claude Code or Codex environment."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from build_plugin import DEFAULT_MCP_ROOT, ROOT, build


PLUGIN_NAME = "thesis-writer"


def configure_codex_mcp(plugin: Path, mcp_root: Path) -> Path:
    interpreter = mcp_root / ".venv" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        raise FileNotFoundError(f"Deep Zotero interpreter not found: {interpreter}")
    subprocess.run([str(interpreter), "-c", "import deep_zotero.server"], cwd=mcp_root, check=True)
    mcp = {
        "mcpServers": {
            "deep-zotero": {
                "command": str(interpreter.resolve()),
                "args": ["-m", "deep_zotero.server"]
            }
        }
    }
    (plugin / ".mcp.json").write_text(json.dumps(mcp, indent=2) + "\n", encoding="utf-8")
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["mcpServers"] = "./.mcp.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return interpreter


def run(command: list[str], execute: bool) -> None:
    if execute:
        subprocess.run(command, check=True)
    else:
        print("DRY RUN:", subprocess.list2cmdline(command))


def ensure_marketplace(marketplace: Path) -> str:
    desired_entry = {
        "name": PLUGIN_NAME,
        "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity"
    }
    if marketplace.exists():
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        marketplace_name = data.get("name")
        if not isinstance(marketplace_name, str) or not marketplace_name.strip():
            raise RuntimeError(f"Marketplace has no valid top-level name: {marketplace}")
        matches = [entry for entry in data.get("plugins", []) if entry.get("name") == PLUGIN_NAME]
        if matches:
            if matches[0] != desired_entry:
                raise RuntimeError(
                    f"Existing {PLUGIN_NAME} marketplace entry differs from the generated schema: {marketplace}"
                )
            return marketplace_name
        data.setdefault("plugins", []).append(desired_entry)
    else:
        data = {"name": "personal", "interface": {"displayName": "Personal"}, "plugins": [desired_entry]}
        marketplace_name = "personal"
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    marketplace.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return marketplace_name


def validate_marketplace_location(plugin_home: Path, marketplace: Path) -> None:
    expected_suffix = (".agents", "plugins", "marketplace.json")
    if tuple(part.lower() for part in marketplace.parts[-3:]) != expected_suffix:
        raise RuntimeError(
            "Custom marketplace paths must use <root>/.agents/plugins/marketplace.json "
            "so ./plugins/thesis-writer resolves unambiguously."
        )
    expected_plugin_home = (marketplace.parents[2] / "plugins").resolve()
    if plugin_home.resolve() != expected_plugin_home:
        raise RuntimeError(
            f"Plugin home {plugin_home} does not match marketplace source root {expected_plugin_home}"
        )


def install_codex(mcp_root: Path, execute: bool, plugin_home: Path, marketplace: Path) -> None:
    plugin_home = plugin_home.resolve()
    marketplace = marketplace.resolve()
    validate_marketplace_location(plugin_home, marketplace)
    cachebuster = Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "update_plugin_cachebuster.py"
    if not cachebuster.is_file():
        raise FileNotFoundError(f"Codex cachebuster helper not found: {cachebuster}")
    built = build("codex")
    target = (plugin_home / PLUGIN_NAME).resolve()
    if target.parent != plugin_home:
        raise RuntimeError(f"refusing to install outside plugin home: {target}")
    plugin_home.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}.staging-", dir=plugin_home))
    backup = plugin_home / f".{PLUGIN_NAME}.backup-{uuid.uuid4().hex}"
    old_moved = False
    new_moved = False
    try:
        shutil.copytree(built, staging, dirs_exist_ok=True)
        configure_codex_mcp(staging, mcp_root)
        subprocess.run([sys.executable, str(cachebuster), str(staging)], check=True)
        marketplace_name = ensure_marketplace(marketplace)

        if target.exists():
            os.replace(target, backup)
            old_moved = True
        os.replace(staging, target)
        new_moved = True
    except Exception:
        if new_moved and target.exists():
            shutil.rmtree(target)
        if old_moved and backup.exists():
            os.replace(backup, target)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    if backup.exists():
        shutil.rmtree(backup)

    run(["codex", "plugin", "add", f"{PLUGIN_NAME}@{marketplace_name}"], execute)
    print(f"Installed Codex plugin source: {target}")
    print("Start a new Codex task to load the updated skills and MCP tools.")


def install_claude(mcp_root: Path, execute: bool) -> None:
    build("claude")
    interpreter = mcp_root / ".venv" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        raise FileNotFoundError(f"Deep Zotero interpreter not found: {interpreter}")
    subprocess.run([str(interpreter), "-c", "import deep_zotero.server"], cwd=mcp_root, check=True)
    if execute:
        marketplace_update = subprocess.run(
            ["claude", "plugin", "marketplace", "update", "thesis-writer-marketplace"], check=False
        )
        if marketplace_update.returncode:
            subprocess.run(["claude", "plugin", "marketplace", "add", str(ROOT)], check=True)
        plugin_update = subprocess.run(
            ["claude", "plugin", "update", f"{PLUGIN_NAME}@thesis-writer-marketplace"], check=False
        )
        if plugin_update.returncode:
            subprocess.run(
                ["claude", "plugin", "install", f"{PLUGIN_NAME}@thesis-writer-marketplace"], check=True
            )
    else:
        print("DRY RUN: update thesis-writer-marketplace; if absent, add", ROOT)
        print(f"DRY RUN: update {PLUGIN_NAME}@thesis-writer-marketplace; if absent, install it")
    print("Restart Claude Code to load the updated plugin.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendor", required=True, choices=["claude", "codex"])
    parser.add_argument("--mcp-root", type=Path, default=DEFAULT_MCP_ROOT)
    parser.add_argument("--plugin-home", type=Path, default=Path.home() / "plugins")
    parser.add_argument("--marketplace", type=Path, default=Path.home() / ".agents" / "plugins" / "marketplace.json")
    parser.add_argument("--execute", action="store_true", help="Run the vendor CLI commands; file installation is always performed.")
    args = parser.parse_args()
    if args.vendor == "codex":
        install_codex(args.mcp_root.resolve(), args.execute, args.plugin_home.resolve(), args.marketplace.resolve())
    else:
        install_claude(args.mcp_root.resolve(), args.execute)


if __name__ == "__main__":
    main()
