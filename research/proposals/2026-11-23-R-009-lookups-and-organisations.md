# Phase 2 content: ORGANISATIONS, SOURCES, lookup tables and the value mapping
**Backlog item:** R-009
**Status:** approved 2026-11-23, with amendments (see "Human decisions" at the end). Applied as R-021 (`scripts/apply_r021.py`).
**Date:** 2026-11-23
**IDs:** mechanism IDs use the `MEC-NNNN` form (R-001 Change 1a). New IDs: `ORG-0001`..`ORG-0035`, `SRC-0001`..`SRC-0045`.

## Summary

R-001 Phase 2 (design approved 2026-11-23) needs reference tables before the existing columns can become
foreign keys. This run drafted them, outside `CSV/`, in `research/drafts/R-009/`. Each file is UTF-8 with a BOM and
CRLF line endings, and was written with Python's `csv` module.

| File | Rows | What it holds |
|---|---|---|
| `ORGANISATIONS.csv` | 35 | 13 bodies (NESO, Elexon, EMRS, LCCC, ESC, DESNZ, Ofgem, ENA, 4 exchanges, plus the NGESO predecessor), 6 DNO groups with 2 former brands (WPD, ENWL), and the 14 DNO licensees |
| `SOURCES.csv` | 45 | Every source cited by a draft row. R-001 Change 5 columns; reuse terms are in `notes` |
| `LK_ORG_TYPE.csv` | 10 | New lookup for `ORGANISATIONS.org_type` (Change 6 had an inline enum) |
| `LK_DSO_STANDARD_PRODUCT.csv` | 5 | FMR-PD products (R-008 Finding 1b) |
| `LK_DSO_PRODUCT_VARIANT.csv` | 17 | 12 FMR-PD variants, 4 legacy ENA products, NPg FlexAdvance (R-008 Findings 1b/1c) |
| `LK_MECHANISM_CLASS.csv` | 9 | Classes used by today's rows |
| `LK_CATEGORY.csv` | 9 | Purposes used by today's rows |
| `LK_STATUS.csv` | 5 | `live`, `planned`, `trial`, `suspended`, `closed` |
| `LK_COMMODITY.csv` | 4 | `active_power`, `reactive_power`, `stability`, `firm_capacity` |
| `LK_DIRECTION.csv` | 4 | `up`, `down`, `both`, `not_applicable` |
| `LK_YESNO.csv` | 4 | Change 7 convention |
| `LK_CONTRACT_LENGTH_BAND.csv` | 4 | The 4 bands in KEY_DATA today |
| `VALUE_MAPPING.csv` | 111 | Every current value in 27 categorical columns mapped to its new code |
| `KEY_DATA_DSO_COLUMNS.csv` | 46 | Proposed `Standard Product` / `Standard Variant` values for the DSO rows (R-008 Change 2) |
| `build/*.py` | 3 | Scripts that regenerate the drafts. The mapping script checks that its value and ID sets match `CSV/` exactly |

Every `source_id`, `ORG-` and `SRC-` reference in the drafts resolves, every source is cited at least once, and
every lookup code is snake_case. No file in `CSV/` was changed.

All drafted content is `proposed` (R-001 Change 8): each row needs human review before it is applied. After you
decide, R-021 (new) applies the drafts mechanically from `VALUE_MAPPING.csv` and `KEY_DATA_DSO_COLUMNS.csv`.

### Not drafted this run (moved to R-020)

- `LK_PRICING_RULE`, `LK_AUCTION_TYPE`, `LK_AGGREGATION_LEVEL` and `LK_SETTLEMENT_TYPE`. Their values are already
  mapped in `VALUE_MAPPING.csv` (status `deferred`).
- `MECHANISM_ORG_ROLE` and a role lookup. The sourced role facts are recorded below so that R-020 can use them.
- Codes from R-001 Change 6 that no current row uses:
  - classes `network_charge`, `system_charge`, `policy_levy`, `tax`, `emissions_trading`, `certificate_scheme`;
  - categories `network_cost_recovery`, `decarbonisation`;
  - commodity `emissions_allowance`.

  They stay reserved. R-002 and R-003 add them, each with a sourced definition, when they draft the rows that use
  them. This keeps every published code backed by a source.

## Decisions needed

Each decision has a recommended default. "Approve the recommendations" is a valid answer.

| # | Decision | Recommended | Alternatives |
|---|---|---|---|
| D1 | Columns added to the R-001 Change 5/6 designs | Keep the added columns, appended last so they can be dropped cleanly. ORGANISATIONS: `registry_id`, `source_id`, `notes`. SOURCES: move reuse terms from `notes` into a new `reuse_terms` column. | Strict Change 5/6 columns, with organisation sources held only in CITATIONS |
| D2 | `ORGANISATIONS.licence_id` | Drop it. Ofgem's licensee list identifies licensees by company name and number, not by a licence number, so `registry_id` plus `org_type = dno_licensee` covers it. | Keep it blank |
| D3 | `registry_id` format | org-id.guide style, e.g. `GB-COH-11014226` (https://org-id.guide/list/GB-COH) | Bare company number |
| D4 | Platforms | `Market Platform` maps to the organisation (role `platform`). Also add a small `LK_PLATFORM` lookup (code, label, operator_org_id, url, source_id) for named systems such as NESO EAC, NESO SMP, Piclo Flex and NGED Market Gateway. Record EUPHEMIA as an algorithm attribute, not as a platform or organisation. | Organisation only, which loses the system names |
| D5 | Commodity model | **Option A** (drafted): the physical quantity (`active_power` and so on). Whether a mechanism pays for energy or for availability is already recorded in `MARKET_INFO` `Availability Payment` / `Utilisation Payment`. | **Option B** (R-001 Change 6 starting list): split `active_energy` from `active_power_capacity` row by row. This needs a judgement for every row that pays both availability and utilisation (STOR, SA+OU, VA+OU). |
| D6 | `Flat` (spot markets) | `both` (participants buy or sell) | `not_applicable` |
| D7 | Re-typing and fills (flagged rows) | Accept, as sourced in the mapping tables below | Reject individually |
| D8 | DSO columns on KEY_DATA | Add `Standard Product` and `Standard Variant` (both foreign keys). Keep `product_fit` only in `LK_DSO_PRODUCT_VARIANT`, because it follows from the variant. | As R-008 Change 1, with a third column `Product Fit` |
| D9 | DSO code style | Lower-case FMR-PD codes (`sa_ou_15`), with the official code kept in `external_code` (`SA OU-15`) | Long words (`scheduled_availability_operational_utilisation_15min`) |
| D10 | How R-021 applies the codes | Replace the text with codes in place; the old text is kept in `research/change_log.csv`. Add `Mechanism Class` and `Category`, then drop `Market Type`. Readable labels come from the SQLite views (R-018). | Add parallel code columns and keep the text until Phase 3 |
| D11 | Header style of new KEY_DATA columns | Match the file's current style now (`Mechanism Class`, `Category`, `Standard Product`, `Standard Variant`), and rename to snake_case in Phase 3 | snake_case now |

## Changes

### 1. ORGANISATIONS (draft: `research/drafts/R-009/ORGANISATIONS.csv`)

Columns: `org_id, name, short_name, org_type, parent_org_id, licence_id, url, valid_from, valid_to,
predecessor_org_id` (Change 6), followed by `registry_id, source_id, notes` (D1).

| ID | Name (short) | Type | Parent / predecessor | Main source |
|---|---|---|---|---|
| ORG-0001 | National Energy System Operator Limited (NESO) | system_operator | predecessor ORG-0002; from 2024-10-01 | SRC-0001 gov.uk designation |
| ORG-0002 | National Grid Electricity System Operator Limited (National Grid ESO) | system_operator | to 2024-09-30; same company as ORG-0001 | SRC-0002 Companies House |
| ORG-0003 | Elexon Limited | code_administrator | | SRC-0019 |
| ORG-0004 | EMR Settlement Limited (EMRS) | settlement_agent | parent ORG-0003 | SRC-0020 |
| ORG-0005 | Low Carbon Contracts Company Ltd (LCCC) | counterparty | parent ORG-0007 | SRC-0021 |
| ORG-0006 | Electricity Settlements Company Ltd (ESC) | counterparty | | SRC-0020 |
| ORG-0007 | Department for Energy Security and Net Zero (DESNZ) | government_department | | SRC-0024 |
| ORG-0008 | Office of Gas and Electricity Markets (Ofgem) | regulator | | SRC-0025 |
| ORG-0009 | Energy Networks Association Limited (ENA) | industry_body | | SRC-0028 |
| ORG-0010 | EPEX SPOT SE | exchange | | SRC-0005 |
| ORG-0011 | Nord Pool AS | exchange | | SRC-0006 |
| ORG-0012 | European Energy Exchange AG (EEX) | exchange | | SRC-0009 |
| ORG-0013 | ICE Futures Europe (ICE) | exchange | | SRC-0010 |
| ORG-0014 | National Grid Electricity Distribution (NGED) | dno | predecessor ORG-0015; from 2022-09-20 | SRC-0011 |
| ORG-0015 | Western Power Distribution (WPD) | dno | to 2022-09-19 | SRC-0002 |
| ORG-0016 | Northern Powergrid (NPg) | dno | | SRC-0012 |
| ORG-0017 | SP Energy Networks (SPEN) | dno | | SRC-0013 |
| ORG-0018 | SP Electricity North West (SPENW) | dno | predecessor ORG-0019; from 2025-08-04 | SRC-0014 |
| ORG-0019 | Electricity North West (ENWL) | dno | to 2025-08-03 | SRC-0014 |
| ORG-0020 | SSEN Distribution (SSEN) | dno | | SRC-0015 |
| ORG-0021 | UK Power Networks (UKPN) | dno | | SRC-0016 |
| ORG-0022..0024 | Eastern / London / South Eastern Power Networks plc (EPN, LPN, SPN) | dno_licensee | parent ORG-0021 | SRC-0003 Ofgem licensee list |
| ORG-0025 | Electricity North West Limited | dno_licensee | parent ORG-0018 | SRC-0003 |
| ORG-0026..0029 | NGED (East Midlands / South Wales / South West / West Midlands) plc | dno_licensee | parent ORG-0014 | SRC-0003 |
| ORG-0030..0031 | Northern Powergrid (Northeast / Yorkshire) plc | dno_licensee | parent ORG-0016 | SRC-0003 |
| ORG-0032..0033 | Scottish Hydro Electric Power Distribution plc (SHEPD), Southern Electric Power Distribution plc (SEPD) | dno_licensee | parent ORG-0020 | SRC-0003 |
| ORG-0034..0035 | SP Distribution plc (SPD), SP Manweb plc (SPM) | dno_licensee | parent ORG-0017 | SRC-0003 |

Design notes:
- **The mechanism operator is the DNO group.** A group such as NGED trades under one name for several licensees.
  The licensee rows are included because DUoS charges (R-003) are set per licence area.
- **Former names get their own rows**, linked by `predecessor_org_id` and bounded by `valid_from` / `valid_to`
  (the last day the name applied). Older sources that say National Grid ESO, WPD or Electricity North West then
  still resolve.
- **NESO and NGESO share a `registry_id`**, because Companies House shows one company renamed on 1 October 2024.
- **Bodies not added:** ultimate parent companies (National Grid plc, SSE plc, Iberdrola / ScottishPower, Berkshire
  Hathaway Energy, Euronext, Deutsche Börse), clearing houses (ICE Clear Europe, ECC) and DSO platforms (Piclo).
  R-020 adds them when a role row needs them.

### 2. SOURCES (draft: `research/drafts/R-009/SOURCES.csv`)

There are 45 rows, all primary except `SRC-0042` (internal: the R-001 proposal, for the in-house vocabularies
`LK_STATUS`, `LK_YESNO`, and `both` / `not_applicable` in `LK_DIRECTION`).
- SRC-0011 to SRC-0017, SRC-0026 to SRC-0030 and SRC-0043 to SRC-0045 are R-008's sources S1, S3-S6, S8, S9,
  S11-S13 and S15-S19, given permanent IDs. R-008's S2, S7 and S14 are not cited by any draft row, so they are not
  included.
- The reuse terms found are recorded in `notes` (see D1):

| Publisher | Reuse terms found | Sources |
|---|---|---|
| GOV.UK (DESNZ) | Open Government Licence v3.0, except where otherwise stated | SRC-0001, 0021, 0022, 0024 |
| Ofgem | Crown copyright, reusable under the OGL; logos and third-party material excluded (https://www.ofgem.gov.uk/copyright) | SRC-0003-0005, 0017, 0023, 0025, 0041 |
| NESO website | Site terms reserve NESO's rights in the content; copies for own use only | SRC-0031-0037, 0039, 0040 |
| NESO Grid Code | "(c) 2026 ... all rights reserved"; reproduction limited | SRC-0038 |
| Nord Pool | Terms page read; no reuse statement found | SRC-0006-0008 |
| Elexon, ENA, EEX, ICE, DNOs, Companies House, EMRS | Not checked in this run | R-019 |

Because NESO and ENA material is all rights reserved, every definition in the lookups is written in my own words,
and none quotes those sources. The R-008 proposal quotes ENA text; those quotes are not carried into the lookups.

### 3. DSO lookups and the KEY_DATA standard-product columns (R-008 Changes 1-2)

**`LK_DSO_STANDARD_PRODUCT`** (`code, label, definition, source_id, external_code`):
`su`, `pr`, `ou`, `sa_ou`, `va_ou`. Source: SRC-0026 (FMR-PD v4.2, Tables 3 and 5).

**`LK_DSO_PRODUCT_VARIANT`** (`code, label, definition, source_id`, followed by `external_code, product_code,
product_fit, payment_structure, availability_refinement, max_response_time_min, utilisation_instruction_timing,
nearest_product_code`):

| Code | FMR-PD code | Product | Fit | Response (min) | Instruction | Source |
|---|---|---|---|---|---|---|
| su, pr | SU, PR | su, pr | standard | not_applicable | at_trade | SRC-0026 |
| ou_2, ou_15 | OU-2, OU-15 | ou | standard | 2, 15 | real_time | SRC-0026 |
| sa_ou_2, sa_ou_15 | SA OU-2, SA OU-15 | sa_ou | standard | 2, 15 | real_time | SRC-0026 (added by FLX CP003, SRC-0030) |
| sa_ou_da, sa_ou_wa | SA OU-DA, SA OU-WA | sa_ou | standard | not_applicable | operational day / week ahead | SRC-0026 |
| va_ou_2, va_ou_15 | VA OU-2, VA OU-15 | va_ou | standard | 2, 15 | real_time | SRC-0026 |
| va_ou_da, va_ou_wa | VA OU-DA, VA OU-WA | va_ou | standard | not_applicable | operational day / week ahead | SRC-0026 |
| legacy_sustain, legacy_secure, legacy_dynamic, legacy_restore | (ENA names) | blank; nearest su / sa_ou / sa_ou / ou | legacy | not_applicable | not_applicable | SRC-0029 |
| npg_flexadvance | FlexAdvance | blank; nearest su | non_standard | not_applicable | not_applicable | SRC-0012 |

The parameter columns are checked against the FMR-PD v4.2 Table 3 text. Availability refinement is `week_ahead` for
VA OU-2, -15 and -DA and `month_ahead` for VA OU-WA. For the legacy and non-standard rows the FMR-PD parameter columns
are `not_applicable`, and the definitions give their payment structure instead.

**New KEY_DATA columns** (D8, D11): `Standard Product` (foreign key to `LK_DSO_STANDARD_PRODUCT`) and
`Standard Variant` (foreign key to `LK_DSO_PRODUCT_VARIANT`). They are filled only for `dso_flexibility` rows and
blank elsewhere; R-010's validator should enforce this. Per-row values, with a source and locator for each, are in
`KEY_DATA_DSO_COLUMNS.csv`. They are R-008 Change 2 in the new codes:

| File | Key | Column | Current | Proposed (Standard Product / Standard Variant) | Source |
|---|---|---|---|---|---|
| KEY_DATA.csv | MEC-0067 | new | (absent) | (blank) / legacy_dynamic | SRC-0043 PDF p.5-6; SRC-0029 p.9 |
| KEY_DATA.csv | MEC-0068 | new | (absent) | ou / ou_15 | SRC-0011 PDF p.6, p.15 |
| KEY_DATA.csv | MEC-0069 | new | (absent) | (blank) / legacy_restore | SRC-0043 PDF p.5-6 |
| KEY_DATA.csv | MEC-0070 | new | (absent) | sa_ou / sa_ou_da | SRC-0011 PDF p.6, p.15 |
| KEY_DATA.csv | MEC-0071 | new | (absent) | (blank) / legacy_secure | SRC-0043 PDF p.5-6 |
| KEY_DATA.csv | MEC-0072, 0073, 0074 | new | (absent) | su / su | SRC-0011 PDF p.6, p.15 |
| KEY_DATA.csv | MEC-0075 | new | (absent) | su / su | SRC-0012 PDF p.16 |
| KEY_DATA.csv | MEC-0076 | new | (absent) | **hold** (R-008 Change 3) | SRC-0012 PDF p.16 |
| KEY_DATA.csv | MEC-0077, 0078, 0079 | new | (absent) | sa_ou / sa_ou_wa | SRC-0012 PDF p.11, p.16 |
| KEY_DATA.csv | MEC-0080, 0081 | new | (absent) | (blank) / npg_flexadvance | SRC-0012 PDF p.3, p.9, p.16 |
| KEY_DATA.csv | MEC-0082, 0083, 0084 | new | (absent) | sa_ou / sa_ou_15 | SRC-0012 PDF p.14, p.21 |
| KEY_DATA.csv | MEC-0085, 0087 | new | (absent) | su / su | SRC-0044 PDF p.6-7 |
| KEY_DATA.csv | MEC-0086 | new | (absent) | sa_ou / sa_ou_wa | SRC-0045 s.6.1; SRC-0030 |
| KEY_DATA.csv | MEC-0088 | new | (absent) | su / su | SRC-0045 Table 2 |
| KEY_DATA.csv | MEC-0089, 0090 | new | (absent) | ou / ou_15 | SRC-0013 PDF p.8 |
| KEY_DATA.csv | MEC-0091 | new | (absent) | sa_ou / sa_ou_da | SRC-0013 PDF p.7 |
| KEY_DATA.csv | MEC-0092, 0093 | new | (absent) | su / su | SRC-0013 PDF p.7 |
| KEY_DATA.csv | MEC-0094, 0095 | new | (absent) | ou / ou_15 | SRC-0014 PDF p.10-11 |
| KEY_DATA.csv | MEC-0096, 0097 | new | (absent) | ou / ou_2 | SRC-0014 PDF p.10-11 |
| KEY_DATA.csv | MEC-0098, 0099 | new | (absent) | pr / pr | SRC-0014 PDF p.10-11 |
| KEY_DATA.csv | MEC-0100, 0101 | new | (absent) | su / su | SRC-0014 PDF p.10-11 |
| KEY_DATA.csv | MEC-0102 | new | (absent) | va_ou / va_ou_15 | SRC-0014 PDF p.11 |
| KEY_DATA.csv | MEC-0103 | new | (absent) | va_ou / va_ou_2 | SRC-0014 PDF p.11; SRC-0026 Table 5 |
| KEY_DATA.csv | MEC-0104 | new | (absent) | ou / ou_2 | SRC-0015 PDF p.6 |
| KEY_DATA.csv | MEC-0105, 0106 | new | (absent) | sa_ou / sa_ou_da | SRC-0015 PDF p.4, p.6 |
| KEY_DATA.csv | MEC-0107, 0108 | new | (absent) | su / su | SRC-0015 PDF p.4 |
| KEY_DATA.csv | MEC-0109 | new | (absent) | va_ou / va_ou_wa | SRC-0015 PDF p.4, p.6 |
| KEY_DATA.csv | MEC-0110 | new | (absent) | sa_ou / sa_ou_da | SRC-0016 PDF p.6 |
| KEY_DATA.csv | MEC-0111, 0112 | new | (absent) | su / su | SRC-0016 PDF p.6 |

Counts: 40 standard, 3 legacy, 2 non-standard and 1 on hold, matching R-008.

### 4. Other lookups drafted

| Lookup | Codes (source_id) |
|---|---|
| LK_MECHANISM_CLASS | exchange_auction (SRC-0007), exchange_continuous (SRC-0008), exchange_derivative (SRC-0010), otc_bilateral (SRC-0041), so_ancillary_service (SRC-0031), balancing_mechanism (SRC-0037), dso_flexibility (SRC-0017), capacity_mechanism (SRC-0022), revenue_support_scheme (SRC-0021) |
| LK_CATEGORY | energy (SRC-0041), frequency_response and reserve (SRC-0032), thermal_constraint (SRC-0036), voltage (SRC-0035), stability (SRC-0033), restoration (SRC-0034), capacity_adequacy (SRC-0022), investment_support (SRC-0021) |
| LK_STATUS | live, planned, trial, suspended, closed (SRC-0042). Status only makes sense with a date, so add `status_as_of` (R-001 Change 6), filled by R-006 |
| LK_COMMODITY | active_power and reactive_power (SRC-0038 Grid Code GD), stability (SRC-0033), firm_capacity (SRC-0022) |
| LK_DIRECTION | up and down (SRC-0037: an offer means generating more or consuming less, a bid the reverse), both and not_applicable (SRC-0042) |
| LK_YESNO | yes, no, not_applicable, unknown (SRC-0042, R-001 Change 7) |
| LK_CONTRACT_LENGTH_BAND | le_day, day_to_week, week_to_month, month_to_year (SRC-0027, FMR-SMD "Auction contract length"). `gt_year` from Change 6 is left out until a source or a row uses it |
| LK_ORG_TYPE | system_operator, dno, dno_licensee, exchange, regulator, government_department, counterparty, settlement_agent, code_administrator, industry_body. `transmission_owner` and `broker` (Change 6) are left out until used |

**Sign convention for direction.** `up` means the mechanism increases net export to the system (more generation or
less demand). Under this convention DC Low is `up` and DC High is `down`, which matches the data today.

### 5. Value mapping: every current categorical value

The full machine-readable version is `research/drafts/R-009/VALUE_MAPPING.csv` (111 rows). The script that builds it
fails unless each value's ID set matches `CSV/` exactly. Status key:
- `clean`: a one-to-one rename.
- `flag`: the value maps, but the row needs your attention.
- `fill`: a new, sourced value for a blank cell.
- `unmapped`: left blank, for the item named.
- `deferred`: the code is known but its lookup is drafted in R-020 or Phase 3.

**KEY_DATA `Market Type` becomes `Mechanism Class` + `Category`** (D7, D10):

| Current | IDs | Mechanism Class | Category | Status |
|---|---|---|---|---|
| Frequency Response | 0001-0009 | so_ancillary_service | frequency_response | clean |
| Reserve | 0010-0017 | so_ancillary_service | reserve | clean |
| Thermal | 0018-0020 | so_ancillary_service | thermal_constraint | clean |
| Voltage | 0021 | so_ancillary_service | voltage | clean |
| Voltage | 0022-0023 | so_ancillary_service | **stability** | flag: the Stability Markets buy inertia and short-circuit level (SRC-0033) |
| Restoration | 0024-0025 | so_ancillary_service | restoration | clean |
| Balancing Mechanism | 0026 | balancing_mechanism | energy | clean |
| Balancing Mechanism | 0027 Trading | **so_ancillary_service** | energy | flag: NESO Trading means forward bilateral trades under Grid Trade Master Agreements, not BM actions (https://www.neso.energy/industry-information/balancing-services/trading) |
| Balancing Mechanism | 0028 DFS | **so_ancillary_service** | energy | flag: DFS is a separate NESO service (https://www.neso.energy/industry-information/balancing-services/demand-flexibility-service-dfs). It replaces the LCM from 7 Oct 2026 (SRC-0036), so `thermal_constraint` may also apply |
| Forwards | 0029-0030 | **capacity_mechanism** | capacity_adequacy | flag: re-typed (SRC-0022) |
| Forwards | 0031 | **revenue_support_scheme** | investment_support | flag: re-typed (SRC-0021) |
| Forwards | 0032 | **revenue_support_scheme** | investment_support | flag: re-typed (SRC-0023) |
| Forwards | 0033-0034 | otc_bilateral | energy | clean |
| Futures | 0035-0056 | exchange_derivative | energy | clean (0035 and 0037 are options; the class covers both) |
| Wholesale Spot | 0057-0060, 0062-0065 | exchange_auction | energy | clean |
| Wholesale Spot | 0061, 0066 | exchange_continuous | energy | clean |
| DSO Flex Market | 0067-0112 | dso_flexibility | thermal_constraint | class clean; category flag (medium). For 0069 (legacy Restore), `restoration` is the alternative |

**KEY_DATA `Market Operator`, and MARKET_INFO `Market Platform`, to ORGANISATIONS:**

| File / column | Current | IDs | Proposed | Status |
|---|---|---|---|---|
| KEY_DATA Market Operator | NESO | 0001-0028 | ORG-0001 | clean |
| KEY_DATA Market Operator | NESO | 0029-0031 | ORG-0001 | flag: NESO is the EMR delivery body here, not the operator (see role facts below) |
| KEY_DATA Market Operator | EEX | 0040-0056 | ORG-0012 | clean |
| KEY_DATA Market Operator | ICE | 0035-0039 | ORG-0013 | clean |
| KEY_DATA Market Operator | EPEX Spot | 0057-0061 | ORG-0010 | clean |
| KEY_DATA Market Operator | Nord Pool | 0062-0066 | ORG-0011 | clean |
| KEY_DATA Market Operator | NGED | 0067-0074 | ORG-0014 | clean |
| KEY_DATA Market Operator | NPg | 0075-0088 | ORG-0016 | clean |
| KEY_DATA Market Operator | SPEN | 0089-0093 | ORG-0017 | clean |
| KEY_DATA Market Operator | SPENW | 0094-0103 | ORG-0018 | clean |
| KEY_DATA Market Operator | SSEN | 0104-0109 | ORG-0020 | clean |
| KEY_DATA Market Operator | UKPN | 0110-0112 | ORG-0021 | clean |
| KEY_DATA Market Operator | Brokers & Bilaterals | 0033-0034 | (blank) | unmapped: not an organisation; the `otc_bilateral` class carries the meaning |
| KEY_DATA Market Operator | (blank) | 0032 | ORG-0008 Ofgem | fill: DESNZ tasked Ofgem with implementing the LDES cap and floor (SRC-0023) |
| MARKET_INFO Market Platform | NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP) | 0001-0007, 0009-0011 | ORG-0001 (role `platform`) | flag: EAC and SMP are NESO systems (SRC-0039, SRC-0040); NESO spells it "Single Markets Platform" (D4) |
| MARKET_INFO Market Platform | EPEX Spot | 0057-0060 | ORG-0010 | clean |
| MARKET_INFO Market Platform | Nord Pool | 0062-0063 | ORG-0011 | clean |
| MARKET_INFO Market Platform | Nord Pool / EUPHEMIA | 0064-0065 | ORG-0011 | flag: EUPHEMIA is a price-coupling algorithm (D4) |

**Status, Commodity, Direction, Contract Length Band** (D5, D6):

| Column | Current | IDs | Code | Status |
|---|---|---|---|---|
| Status | Live | all except 0018, 0020-0023, 0030 | live | clean. Doubts go to R-006, e.g. 0019 LCM, which DFS replaces from 7 Oct 2026 (SRC-0036) |
| Status | Planned | 0020-0023 | planned | clean. R-006: NESO launched its first Y-4 stability tender in 2025 (SRC-0033), so 0023 may now be live |
| Status | (blank) | 0018, 0030 | (blank) | unmapped (R-006) |
| Commodity | Active Power | 0001-0009, 0012-0020, 0024-0028, 0033, 0057-0112 | active_power | clean |
| Commodity | Active Power Capacity | 0010-0011 | active_power | flag (D5): their availability payment is already recorded in MARKET_INFO |
| Commodity | Reactive Power | 0021 | reactive_power | clean |
| Commodity | Reactive Power | 0022-0023 | **stability** | flag (SRC-0033) |
| Commodity | Financial Futures | 0035-0039 | active_power | flag: "financial" describes settlement, and ICE UK Base futures are physically delivered via ECVNs (SRC-0010). Settlement goes to `LK_SETTLEMENT_TYPE` (R-020) |
| Commodity | Financial Futures | 0040-0056 | active_power | flag: EEX lists "Cash settlement / Physical fulfilment" (SRC-0009) |
| Commodity | Financial Forwards | 0034 | active_power | flag: Ofgem says OTC Financial deals have no physical delivery (SRC-0041, para 2.13) |
| Commodity | (blank) | 0029-0030 | firm_capacity | fill (SRC-0022) |
| Commodity | (blank) | 0031 | active_power | fill: CfD pays per unit of electricity generated (SRC-0021) |
| Commodity | (blank) | 0032 | (blank) | unmapped (R-002) |
| Direction | Up | 0002, 0004, 0006, 0009, 0010, 0012, 0014 | up | clean |
| Direction | Down | 0001, 0003, 0005, 0011, 0013, 0015, 0018 | down | clean |
| Direction | Up/Down | 0007-0008 | both | clean |
| Direction | Up/Down | 0067-0112 | both | flag: most DSO sub-markets are turn-down only, i.e. `up` (R-013) |
| Direction | Flat | 0057-0066 | both | flag (D6) |
| Direction | N/A | 0034, 0040-0056 | not_applicable | clean |
| Direction | N/A | 0035-0039 | not_applicable | flag: ICE futures are physically delivered, so `both` may fit better (R-005) |
| Direction | (blank) | 0016-0017, 0019-0033 | (blank) | unmapped (R-005) |
| Contract Length Band | Month < x <= Year / Week < x <= Month / Day < x <= Week / Less Than or Equal to a Day | 10 / 8 / 1 / 1 rows | month_to_year / week_to_month / day_to_week / le_day | clean |

**Remaining columns** (codes known; their lookup files come in R-020 or Phase 3):

| File / column | Current -> code | Status |
|---|---|---|
| MARKET_INFO Pricing Structure | Pay-as-Clear -> pay_as_clear (19 rows) | deferred (LK_PRICING_RULE) |
| MARKET_INFO Auction Type | Closed Double Sided -> sealed_double_sided (14 rows) | deferred (LK_AUCTION_TYPE) |
| MARKET_INFO Market Structure | One-to-Many -> one_to_many; Many-to-Many -> many_to_many | deferred: Change 6 has no lookup for this. R-020 to propose one, or to drop the column, since `mechanism_class` already implies it |
| MARKET_INFO Market Objective | Maximise Social Welfare -> maximise_social_welfare; `Nor` (0065) -> unmapped (truncated, R-005) | deferred |
| MARKET_INFO Market Co-Optimisation | Yes: Response & Reserve -> yes, plus `co_optimised_with` relationship rows (Change 13) | flag |
| MARKET_INFO Availability Payment, Parent-Child Orders, Block Orders | Yes -> yes | clean |
| MARKET_INFO Utilisation Payment | No -> no; Yes (via. BM) (0010-0011) -> yes, with "via BM" moved to a note or a `settles_via` relationship | clean / flag |
| DISPATCH Dispatcher | NESO -> ORG-0001; N/A -> not_applicable; Self -> self (Change 10) | clean / deferred |
| DISPATCH Dispatch Type | Auto -> automatic_frequency; Self -> self_dispatch; N/A -> not_applicable; BOA/OBP (0010-0011) -> boa + obp (multi-valued) | deferred (Phase 3 Change 10) / flag |
| DISPATCH Pre-Fault, Post-Fault | Yes / No / N/A -> yes / no / not_applicable | clean |
| PARTICIPANTS BMUs, Non-BMUs, Generation, Demand, Storage | Yes -> yes | clean |
| PARTICIPANTS Suppliers | No? (0001-0006) -> no, with confidence `low` (Change 7) | flag |
| PARTICIPANTS Aggregation | GSP -> gsp; National -> national | deferred (LK_AGGREGATION_LEVEL). Check whether the service terms mean GSP or GSP Group |

Out of scope for lookups: `Market Timing`, `Market Period`, `Settlement Period`, `Period Coverage`, `Payment Unit`,
`Maximum Block Size` and the numeric TECHNICAL columns. These are restructured in Phase 3 (R-001 Changes 9 and 11).

### 6. Sourced role facts for MECHANISM_ORG_ROLE (input to R-020; not drafted as a table)

| Mechanism | Role | Organisation | Source |
|---|---|---|---|
| MEC-0031 CfD | policy owner (publisher) | ORG-0007 DESNZ | SRC-0021 |
| MEC-0031 CfD | counterparty | ORG-0005 LCCC | SRC-0021 |
| MEC-0031 CfD | delivery body (allocation) | ORG-0001 NESO (the page still says National Grid ESO) | SRC-0021 |
| MEC-0031 CfD | settlement agent | ORG-0004 EMRS | SRC-0020 |
| MEC-0031 CfD | appeals (certain) | ORG-0008 Ofgem | SRC-0021 |
| MEC-0029/0030 CM | settlement body (counterparty) | ORG-0006 ESC | SRC-0020 |
| MEC-0029/0030 CM | settlement agent | ORG-0004 EMRS | SRC-0020 |
| MEC-0029/0030 CM | policy owner (publisher) | ORG-0007 DESNZ | SRC-0022 |
| MEC-0032 LDES | policy owner / delivery | ORG-0007 DESNZ / ORG-0008 Ofgem | SRC-0023 |
| MEC-0001-0007, 0009-0011 | platform | ORG-0001 (EAC / SMP) | SRC-0039, SRC-0040 |

Not yet sourced: NESO's role as Capacity Market delivery body (the gov.uk CM collection page does not state it; the
EMR Delivery Body site did not load). R-020 should source it.

## Confidence and caveats

- **High confidence:**
  - licensee names and company numbers (Ofgem list of 14 April 2026, cross-checked with Companies House for
    03600574 and 02366949);
  - the NESO/NGESO and WPD/NGED rename dates (Companies House);
  - the FMR-PD variant parameters (re-checked against the v4.2 Table 3 text);
  - the value-to-code mapping (machine-checked against `CSV/`).
- **Medium confidence:**
  - SPENW `valid_from` 2025-08-04 comes from the Iberdrola press release cited in R-001, which returned 403 in this
    run. The SPENW statement confirms the rebrand but gives no date.
  - NGED `valid_from` uses the licensees' Companies House rename date (20 September 2022); the brand launch may differ
    by a few days.
  - The DSO `thermal_constraint` category.
  - The legacy DSO "nearest product" (inferred in R-008).
- **Left blank on purpose** (not confirmed from a primary source in this run):
  - Nord Pool's `registry_id`. Ofgem's 2015 designation gives 984 058 098, but under the name Nord Pool Spot AS.
  - EEX's German register number.
  - ESC's parent and website.
  - DESNZ's creation date.
- **Ofgem's caveat:** its licensee lists "are not formal Public Register documents and should not be relied upon".
  Companies House is the better authority for names and numbers.
- **Dated sources:**
  - the EPEX SPOT SE registration (Ofgem 2016 decision);
  - "National Grid ESO" on the gov.uk CfD page;
  - the Grid Code GD Issue 6 Rev 40 (May 2026). A later revision may exist.
- **Access problems:** WebFetch could not verify, or was refused by, several domains (UKPN, ENWL, Nord Pool, EEX,
  EPEX, Iberdrola, LCCC, ENA). Pages were read with `curl` where possible. EPEX SPOT's site refused both routes, so
  EPEX facts rest on Ofgem's decision.

## Questions for the human

1. Decisions D1-D11 above. "Approve the recommendations" is a valid answer.
2. The re-typed and filled values (D7) change meaning, not just spelling:
   - CM, CfD and LDES are no longer `Forwards`;
   - MEC-0022/0023 become `stability`;
   - MEC-0027/0028 become `so_ancillary_service`;
   - LDES operator = Ofgem;
   - CM commodity = `firm_capacity`; CfD commodity = `active_power`.

   Approve all of them, or list the ones to reject.

## Human decisions (2026-11-23)

- **D1-D7 and D9-D11:** approved as recommended, including every D7 re-typing and fill. Both
  judgement calls take the recommended value: the DSO category is `thermal_constraint`, including
  for MEC-0069 legacy Restore.
- **D8 (amended):** add only `Standard Variant` to KEY_DATA. `Standard Product` is not added, because
  `LK_DSO_PRODUCT_VARIANT.product_code` already records it, so a second column could drift.
  `product_fit` stays in the lookup.
- **Human change 1: contract length.** `LK_CONTRACT_LENGTH_BAND` holds the range in two columns instead
  of in one cell: `min_duration_exclusive` and `max_duration_inclusive`, as ISO 8601 durations (e.g.
  `P7D`, `P1M`). The labels are now words ("More than 1 week, up to 1 month"). The human also asked
  for a later review: as research covers more markets, would contract length be better recorded as
  yes/no for set durations? Logged as R-022.
- **Human change 2: mechanism classes.** `LK_MECHANISM_CLASS` must allow other kinds of mechanism,
  e.g. BSUoS charges and carbon taxes. The reserved classes from R-001 Change 6 cover these
  (`system_charge`, `network_charge`, `tax`, `emissions_trading`, `policy_levy`,
  `certificate_scheme`). They are added, with sourced definitions, when R-002 / R-003 draft the
  rows. R-010 checks allowed values against the lookup files, not against a fixed list in the
  schema, so a new class needs only a new lookup row. Recorded in R-001 Change 6.

**How R-021 applied it (main session, 2026-11-23):**
- **Converted now:** a column is converted only if every non-blank value in it can be converted. So
  KEY_DATA Market Type, Market Operator, Status, Commodity, Direction and Contract Length Band are
  converted, as are the yes/no columns in MARKET_INFO, DISPATCH and PARTICIPANTS.
- **Left as text until their lookups exist:** MARKET_INFO Market Platform (converting now would lose
  the EAC/SMP system names before `LK_PLATFORM` exists), Pricing Structure, Auction Type, Market
  Structure, Market Objective; DISPATCH Dispatcher and Dispatch Type; PARTICIPANTS Aggregation. See
  R-020.
- **Qualifiers kept:** where a mapping drops part of a value (`Yes: Response & Reserve`,
  `Yes (via. BM)`, `No?`), that part was copied into the row's `Notes`.
- **SOURCES:** the "Reuse:" text was moved from `notes` into `reuse_terms` (D1).
- **ORGANISATIONS:** `licence_id` was dropped (D2).
- **Records:** 141 rows in research/change_log.csv. Backup: research/backups/2026-11-23-pre-r021/.
