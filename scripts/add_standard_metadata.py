#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 4:
        print("Usage: python scripts/add_standard_metadata.py <input.jsonl> <output.jsonl> <manifest.json>")
        return 2
    input_path, output_path, manifest_path = map(Path, sys.argv[1:])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata = {
        "dataset_name": manifest.get("dataset_name"),
        "schema_version": manifest.get("schema_version", "1.1.0"),
        "metadata_scope": "record_with_dataset_context",
        "manifest_ref": manifest_path.name,
        "split_config": manifest.get("split_config", {}),
        "rag_config": manifest.get("rag_config", {}),
    }
    do_not_embed = metadata["rag_config"].setdefault("do_not_embed_fields", [])
    if "metadata" not in do_not_embed:
        do_not_embed.append("metadata")
    count = 0
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            record = json.loads(line)
            new_record = copy.deepcopy(record)
            new_record["metadata"] = copy.deepcopy(metadata)
            new_record["version"] = metadata["schema_version"]
            fout.write(json.dumps(new_record, ensure_ascii=False, separators=(",", ":")) + "\n")
            count += 1
    print(f"[OK] wrote {count} records to {output_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
