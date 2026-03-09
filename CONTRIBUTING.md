# Contributing

## Scope

Contribute inside one workspace at a time:

- `AAAAAAGENTS.MD.CN/` for Chinese content and behavior
- `AAAAAAGENTS.MD.EN/` for English content and behavior

Keep the folder structure 1:1 between CN and EN.

## Basic Rules

1. Keep file paths aligned between CN and EN.
2. Keep runtime behavior aligned between CN and EN.
3. Keep user-facing language separated:
   - CN uses Chinese
   - EN uses English only
4. Update docs and scripts together when changing workflows.

## Validation

Before pushing changes, run checks in the workspace you modified:

```bash
python agents_tools/tree.py sync
python agents_tools/baseline_refresh.py
python agents_tools/verify_rules.py finalize --json
```

Then verify EN contains no Chinese characters and CN/EN structures remain aligned.
