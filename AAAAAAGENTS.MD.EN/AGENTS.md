---
last_updated: 2026-03-08-16-20
---

# AGENTS

## illustrate
- This file is used to index project constraints,Regulation Agent The execution process in this project,Editable range,Verification rules and closing standards

## constrained file index
- `./AGENTS.md`: This is for the entire project AI Agent master control file,Used to illustrate the overall workflow,Task execution rules and relationships between documents,if a AI Or a developer enters the project,The first step should be to read this file
- `./BACKGROUND.md`: This file records background information about the project,technical environment,Use tools and related resources and access information,Help anyone taking over the project quickly understand the project context
- `./MILESTONE.md`: This file is used to plan and track the project's phased goals and progress status.,Record current completion status and next steps plans
- `./CHANGE.md`: This file is used to REACT Structure records every important update and reason for modification,Content and impact,As a structured change log for the project
- `./TREE.md`: This file records The complete directory structure of the project and the purpose or meta-information of each file,Used to help quickly understand the overall structure of the project
- `./agents_standards/PYTHON_STANDARD.md`: This file defines the project Python Unified coding standards and structural requirements for code,To ensure that the code style is consistent and easy to maintain
- `./agents_standards/MARKDOWN_STANDARD.md`: This file defines the project Markdown Unified format and writing standards for documents,To ensure that all documents have a clear structure and consistent style

## Edit permissions
- The read-only policy is executed through soft constraints of the closing verification script.,Modify if out of bounds,Agent The task must be restored to the error-free state before the task can be ended.
- Agent Editable:
  - `./MILESTONE.md`
  - `./CHANGE.md`
  - `./TREE.md`
- Agent read only:
  - `./AGENTS.md`
  - `./BACKGROUND.md`
  - `./agents_standards/PYTHON_STANDARD.md`
  - `./agents_standards/MARKDOWN_STANDARD.md`

## Agent Standard workflow
1. read first `./AGENTS.md`,`./BACKGROUND.md` and related `./agents_standards/*_STANDARD.md` document,To confirm the task boundaries of the project,Contextual information and specifications to follow
2. Implement according to task requirements,And only authorized files or specific code implementation files are allowed to be modified.
3. Update after completing the task `./MILESTONE.md`,Ensure that each task only executes and updates one milestone node
4. exist `./CHANGE.md` Record this modification in,and followREACT Structure adds structured change records
5. execute command `python agents_tools/tree.py sync`,Update project file tree,And fill in all missing project file structure information
6. execute command `python agents_tools/verify_rules.py finalize --fix-safe` Final rule verification of the project,and automatically perform safe-scope repairs
7. If the verification still reports an error,then continue to fix the problem and repeat `finalize`,Until the command returns status code `0` until
8. by executing Git Push Synchronize local projects to remote repository(This step is disabled in the current process)
9. Output process optimization suggestions during this execution

## File tree generation process
1. Automatically scan all files and directories under the project root directory,Includes hidden files and temporary files
2. Automatically add new scanned files to `yaml` Recording,and create an entry for it,in `note` Fields are left blank by default
3. return to Agent all `note` is empty `yaml` Entry file path,and request Agent Add manual comments to these files, `note` The information that needs to be filled in is the core description of the file's role in the project.,prohibit `note` Simply fill in the file meta-attribute related information
4. Require Agent Return key-value pairs in a unified intermediate format,And based on these key-value pairs, the corresponding `note` Content is written to the corresponding file `yaml` Record
5. Automatically scan and update meta information fields of all files using scripts,include `path`,`name`,`parent`,`type`,`status`,`last_modified` and `editable` and other parameters
6. Automatically generate the current project based on the latest datatext file tree view,This view does not need to show deleted files,Only display the latest file structure

## Verification process
1. `./AGENTS.md` has not been modified in any way
2. `./BACKGROUND.md` has not been modified in any way
3. `./agents_standards/*_STANDARD.md` has not been modified in any way
4. `./agents_standards` No files may be added to the directory that do not exist in the constrained file index
5. `./agents_tools` in directory,Apart from`./agents_tools/__pycache__`Inside,No new files may be added that do not previously exist,and no files have been modified in any way
6. `./agents_web` in directory,Apart from`./agents_web/__pycache__`Inside,No new files may be added that do not previously exist,and no files have been modified in any way
7. `./agents_artifacts` in directory,only`./agents_artifacts/logs`,`./agents_artifacts/notes`,`./agents_artifacts/outputs`three subdirectories,No other folders or residual files should appear
8. `./MILESTONE.md` No milestone nodes may be added or deleted from,And there must and can only be one milestone node that changes state.,The fields of the change record must strictly meet the requirements,not more,No less,Cannot leave blank content,And the completion order of all nodes must comply with the established logical order.,No subsequent node shall be marked complete before its predecessor has completed
9. `./CHANGE.md` Historical change records in may not be modified or deleted,And only one latest change record must be added,The fields of the change record must strictly meet the requirements,not more,No less,Cannot leave blank content
10. `./TREE.md` File tree entries in must not be deleted,For deleted files one must pass only `status` Field record status changes,rather than removing items directly
11. `./TREE.md` file tree intextview with `yaml` middle`status`Valid entries must correspond one to one and be fully synchronized,There must be no gaps or inconsistencies
12. `./TREE.md` middle `yaml` Each file entry must contain `note` Field,and the field must not be empty
13. Update all relevant documents above `last_updated` The parameter is the latest timestamp
14. Check to make sure there are no files whose contents have been modified but not updated `last_updated` Wrong file residue with timestamp
15. Check that the metadata format of all file headers must be correct and complete,There must be no missing or redundant fields

## Failure handling
- When any verification step fails,Agent Do not end the task directly,Repair process must continue,Until the verification script returns the status code `0` until
- For issues that can be fixed,Can be used `--fix-safe` Parameter execution automatic repair
- For issues where a fix cannot be determined automatically,must be Agent Make an explicit repair,And perform verification again after repairing

## local visualization Web
- Visualization Web Services are only allowed to be started manually by the user,Used to assist user observation and debugging Agent workflow
- before starting the service,Need to install dependencies first `pip install -r requirements.txt`
- Linux The command to start the local service with one click is `./start_web.sh`
- Windows The command to start the local service with one click is `./start_web.bat`
- Python The command to start the local service with one click is `python ./start_web.py`
