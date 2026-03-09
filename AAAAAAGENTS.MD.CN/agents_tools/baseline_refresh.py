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


def parse_data_payload(path: Path) -> dict[str, Any]:
    text = read_text(path)
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
        "ddl": node.get("ddl"),
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
