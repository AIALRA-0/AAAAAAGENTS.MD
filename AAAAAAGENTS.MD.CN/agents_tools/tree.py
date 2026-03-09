from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TREE_MD_PATH = ROOT / "TREE.md"
STATE_PATH = ROOT / "agents_artifacts" / "outputs" / "tree_state.json"

EDITABLE_FILES = {"MILESTONE.md", "CHANGE.md", "TREE.md"}
IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", ".venv-win", ".venv-linux", "venv", "node_modules"}
IGNORED_RELATIVE_PATHS = {"agents_artifacts/outputs/tree_state.json"}
IGNORED_RELATIVE_PREFIXES = {"agents_artifacts/outputs/web_backups/"}
DATA_BLOCK_RE = re.compile(r"##\s*DATA.*?```(?:yaml|yml|json)\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
TIME_FMT = "%Y-%m-%d-%H-%M"
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")


def now_stamp() -> str:
    return datetime.now().strftime(TIME_FMT)


def to_stamp(value: datetime) -> str:
    return value.strftime(TIME_FMT)


def normalize_stamp(raw: Any) -> str:
    value = str(raw or "").strip()
    if TIME_RE.fullmatch(value):
        return value
    if value:
        candidates = [value, value.replace("T", " ")]
        for cand in candidates:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
                try:
                    return datetime.strptime(cand, fmt).strftime(TIME_FMT)
                except ValueError:
                    continue
    return now_stamp()


def to_posix(path: Path) -> str:
    return path.as_posix()


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def is_ignored_relative(rel_path: str) -> bool:
    value = str(rel_path).replace("\\", "/").strip("/")
    if value in IGNORED_RELATIVE_PATHS:
        return True
    for prefix in IGNORED_RELATIVE_PREFIXES:
        clean_prefix = prefix.strip("/")
        if value == clean_prefix or value.startswith(clean_prefix + "/"):
            return True
    return False


def default_note_for_path(path_str: str, is_dir: bool) -> str:
    rel = str(path_str).replace("\\", "/")
    if rel.startswith("agents_standards/") and rel.endswith("_STANDARD.md"):
        stem = Path(rel).stem
        kind = stem.replace("_STANDARD", "").replace("_", " ").strip().upper()
        if not kind:
            kind = "通用"
        return f"{kind} 标准规范文件，定义该类型内容的编写、注释、格式与校验要求"
    if is_dir and rel == "agents_standards":
        return "标准规范目录，集中管理各类型文件的标准文档"
    if is_dir and rel == "agents_web/static":
        return "Web 静态资源目录，存放样式与前端脚本"
    if rel == "agents_web/static/app.css":
        return "工作台样式文件，定义整体界面布局与视觉风格"
    if rel == "agents_web/static/app.js":
        return "工作台前端脚本文件，处理交互、渲染与接口调用"
    return ""


def load_existing_nodes_from_tree_md() -> dict[str, dict[str, Any]]:
    if not TREE_MD_PATH.exists():
        return {}
    text = TREE_MD_PATH.read_text(encoding="utf-8")
    match = DATA_BLOCK_RE.search(text)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return {}
    nodes = payload.get("nodes", [])
    if not isinstance(nodes, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("path"), str):
            result[node["path"]] = node
    return result


def load_existing_nodes_from_state() -> dict[str, dict[str, Any]]:
    if not STATE_PATH.exists():
        return {}
    try:
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    nodes = payload.get("nodes", [])
    if not isinstance(nodes, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("path"), str):
            result[node["path"]] = node
    return result


def load_previous_nodes() -> dict[str, dict[str, Any]]:
    from_tree = load_existing_nodes_from_tree_md()
    if from_tree:
        return from_tree
    return load_existing_nodes_from_state()


def infer_parent(path_str: str) -> str:
    if path_str in {"", "."}:
        return ""
    parent = str(Path(path_str).parent).replace("\\", "/")
    return "." if parent in {"", "."} else parent


def scan_active_nodes(previous_nodes: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    root_mtime = to_stamp(datetime.fromtimestamp(ROOT.stat().st_mtime))
    root_note = ""
    if "." in previous_nodes and isinstance(previous_nodes["."].get("note"), str):
        root_note = str(previous_nodes["."].get("note"))
    nodes: dict[str, dict[str, Any]] = {
        ".": {
            "path": ".",
            "name": ".",
            "parent": "",
            "type": "dir",
            "status": "active",
            "last_modified": root_mtime,
            "editable": False,
            "note": root_note,
        }
    }

    for current, dirs, files in os.walk(ROOT):
        current_path = Path(current)
        rel_current = current_path.relative_to(ROOT)
        rel_current_str = "." if str(rel_current) == "." else to_posix(rel_current)
        if rel_current_str != "." and is_ignored_relative(rel_current_str):
            dirs[:] = []
            continue
        dirs[:] = sorted([d for d in dirs if d not in IGNORED_DIRS], key=str.lower)
        dirs[:] = [
            d
            for d in dirs
            if not is_ignored_relative(
                to_posix((Path(rel_current_str if rel_current_str != "." else "") / d))
                if rel_current_str != "."
                else d
            )
        ]
        files = sorted(files, key=str.lower)

        if rel_current_str != ".":
            stat = current_path.stat()
            note = ""
            old = previous_nodes.get(rel_current_str, {})
            if isinstance(old.get("note"), str):
                note = str(old["note"])
            if not note.strip():
                note = default_note_for_path(rel_current_str, True)
            nodes[rel_current_str] = {
                "path": rel_current_str,
                "name": current_path.name,
                "parent": infer_parent(rel_current_str),
                "type": "dir",
                "status": "active",
                "last_modified": to_stamp(datetime.fromtimestamp(stat.st_mtime)),
                "editable": False,
                "note": note,
            }

        for file_name in files:
            rel_file_str = to_posix((current_path / file_name).relative_to(ROOT))
            if is_ignored_relative(rel_file_str):
                continue
            rel_file = Path(rel_file_str)
            if is_ignored(rel_file):
                continue
            stat = (current_path / file_name).stat()
            old = previous_nodes.get(rel_file_str, {})
            note = ""
            if isinstance(old.get("note"), str):
                note = str(old["note"])
            if not note.strip():
                note = default_note_for_path(rel_file_str, False)
            nodes[rel_file_str] = {
                "path": rel_file_str,
                "name": file_name,
                "parent": infer_parent(rel_file_str),
                "type": "file",
                "status": "active",
                "last_modified": to_stamp(datetime.fromtimestamp(stat.st_mtime)),
                "editable": rel_file_str in EDITABLE_FILES,
                "note": note,
            }
    return nodes


def merge_deleted_nodes(
    active_nodes: dict[str, dict[str, Any]], previous_nodes: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    merged = dict(active_nodes)
    for path_str, old in previous_nodes.items():
        if path_str in {"."} or is_ignored_relative(path_str) or path_str in merged:
            continue
        node_type = str(old.get("type") or ("dir" if path_str.endswith("/") else "file"))
        if node_type not in {"file", "dir"}:
            node_type = "file"
        note = old.get("note")
        merged[path_str] = {
            "path": path_str,
            "name": str(old.get("name") or Path(path_str).name),
            "parent": str(old.get("parent") or infer_parent(path_str)),
            "type": node_type,
            "status": "deleted",
            "last_modified": normalize_stamp(old.get("last_modified")),
            "editable": bool(old.get("editable")) if node_type == "file" else False,
            "note": str(note) if isinstance(note, str) else "",
        }
    return merged


def sort_key(node: dict[str, Any]) -> tuple[int, int, str]:
    status_rank = 1 if node.get("status") == "deleted" else 0
    type_rank = 0 if node.get("type") == "dir" else 1
    return (status_rank, type_rank, str(node.get("name", "")).lower())


def build_snapshot() -> dict[str, Any]:
    previous_nodes = load_previous_nodes()
    active_nodes = scan_active_nodes(previous_nodes)
    merged_nodes = merge_deleted_nodes(active_nodes, previous_nodes)
    ordered_nodes = sorted(merged_nodes.values(), key=lambda n: (str(n.get("parent", "")),) + sort_key(n))
    return {"last_updated": now_stamp(), "nodes": ordered_nodes}


def build_tree_text(snapshot: dict[str, Any]) -> str:
    nodes = snapshot.get("nodes", [])
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("status") != "active":
            continue
        parent = str(node.get("parent", ""))
        by_parent.setdefault(parent, []).append(node)
    for children in by_parent.values():
        children.sort(key=lambda n: (0 if n.get("type") == "dir" else 1, str(n.get("name", "")).lower()))

    lines: list[str] = ["."]

    def walk(parent_path: str, prefix: str) -> None:
        children = by_parent.get(parent_path, [])
        for idx, child in enumerate(children):
            is_last = idx == len(children) - 1
            branch = "└── " if is_last else "├── "
            lines.append(prefix + branch + str(child.get("name", "")))
            if child.get("type") == "dir":
                walk(str(child.get("path")), prefix + ("    " if is_last else "│   "))

    walk(".", "")
    return "\n".join(lines)


def render_markdown(snapshot: dict[str, Any]) -> str:
    tree_text = build_tree_text(snapshot)
    data_json = json.dumps({"nodes": snapshot["nodes"]}, ensure_ascii=False, indent=2)
    return (
        "---\n"
        f"last_updated: {snapshot['last_updated']}\n"
        "---\n\n"
        "# TREE\n\n"
        "## TREE_TEXT\n"
        "```text\n"
        f"{tree_text}\n"
        "```\n\n"
        "## DATA\n"
        "```yaml\n"
        f"{data_json}\n"
        "```\n"
    )


def sync_tree() -> dict[str, Any]:
    snapshot = build_snapshot()
    TREE_MD_PATH.write_text(render_markdown(snapshot), encoding="utf-8")
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync TREE.md from filesystem")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("sync", help="Write TREE.md and tree_state.json")
    subparsers.add_parser("print-json", help="Print current snapshot")
    args = parser.parse_args()

    if args.command == "sync":
        snap = sync_tree()
        print(json.dumps({"status": "ok", "last_updated": snap["last_updated"], "node_count": len(snap["nodes"])}, ensure_ascii=False))
        return 0
    if args.command == "print-json":
        print(json.dumps(build_snapshot(), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
