#!/usr/bin/env python3
"""Refresh an append-only approval-pipeline ledger from Obsidian frontmatter.

Existing records are updated but never removed. A note that is later filed,
renamed, merged, or deleted therefore keeps its proposal-versus-outcome record.
"""

import argparse
import datetime
import json
import os
import re
import sys


KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
FIELDS = [
    "created", "item_type", "active_todo", "approval_stage", "approve", "hold",
    "proposed_dest", "user_dest", "final_dest", "pipeline_outcome",
    "pipeline_started", "pipeline_finished", "agent_note",
]


def get_frontmatter(path):
    """Parse simple key/value YAML frontmatter without requiring PyYAML."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return None
    if len(lines) < 2 or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None

    frontmatter = {}
    current_key = None
    for line in lines[1:end]:
        match = KEY_RE.match(line)
        if match:
            current_key = match.group(1)
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            frontmatter[current_key] = value
        elif current_key and re.match(r"^\s+\S", line):
            frontmatter[current_key] = (
                frontmatter[current_key] + " " + line.strip()
            ).strip()
    return frontmatter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault")
    parser.add_argument(
        "--ledger",
        default=os.path.join(os.path.dirname(__file__), "approval_ledger.json"),
        help="Append-only JSON ledger path",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[".trash"],
        help="Folder-name fragment to skip; repeat as needed",
    )
    args = parser.parse_args()
    if not os.path.isdir(args.vault):
        sys.exit("vault not found -- pass --vault <path>")

    today = datetime.date.today().isoformat()
    ledger = {}
    if os.path.isfile(args.ledger):
        with open(args.ledger, encoding="utf-8-sig") as handle:
            raw = handle.read().strip()
        if raw:
            ledger = {record["id"]: record for record in json.loads(raw)}
    previous_count = len(ledger)

    seen = 0
    seen_ids = set()
    for root, directories, files in os.walk(args.vault):
        directories[:] = [
            name for name in directories
            if not any(fragment in os.path.join(root, name) for fragment in args.exclude)
        ]
        for name in files:
            if not name.endswith(".md"):
                continue
            full_path = os.path.join(root, name)
            frontmatter = get_frontmatter(full_path)
            if not frontmatter or "approval_stage" not in frontmatter:
                continue
            seen += 1
            title = name[:-3]
            created_stamp = frontmatter.get("created", "")
            preferred_id = "{}|{}".format(title, created_stamp)
            created_matches = [
                key for key, item in ledger.items()
                if created_stamp and item.get("created") == created_stamp
            ]
            if preferred_id in ledger:
                record_id = preferred_id
            elif len(created_matches) == 1:
                record_id = created_matches[0]
            else:
                record_id = preferred_id
            seen_ids.add(record_id)
            record = ledger.get(record_id, {
                "id": record_id,
                "first_seen": today,
            })
            record["title"] = title
            for field in FIELDS:
                record[field] = frontmatter.get(field)
            record["current_path"] = os.path.relpath(full_path, args.vault)
            record["last_seen"] = today
            record["vanished"] = False
            ledger[record_id] = record

    for record_id, record in ledger.items():
        record["vanished"] = record_id not in seen_ids

    records = sorted(
        ledger.values(),
        key=lambda record: (
            record.get("pipeline_started") or "",
            (record.get("title") or "").lower(),
        ),
    )
    with open(args.ledger, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    resolved = [record for record in records if record.get("approval_stage") != "review"]
    agreed = sum(record.get("pipeline_outcome") == "approved-and-filed" for record in resolved)
    redirected = sum(record.get("pipeline_outcome") == "redirected-and-filed" for record in resolved)
    in_review = sum(record.get("approval_stage") == "review" for record in records)
    vanished = sum(bool(record.get("vanished")) for record in records)
    rate = round(100 * redirected / len(resolved)) if resolved else 0

    print("notes scanned with approval frontmatter : {}".format(seen))
    print("ledger records  : {}  (was {})".format(len(records), previous_count))
    print("resolved        : {}   in review: {}   vanished-but-retained: {}".format(
        len(resolved), in_review, vanished
    ))
    print("agreed          : {}".format(agreed))
    print("overridden      : {}  ({}% of resolved)".format(redirected, rate))
    print("ledger -> {}".format(args.ledger))


if __name__ == "__main__":
    main()
