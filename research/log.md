# Research Log

One entry per run, newest at the top. Written by the researcher agent.

Entry template:

```
## YYYY-MM-DD · R-XXX · <short title>
**Outcome:** done | partial | blocked
**Summary:** what was done, in 2–4 sentences.
**Proposal:** research/proposals/<file>.md (if any)
**Sources consulted:** URLs
**Open questions for human:** list, or "none"
**Suggested new backlog items:** list, or "none"
```

---

## 2026-11-23 · R-012 · Nord Pool spelling in Market Platform (human decisions)
**Outcome:** done
**Summary:** Applied by the main session on the human's instruction. MARKET_INFO `Market Platform` for IDs 062-065 changed from `Nordpool` to `Nord Pool` (4 cells, logged in research/change_log.csv). The human also decided that duplicate market names (e.g. 092/093 `Scheduled Utilisation (SU)`) are acceptable until Phase 3 (R-001 Change 12).
**Proposal:** n/a (follow-up to research/proposals/2026-11-23-R-001-database-structure-review.md)
**Sources consulted:** https://www.nordpoolgroup.com/
**Open questions for human:** none
**Suggested new backlog items:** none

## 2026-11-23 · R-007 · Apply R-001 Phase 1
**Outcome:** done
**Summary:** The human approved Phase 1, and this run applied it. Before any edit, the six CSVs were backed up to `research/backups/2026-11-23-pre-phase1/` and SHA-256 hashes confirmed identical copies.
- **Change 1:** `ID` (text `001`-`112`) was added as the first column of the five child files using the positional mapping. The blank `Capacity Market` row was split into 029/030, and `Distributed Restart` was renamed `Distributed ReStart`.
- **Change 2:** header typos were fixed, and KEY_DATA `Notes` became `Contract Length Band`, with a new empty `Notes` column.
- **Change 3:** the name typos were fixed. ID 103 got a spelling fix only. The DESCRIPTION typos `Epiry`/`minushed` were also fixed.
- **Change 4:** `Pay-as-Clear`, `GBP/MW/h` and `Nord Pool` (KEY_DATA operator) were applied.

A verification script passed. All six files have IDs 001-112 (112 rows, unique, same order), and Market Name matches KEY_DATA for every ID. The files are still UTF-8 with BOM and CRLF line endings. A diff against the backup shows only the intended changes. 95 rows were logged in `research/change_log.csv`.
**Proposal:** research/proposals/2026-11-23-R-001-database-structure-review.md (Phase 1 marked approved and applied; Phases 2-4 pending)
**Sources consulted:** https://www.nordpoolgroup.com/ ; https://www.iso.org/iso-4217-currency-codes.html ; https://www.iberdrola.com/press-room/news/detail/sp-electricity-north-west-unveiled-new-name-visual-identity-part-iberdrola-group ; https://www.enwl.co.uk/about-us/ ; https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/monthly-tender/itt111546---sp-enw-flexibility-services-monthly-tenders-2026---appendix-2---technical-specification.pdf (password-protected, not read)
**Open questions for human:** R-001 Questions 2-7 are still open. Should `Nordpool` in `MARKET_INFO.Market Platform` (IDs 062-065) also become `Nord Pool`? (logged as R-012). Note that ID 092 now has the same name as 093 (both SPEN); they are told apart by `Contract Length Band`.
**Suggested new backlog items:** R-011 confirm the ID 103 SPENW product name; R-012 `Nordpool` in Market Platform.

## 2026-11-23 · R-001 · Review database structure
**Outcome:** done
**Summary:** Profiled every column of the six CSVs. `Market Name` is not a unique key: 4 names are duplicated, and they can only be told apart by KEY_DATA `Notes`. The 112 vs 111 mismatch comes from KEY_DATA splitting `Capacity Market` into T-1/T-4 (IDs 029/030) while the other files have one blank `Capacity Market` row, plus a `Distributed ReStart`/`Restart` case mismatch. Row order otherwise matches, so IDs can be back-filled by position. MARKET_INFO has 7 fully blank columns and the child tables are 83-99% blank. The proposal has four phases: (1) ID key and typo fixes; (2) lookups, SOURCES/CITATIONS, review status and CHANGE_LOG; (3) long-format restructure (order types, eligibility, procurement windows); (4) a mechanism supertype with INSTRUMENT/SCHEME/CHARGE subtype tables, relationships and time-varying parameters for CfD, CM, futures, UoS charges and carbon taxes.
**Proposal:** research/proposals/2026-11-23-R-001-database-structure-review.md
**Sources consulted:** https://www.w3.org/TR/tabular-data-primer/ ; https://www.w3.org/TR/tabular-metadata/ ; https://datapackage.org/standard/table-schema/ ; https://www.rfc-editor.org/rfc/rfc4180 ; https://www.ice.com/products/20788778/UK-Base-Electricity-Future-Gregorian ; https://www.iberdrola.com/press-room/news/detail/sp-electricity-north-west-unveiled-new-name-visual-identity-part-iberdrola-group ; https://www.enwl.co.uk/about-us/ ; https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf (403, not read) ; https://www.emrdeliverybody.com/ ; https://www.lowcarboncontracts.uk/
**Open questions for human:** (1) approve Phase 1 ID back-fill and typo fixes; (2) rename "market" to "mechanism"; (3) snake_case headers plus data dictionary, or keep human headers; (4) product-family rows with child tables for DSO windows, CM/CfD rounds and futures tenors; (5) field-level vs record-level citations; (6) CSV-only vs a SQLite build, and whether to keep the BOM; (7) GB-only, or include SEM-GB/interconnector products.
**Suggested new backlog items:** R-007 apply Phase 1; R-008 ENA DSO product taxonomy; R-009 lookups and ORGANISATIONS; R-010 datapackage.json and validator. Data-quality findings were added to the proposal for R-005.

