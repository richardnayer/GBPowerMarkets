# Research Backlog

The researcher agent works through this queue top to bottom, one item per run.
Humans can add, reorder or remove items at any time.

**Status key:** `[ ]` open · `[~]` in progress · `[?]` blocked / needs human input · `[x]` done

**Priority:** P1 (do next) · P2 · P3

---

## Open

- [ ] **P1 · R-001 · Review database structure.** Review the six CSV files in `CSV/` and recommend structural changes: primary keys (KEY_DATA has an `ID` column but the other files join on `Market Name`, and KEY_DATA has 112 rows vs 111 elsewhere), column naming/typos, units, controlled vocabularies, splitting/adding tables, and how to store sources/references and review status. Output a proposal only; no CSV changes until approved.
- [ ] **P2 · R-002 · Scope gap: government mechanisms.** No CfD or Capacity Market entries appear in `Market Type`. Identify the missing mechanisms (CfD allocation rounds, Capacity Market T-1/T-4, RO, etc.) and draft rows.
- [ ] **P2 · R-003 · Scope gap: system charges and taxes.** Identify charges and taxes that enable the system (TNUoS, BSUoS, DUoS, CCL, UK ETS, Carbon Price Support, etc.) and propose how to represent them (they may not fit the current "market" columns).
- [ ] **P2 · R-004 · Fill DESCRIPTION summaries.** `DESCRIPTION.csv` summary paragraphs and references are largely blank. Draft sourced summaries, in batches of about 10 markets per run.
- [ ] **P3 · R-005 · Data-quality sweep.** Find blank cells, uncertain values (e.g. "No?"), inconsistent units and mismatched market names across files.
- [ ] **P3 · R-006 · Verify Live/Status values.** Check that each market's `Status` is current against primary sources.

## Blocked / needs human input

_(none)_

## Done

_(none)_
