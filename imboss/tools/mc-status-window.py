#!/usr/bin/env python3
"""Floating status window for MC Core instances.

The window is a sidecar observer. It reads each mission root's runtime files
and never sends control commands or edits mission state.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import time
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import ttk


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def registry_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "CodeStable" / "mc-cores.json"
    return Path.home() / ".codestable" / "mc-cores.json"


def runtime_dir(root: Path) -> Path:
    return root / "runtime"


def pid_path(root: Path) -> Path:
    return runtime_dir(root) / "core.pid"


def state_path(root: Path) -> Path:
    return runtime_dir(root) / "state.json"


def read_pid(root: Path) -> int | None:
    try:
        text = pid_path(root).read_text(encoding="utf-8").strip()
        return int(text) if text else None
    except (FileNotFoundError, ValueError, OSError):
        return None


def process_running(pid: int | None) -> bool:
    if not pid:
        return False
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == 259
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_age(seconds: float | None) -> str:
    if seconds is None:
        return "-"
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{seconds:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"


def log_quiet_seconds(state: dict) -> float | None:
    ages = []
    for key in ["child_stdout", "child_stderr"]:
        value = state.get(key)
        if not isinstance(value, str) or not value:
            continue
        try:
            ages.append(time.time() - Path(value).stat().st_mtime)
        except OSError:
            continue
    return min(ages) if ages else None


def core_rows(root: Path) -> dict:
    state = read_json(state_path(root))
    pid = read_pid(root)
    child_pid = state.get("child_pid")
    updated_at = parse_time(state.get("updated_at"))
    now = datetime.now(timezone.utc)
    return {
        "root": str(root),
        "label": root.resolve().parent.name or str(root),
        "pid": pid,
        "running": process_running(pid),
        "status": state.get("status", "unknown"),
        "provider": state.get("provider", "-"),
        "round": state.get("round", "-"),
        "child_running": process_running(child_pid if isinstance(child_pid, int) else None),
        "state_age": round((now - updated_at).total_seconds(), 1) if updated_at else None,
        "log_quiet": log_quiet_seconds(state),
    }


def registered_roots(explicit_root: Path, include_all: bool) -> list[Path]:
    roots = [explicit_root.resolve()]
    if include_all:
        for item in read_json(registry_path()).get("cores", []):
            value = item.get("root")
            if isinstance(value, str) and value:
                roots.append(Path(value).resolve())
    deduped = []
    seen = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            deduped.append(root)
            seen.add(key)
    return deduped


class StatusWindow:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.root = tk.Tk()
        self.root.title("MC Core")
        self.root.attributes("-topmost", True)
        self.root.geometry("760x220")
        self.root.minsize(520, 160)
        self.root.configure(bg="#101418")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", background="#151b20", foreground="#f2f4f5", fieldbackground="#151b20", rowheight=26)
        style.configure("Treeview.Heading", background="#222a31", foreground="#f2f4f5")
        style.map("Treeview", background=[("selected", "#2f6fed")])

        columns = ("status", "pid", "agent", "round", "age", "quiet", "root")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        headings = {
            "status": "Status",
            "pid": "PID",
            "agent": "Agent",
            "round": "Round",
            "age": "State",
            "quiet": "Logs",
            "root": "工作目录",
        }
        widths = {"status": 92, "pid": 74, "agent": 96, "round": 70, "age": 70, "quiet": 70, "root": 280}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w", stretch=column == "root")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        self.footer = tk.StringVar(value="")
        tk.Label(
            self.root,
            textvariable=self.footer,
            anchor="w",
            bg="#101418",
            fg="#a9b4bd",
            padx=10,
        ).pack(fill="x", pady=(0, 6))

    def refresh(self) -> None:
        roots = registered_roots(Path(self.args.root), self.args.all)
        rows = [core_rows(root) for root in roots]
        existing = set(self.tree.get_children())
        for index, row in enumerate(rows):
            item_id = row["root"]
            existing.discard(item_id)
            status = row["status"]
            if row["running"]:
                status = f"{status}"
            else:
                status = "offline"
            agent = row["provider"]
            if row["child_running"]:
                agent = f"{agent} child"
            values = (
                status,
                row["pid"] or "-",
                agent,
                row["round"],
                format_age(row["state_age"]),
                format_age(row["log_quiet"]),
                row["root"],
            )
            if self.tree.exists(item_id):
                self.tree.item(item_id, values=values)
            else:
                self.tree.insert("", "end", iid=item_id, values=values)
        for stale in existing:
            self.tree.delete(stale)
        now = datetime.now().strftime("%H:%M:%S")
        self.footer.set(f"Updated {now} | {len(rows)} registered core(s)")
        self.root.after(max(250, int(self.args.refresh * 1000)), self.refresh)

    def run(self) -> None:
        self.refresh()
        self.root.mainloop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show a floating MC Core status window.")
    parser.add_argument("--root", default=".mission", help="mission directory")
    parser.add_argument("--all", action="store_true", help="show all registered mission roots")
    parser.add_argument("--refresh", type=float, default=2.0, help="seconds between refreshes")
    return parser.parse_args()


def main() -> int:
    StatusWindow(parse_args()).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
