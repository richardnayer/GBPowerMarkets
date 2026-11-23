# Proposals

Each researcher run that recommends a change to the database writes one file here, named
`YYYY-MM-DD-R-XXX-<slug>.md`. Proposals are never applied to `CSV/` until a human approves them.

## Proposal file format

```
# <title>
**Backlog item:** R-XXX
**Status:** pending review | approved | rejected | applied
**Date:** YYYY-MM-DD

## Summary
Why the change is needed.

## Changes
For each change, give the file, the key (Market Name / ID), the column, the current value, the
proposed value, and the source URL. For structural changes, give the before/after schema.

| File | Key | Column | Current | Proposed | Source |
|------|-----|--------|---------|----------|--------|

## Confidence and caveats
What is uncertain and what should be double-checked.
```

## Review

To review a proposal, set its **Status** to approved or rejected, adding notes if needed.
An approved proposal can then be applied by asking Claude (or the researcher) to apply it.
