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
SECTION_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SECTION_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*-\s*([^:：]+?)\s*[:：]\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s{2,}-\s*(.+)$")
TIME_FMT = "%Y-%m-%d-%H-%M"

MILESTONE_FIELDS = [
    "id",
    "title",
    "prerequisites",
    "postnodes",
    "why",
    "what",
    "how",
    "verify",
    "status",
    "notes",
    "updated_at",
]
MILESTONE_LIST_FIELDS = {"prerequisites", "postnodes", "why", "what", "how", "verify", "notes"}
CHANGE_FIELDS = ["version", "date", "reason", "action", "observation", "impacted_files", "notes", "suggestions"]
CHANGE_LIST_FIELDS = {"reason", "action", "observation", "impacted_files", "notes", "suggestions"}

MILESTONE_TEMPLATE_MD = """## TEMPLATE
### MS-TYPE-NUM
- id: MS-TYPE-NUM
- title: 里程碑标题
- prerequisites: []
- postnodes: []
- why:
  - 为什么要做1
  - 为什么要做2
- what:
  - 要做什么1
  - 要做什么2
- how:
  - 如何执行1
  - 如何执行2
- verify:
  - 如何验证1
  - 如何验证2
- status: unfinished
- notes:
  - 补充说明1
  - 补充说明2
- updated_at: YYYY-MM-DD-HH-MM"""

CHANGE_TEMPLATE_MD = """## TEMPLATE
### 0.0.1
- version: 0.0.1
- date: YYYY-MM-DD-HH-MM
- reason:
  - 变更原因1
  - 变更原因2
- action:
  - 执行动作1
  - 执行动作2
- observation:
  - 结果观察1
  - 结果观察2
- impacted_files:
  - path/to/file1
  - path/to/file2
- notes:
  - 备注1
- suggestions:
  - 建议1"""


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
        if re.search(r"^\s*-\s*positions\s*[:：]\s*\[\s*\]\s*$", layout_text, re.MULTILINE):
            return {}
        return {}
    positions: dict[str, dict[str, float]] = {}
    for rec in records:
        rec_id = str(rec.get("id") or rec.get("__title") or "").strip()
        if not rec_id:
            continue
        try:
            x = float(str(rec.get("x", "")).strip())
            y = float(str(rec.get("y", "")).strip())
        except ValueError:
            continue
        positions[rec_id] = {"x": x, "y": y}
    return positions


def parse_milestone_payload(text: str) -> dict[str, Any]:
    data_text = extract_section(text, "DATA")
    records = parse_markdown_records(data_text)
    milestones: list[dict[str, Any]] = []
    for rec in records:
        node_id = str(rec.get("id") or rec.get("__title") or "").strip()
        if not node_id:
            continue
        milestone: dict[str, Any] = {
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
        if not milestone["title"]:
            milestone["title"] = node_id
        milestones.append(milestone)
    layout_text = extract_section(text, "LAYOUT")
    return {"milestones": milestones, "layout": {"positions": parse_layout_positions(layout_text)}}


def parse_change_payload(text: str) -> dict[str, Any]:
    data_text = extract_section(text, "DATA")
    records = parse_markdown_records(data_text)
    changes: list[dict[str, Any]] = []
    for rec in records:
        version = str(rec.get("version") or rec.get("__title") or "").strip()
        if not version:
            continue
        change: dict[str, Any] = {
            "version": version,
            "date": str(rec.get("date", "")).strip(),
            "reason": normalize_list(rec.get("reason")),
            "action": normalize_list(rec.get("action")),
            "observation": normalize_list(rec.get("observation")),
            "impacted_files": normalize_list(rec.get("impacted_files")),
            "notes": normalize_list(rec.get("notes")),
            "suggestions": normalize_list(rec.get("suggestions")),
        }
        changes.append(change)
    return {"changes": changes}


def parse_json_data_payload(text: str) -> dict[str, Any]:
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


def parse_data_payload(text: str, doc_name: str) -> dict[str, Any]:
    if doc_name == "MILESTONE.md":
        payload = parse_milestone_payload(text)
        if payload.get("milestones"):
            return payload
    if doc_name == "CHANGE.md":
        payload = parse_change_payload(text)
        if payload.get("changes"):
            return payload
    return parse_json_data_payload(text)


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
                str(item.get("title", "")).strip() or f"里程碑-{node_id}",
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
                f"版本 {version}",
                "done",
                item,
                subtitle=f"时间 {date_value or '未填写'}",
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


def render_list_field(key: str, value: Any) -> list[str]:
    items = normalize_list(value)
    if not items:
        return [f"- {key}: []"]
    lines = [f"- {key}:"]
    for item in items:
        lines.append(f"  - {item}")
    return lines


def render_scalar_field(key: str, value: Any) -> str:
    return f"- {key}: {str(value or '').strip()}"


def render_markdown_records(records: list[dict[str, Any]], fields: list[str], list_fields: set[str], title_field: str) -> str:
    if not records:
        return ""
    lines: list[str] = []
    for idx, record in enumerate(records):
        title = str(record.get(title_field) or record.get("__title") or f"ITEM-{idx+1}").strip()
        lines.append(f"### {title}")
        for field_name in fields:
            value = record.get(field_name, [] if field_name in list_fields else "")
            if field_name in list_fields:
                lines.extend(render_list_field(field_name, value))
            else:
                lines.append(render_scalar_field(field_name, value))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_layout_positions(payload: dict[str, Any]) -> str:
    layout = payload.get("layout")
    if not isinstance(layout, dict):
        return "- positions: []"
    raw = layout.get("positions")
    if not isinstance(raw, dict) or not raw:
        return "- positions: []"
    lines: list[str] = []
    for node_id in sorted(raw.keys()):
        pos = raw.get(node_id)
        if not isinstance(pos, dict):
            continue
        try:
            x = float(pos.get("x"))
            y = float(pos.get("y"))
        except (TypeError, ValueError):
            continue
        lines.append(f"### {node_id}")
        lines.append(f"- id: {node_id}")
        lines.append(f"- x: {x}")
        lines.append(f"- y: {y}")
        lines.append("")
    if not lines:
        return "- positions: []"
    return "\n".join(lines).rstrip()


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
    if name == "MILESTONE.md":
        milestones = payload.get("milestones")
        records = milestones if isinstance(milestones, list) else []
        return (
            "---\n"
            f"last_updated: {last_updated}\n"
            "---\n\n"
            "# MILESTONE\n\n"
            f"{MILESTONE_TEMPLATE_MD}\n\n"
            "## DATA\n"
            f"{render_markdown_records(records, MILESTONE_FIELDS, MILESTONE_LIST_FIELDS, 'id')}\n\n"
            "## LAYOUT\n"
            f"{render_layout_positions(payload)}\n"
        )
    if name == "CHANGE.md":
        changes = payload.get("changes")
        records = changes if isinstance(changes, list) else []
        return (
            "---\n"
            f"last_updated: {last_updated}\n"
            "---\n\n"
            "# CHANGE\n\n"
            f"{CHANGE_TEMPLATE_MD}\n\n"
            "## DATA\n"
            f"{render_markdown_records(records, CHANGE_FIELDS, CHANGE_LIST_FIELDS, 'version')}\n"
        )
    title = name
    return (
        "---\n"
        f"last_updated: {last_updated}\n"
        "---\n\n"
        f"# {title}\n\n"
    )


def load_document(path: Path) -> dict[str, Any]:
    raw = normalize_text(path.read_text(encoding="utf-8"))
    frontmatter = parse_frontmatter(raw)
    payload = parse_data_payload(raw, path.name)
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
