# Research Backlog

The researcher agent works through this queue top to bottom, one item per run.
Humans can add, reorder or remove items at any time.

**Status key:** `[ ]` open · `[~]` in progress · `[?]` blocked / needs human input · `[x]` done

**Priority:** P1 (do next) · P2 · P3

---

## Open

- [ ] **P2 · R-008 · Verify the ENA Open Networks DSO product taxonomy.** Confirm the standard products (Sustain/Secure/Dynamic/Restore; SU/SAOU/VAOU/OU) from the ENA Feb 2024 alignment report (automated fetch returned 403) and map the 46 DSO rows to them. Resolve NPg tender lines that differ only by number (076/077, 082-084).
- [ ] **P2 · R-009 · Draft lookup tables and the ORGANISATIONS table.** Populate the LK_* vocabularies and ORGANISATIONS (with roles such as DESNZ/NESO EMR DB/LCCC for CfD) with a sourced definition for each code, as specified in R-001 Change 6. Depends on R-001 approval.
- [ ] **P3 · R-010 · Schema metadata and validator.** Write a `datapackage.json` (Frictionless Table Schema) or CSVW metadata declaring PKs, FKs and enums, plus a stdlib-only Python validation script. Depends on R-001 approval.
- [ ] **P2 · R-002 · Scope gap: government mechanisms.** No CfD or Capacity Market entries appear in `Market Type`. Identify the missing mechanisms (CfD allocation rounds, Capacity Market T-1/T-4, RO, etc.) and draft rows.
- [ ] **P2 · R-003 · Scope gap: system charges and taxes.** Identify charges and taxes that enable the system (TNUoS, BSUoS, DUoS, CCL, UK ETS, Carbon Price Support, etc.) and propose how to represent them (they may not fit the current "market" columns).
- [ ] **P2 · R-004 · Fill DESCRIPTION summaries.** `DESCRIPTION.csv` summary paragraphs and references are largely blank. Draft sourced summaries, in batches of about 10 markets per run.
- [ ] **P3 · R-005 · Data-quality sweep.** Find blank cells, uncertain values (e.g. "No?"), inconsistent units and mismatched market names across files.
- [ ] **P3 · R-006 · Verify Live/Status values.** Check that each market's `Status` is current against primary sources.
- [ ] **P3 · R-011 · Confirm ID 103 SPENW product name.** Check whether `Variable Availability Operational + 2 mins` should read `Variable Availability Operational Utilisation + 2 mins` (and whether a 2-minute variant exists). Use SPENW tender documents: the ITT 111546 technical specification (password-protected PDF) at https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/monthly-tender/itt111546---sp-enw-flexibility-services-monthly-tenders-2026---appendix-2---technical-specification.pdf, or Service Terms v3.2.
- [ ] **P3 · R-012 · `Nordpool` in MARKET_INFO.Market Platform.** IDs 062-065 still read `Nordpool` / `Nordpool / EUPHEMIA`. Phase 1 Change 4 only covered KEY_DATA `Market Operator`. Propose `Nord Pool` (or fold this into the Phase 2 ORGANISATIONS / platform role design).

## Blocked / needs human input

_(none)_

## Done

- [x] **P1 · R-007 · Apply R-001 Phase 1 (after approval).** Add `ID` to all five child CSVs using the positional mapping, split the `Capacity Market` row into T-1/T-4, and fix header and name typos. Record each change in a CHANGE_LOG. _Done 2026-11-23: applied after human approval. 95 rows logged in `research/change_log.csv`. Backup is in `research/backups/2026-11-23-pre-phase1/`. The `No?` and missing-value items are deferred to Phase 2 Change 7._

- [x] **P1 · R-001 · Review database structure.** Review the six CSV files in `CSV/` and recommend structural changes: primary keys (KEY_DATA has an `ID` column but the other files join on `Market Name`, and KEY_DATA has 112 rows vs 111 elsewhere), column naming/typos, units, controlled vocabularies, splitting/adding tables, and how to store sources/references and review status. Output a proposal only; no CSV changes until approved. _Done 2026-11-23: proposal `research/proposals/2026-11-23-R-001-database-structure-review.md` (pending review; 7 design questions)._
