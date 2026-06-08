#!/usr/bin/env python3
"""
AI Log Analyser for SONiC platform=vs pipeline failures.
Reads a log file, extracts error lines, and asks GPT-4o to explain them.

Usage:
    python analyze.py <log_file>
    OPENAI_API_KEY=sk-... python analyze.py build.log
"""

import os
import re
import sys

from openai import OpenAI

FAIL_RE = re.compile(
    r"\b(error|failed|failure|fatal|critical|crash|panic|timeout|"
    r"segfault|oom|killed|refused|unavailable|not found|unable|abort)\b",
    re.IGNORECASE,
)

PROMPT = """You are a SONiC network OS expert (platform=vs).
Analyse these failed log lines from a SONiC VS CI pipeline.
For each distinct issue output:

Issue: <title>
Severity: Critical | High | Medium | Low
Root cause: <one sentence>
Fix: <one SONiC VS command or action>

Group duplicates. Keep it concise."""


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python analyze.py <log_file>")

    log_file = sys.argv[1]
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY environment variable not set.")

    # Extract failure lines
    failed: list[str] = []
    try:
        with open(log_file, errors="replace") as fh:
            for line in fh:
                if FAIL_RE.search(line):
                    failed.append(line.strip())
    except FileNotFoundError:
        sys.exit(f"ERROR: Log file not found: {log_file}")

    if not failed:
        print("No failures found in log — pipeline looks healthy.")
        return

    print(f"Found {len(failed)} failure lines. Sending to GPT-4o for analysis...\n")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user",   "content": "\n".join(failed[:200])},
        ],
        temperature=0.2,
    )

    print("=" * 60)
    print("       SONiC VS Pipeline Failure Analysis")
    print("=" * 60)
    print(response.choices[0].message.content)
    print("=" * 60)


if __name__ == "__main__":
    main()
