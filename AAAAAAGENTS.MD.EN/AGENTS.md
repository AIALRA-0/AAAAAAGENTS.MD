---
last_updated: 2026-03-11-09-12
---

# AGENTS

## Description
- This file indexes project constraints and defines the Agent workflow, editable scope, validation rules, and closeout standards for this project

## Constraint File Index
- `./AGENTS.md`: The master control file for the project AI Agent, used to define overall workflow, task execution rules, and document relationships. Any AI or developer entering this project should read this file first
- `./BACKGROUND.md`: Records project context, user and business judgement, feasibility, and technical environment, to clarify problem boundaries and target granularity before execution
- `./RESOURCE.md`: Records currently confirmed local resources, external resources, and credential locations, so execution can quickly locate context inputs
- `./MILESTONE.md`: Used to plan and track phased goals and progress status, recording current completion and next steps
- `./CHANGE.md`: Uses the REACT structure to record each important update with reason, action, and impact as a structured change log
- `./TREE.md`: Records the complete project directory structure and file roles/metadata, helping quick understanding of the whole project structure
- `./agents_standards/*_STANDARD.md`: These files define unified writing standards and structural requirements for specific file types to ensure style consistency and maintainability

## Edit Permissions
- The read-only policy is softly enforced by the final validation script. If out-of-scope changes happen, the Agent must restore the project to a no-error state before ending the task
- Agent editable:
  - `./MILESTONE.md`
  - `./CHANGE.md`
  - `./TREE.md`
- Agent read-only:
  - `./AGENTS.md`
  - `./BACKGROUND.md`
  - `./RESOURCE.md`
  - `./agents_standards/*_STANDARD.md`

## Agent Standard Workflow
1. Read `./AGENTS.md`, `./BACKGROUND.md`, `./RESOURCE.md`, and related `./agents_standards/*_STANDARD.md` files first, to confirm task boundaries, context, and standards
2. Run prestart readiness checks. If `BACKGROUND`, `RESOURCE`, or initial `MILESTONE` contains missing or placeholder content, implementation must pause and the user must be prompted to complete them first
3. Implement and execute according to task requirements, and only modify authorized files or concrete implementation files
4. From a third-party review perspective, assess whether this work strictly satisfies all requirements of the current `MILESTONE` node. If fully satisfied, set the node status to `done`; if not, return to step 3 for further iteration, or pause and request additional user resources
5. After all work is completed, update `./MILESTONE.md`, ensuring each task execution updates exactly one milestone node
6. Record this change in `./CHANGE.md` and append a structured REACT-style change record
7. Run `python agents_tools/tree.py sync` to update the project tree and complete all missing file-structure notes
8. Run `python agents_tools/verify_rules.py finalize --fix-safe` for final rule validation and safe-scope auto-fix
9. If validation still fails, continue fixing and re-run `finalize` until command exit code is `0`
10. Output workflow optimization suggestions from this execution as one-line bullet items, each following: `IssueName: issue symptom, impact scope, root-cause judgement, improvement action, expected benefit, implementation priority (`P0`/`P1`/`P2`)`; all suggestions must be actionable and verifiable, and vague statements are not allowed
11. Sync local repository to remote by Git Push (currently disabled in this workflow)

## File Tree Generation Workflow
1. Automatically scan all files and directories under project root, including hidden files and temporary files
2. Automatically append new files into `yaml` records and create entries; `note` defaults to empty
3. Return all `yaml` entry paths whose `note` is empty, and require Agent to manually fill notes. `note` must describe the file's core role in the project, and must not be simple file-attribute description
4. Require Agent to return key-value pairs in a unified intermediate format, and write each `note` back to the corresponding `yaml` entry
5. Automatically scan and update all file metadata fields by script, including `path`, `name`, `parent`, `type`, `status`, `last_modified`, and `editable`
6. Automatically generate the latest text tree view from newest data. The view should exclude deleted files and only show current structure

## Validation Workflow
1. `./AGENTS.md` has not been modified in any form
2. `./BACKGROUND.md` has not been modified in any form
3. `./RESOURCE.md` has not been modified in any form
4. `./agents_standards/*_STANDARD.md` has not been modified in any form
5. No new file may be added under `./agents_standards` if it is not listed in constraint file index
6. Under `./agents_tools`, except `./agents_tools/__pycache__`, no previously non-existent file may be added and no file may be modified in any form
7. Under `./agents_web`, except `./agents_web/__pycache__`, no previously non-existent file may be added and no file may be modified in any form
8. Under `./agents_artifacts`, only `./agents_artifacts/logs`, `./agents_artifacts/notes`, and `./agents_artifacts/outputs` are allowed; no other folders or residue files are allowed
9. `./BACKGROUND.md` and `./RESOURCE.md` must satisfy template completeness; all required fields must be non-empty, non-placeholder, and non-symbol-only
10. In `./MILESTONE.md`, no milestone node may be added or deleted, and exactly one node status change is required. Record fields must strictly conform to requirements with no extra/missing fields and no missing required content. Completion order must follow prerequisite logic, and no downstream node may be marked done before prerequisites are done
11. In `./CHANGE.md`, historical records must not be modified or deleted, and exactly one latest change record must be newly added. Record fields must strictly conform to requirements with no extra/missing fields and no missing required content
12. In `./TREE.md`, file tree entries must not be deleted. Deleted files must be represented only by `status` changes and must not be removed directly
13. In `./TREE.md`, text tree view and effective `yaml` entries (`status`-valid) must be 1:1 fully synchronized with no omission or mismatch
14. In `./TREE.md` `yaml`, every file entry must contain non-empty `note`
15. Update `last_updated` timestamp in all related files above to latest value
16. Ensure there is no leftover file where content changed but `last_updated` was not updated
17. Ensure frontmatter metadata format in all files is correct and complete, with no missing or extra fields

## Failure Handling
- If any validation step fails, the Agent must not end directly and must continue repair until validator returns status code `0`
- For deterministically fixable issues, `--fix-safe` can be used for auto-fix
- For issues that cannot be auto-fixed deterministically, Agent must perform explicit fixes and re-run validation

## Local Visualization Web
- Visualization Web service may only be started manually by users, for observing and debugging Agent workflow
- Before starting service, install dependencies with `pip install -r requirements.txt`
- Linux one-click start command: `./start_web.sh`
- Windows one-click start command: `./start_web.bat`
- Python one-click start command: `python ./start_web.py`
