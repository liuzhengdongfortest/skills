#!/usr/bin/env python3
"""Print available local agent CLIs.

This script is a probe only. It does not edit mission files. MC should run it,
read stdout or JSON, then update runtime-capabilities.md itself.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess


CLI_CANDIDATES = [
    ("claude", "Claude Code", "independent code review, long-form critique, autonomous coding"),
    ("codex", "Codex CLI", "local coding, refactoring, repository work"),
    ("opencode", "OpenCode", "local coding agent"),
    ("gemini", "Gemini CLI", "analysis, research-style second opinion"),
    ("qwen", "Qwen CLI", "code and analysis agent"),
    ("aider", "Aider", "patch-oriented coding"),
    ("goose", "Goose", "agentic local work"),
    ("cursor-agent", "Cursor Agent", "local code agent"),
    ("crush", "Crush", "local code agent"),
    ("amp", "Amp", "local code agent"),
]


def version_of(command: str) -> str:
    for flag in ["--version", "version", "-v"]:
        try:
            completed = subprocess.run(
                [command, flag],
                text=True,
                capture_output=True,
                timeout=3,
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue
        output = (completed.stdout or completed.stderr).strip().splitlines()
        if output:
            return output[0][:160]
    return ""


def scan() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for command, label, use in CLI_CANDIDATES:
        path = shutil.which(command) or ""
        rows.append(
            {
                "command": command,
                "label": label,
                "use": use,
                "path": path,
                "status": "available" if path else "unavailable",
                "version": version_of(command) if path else "",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe local agent CLI availability.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON for MC to interpret")
    args = parser.parse_args()

    rows = scan()
    available = [row for row in rows if row["status"] == "available"]
    if args.json:
        print(json.dumps({"available": available, "checked": rows}, ensure_ascii=False, indent=2))
        return 0

    print(f"Agent CLI scan: {len(available)} available / {len(rows)} checked")
    for row in rows:
        marker = "ok" if row["status"] == "available" else "missing"
        detail = f" ({row['version']})" if row["version"] else ""
        print(f"- {row['command']}: {marker} {row['path']}{detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
