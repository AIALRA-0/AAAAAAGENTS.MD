---
last_updated: 2026-03-12-07-06
---

# MILESTONE

## TEMPLATE
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
- updated_at: YYYY-MM-DD-HH-MM

## DATA
### MS-INIT-001
- id: MS-INIT-001
- title: Initialize common project skeleton
- prerequisites: []
- postnodes: []
- why:
  - Establish unified AGENTS collaboration rules and core engineering structure so all participants work under one standard
  - Reduce execution deviations caused by different process interpretations when future tasks or modules are added
  - Make key project rules traceable and automatically verifiable with clear auditability
  - Use script-based checks to reduce hidden risks from verbal process agreements
  - Provide a stable and compatible initialization baseline for future standard-file and module expansion
- what:
  - Build minimum usable templates for AGENTS, BACKGROUND, MILESTONE, CHANGE, and TREE
  - Connect tree, baseline_refresh, and verify_rules into one complete execution chain
  - Deliver basic local dashboard capabilities for document read, edit, save, and preview
  - Establish auto-indexing of project structure so TREE stays synchronized with the real file system
  - Initialize the first project baseline and final-check state file for subsequent validation
- how:
  - Define field structures from constraint templates first, then fill minimum executable sample data
  - Run tree sync to generate TREE and record the current directory structure
  - Run baseline_refresh to generate baseline for future change comparison
  - Verify read/edit/save/preview workflow on the dashboard end to end
  - Run finalize for rules validation and auto-fix all safely fixable issues
  - Replay the full initialization workflow and record results in CHANGE
- verify:
  - Running python agents_tools/tree.py sync succeeds without errors
  - Running python agents_tools/baseline_refresh.py returns status=ok
  - Running python agents_tools/verify_rules.py finalize --json returns status=ok
  - The dashboard can correctly load and display MILESTONE, CHANGE, and TREE
  - Newly added TREE nodes all have non-empty note fields and stay consistent with actual structure
- status: done
- notes:
  - This milestone is only for completing common project initialization
  - Before adding new milestones, confirm template fields stay aligned with validation logic
  - If read-only constraint files are changed, run baseline_refresh first to refresh baseline
  - After initialization, new business milestones can be extended from this node
  - This node serves as the reference starting point for later graph rendering and rule validation
- updated_at: 2026-03-08-23-17

## LAYOUT
- positions: []
