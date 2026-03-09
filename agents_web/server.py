from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

try:
    from .renderer import (
        build_graph,
        build_tree_explorer,
        build_tree_text_from_payload,
        load_document,
        serialize_document,
    )
except ImportError:
    from renderer import (  # type: ignore
        build_graph,
        build_tree_explorer,
        build_tree_text_from_payload,
        load_document,
        serialize_document,
    )

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"
BACKUP_DIR = ROOT / "agents_artifacts" / "outputs" / "web_backups"
STANDARDS_DIR = ROOT / "agents_standards"

BASE_DOCS = ["AGENTS.md", "BACKGROUND.md", "MILESTONE.md", "CHANGE.md", "TREE.md"]
MODEL_EDITABLE_DOCS = {"MILESTONE.md", "CHANGE.md", "TREE.md"}
GRAPH_DOCS = {"MILESTONE.md", "CHANGE.md"}
TIME_FMT = "%Y-%m-%d-%H-%M"

app = FastAPI(title="AGENTS Rules Dashboard", version="0.5.1")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.middleware("http")
async def disable_cache(request: Request, call_next: Any) -> Any:
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


class SaveDocRequest(BaseModel):
    content: str


class SaveModelRequest(BaseModel):
    payload: dict[str, Any]


class NodeUpdateRequest(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)


class NodeCreateRequest(BaseModel):
    id: str = ""
    title: str = ""


class StandardCreateRequest(BaseModel):
    name: str


class GraphLayoutRequest(BaseModel):
    positions: dict[str, dict[str, float]] = Field(default_factory=dict)


def ensure_runtime_dirs() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime(TIME_FMT)


def today_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def mtime_stamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime(TIME_FMT)


def asset_version() -> str:
    files = [STATIC_DIR / "app.css", STATIC_DIR / "app.js", TEMPLATES_DIR / "index.html"]
    versions: list[str] = []
    for path in files:
        if not path.exists():
            continue
        versions.append(str(int(path.stat().st_mtime)))
    if not versions:
        return now_stamp()
    return "-".join(versions)


def list_standard_docs() -> list[str]:
    if not STANDARDS_DIR.exists():
        return []
    return sorted(
        [f"agents_standards/{p.name}" for p in STANDARDS_DIR.glob("*_STANDARD.md") if p.is_file()],
        key=str.lower,
    )


def all_docs_order() -> list[str]:
    return BASE_DOCS + list_standard_docs()


def is_standard_doc(name: str) -> bool:
    return name.startswith("agents_standards/") and name in list_standard_docs()


def is_user_editable_doc(name: str) -> bool:
    return name in all_docs_order()


def doc_kind(name: str) -> str:
    if name in GRAPH_DOCS:
        return "graph_doc"
    if name == "TREE.md":
        return "tree_doc"
    return "plain_doc"


def normalize_doc_name(name: str) -> str:
    posix = PurePosixPath(str(name).replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts:
        raise HTTPException(status_code=400, detail="路径不合法")
    value = posix.as_posix().strip("/")
    if not value:
        raise HTTPException(status_code=400, detail="路径不能为空")
    return value


def resolve_doc(name: str) -> Path:
    normalized = normalize_doc_name(name)
    if normalized not in all_docs_order():
        raise HTTPException(status_code=404, detail=f"未知文档: {normalized}")
    path = (ROOT / normalized).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise HTTPException(status_code=400, detail="文档路径越界")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"文档不存在: {normalized}")
    return path


def run_command(command: list[str]) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def build_verify_hints(errors: list[str]) -> list[str]:
    hints: list[str] = []
    if any("必须且只能有 1 个节点状态变化" in err for err in errors) or any(
        "exactly one node status change is required" in err for err in errors
    ):
        hints.append("本次终检要求里程碑状态必须且仅能有一个 unfinished->done 变化")
        hints.append("如果当前只是做文档/UI维护，请先点击“同步终检基线”再执行终检")
    if any("CHANGE.md: 必须且只能新增一条变更记录" in err for err in errors) or any(
        "CHANGE.md: exactly one new change entry is required" in err for err in errors
    ):
        hints.append("请在 CHANGE.md 仅新增一条最新记录，历史条目不可改删")
    if any("只读文件被修改" in err for err in errors) or any("read-only file modified" in err for err in errors):
        hints.append("检测到用户修改了只读基线文件，先执行“同步终检基线”将当前内容设为新标准")
    if any("日期格式错误" in err for err in errors) or any("invalid date" in err for err in errors):
        hints.append("CHANGE.date 需要使用 YYYY-MM-DD-HH-MM 格式，例如 2026-03-09-15-30")
    if not hints and errors:
        hints.append("请按错误列表逐项修复后再执行终检，必要时先同步终检基线")
    return hints


def backup_file(path: Path) -> Path:
    ensure_runtime_dirs()
    safe_name = path.relative_to(ROOT).as_posix().replace("/", "__")
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = BACKUP_DIR / f"{safe_name}.{stamp}.bak.md"
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def latest_backup(path: Path) -> Path | None:
    safe_name = path.relative_to(ROOT).as_posix().replace("/", "__")
    candidates = sorted(BACKUP_DIR.glob(f"{safe_name}.*.bak.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def build_docs_tree() -> list[dict[str, Any]]:
    root: dict[str, Any] = {"name": ".", "type": "dir", "children": {}}
    meta: dict[str, dict[str, Any]] = {}
    for name in all_docs_order():
        path = ROOT / name
        parts = name.split("/")
        node = root
        current_path: list[str] = []
        for idx, part in enumerate(parts):
            current_path.append(part)
            key = "/".join(current_path)
            is_file = idx == len(parts) - 1
            if part not in node["children"]:
                node["children"][part] = {"name": part, "type": "file" if is_file else "dir", "children": {}}
            if is_file:
                meta[key] = {
                    "editable": is_user_editable_doc(key),
                    "graph_enabled": key in GRAPH_DOCS,
                    "doc_kind": doc_kind(key),
                    "exists": path.exists(),
                    "last_modified": mtime_stamp(path) if path.exists() else None,
                }
            node = node["children"][part]

    def to_list(node: dict[str, Any], parent_path: str = "") -> list[dict[str, Any]]:
        children: list[dict[str, Any]] = []
        for child_name in sorted(node.get("children", {}).keys(), key=str.lower):
            child = node["children"][child_name]
            full_path = child_name if not parent_path else f"{parent_path}/{child_name}"
            if child["type"] == "dir":
                children.append({"name": child_name, "type": "dir", "path": full_path, "children": to_list(child, full_path)})
            else:
                item = {"name": child_name, "type": "file", "path": full_path}
                item.update(meta.get(full_path, {}))
                children.append(item)
        return children

    return to_list(root)


def model_shape(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    if name not in MODEL_EDITABLE_DOCS:
        return {"node_key": "", "nodes": []}
    if name == "MILESTONE.md":
        nodes = payload.get("milestones", [])
        return {"node_key": "id", "nodes": nodes if isinstance(nodes, list) else []}
    if name == "CHANGE.md":
        nodes = payload.get("changes", [])
        return {"node_key": "version", "nodes": nodes if isinstance(nodes, list) else []}
    if name == "TREE.md":
        nodes = payload.get("nodes", [])
        return {"node_key": "path", "nodes": nodes if isinstance(nodes, list) else []}
    return {"node_key": "", "nodes": []}


def graph_node_ids(name: str, payload: dict[str, Any]) -> set[str]:
    if name == "MILESTONE.md":
        nodes = payload.get("milestones", [])
        if not isinstance(nodes, list):
            return set()
        return {str(node.get("id", "")).strip() for node in nodes if isinstance(node, dict) and str(node.get("id", "")).strip()}
    if name == "CHANGE.md":
        nodes = payload.get("changes", [])
        if not isinstance(nodes, list):
            return set()
        return {
            str(node.get("version", "")).strip()
            for node in nodes
            if isinstance(node, dict) and str(node.get("version", "")).strip()
        }
    return set()


def graph_positions_from_payload(name: str, payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    if name not in GRAPH_DOCS:
        return {}
    layout = payload.get("layout")
    if not isinstance(layout, dict):
        return {}
    raw = layout.get("positions")
    if not isinstance(raw, dict):
        return {}
    valid_ids = graph_node_ids(name, payload)
    result: dict[str, dict[str, float]] = {}
    for node_id, pos in raw.items():
        if str(node_id) not in valid_ids:
            continue
        if not isinstance(pos, dict):
            continue
        try:
            x = float(pos.get("x"))
            y = float(pos.get("y"))
        except (TypeError, ValueError):
            continue
        result[str(node_id)] = {"x": x, "y": y}
    if valid_ids and len(result) != len(valid_ids):
        return {}
    return result


def with_graph_positions(name: str, payload: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(graph)
    enriched["positions"] = graph_positions_from_payload(name, payload)
    return enriched


def write_payload_to_doc(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    path = resolve_doc(name)
    old_doc = load_document(path)
    frontmatter = dict(old_doc["frontmatter"])
    frontmatter["last_updated"] = now_stamp()
    tree_text = build_tree_text_from_payload(payload) if name == "TREE.md" else ""
    content = serialize_document(name, frontmatter, payload, tree_text=tree_text)
    backup = backup_file(path)
    path.write_text(content, encoding="utf-8")
    new_doc = load_document(path)
    return {
        "backup": backup.relative_to(ROOT).as_posix(),
        "last_modified": mtime_stamp(path),
        "document": new_doc,
    }


def update_node(name: str, node_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    path = resolve_doc(name)
    doc = load_document(path)
    payload = dict(doc["payload"])
    shape = model_shape(name, payload)
    node_key = shape["node_key"]
    nodes = shape["nodes"]
    if not isinstance(nodes, list):
        raise HTTPException(status_code=400, detail="节点列表格式不正确")

    target = None
    for node in nodes:
        if isinstance(node, dict) and str(node.get(node_key)) == node_id:
            target = node
            break
    if target is None:
        raise HTTPException(status_code=404, detail=f"未找到节点: {node_id}")

    if name == "MILESTONE.md":
        allowed = {"title", "prerequisites", "postnodes", "why", "what", "how", "verify", "ddl", "status", "notes"}
    elif name == "CHANGE.md":
        allowed = {"date", "reason", "action", "observation", "notes", "suggestions"}
    elif name == "TREE.md":
        allowed = {"note"}
    else:
        allowed = set()

    for key, value in fields.items():
        if key in allowed:
            target[key] = value

    if name == "MILESTONE.md":
        payload["milestones"] = nodes
    elif name == "CHANGE.md":
        payload["changes"] = nodes
    elif name == "TREE.md":
        payload["nodes"] = nodes

    return write_payload_to_doc(name, payload)


def create_milestone_node(payload: dict[str, Any], node_id: str, title: str) -> dict[str, Any]:
    nodes = payload.get("milestones")
    if not isinstance(nodes, list):
        raise HTTPException(status_code=400, detail="里程碑数据格式不正确")
    if any(isinstance(one, dict) and str(one.get("id")) == node_id for one in nodes):
        raise HTTPException(status_code=409, detail=f"里程碑 ID 已存在: {node_id}")
    node = {
        "id": node_id,
        "title": title or node_id,
        "prerequisites": [],
        "postnodes": [],
        "why": ["待补充"],
        "what": ["待补充"],
        "how": ["待补充"],
        "verify": ["待补充"],
        "ddl": today_date(),
        "status": "unfinished",
        "notes": ["待补充"],
        "updated_at": now_stamp(),
    }
    nodes.append(node)
    payload["milestones"] = nodes
    return payload


def delete_milestone_node(payload: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = payload.get("milestones")
    if not isinstance(nodes, list):
        raise HTTPException(status_code=400, detail="里程碑数据格式不正确")
    kept = [one for one in nodes if not (isinstance(one, dict) and str(one.get("id")) == node_id)]
    if len(kept) == len(nodes):
        raise HTTPException(status_code=404, detail=f"未找到节点: {node_id}")
    if not kept:
        raise HTTPException(status_code=400, detail="至少保留一个里程碑节点")
    for one in kept:
        if not isinstance(one, dict):
            continue
        for key in ["prerequisites", "postnodes"]:
            value = one.get(key)
            if isinstance(value, list):
                one[key] = [v for v in value if str(v) != node_id]
    payload["milestones"] = kept
    return payload


def normalize_standard_token(raw: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_]", "", raw.strip()).upper().strip("_")
    if not token:
        raise HTTPException(status_code=400, detail="标准名称不能为空")
    return token


def standard_relpath_from_name(raw: str) -> str:
    value = str(raw or "").strip().replace("\\", "/")
    if value.startswith("agents_standards/"):
        filename = value.split("/", 1)[1]
        if not filename:
            raise HTTPException(status_code=400, detail="无效标准文件名")
        return f"agents_standards/{filename}"
    token = normalize_standard_token(value.removesuffix("_STANDARD.md").removesuffix("_STANDARD.MD"))
    return f"agents_standards/{token}_STANDARD.md"


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "docs_tree": build_docs_tree(),
            "asset_version": asset_version(),
        },
    )


@app.get("/api/docs")
def list_docs() -> JSONResponse:
    docs = []
    for name in all_docs_order():
        path = ROOT / name
        docs.append(
            {
                "name": name,
                "editable": is_user_editable_doc(name),
                "doc_kind": doc_kind(name),
                "graph_enabled": name in GRAPH_DOCS,
                "exists": path.exists(),
                "last_modified": mtime_stamp(path) if path.exists() else None,
            }
        )
    return JSONResponse({"docs": docs, "tree": build_docs_tree()})


@app.get("/api/docs/{name:path}")
def get_doc(name: str) -> JSONResponse:
    normalized = normalize_doc_name(name)
    path = resolve_doc(normalized)
    doc = load_document(path)
    graph_enabled = normalized in GRAPH_DOCS
    graph = (
        with_graph_positions(normalized, doc["payload"], build_graph(normalized, doc["payload"]))
        if graph_enabled
        else {"type": "none", "nodes": [], "edges": [], "positions": {}}
    )
    tree_explorer = build_tree_explorer(doc["payload"]) if normalized == "TREE.md" else None
    return JSONResponse(
        {
            "name": normalized,
            "editable": is_user_editable_doc(normalized),
            "doc_kind": doc_kind(normalized),
            "view_mode": "preview",
            "graph_enabled": graph_enabled,
            "raw": doc["raw"],
            "frontmatter": doc["frontmatter"],
            "rendered_html": doc["rendered_html"],
            "graph": graph,
            "model": model_shape(normalized, doc["payload"]),
            "tree_explorer": tree_explorer,
        }
    )


@app.put("/api/docs/{name:path}")
def save_doc(name: str, body: SaveDocRequest) -> JSONResponse:
    normalized = normalize_doc_name(name)
    path = resolve_doc(normalized)
    if not is_user_editable_doc(normalized):
        raise HTTPException(status_code=403, detail=f"{normalized} 为只读文档")
    backup = backup_file(path)
    path.write_text(body.content, encoding="utf-8")
    return JSONResponse(
        {
            "status": "ok",
            "message": f"{normalized} 已保存",
            "backup": backup.relative_to(ROOT).as_posix(),
            "last_modified": mtime_stamp(path),
        }
    )


@app.post("/api/docs/{name:path}/reset")
def reset_doc(name: str) -> JSONResponse:
    normalized = normalize_doc_name(name)
    path = resolve_doc(normalized)
    if not is_user_editable_doc(normalized):
        raise HTTPException(status_code=403, detail=f"{normalized} 为只读文档")
    backup = latest_backup(path)
    if backup is None:
        raise HTTPException(status_code=404, detail=f"未找到 {normalized} 的备份")
    path.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
    return JSONResponse(
        {
            "status": "ok",
            "message": f"{normalized} 已从备份恢复",
            "restored_from": backup.relative_to(ROOT).as_posix(),
            "last_modified": mtime_stamp(path),
        }
    )


@app.get("/api/model/{name:path}")
def get_model(name: str) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized not in MODEL_EDITABLE_DOCS:
        raise HTTPException(status_code=403, detail=f"{normalized} 不支持结构化节点编辑")
    path = resolve_doc(normalized)
    doc = load_document(path)
    return JSONResponse({"name": normalized, "model": model_shape(normalized, doc["payload"])})


@app.post("/api/model/{name:path}/node/{node_id:path}")
def post_model_node(name: str, node_id: str, body: NodeUpdateRequest) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized not in MODEL_EDITABLE_DOCS:
        raise HTTPException(status_code=403, detail=f"{normalized} 不支持结构化节点编辑")
    result = update_node(normalized, node_id, body.fields)
    graph_enabled = normalized in GRAPH_DOCS
    graph = (
        with_graph_positions(normalized, result["document"]["payload"], build_graph(normalized, result["document"]["payload"]))
        if graph_enabled
        else {"type": "none", "nodes": [], "edges": [], "positions": {}}
    )
    tree_explorer = build_tree_explorer(result["document"]["payload"]) if normalized == "TREE.md" else None
    return JSONResponse(
        {
            "status": "ok",
            "backup": result["backup"],
            "last_modified": result["last_modified"],
            "graph": graph,
            "model": model_shape(normalized, result["document"]["payload"]),
            "tree_explorer": tree_explorer,
        }
    )


@app.post("/api/model/{name:path}/save")
def post_model_save(name: str, body: SaveModelRequest) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized not in MODEL_EDITABLE_DOCS:
        raise HTTPException(status_code=403, detail=f"{normalized} 不支持结构化节点编辑")
    result = write_payload_to_doc(normalized, body.payload)
    graph_enabled = normalized in GRAPH_DOCS
    graph = (
        with_graph_positions(normalized, result["document"]["payload"], build_graph(normalized, result["document"]["payload"]))
        if graph_enabled
        else {"type": "none", "nodes": [], "edges": [], "positions": {}}
    )
    tree_explorer = build_tree_explorer(result["document"]["payload"]) if normalized == "TREE.md" else None
    return JSONResponse(
        {
            "status": "ok",
            "backup": result["backup"],
            "last_modified": result["last_modified"],
            "graph": graph,
            "model": model_shape(normalized, result["document"]["payload"]),
            "tree_explorer": tree_explorer,
        }
    )


@app.post("/api/model/{name:path}/nodes/create")
def create_model_node(name: str, body: NodeCreateRequest) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized != "MILESTONE.md":
        raise HTTPException(status_code=403, detail="仅 MILESTONE 支持节点新增和删除")
    node_id = str(body.id or "").strip()
    if not node_id:
        raise HTTPException(status_code=400, detail="节点 ID 不能为空")
    path = resolve_doc(normalized)
    doc = load_document(path)
    payload = dict(doc["payload"])
    payload = create_milestone_node(payload, node_id=node_id, title=str(body.title or "").strip())
    result = write_payload_to_doc(normalized, payload)
    return JSONResponse(
        {
            "status": "ok",
            "backup": result["backup"],
            "last_modified": result["last_modified"],
            "graph": with_graph_positions(normalized, result["document"]["payload"], build_graph(normalized, result["document"]["payload"])),
            "model": model_shape(normalized, result["document"]["payload"]),
        }
    )


@app.delete("/api/model/{name:path}/node/{node_id:path}")
def delete_model_node(name: str, node_id: str) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized != "MILESTONE.md":
        raise HTTPException(status_code=403, detail="仅 MILESTONE 支持节点新增和删除")
    path = resolve_doc(normalized)
    doc = load_document(path)
    payload = dict(doc["payload"])
    payload = delete_milestone_node(payload, node_id=node_id)
    result = write_payload_to_doc(normalized, payload)
    return JSONResponse(
        {
            "status": "ok",
            "backup": result["backup"],
            "last_modified": result["last_modified"],
            "graph": with_graph_positions(normalized, result["document"]["payload"], build_graph(normalized, result["document"]["payload"])),
            "model": model_shape(normalized, result["document"]["payload"]),
        }
    )


@app.post("/api/standards/create")
def create_standard(body: StandardCreateRequest) -> JSONResponse:
    token = normalize_standard_token(body.name)
    rel = f"agents_standards/{token}_STANDARD.md"
    path = (ROOT / rel).resolve()
    if path.exists():
        raise HTTPException(status_code=409, detail=f"标准已存在: {path.name}")
    title = f"{token} STANDARD"
    content = (
        "---\n"
        f"last_updated: {now_stamp()}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## RULES\n"
        "- 用户在此补充规范\n"
    )
    path.write_text(content, encoding="utf-8")
    return JSONResponse({"status": "ok", "file": rel, "last_modified": mtime_stamp(path), "docs": all_docs_order(), "tree": build_docs_tree()})


@app.delete("/api/standards/{name:path}")
def delete_standard(name: str) -> JSONResponse:
    rel = standard_relpath_from_name(name)
    if rel not in list_standard_docs():
        raise HTTPException(status_code=404, detail=f"标准不存在: {rel}")
    path = (ROOT / rel).resolve()
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"标准不存在: {rel}")
    path.unlink()
    return JSONResponse({"status": "ok", "deleted": rel, "docs": all_docs_order(), "tree": build_docs_tree()})


@app.get("/api/tree/explorer")
def get_tree_explorer() -> JSONResponse:
    path = resolve_doc("TREE.md")
    doc = load_document(path)
    return JSONResponse({"name": "TREE.md", "explorer": build_tree_explorer(doc["payload"])})


@app.post("/api/tree/sync")
def sync_tree() -> JSONResponse:
    code, stdout, stderr = run_command([sys.executable, str(ROOT / "agents_tools" / "tree.py"), "sync"])
    return JSONResponse({"status": "ok" if code == 0 else "failed", "exit_code": code, "stdout": stdout, "stderr": stderr})


@app.post("/api/verify/finalize")
def verify_finalize() -> JSONResponse:
    code, stdout, stderr = run_command([sys.executable, str(ROOT / "agents_tools" / "verify_rules.py"), "finalize", "--json"])
    parsed: dict[str, Any]
    try:
        parsed = json.loads(stdout) if stdout else {"status": "failed", "errors": ["终检脚本没有输出内容"]}
    except json.JSONDecodeError:
        parsed = {"status": "failed", "errors": [stdout or "终检脚本输出不是有效 JSON"]}
    errors = parsed.get("errors")
    if not isinstance(errors, list):
        errors = []
    parsed["exit_code"] = code
    parsed["hints"] = build_verify_hints([str(err) for err in errors])
    if stderr:
        parsed["stderr"] = stderr
    return JSONResponse(parsed)


@app.post("/api/verify")
def verify_finalize_compat() -> JSONResponse:
    return verify_finalize()


def _refresh_baseline_impl() -> JSONResponse:
    code, stdout, stderr = run_command([sys.executable, str(ROOT / "agents_tools" / "baseline_refresh.py")])
    payload: dict[str, Any]
    try:
        payload = json.loads(stdout) if stdout else {"status": "failed", "message": "基线脚本没有输出内容"}
    except json.JSONDecodeError:
        payload = {"status": "failed", "message": stdout or "基线脚本输出不是有效 JSON"}
    payload["exit_code"] = code
    if stderr:
        payload["stderr"] = stderr
    if code != 0:
        return JSONResponse(payload, status_code=500)
    return JSONResponse(payload)


@app.post("/api/baseline/refresh")
def refresh_baseline() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/baseline/refresh")
def refresh_baseline_get() -> JSONResponse:
    return _refresh_baseline_impl()


@app.post("/api/baseline/sync")
def sync_baseline_alias() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/baseline/sync")
def sync_baseline_alias_get() -> JSONResponse:
    return _refresh_baseline_impl()


@app.post("/api/baseline")
def baseline_alias() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/baseline")
def baseline_alias_get() -> JSONResponse:
    return _refresh_baseline_impl()


@app.post("/api/baseline_refresh")
def baseline_refresh_legacy() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/baseline_refresh")
def baseline_refresh_legacy_get() -> JSONResponse:
    return _refresh_baseline_impl()


@app.post("/api/baseline-refresh")
def baseline_refresh_dash_legacy() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/baseline-refresh")
def baseline_refresh_dash_legacy_get() -> JSONResponse:
    return _refresh_baseline_impl()


@app.get("/api/meta")
def api_meta() -> JSONResponse:
    return JSONResponse(
        {
            "service": "agents_web",
            "version": app.version,
            "time_format": TIME_FMT,
            "baseline_routes": [
                "/api/baseline/refresh",
                "/api/baseline/sync",
                "/api/baseline",
                "/api/baseline_refresh",
                "/api/baseline-refresh",
            ],
        }
    )


@app.post("/api/graph/{name:path}/layout")
def save_graph_layout(name: str, body: GraphLayoutRequest) -> JSONResponse:
    normalized = normalize_doc_name(name)
    if normalized not in GRAPH_DOCS:
        raise HTTPException(status_code=403, detail=f"{normalized} 不支持流程图布局持久化")
    path = resolve_doc(normalized)
    doc = load_document(path)
    payload = dict(doc["payload"])
    nodes = graph_node_ids(normalized, payload)
    layout = payload.get("layout")
    if not isinstance(layout, dict):
        layout = {}
    positions: dict[str, dict[str, float]] = {}
    for node_id, pos in body.positions.items():
        if str(node_id) not in nodes:
            continue
        if not isinstance(pos, dict):
            continue
        try:
            x = float(pos.get("x"))
            y = float(pos.get("y"))
        except (TypeError, ValueError):
            continue
        positions[str(node_id)] = {"x": x, "y": y}
    layout["positions"] = positions
    payload["layout"] = layout
    result = write_payload_to_doc(normalized, payload)
    return JSONResponse(
        {
            "status": "ok",
            "backup": result["backup"],
            "last_modified": result["last_modified"],
            "graph": with_graph_positions(normalized, result["document"]["payload"], build_graph(normalized, result["document"]["payload"])),
            "saved_count": len(positions),
        }
    )


@app.get("/api/graph/{name:path}")
def get_graph(name: str) -> JSONResponse:
    normalized = normalize_doc_name(name)
    path = resolve_doc(normalized)
    doc = load_document(path)
    if normalized not in GRAPH_DOCS:
        return JSONResponse(
            {
                "name": normalized,
                "graph_enabled": False,
                "graph": {"type": "none", "nodes": [], "edges": [], "positions": {}},
            }
        )
    return JSONResponse(
        {
            "name": normalized,
            "graph_enabled": True,
            "graph": with_graph_positions(normalized, doc["payload"], build_graph(normalized, doc["payload"])),
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agents_web.server:app", host="127.0.0.1", port=8765, reload=True)
