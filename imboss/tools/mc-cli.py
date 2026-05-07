#!/usr/bin/env python3
"""Command line controller for MC Core — imboss edition.

New vs upstream:
  start --prompt "..."   inline custom prompt passed to mc-core
  start --skill NAME     skill to load before main prompt (passed to mc-core)
  default root           .boss/ (imboss convention)
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for attempt in range(6):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(0.05 * (attempt + 1))


def runtime_dir(root: Path) -> Path:
    return root / "runtime"


def pid_path(root: Path) -> Path:
    return runtime_dir(root) / "core.pid"


def state_path(root: Path) -> Path:
    return runtime_dir(root) / "state.json"


def command_path(root: Path) -> Path:
    return runtime_dir(root) / "command.json"


def registry_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "CodeStable" / "mc-cores.json"
    return Path.home() / ".codestable" / "mc-cores.json"


def status_window_script() -> Path:
    return Path(__file__).with_name("mc-status-window.py")


def read_pid(root: Path) -> int | None:
    try:
        text = pid_path(root).read_text(encoding="utf-8").strip()
        return int(text) if text else None
    except (FileNotFoundError, ValueError):
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


def command_payload(command: str, **extra: object) -> dict:
    return {"id": f"{now_iso()}-{uuid.uuid4().hex}", "command": command, "ts": now_iso(), **extra}


def send_command(root: Path, command: str, **extra: object) -> None:
    write_json(command_path(root), command_payload(command, **extra))


def read_registry() -> dict:
    data = read_json(registry_path())
    items = data.get("cores")
    return data if isinstance(items, list) else {"version": 1, "cores": []}


def register_root(root: Path, label: str | None = None) -> None:
    registry = read_registry()
    resolved = str(root.resolve())
    cores = [item for item in registry.get("cores", []) if item.get("root") != resolved]
    cores.append(
        {
            "root": resolved,
            "label": label or root.resolve().parent.name or resolved,
            "registered_at": now_iso(),
            "last_seen_at": now_iso(),
        }
    )
    write_json(registry_path(), {"version": 1, "cores": cores})


def core_script() -> Path:
    return Path(__file__).with_name("mc-core.py")


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


def file_info(path_value: object) -> dict:
    if not isinstance(path_value, str) or not path_value:
        return {"path": path_value, "exists": False}
    path = Path(path_value)
    try:
        stat = path.stat()
    except OSError:
        return {"path": str(path), "exists": False}
    age = time.time() - stat.st_mtime
    return {
        "path": str(path),
        "exists": True,
        "bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "modified_age_seconds": round(age, 1),
    }


def latest_agent_logs(root: Path) -> tuple[Path | None, Path | None]:
    logs = root / "logs"
    candidates = []
    for path in logs.glob("agent-round-*.out.log"):
        try:
            round_text = path.name.removeprefix("agent-round-").removesuffix(".out.log")
            candidates.append((int(round_text), path))
        except ValueError:
            continue
    if not candidates:
        return None, None
    _, stdout = max(candidates, key=lambda item: item[0])
    stderr = stdout.with_name(stdout.name.replace(".out.log", ".err.log"))
    return stdout, stderr


def read_tail(path: Path, lines: int) -> str:
    if lines <= 0:
        return ""
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            end = handle.tell()
            chunk_size = 4096
            data = b""
            while end > 0 and data.count(b"\n") <= lines:
                read_size = min(chunk_size, end)
                end -= read_size
                handle.seek(end)
                data = handle.read(read_size) + data
    except OSError:
        return ""
    text = data.decode("utf-8", errors="replace")
    return "\n".join(text.splitlines()[-lines:])


def enrich_status(root: Path, pid: int | None, state: dict) -> dict:
    running = process_running(pid)
    child_pid = state.get("child_pid")
    child_running = process_running(int(child_pid)) if isinstance(child_pid, int) else False
    now = datetime.now(timezone.utc)
    child_started = parse_time(state.get("child_started_at"))
    updated_at = parse_time(state.get("updated_at"))
    stdout_path = state.get("child_stdout")
    stderr_path = state.get("child_stderr")
    if not stdout_path and not stderr_path:
        latest_stdout, latest_stderr = latest_agent_logs(root)
        stdout_path = str(latest_stdout) if latest_stdout else None
        stderr_path = str(latest_stderr) if latest_stderr else None
    stdout = file_info(stdout_path)
    stderr = file_info(stderr_path)
    log_ages = [
        item.get("modified_age_seconds")
        for item in [stdout, stderr]
        if item.get("exists") and isinstance(item.get("modified_age_seconds"), (int, float))
    ]
    quiet_seconds = min(log_ages) if log_ages else None
    return {
        "root": str(root),
        "pid": pid,
        "running": running,
        "child_running": child_running,
        "child_runtime_seconds": round((now - child_started).total_seconds(), 1) if child_started else None,
        "state_age_seconds": round((now - updated_at).total_seconds(), 1) if updated_at else None,
        "log_quiet_seconds": quiet_seconds,
        "stdout": stdout,
        "stderr": stderr,
        "state": state,
    }


def start(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    register_root(root)
    pid = read_pid(root)
    if process_running(pid):
        print(f"MC Core already running pid={pid}")
        return 0
    if not args.prompt and not args.prompt_file:
        print("MC Core has no default prompt. Provide --prompt or --prompt-file when starting.")
        return 2

    cmd = [
        sys.executable,
        str(core_script()),
        "--root", str(root),
        "--provider", args.provider,
        "--interval", str(args.interval),
    ]
    if args.max_rounds:
        cmd += ["--max-rounds", str(args.max_rounds)]
    if args.cwd:
        cmd += ["--cwd", args.cwd]
    if args.prompt:
        cmd += ["--prompt", args.prompt]
    if args.prompt_file:
        cmd += ["--prompt-file", str(args.prompt_file)]
    if args.skill:
        cmd += ["--skill", args.skill]
    if args.start_paused:
        cmd.append("--start-paused")
    if args.dry_run_core:
        cmd.append("--dry-run")

    if args.dry_run:
        print(json.dumps({"command": cmd}, ensure_ascii=False, indent=2))
        return 0
    if args.foreground:
        return subprocess.call(cmd)

    logs = root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    stdout = (logs / "core.out.log").open("a", encoding="utf-8")
    stderr = (logs / "core.err.log").open("a", encoding="utf-8")
    popen_kwargs = {"stdout": stdout, "stderr": stderr, "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        popen_kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    proc = subprocess.Popen(cmd, **popen_kwargs)
    stdout.close()
    stderr.close()
    print(f"MC Core started pid={proc.pid}")
    return 0


def window(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    register_root(root)
    cmd = [sys.executable, str(status_window_script()), "--root", str(root)]
    if args.all:
        cmd.append("--all")
    if args.refresh:
        cmd += ["--refresh", str(args.refresh)]
    if args.foreground:
        return subprocess.call(cmd)

    logs = root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    stdout = (logs / "status-window.out.log").open("a", encoding="utf-8")
    stderr = (logs / "status-window.err.log").open("a", encoding="utf-8")
    popen_kwargs = {"stdout": stdout, "stderr": stderr, "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        popen_kwargs["creationflags"] = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    proc = subprocess.Popen(cmd, **popen_kwargs)
    stdout.close()
    stderr.close()
    print(f"MC status window started pid={proc.pid}")
    return 0


def status(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    register_root(root)
    pid = read_pid(root)
    state = read_json(state_path(root))
    payload = enrich_status(root, pid, state)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        state_status = state.get("status", "unknown")
        print(f"root: {root}")
        print(f"pid: {pid or '-'}")
        print(f"running: {payload['running']}")
        print(f"status: {state_status}")
        if state.get("provider"):
            print(f"provider: {state['provider']}")
        if state.get("skill"):
            print(f"skill: {state['skill']}")
        if state.get("round") is not None:
            print(f"round: {state['round']}")
        if state.get("child_pid"):
            print(f"child_pid: {state['child_pid']}")
            print(f"child_running: {payload['child_running']}")
        if state.get("child_cwd"):
            print(f"child_cwd: {state['child_cwd']}")
        if payload.get("child_runtime_seconds") is not None:
            print(f"child_runtime: {format_age(payload['child_runtime_seconds'])}")
        if payload.get("log_quiet_seconds") is not None:
            print(f"log_quiet_for: {format_age(payload['log_quiet_seconds'])}")
        if payload["stdout"].get("path"):
            print(
                "stdout: "
                f"{payload['stdout']['path']} "
                f"({payload['stdout'].get('bytes', 0)} bytes, "
                f"updated {format_age(payload['stdout'].get('modified_age_seconds'))} ago)"
            )
        if payload["stderr"].get("path"):
            print(
                "stderr: "
                f"{payload['stderr']['path']} "
                f"({payload['stderr'].get('bytes', 0)} bytes, "
                f"updated {format_age(payload['stderr'].get('modified_age_seconds'))} ago)"
            )
        if state.get("updated_at"):
            print(f"updated_at: {state['updated_at']}")
        if payload["running"] and payload.get("log_quiet_seconds") is not None and payload["log_quiet_seconds"] > args.stale_after:
            print(f"warning: agent logs have been quiet for more than {format_age(args.stale_after)}")
        if args.tail:
            for label, key in [("stdout", "child_stdout"), ("stderr", "child_stderr")]:
                path_value = state.get(key)
                if not isinstance(path_value, str):
                    continue
                text = read_tail(Path(path_value), args.tail)
                if text:
                    print(f"\n--- {label} tail ({args.tail}) ---")
                    print(text)
    return 0


def logs(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    state = read_json(state_path(root))
    if args.core:
        paths = [root / "logs" / "core.out.log", root / "logs" / "core.err.log"]
    else:
        paths = []
        if not args.stderr_only:
            stdout = state.get("child_stdout")
            if isinstance(stdout, str):
                paths.append(Path(stdout))
        if not args.stdout_only:
            stderr = state.get("child_stderr")
            if isinstance(stderr, str):
                paths.append(Path(stderr))
        if not paths:
            stdout, stderr = latest_agent_logs(root)
            if stdout and not args.stderr_only:
                paths.append(stdout)
            if stderr and not args.stdout_only:
                paths.append(stderr)
    if not paths:
        print("no log path found")
        return 1
    positions = {}
    for path in paths:
        print(f"--- {path} ---")
        text = read_tail(path, args.lines)
        if text:
            print(text)
        try:
            positions[path] = path.stat().st_size
        except OSError:
            positions[path] = 0
    if not args.follow:
        return 0
    try:
        while True:
            for path in paths:
                try:
                    with path.open("r", encoding="utf-8", errors="replace") as handle:
                        handle.seek(positions.get(path, 0))
                        text = handle.read()
                        positions[path] = handle.tell()
                except OSError:
                    continue
                if text:
                    print(f"\n--- {path} ---")
                    print(text, end="" if text.endswith("\n") else "\n")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


def control(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    pid = read_pid(root)
    if not process_running(pid):
        print("MC Core is not running")
        return 1
    send_command(root, args.command)
    print(f"sent command: {args.command}")
    if args.command == "stop" and args.wait:
        deadline = time.time() + args.wait
        while time.time() < deadline:
            if not process_running(pid):
                print("MC Core stopped")
                return 0
            time.sleep(0.5)
        print("MC Core stop command sent; process still running")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control the Mission Control core process (imboss edition).")
    parser.add_argument("--root", default=".boss", help=".boss directory (default: .boss for imboss)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    start_parser = sub.add_parser("start", help="start MC Core")
    start_parser.add_argument("--provider", choices=["codex", "claude", "opencode", "gemini"], default="codex")
    start_parser.add_argument("--interval", type=float, default=5.0)
    start_parser.add_argument("--max-rounds", type=int)
    start_parser.add_argument("--cwd", help="working directory for Agent CLI child process")
    start_parser.add_argument("--prompt", help="inline work order for the Agent CLI")
    start_parser.add_argument("--prompt-file", type=Path, help="read the Agent CLI work order from a file")
    start_parser.add_argument("--skill", help="skill to load before the main prompt (e.g. imboss)")
    start_parser.add_argument("--start-paused", action="store_true")
    start_parser.add_argument("--foreground", action="store_true")
    start_parser.add_argument("--dry-run", action="store_true", help="print core command without starting it")
    start_parser.add_argument("--dry-run-core", action="store_true", help="start core in dry-run mode")
    start_parser.set_defaults(func=start)

    status_parser = sub.add_parser("status", help="show MC Core status")
    status_parser.add_argument("--json", action="store_true")
    status_parser.add_argument("--tail", type=int, default=0, help="also show last N lines of current agent logs")
    status_parser.add_argument("--stale-after", type=float, default=120.0, help="warn when logs are quiet for this many seconds")
    status_parser.set_defaults(func=status)

    logs_parser = sub.add_parser("logs", help="show current MC Core or Agent CLI logs")
    logs_parser.add_argument("--lines", type=int, default=80)
    logs_parser.add_argument("--follow", action="store_true")
    logs_parser.add_argument("--interval", type=float, default=1.0)
    logs_parser.add_argument("--core", action="store_true", help="show core logs instead of current agent logs")
    logs_parser.add_argument("--stdout-only", action="store_true")
    logs_parser.add_argument("--stderr-only", action="store_true")
    logs_parser.set_defaults(func=logs)

    window_parser = sub.add_parser("window", help="open a floating MC Core status window")
    window_parser.add_argument("--all", action="store_true", help="show all registered .boss roots")
    window_parser.add_argument("--foreground", action="store_true", help="run the window in this process")
    window_parser.add_argument("--refresh", type=float, default=2.0, help="seconds between refreshes")
    window_parser.set_defaults(func=window)

    for name in ["wake", "pause", "resume", "stop"]:
        item = sub.add_parser(name, help=f"send {name} command to MC Core")
        item.set_defaults(func=control, command=name)
        if name == "stop":
            item.add_argument("--wait", type=float, default=10.0, help="seconds to wait for core to exit")
        else:
            item.set_defaults(wait=0.0)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
