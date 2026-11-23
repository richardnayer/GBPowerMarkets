# Remaining lookups, LK_PLATFORM and MECHANISM_ORG_ROLE
**Backlog item:** R-020
**Status:** pending review
**Date:** 2026-11-23
**IDs:** new `ORG-0036`..`ORG-0038`, `SRC-0046`..`SRC-0060`; proposed new prefix `MOR-` (6 digits) for MECHANISM_ORG_ROLE rows.

## Summary

R-021 left seven columns as plain text until their lookups exist. This run drafts those lookups, the
`MECHANISM_ORG_ROLE` table that replaces KEY_DATA `Market Operator` and MARKET_INFO `Market Platform`,
and a value mapping that makes applying them mechanical. It also sources NESO's role as Capacity Market
delivery body, from legislation.

All drafts are in `research/drafts/R-020/` (UTF-8 with BOM, CRLF, written with the `csv` module).
`build/build_r020.py` regenerates them. It fails unless:
- every current value in the mapped columns is covered, with exactly the IDs found in `CSV/`;
- every ORG-, SRC-, MEC-, role, platform and lookup code resolves;
- each platform row's `org_id` equals that platform's `operator_org_id`;
- each KEY_DATA operator is carried over exactly once.

Nothing in `CSV/` was changed.

| File | Rows | What it holds |
|---|---|---|
| `LK_PLATFORM.csv` | 7 | Named systems: `neso_eac`, `neso_smp`, `nged_market_gateway`, `flexible_power`, `piclo_flex`, `electronconnect`, `epex_localflex` |
| `LK_ORG_ROLE.csv` | 8 | `operator`, `delivery_body`, `policy_owner`, `counterparty`, `settlement_agent`, `regulator`, `market_platform`, `dispatch_platform` |
| `LK_PRICING_RULE.csv` | 2 | `pay_as_clear`, `pay_as_bid` |
| `LK_AUCTION_TYPE.csv` | 1 | `sealed_double_sided` |
| `LK_MARKET_STRUCTURE.csv` | 2 | `single_buyer`, `multilateral` |
| `LK_MARKET_OBJECTIVE.csv` | 1 | `maximise_social_welfare` |
| `LK_CLEARING_ALGORITHM.csv` | 1 | `euphemia` |
| `LK_DISPATCHER.csv` | 3 | `operator`, `self`, `not_applicable` |
| `LK_AGGREGATION_LEVEL.csv` | 2 | `gsp_group`, `national` |
| `MECHANISM_ORG_ROLE.csv` | 245 | 107 operator rows and 3 delivery-body rows carried over from KEY_DATA; 28 platform rows carried over from MARKET_INFO; 94 new DSO platform rows; 13 new CfD/CM/LDES role rows |
| `ORGANISATIONS_additions.csv` | 3 | ORG-0036 Piclo, ORG-0037 Chaddenwych Services Limited (Electron), ORG-0038 Flexible Power |
| `LK_ORG_TYPE_additions.csv` | 1 | `platform_provider` |
| `SOURCES_additions.csv` | 15 | SRC-0046..SRC-0060, with `reuse_terms` |
| `EXISTING_ROW_UPDATES.csv` | 2 | Notes appended to SRC-0002 and ORG-0014 |
| `VALUE_MAPPING.csv` | 51 | Same columns as R-009's: 31 clean, 12 flag, 6 fill, 2 unmapped |
| `COLUMN_ACTIONS.csv` | 10 | Per column: drop, convert in place, add, or no change |

Each lookup follows the R-009 convention: it holds only codes that rows use, and each code has a definition
in my own words and a primary source. Reserved codes (e.g. `descending_clock`, `single_seller`,
`minimise_procurement_cost`) are added when a row needs them.

## Decisions needed

"Approve the recommendations" is a valid answer.

| # | Decision | Recommended | Alternatives |
|---|---|---|---|
| D1 | MECHANISM_ORG_ROLE columns | `role_id, mechanism_id, org_id, role, platform_code, valid_from, valid_to, source_id, notes`. `role_id` uses a new prefix `MOR-NNNNNN` (add it to the R-001 Change 1a table), so that CITATIONS and the website can refer to one row. `valid_from`/`valid_to` record role changes, e.g. SPEN moving from Piclo to ElectronConnect in April 2026 | Composite key `(mechanism_id, org_id, role, platform_code)` with no ID; no validity dates |
| D2 | Role codes | The 8 codes above. R-001 Change 6's `platform` is split into `market_platform` (register, bid, see results) and `dispatch_platform` (instructions, metering, settlement), because NGED and SSEN use different systems for each. `clearing_house` waits for R-024 | A single `platform` role, losing the trading/dispatch distinction |
| D3 | KEY_DATA `Market Operator` and MARKET_INFO `Market Platform` | Drop both once the role rows are applied. The role table becomes the only record of who operates a mechanism; the SQLite views (R-018) show it as a column again. This follows the D8 reasoning for dropping `Standard Product`: a second copy could drift | Keep `Market Operator` as a copy that the validator checks against the `operator` role rows |
| D4 | LK_PLATFORM design | Columns as briefed (`code, label, definition, source_id, operator_org_id, url`), plus `notes` appended last (as in R-009 D1). A platform role row carries `platform_code`, and its `org_id` must equal the platform's `operator_org_id` (a rule for R-010). Exchange spot rows keep a blank `platform_code` (the exchange's own trading system, which has no sourced name) | Platform rows only for named systems, dropping the exchange rows |
| D5 | DSO platform rows and new organisations | Accept the 94 new rows (sourced from the 2026-27 procurement statements), ORG-0036..0038 and org type `platform_provider`. Flexible Power is recorded as its own organisation (a joint DNO initiative) | Make NGED (the trademark owner) the operator of `flexible_power` instead of ORG-0038 |
| D6 | Pricing and auction type | Convert as mapped. **MEC-0061 changes from pay-as-clear to `pay_as_bid`**: it is continuous trading, where each trade takes the price of the order already in the book | Keep MEC-0061 as `pay_as_clear`, or clear it (R-005) |
| D7 | `Market Structure` | Keep it, with `LK_MARKET_STRUCTURE`. The codes say who is single: `single_buyer` (was One-to-Many) and `multilateral` (was Many-to-Many). `mechanism_class` does not always fix the structure: NESO Trading (MEC-0027) is bilateral, and the interconnector capacity auctions now in scope (R-001 Q7) have a single seller | (a) Drop the column, as R-009 suggested; (b) keep the codes `one_to_many` / `many_to_many` |
| D8 | `Market Objective` | Keep it, with `LK_MARKET_OBJECTIVE`. It separates welfare-maximising auctions from cost-minimising procurement (e.g. SSEN stacks bids by price, SRC-0015 PDF p.17). Clear MEC-0065's truncated `Nor` | Drop the column |
| D9 | EUPHEMIA (R-009 D4) | Add MARKET_INFO `Clearing Algorithm` (after `Market Objective`), with `LK_CLEARING_ALGORITHM`; MEC-0064/0065 = `euphemia`, flagged as carried over and unconfirmed (R-026) | Keep "EUPHEMIA" only in MARKET_INFO `Notes` until R-026 confirms it |
| D10 | DISPATCH `Dispatcher` | Hold codes from `LK_DISPATCHER`: `operator` (the mechanism's operator instructs), `self`, `not_applicable`. The organisation is read from the operator role row, so the column never mixes ORG IDs and words. If a mechanism is ever dispatched by someone other than its operator, add a `dispatcher` role then | Drop `Dispatcher` in Phase 3 and derive it from Change 10's `dispatch_method` |
| D11 | PARTICIPANTS `Aggregation` | `LK_AGGREGATION_LEVEL`. `GSP` becomes `gsp_group` (8 rows), because NESO's rules say GSP Group; Static FFR `National` becomes `national` (medium confidence) | Keep `gsp` and note the difference |
| D12 | Scope split | Move `LK_SETTLEMENT_TYPE` and the clearing-house organisations and roles (ICE Clear Europe, ECC) to a new item, R-024. No current column uses them; they belong to Phase 4 `INSTRUMENT_INFO` | Do them in R-020 |

Also needed: approval of the 12 flagged mapping rows. They are listed in "Changes" below; the main ones
are MEC-0007 and MEC-0009 (R-027).

## Changes

### 1. NESO as Capacity Market (and CfD) delivery body: now sourced

R-009 could not source this. The chain is now complete and every link is primary legislation, which is
reusable under the OGL:
1. The Electricity Capacity Regulations 2014, reg 2: "Delivery Body" means the national system operator.
   Reg 24(1) says the Delivery Body must hold the capacity auction. (SRC-0051)
2. Energy Act 2013 s.27(6), substituted from 1 October 2024 by SI 2024/706 reg 9(4): the national system
   operator is the person designated as the Independent System Operator and Planner under s.162 of the
   Energy Act 2023. (SRC-0052)
3. NESO was designated ISOP with effect from 1 October 2024. (SRC-0001)

The CfD chain is the same: the CfD (Allocation) Regulations 2014 reg 2 (SRC-0053) and Energy Act 2013
s.8(3) (SRC-0052). This replaces SRC-0021, which still says "National Grid ESO". Reg 2 of the Capacity
Regulations also names the scheme's "administrative parties": the Secretary of State, the Authority
(Ofgem), the Delivery Body and the Settlement Body. These support the `policy_owner` and `regulator`
rows.

### 2. MECHANISM_ORG_ROLE (`research/drafts/R-020/MECHANISM_ORG_ROLE.csv`)

| Rows | Role | Org | Source | Origin |
|---|---|---|---|---|
| 107 | operator | as KEY_DATA today | per family: SRC-0031..0039, 0050 (NESO); 0005, 0007-0010, 0060 (exchanges); 0011-0016 (DNOs); 0023 (LDES) | carried over, `clean` |
| 3 | delivery_body | ORG-0001 for MEC-0029, 0030, 0031 | SRC-0051, SRC-0053 (plus SRC-0052, SRC-0001) | carried over; role corrected from operator (resolves the R-009 flag) |
| 4 | policy_owner | ORG-0007 DESNZ for MEC-0029..0032 | SRC-0021, 0022, 0023 | new (R-009 section 6) |
| 3 | counterparty | ORG-0006 ESC (CM), ORG-0005 LCCC (CfD) | SRC-0020, SRC-0021 | new |
| 3 | settlement_agent | ORG-0004 EMRS | SRC-0020 | new |
| 3 | regulator | ORG-0008 Ofgem for CM and CfD | SRC-0051 (CM); SRC-0021 (CfD appeals) | new |
| 20 | market_platform | ORG-0001 with `neso_eac` and `neso_smp`, MEC-0001..0006, 0010, 0011 | SRC-0039, SRC-0040 | carried over |
| 4 | market_platform | as above for MEC-0007 and MEC-0009 | SRC-0046 / SRC-0040 / SRC-0050 | carried over, **flag** (R-027) |
| 8 | market_platform | ORG-0010 EPEX (0057-0060), ORG-0011 Nord Pool (0062-0065), no `platform_code` | SRC-0005, 0007, 0060 | carried over |
| 94 | market_platform / dispatch_platform | DSO rows, see below | SRC-0011..0016, SRC-0056 | new, `fill` |

DSO platforms, from each DNO's 2026-27 procurement statement:

| DNO (rows) | market_platform | dispatch_platform | Source |
|---|---|---|---|
| NGED (0067-0074) | `nged_market_gateway` (in-house); `piclo_flex` (partner route since 2024) | `flexible_power` | SRC-0011 PDF p.6, p.22 |
| NPg (0075-0088) | `piclo_flex` | `piclo_flex`, except 0082-0084 (outage support, dispatched by telephone) | SRC-0012 PDF p.10, p.17, p.19 |
| SPEN (0089-0093) | `electronconnect`, valid from 2026-04-01 | `electronconnect`, valid from 2026-04-01 | SRC-0013 PDF p.9, p.10, p.12 |
| SPENW (0094-0103) | `electronconnect` (since March 2024) | `electronconnect` (by API, or by email if there is no API) | SRC-0014 PDF p.7, p.20 |
| SSEN (0104-0109) | `electronconnect` | `flexible_power` | SRC-0015 PDF p.14, p.26; SRC-0056 |
| UKPN (0110-0112) | `epex_localflex` | (not stated) | SRC-0016 PDF p.3, p.7, p.12 |

No rows were added for SPEN's past use of Piclo (its contract "ended at the end of Q1, 2026"), because the
exact end date is not stated.

### 3. Column conversions (full detail in `VALUE_MAPPING.csv` and `COLUMN_ACTIONS.csv`)

| File | Key | Column | Current | Proposed | Source / status |
|---|---|---|---|---|---|
| KEY_DATA.csv | all | Market Operator | ORG IDs | role rows, then drop the column (D3) | clean; 0029-0031 become `delivery_body` |
| MARKET_INFO.csv | 0001-0007, 0009-0011 | Market Platform | NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP) | 2 role rows each: `neso_eac`, `neso_smp`; then drop the column | SRC-0039/0040; flag 0007, 0009 |
| MARKET_INFO.csv | 0057-0060 / 0062-0063 | Market Platform | EPEX Spot / Nord Pool | role row ORG-0010 / ORG-0011 | clean |
| MARKET_INFO.csv | 0064-0065 | Market Platform | Nord Pool / EUPHEMIA | role row ORG-0011 + `Clearing Algorithm` = `euphemia` | flag (R-026) |
| MARKET_INFO.csv | 0001-0007, 0009-0011, 0057-0060, 0062-0065 | Pricing Structure | Pay-as-Clear | `pay_as_clear` | SRC-0046 p.8, SRC-0047 para 12.2, SRC-0048 para 13.2, SRC-0050 para 9.1; flag 0007 |
| MARKET_INFO.csv | 0061 | Pricing Structure | Pay-as-Clear | **`pay_as_bid`** | flag (D6); SRC-0055 p.15 |
| MARKET_INFO.csv | 0001-0007, 0009-0011, 0059-0060, 0062-0063 | Auction Type | Closed Double Sided | `sealed_double_sided` | SRC-0046 p.8 ("Closed double-sided auction"); SRC-0050; flag 0007 |
| MARKET_INFO.csv | 0001-0007, 0009-0011 | Market Structure | One-to-Many | `single_buyer` | SRC-0046 p.4; flag 0007 |
| MARKET_INFO.csv | 0057-0060, 0062-0065 | Market Structure | Many-to-Many | `multilateral` | clean |
| MARKET_INFO.csv | 0001-0007, 0009-0011, 0062-0064 | Market Objective | Maximise Social Welfare | `maximise_social_welfare` | SRC-0046 p.8/p.10, SRC-0047 para 9.1.1, SRC-0048 para 10.1.1, SRC-0050 para 9.2.1; flag 0007; 0062-0064 carried over |
| MARKET_INFO.csv | 0065 | Market Objective | Nor | (blank) | unmapped: truncated value (D8, R-026) |
| MARKET_INFO.csv | 0064-0065 | Clearing Algorithm (new) | (absent) | `euphemia` | flag (D9, R-026) |
| DISPATCH.csv | 0001-0007, 0009, 0033, 0057-0066 | Dispatcher | Self | `self` | automatic response, or self-dispatch to a traded position (SRC-0059) |
| DISPATCH.csv | 0010-0011 | Dispatcher | NESO | `operator` | SRC-0049 p.5, p.13 (BOAs and Instructions) |
| DISPATCH.csv | 0034-0056 | Dispatcher | N/A | `not_applicable` | clean (ICE physical delivery revisited in R-024) |
| PARTICIPANTS.csv | 0001-0006, 0010-0011 | Aggregation | GSP | `gsp_group` | flag: SRC-0047 PDF p.32 and SRC-0048 PDF p.29 say "same GSP Group" (NESO may tighten this to one GSP) |
| PARTICIPANTS.csv | 0009 | Aggregation | National | `national` | flag (medium): SRC-0050 PDF p.22 sets no location limit |

After conversion, every non-blank value in these seven columns is a code (or the column is dropped), so all
seven can be converted together. DISPATCH `Dispatch Type` is unchanged (Phase 3 Change 10).

### 4. ORGANISATIONS and SOURCES additions

| ID | Name | Type | registry_id | Source | Note |
|---|---|---|---|---|---|
| ORG-0036 | Piclo | platform_provider | (blank) | SRC-0012 | Legal entity not confirmed: Companies House lists Open Utility Ltd (08384033) and Piclo Ltd (14266869) at the same address; secondary sources say Open Utility Ltd operates Piclo |
| ORG-0037 | Chaddenwych Services Limited (Electron) | platform_provider | GB-COH-09914060 | SRC-0058 | Electron's privacy notice gives the company and number; Companies House confirms it is active |
| ORG-0038 | Flexible Power | platform_provider | (blank: not a company) | SRC-0057 | Joint initiative of NGED, NPg, SSEN and SPEN; NGED owns the trademark |

Sources, with the reuse terms found:

| IDs | What | Reuse terms |
|---|---|---|
| SRC-0046..0050, 0059 | NESO: EAC algorithm description (June 2024), Response Procurement Rules v6, QR Procurement Rules v4.0, QR Service Terms v2.1, Static FFR Procurement Rules v2.0, REMA dispatch assessment (Feb 2026) | NESO site terms: own use only. Paraphrased |
| SRC-0051..0053 | Capacity Regulations 2014, Energy Act 2013, CfD (Allocation) Regulations 2014 | Open Government Licence v3.0 (legislation.gov.uk) |
| SRC-0054, 0055 | NEMO Committee: EUPHEMIA public description (Aug 2024); continuous trading matching algorithm | "All rights reserved". Facts only, paraphrased |
| SRC-0056..0058, 0060 | SSEN Flexible Power user guide, Flexible Power site (Wayback copy), Electron privacy notice, Nord Pool SEM-GB article | Not checked (R-019) / none found |

Publishers that are not organisations (legislation.gov.uk, NEMO Committee) are written as text, as SRC-0002
is now. If R-010 D5 (a strict publisher foreign key) is approved, they join Companies House in R-032.

## Confidence and caveats

- **High confidence:**
  - the legislative chain for the delivery body;
  - the EAC auction type, objective and pricing (stated in SRC-0046 and the current Response and QR rules);
  - GSP Group as the aggregation limit (the same clause appears in the current Response and QR rules);
  - the DSO platform rows (each DNO's own 2026-27 statement).
- **Medium confidence:**
  - Static FFR `national`: inferred from the absence of a location limit, not from a positive statement.
  - `flexible_power` operated by ORG-0038, a joint initiative with no legal entity.
  - Piclo's legal entity.
  - `pay_as_bid` for MEC-0061: the source describes the EU SIDC algorithm, not EPEX's GB continuous market,
    whose site refuses automated clients. The approved class definition (`exchange_continuous`: each trade
    has its own price) already contradicts pay-as-clear.
- **Not resolved (open point, R-026): EUPHEMIA.** I found no primary source saying whether the SEM-GB intraday
  auctions still clear with EUPHEMIA after GB left SDAC:
  - Nord Pool's SEM-GB article (SRC-0060) names no algorithm.
  - The EUPHEMIA description (SRC-0054) covers SDAC and the SIDC auctions and does not mention GB.
  - SEMOpx's pages and two Ofgem 2019 decisions do not mention it either.

  The value is carried over from the existing data, flagged.
- **Carried-over values not re-verified:**
  - MEC-0062-0064's objective;
  - the exchange rows' auction type;
  - MEC-0007 (MFR, probably copied down from the EAC rows; R-001 data-quality list) and MEC-0009 (Static
    FFR: EAC not confirmed; SRC-0039 does not list it) (R-027).
- **Sources cited only in notes:** SRC-0048 and SRC-0052 support row facts but are not a row's `source_id`.
  They become proper citations when CITATIONS exists (R-023), as for R-010 Findings 2 and 3.
- **Coordination with R-010:** the new tables need `datapackage.json` resources and foreign keys, and
  dropping `Market Operator` removes a foreign key that R-010 declares. Per R-010's proposal, the schema
  update must go in the same commit as the apply step.
- **Not done:**
  - NESO's Open Balancing Platform (OBP, named in SRC-0049) is a candidate `dispatch_platform` for Quick
    Reserve. It is left for Phase 3 Change 10 with `Dispatch Type`.
  - `LK_SETTLEMENT_TYPE` and clearing houses: see D12 / R-024.

## Questions for the human

1. Decisions D1-D12 above.
2. Approve the flagged mapping rows (12), the 94 DSO platform fills and the 13 new CfD/CM/LDES role rows,
   or list the ones to reject. In particular:
   - MEC-0061 becomes `pay_as_bid`;
   - MEC-0065 `Nor` is cleared;
   - `GSP` becomes `gsp_group`;
   - the MEC-0007/0009 EAC values are carried over with flags.
