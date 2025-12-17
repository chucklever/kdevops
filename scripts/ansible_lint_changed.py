#!/usr/bin/env python3
"""
Run ansible-lint only on changed lines.

This script filters ansible-lint warnings to show only issues on lines
that were modified in the working directory, staging area, or current
commit (for stg workflow support).
"""

import json
import re
import subprocess
import sys
from collections import defaultdict


def get_changed_lines_workdir():
    """Get changed lines from working directory (unstaged changes)."""
    return _parse_diff(["git", "diff", "--unified=0", "--", "playbooks/"])


def get_changed_lines_staged():
    """Get changed lines from staging area."""
    return _parse_diff(["git", "diff", "--cached", "--unified=0", "--", "playbooks/"])


def get_changed_lines_head():
    """Get changed lines from HEAD commit (for post-stg-refresh)."""
    return _parse_diff(
        ["git", "diff-tree", "-p", "--unified=0", "HEAD", "--", "playbooks/"]
    )


def _parse_diff(cmd):
    """
    Parse unified diff output to extract file -> set of changed line numbers.

    Returns dict: {filepath: {line_numbers}}
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
    except Exception:
        return {}

    changed = defaultdict(set)
    current_file = None

    for line in output.split("\n"):
        # Match file header: +++ b/playbooks/foo.yml
        if line.startswith("+++ b/"):
            current_file = line[6:]  # Remove '+++ b/' prefix
        # Match hunk header: @@ -old,count +new,count @@
        elif line.startswith("@@") and current_file:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) else 1
                # Add all lines in the range
                for i in range(start, start + count):
                    changed[current_file].add(i)

    return dict(changed)


def run_ansible_lint(files):
    """Run ansible-lint and return parsed JSON issues."""
    if not files:
        return []

    cmd = ["ansible-lint", "-f", "json", "--nocolor"] + list(files)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # JSON is on first line of stdout
        first_line = result.stdout.split("\n")[0]
        if first_line.startswith("["):
            return json.loads(first_line)
    except Exception as e:
        print(f"Error running ansible-lint: {e}", file=sys.stderr)
    return []


def filter_issues_to_changed_lines(issues, changed_lines):
    """Filter issues to only those on changed lines."""
    filtered = []
    for issue in issues:
        filepath = issue.get("location", {}).get("path", "")
        line = issue.get("location", {}).get("lines", {}).get("begin", 0)

        if filepath in changed_lines and line in changed_lines[filepath]:
            filtered.append(issue)

    return filtered


def format_issue(issue):
    """Format an issue for display."""
    path = issue.get("location", {}).get("path", "unknown")
    line = issue.get("location", {}).get("lines", {}).get("begin", "?")
    rule = issue.get("check_name", "unknown")
    severity = issue.get("severity", "unknown")
    desc = issue.get("description", "")
    # Truncate long descriptions
    if len(desc) > 80:
        desc = desc[:77] + "..."
    return f"{path}:{line}: [{severity}] {rule}: {desc}"


def main():
    # Collect changed lines from all sources
    changed_lines = defaultdict(set)

    for source_fn in [
        get_changed_lines_workdir,
        get_changed_lines_staged,
        get_changed_lines_head,
    ]:
        for filepath, lines in source_fn().items():
            changed_lines[filepath].update(lines)

    if not changed_lines:
        # No ansible files changed
        return 0

    # Get all changed ansible files
    changed_files = [f for f in changed_lines.keys() if f.endswith((".yml", ".yaml"))]

    if not changed_files:
        return 0

    print(f"Checking {len(changed_files)} changed ansible file(s)...", file=sys.stderr)

    # Run ansible-lint on changed files only
    issues = run_ansible_lint(changed_files)

    # Filter to only issues on changed lines
    filtered = filter_issues_to_changed_lines(issues, changed_lines)

    if not filtered:
        print("No ansible-lint issues on changed lines.", file=sys.stderr)
        return 0

    # Display filtered issues
    print(f"\n{len(filtered)} issue(s) on changed lines:\n", file=sys.stderr)
    for issue in filtered:
        print(format_issue(issue))

    return 1 if filtered else 0


if __name__ == "__main__":
    sys.exit(main())
