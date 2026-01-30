#!/usr/bin/env python3
"""Run Claude Code (claude CLI) in headless mode reliably.

Why this wrapper exists:
- Claude Code can hang when run without a TTY.
- Clawdbot exec is often non-interactive.
- We run `claude ...` via `script -q -c` to allocate a pseudo-terminal.

This is a thin passthrough for common flags documented at:
https://code.claude.com/docs/en/headless
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


DEFAULT_CLAUDE = os.environ.get("CLAUDE_CODE_BIN", "/home/ubuntu/.local/bin/claude")


def build_cmd(args: argparse.Namespace) -> list[str]:
    claude_bin = args.claude_bin

    cmd: list[str] = [claude_bin]

    # Permission mode
    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]

    # Headless prompt
    if args.prompt is not None:
        cmd += ["-p", args.prompt]

    # Pass-through common options
    if args.allowedTools:
        cmd += ["--allowedTools", args.allowedTools]

    if args.output_format:
        cmd += ["--output-format", args.output_format]

    if args.json_schema:
        cmd += ["--json-schema", args.json_schema]

    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]

    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]

    if args.continue_latest:
        cmd.append("--continue")

    if args.resume:
        cmd += ["--resume", args.resume]

    # Any extra args after --
    if args.extra:
        cmd += args.extra

    return cmd


def run_with_pty(cmd: list[str], cwd: str | None) -> int:
    """Run command through `script` to force a pseudo-terminal."""
    # `script` is widely available on Linux. Write to /dev/null, quiet mode.
    # Use a shell command string so script can execute it.
    cmd_str = " ".join(shlex.quote(c) for c in cmd)

    script_bin = shutil_which("script")
    if not script_bin:
        # Fall back to direct run (may hang in some environments)
        proc = subprocess.run(cmd, cwd=cwd, text=True)
        return proc.returncode

    proc = subprocess.run([script_bin, "-q", "-c", cmd_str, "/dev/null"], cwd=cwd, text=True)
    return proc.returncode


def shutil_which(name: str) -> str | None:
    # local tiny implementation to avoid importing shutil (keeps script minimal)
    paths = os.environ.get("PATH", "").split(":")
    for p in paths:
        cand = Path(p) / name
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        except OSError:
            pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Run Claude Code (claude CLI) headlessly via a pseudo-terminal")

    ap.add_argument("-p", "--prompt", help="Headless prompt (Claude Code -p)")
    ap.add_argument(
        "--permission-mode",
        choices=["plan", "auto-accept", "normal"],
        default=None,
        help="Permission mode (best practice: plan for read-only analysis)",
    )

    ap.add_argument("--allowedTools", dest="allowedTools", help="Allowed tools allowlist string")
    ap.add_argument("--output-format", dest="output_format", choices=["text", "json", "stream-json"], help="Output format")
    ap.add_argument("--json-schema", dest="json_schema", help="JSON schema (string) when using --output-format json")

    ap.add_argument("--append-system-prompt", dest="append_system_prompt", help="Append to Claude Code default system prompt")
    ap.add_argument("--system-prompt", dest="system_prompt", help="Replace system prompt")

    ap.add_argument("--continue", dest="continue_latest", action="store_true", help="Continue the most recent session")
    ap.add_argument("--resume", help="Resume a specific session ID")

    ap.add_argument(
        "--claude-bin",
        default=DEFAULT_CLAUDE,
        help=f"Path to claude binary (default: {DEFAULT_CLAUDE}). You can also set CLAUDE_CODE_BIN.",
    )

    ap.add_argument("--cwd", help="Working directory to run claude in (defaults to current directory)")

    ap.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args after --")

    args = ap.parse_args()

    # Clean leading -- from extra
    extra = args.extra
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra

    if not Path(args.claude_bin).exists():
        print(f"claude binary not found: {args.claude_bin}", file=sys.stderr)
        print("Tip: set CLAUDE_CODE_BIN=/path/to/claude", file=sys.stderr)
        return 2

    cmd = build_cmd(args)
    return run_with_pty(cmd, cwd=args.cwd)


if __name__ == "__main__":
    raise SystemExit(main())
