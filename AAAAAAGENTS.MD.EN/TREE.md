---
last_updated: 2026-03-08-23-38
---

# TREE

## TREE_TEXT
```text
.
├── agents_artifacts
│   ├── logs
│   ├── notes
│   └── outputs
│       ├── baseline.json
│       ├── finalize_state.json
│       └── rules_snapshot.json
├── agents_standards
│   ├── BATCH_STANDARD.md
│   ├── HTML_STANDARD.md
│   ├── JSON_STANDARD.md
│   ├── MARKDOWN_STANDARD.md
│   ├── PYTHON_STANDARD.md
│   ├── SHELL_SCRIPT_STANDARD.md
│   ├── TEXT_STANDARD.md
│   └── YAML_STANDARD.md
├── agents_tools
│   ├── baseline_refresh.py
│   ├── tree.py
│   └── verify_rules.py
├── agents_web
│   ├── static
│   │   ├── app.css
│   │   └── app.js
│   ├── templates
│   │   └── index.html
│   ├── renderer.py
│   └── server.py
├── AGENTS.md
├── BACKGROUND.md
├── CHANGE.md
├── MILESTONE.md
├── requirements.txt
├── start_web.bat
├── start_web.py
├── start_web.sh
└── TREE.md
```

## DATA
```yaml
{
  "nodes": [
    {
      "path": ".",
      "name": ".",
      "parent": "",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-22-48",
      "editable": false,
      "note": "Project root directory, centralized management of rule documents, automation scripts and visualization modules"
    },
    {
      "path": "agents_artifacts",
      "name": "agents_artifacts",
      "parent": ".",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-04-37",
      "editable": false,
      "note": "Run the product root directory, store logs, notes and output snapshots"
    },
    {
      "path": "agents_standards",
      "name": "agents_standards",
      "parent": ".",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-22-03",
      "editable": false,
      "note": "Standard specification directory, which stores code and document specification files"
    },
    {
      "path": "agents_tools",
      "name": "agents_tools",
      "parent": ".",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-13-55",
      "editable": false,
      "note": "Automated script directory, responsible for synchronization, verification and baseline maintenance"
    },
    {
      "path": "agents_web",
      "name": "agents_web",
      "parent": ".",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-22-26",
      "editable": false,
      "note": "Local visualization service directory"
    },
    {
      "path": "AGENTS.md",
      "name": "AGENTS.md",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-20-19",
      "editable": false,
      "note": "Project master control constraint file, defining Agent workflow and boundaries"
    },
    {
      "path": "BACKGROUND.md",
      "name": "BACKGROUND.md",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-15-50",
      "editable": false,
      "note": "Project background and resource information templates, maintained by users"
    },
    {
      "path": "CHANGE.md",
      "name": "CHANGE.md",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-23-38",
      "editable": true,
      "note": "Structured change log file"
    },
    {
      "path": "MILESTONE.md",
      "name": "MILESTONE.md",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-23-37",
      "editable": true,
      "note": "Milestone planning and node status record files"
    },
    {
      "path": "requirements.txt",
      "name": "requirements.txt",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-05-11",
      "editable": false,
      "note": "Python dependency manifest file"
    },
    {
      "path": "start_web.bat",
      "name": "start_web.bat",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-23",
      "editable": false,
      "note": "Windows default entry script, automatically calls Python to start local visualization service after double-clicking"
    },
    {
      "path": "start_web.py",
      "name": "start_web.py",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-22",
      "editable": false,
      "note": "Cross-platform Python can start local visualization service scripts with one click"
    },
    {
      "path": "start_web.sh",
      "name": "start_web.sh",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-23",
      "editable": false,
      "note": "Linux starts local visualization service script with one click"
    },
    {
      "path": "TREE.md",
      "name": "TREE.md",
      "parent": ".",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-23-38",
      "editable": true,
      "note": "Project file tree and node function description file"
    },
    {
      "path": "start_web.ps1",
      "name": "start_web.ps1",
      "parent": ".",
      "type": "file",
      "status": "deleted",
      "last_modified": "2026-03-08-16-17",
      "editable": false,
      "note": "Windows compatible entry script, transposed Python launcher, non-default entry"
    },
    {
      "path": "agents_artifacts/logs",
      "name": "logs",
      "parent": "agents_artifacts",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-04-37",
      "editable": false,
      "note": "Execution log directory, used to troubleshoot task process problems"
    },
    {
      "path": "agents_artifacts/notes",
      "name": "notes",
      "parent": "agents_artifacts",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-04-37",
      "editable": false,
      "note": "Supplementary notes directory, used to save manual instructions"
    },
    {
      "path": "agents_artifacts/outputs",
      "name": "outputs",
      "parent": "agents_artifacts",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-22-07",
      "editable": false,
      "note": "Script output directory, used to save baselines and status snapshots"
    },
    {
      "path": "agents_artifacts/outputs/baseline.json",
      "name": "baseline.json",
      "parent": "agents_artifacts/outputs",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-23-38",
      "editable": false,
      "note": "User baseline file, recording boundary hash and structure locking information"
    },
    {
      "path": "agents_artifacts/outputs/finalize_state.json",
      "name": "finalize_state.json",
      "parent": "agents_artifacts/outputs",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-23-38",
      "editable": false,
      "note": "Finishing status file, records the last task comparison baseline"
    },
    {
      "path": "agents_artifacts/outputs/rules_snapshot.json",
      "name": "rules_snapshot.json",
      "parent": "agents_artifacts/outputs",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-05-12",
      "editable": false,
      "note": "Historical rule snapshot file for compatibility with old processes"
    },
    {
      "path": "agents_standards/BATCH_STANDARD.md",
      "name": "BATCH_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-04",
      "editable": false,
      "note": "BATCH standard specification file, defining the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_standards/HTML_STANDARD.md",
      "name": "HTML_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-06",
      "editable": false,
      "note": "HTML standard specification document, defining the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_standards/JSON_STANDARD.md",
      "name": "JSON_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-06",
      "editable": false,
      "note": "JSON standard specification file, defining the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_standards/MARKDOWN_STANDARD.md",
      "name": "MARKDOWN_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-21-54",
      "editable": false,
      "note": "Markdown writing specification document"
    },
    {
      "path": "agents_standards/PYTHON_STANDARD.md",
      "name": "PYTHON_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-21-59",
      "editable": false,
      "note": "Python development specification document"
    },
    {
      "path": "agents_standards/SHELL_SCRIPT_STANDARD.md",
      "name": "SHELL_SCRIPT_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-05",
      "editable": false,
      "note": "SHELL SCRIPT standard specification document, which defines the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_standards/TEXT_STANDARD.md",
      "name": "TEXT_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-05",
      "editable": false,
      "note": "TEXT standard specification file, which defines the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_standards/YAML_STANDARD.md",
      "name": "YAML_STANDARD.md",
      "parent": "agents_standards",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-07",
      "editable": false,
      "note": "YAML standard specification file, defining the writing, annotation, format and verification requirements for this type of content"
    },
    {
      "path": "agents_tools/baseline_refresh.py",
      "name": "baseline_refresh.py",
      "parent": "agents_tools",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-21-31",
      "editable": false,
      "note": "User baseline refresh script, rebuild structure and hash baseline"
    },
    {
      "path": "agents_tools/tree.py",
      "name": "tree.py",
      "parent": "agents_tools",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-29",
      "editable": false,
      "note": "File tree synchronization script, generate TREE_TEXT and node data"
    },
    {
      "path": "agents_tools/verify_rules.py",
      "name": "verify_rules.py",
      "parent": "agents_tools",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-21-46",
      "editable": false,
      "note": "The only finalize verification script, performs full rule checking"
    },
    {
      "path": "agents_web/static",
      "name": "static",
      "parent": "agents_web",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-22-26",
      "editable": false,
      "note": "Web static resource directory, storing styles and front-end scripts"
    },
    {
      "path": "agents_web/templates",
      "name": "templates",
      "parent": "agents_web",
      "type": "dir",
      "status": "active",
      "last_modified": "2026-03-08-18-11",
      "editable": false,
      "note": "Web front-end template directory"
    },
    {
      "path": "agents_web/renderer.py",
      "name": "renderer.py",
      "parent": "agents_web",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-22",
      "editable": false,
      "note": "Document parsing and flowchart rendering logic"
    },
    {
      "path": "agents_web/server.py",
      "name": "server.py",
      "parent": "agents_web",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-28",
      "editable": false,
      "note": "Web service entrance and API routing implementation"
    },
    {
      "path": "agents_web/static/app.css",
      "name": "app.css",
      "parent": "agents_web/static",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-26",
      "editable": false,
      "note": "Workbench style file, defining the overall interface layout and visual style"
    },
    {
      "path": "agents_web/static/app.js",
      "name": "app.js",
      "parent": "agents_web/static",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-26",
      "editable": false,
      "note": "Workbench front-end script file, handles interaction, rendering and interface calling"
    },
    {
      "path": "agents_web/templates/index.html",
      "name": "index.html",
      "parent": "agents_web/templates",
      "type": "file",
      "status": "active",
      "last_modified": "2026-03-08-22-28",
      "editable": false,
      "note": "Dashboard page template, providing tree navigation and node form editing"
    }
  ]
}
```
