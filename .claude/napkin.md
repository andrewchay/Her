# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Execution & Validation (Highest Priority)
1. **[2026-03-15] Verify implementation against narrative docs**
   Do instead: inspect `.her/`, `cli.py`, and tests before trusting README or `CLAUDE.md` about shipped capabilities.

2. **[2026-03-15] Distinguish demo readiness from product readiness**
   Do instead: treat passing `python3 cli.py her-test` as proof the meta-cognition scaffold works, not proof that relationship features exist.

## Shell & Command Reliability
1. **[2026-03-15] Hidden files contain most of the real logic**
   Do instead: use `rg --files --hidden .her src tests experiments` when surveying the repo.

## Domain Behavior Guardrails
1. **[2026-03-15] Project story has outrun implementation**
   Do instead: frame analysis around the gap between the romance vision and the still meta-cognitive codebase.

## User Directives
1. **[2026-03-15] Keep explanations grounded and kind**
   Do instead: explain why the project is not dating yet with concrete repo evidence, not just playful metaphor.
