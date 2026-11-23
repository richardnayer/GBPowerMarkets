# Database structure review: keys, naming, vocabularies, provenance and scope extension
**Backlog item:** R-001
**Status:** Phase 1: approved 2026-11-23, applied (R-007). Phase 2: design approved 2026-11-23, not yet applied (R-009, R-010); content added under it is still flagged `proposed` for human review. Phases 3-4: pending review. All questions answered 2026-11-23.
**Date:** 2026-11-23

## Summary

All six CSVs in `CSV/` were profiled column by column with Python's `csv` module (`utf-8-sig`). The
main findings:

1. **The join key is broken.** `Market Name` is not unique. Four names appear twice (in KEY_DATA and
   in the other five files): `Operational Utilisation - 15 Minutes`, `Scheduled Utilisation (SU)`,
   `Operational Utilisation + 15 mins` and `Operational Utilisation + 2 mins`. So a join on name
   duplicates rows (2 x 2 = 4 rows per pair). In KEY_DATA, the only thing that tells these pairs apart
   is the `Notes` column (contract-length band), and that column does not exist in the other files.
   The `ID` column exists only in KEY_DATA.
2. **The 112 vs 111 row mismatch is fully explained.** KEY_DATA has separate rows `029 Capacity Market (T-1)`
   and `030 Capacity Market (T-4)`. The other five files have one row, `Capacity Market`, and it is
   entirely blank. There is also a case mismatch: `Distributed ReStart` (KEY_DATA) vs `Distributed Restart`
   (other files). Otherwise all five non-key files have the same row order as KEY_DATA, so IDs can be
   back-filled by position with no ambiguity (mapping in Change 1).
3. **Most of the database is empty.** MARKET_INFO has 28 columns. 7 of them are 100% blank and the
   others are 83-99% blank. TECHNICAL is 92-94% blank and PARTICIPANTS is 92-95% blank. In DISPATCH,
   about 60% of cells are blank and most filled cells are `N/A`. DESCRIPTION has 3 summaries and 4
   reference cells out of 111 rows. Only about 20 markets (NESO EAC services and exchange spot
   auctions) have any detail beyond KEY_DATA. The wide-table design does not fit the data: block-order
   parameters only make sense for exchange auctions, and response times only for ancillary services.
4. **Headers and values have typos, mixed units and inconsistent vocabularies.** These are listed in
   Changes 2-4.
5. **There is nowhere to store provenance or review status**, although the project rules require both.
   References are free text in `DESCRIPTION.Useful References` and `MARKET_INFO.Notes`.
6. **The "market" model does not fit the wider scope.** CfD, Capacity Market and LDES cap and floor are
   currently typed as `Forwards`. Charges and taxes (TNUoS, BSUoS, DUoS, CCL, CPS, UK ETS) have no
   home: they have no auction, no dispatch and no technical requirements. Instead they have charging
   bases, tariffs that change over time, and charged parties.

The recommendations are split into four phases. Phase 1 can be applied without changing the shape of
the existing tables. Phases 2-4 change the schema and need the human's approval of the design questions
at the end. Good practice is taken from the W3C CSV on the Web (CSVW) recommendations and the
Frictionless Table Schema. Both define primary keys, foreign keys, enumerated constraints and
missing-value conventions for plain CSV files:
- https://www.w3.org/TR/tabular-data-primer/ (sections 3.1, 3.10.2, 3.11, 3.14)
- https://www.w3.org/TR/tabular-metadata/
- https://datapackage.org/standard/table-schema/ (`primaryKey`, `foreignKeys`, `missingValues`, `enum`)
- https://www.rfc-editor.org/rfc/rfc4180 (CSV format)

---

## Changes

### Phase 1: key and hygiene fixes (no change to table shape except adding `ID`)

**Phase 1 status: approved 2026-11-23, applied (R-007).** Every change is logged cell by cell in
`research/change_log.csv` (95 rows). The pre-change CSVs are in `research/backups/2026-11-23-pre-phase1/`.
How each item was applied:
- ID is plain text `001`-`112` (no `GBM-` prefix; later replaced by `MEC-0001`-`MEC-0112`, see
  Change 1a). It is the first column of all five child files,
  and the child `Capacity Market` row is split into 029 (T-1) and 030 (T-4).
- KEY_DATA `Notes` is renamed `Contract Length Band`, with a new empty `Notes` column after it.
- ID 103 had only its spelling fixed: `Variable Availability Operational + 2 mins`. The word
  `Utilisation` was *not* inserted because no SPENW primary source confirmed it (the ITT 111546
  technical specification PDF is password-protected).
- Renaming ID 092 to `Scheduled Utilisation (SU)` makes it share a name with 093 (both SPEN). The two
  rows are distinguished by `Contract Length Band` and by `ID`.
- The DESCRIPTION typos `Epiry` and `minushed` (IDs 035 and 063) were fixed because both fixes are
  unambiguous. `Nor` (065) was left for R-005.
- Change 4 applied: `Pay-as-Clear`, `GBP/MW/h`, and KEY_DATA `Market Operator` `Nord Pool`.
  `MARKET_INFO.Market Platform` still reads `Nordpool` / `Nordpool / EUPHEMIA` (IDs 062-065) because
  that column was not listed in Change 4. It is a follow-up for approval.
- Deferred to Phase 2 Change 7: the `No?` and missing-value convention items. Those values are untouched.
- The SPEN and SPENW definitions are recorded in the change log only. No lookup table has been created.

#### Change 1. Make `ID` the primary key in every file

- Add an `ID` column as the first column of MARKET_INFO, TECHNICAL, DISPATCH, PARTICIPANTS and DESCRIPTION.
- Join on `ID` only. Keep `Market Name` as a descriptive label for now. It can be dropped from the
  child files in Phase 3, which removes the risk of the copies drifting apart.
- Store `ID` as text (for example `001`) so that leading zeros survive. Spreadsheet tools strip them
  if the column is treated as a number. Option: add a prefix such as `GBM-001` so that no tool can
  read the ID as a number. Never renumber or reuse an ID, and give new rows the next free number.
- Split the child-file `Capacity Market` row into two rows (`029`, `030`). This is safe because every
  child-file cell for that row is blank.

Positional mapping, verified by sequence alignment of names:

| Child-file data rows (1-based) | KEY_DATA ID | Note |
|---|---|---|
| 1-24 | 001-024 | exact name match |
| 25 `Distributed Restart` | 025 `Distributed ReStart` | case differs; use `Distributed ReStart` (NESO's usage) |
| 26-28 | 026-028 | exact match |
| 29 `Capacity Market` | 029 and 030 | duplicate the blank row for T-1 and T-4 |
| 30-111 | 031-112 | exact match, including the 4 duplicated names |

| File | Key | Column | Current | Proposed | Source |
|------|-----|--------|---------|----------|--------|
| MARKET_INFO, TECHNICAL, DISPATCH, PARTICIPANTS, DESCRIPTION | all rows | `ID` (new) | (absent) | back-filled per mapping above | internal analysis; CSVW primer s.3.14 https://www.w3.org/TR/tabular-data-primer/ |
| same five files | row 29 | `Market Name` | `Capacity Market` | `Capacity Market (T-1)` (ID 029) + new row `Capacity Market (T-4)` (ID 030) | KEY_DATA.csv rows 029/030 |
| same five files | row 25 | `Market Name` | `Distributed Restart` | `Distributed ReStart` | KEY_DATA.csv row 025 |

#### Change 1a. Prefixed, permanent IDs for every table (approved 2026-11-23)

The human approved this on 2026-11-23, after Phase 1 was applied. It replaces the plain `001`-`112`
format from Change 1. The reason: the dataset will be published, and its IDs will appear in website
URLs and in other people's citations.

Rules:
- **IDs carry no meaning.** An ID never encodes a name, operator or product, because those change
  (National Grid ESO became NESO; ENWL became SPENW). Meaning lives in the name and acronym columns. If
  readable URLs are wanted, a separate `slug` column can provide them, e.g.
  `/mechanism/MEC-0029/capacity-market-t1`. The slug may change; the ID may not.
- **Format:** an uppercase prefix, a hyphen, then a zero-padded number of fixed width: 4 digits for
  core and reference tables, 6 for high-volume tables. No prefix may look like a month name, because
  Excel can read e.g. `MAR-0001` as a date.
- **IDs are permanent.** Never renumber or reuse an ID. A retired or merged record is kept with
  `record_status = deprecated`. New records take the next free number.
- **Existing mechanisms keep their numbers:** `001` becomes `MEC-0001`, `029` becomes `MEC-0029`.
- **Historical records keep the old IDs.** This covers change-log rows written before the rename,
  proposals and `research/log.md`. The rename itself is logged as one mapping row per ID.
- **Lookup tables (`LK_*`) have no prefix.** Their codes are readable snake_case words such as
  `pay_as_clear`.

| Table | Prefix | Digits | Example |
|---|---|---|---|
| MECHANISM (today KEY_DATA and its child files) | `MEC` | 4 | `MEC-0029` |
| ORGANISATIONS | `ORG` | 4 | `ORG-0001` |
| SOURCES | `SRC` | 4 | `SRC-0001` |
| MECHANISM_RELATIONSHIP | `REL` | 4 | `REL-0001` |
| CITATIONS | `CIT` | 6 | `CIT-000001` |
| SUB_MARKET (was PROCUREMENT_WINDOW; see Change 12) | `SUB` | 6 | `SUB-000001` |
| PARAMETER_VALUES | `PAR` | 6 | `PAR-000001` |
| CHANGE_LOG | `CHG` | 6 | `CHG-000001` |

Applying it: `scripts/apply_mec_ids.py` renames the mechanism IDs in all six CSVs. The other prefixes
come into use as their tables are created, starting with R-009.

#### Change 2. Fix header typos

| File | Column | Current | Proposed |
|------|--------|---------|----------|
| MARKET_INFO | 2 | `Market Structue` | `Market Structure` |
| MARKET_INFO | 16 | `Parent Child Oders` | `Parent-Child Orders` |
| MARKET_INFO | 17 | `Max Generations` | `Max Parent-Child Generations` |
| MARKET_INFO | 19 | `Max Parents per Child2` | `Max Parents per Child` |
| MARKET_INFO | 13-14 | `Availability`, `Utilisation` | `Availability Payment`, `Utilisation Payment` (they record whether each payment exists) |
| DISPATCH | 5 | `Post-Faul` | `Post-Fault` |
| TECHNICAL | 6 | `Ramp Rate Lower Bound [s-1]` | `Ramp Rate Lower Bound [pu/s]`: the value is a fraction of contracted MW per second (2 = 100% in 0.5 s for DC; 0.125 = 100% in 8 s for DR). Check against the NESO service terms during R-005. |
| KEY_DATA | 9 | `Notes` (holds contract-length bands) | `Contract Length Band`, with a new free-text `Notes` column |

Source for the typo fixes: the files themselves. The ramp-rate unit should be confirmed against the NESO
Dynamic Response service terms (https://www.neso.energy/industry-information/balancing-services/frequency-response-services).

#### Change 3. Fix market-name typos and make duplicated names unique

| File | ID | Current | Proposed |
|------|----|---------|----------|
| all | 100 | `Scheduled Utilisation ` (trailing space) | `Scheduled Utilisation` |
| all | 102 | `Variable Availabiulity Operational Utilisation + 15 mins` | `Variable Availability Operational Utilisation + 15 mins` |
| all | 103 | `Variable Availabiulity Operational + 2 mins` | `Variable Availability Operational Utilisation + 2 mins` (confirm with SPENW source) |
| all | 092 | `Schedule Utilisation (SU)` | `Scheduled Utilisation (SU)` |
| all | 111 | `Schedule Utilisation (Day Ahead)` | `Scheduled Utilisation (Day Ahead)` |
| all | 089/090, 093/101, 094/095, 096/097 | duplicated names | Keep the names. They become unique when combined with `Market Operator` and `Contract Length Band`. Uniqueness is then guaranteed by `ID`. Phase 3 (Change 12) removes the duplication properly. |
| all | 076/077 and 082/083/084 | NPg names that differ only by a numeric prefix (`2)`/`3)`, `8)`/`9)`/`10)`) | Flag for R-005: find what tells these tenders apart (zone, season, voltage) in NPg's tender documents. |

Text typos in DESCRIPTION (`Epiry` -> `Expiry`; `minushed` -> `minutes`) and MARKET_INFO
`Market Objective` = `Nor` (truncated, ID 065 SEM-GB Auction 2) are passed to R-005 as value fixes.

#### Change 4. Normalise vocabulary inconsistencies that are already visible

| File | Column | Current values | Proposed |
|------|--------|---------------|----------|
| MARKET_INFO | `Pricing Structure` | `Pay as Clear` (10), `Pay-as-Cleared` (9) | `Pay-as-Clear` (one spelling; use the lookup in Change 6) |
| MARKET_INFO | `Payment Unit` | `£/MW/h` | `GBP/MW/h`, an ASCII-safe currency code that avoids encoding problems. The file stores `£` correctly as UTF-8 bytes C2 A3, but it displays as `?` in Windows consoles. |
| KEY_DATA | `Market Operator` | `Nordpool` | `Nord Pool` (the exchange's own spelling) |
| KEY_DATA | `Market Operator` | `SPEN` and `SPENW` | Define both. SPEN = SP Energy Networks (licensees SP Distribution and SP Manweb). SPENW = SP Electricity North West, the former Electricity North West, renamed 4 Aug 2025 after Iberdrola acquired it. Sources: https://www.iberdrola.com/press-room/news/detail/sp-electricity-north-west-unveiled-new-name-visual-identity-part-iberdrola-group and https://www.enwl.co.uk/about-us/ |
| PARTICIPANTS | `Suppliers` | `No?` | Split into a value and a confidence: value `No`, confidence `low`. See Change 7. |
| all | missing values | mixture of blank, `N/A` and `No?` | Adopt the convention in Change 7. |

### Phase 2: lookup tables, provenance and review status (new tables; existing columns become foreign keys)

#### Change 5. Add a `SOURCES` table and a field-level `CITATIONS` table

This is needed to meet project rules 3 and 4 (every change has a referenceable source, with primary
sources preferred).

```
SOURCES.csv
  source_id        PK, text, e.g. SRC-0001
  title            text
  publisher        text (FK -> ORGANISATIONS.org_id where possible)
  url              text (canonical URL)
  source_type      enum: primary | secondary | internal
  doc_type         enum: webpage | service_terms | rulebook | contract_spec | consultation | decision | dataset | statute | other
  version_or_date  text (document version or publication date, ISO 8601)
  accessed_date    date (ISO 8601, YYYY-MM-DD)
  archive_url      text (optional; e.g. Wayback Machine snapshot)
  notes            text

CITATIONS.csv
  citation_id      PK
  table_name       text (e.g. TECHNICAL)
  record_id        FK -> mechanism ID
  field_name       text (column name, or * for the whole record)
  source_id        FK -> SOURCES.source_id
  locator          text (page / section / clause, e.g. "Schedule 2, para 3.1")
  quote_or_note    text (short supporting extract)
```

Migration: move `DESCRIPTION.Useful References` (semicolon lists, IDs 010-013) and the EPEX URL in
`MARKET_INFO.Notes` (IDs 057-060) into SOURCES and CITATIONS. Then drop `Useful References` and
restrict `Notes` to free text. R-005 should also note that IDs 012/013 (Slow Reserve) currently cite
the Quick Reserve web page.

#### Change 6. Controlled vocabularies as lookup CSVs (`LK_*.csv`) with foreign keys

Each lookup has the columns `code, label, definition, source_id`. The proposed initial values below
were derived from the data. Definitions are to be sourced.

| Lookup | Used by | Proposed codes (initial) | Issue fixed |
|---|---|---|---|
| `LK_MECHANISM_CLASS` | mechanism | `exchange_auction`, `exchange_continuous`, `otc_bilateral`, `exchange_derivative`, `so_ancillary_service`, `balancing_mechanism`, `dso_flexibility`, `capacity_mechanism`, `revenue_support_scheme`, `network_charge`, `system_charge`, `policy_levy`, `tax`, `emissions_trading`, `certificate_scheme` | `Market Type` mixes service purpose (`Thermal`, `Voltage`), instrument (`Futures`, `Forwards`) and venue (`Wholesale Spot`). CM, CfD and LDES are mis-typed as `Forwards`. |
| `LK_CATEGORY` (service purpose) | mechanism | `energy`, `frequency_response`, `reserve`, `thermal_constraint`, `voltage`, `stability`, `restoration`, `capacity_adequacy`, `investment_support`, `network_cost_recovery`, `decarbonisation` | Separates purpose from mechanism class. |
| `LK_STATUS` | mechanism | `live`, `planned`, `trial`, `suspended`, `closed` | 2 blank statuses (018 Megawatt Dispatch, 030 CM T-4). Add a `status_as_of` date column. |
| `LK_COMMODITY` | mechanism | `active_energy` (MWh), `active_power_capacity` (MW), `reactive_power` (MVAr), `stability` (MVA.s inertia / short-circuit level), `firm_capacity`, `financial_exposure`, `emissions_allowance` (tCO2e), `none` | `Financial Futures` and `Financial Forwards` describe instrument type, not commodity. Note that ICE UK Base Electricity futures are *physically* delivered via ECVNs (https://www.ice.com/products/20788778/UK-Base-Electricity-Future-Gregorian), so `Financial Futures` is factually wrong for them. Passed to R-005. |
| `LK_SETTLEMENT_TYPE` (new) | instrument | `physical_ecvn`, `physical_exchange_nomination`, `cash`, `not_applicable` | Needed to tell physical ICE contracts from cash-settled ones. |
| `LK_DIRECTION` | mechanism | `up`, `down`, `both`, `not_applicable` | Values `Up/Down`, `Flat`, `N/A` and blank (17 rows) are mixed. A sign convention must be defined, e.g. *up = increase net export to the system (more generation or less demand)*. Under that convention DC High (response to high frequency) = `down`, which matches the current data, but this needs documenting. `Flat` for spot markets should become `both` or `not_applicable`. |
| `LK_YESNO` | all Yes/No fields | `yes`, `no`, `not_applicable`, `unknown` | See Change 7. |
| `LK_PRICING_RULE` | market_info | `pay_as_clear`, `pay_as_bid`, `regulated_tariff`, `administered_strike`, `bilateral` | Two spellings in use today. |
| `LK_AUCTION_TYPE` | market_info | `sealed_double_sided`, `sealed_single_sided`, `descending_clock`, `continuous`, `not_applicable` | Only `Closed Double Sided` in use today. The Capacity Market uses a descending clock auction; R-002 to verify. |
| `LK_AGGREGATION_LEVEL` | participants | `site`, `gsp`, `gsp_group`, `national`, `cmz` (DSO constraint managed zone) | `GSP` and `National` in use today. |
| `LK_CONTRACT_LENGTH_BAND` | mechanism / procurement | `le_day`, `day_to_week`, `week_to_month`, `month_to_year`, `gt_year` | Current KEY_DATA `Notes` values (`Week < x <= Month`, etc.). |
| `ORGANISATIONS` | mechanism and roles | `org_id, name, short_name, org_type (SO/DNO/TO/exchange/regulator/government/counterparty/settlement_agent/broker), parent_org_id, licence_id, url, valid_from, valid_to, predecessor_org_id` | Free-text operators; DNO renames (ENWL -> SPENW); `Brokers & Bilaterals` is not an organisation. |
| `MECHANISM_ORG_ROLE` | mechanism | `mechanism_id, org_id, role` with role in {`operator`, `platform`, `counterparty`, `settlement_agent`, `policy_owner`, `regulator`, `clearing_house`, `delivery_body`} | `Market Operator` holds a single value, but the CfD involves DESNZ (policy), NESO as EMR Delivery Body (allocation) and LCCC (counterparty); the CM involves NESO (delivery body) and EMR Settlement / ESC; LDES cap and floor involves Ofgem (operator blank today). `Market Platform` = `NESO EAC & SMP` and `Nordpool / EUPHEMIA` are multi-valued cells. Sources: https://www.emrdeliverybody.com/ and https://www.lowcarboncontracts.uk/ |

#### Change 7. Missing-value and confidence convention

This follows Frictionless `missingValues` (https://datapackage.org/standard/table-schema/#missingValues).

- **blank** = not yet researched.
- **`not_applicable`** = researched, and the attribute does not apply (for example dispatch fields for a cash future).
- **`unknown`** = researched, but no authoritative source found.
- Never encode uncertainty inside the value (`No?`). Put it in CITATIONS, or add a `confidence` column
  (`high`/`medium`/`low`) on the review tables in Change 8.
- Numeric columns hold numbers only. `N/A` in TECHNICAL numeric columns becomes `not_applicable`, or
  blank with a citation note. The unit goes in the column header or in a unit column, never in the
  value: `Maximum Block Size` = `500 MW` becomes `500` in `Max Block Size [MW]`.

#### Change 8. Review status and change log

- Add record-level columns to the mechanism table:
  - `record_status`: `draft` | `proposed` | `verified` | `deprecated`
  - `last_verified_date`
  - `last_verified_by`
- Add `CHANGE_LOG.csv` with the columns `change_id, proposal_file, table_name, record_id, field_name,
  old_value, new_value, source_id, status (pending|approved|rejected|applied), reviewer, decided_date,
  applied_date`.
- Each approved proposal adds rows to CHANGE_LOG when it is applied. This gives the label and flag for
  human review that project rule 2 requires, and it gives an audit trail that sits alongside git history.

### Phase 3: restructure the sparse wide tables

#### Change 9. MARKET_INFO: drop empty columns and move order-type parameters to a child table

- **Drop** the 7 columns that are 100% blank: `Overholding`, `Curve Orders`, `Loop Blocks`,
  `Curtailable Blocks`, `Linked Blocks`, `Exclusive Blocks` and `Exclusive Links`. Re-add them as rows
  in the child table only when sourced.
- **Move** these columns to a new long-format table `ORDER_TYPES.csv`, with the columns
  `mechanism_id, order_type, supported (LK_YESNO), parameter, value, unit, source_id`:
  - `Parent-Child Orders`
  - `Max Parent-Child Generations`
  - `Max Children per Parent`
  - `Max Parents per Child`
  - `Block Orders`
  - `Max Block Size`

  These are only populated for 4 EPEX auctions (IDs 057-060), and NESO EAC's parent-child orders
  (IDs 001-011). Example row: `057, block, yes, max_block_size, 500, MW, SRC-xxxx` (source:
  https://www.epexspot.com/sites/default/files/download_center_files/EPEX%20SPOT_Power%20Spot%20Auctions_Block%20Parameters.pdf).
- **Restructure `Market Timing`** (`D-1 @ 14:00`, `D-1 @ 09:20 GMT`) into separate columns:
  - `gate_closure_day_offset` (integer, e.g. -1)
  - `gate_closure_time` (HH:MM)
  - `time_zone`, using an IANA name such as `Europe/London` or `CET`

  `GMT` is ambiguous in summer, when GB markets run on UK local time (BST), and some rows have no time
  zone at all (`D-1 @ 14:00`). Follow ISO 8601 / IANA tz.
- **Split multi-valued cells.** `Market Period [mins]` and `Settlement Period [mins]` = `30 / 60` (SEM-GB
  auctions) should become either min/max columns or one row per product variant. `Market Co-Optimisation`
  = `Yes: Response & Reserve` should become `co_optimised (yes/no)` plus a relationship row (Change 13).
- **Split `Period Coverage`** (`00:00 to 24:00`) into `delivery_start_time` and `delivery_end_time`.

#### Change 10. Long-format PARTICIPANTS and merged DISPATCH

- PARTICIPANTS becomes `ELIGIBILITY.csv`, with the columns
  `mechanism_id, participant_type, eligible (LK_YESNO), conditions, source_id`. `participant_type` is
  one of: `bmu`, `non_bmu`, `generation`, `demand`, `storage`, `supplier`, `interconnector`,
  `aggregator`, `ev_or_domestic`. New participant types can then be added as rows, not columns.
  `Aggregation` moves to TECHNICAL as `aggregation_level` (LK_AGGREGATION_LEVEL).
- DISPATCH has only 4 attributes. Merge it into TECHNICAL as `dispatcher` (FK ORGANISATIONS, or `self`),
  `dispatch_method` (`automatic_frequency`, `boa`, `obp`, `dso_instruction`, `self_dispatch`,
  `not_applicable`), `pre_fault` and `post_fault`. The current `Dispatcher` = `Self` and
  `Dispatch Type` = `Self` pair is redundant. `BOA/OBP` is multi-valued and should become two flags or
  a relationship. Alternatively, keep DISPATCH as a separate 1:1 table if the human prefers fewer files
  to change.

#### Change 11. TECHNICAL: units and types

- Use SI or explicit units in header suffixes: `[s]`, `[min]`, `[MW]`, `[pu/s]`.
- Add `delivery_duration_basis` if needed (energy-limited duration vs contracted window).
- `Minimum Capacity [MW]` / `Maximum Capacity [MW]` are numeric only.
- Add a `data_dictionary.csv`, or a Frictionless `datapackage.json`, that records each column's type,
  unit, allowed values and definition. This is where human-readable labels can live if the headers
  become machine names (see Question 3).

#### Change 12. Separate *product* from *sub-market* (DSO and similar)

_Corrected 2026-11-23 (R-008 Change 7, approved). The table is now named `SUB_MARKET`, prefix `SUB-`
(approved 2026-11-23). The earlier text described Sustain / Secure / Dynamic / Restore as the ENA
product families. That was wrong: they are superseded legacy products._

46 rows are DSO flexibility (43% of the database). Many are the same product procured over different
horizons. For example, SPEN `Operational Utilisation - 15 Minutes` appears twice, differing only by
contract-length band, and NPg has numbered tender lines. The DSO standard products are now defined by
Elexon's Flexibility Market Rule FMR-PD v4.2: five products (SU, PR, OU, SA+OU, VA+OU) in 12
variants (https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions).
The mapping of all 46 rows is in research/proposals/2026-11-23-R-008-dso-product-taxonomy.md. The
human confirmed that the DSO rows were taken from Elexon's Flexibility Market Catalogue, which lists
*sub-markets*.

Proposal:
- The mechanism row is *DNO x standard variant* (e.g. `SPEN - Scheduled Utilisation`), with a column
  `standard_variant_code` (FK -> `LK_DSO_PRODUCT_VARIANT`). R-008 found that the 46 DSO rows collapse
  to 25 such rows.
- A new `SUB_MARKET.csv` holds `sub_market_id, mechanism_id, contract_length_band,
  procurement_lead_time, procurement_frequency, platform (FK ORGANISATIONS e.g. Piclo/Flexible
  Power/own portal), first_seen, last_seen, source_id`. The term is Elexon's: in FMR-SMD, a
  sub-market is one system operator procuring one product within one time period. The columns should
  follow FMR-SMD Table 2, so that the table can be checked against the catalogue
  (https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-smd-sub-market-definitions).

This removes the duplicate names and makes cross-DNO comparison possible. The same pattern applies
to:
- Capacity Market T-1/T-4 (one scheme, two auction windows)
- CfD Allocation Rounds (AR1...AR7+)
- Exchange futures (one product family, many tenors: Day/Weekend/Week/Month/Quarter/Season/Year).
  This would reduce the 17 EEX rows to 3 families (Base, Peak, TB2) x tenors.

Whether these cases use `SUB_MARKET` or child tables of their own will be settled when Phase 3 is
designed in detail.

This is the largest change. Its direction was approved under Question 4.

### Phase 4: extend the schema for the wider scope (CfDs, CM, futures, use-of-system charges, carbon taxes)

#### Change 13. Generalise "market" to "mechanism", with subtype tables

The core table, currently KEY_DATA, becomes `MECHANISM.csv` (one row per market, product, scheme,
charge or tax). It holds only attributes common to everything: ID, name, acronym, `mechanism_class`,
`category`, status, `status_as_of`, commodity, direction, `jurisdiction` (`GB`, `GB-SEM`), `record_status`
and `parent_mechanism_id`.

Class-specific attributes live in optional 1:1 subtype tables. Each row exists only if it applies.
This is a "supertype/subtype" or "class table inheritance" pattern, and it avoids the 90%-blank wide
tables seen today.

| Subtype table | Applies to `mechanism_class` | Key columns (indicative) |
|---|---|---|
| `MARKET_INFO` (existing, slimmed) | exchange_auction, exchange_continuous, so_ancillary_service, dso_flexibility, balancing_mechanism | structure, gate closure, market period, settlement period, auction type, pricing rule, objective, availability/utilisation payment, payment unit |
| `TECHNICAL` (existing + dispatch) | so_ancillary_service, dso_flexibility, balancing_mechanism | response times, ramp, duration, min/max MW, dispatch fields, aggregation level |
| `INSTRUMENT_INFO` (new) | exchange_derivative, otc_bilateral | venue (FK ORGANISATIONS), contract code (e.g. ICE `UBL`), clearing house, load shape (`base`, `peak`, `tb2`, `other`), tenor, contract size + unit, tick size, currency, settlement type (LK_SETTLEMENT_TYPE), underlying (FK mechanism, e.g. options -> futures), last trading rule |
| `SCHEME_INFO` (new) | capacity_mechanism, revenue_support_scheme, certificate_scheme | legal basis (statute/regulations URL), policy owner, allocation method (sealed bid / descending clock / administered), allocation frequency, contract length [years], counterparty, price basis (strike price GBP/MWh, clearing price GBP/kW/yr), indexation, eligibility summary, funding route (FK mechanism, e.g. CfD -> supplier obligation levy) |
| `CHARGE_INFO` (new) | network_charge, system_charge, policy_levy, tax, emissions_trading | charging body, governing code/methodology (CUSC section 14, DCUSA, BSC, Finance Act, ETS Order), charged party (generator/supplier/demand/all), charging basis (GBP/kW/yr, p/kWh, GBP/MWh, GBP/tCO2e, p/day), tariff period (charging year Apr-Mar), locational (yes/no), zone basis (TNUoS zone, DNO area, GSP group), exemptions summary |

Two more new tables:

- **`MECHANISM_RELATIONSHIP.csv`**: `from_id, to_id, relationship_type`. `relationship_type` is one of:
  - `variant_of`: High/Low pairs; CM T-1/T-4 -> CM
  - `underlying_of`: options -> futures
  - `funded_by`: CfD -> CfD supplier obligation levy; CM -> CM supplier charge
  - `settles_via`: services -> BM / BSC
  - `co_optimised_with`: EAC services
  - `replaces`: e.g. SFFR replacing legacy FFR
  - `coupled_with`: SEM-GB auctions

  This replaces the free-text `Market Co-Optimisation` and lets the database show how the GB system
  fits together.
- **`PARAMETER_VALUES.csv`** (time series of headline values): `mechanism_id, parameter, value, unit,
  valid_from, valid_to, source_id`. Examples include:
  - Carbon Price Support rate (GBP/tCO2)
  - CCL main rates (p/kWh)
  - BSUoS fixed tariff (GBP/MWh)
  - TNUoS demand residual bands
  - CM clearing prices by delivery year
  - CfD administrative strike prices by round
  - DC clearing price caps

  Rates change every year, so they must not overwrite a single cell.

Content for these tables is the job of backlog items R-002 (government mechanisms) and R-003 (charges
and taxes). This proposal defines only where that content goes.

#### Change 14 (optional). Storage format

_Decided 2026-11-23 (Question 6): CSV canonical + `datapackage.json` + pre-commit validator +
generated SQLite build with views._

Keep CSV as the canonical, diff-friendly store in git. Add a `datapackage.json` (Frictionless) or CSVW
metadata file that declares primary keys, foreign keys and enums, and add a small validation script
(new backlog item). Option: generate a SQLite build from the CSVs for querying. The UTF-8 BOM can stay
for Excel compatibility, but it should be documented in the data dictionary.

---

## Before / after schema (summary)

**Before:** 6 files, all keyed on non-unique `Market Name`. 64 columns in total, many empty.
- KEY_DATA(ID, Market Name, Market Type, Market Operator, Acronym, Status, Commodity, Direction, Notes)
- MARKET_INFO(Market Name + 27 attribute columns)
- TECHNICAL(Market Name + 9)
- DISPATCH(Market Name + 4)
- PARTICIPANTS(Market Name + 8)
- DESCRIPTION(Market Name, Summary Paragraph, Useful References)

**After (all phases):**

Core:
- MECHANISM (PK mechanism_id). FKs: LK_MECHANISM_CLASS, LK_CATEGORY, LK_STATUS, LK_COMMODITY, LK_DIRECTION, and parent_mechanism_id -> MECHANISM.

Subtypes (1:1, optional):
- MARKET_INFO
- TECHNICAL (includes dispatch)
- INSTRUMENT_INFO
- SCHEME_INFO
- CHARGE_INFO

Children (1:N):
- ORDER_TYPES
- ELIGIBILITY
- SUB_MARKET
- PARAMETER_VALUES
- MECHANISM_ORG_ROLE
- MECHANISM_RELATIONSHIP
- DESCRIPTION (could also be 1:1)

Reference:
- ORGANISATIONS
- LK_* lookups
- SOURCES

Governance:
- CITATIONS
- CHANGE_LOG
- data_dictionary / datapackage.json

## Data-quality issues found (passed to R-005, not proposed here)

| ID | Issue |
|---|---|
| 007 MFR LFSM | MARKET_INFO is filled with EAC auction values identical to DC (D-1 14:00, pay-as-clear, co-optimised). MFR / LFSM is a Grid Code requirement, not an EAC auction product, so these look like copy-down errors. 008 MFR FSM is blank. |
| 018 Megawatt Dispatch | Status blank. |
| 029-032 CM / CfD / LDES | Typed `Forwards`. Commodity blank. CfD operator `NESO` (should be a role set). LDES operator blank (Ofgem). |
| 030 CM T-4 | Status blank. |
| 035-039 ICE contracts | Commodity `Financial Futures` and all dispatch fields `N/A`, but ICE UK Base futures are physically delivered via ECVN (https://www.ice.com/products/20788778/UK-Base-Electricity-Future-Gregorian). |
| 012/013 Slow Reserve | References point to the Quick Reserve page. |
| 016/017, 019-028, 033 | Direction blank. |
| 065 SEM-GB Auction 2 | `Market Objective` = `Nor` (truncated). |
| 001-006 | Suppliers = `No?`. |
| DESCRIPTION 035, 063 | Typos (`Epiry`, `minushed`). |

## Confidence and caveats

- **High confidence:** the key and row-mismatch analysis, blank-column statistics, header typos, and
  duplicate names. All of these were computed directly from the files.
- **Medium confidence:** the proposed vocabularies. The codes are derived from the data and general GB
  market knowledge, and each definition still needs a cited source when the lookup is populated. The
  ramp-rate unit interpretation (`pu/s`) and the Direction sign convention must be confirmed against
  NESO service terms.
- **DSO product taxonomy:** verified in R-008 against Elexon FMR-PD v4.2 and the ENA Feb 2024 report
  (read from a Wayback Machine copy). See research/proposals/2026-11-23-R-008-dso-product-taxonomy.md.
- **Phase 3 Change 12 and Phase 4** are design choices with trade-offs. Long-format tables are more
  flexible but harder to edit by hand in Excel. Wide 1:1 subtype tables are easier to edit but sparse.
- **CSV changes:** only Phase 1 has been applied (2026-11-23, R-007). Phases 2-4 have not been applied.

## Questions for the human

1. ~~Approve Phase 1~~ Answered: approved 2026-11-23 and applied (R-007).
2. ~~Rename the core entity from "market" to "mechanism" (KEY_DATA -> MECHANISM) to cover schemes,
   charges and taxes?~~ Answered 2026-11-23: **yes**, rename to "mechanism".
3. ~~Headers: switch to machine-friendly `snake_case` with units in a data dictionary, or keep the
   current human-readable headers (`Max Time to Full Delivery [s]`)?~~ Answered 2026-11-23:
   **`snake_case` with the unit as a suffix** (e.g. `max_time_to_full_delivery_s`), plus a data
   dictionary.
4. ~~Granularity: should DSO products, CM/CfD rounds and futures tenors be one row per product family,
   with windows/tenors in child tables (recommended)? Or keep one row per tender line or contract tenor
   as now?~~ Answered 2026-11-23: **one row per product family**, with procurement windows, CM/CfD
   rounds and futures tenors in child tables.
5. ~~Provenance: field-level CITATIONS (recommended), or record-level only?~~ Answered 2026-11-23:
   **field-level**, with `field_name = *` allowed where one source covers the whole record.
6. ~~Format: CSV-only with a `datapackage.json`, or also a generated SQLite build? Keep the UTF-8
   BOM?~~ Answered 2026-11-23: **CSV is the canonical store.** A Frictionless `datapackage.json`
   declares keys, foreign keys and allowed values. A standard-library validator runs as a git
   pre-commit hook. A build script generates a SQLite database (foreign keys enforced) with views that
   join the tables back into readable form. The SQLite file is a build output and is not committed.
   Keep the UTF-8 BOM for now, document it in the data dictionary, and revisit before publication.
   Context: the human intends to publish the dataset and later build an open-source website on it for
   looking up mechanisms and how they are linked.
7. ~~Should the database be GB-only, or include SEM-GB coupled products and interconnector capacity
   auctions (e.g. JAO / interconnector explicit auctions) as their own mechanisms?~~ Answered
   2026-11-23: **include them** as their own mechanisms, tagged with a `jurisdiction` column.
