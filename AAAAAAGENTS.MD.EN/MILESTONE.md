---
last_updated: 2026-03-08-23-17
---

# MILESTONE

## TEMPLATE
```yaml
{
  "milestones": [
    {
      "id": "MS-TYPE-NUM",
      "title": "Milestone title",
      "prerequisites": [],
      "postnodes": [],
      "why": [
        "Why do 1",
        "Why do 2",
        ......
      ],
      "what": [
        "What to do1",
        "What to do 2",
        ......
      ],
      "how": [
        "How to do 1",
        "How to do 2",
        ......
      ],
      "verify": [
        "How to verify 1",
        "How to verify 2",
        ......
      ],
      "ddl": "YYYY-MM-DD",
      "status": "unfinished",
      "notes": [
        "Supplementary Note 1",
        "Supplementary Note 2",
        ......
      ],
      "updated_at": "YYYY-MM-DD-HH-MM"
    }
  ],
  "layout": {
    "positions": {}
  }
}
```

## DATA
```yaml
{
  "milestones": [
    {
      "id": "MS-INIT-001",
      "title": "Initialize common project skeleton",
      "prerequisites": [],
      "postnodes": [],
      "why": [
        "Establish unified AGENTS collaboration rules and basic engineering structures to allow all participants to work under the same specifications",
        "Reduce execution deviations caused by different process understandings when new tasks or modules are added in the future, and reduce collaboration friction",
        "Let the key rules of the project be traced, automatically verified, and have clear audit capabilities",
        "Automatically check project status through scripting tools to reduce the hidden risks caused by relying on verbal agreements",
        "Provide a stable and compatible initialization basis for subsequent expansion of new standard files or modules"
      ],
      "what": [
        "Create the minimum available template for five types of core documents AGENTS, BACKGROUND, MILESTONE, CHANGE, and TREE",
        "Open up the three core scripts of tree, baseline_refresh and verify_rules to form a complete execution process",
        "Realize the basic capabilities of the local visual workbench and support document reading, editing, saving and previewing",
        "Establish an automatic indexing mechanism for the project directory structure and file tree to ensure that TREE files are synchronized with the real directory",
        "Initialize the first baseline file and final inspection status file of the project to provide a reference for subsequent verification"
      ],
      "how": [
        "First define various document field structures according to the constraint template, and then fill in the minimum executable sample data",
        "Execute tree sync to generate the project TREE file and record the current directory structure",
        "Execute baseline_refresh to generate a project baseline for comparison of future changes",
        "Test whether the document reading, editing, saving and preview processes are complete and available on the visualization page",
        "Run finalize to perform rule verification and automatically fix all fixable problems",
        "Play back the complete initialization process and record the results of the initialization phase into the CHANGE file"
      ],
      "verify": [
        "After running python agents_tools/tree.py sync, the script was executed successfully and no error was reported",
        "Return status=ok" after running python agents_tools/baseline_refresh.py,
        "Run python agents_tools/verify_rules.py finalize --json and return status=ok",
        "The visual page can correctly load and display the three core documents MILESTONE, CHANGE and TREE",
        "All new nodes in the TREE file contain non-empty note fields, and the structure is consistent with the real directory"
      ],
      "ddl": "2026-03-10",
      "status": "done",
      "notes": [
        "The current milestone is only used to complete the general project initialization phase",
        "Before adding a new milestone, you need to confirm that the template fields are consistent with the rule verification logic",
        "If you modify the read-only constraint file, you need to execute baseline_refresh first to update the baseline",
        "After the initialization is completed, you can continue to expand new business milestones based on this node",
        "This node will serve as a reference starting point for subsequent flow chart generation and rule verification"
      ],
      "updated_at": "2026-03-08-23-17"
    }
  ],
  "layout": {
    "positions": {}
  }
}
```
