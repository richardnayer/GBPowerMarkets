# Research Backlog

The researcher agent works through this queue top to bottom, one item per run.
Humans can add, reorder or remove items at any time.

**Status key:** `[ ]` open · `[~]` in progress · `[?]` blocked / needs human input · `[x]` done

**Priority:** P1 (do next) · P2 · P3

**Model:** researcher runs use Sonnet by default (set in `.claude/agents/gb-markets-researcher.md`). Items tagged **(opus)** redesign the database structure and are launched on Opus. Add or remove the tag to change this.

---

## Open

- [ ] **P2 · R-031 · Schema entries for R-020's tables.** When R-020 is applied, add resources to `CSV/datapackage.json` for LK_PLATFORM, LK_PRICING_RULE, LK_AUCTION_TYPE, LK_AGGREGATION_LEVEL, LK_SETTLEMENT_TYPE, the role lookup and MECHANISM_ORG_ROLE. Replace the plain-text typing of each converted column with a foreign key. Do it in the same commit as the R-020 apply step: validator check P2 fails on any CSV that is not declared.
- [ ] **P3 · R-032 · Lookups for the remaining coded columns, and the publisher foreign key.** R-010 D5/D6.
  - Draft sourced lookups for SOURCES `source_type` and `doc_type`, and for the LK_DSO_PRODUCT_VARIANT columns `product_fit`, `payment_structure`, `availability_refinement` and `utilisation_instruction_timing` (FMR-PD Table 3).
  - Make SOURCES `publisher` a strict foreign key: add Companies House to ORGANISATIONS (it needs a sourced `org_type`), and allow a blank publisher only for `internal` sources (SRC-0042).
- [ ] **P2 · R-033 · Machine-readable citations for the R-009 facts.** Validator X9 found 9 sources that no foreign key reaches.
  - SRC-0030 and SRC-0043..0045 are cited only in `research/drafts/R-009/KEY_DATA_DSO_COLUMNS.csv`, which gives a source and locator for each KEY_DATA `Standard Variant` value.
  - SRC-0004, 0018, 0023, 0039 and 0040 are cited only in ORGANISATIONS `notes`.

  Move both sets into CITATIONS once R-023 creates it.
- [ ] **P2 · R-018 · SQLite build with readable views.** A stdlib `sqlite3` script that loads the CSVs into a SQLite file with foreign keys enforced, so the build fails on a broken reference. Add views that join the tables back into readable wide form. Output goes to a git-ignored build folder; the CSVs stay the master copy. Decided in R-001 Question 6. Use the schema from R-010.
- [ ] **P3 · R-024 · Instrument settlement type and clearing houses.** Moved out of R-020 (its D12): no current column uses these; they belong to Phase 4 `INSTRUMENT_INFO`.
  - Draft `LK_SETTLEMENT_TYPE`: ICE physical via ECVN (SRC-0010), EEX cash or physical fulfilment (SRC-0009), OTC physical / financial (SRC-0041 para 2.13).
  - Add a `clearing_house` role (LK_ORG_ROLE) with rows for MEC-0035..0056. Add ICE Clear Europe Limited (Companies House 06219884, read in R-020) and European Commodity Clearing AG to ORGANISATIONS, each with a source that names it as the clearing house for these contracts.
  - Revisit Direction and Dispatcher `not_applicable` for the physically delivered ICE contracts (MEC-0035..0039).
- [ ] **P3 · R-026 · SEM-GB intraday auctions (MEC-0064/0065): algorithm, objective, pricing.** R-020 found no primary source on whether the SEM-GB IDAs still clear with EUPHEMIA after GB left SDAC:
  - Nord Pool's SEM-GB article (SRC-0060) names no algorithm.
  - The EUPHEMIA description (SRC-0054) does not mention GB.
  - SEMOpx's pages and two Ofgem 2019 decisions do not mention it either.

  Read the SEMOpx intraday auction rules or market rules, or a Nord Pool/EPEX SEM-GB rulebook. Then confirm or correct `Clearing Algorithm` = `euphemia`, fill MEC-0065 `Market Objective` (cleared from `Nor`), and check the Nord Pool GB auctions' objective (MEC-0062/0063).
- [ ] **P3 · R-027 · Verify carried-over EAC values for MEC-0007 (MFR LFSM) and MEC-0009 (Static FFR).**
  - MEC-0007's MARKET_INFO values (platform, pricing, auction type, structure, objective) look copied down from the EAC rows (R-001 data-quality list). MFR is a Grid Code requirement, not an EAC product.
  - MEC-0009: the SMP is confirmed (SRC-0050), but EAC is not. SRC-0039 does not list Static FFR, and its rules name only a "Designated Auction Platform".

  Check NESO's MFR and Static FFR pages and documents, and propose corrections to the flagged R-020 role and mapping rows.
- [ ] **P3 · R-019 · Publication readiness.** The dataset will be published, and later used for an open-source lookup website. Research and draft: a data licence (e.g. CC BY 4.0 or ODbL; the repo's MIT licence covers code only); the reuse terms of the main sources (Open Government Licence, NESO, Elexon, DNOs); a `README.md` (the current `README.me` is empty and misnamed); `CITATION.cff`; a data dictionary; versioned releases with a Zenodo DOI. Choosing the licence is the human's decision.
- [ ] **P2 · R-002 · Scope gap: government mechanisms.** No CfD or Capacity Market entries appear in `Market Type`. Identify the missing mechanisms (CfD allocation rounds, Capacity Market T-1/T-4, RO, etc.) and draft rows. _R-009: the classes `certificate_scheme`, the commodity `emissions_allowance` and the category `decarbonisation` are reserved in R-001 Change 6. Add them to the lookups, with sourced definitions, when the rows need them._
- [ ] **P2 · R-003 · Scope gap: system charges and taxes.** Identify charges and taxes that enable the system (TNUoS, BSUoS, DUoS, CCL, UK ETS, Carbon Price Support, etc.) and propose how to represent them (they may not fit the current "market" columns). _R-009: the reserved codes `network_charge`, `system_charge`, `policy_levy`, `tax`, `emissions_trading` (class) and `network_cost_recovery`, `decarbonisation` (category) need sourced definitions when added. ORG-0022..ORG-0035 (DNO licensees) are ready for DUoS rows._ _Human (2026-11-23): make sure `LK_MECHANISM_CLASS` covers these mechanisms, e.g. BSUoS → `system_charge`, TNUoS/DUoS → `network_charge`, Carbon Price Support and CCL → `tax`, UK ETS → `emissions_trading`, policy cost levies → `policy_levy`. Check `LK_CATEGORY` too: BSUoS recovers balancing costs, which `network_cost_recovery` does not describe. Charge attributes go in Phase 4 CHARGE_INFO (R-001 Change 13)._
- [ ] **P2 · R-004 · Fill DESCRIPTION summaries.** `DESCRIPTION.csv` summary paragraphs and references are largely blank. Draft sourced summaries, in batches of about 10 markets per run.
- [ ] **P3 · R-005 · Data-quality sweep.** Find blank cells, uncertain values (e.g. "No?"), inconsistent units and mismatched market names across files.
- [ ] **P3 · R-006 · Verify Live/Status values.** Check that each market's `Status` is current against primary sources. Start with the doubtful DSO statuses listed in R-008 Change 6. _Added by R-009: MEC-0019 LCM (NESO says the Demand Flexibility Service replaces it from 7 Oct 2026); MEC-0023 Y-4 Stability Market (NESO launched its first long-term tender in 2025, so it may not be `Planned`); MEC-0021 short-term reactive market (not mentioned on NESO's reactive power page). Record a `status_as_of` date for each._
- [ ] **P3 · R-011 · Confirm ID 103 SPENW product name.** Check whether `Variable Availability Operational + 2 mins` should read `Variable Availability Operational Utilisation + 2 mins` (and whether a 2-minute variant exists). Use SPENW tender documents: the ITT 111546 technical specification (password-protected PDF) at https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/monthly-tender/itt111546---sp-enw-flexibility-services-monthly-tenders-2026---appendix-2---technical-specification.pdf, or Service Terms v3.2. _Note from R-008 (2026-11-23): primary-source evidence already found. SP ENW's April 2026 Procurement Statement (PDF p.11) says VA+OU response times are "either two (2) or fifteen (15) minutes", and Elexon FMR-PD v4.2 defines variant `VA OU-2`. See research/proposals/2026-11-23-R-008-dso-product-taxonomy.md. This item can probably close with those citations._
- [ ] **P2 · R-014 · Elexon Flexibility Market Catalogue as a DSO source.** The catalogue (https://www.elexon.co.uk/flexibility-markets/implementation-monitoring/flexibility-market-catalogue/) lists every GB flexibility sub-market with its FMR-SMD parameters, but it is a Power BI embed that automated fetches cannot read. _Human input 2026-11-23: the DSO rows were taken from this catalogue, and it has no data-export option._ Look for another route (a downloadable version elsewhere on Elexon's site, or Elexon's sub-market registration documents). Failing that, ask the human to read the few specific entries by eye. Use it to (a) confirm NPg IDs 076, 083 and 084, (b) find the original source of the DSO rows, and (c) fill sub-market parameters (platform, contract length, instruction trigger).
- [ ] **P2 · R-015 · Fill DSO MARKET_INFO/TECHNICAL fields from FMR-PD.** Elexon FMR-PD v4.2 Table 3 gives, for each standard variant: payment structure, availability and utilisation payment units (GBP/MW/h, GBP/MWh), max response time (2 or 15 min), minimum utilisation time (30 min) and instruction timing. Draft sourced values for the 41 standard-mapped DSO rows. _R-008 approved 2026-11-23. Use the KEY_DATA `Standard Variant` codes and `LK_DSO_PRODUCT_VARIANT` (R-021)._
- [ ] **P3 · R-013 · Verify DSO `Direction` values.** All 46 DSO rows say `Up/Down`. Most DSO sub-markets are demand turn-down / generation turn-up (DTD/GTU) only. FMR-SMD and NGED split DTD/GTU from DTU/GTD (e.g. NGED `SU_HV_DTUGTD`, `SAOU_DA_DTUGTD`). Check each row against the DNO's own statement.
- [ ] **P3 · R-016 · DSO coverage gaps.** Products found in 2026/27 DNO statements but missing from the CSV: SSEN "Legacy-Secure" and the LMA Interim Payment service; NGED `SU_SPP`/`SU_SEP`, DTU variants and FlexUp; SPEN's day-ahead DTU at the B6 boundary. Decide which to add as rows (or as windows, under R-001 Question 4).
- [ ] **P2 · R-023 · Phase 2 governance tables.** Draft the rest of R-001 Phase 2, which is approved:
  - `CITATIONS` (Change 5), with `CIT-NNNNNN` IDs;
  - record-level `record_status`, `last_verified_date`, `last_verified_by` and a `confidence` field (Changes 7-8);
  - `CHANGE_LOG` with `CHG-NNNNNN` IDs (Change 8), including how to migrate `research/change_log.csv`.

  Then move the R-021 qualifier notes into their proper place, e.g. the low-confidence `Suppliers = no` for MEC-0001..0006 (PARTICIPANTS `Notes`).
- [ ] **P3 · R-022 · (opus) · Contract length: band, min/max or yes/no per duration?** Human request (2026-11-23). `LK_CONTRACT_LENGTH_BAND` now holds min/max ISO 8601 durations. As research covers more markets, review whether contract length is better recorded as yes/no for set durations (e.g. day / week / month / year / multi-year), or as actual lengths on `SUB_MARKET` rows (R-001 Change 12), from which the bands and yes/no flags could be derived. Revisit after R-002 (CM/CfD agreements run for years) and when Phase 3 is designed.

## Blocked / needs human input

- [?] **P3 · R-034 · Install the pre-commit hook (human action).** The human chose not to install it yet (2026-11-23). When ready, run `git config core.hooksPath scripts/hooks` from the repository root; to undo it, run `git config --unset core.hooksPath`. Until then, run `python scripts/validate.py` before committing changes to `CSV/`.
- [?] **P2 · R-025 · Apply R-020 (after approval).** Blocked on the human's decisions D1-D12 in `research/proposals/2026-11-23-R-020-remaining-lookups-and-org-roles.md`.
  - Apply mechanically from `research/drafts/R-020/`: `COLUMN_ACTIONS.csv`, `VALUE_MAPPING.csv`, the `*_additions.csv` files and `EXISTING_ROW_UPDATES.csv`. Log each change in research/change_log.csv.
  - Do it in the same commit as R-031 (schema entries). Note for R-031: the tables to declare are LK_PLATFORM, LK_ORG_ROLE, LK_PRICING_RULE, LK_AUCTION_TYPE, LK_MARKET_STRUCTURE, LK_MARKET_OBJECTIVE, LK_CLEARING_ALGORITHM, LK_DISPATCHER, LK_AGGREGATION_LEVEL and MECHANISM_ORG_ROLE. LK_SETTLEMENT_TYPE has moved to R-024.
  - If D3 is approved, also remove the KEY_DATA `Market Operator` foreign key, and add the rule "platform row org_id = LK_PLATFORM.operator_org_id".
  - Run `python scripts/validate.py` before committing.

## Done

- [x] **P2 · R-020 · Remaining lookups and MECHANISM_ORG_ROLE.** _Done 2026-11-23 (pending review):_
  - _Drafts in `research/drafts/R-020/`, regenerated and machine-checked by `build/build_r020.py`:_
    - _9 lookups (LK_PLATFORM 7 rows, LK_ORG_ROLE 8, plus pricing, auction type, market structure, objective, clearing algorithm, dispatcher, aggregation);_
    - _MECHANISM_ORG_ROLE (245 rows, `MOR-` IDs);_
    - _ORG-0036..0038 (Piclo, Electron, Flexible Power), SRC-0046..0060;_
    - _VALUE_MAPPING (51 rows covering the 7 text columns and Market Operator) and COLUMN_ACTIONS._
  - _NESO's CM and CfD delivery-body role is sourced from legislation (Capacity Regulations reg 2/24, CfD Allocation Regulations reg 2, Energy Act 2013 s.8(3)/s.27(6))._
  - _GSP is GSP Group in the current NESO rules._
  - _MEC-0061 is continuous trading, so it should be pay-as-bid._
  - _The DSO platform rows come from the 2026-27 statements._
  - _EUPHEMIA for SEM-GB is unconfirmed (R-026)._
  - _Proposal: `research/proposals/2026-11-23-R-020-remaining-lookups-and-org-roles.md` (D1-D12). Follow-ups: R-024..R-027._
- [x] **P1 · R-030 · Apply R-010 decisions (after approval).** _Done 2026-11-23:_
  - _The human approved D1-D8 with D3 amended: no `.gitattributes`; instead `scripts/validate.py` check F1 accepts LF or CRLF, one style per file (mixed endings or a bare CR are still errors)._
  - _D1: the three files are committed, the hook as executable._
  - _D2, D4 and D8 are as drafted. D5/D6 go to R-032._
  - _D7: the human chose not to install the hook yet (R-034)._

- [x] **P2 · R-010 · Schema metadata and validator.** Write a `datapackage.json` (Frictionless Table Schema) declaring primary keys, foreign keys, allowed values and the ID patterns from R-001 Change 1a. Add a stdlib-only Python validator and a git pre-commit hook. Decided in R-001 Question 6. _Done 2026-11-23 (pending review):_
  - _`CSV/datapackage.json` (Data Package v2): 18 resources, 146 described fields, 42 foreign keys; allowed values are foreign keys to the lookups, not enums._
  - _`not_applicable` and `unknown` stay codes; `missingValues` is `[""]` (D2)._
  - _`scripts/validate.py` (stdlib only): passes with 0 errors and 12 warnings; tested with 29 mutation cases._
  - _`scripts/hooks/pre-commit` checks the staged copies; not installed (D7)._
  - _Finding: git stores the CSVs with LF, so CRLF holds only in Windows checkouts (D3)._
  - _Proposal: `research/proposals/2026-11-23-R-010-schema-and-validator.md`, decisions D1-D8. Follow-ups: R-030 to R-033._
- [x] **P1 · R-021 · Apply R-009 (after approval).** _Done 2026-11-23: human approved D1-D11, with D8 amended (`Standard Variant` only) and two human changes. Applied with `scripts/apply_r021.py`: 12 new tables in `CSV/` (ORGANISATIONS, SOURCES, 10 `LK_*`). KEY_DATA now has `Mechanism Class`, `Category` and `Standard Variant` in place of `Market Type`, and its coded columns and the yes/no columns hold codes. 8 columns are left as text for R-020. 141 rows in research/change_log.csv; backup in `research/backups/2026-11-23-pre-r021/`._
- [x] **P2 · R-009 · Draft lookup tables and the ORGANISATIONS table.** _Done 2026-11-23: drafts are in `research/drafts/R-009/`: ORGANISATIONS (35 rows), SOURCES (45), 10 lookups (incl. LK_DSO_STANDARD_PRODUCT 5 and LK_DSO_PRODUCT_VARIANT 17; new LK_ORG_TYPE), VALUE_MAPPING (111 rows covering every value in 27 categorical columns, machine-checked) and KEY_DATA_DSO_COLUMNS (R-008 Change 2 in the new codes; MEC-0076 on hold). Proposal: `research/proposals/2026-11-23-R-009-lookups-and-organisations.md`, with decisions D1-D11. Remaining lookups and MECHANISM_ORG_ROLE moved to R-020; applying moved to R-021._
- [x] **P1 · R-017 · Prefixed permanent IDs.** Rename mechanism IDs `001`-`112` to `MEC-0001`-`MEC-0112` in all six CSVs (R-001 Change 1a). _Done 2026-11-23: human approved; applied with `scripts/apply_mec_ids.py`; 112 mapping rows in research/change_log.csv; backup in `research/backups/2026-11-23-pre-mec-ids/`. Older proposals and logs keep the 3-digit form (`067` = `MEC-0067`)._
- [x] **P2 · R-008 · Verify the ENA Open Networks DSO product taxonomy.** Confirm the standard products (Sustain/Secure/Dynamic/Restore; SU/SAOU/VAOU/OU) from the ENA Feb 2024 alignment report (automated fetch returned 403) and map the 46 DSO rows to them. Resolve NPg tender lines that differ only by number (076/077, 082-084). _Done 2026-11-23: the ENA PDF was read via the Wayback Machine. The current standard is Elexon FMR-PD v4.2: 5 products (SU, PR, OU, SA+OU, VA+OU) with 12 variants. Sustain/Secure/Dynamic/Restore are legacy. All 46 rows mapped: 41 standard, 3 legacy (NGED 067/069/071), 2 non-standard (NPg FlexAdvance 080/081). The NPg numbers are NPg's own sub-market numbers. 076 is probably a mislabelled Sub-Market 2; 083/084 are windows or duplicates of 082 (no Sub-Markets 9/10). Proposal: `research/proposals/2026-11-23-R-008-dso-product-taxonomy.md`. Human decisions 2026-11-23: Changes 4, 5 and 7 and the `SUB_MARKET` name applied; Changes 1-2 folded into R-009; Change 3 on hold; Change 6 passed to R-006._
- [x] **P3 · R-012 · `Nordpool` in MARKET_INFO.Market Platform.** IDs 062-065 still read `Nordpool` / `Nordpool / EUPHEMIA`. Phase 1 Change 4 only covered KEY_DATA `Market Operator`. Propose `Nord Pool` (or fold this into the Phase 2 ORGANISATIONS / platform role design). _Done 2026-11-23: human approved; 062-065 changed to `Nord Pool`, logged in research/change_log.csv._
- [x] **P1 · R-007 · Apply R-001 Phase 1 (after approval).** Add `ID` to all five child CSVs using the positional mapping, split the `Capacity Market` row into T-1/T-4, and fix header and name typos. Record each change in a CHANGE_LOG. _Done 2026-11-23: applied after human approval. 95 rows logged in `research/change_log.csv`. Backup is in `research/backups/2026-11-23-pre-phase1/`. The `No?` and missing-value items are deferred to Phase 2 Change 7._

- [x] **P1 · R-001 · Review database structure.** Review the six CSV files in `CSV/` and recommend structural changes: primary keys (KEY_DATA has an `ID` column but the other files join on `Market Name`, and KEY_DATA has 112 rows vs 111 elsewhere), column naming/typos, units, controlled vocabularies, splitting/adding tables, and how to store sources/references and review status. Output a proposal only; no CSV changes until approved. _Done 2026-11-23: proposal `research/proposals/2026-11-23-R-001-database-structure-review.md` (pending review; 7 design questions)._
