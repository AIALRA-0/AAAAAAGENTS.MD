from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "agents_artifacts" / "outputs" / "baseline.json"
FINALIZE_STATE_PATH = ROOT / "agents_artifacts" / "outputs" / "finalize_state.json"

READ_ONLY_FILES = [
    "AGENTS.md",
    "BACKGROUND.md",
    "RESOURCE.md",
    "agents_standards/PYTHON_STANDARD.md",
    "agents_standards/MARKDOWN_STANDARD.md",
]
IGNORED_HASH_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", ".venv-win", ".venv-linux", "venv", "node_modules"}
IGNORED_HASH_PREFIXES = {
    "agents_artifacts/",
    "agents_web/__pycache__/",
    "agents_tools/__pycache__/",
}
IGNORED_HASH_FILES = {
    "agents_artifacts/outputs/baseline.json",
    "agents_artifacts/outputs/finalize_state.json",
    "agents_artifacts/outputs/tree_state.json",
}
DOC_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
DATA_BLOCK_RE = re.compile(r"##\s*DATA.*?```(?:yaml|yml|json)\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
SECTION_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SECTION_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*-\s*([^:：]+?)\s*[:：]\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s{2,}-\s*(.+)$")
TIME_FMT = "%Y-%m-%d-%H-%M"


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def now_stamp() -> str:
    return datetime.now().strftime(TIME_FMT)


def read_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    match = DOC_FRONTMATTER_RE.search(text)
    if not match:
        return {}
    parsed: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def extract_section(text: str, section_name: str) -> str:
    lines = normalize_text(text).splitlines()
    start_idx = -1
    for idx, line in enumerate(lines):
        match = SECTION_H2_RE.match(line.strip())
        if match and match.group(1).strip().lower() == section_name.strip().lower():
            start_idx = idx + 1
            break
    if start_idx < 0:
        return ""
    end_idx = len(lines)
    for idx in range(start_idx, len(lines)):
        if SECTION_H2_RE.match(lines[idx].strip()):
            end_idx = idx
            break
    return "\n".join(lines[start_idx:end_idx]).strip()


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text or text == "[]":
        return []
    return [text]


def parse_markdown_records(section_text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    list_field: str | None = None
    for raw_line in normalize_text(section_text).splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        h3 = SECTION_H3_RE.match(line.strip())
        if h3:
            current = {"__title": h3.group(1).strip()}
            records.append(current)
            list_field = None
            continue
        if current is None:
            continue
        item_match = LIST_ITEM_RE.match(line)
        if item_match and list_field:
            item = item_match.group(1).strip()
            if item:
                existing = current.get(list_field)
                if not isinstance(existing, list):
                    existing = []
                    current[list_field] = existing
                existing.append(item)
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            key = field_match.group(1).strip()
            value = field_match.group(2).strip()
            if value == "" or value == "[]":
                current[key] = []
                list_field = key if value == "" else None
            else:
                current[key] = value
                list_field = None
            continue
    return records


def parse_layout_positions(layout_text: str) -> dict[str, dict[str, float]]:
    if not layout_text.strip():
        return {}
    records = parse_markdown_records(layout_text)
    if not records:
        return {}
    positions: dict[str, dict[str, float]] = {}
    for rec in records:
        node_id = str(rec.get("id") or rec.get("__title") or "").strip()
        if not node_id:
            continue
        try:
            x = float(str(rec.get("x", "")).strip())
            y = float(str(rec.get("y", "")).strip())
        except ValueError:
            continue
        positions[node_id] = {"x": x, "y": y}
    return positions


def parse_json_data_payload(text: str) -> dict[str, Any]:
    match = DATA_BLOCK_RE.search(text)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def parse_data_payload(path: Path) -> dict[str, Any]:
    text = read_text(path)
    if path.name == "MILESTONE.md":
        records = parse_markdown_records(extract_section(text, "DATA"))
        milestones: list[dict[str, Any]] = []
        for rec in records:
            node_id = str(rec.get("id") or rec.get("__title") or "").strip()
            if not node_id:
                continue
            milestones.append(
                {
                    "id": node_id,
                    "title": str(rec.get("title", "")).strip(),
                    "prerequisites": normalize_list(rec.get("prerequisites")),
                    "postnodes": normalize_list(rec.get("postnodes")),
                    "why": normalize_list(rec.get("why")),
                    "what": normalize_list(rec.get("what")),
                    "how": normalize_list(rec.get("how")),
                    "verify": normalize_list(rec.get("verify")),
                    "status": str(rec.get("status", "")).strip(),
                    "notes": normalize_list(rec.get("notes")),
                    "updated_at": str(rec.get("updated_at", "")).strip(),
                }
            )
        if milestones:
            return {"milestones": milestones, "layout": {"positions": parse_layout_positions(extract_section(text, "LAYOUT"))}}
    if path.name == "CHANGE.md":
        records = parse_markdown_records(extract_section(text, "DATA"))
        changes: list[dict[str, Any]] = []
        for rec in records:
            version = str(rec.get("version") or rec.get("__title") or "").strip()
            if not version:
                continue
            changes.append(
                {
                    "version": version,
                    "date": str(rec.get("date", "")).strip(),
                    "reason": normalize_list(rec.get("reason")),
                    "action": normalize_list(rec.get("action")),
                    "observation": normalize_list(rec.get("observation")),
                    "impacted_files": normalize_list(rec.get("impacted_files")),
                    "notes": normalize_list(rec.get("notes")),
                    "suggestions": normalize_list(rec.get("suggestions")),
                }
            )
        if changes:
            return {"changes": changes}
    return parse_json_data_payload(text)


def to_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_ignored_hash_path(rel: str) -> bool:
    if rel in IGNORED_HASH_FILES:
        return True
    if any(rel.startswith(prefix) for prefix in IGNORED_HASH_PREFIXES):
        return True
    parts = rel.split("/")
    return any(part in IGNORED_HASH_DIRS for part in parts)


def compute_all_file_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for root, dirs, names in os.walk(ROOT):
        root_path = Path(root)
        dirs[:] = sorted([d for d in dirs if d not in IGNORED_HASH_DIRS], key=str.lower)
        names = sorted(names, key=str.lower)
        for name in names:
            path = root_path / name
            rel = to_rel(path)
            if is_ignored_hash_path(rel):
                continue
            hashes[rel] = sha256_text(read_text(path))
    return dict(sorted(hashes.items(), key=lambda kv: kv[0].lower()))


def compute_dir_hashes(dir_name: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in (ROOT / dir_name).rglob("*"):
        if not path.is_file():
            continue
        rel = to_rel(path)
        if "__pycache__" in rel or rel.endswith(".pyc"):
            continue
        result[rel] = sha256_text(read_text(path))
    return dict(sorted(result.items(), key=lambda kv: kv[0].lower()))


def milestone_signature(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node.get("id"),
        "title": node.get("title"),
        "prerequisites": node.get("prerequisites"),
        "postnodes": node.get("postnodes"),
        "why": node.get("why"),
        "what": node.get("what"),
        "how": node.get("how"),
        "verify": node.get("verify"),
        "notes": node.get("notes"),
    }


def build_milestone_structure() -> dict[str, Any]:
    payload = parse_data_payload(ROOT / "MILESTONE.md")
    milestones = payload.get("milestones", [])
    ids: list[str] = []
    signature_by_id: dict[str, Any] = {}
    status_by_id: dict[str, str] = {}
    if isinstance(milestones, list):
        for node in milestones:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id", "")).strip()
            if not node_id:
                continue
            ids.append(node_id)
            signature_by_id[node_id] = milestone_signature(node)
            status_by_id[node_id] = str(node.get("status", ""))
    return {"ids": ids, "signature_by_id": signature_by_id, "status_by_id": status_by_id}


def build_change_entries() -> list[dict[str, Any]]:
    payload = parse_data_payload(ROOT / "CHANGE.md")
    changes = payload.get("changes", [])
    if isinstance(changes, list):
        return [item for item in changes if isinstance(item, dict)]
    return []


def build_tree_nodes() -> list[dict[str, Any]]:
    payload = parse_data_payload(ROOT / "TREE.md")
    nodes = payload.get("nodes", [])
    if isinstance(nodes, list):
        return [item for item in nodes if isinstance(item, dict)]
    return []


def main() -> int:
    read_only_hashes: dict[str, str] = {}
    read_only_frontmatter_keys: dict[str, list[str]] = {}
    for rel in READ_ONLY_FILES:
        path = ROOT / rel
        read_only_hashes[rel] = sha256_text(read_text(path))
        frontmatter = parse_frontmatter(read_text(path))
        read_only_frontmatter_keys[rel] = sorted(frontmatter.keys())

    milestone_structure = build_milestone_structure()
    file_hashes = compute_all_file_hashes()
    baseline = {
        "updated_at": now_stamp(),
        "read_only_hashes": read_only_hashes,
        "read_only_frontmatter_keys": read_only_frontmatter_keys,
        "standards_file_list": sorted([to_rel(p) for p in (ROOT / "agents_standards").glob("*.md")]),
        "agents_tools_hashes": compute_dir_hashes("agents_tools"),
        "agents_web_hashes": compute_dir_hashes("agents_web"),
        "milestone_structure": {
            "ids": milestone_structure["ids"],
            "signature_by_id": milestone_structure["signature_by_id"],
        },
        "file_hashes": file_hashes,
    }

    finalize_state = {
        "last_finalized_at": now_stamp(),
        "file_hashes": file_hashes,
        "milestone_statuses": milestone_structure["status_by_id"],
        "change_entries": build_change_entries(),
        "tree_nodes": build_tree_nodes(),
        "skip_progress_checks_once": True,
        "state_source": "baseline_refresh",
    }

    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    FINALIZE_STATE_PATH.write_text(json.dumps(finalize_state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "baseline": BASELINE_PATH.relative_to(ROOT).as_posix(),
                "finalize_state": FINALIZE_STATE_PATH.relative_to(ROOT).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
