#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL_FIELDS = ["id", "data_content", "annotation", "final_result", "split_info", "metadata"]
REQUIRED_METADATA_FIELDS = ["dataset_name", "schema_version", "metadata_scope", "manifest_ref", "rag_config"]

def get_nested(obj, path):
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur

def validate_record(record, line_no):
    errors = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in record:
            errors.append(f"line {line_no}: missing top-level field: {field}")
    content = record.get("data_content")
    if not isinstance(content, list) or not content or not content[0].get("content"):
        errors.append(f"line {line_no}: data_content[0].content is required")
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append(f"line {line_no}: metadata must be an object")
    else:
        for field in REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                errors.append(f"line {line_no}: missing metadata field: {field}")
        do_not_embed = get_nested(metadata, ["rag_config", "do_not_embed_fields"])
        if isinstance(do_not_embed, list) and "metadata" not in do_not_embed:
            errors.append(f"line {line_no}: metadata should be listed in do_not_embed_fields")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_jsonl_schema.py <path.jsonl>")
        return 2
    path = Path(sys.argv[1])
    errors = []
    count = 0
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON: {exc}")
                continue
            errors.extend(validate_record(record, line_no))
    if errors:
        print("[FAIL] validation failed")
        for e in errors[:100]:
            print("-", e)
        return 1
    print(f"[PASS] {path} is valid. records={count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
