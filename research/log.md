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

## 2026-11-23 · R-020 · Remaining lookups, LK_PLATFORM and MECHANISM_ORG_ROLE
**Outcome:** done (pending review). The run was resumed once after a usage limit.
**Summary:** Drafted in `research/drafts/R-020/` (BOM, CRLF, `csv` module). `build/build_r020.py` regenerates the drafts and fails on any coverage or reference error. `CSV/` is untouched.
- **New lookups (9):**
  - LK_PLATFORM: NESO EAC and SMP, NGED Market Gateway, Flexible Power, Piclo Flex, ElectronConnect, EPEX Localflex;
  - LK_ORG_ROLE: 8 roles; `platform` is split into market and dispatch platforms;
  - LK_PRICING_RULE, LK_AUCTION_TYPE, LK_MARKET_STRUCTURE, LK_MARKET_OBJECTIVE, LK_CLEARING_ALGORITHM (EUPHEMIA, D4), LK_DISPATCHER (operator/self/not_applicable, so the column holds no ORG IDs) and LK_AGGREGATION_LEVEL.
- **MECHANISM_ORG_ROLE:** 245 rows with `MOR-` IDs:
  - operators carried over from KEY_DATA;
  - CM and CfD NESO rows corrected to `delivery_body`;
  - 13 new DESNZ/LCCC/ESC/EMRS/Ofgem role rows;
  - 28 platform rows carried over from MARKET_INFO;
  - 94 new DSO platform rows from the 2026-27 procurement statements.
- **Additions:** ORG-0036..0038, SRC-0046..0060, org type `platform_provider`.
- **Mapping:** VALUE_MAPPING (51 rows) and COLUMN_ACTIONS. The proposal recommends dropping `Market Operator` and `Market Platform` once the role rows exist.

Findings:
- NESO's delivery-body role for the CM and CfD is now sourced from legislation.
- NESO's rules say aggregation is within a GSP Group, not a GSP.
- MEC-0061 (continuous trading) is mis-recorded as pay-as-clear.
- SPEN moved from Piclo to ElectronConnect in April 2026.

LK_SETTLEMENT_TYPE and the clearing houses moved to R-024.
**Proposal:** research/proposals/2026-11-23-R-020-remaining-lookups-and-org-roles.md
**Sources consulted:**
- NESO:
  - https://www.neso.energy/industry-information/balancing-services/enduring-auction-capability-eac
  - .../frequency-response-services/dynamic-containment
  - .../reserve-services/quick-reserve
  - .../frequency-response-services/static-firm-frequency-response-sffr
  - documents 282401, 286021, 290566, 290571, 290576, 286031, 378246, 378266, 364276, 384301, 384306, 377331 (https://www.neso.energy/document/<n>/download)
- Legislation:
  - https://www.legislation.gov.uk/uksi/2014/2043/regulation/2 and /regulation/24
  - https://www.legislation.gov.uk/ukpga/2013/32/section/8 and /section/27
  - https://www.legislation.gov.uk/uksi/2024/706/regulation/9/made and /regulation/1/made
  - https://www.legislation.gov.uk/uksi/2014/2011/regulation/2
  - https://www.legislation.gov.uk/help
- DNO statements:
  - SRC-0011..0016 URLs, re-read; NGED, SPEN and UKPN from the Ofgem ZIP
  - https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/service-documentation/flexible-power---ssen-fsp-user-guide-v1.1.pdf
- Platforms:
  - https://web.archive.org/web/20260115015058/https://www.flexiblepower.co.uk/ and https://www.flexiblepower.co.uk/about
  - https://electron.net/ and /electron-privacy-policy/
- Companies House: 09914060, 14266869, 06219884; searches for piclo, open utility, electron connect, ICE Clear Europe
- NEMO Committee:
  - https://www.nemo-committee.eu/sdac and /publications
  - euphemia-public-description-2024.pdf
  - public-description-continuous-trading-matching-algorithm-updated.pdf
- Nord Pool:
  - https://support.nordpoolgroup.com/support/solutions/articles/8000086528-about-the-sem-gb-intraday-auction
  - https://www.nordpoolgroup.com/en/trading/Intraday-trading/
- SEMOpx: https://www.semopx.com/ and /markets/
- Ofgem: the 2019 EPEX/EEX commitments notice and decision (no EUPHEMIA mention)
- SEMO: the EU re-integration response
- Not readable: piclo.com (connection reset), www.flexiblepower.co.uk home page (live), nationalgrid.co.uk news page (404).

**Open questions for human:** D1-D12 in the proposal, and approval of the 12 flagged mapping rows, the 94 DSO platform fills and the 13 new role rows. Main points:
- the `MOR-` prefix and validity dates;
- splitting the platform role;
- dropping `Market Operator` / `Market Platform`;
- keeping `Market Structure` / `Market Objective`;
- the new `Clearing Algorithm` column;
- MEC-0061 changing to `pay_as_bid`;
- GSP becoming `gsp_group`.

**Suggested new backlog items:**
- R-024: settlement type and clearing houses;
- R-025: apply R-020, blocked on approval and paired with R-031;
- R-026: SEM-GB algorithm, objective and pricing (the open EUPHEMIA point);
- R-027: verify the carried-over EAC values for MEC-0007/0009.

## 2026-11-23 · R-030 · Apply R-010 decisions (human decisions)
**Outcome:** done
**Summary:** Main session, on the human's instruction. The human approved R-010 D1-D8, with D3 amended:
- **D3 (line endings):** no `.gitattributes`. Validator check F1 now accepts LF or CRLF, one style per file, because git stores LF and checkouts on other systems and release downloads get LF. Tested in a scratch copy: the all-LF files pass, and a mixed file fails. The hook needs no `eol=lf` rule either.
- **D5/D6:** carried out in R-032.
- **D7:** the hook is not installed, at the human's request (R-034).
- **Checks:** before committing, the main session re-ran the validator (0 errors, 12 expected warnings) and its staged-copy mode in a throwaway clone (pass).
**Proposal:** research/proposals/2026-11-23-R-010-schema-and-validator.md ("Human decisions")
**Sources consulted:** none
**Open questions for human:** when to install the hook (R-034)
**Suggested new backlog items:** R-034 (install the hook)

## 2026-11-23 · R-010 · Schema metadata (datapackage.json), validator and pre-commit hook
**Outcome:** done (pending review)
**Summary:** Built the R-001 Question 6 design. No CSV data file was changed, and the hook is not installed.
- `CSV/datapackage.json` (Frictionless Data Package v2) describes all 18 CSVs: 146 fields, each with a type, a description and constraints; 18 primary keys; 42 foreign keys. Allowed values are foreign keys to the `LK_*` files, ORGANISATIONS or SOURCES, never enums.
- `missingValues` is `[""]`, so a blank still means not yet researched. `not_applicable` and `unknown` stay codes, because declaring them missing would merge them with blank in typed readers and break the lookups' primary keys.
- The 8 R-020 text columns and the `N/A`/multi-value columns are typed as they are today, with their targets in the descriptions.
- `scripts/validate.py` (stdlib only) checks files, types, keys and 11 cross-table rules (X1-X11). On today's data it passes: 0 errors, 12 warnings. It was tested with 29 mutation cases, and the hook end to end in a scratch repository.
- `scripts/hooks/pre-commit` validates the staged copies.
- Main finding: git stores the CSVs with LF (`i/lf w/crlf`), so CRLF holds only in Windows checkouts; `.gitattributes` is proposed. Also, 9 sources have no foreign-key reference: 4 are cited only in the R-009 draft evidence for `Standard Variant`, and 5 only in ORGANISATIONS notes.
**Proposal:** research/proposals/2026-11-23-R-010-schema-and-validator.md
**Sources consulted:**
- https://datapackage.org/standard/table-schema/
- https://datapackage.org/standard/data-resource/
- https://datapackage.org/standard/data-package/
- https://datapackage.org/standard/table-dialect/
- https://git-scm.com/docs/gitattributes
- https://org-id.guide/about
**Open questions for human:** decisions D1-D8 in the proposal:
- adopt the files;
- codes rather than missing values for `not_applicable` / `unknown`;
- `.gitattributes` for line endings;
- the required fields;
- `SOURCES.publisher` as a strict foreign key;
- lookups for coded columns that have none;
- installing the hook (`git config core.hooksPath scripts/hooks`);
- warning and error levels.
**Suggested new backlog items:** R-030 apply the R-010 decisions; R-031 schema entries for R-020's tables; R-032 lookups for the remaining coded columns and the publisher foreign key; R-033 move the R-009 per-row citations into CITATIONS.

## 2026-11-23 · R-021 · Apply R-009 lookups, ORGANISATIONS and SOURCES
**Outcome:** done
**Summary:** Main session, on the human's instruction.
- **Decisions:** the human approved R-009 D1-D11. D8 was amended: only `Standard Variant` is added, since the variant lookup already records the product.
- **Human change 1:** `LK_CONTRACT_LENGTH_BAND` now holds min/max ISO 8601 durations instead of a range in one cell. A later review of a yes/no-per-duration design is R-022.
- **Human change 2:** `LK_MECHANISM_CLASS` must allow for charges and taxes (BSUoS, carbon taxes), recorded in R-001 Change 6 and R-003.
- **Applied with `scripts/apply_r021.py`:**
  - 12 new tables added to `CSV/`.
  - KEY_DATA `Market Type` replaced by `Mechanism Class` + `Category`; `Standard Variant` added for 45 DSO rows (MEC-0076 on hold).
  - Market Operator, Status, Commodity, Direction, Contract Length Band and 13 yes/no columns converted to codes in place.
  - 8 columns whose lookups don't exist yet are left as text (R-020).
  - The qualifiers dropped by a mapping are kept in Notes.
- **Checks:** all passed: same IDs and order; no cell outside the converted columns changed; Notes only appended to; every code resolves to its lookup; every source and organisation reference resolves; BOM and CRLF kept. 141 change-log rows. Backup: research/backups/2026-11-23-pre-r021/.
**Proposal:** research/proposals/2026-11-23-R-009-lookups-and-organisations.md ("Human decisions")
**Sources consulted:** none new (sources are in CSV/SOURCES.csv)
**Open questions for human:** none
**Suggested new backlog items:** R-022 contract-length representation; R-023 Phase 2 governance tables (CITATIONS, record status and confidence, CHANGE_LOG).

## 2026-11-23 · R-009 · Lookup tables, ORGANISATIONS, SOURCES and the value mapping
**Outcome:** done (scope items 1-3 complete; item 4 moved to R-020)
**Summary:** Drafted the Phase 2 reference tables in `research/drafts/R-009/` (UTF-8 BOM, CRLF, `csv` module; `CSV/` untouched):
- ORGANISATIONS: 35 rows. These are 13 bodies (including the NGESO predecessor), 6 DNO groups plus the WPD and ENWL former brands, and the 14 DNO licensees with Companies House numbers.
- SOURCES: 45 rows, all cited. Reuse terms are in `notes`: GOV.UK and Ofgem are under the OGL; NESO's website and Grid Code are all rights reserved, so every definition is paraphrased.
- 10 lookups: LK_DSO_STANDARD_PRODUCT (5), LK_DSO_PRODUCT_VARIANT (17, with FMR-PD Table 3 parameters re-checked), LK_MECHANISM_CLASS, LK_CATEGORY, LK_STATUS, LK_COMMODITY, LK_DIRECTION, LK_YESNO, LK_CONTRACT_LENGTH_BAND, and a new LK_ORG_TYPE.
- VALUE_MAPPING.csv: 111 rows covering every value in 27 categorical columns (64 clean, 28 flagged, 3 sourced fills, 5 unmapped, 11 deferred). Its build script fails unless the ID sets match `CSV/` exactly.
- KEY_DATA_DSO_COLUMNS.csv: R-008 Change 2 in the new codes (40 standard, 3 legacy, 2 non-standard, MEC-0076 on hold).

Main findings:
- `Market Type` doesn't map cleanly for CM, CfD and LDES (re-typed), MEC-0022/0023 (stability, not voltage) and MEC-0027/0028 (NESO Trading and DFS are not BM actions).
- NESO says DFS replaces the Local Constraint Market from 7 Oct 2026. NESO's own name is "Single Markets Platform".
**Proposal:** research/proposals/2026-11-23-R-009-lookups-and-organisations.md
**Sources consulted:**
- Government and Companies House:
  - https://www.gov.uk/government/publications/designation-of-the-national-energy-system-operator-neso
  - https://www.gov.uk/government/collections/contracts-for-difference
  - https://www.gov.uk/government/collections/electricity-market-reform-capacity-market
  - https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero
  - https://find-and-update.company-information.service.gov.uk/ (company pages 11014226, 03600574, 02366949, 03782949, 08818711, 08961281, 08924703, 01528617; searches)
- Ofgem:
  - https://www.ofgem.gov.uk/sites/default/files/2026-03/all-electricity-licensees.pdf
  - https://www.ofgem.gov.uk/copyright
  - https://www.ofgem.gov.uk/about-us
  - https://www.ofgem.gov.uk/sites/default/files/docs/final_decisions_on_applications_to_be_designated_a_nemo_in_gb_10122015_2.pdf
  - https://www.ofgem.gov.uk/sites/default/files/docs/2016/11/final_decisions_on_epex_spot_nemo_designation_and_revocation_of_apx_nemo_designation_in_gb.pdf
  - https://www.ofgem.gov.uk/call-for-input/ldes-cap-and-floor-regime-our-role-plan-and-response-desnz-publication
  - https://www.ofgem.gov.uk/decision/long-duration-electricity-storage-ldes-window-1-eligibility-assessment-outcome
  - https://www.ofgem.gov.uk/sites/default/files/2023-12/Call%20for%20Input%20-%20Power%20Market%20Liquidity.pdf
- NESO:
  - https://www.neso.energy/industry-information/balancing-services and its sub-pages: response-and-reserve, stability-market, electricity-system-restoration-standard, reactive-power-services, local-constraint-market, trading, demand-flexibility-service-dfs, enduring-auction-capability-eac, single-markets-platform
  - https://www.neso.energy/what-we-do/systems-operations/what-balancing-mechanism
  - https://www.neso.energy/document/382376/download (Grid Code GD Issue 6 Rev 40)
  - https://www.neso.energy/terms-and-conditions
- Elexon and EMR Settlement:
  - https://www.elexon.co.uk/flexibility-markets/about/elexons-role/
  - https://www.elexon.co.uk/what-we-do/
  - https://www.emrsettlement.co.uk/
- Exchanges:
  - https://www.nordpoolgroup.com/en/about-us/
  - https://www.nordpoolgroup.com/en/trading/Day-ahead-trading/
  - https://www.nordpoolgroup.com/en/trading/Intraday-trading/
  - https://www.eex.com/en/markets/power/power-futures
  - https://www.ice.com/products/20788778/UK-Base-Electricity-Future-Gregorian
- Other:
  - https://www.ssen.co.uk/about-ssen/
  - https://org-id.guide/list/GB-COH
- R-008 sources were re-used from that run's copies.
- Not readable: ukpowernetworks.co.uk, enwl.co.uk (only the about page loaded), epexspot.com, lowcarboncontracts.uk, emrdeliverybody.com, energynetworks.org and the Iberdrola press release.

**Open questions for human:** R-009 decisions D1-D11 and approval of the D7 re-typings and fills. In short:
- extra columns (`registry_id`, `source_id`, `reuse_terms`);
- drop `licence_id`;
- a platform lookup;
- commodity Option A vs B;
- `Flat` -> `both`;
- DSO columns (variant + product, with fit in the lookup) and their code style;
- replace text with codes in place.

**Suggested new backlog items:**
- R-020: the remaining lookups and MECHANISM_ORG_ROLE.
- R-021: apply R-009 after approval (blocked).
- Annotated R-002, R-003, R-006 and R-010.

## 2026-11-23 · R-008 · Apply approved changes (human decisions)
**Outcome:** done
**Summary:** Main session, on the human's instruction. The human confirmed that the DSO rows came from Elexon's Flexibility Market Catalogue, and that the catalogue has no export option.
- **Applied with `scripts/apply_r008.py`** (9 rows in research/change_log.csv): Change 5 filled NPg `Contract Length Band` for MEC-0075 and MEC-0077 to MEC-0082 from NPg's 2026-27 statement; Change 4 added a flag note to MEC-0083 and MEC-0084.
- **Applied in the R-001 proposal text:** Change 7 corrected R-001 Change 12 (FMR-PD products, not ENA families), and the Phase 3 child table became `SUB_MARKET` (prefix `SUB-`).
- **Folded into R-009:** Changes 1-2 (standard product and variant columns).
- **On hold:** Change 3 (rename 076). The name probably matches what the catalogue said, so it needs checking by eye.
- **Passed to R-006:** Change 6.
**Proposal:** research/proposals/2026-11-23-R-008-dso-product-taxonomy.md
**Sources consulted:** https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202026-27.pdf (as cited in the proposal)
**Open questions for human:** none new (076 needs the catalogue entry checked by eye; see R-014)
**Suggested new backlog items:** none

## 2026-11-23 · R-017 · Prefixed permanent IDs (MEC-0001..MEC-0112) and R-001 decisions
**Outcome:** done
**Summary:** Main session, on the human's instruction. The human answered all remaining R-001 questions: rename "market" to "mechanism"; `snake_case` headers with unit suffixes; one row per product family with child tables; field-level citations; include SEM-GB and interconnector mechanisms with a `jurisdiction` column. Storage stays CSV as the master copy, plus `datapackage.json`, a pre-commit validator and a generated SQLite build that is not committed. Phase 2 design is approved. The human also approved R-001 Change 1a (prefixed, permanent IDs for every table), because the dataset will be published and its IDs will appear in website URLs. `scripts/apply_mec_ids.py` renamed the ID column in all six CSVs from `001`-`112` to `MEC-0001`-`MEC-0112`, keeping the same number. Nothing else changed: the script verified every non-ID cell, the BOM and CRLF. 112 mapping rows were added to research/change_log.csv. Backup: research/backups/2026-11-23-pre-mec-ids/.
**Proposal:** research/proposals/2026-11-23-R-001-database-structure-review.md (Change 1a; Questions 2-7)
**Sources consulted:** none (internal change)
**Open questions for human:** none
**Suggested new backlog items:** R-018 SQLite build with views; R-019 publication readiness.

## 2026-11-23 · R-008 · DSO flexibility product taxonomy and mapping
**Outcome:** done
**Summary:** The ENA Feb 2024 alignment report was read from a Wayback snapshot, since the direct URL still returns 403. Its five aligned products (PR, SU, OU, OU+SA, OU+VA) replaced Sustain/Secure/Dynamic/Restore, which it calls "historical nomenclature". The standard is now Elexon's Flexibility Market Rule FMR-PD v4.2 (25/08/2026): 5 products with 12 variants, of which SA OU-2/15/WA were added by NPg's change proposal FLX CP003 (11/06/2026). All 46 DSO rows were mapped from each DNO's own 2026/27 statement: 41 standard, 3 NGED legacy, 2 NPg FlexAdvance (non-standard). The NPg numbers 1)-10) are NPg's sub-market numbers, of which only 8 exist. 076 is probably a mislabelled Sub-Market 2 (LV SU month-ahead), 083/084 are windows or duplicates of 082 (SA OU-15), and 085-088 are NPg's 2025/26 sub-markets.
**Proposal:** research/proposals/2026-11-23-R-008-dso-product-taxonomy.md
**Sources consulted:**
- ENA and Elexon:
  - https://web.archive.org/web/20240503005600/https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf
  - https://www.energynetworks.org/assets/images/202412-rationalisation-of-dso-flexibility-products-(1)-(2).pdf
  - https://www.energynetworks.org/assets/images/Resource%20library/ON22-WS1A-P6%20Active%20Power%20Products%20Review%20(01%20Aug%202022).pdf
  - https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions
  - https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-smd-sub-market-definitions
  - https://www.elexon.co.uk/flexibility-markets/change-proposals/flx-cp003/
  - https://www.elexon.co.uk/flexibility-markets/implementation-monitoring/flexibility-market-catalogue/ (Power BI, not read)
- NGED:
  - https://dso.nationalgrid.co.uk/downloads/15141/nged-dso-distribution-flexibility-services-procurement-statement-2026-27.pdf
  - https://dso.nationalgrid.co.uk/downloads/15152/nged-distribution-flexibility-services-procurement-report-2025-26.pdf
  - https://dso.nationalgrid.co.uk/downloads/15098/unlocking-the-power-of-flexibility-deep-dive-oct-2025-1-.pdf
- NPg:
  - https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202026-27.pdf
  - https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202025-26%20v2.pdf
  - https://piclo-so-docs.s3.eu-west-2.amazonaws.com/Northern+Powergrid+/2025.12/Document+2+-+Scope+and+Specification.pdf
  - https://piclo-so-docs.s3.eu-west-2.amazonaws.com/Northern+Powergrid+/06.2026/Document+2+-+Scope+and+Specification.pdf
- SPEN, SP ENW, SSEN and UKPN:
  - https://www.spenergynetworks.co.uk/userfiles/file/SP5175_SPEN_DSO_C31E_Procurement_Statement_2026_v8_003.pdf (403; read from the Ofgem ZIP)
  - https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/sp-enw-distribution-flexibility-services-procurement-statement-2026..pdf
  - https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2026-27-flexibility-services-procurement-statement.pdf
- Ofgem:
  - https://www.ofgem.gov.uk/transparency-document/electricity-distribution-standard-licence-condition-31e-flexibility-procurement-statements-2026-2027
  - https://www.ofgem.gov.uk/sites/default/files/2026-06/Procurement-statements-2026-2027.zip (SPEN and UKPN statements)

**Open questions for human:**
1. The R-001 proposal now records Question 4 as answered (product family plus child tables), which was edited during this run. My brief said it was still open. Which is correct?
2. Add `Standard Product` / `Standard Variant` / `Product Fit` columns to KEY_DATA now, or wait for the Phase 2 lookups?
3. Do you know where the DSO rows came from (e.g. an Elexon catalogue export)? That would confirm the 076 rename and what 083/084 are.
4. For 083/084: keep them as windows until Phase 3, or delete them now?

**Suggested new backlog items:**
- R-013: DSO `Direction` values.
- R-014: Elexon Flexibility Market Catalogue export.
- R-015: fill DSO MARKET_INFO/TECHNICAL from FMR-PD.
- R-016: DSO coverage gaps.
- R-011 has been annotated with evidence that likely closes it.

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

