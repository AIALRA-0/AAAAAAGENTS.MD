from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import markdown as markdown_lib  # type: ignore
except Exception:  # pragma: no cover
    markdown_lib = None

DOC_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
DATA_BLOCK_RE = re.compile(r"##\s*DATA.*?```(?:yaml|yml|json)\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
TREE_TEXT_RE = re.compile(r"##\s*TREE_TEXT.*?```text\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
TIME_FMT = "%Y-%m-%d-%H-%M"


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def now_stamp() -> str:
    return datetime.now().strftime(TIME_FMT)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = DOC_FRONTMATTER_RE.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def parse_data_payload(text: str) -> dict[str, Any]:
    match = DATA_BLOCK_RE.search(text)
    if not match:
        return {}
    block = match.group(1).strip()
    try:
        payload = json.loads(block)
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def parse_tree_text(text: str) -> str:
    match = TREE_TEXT_RE.search(text)
    if not match:
        return ""
    return normalize_text(match.group(1).strip())


def markdown_to_html(text: str) -> str:
    if markdown_lib is None:
        return f"<pre>{html.escape(text)}</pre>"
    return markdown_lib.markdown(text, extensions=["fenced_code", "tables", "nl2br"], output_format="html5")


def strip_frontmatter(text: str) -> str:
    match = DOC_FRONTMATTER_RE.search(text)
    if not match:
        return text
    return text[match.end() :].lstrip("\n")


def safe_graph_id(value: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z_]+", "_", value.strip())
    if not cleaned:
        cleaned = "node"
    if cleaned[0].isdigit():
        cleaned = f"n_{cleaned}"
    return cleaned


def status_style(status: str) -> dict[str, str]:
    mapping = {
        "done": {"fill": "#1d4ed8", "text": "#f8fbff", "border": "#1e3a8a"},
        "unfinished": {"fill": "#dbeafe", "text": "#0f172a", "border": "#3b82f6"},
        "archived": {"fill": "#f1f5f9", "text": "#475569", "border": "#94a3b8"},
        "deleted": {"fill": "#f1f5f9", "text": "#475569", "border": "#94a3b8"},
    }
    return mapping.get(status, {"fill": "#dbeafe", "text": "#0f172a", "border": "#3b82f6"})


def first_line(value: Any, fallback: str = "") -> str:
    if not isinstance(value, list):
        return fallback
    for item in value:
        text = str(item).strip()
        if text:
            return text
    return fallback


def trim_line(value: str, limit: int = 26) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def node_size_for_lines(lines: list[str]) -> tuple[float, float, float]:
    line_count = max(1, len(lines))
    max_len = max((len(line) for line in lines), default=14)
    width = float(min(360, max(260, max_len * 8 + 54)))
    height = float(min(220, max(124, line_count * 22 + 26)))
    font_size = float(min(15, max(12, 15 - max_len // 18)))
    return width, height, font_size


def build_graph_node(
    node_id: str,
    title: str,
    status: str,
    raw: dict[str, Any],
    *,
    subtitle: str = "",
    show_id: bool = True,
) -> dict[str, Any]:
    style = status_style(status)
    lines: list[str] = []
    safe_node_id = trim_line(node_id, 28)
    safe_title = trim_line(title or node_id, 34)
    if show_id:
        lines.append(safe_node_id)
    if not lines or safe_title != lines[-1]:
        lines.append(safe_title)
    if subtitle.strip():
        lines.append(trim_line(subtitle, 34))
    width, height, font_size = node_size_for_lines(lines)
    return {
        "data": {
            "id": node_id,
            "label": "\n".join(lines),
            "status": status,
            "fill": style["fill"],
            "text": style["text"],
            "border": style["border"],
            "width": width,
            "height": height,
            "font_size": font_size,
            "raw": raw,
        }
    }


def build_milestone_graph(payload: dict[str, Any]) -> dict[str, Any]:
    milestones = payload.get("milestones", [])
    if not isinstance(milestones, list):
        milestones = []
    by_id: dict[str, dict[str, Any]] = {}
    nodes: list[dict[str, Any]] = []
    for item in milestones:
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("id", "")).strip()
        if not node_id:
            continue
        by_id[node_id] = item
        status = str(item.get("status", "unfinished"))
        nodes.append(
            build_graph_node(
                node_id,
                str(item.get("title", "")).strip() or f"milestone-{node_id}",
                status,
                item,
            )
        )

    edges: list[dict[str, Any]] = []
    for item in milestones:
        if not isinstance(item, dict):
            continue
        target_id = str(item.get("id", "")).strip()
        if not target_id:
            continue
        prerequisites = item.get("prerequisites", [])
        if not isinstance(prerequisites, list):
            continue
        for pre in prerequisites:
            pre_id = str(pre).strip()
            if not pre_id or pre_id not in by_id:
                continue
            pre_status = str(by_id[pre_id].get("status", "unfinished"))
            required = pre_status not in {"archived", "deleted"}
            edges.append(
                {
                    "data": {
                        "id": f"e_{safe_graph_id(pre_id)}_{safe_graph_id(target_id)}",
                        "source": pre_id,
                        "target": target_id,
                        "required": required,
                        "source_status": pre_status,
                    }
                }
            )

    return {"type": "milestone_flow", "nodes": nodes, "edges": edges}


def build_change_graph(payload: dict[str, Any]) -> dict[str, Any]:
    changes = payload.get("changes", [])
    if not isinstance(changes, list):
        changes = []

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    ordered_versions: list[str] = []
    for idx, item in enumerate(changes):
        if not isinstance(item, dict):
            continue
        version = str(item.get("version", f"0.0.{idx+1}")).strip()
        if not version:
            continue
        date_value = str(item.get("date", "")).strip()
        nodes.append(
            build_graph_node(
                version,
                f"version {version}",
                "done",
                item,
                subtitle=f"Time {date_value or 'Not filled in'}",
                show_id=False,
            )
        )
        ordered_versions.append(version)

    for idx in range(len(ordered_versions) - 1):
        source = ordered_versions[idx]
        target = ordered_versions[idx + 1]
        edges.append(
            {
                "data": {
                    "id": f"e_{safe_graph_id(source)}_{safe_graph_id(target)}",
                    "source": source,
                    "target": target,
                    "required": True,
                    "source_status": "done",
                }
            }
        )

    return {"type": "change_timeline", "nodes": nodes, "edges": edges}


def build_tree_explorer(payload: dict[str, Any], include_deleted: bool = False) -> dict[str, Any]:
    raw_nodes = payload.get("nodes", [])
    if not isinstance(raw_nodes, list):
        raw_nodes = []
    filtered: list[dict[str, Any]] = []
    for item in raw_nodes:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "active"))
        if not include_deleted and status == "deleted":
            continue
        filtered.append(item)

    by_path: dict[str, dict[str, Any]] = {}
    children_by_parent: dict[str, list[str]] = {}
    for item in filtered:
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        by_path[path] = item
        parent = str(item.get("parent", "")).strip()
        children_by_parent.setdefault(parent, []).append(path)

    def order_key(path_value: str) -> tuple[int, str]:
        node = by_path[path_value]
        is_dir = str(node.get("type", "file")) == "dir"
        return (0 if is_dir else 1, str(node.get("name", path_value)).lower())

    for parent_key in list(children_by_parent.keys()):
        children_by_parent[parent_key] = sorted(children_by_parent[parent_key], key=order_key)

    def build_node(path_value: str) -> dict[str, Any]:
        node = by_path[path_value]
        children = [build_node(child_path) for child_path in children_by_parent.get(path_value, []) if child_path in by_path]
        return {
            "path": str(node.get("path", "")),
            "name": str(node.get("name", "")),
            "parent": str(node.get("parent", "")),
            "type": str(node.get("type", "file")),
            "status": str(node.get("status", "active")),
            "last_modified": str(node.get("last_modified", "")),
            "editable": bool(node.get("editable", False)),
            "note": str(node.get("note", "")),
            "children": children,
        }

    root_path = "." if "." in by_path else ""
    if root_path:
        tree = build_node(root_path)
    else:
        roots = children_by_parent.get("", [])
        tree = {
            "path": "",
            "name": "root",
            "parent": "",
            "type": "dir",
            "status": "active",
            "last_modified": "",
            "editable": False,
            "note": "",
            "children": [build_node(path_value) for path_value in roots if path_value in by_path],
        }
    return {"type": "tree_explorer", "count": len(by_path), "root": tree}


def build_tree_text_from_payload(payload: dict[str, Any]) -> str:
    nodes = payload.get("nodes", [])
    if not isinstance(nodes, list):
        return "."
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if str(node.get("status")) != "active":
            continue
        by_parent.setdefault(str(node.get("parent", "")), []).append(node)
    for children in by_parent.values():
        children.sort(key=lambda n: (0 if n.get("type") == "dir" else 1, str(n.get("name", "")).lower()))
    lines = ["."]

    def walk(parent: str, prefix: str) -> None:
        children = by_parent.get(parent, [])
        for idx, child in enumerate(children):
            last = idx == len(children) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + str(child.get("name", "")))
            if child.get("type") == "dir":
                walk(str(child.get("path", "")), prefix + ("    " if last else "│   "))

    walk(".", "")
    return "\n".join(lines)


def build_graph(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    if name == "MILESTONE.md":
        return build_milestone_graph(payload)
    if name == "CHANGE.md":
        return build_change_graph(payload)
    return {"type": "none", "nodes": [], "edges": []}


def serialize_document(name: str, frontmatter: dict[str, str], payload: dict[str, Any], tree_text: str = "") -> str:
    last_updated = str(frontmatter.get("last_updated", "")).strip()
    if not last_updated:
        last_updated = now_stamp()
    if name == "TREE.md":
        if not tree_text:
            tree_text = build_tree_text_from_payload(payload)
        return (
            "---\n"
            f"last_updated: {last_updated}\n"
            "---\n\n"
            "# TREE\n\n"
            "## TREE_TEXT\n"
            "```text\n"
            f"{tree_text}\n"
            "```\n\n"
            "## DATA\n"
            "```yaml\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
            "```\n"
        )
    title = "MILESTONE" if name == "MILESTONE.md" else "CHANGE" if name == "CHANGE.md" else name
    return (
        "---\n"
        f"last_updated: {last_updated}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## DATA\n"
        "```yaml\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def load_document(path: Path) -> dict[str, Any]:
    raw = normalize_text(path.read_text(encoding="utf-8"))
    frontmatter = parse_frontmatter(raw)
    payload = parse_data_payload(raw)
    tree_text = parse_tree_text(raw) if path.name == "TREE.md" else ""
    html_source = strip_frontmatter(raw)
    html_value = markdown_to_html(html_source)
    return {
        "raw": raw,
        "frontmatter": frontmatter,
        "payload": payload,
        "tree_text": tree_text,
        "rendered_html": html_value,
    }
