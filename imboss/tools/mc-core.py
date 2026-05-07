#!/usr/bin/env python3
"""Mission Control core process - imboss edition.

MC Core keeps the runtime alive. It starts one Agent CLI turn, waits for it to
exit, records runtime events, then decides whether to continue, pause, or stop
based on commands written by mc-cli.py.

Task state lives wherever the Agent prompt and skill decide. Core owns process
control only; it does not parse plans, requirements, tasks, or project context.

New vs upstream:
  --prompt "..."     required inline work order for the Agent CLI
  --skill NAME       prepend skill-loading instruction before the main prompt
  default root       .boss/ (imboss convention)
  no default prompt  MC Core controls process lifetime, not work policy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SKILL_PRELUDE = """本轮使用 {skill} 技能（/{skill}）。
然后继续执行下面的工作指令：

"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


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


def append_event(root: Path, payload: dict) -> None:
    log = root / "logs" / "runtime.ndjson"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": now_iso(), **payload}, ensure_ascii=False) + "\n")


def node_path_for(shim_dir: Path) -> str:
    local_node = shim_dir / "node.exe"
    if local_node.exists():
        return str(local_node)
    return shutil.which("node.exe") or shutil.which("node") or "node"


def node_script_argv(command: str, script: Path, args: list[str]) -> list[str] | None:
    if script.exists():
        return [node_path_for(script.parent), str(script), *args]
    shim = shutil.which(f"{command}.cmd") or shutil.which(command)
    if not shim:
        return None
    shim_dir = Path(shim).resolve().parent
    if script.is_absolute():
        candidate = script
    else:
        candidate = shim_dir / script
    if candidate.exists():
        return [node_path_for(shim_dir), str(candidate), *args]
    return None


def npm_node_argv(command: str, relative_script: Path, args: list[str]) -> list[str] | None:
    shim = shutil.which(f"{command}.cmd") or shutil.which(command)
    if not shim:
        return None
    shim_dir = Path(shim).resolve().parent
    script = shim_dir / relative_script
    if script.exists():
        return [node_path_for(shim_dir), str(script), *args]
    return None


def pnpm_opencode_argv(prompt: str) -> list[str] | None:
    shim = shutil.which("opencode.cmd") or shutil.which("opencode")
    if not shim:
        return None
    shim_dir = Path(shim).resolve().parent
    cmd_path = Path(shim)
    if cmd_path.suffix.lower() == ".cmd":
        try:
            text = cmd_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        match = re.search(r'node(?:\.exe)?"\s+"%~dp0\\([^"]+)"', text, re.IGNORECASE)
        if not match:
            match = re.search(r'node\s+"%~dp0\\([^"]+)"', text, re.IGNORECASE)
        if match:
            script = shim_dir / match.group(1)
            if script.exists():
                return [node_path_for(shim_dir), str(script), "run", "--dangerously-skip-permissions", prompt]
    candidates = sorted(
        (shim_dir / "global" / "5" / ".pnpm").glob("opencode-ai@*/node_modules/opencode-ai/bin/opencode"),
        reverse=True,
    )
    if candidates:
        return [node_path_for(shim_dir), str(candidates[0]), "run", "--dangerously-skip-permissions", prompt]
    return None


def codex_argv(prompt: str) -> list[str]:
    if os.name == "nt":
        argv = npm_node_argv(
            "codex",
            Path("node_modules") / "@openai" / "codex" / "bin" / "codex.js",
            ["exec", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", prompt],
        )
        if argv:
            return argv
    return ["codex", "exec", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", prompt]


def claude_argv(prompt: str, skill: str | None = None) -> list[str]:
    claude = shutil.which("claude.exe") or shutil.which("claude") or "claude"
    # Note: --skill is not a claude CLI flag. Skills resolve via /skill-name in the prompt.
    # The SKILL_PRELUDE (prepended by build_prompt when --skill is set) handles this.
    return [claude, "--permission-mode", "bypassPermissions", "-p", prompt]


def gemini_argv(prompt: str) -> list[str]:
    if os.name == "nt":
        argv = npm_node_argv(
            "gemini",
            Path("node_modules") / "@google" / "gemini-cli" / "bundle" / "gemini.js",
            ["-p", prompt, "--approval-mode", "yolo"],
        )
        if argv:
            return argv
    return ["gemini", "-p", prompt, "--approval-mode", "yolo"]


def opencode_argv(prompt: str) -> list[str]:
    if os.name == "nt":
        argv = pnpm_opencode_argv(prompt)
        if argv:
            return argv
    return ["opencode", "run", "--dangerously-skip-permissions", prompt]


def provider_argv(provider: str, prompt: str, skill: str | None = None) -> list[str]:
    if provider == "codex":
        return codex_argv(prompt)
    if provider == "claude":
        return claude_argv(prompt, skill=skill)
    if provider == "opencode":
        return opencode_argv(prompt)
    if provider == "gemini":
        return gemini_argv(prompt)
    raise RuntimeError(f"unknown provider: {provider}")


def build_prompt(root: Path, args: argparse.Namespace) -> str:
    # Base prompt: --prompt > --prompt-file. MC Core intentionally has no default work order.
    if args.prompt:
        base = args.prompt
    elif args.prompt_file:
        base = read_text(args.prompt_file)
    else:
        raise RuntimeError(
            "MC Core has no default prompt. Start it with --prompt or --prompt-file so the Agent startup defines the work order."
        )

    # Prepend skill prelude if --skill is set
    if args.skill:
        base = SKILL_PRELUDE.format(skill=args.skill) + base

    return base.rstrip()


def command_from_args(args: argparse.Namespace, prompt: str) -> list[str]:
    if args.command:
        return [part.replace("{prompt}", prompt) for part in args.command]
    return provider_argv(args.provider, prompt, skill=args.skill)


class Core:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.root = Path(args.root).resolve()
        self.runtime = self.root / "runtime"
        self.state_path = self.runtime / "state.json"
        self.command_path = self.runtime / "command.json"
        self.pid_path = self.runtime / "core.pid"
        self.last_command_id = read_json(self.command_path).get("id")
        self.round_index = 0
        self.paused = bool(args.start_paused)
        self.wake_once = False
        self.stopping = False
        self.child: subprocess.Popen | None = None

    def write_state(self, status: str, **extra: object) -> None:
        payload = {
            "status": status,
            "pid": os.getpid(),
            "provider": self.args.provider if not self.args.command else "custom",
            "skill": self.args.skill,
            "round": self.round_index,
            "paused": self.paused,
            "updated_at": now_iso(),
            **extra,
        }
        write_json(self.state_path, payload)

    def read_next_command(self) -> dict | None:
        data = read_json(self.command_path)
        command_id = data.get("id")
        if not command_id or command_id == self.last_command_id:
            return None
        self.last_command_id = str(command_id)
        append_event(self.root, {"event": "command", "command": data.get("command"), "id": command_id})
        return data

    def terminate_child(self) -> None:
        if not self.child or self.child.poll() is not None:
            return
        append_event(self.root, {"event": "terminate_child", "pid": self.child.pid})
        self.child.terminate()
        try:
            self.child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            append_event(self.root, {"event": "kill_child", "pid": self.child.pid})
            self.child.kill()
            self.child.wait(timeout=10)

    def handle_command(self) -> None:
        data = self.read_next_command()
        if not data:
            return
        command = data.get("command")
        if command == "pause":
            self.paused = True
            self.write_state("pausing" if self.child else "paused")
        elif command == "resume":
            self.paused = False
            self.write_state("running")
        elif command == "wake":
            self.wake_once = True
            self.write_state("waking")
        elif command == "stop":
            self.stopping = True
            self.write_state("stopping")
            self.terminate_child()
        else:
            append_event(self.root, {"event": "ignored_command", "command": command})

    def sleep_with_commands(self, seconds: float) -> None:
        deadline = time.time() + max(0.0, seconds)
        while not self.stopping and time.time() < deadline:
            self.handle_command()
            if self.wake_once:
                return
            time.sleep(min(1.0, max(0.0, deadline - time.time())))

    def run_round(self) -> int:
        prompt = build_prompt(self.root, self.args)
        argv = command_from_args(self.args, prompt)
        provider = self.args.provider if not self.args.command else "custom"
        missing = shutil.which(argv[0]) is None
        event = {
            "event": "launch",
            "round": self.round_index,
            "provider": provider,
            "skill": self.args.skill,
            "argv0": argv[0],
            "dry_run": self.args.dry_run,
        }
        append_event(self.root, event)
        self.write_state("launching", child_argv0=argv[0], dry_run=self.args.dry_run)

        if self.args.dry_run:
            print(json.dumps({**event, "prompt": prompt}, ensure_ascii=False, indent=2))
            append_event(self.root, {"event": "dry_run_exit", "round": self.round_index})
            return 0
        if missing:
            reason = f"command not found: {argv[0]}"
            append_event(self.root, {"event": "blocked", "round": self.round_index, "reason": reason})
            self.write_state("blocked", last_error=reason)
            raise RuntimeError(reason)

        started = time.time()
        agent_stdout_path = self.root / "logs" / f"agent-round-{self.round_index}.out.log"
        agent_stderr_path = self.root / "logs" / f"agent-round-{self.round_index}.err.log"
        child_cwd = Path(self.args.cwd).resolve() if self.args.cwd else self.root.parent
        agent_stdout_path.parent.mkdir(parents=True, exist_ok=True)
        with agent_stdout_path.open("a", encoding="utf-8") as agent_stdout, agent_stderr_path.open(
            "a", encoding="utf-8"
        ) as agent_stderr:
            child_started_at = now_iso()
            popen_kwargs = {
                "cwd": str(child_cwd),
                "stdin": subprocess.DEVNULL,
                "stdout": agent_stdout,
                "stderr": agent_stderr,
            }
            if os.name == "nt":
                popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self.child = subprocess.Popen(argv, **popen_kwargs)
            self.write_state(
                "running",
                child_pid=self.child.pid,
                child_cwd=str(child_cwd),
                child_started_at=child_started_at,
                child_stdout=str(agent_stdout_path),
                child_stderr=str(agent_stderr_path),
            )
            last_heartbeat = time.time()
            while self.child.poll() is None:
                self.handle_command()
                if time.time() - last_heartbeat >= 5.0:
                    self.write_state(
                        "running",
                        child_pid=self.child.pid,
                        child_cwd=str(child_cwd),
                        child_started_at=child_started_at,
                        child_stdout=str(agent_stdout_path),
                        child_stderr=str(agent_stderr_path),
                    )
                    last_heartbeat = time.time()
                time.sleep(1.0)

            returncode = int(self.child.returncode)
        elapsed = round(time.time() - started, 3)
        append_event(
            self.root,
            {
                "event": "exit",
                "round": self.round_index,
                "provider": provider,
                "skill": self.args.skill,
                "returncode": returncode,
                "elapsed_seconds": elapsed,
            },
        )
        self.child = None
        return returncode

    def run(self) -> int:
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.pid_path.write_text(str(os.getpid()), encoding="utf-8")
        append_event(self.root, {"event": "core_start", "pid": os.getpid(), "skill": self.args.skill})
        self.write_state("paused" if self.paused else "running", started_at=now_iso())

        try:
            while not self.stopping:
                self.handle_command()
                if self.paused and not self.wake_once:
                    self.write_state("paused")
                    self.sleep_with_commands(1.0)
                    continue

                self.wake_once = False
                self.round_index += 1
                self.run_round()
                if self.args.dry_run or (self.args.max_rounds and self.round_index >= self.args.max_rounds):
                    self.write_state("completed")
                    append_event(self.root, {"event": "core_complete", "round": self.round_index})
                    return 0
                if not self.stopping and not self.paused:
                    self.write_state("sleeping")
                    self.sleep_with_commands(self.args.interval)

            self.write_state("stopped")
            append_event(self.root, {"event": "core_stop"})
            return 0
        except KeyboardInterrupt:
            self.stopping = True
            self.terminate_child()
            self.write_state("stopped", reason="keyboard_interrupt")
            append_event(self.root, {"event": "core_stop", "reason": "keyboard_interrupt"})
            return 130
        except Exception as exc:
            self.terminate_child()
            self.write_state("error", last_error=str(exc))
            append_event(self.root, {"event": "core_error", "error": str(exc)})
            raise
        finally:
            try:
                if self.pid_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                    self.pid_path.unlink()
            except FileNotFoundError:
                pass


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Mission Control core process (imboss edition).")
    parser.add_argument("--root", default=".boss", help=".boss directory (default: .boss for imboss)")
    parser.add_argument("--provider", choices=["codex", "claude", "opencode", "gemini"], default="codex")
    parser.add_argument(
        "--command",
        nargs=argparse.REMAINDER,
        help="custom command placed last; use {prompt} where the MC prompt should go",
    )
    parser.add_argument("--prompt", help="inline work order for the Agent CLI (required unless --prompt-file is used)")
    parser.add_argument("--prompt-file", type=Path, help="read the Agent CLI work order from a file")
    parser.add_argument("--skill", help="skill to load before the main prompt (e.g. imboss)")
    parser.add_argument("--cwd", help="working directory for the Agent CLI child process")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds to wait between launches")
    parser.add_argument("--max-rounds", type=positive_int, help="stop after this many launches")
    parser.add_argument("--dry-run", action="store_true", help="print the assembled invocation without starting Agent CLI")
    parser.add_argument("--start-paused", action="store_true", help="start core in paused state")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return Core(args).run()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
