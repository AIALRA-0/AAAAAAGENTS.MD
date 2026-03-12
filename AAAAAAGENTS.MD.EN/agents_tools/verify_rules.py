from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
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
EDITABLE_FILES = ["MILESTONE.md", "CHANGE.md", "TREE.md"]
MILESTONE_STATUSES = {"archived", "unfinished", "done", "deleted"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DOC_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
DATA_BLOCK_RE = re.compile(r"##\s*DATA.*?```(?:yaml|yml|json)\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
TREE_TEXT_RE = re.compile(r"##\s*TREE_TEXT.*?```text\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
SECTION_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SECTION_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*-\s*([^:：]+?)\s*[:：]\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s{2,}-\s*(.+)$")
TIME_FMT = "%Y-%m-%d-%H-%M"
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")

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
- title: Milestone title
- prerequisites: []
- postnodes: []
- why:
  - Why item 1
  - Why item 2
- what:
  - What item 1
  - What item 2
- how:
  - How item 1
  - How item 2
- verify:
  - Verify item 1
  - Verify item 2
- status: unfinished
- notes:
  - Note item 1
  - Note item 2
- updated_at: YYYY-MM-DD-HH-MM"""

CHANGE_TEMPLATE_MD = """## TEMPLATE
### 0.0.1
- version: 0.0.1
- date: YYYY-MM-DD-HH-MM
- reason:
  - Reason 1
  - Reason 2
- action:
  - Action 1
  - Action 2
- observation:
  - Observation 1
  - Observation 2
- impacted_files:
  - path/to/file1
  - path/to/file2
- notes:
  - Note 1
- suggestions:
  - Suggestion 1"""

TREE_NOTE_FORBIDDEN_HINTS = [
    "File node",
    "Directory node",
    "Last modified time",
    "Last scan time",
    "Status normal",
    "read only",
    "editable",
]

PLACEHOLDER_TOKENS = {
    "",
    "-",
    "--",
    "...",
    "tbd",
    "todo",
    "xxx",
    "to be added",
    "to be filled",
    "example",
    "sample",
    "n/a",
    "na",
    "none",
    "null",
}

BACKGROUND_REQUIRED_FIELDS: dict[str, list[str]] = {
    "Usage Boundary": ["Description", "Non-exclusivity statement"],
    "Project Background": [
        "Project name",
        "Project summary - Briefly describe what this project is",
        "Core problem 1",
        "Core reason 1",
        "Current state 1",
        "Core goal 1",
        "Core boundary 1",
        "Core constraint 1",
        "Core change 1",
    ],
    "Tech Stack": [
        "Tech stack 1 name",
        "Type - Category of this technology in the system",
        "Summary - Briefly explain what this technology is",
        "Purpose 1",
        "Why selected 1",
        "Usage note 1",
    ],
    "Environment Information": [
        "Environment item 1 name",
        "Type - Nature/category of this environment",
        "Summary - Explain what this environment is",
        "Version - Version/spec information",
        "Usage note 1",
    ],
    "ICP Ideal Customer Profile": [
        "User segment - The customer type most suitable for this product",
        "Pain source 1",
        "Reach channel 1",
        "Trial willingness 1",
        "End user 1",
        "Decision maker 1",
        "Payer 1",
        "Driver 1",
        "Blocker 1",
        "Purchase path 1",
    ],
    "Alternatives": [
        "Alternative 1 name",
        "Type - Category of this alternative",
        "Summary - Explain what this alternative is",
        "Market research - Current usage and market share of this alternative",
        "Core problem solved 1",
        "Usage scenario 1",
        "Core advantage 1",
        "Core limitation 1",
    ],
    "Differentiation": [
        "Differentiation 1 name",
        "Type - What category this differentiation belongs to",
        "Summary - Core description of this differentiation",
        "Source 1",
        "User perception - Whether users can directly perceive this differentiation",
        "User driver - How this differentiation drives user switching or continued usage",
        "Copy difficulty - Difficulty estimate for competitors to copy this differentiation",
    ],
    "Feasibility": [
        "Feasibility item 1 name",
        "Type - Category of this feasibility evaluation",
        "Summary - Core objective of this feasibility evaluation",
        "Technical feasibility - Whether it can be implemented under current technical conditions",
        "Data availability - Whether required data can be obtained",
        "Implementation complexity - Difficulty and timeline estimate",
        "Implementation priority - Recommended priority",
        "Dependency risk 1",
        "Compliance risk 1",
        "Resource requirement 1",
        "Confidence level - Confidence and evidence source for current feasibility judgement",
    ],
    "Business": [
        "Business item 1 name",
        "Willing users - User segments most willing to try and continue using",
        "Paying entity - Budget decision and payment owner",
        "Customer value - Expected value range per customer",
        "Acquisition cost - Total cost to acquire one valid customer",
        "Retention capability - Continued usage and renewal likelihood",
        "Business model - Current planned commercialization model",
        "Confidence level - Confidence and evidence source for current business judgement",
    ],
}

RESOURCE_REQUIRED_FIELDS: dict[str, list[str]] = {
    "Usage Boundary": ["Description", "Non-exclusivity statement"],
    "Local Resources": [
        "Local resource 1 name",
        "Type - Category of this resource",
        "Summary - Briefly describe what this resource is",
        "Version - Briefly describe the version of this resource",
        "Path 1 title",
        "Note 1",
    ],
    "External Resources": [
        "External resource 1 name",
        "Type - Category of this resource",
        "Summary - Briefly describe what this resource is",
        "Version - Briefly describe the version of this resource",
        "URL 1 title",
        "Note 1",
    ],
    "Access Credentials": [
        "Access credential 1 name",
        "Type - Credential type",
        "Summary - Briefly describe the purpose of this credential",
        "Storage location - Where this credential is stored",
        "Permission scope - Accessible scope of this credential",
        "Rotation policy - Credential update/rotation rules",
        "Owner - Responsible maintainer of this credential",
    ],
}

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


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_fix(self, message: str) -> None:
        self.fixes.append(message)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "status": "ok" if not self.errors else "failed",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "fix_count": len(self.fixes),
            "errors": self.errors,
            "warnings": self.warnings,
            "fixes": self.fixes,
        }
        if self.details:
            payload["details"] = self.details
        return payload


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def now_stamp() -> str:
    return datetime.now().strftime(TIME_FMT)


def normalize_stamp(value: Any) -> str:
    raw = str(value or "").strip()
    if TIME_RE.fullmatch(raw):
        return raw
    if raw:
        candidates = [raw, raw.replace("T", " ")]
        for cand in candidates:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
                try:
                    return datetime.strptime(cand, fmt).strftime(TIME_FMT)
                except ValueError:
                    continue
    return now_stamp()


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def to_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = DOC_FRONTMATTER_RE.search(text)
    if not match:
        raise ValueError("missing frontmatter header")
    raw = match.group(1).strip()
    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line format error: {line}")
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip()
    body = text[match.end() :]
    return parsed, body


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


def parse_milestone_markdown_payload(text: str) -> dict[str, Any]:
    records = parse_markdown_records(extract_section(text, "DATA"))
    milestones: list[dict[str, Any]] = []
    for rec in records:
        node_id = str(rec.get("id") or rec.get("__title") or "").strip()
        if not node_id:
            continue
        milestone = {
            "id": node_id,
            "title": str(rec.get("title", "")).strip() or node_id,
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
        milestones.append(milestone)
    if not milestones:
        return {}
    return {"milestones": milestones, "layout": {"positions": parse_layout_positions(extract_section(text, "LAYOUT"))}}


def parse_change_markdown_payload(text: str) -> dict[str, Any]:
    records = parse_markdown_records(extract_section(text, "DATA"))
    changes: list[dict[str, Any]] = []
    for rec in records:
        version = str(rec.get("version") or rec.get("__title") or "").strip()
        if not version:
            continue
        change = {
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
    if not changes:
        return {}
    return {"changes": changes}


def parse_json_data_payload(text: str) -> dict[str, Any]:
    match = DATA_BLOCK_RE.search(text)
    if not match:
        raise ValueError("Missing DATA block")
    block = match.group(1).strip()
    try:
        payload = json.loads(block)
    except json.JSONDecodeError as exc:
        raise ValueError(f"DATA content is not legal JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("DATA top level must be an object")
    return payload


def parse_data_payload(text: str, doc_name: str) -> dict[str, Any]:
    if doc_name == "MILESTONE.md":
        payload = parse_milestone_markdown_payload(text)
        if payload:
            return payload
    if doc_name == "CHANGE.md":
        payload = parse_change_markdown_payload(text)
        if payload:
            return payload
    return parse_json_data_payload(text)


def extract_tree_text(text: str) -> str:
    match = TREE_TEXT_RE.search(text)
    if not match:
        raise ValueError("Missing TREE_TEXT code block")
    return normalize_text(match.group(1).strip())


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
        for field in fields:
            value = record.get(field, [] if field in list_fields else "")
            if field in list_fields:
                lines.extend(render_list_field(field, value))
            else:
                lines.append(render_scalar_field(field, value))
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


def render_doc(path_name: str, last_updated: str, payload: dict[str, Any]) -> str:
    if path_name == "MILESTONE.md":
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
    if path_name == "CHANGE.md":
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
    raise ValueError(f"render_doc does not support document: {path_name}")


def load_tree_module():
    tree_path = ROOT / "agents_tools" / "tree.py"
    spec = importlib.util.spec_from_file_location("agents_tree_tool", tree_path)
    if not spec or not spec.loader:
        raise RuntimeError("Unable to load agents_tools/tree.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_ignored_hash_path(rel: str) -> bool:
    if rel in IGNORED_HASH_FILES:
        return True
    if any(rel.startswith(prefix) for prefix in IGNORED_HASH_PREFIXES):
        return True
    parts = rel.split("/")
    return any(part in IGNORED_HASH_DIRS for part in parts)


def list_hashable_files() -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(ROOT):
        root_path = Path(root)
        dirs[:] = sorted([d for d in dirs if d not in IGNORED_HASH_DIRS], key=str.lower)
        names = sorted(names, key=str.lower)
        for name in names:
            file_path = root_path / name
            rel = file_path.relative_to(ROOT).as_posix()
            if is_ignored_hash_path(rel):
                continue
            files.append(file_path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix().lower())


def compute_file_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for file_path in list_hashable_files():
        rel = to_rel(file_path)
        hashes[rel] = sha256_text(read_text(file_path))
    return hashes


def compute_changed_files(previous: dict[str, str], current: dict[str, str]) -> list[str]:
    changed: list[str] = []
    all_paths = set(previous) | set(current)
    for rel in sorted(all_paths):
        if previous.get(rel) != current.get(rel):
            changed.append(rel)
    return changed


def ensure_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def ensure_minute_timestamp(value: str) -> bool:
    return TIME_RE.fullmatch(str(value or "").strip()) is not None


def parse_semver(value: str) -> tuple[int, int, int] | None:
    if not SEMVER_RE.fullmatch(value):
        return None
    major, minor, patch = value.split(".")
    return (int(major), int(minor), int(patch))


def load_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return data
    return None


def progress_checks_disabled(state: dict[str, Any] | None) -> bool:
    if not isinstance(state, dict):
        return False
    return bool(state.get("skip_progress_checks_once"))


def load_docs(report: Report) -> dict[str, dict[str, Any]]:
    docs: dict[str, dict[str, Any]] = {}
    for rel in EDITABLE_FILES:
        path = ROOT / rel
        if not path.exists():
            report.add_error(f"Missing required file: {rel}")
            continue
        text = read_text(path)
        try:
            frontmatter, body = parse_frontmatter(text)
            payload = parse_data_payload(text, rel)
        except ValueError as exc:
            report.add_error(f"{rel}: {exc}")
            continue
        docs[rel] = {"path": path, "text": text, "frontmatter": frontmatter, "body": body, "payload": payload}
    return docs


def normalize_value(value: str) -> str:
    return re.sub(r"\s+", "", str(value).strip()).lower()


def is_placeholder_or_empty(value: Any) -> bool:
    text = str(value or "").strip()
    normalized = normalize_value(text)
    if not normalized:
        return True
    if normalized in PLACEHOLDER_TOKENS:
        return True
    if text.startswith("<") and text.endswith(">"):
        return True
    if re.fullmatch(r"[\-._,:;|/\\`'\"*+]+", text):
        return True
    return False


def extract_section_fields(text: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_section = ""
    for raw_line in normalize_text(text).splitlines():
        line = raw_line.rstrip()
        section_match = re.match(r"^\s*##\s+(.+?)\s*$", line)
        if section_match:
            current_section = section_match.group(1).strip()
            sections.setdefault(current_section, {})
            continue
        field_match = re.match(r"^\s*-\s*([^:：]+?)\s*[:：]\s*(.*)$", line)
        if field_match and current_section:
            field = field_match.group(1).strip()
            value = field_match.group(2).strip()
            sections[current_section][field] = value
    return sections


def validate_template_fields(
    doc_name: str,
    text: str,
    required: dict[str, list[str]],
    report: Report,
    require_non_exclusive_keywords: list[str],
) -> None:
    sections = extract_section_fields(text)
    for section, fields in required.items():
        if section not in sections:
            report.add_error(f"{doc_name}[section={section}][field=*]: missing required section")
            continue
        for field_name in fields:
            if field_name not in sections[section]:
                report.add_error(f"{doc_name}[section={section}][field={field_name}]: missing required field")
                continue
            value = sections[section][field_name]
            if is_placeholder_or_empty(value):
                report.add_error(f"{doc_name}[section={section}][field={field_name}]: empty or placeholder value")

    non_exclusive_value = sections.get("Usage boundary", {}).get("Non-exclusivity statement", "")
    if not non_exclusive_value:
        return
    lower_value = non_exclusive_value.lower()
    if not all(keyword in lower_value for keyword in require_non_exclusive_keywords):
        report.add_error(
            f"{doc_name}[section=Usage boundary][field=Non-exclusivity statement]: "
            "must clearly state that the document does not represent all available resources"
        )


def validate_initial_milestone_ready(payload: dict[str, Any], report: Report) -> None:
    milestones = payload.get("milestones")
    if not isinstance(milestones, list) or len(milestones) == 0:
        report.add_error("MILESTONE.md[section=DATA][field=milestones]: at least one valid initial node is required")
        return
    first = next((node for node in milestones if isinstance(node, dict)), None)
    if not isinstance(first, dict):
        report.add_error("MILESTONE.md[section=DATA][field=milestones]: invalid initial node structure")
        return

    scalar_fields = ["id", "title", "status", "updated_at"]
    for field_name in scalar_fields:
        if is_placeholder_or_empty(first.get(field_name)):
            report.add_error(f"MILESTONE.md[section=DATA][field={field_name}]: initial node field is not filled")

    list_fields = ["why", "what", "how", "verify"]
    for field_name in list_fields:
        value = first.get(field_name)
        if not isinstance(value, list) or len(value) == 0:
            report.add_error(f"MILESTONE.md[section=DATA][field={field_name}]: initial node field must be a non-empty list")
            continue
        if any(is_placeholder_or_empty(item) for item in value):
            report.add_error(f"MILESTONE.md[section=DATA][field={field_name}]: initial node list has empty or placeholder entries")


def validate_prestart_readiness(milestone_payload: dict[str, Any], report: Report) -> None:
    background_path = ROOT / "BACKGROUND.md"
    resource_path = ROOT / "RESOURCE.md"
    if not background_path.exists():
        report.add_error("BACKGROUND.md[section=*][field=*]: file missing, prestart readiness failed")
    else:
        validate_template_fields(
            "BACKGROUND.md",
            read_text(background_path),
            BACKGROUND_REQUIRED_FIELDS,
            report,
            require_non_exclusive_keywords=["not", "represent"],
        )

    if not resource_path.exists():
        report.add_error("RESOURCE.md[section=*][field=*]: file missing, prestart readiness failed")
    else:
        validate_template_fields(
            "RESOURCE.md",
            read_text(resource_path),
            RESOURCE_REQUIRED_FIELDS,
            report,
            require_non_exclusive_keywords=["not", "represent"],
        )

    validate_initial_milestone_ready(milestone_payload, report)


def update_change_impacted_files(
    change_payload: dict[str, Any],
    previous_hashes: dict[str, str],
    current_hashes: dict[str, str],
    report: Report,
) -> bool:
    changes = change_payload.get("changes")
    if not isinstance(changes, list) or not changes:
        report.add_error("CHANGE.md: changes must be a non-empty list")
        return False
    latest = changes[-1]
    if not isinstance(latest, dict):
        report.add_error("CHANGE.md: The latest record must be an object")
        return False
    changed_files = compute_changed_files(previous_hashes, current_hashes)
    if latest.get("impacted_files") != changed_files:
        latest["impacted_files"] = changed_files
        report.add_fix("CHANGE.md has automatically updated the latest recorded impacted_files")
        return True
    return False


def migrate_change_dates(change_payload: dict[str, Any], report: Report) -> bool:
    changes = change_payload.get("changes")
    if not isinstance(changes, list):
        return False
    changed = False
    for idx, entry in enumerate(changes):
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("date", "")).strip()
        if not raw:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            entry["date"] = f"{raw}-00-00"
            changed = True
            report.add_fix(f"CHANGE[{idx}] date has been automatically migrated to minute format")
            continue
        normalized = normalize_stamp(raw)
        if normalized != raw:
            entry["date"] = normalized
            changed = True
            report.add_fix(f"CHANGE[{idx}] date has been normalized to {normalized}")
    return changed


def update_milestone_updated_at(
    milestone_payload: dict[str, Any],
    previous_statuses: dict[str, str] | None,
    now_value: str,
) -> bool:
    if previous_statuses is None:
        return False
    milestones = milestone_payload.get("milestones")
    if not isinstance(milestones, list):
        return False
    changed = []
    for node in milestones:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id", ""))
        if not node_id or node_id not in previous_statuses:
            continue
        if str(node.get("status")) != previous_statuses[node_id]:
            changed.append(node)
    if len(changed) != 1:
        return False
    one = changed[0]
    node_id = str(one.get("id"))
    if previous_statuses.get(node_id) == "unfinished" and str(one.get("status")) == "done":
        if str(one.get("updated_at", "")) != now_value:
            one["updated_at"] = now_value
            return True
    return False


def ensure_frontmatter_for_editable(name: str, frontmatter: dict[str, str], report: Report) -> None:
    keys = set(frontmatter.keys())
    if keys != {"last_updated"}:
        report.add_error(f"{name}: frontmatter can only contain last_updated")
        return
    if not ensure_minute_timestamp(str(frontmatter.get("last_updated", ""))):
        report.add_error(f"{name}: last_updated must be YYYY-MM-DD-HH-MM")


def milestone_signature(node: dict[str, Any]) -> dict[str, Any]:
    keep = {
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
    return keep


def validate_milestone(
    payload: dict[str, Any],
    baseline: dict[str, Any] | None,
    state: dict[str, Any] | None,
    report: Report,
) -> None:
    milestones = payload.get("milestones")
    if not isinstance(milestones, list) or not milestones:
        report.add_error("MILESTONE.md: milestones must be a non-empty list")
        return

    required = {
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
    }
    seen_ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for idx, node in enumerate(milestones):
        ctx = f"MILESTONE[{idx}]"
        if not isinstance(node, dict):
            report.add_error(f"{ctx}: node must be an object")
            continue
        keys = set(node.keys())
        if keys != required:
            missing = sorted(required - keys)
            extra = sorted(keys - required)
            if missing:
                report.add_error(f"{ctx}: missing field {', '.join(missing)}")
            if extra:
                report.add_error(f"{ctx}: There are extra fields {', '.join(extra)}")
            continue
        node_id = str(node.get("id", "")).strip()
        if not node_id:
            report.add_error(f"{ctx}: id cannot be empty")
            continue
        if node_id in seen_ids:
            report.add_error(f"{ctx}: id duplicate {node_id}")
            continue
        seen_ids.add(node_id)
        by_id[node_id] = node

        if not str(node.get("title", "")).strip():
            report.add_error(f"{ctx}: title cannot be empty")
        if str(node.get("status")) not in MILESTONE_STATUSES:
            report.add_error(f"{ctx}: status illegal {node.get('status')}")
        if not ensure_minute_timestamp(str(node.get("updated_at", ""))):
            report.add_error(f"{ctx}: updated_at must be YYYY-MM-DD-HH-MM")

        for list_key in ["prerequisites", "postnodes", "why", "what", "how", "verify", "notes"]:
            value = node.get(list_key)
            if not isinstance(value, list):
                report.add_error(f"{ctx}: {list_key} must be a list")
                continue
            if list_key in {"why", "what", "how", "verify"} and len(value) == 0:
                report.add_error(f"{ctx}: {list_key} must be a non-empty list")
            if any(not str(item).strip() for item in value):
                report.add_error(f"{ctx}: {list_key} has an empty entry")

    for node_id, node in by_id.items():
        if str(node.get("status")) != "done":
            continue
        prerequisites = node.get("prerequisites", [])
        if not isinstance(prerequisites, list):
            continue
        for pre_id in prerequisites:
            pre = by_id.get(str(pre_id))
            if not pre:
                report.add_error(f"MILESTONE[{node_id}]: The preceding node does not exist {pre_id}")
                continue
            pre_status = str(pre.get("status"))
            if pre_status in {"archived", "deleted"}:
                continue
            if pre_status != "done":
                report.add_error(f"MILESTONE[{node_id}]: The pre-node {pre_id} is not completed")

    baseline_structure = (baseline or {}).get("milestone_structure")
    if isinstance(baseline_structure, dict):
        baseline_ids = baseline_structure.get("ids")
        if isinstance(baseline_ids, list):
            now_ids = [str(node.get("id")) for node in milestones if isinstance(node, dict)]
            if sorted(now_ids) != sorted([str(i) for i in baseline_ids]):
                report.add_error("MILESTONE.md: It is detected that the node is added or deleted, please execute baseline_refresh first")
        baseline_sig = baseline_structure.get("signature_by_id")
        if isinstance(baseline_sig, dict):
            for node in milestones:
                if not isinstance(node, dict):
                    continue
                node_id = str(node.get("id"))
                if node_id in baseline_sig:
                    if milestone_signature(node) != baseline_sig[node_id]:
                        report.add_error(f"MILESTONE[{node_id}]: Non-status field structure change detected")

    if progress_checks_disabled(state):
        report.add_warning("MILESTONE.md: Baseline synchronization has been detected, milestone progress difference verification is skipped this time")
        return

    previous_statuses = None
    if isinstance(state, dict):
        previous_statuses = state.get("milestone_statuses")
    if isinstance(previous_statuses, dict):
        changed: list[tuple[str, str, str]] = []
        for node_id, node in by_id.items():
            prev = previous_statuses.get(node_id)
            if prev is None:
                continue
            now_status = str(node.get("status"))
            if now_status != prev:
                changed.append((node_id, str(prev), now_status))
        report.details["milestone_status_changes"] = [
            {"id": node_id, "from": old_status, "to": new_status}
            for node_id, old_status, new_status in changed
        ]
        if len(changed) != 1:
            if changed:
                preview = ", ".join([f"{node_id}:{old_status}->{new_status}" for node_id, old_status, new_status in changed])
            else:
                preview = "none"
            report.add_error(
                "MILESTONE.md: There must be and can only be 1 node status change; "
                f"Currently detected change [{preview}] at {len(changed)}, expect only one unfinished->done."
                "If this is just a document or interface adjustment, please synchronize the final inspection baseline first."
            )
        else:
            node_id, old_status, new_status = changed[0]
            if not (old_status == "unfinished" and new_status == "done"):
                report.add_error(
                    f"MILESTONE[{node_id}]: Only unfinished->done is allowed, currently {old_status}->{new_status}"
                )
    else:
        report.add_warning("MILESTONE.md: missing finalize_state, state difference verification skipped (boot mode)")


def validate_change(payload: dict[str, Any], state: dict[str, Any] | None, report: Report) -> None:
    changes = payload.get("changes")
    if not isinstance(changes, list) or not changes:
        report.add_error("CHANGE.md: changes must be a non-empty list")
        return
    required = {"version", "date", "reason", "action", "observation", "impacted_files", "notes", "suggestions"}
    versions: list[tuple[int, int, int]] = []
    for idx, entry in enumerate(changes):
        ctx = f"CHANGE[{idx}]"
        if not isinstance(entry, dict):
            report.add_error(f"{ctx}: entry must be an object")
            continue
        keys = set(entry.keys())
        if keys != required:
            missing = sorted(required - keys)
            extra = sorted(keys - required)
            if missing:
                report.add_error(f"{ctx}: missing field {', '.join(missing)}")
            if extra:
                report.add_error(f"{ctx}: There are extra fields {', '.join(extra)}")
            continue
        version = str(entry.get("version", ""))
        parsed_version = parse_semver(version)
        if parsed_version is None:
            report.add_error(f"{ctx}: The version number is illegal {version}")
        else:
            versions.append(parsed_version)
        date_value = str(entry.get("date", "")).strip()
        if not ensure_minute_timestamp(date_value):
            report.add_error(f"{ctx}: Date format error `{date_value}`, should be YYYY-MM-DD-HH-MM")
        for key in ["reason", "action", "observation"]:
            value = entry.get(key)
            if not isinstance(value, list) or len(value) == 0:
                report.add_error(f"{ctx}: {key} must be a non-empty list")
            elif any(not str(item).strip() for item in value):
                report.add_error(f"{ctx}: {key} has an empty entry")
        for key in ["notes", "suggestions", "impacted_files"]:
            value = entry.get(key)
            if not isinstance(value, list):
                report.add_error(f"{ctx}: {key} must be a list")
            elif any(not isinstance(item, str) for item in value):
                report.add_error(f"{ctx}: {key} can only contain strings")

    expected_versions = [(0, 0, i + 1) for i in range(len(changes))]
    if versions and versions != expected_versions:
        report.add_error("CHANGE.md: The version must be continuously incremented by patch starting from 0.0.1")

    if progress_checks_disabled(state):
        report.add_warning("CHANGE.md: Baseline synchronization has been detected, incremental verification of changed entries will be skipped this time")
        return

    prev_entries = None
    if isinstance(state, dict):
        prev_entries = state.get("change_entries")
    if isinstance(prev_entries, list):
        if len(changes) != len(prev_entries) + 1:
            report.add_error("CHANGE.md: You must and can only add one change record")
        else:
            if changes[:-1] != prev_entries:
                report.add_error("CHANGE.md: The historical change record was modified or deleted")
    else:
        report.add_warning("CHANGE.md: finalize_state is missing, historical difference verification (boot mode) skipped")


def validate_tree(text: str, payload: dict[str, Any], state: dict[str, Any] | None, report: Report) -> None:
    nodes = payload.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        report.add_error("TREE.md: nodes must be a non-empty list")
        return
    required = {"path", "name", "parent", "type", "status", "last_modified", "editable", "note"}
    seen_paths: set[str] = set()
    for idx, node in enumerate(nodes):
        ctx = f"TREE[{idx}]"
        if not isinstance(node, dict):
            report.add_error(f"{ctx}: node must be an object")
            continue
        keys = set(node.keys())
        if keys != required:
            missing = sorted(required - keys)
            extra = sorted(keys - required)
            if missing:
                report.add_error(f"{ctx}: missing field {', '.join(missing)}")
            if extra:
                report.add_error(f"{ctx}: There are extra fields {', '.join(extra)}")
            continue
        path = str(node.get("path", "")).strip()
        path_ctx = f"TREE[path={path or '?'}]"
        if not path:
            report.add_error(f"{ctx}: path cannot be empty")
            continue
        if path in seen_paths:
            report.add_error(f"{path_ctx}: path repeated")
        seen_paths.add(path)
        node_type = str(node.get("type"))
        if node_type not in {"file", "dir"}:
            report.add_error(f"{path_ctx}: type is illegal")
        status = str(node.get("status"))
        if status not in {"active", "deleted"}:
            report.add_error(f"{path_ctx}: status illegal")
        if not ensure_minute_timestamp(str(node.get("last_modified", ""))):
            report.add_error(f"{path_ctx}: last_modified must be YYYY-MM-DD-HH-MM")
        if not isinstance(node.get("editable"), bool):
            report.add_error(f"{path_ctx}: editable must be a Boolean value")
        note_text = str(node.get("note", "")).strip()
        if not note_text:
            report.add_error(f"{path_ctx}: note cannot be empty")
        elif any(hint in note_text for hint in TREE_NOTE_FORBIDDEN_HINTS):
            report.add_error(f"{path_ctx}: note The role of the file in the project needs to be described, and file attributes cannot be written")

    try:
        declared_text = extract_tree_text(text)
    except ValueError as exc:
        report.add_error(f"TREE.md: {exc}")
        declared_text = ""

    tree_module = load_tree_module()
    expected_text = normalize_text(
        tree_module.build_tree_text({"nodes": nodes, "last_updated": now_stamp()})  # type: ignore[arg-type]
    ).strip()
    if declared_text.strip() != expected_text:
        report.add_error("TREE.md: TREE_TEXT is inconsistent with the active node in DATA")

    prev_nodes = None
    if isinstance(state, dict):
        prev_nodes = state.get("tree_nodes")
    if isinstance(prev_nodes, list):
        prev_deleted = {str(n.get("path")) for n in prev_nodes if isinstance(n, dict) and n.get("status") == "deleted"}
        now_paths = {str(n.get("path")) for n in nodes if isinstance(n, dict)}
        missing_deleted = sorted(p for p in prev_deleted if p not in now_paths)
        if missing_deleted:
            report.add_error(f"TREE.md: Deleted paths were removed instead of retained records: {', '.join(missing_deleted)}")


def validate_agents_artifacts_layout(report: Report) -> None:
    root = ROOT / "agents_artifacts"
    if not root.exists():
        report.add_error("agents_artifacts: directory does not exist")
        return
    allowed_dirs = {"logs", "notes", "outputs"}
    for child in root.iterdir():
        if child.is_file():
            report.add_error(f"agents_artifacts: Direct file placement is not allowed in the root directory -> {child.name}")
            continue
        if child.is_dir() and child.name not in allowed_dirs:
            report.add_error(f"agents_artifacts: Unallowed subdirectory exists -> {child.name}")


def validate_read_only_and_frozen_dirs(baseline: dict[str, Any], report: Report) -> None:
    read_only_hashes = baseline.get("read_only_hashes")
    if not isinstance(read_only_hashes, dict):
        report.add_error("baseline: missing read_only_hashes")
        return
    for rel in READ_ONLY_FILES:
        path = ROOT / rel
        if not path.exists():
            report.add_error(f"Read-only file missing: {rel}")
            continue
        current_hash = sha256_text(read_text(path))
        expected_hash = str(read_only_hashes.get(rel, ""))
        if current_hash != expected_hash:
            report.add_error(f"Read-only file was modified: {rel}")

    standards_known = baseline.get("standards_file_list")
    if isinstance(standards_known, list):
        current = sorted((p.relative_to(ROOT).as_posix() for p in (ROOT / "agents_standards").glob("*.md")))
        expected = sorted(str(v) for v in standards_known)
        if current != expected:
            report.add_error("agents_standards: file collection changed")

    for key, folder in [("agents_tools_hashes", "agents_tools"), ("agents_web_hashes", "agents_web")]:
        expected_map = baseline.get(key)
        if not isinstance(expected_map, dict):
            report.add_error(f"baseline: missing {key}")
            continue
        current_map: dict[str, str] = {}
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if "__pycache__" in rel or rel.endswith(".pyc"):
                continue
            current_map[rel] = sha256_text(read_text(path))
        if set(current_map.keys()) != set(expected_map.keys()):
            report.add_error(f"{folder}: The file collection has changed")
            continue
        for rel, digest in current_map.items():
            if digest != expected_map.get(rel):
                report.add_error(f"{folder}: File modified -> {rel}")


def validate_metadata_headers(docs: dict[str, dict[str, Any]], baseline: dict[str, Any], report: Report) -> None:
    for name in EDITABLE_FILES:
        if name in docs:
            ensure_frontmatter_for_editable(name, docs[name]["frontmatter"], report)

    read_only_meta = baseline.get("read_only_frontmatter_keys")
    if isinstance(read_only_meta, dict):
        for rel in READ_ONLY_FILES:
            path = ROOT / rel
            if not path.exists():
                continue
            try:
                frontmatter, _ = parse_frontmatter(read_text(path))
            except ValueError:
                report.add_error(f"{rel}: frontmatter is invalid or missing")
                continue
            expected_keys = set(read_only_meta.get(rel, []))
            current_keys = set(frontmatter.keys())
            if expected_keys and current_keys != expected_keys:
                report.add_error(f"{rel}: frontmatter field set changes")


def save_doc_if_changed(name: str, docs: dict[str, dict[str, Any]], payload: dict[str, Any], new_last_updated: str) -> bool:
    old_text = docs[name]["text"]
    new_text = render_doc(name, new_last_updated, payload)
    if normalize_text(old_text).strip() == normalize_text(new_text).strip():
        return False
    write_text(ROOT / name, new_text)
    docs[name]["text"] = new_text
    docs[name]["frontmatter"] = {"last_updated": new_last_updated}
    docs[name]["payload"] = payload
    return True


def run_finalize(output_json: bool) -> int:
    report = Report()
    baseline = load_json_file(BASELINE_PATH)
    if baseline is None:
        report.add_error("baseline.json is missing, please execute `python agents_tools/baseline_refresh.py` first")
        print_report(report, output_json)
        return 1
    state = load_json_file(FINALIZE_STATE_PATH)

    tree_module = load_tree_module()
    tree_module.sync_tree()
    report.add_fix("TREE.md has been synchronized through tree.py")

    docs = load_docs(report)
    if report.errors:
        print_report(report, output_json)
        return 1
    if "MILESTONE.md" in docs:
        validate_prestart_readiness(docs["MILESTONE.md"]["payload"], report)

    now_value = now_stamp()
    previous_hashes = {}
    if isinstance(state, dict) and isinstance(state.get("file_hashes"), dict):
        previous_hashes = {str(k): str(v) for k, v in state["file_hashes"].items()}
    else:
        previous_hashes = {}
    current_hashes_before = compute_file_hashes()

    if "CHANGE.md" in docs:
        if migrate_change_dates(docs["CHANGE.md"]["payload"], report):
            save_doc_if_changed("CHANGE.md", docs, docs["CHANGE.md"]["payload"], now_value)
        changed = update_change_impacted_files(
            docs["CHANGE.md"]["payload"],
            previous_hashes=previous_hashes,
            current_hashes=current_hashes_before,
            report=report,
        )
        if changed:
            save_doc_if_changed("CHANGE.md", docs, docs["CHANGE.md"]["payload"], now_value)

    previous_statuses = None
    if isinstance(state, dict) and isinstance(state.get("milestone_statuses"), dict):
        previous_statuses = {str(k): str(v) for k, v in state["milestone_statuses"].items()}
    if "MILESTONE.md" in docs and update_milestone_updated_at(docs["MILESTONE.md"]["payload"], previous_statuses, now_value):
        report.add_fix("The updated_at of the milestone status change node has been automatically updated")
        save_doc_if_changed("MILESTONE.md", docs, docs["MILESTONE.md"]["payload"], now_value)

    if "CHANGE.md" in docs and not ensure_minute_timestamp(docs["CHANGE.md"]["frontmatter"].get("last_updated", "")):
        save_doc_if_changed("CHANGE.md", docs, docs["CHANGE.md"]["payload"], now_value)
    if "MILESTONE.md" in docs and not ensure_minute_timestamp(docs["MILESTONE.md"]["frontmatter"].get("last_updated", "")):
        save_doc_if_changed("MILESTONE.md", docs, docs["MILESTONE.md"]["payload"], now_value)

    validate_read_only_and_frozen_dirs(baseline, report)
    validate_agents_artifacts_layout(report)
    validate_metadata_headers(docs, baseline, report)

    if "MILESTONE.md" in docs:
        validate_milestone(docs["MILESTONE.md"]["payload"], baseline=baseline, state=state, report=report)
    if "CHANGE.md" in docs:
        validate_change(docs["CHANGE.md"]["payload"], state=state, report=report)
    if "TREE.md" in docs:
        validate_tree(docs["TREE.md"]["text"], docs["TREE.md"]["payload"], state=state, report=report)

    if not report.errors:
        current_hashes_after = compute_file_hashes()
        milestone_statuses: dict[str, str] = {}
        for node in docs["MILESTONE.md"]["payload"].get("milestones", []):
            if isinstance(node, dict):
                milestone_statuses[str(node.get("id"))] = str(node.get("status"))
        finalize_state = {
            "last_finalized_at": now_stamp(),
            "file_hashes": current_hashes_after,
            "milestone_statuses": milestone_statuses,
            "change_entries": docs["CHANGE.md"]["payload"].get("changes", []),
            "tree_nodes": docs["TREE.md"]["payload"].get("nodes", []),
            "skip_progress_checks_once": False,
            "state_source": "finalize",
        }
        FINALIZE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FINALIZE_STATE_PATH.write_text(json.dumps(finalize_state, ensure_ascii=False, indent=2), encoding="utf-8")
        report.add_fix("finalize_state updated")

    report.details["baseline_path"] = BASELINE_PATH.relative_to(ROOT).as_posix()
    report.details["finalize_state_path"] = FINALIZE_STATE_PATH.relative_to(ROOT).as_posix()
    print_report(report, output_json)
    return 0 if not report.errors else 1


def print_report(report: Report, output_json: bool) -> None:
    payload = report.to_dict()
    if output_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"status: {payload['status']}")
    print(f"Error: {payload['error_count']}, Warning: {payload['warning_count']}, Fix: {payload['fix_count']}")
    if report.errors:
        print("Error details:")
        for item in report.errors:
            print(f"  - {item}")
    if report.warnings:
        print("Warning details:")
        for item in report.warnings:
            print(f"  - {item}")
    if report.fixes:
        print("Repair details:")
        for item in report.fixes:
            print(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTS final check validator (only supports finalize)")
    parser.add_argument("command", choices=["finalize"], help="Only the finalize command is supported")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()
    if args.command == "finalize":
        return run_finalize(output_json=args.json)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
