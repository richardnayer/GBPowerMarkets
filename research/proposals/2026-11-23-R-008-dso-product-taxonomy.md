# DSO flexibility product taxonomy and mapping of the 46 DSO rows
**Backlog item:** R-008
**Status:** partly approved 2026-11-23.
- Changes 4, 5 and 7 are approved and applied (`scripts/apply_r008.py`, logged in research/change_log.csv).
- The `SUB_MARKET` child-table name (Finding 4) is approved and recorded in R-001 Change 12.
- Changes 1-2 are folded into R-009.
- Change 3 (076) is on hold until the Elexon catalogue entry is checked.
- Change 6 is passed to R-006.

**Date:** 2026-11-23
**IDs:** written in the earlier 3-digit form. After R-017 (R-001 Change 1a), `067` = `MEC-0067`.
**Human input (2026-11-23):** the DSO rows were taken from the Elexon Flexibility Market Catalogue,
which confirms Finding 4. The catalogue has no data-export option.

## Summary

The R-001 review described the DSO standard products as "Sustain / Secure / Dynamic / Restore families
and their SU / SAOU / VAOU / OU payment structures". The primary sources show that description is
wrong in two ways.

1. **There are two generations of products, not a hierarchy.** Sustain, Secure, Dynamic and Restore
   were the original four ENA Open Networks products (ON20). The February 2024 ENA alignment report
   calls them "historical nomenclature" and replaces them with **five** aligned products: Peak
   Reduction (PR), Scheduled Utilisation (SU), Operational Utilisation (OU), Scheduled Availability +
   Operational Utilisation (SA+OU / SAOU) and Variable Availability + Operational Utilisation
   (VA+OU / VAOU). Each has speed or notice sub-parameters, which "will not be classed as separate
   products" [S1 p.6, p.7, p.10].
2. **Governance has moved from ENA to Elexon.** Elexon is now the Market Facilitator, and the
   standard set is a legally binding Flexibility Market Rule: **FMR-PD Product definitions**. The
   current version is v4.2, published 25/08/2026. It defines **5 standard DNO products with 12
   variants**, and DNOs must use them for at least 80% of tendered and procured volume [S4]. Three of
   the variants (SA OU-2, SA OU-15, SA OU-WA) were added on 11/06/2026 by change proposal FLX CP003,
   which **Northern Powergrid** raised [S6]. That change is why NPg's `SAOU-WA` and `SAOU-15` tender
   lines exist.

Outcome against the three goals:

- **Goal 1 (taxonomy):** confirmed from the primary documents, with a sourced definition for each
  product and variant (Finding 1). The ENA PDF that returned 403 was read from a Wayback Machine
  snapshot. The current Elexon rule supersedes it.
- **Goal 2 (mapping):** all 46 DSO rows (IDs 067-112) are mapped (Finding 2):
  - 41 map to a current standard variant. Three of these are anomalous NPg lines (076, 083, 084; see
    goal 3).
  - 3 are legacy ENA products (NGED Dynamic/Restore/Secure LT: 067, 069, 071).
  - 2 are a non-standard NPg product (FlexAdvance: 080, 081).
- **Goal 3 (NPg numbered lines):** the numbers are NPg's own **sub-market** numbers from its 2026-27
  Procurement Statement, Figure 2 [S11 PDF p.16]. They are procurement windows of a few products,
  not distinct products.
  - 077 is Sub-Market 3.
  - 076 cannot be Sub-Market 3 a second time. NPg's Sub-Market 2 is "LV SU procuring month ahead",
    so 076 is probably a mislabelled copy.
  - 082 is Sub-Market 8 (SA OU-15, planned outages). NPg defines **no Sub-Markets 9 or 10**, so 083
    and 084 are further windows of the same sub-market or duplicates.
  - IDs 085-088 are NPg's **2025/26** sub-markets, while 075-084 are its **2026/27** sub-markets.

**Note on R-001 Question 4.** This run's brief said Question 4 is still open. However, the R-001
proposal file was edited during this run and now records Question 4 as **answered 2026-11-23: "one
row per product family, with procurement windows ... in child tables"**. This proposal does not
depend on either answer. Finding 4 sets out the evidence. Please confirm which state is correct.

No CSV files have been changed.

## Sources

Every claim below cites one of these. "PDF p." is the page number in the PDF file, which can differ
from the printed page number. SHA-256 prefixes are for the copies that were read.

| ID | Document | Publisher, date | URL | Notes |
|----|----------|-----------------|-----|-------|
| S1 | Flexibility Products Review and Alignment, v1.0 | ENA Open Networks, Feb 2024 (authorised 05/12/2023) | https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf ; read via Wayback: https://web.archive.org/web/20240503005600/https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf ; landing page: https://www.energynetworks.org/publications/on-flexibility-products-review-and-alignment-(feb-2024) | The direct URL returns 403 to automated clients. sha256 `5d8d168391f21aa7...` |
| S2 | Review of standard flexibility products (rationalisation) | ENA Open Networks, Flexibility Products and Stackability TWG, Dec 2024 | https://www.energynetworks.org/assets/images/202412-rationalisation-of-dso-flexibility-products-(1)-(2).pdf | Direct fetch worked. sha256 `f65ba2ed86655cfa...` |
| S3 | ON22-WS1A-P6 Active Power Products Review | ENA Open Networks, 01 Aug 2022 | https://www.energynetworks.org/assets/images/Resource%20library/ON22-WS1A-P6%20Active%20Power%20Products%20Review%20(01%20Aug%202022).pdf | Defines and benchmarks the legacy four products. sha256 `74cf5bb2fc0e7d36...` |
| S4 | FMR-PD Product definitions, v4.2 (current); also v3.2 and v1.0 | Elexon (Market Facilitator), v4.2 published 25/08/2026; v3.2 12/05/2026; v1.0 12/12/2025 | https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions ; v3.2: https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions/v-3-2/id-6a02cada7ad07bbb59a44c0e ; v1.0: https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions/v-1-0/id-6939aa52825ab886c4047af6 | Text read from the HTML; the PDF download returned HTTP 500. v1.0 and v2.1 have 9 variants; v3.2 and v4.2 have 12. |
| S5 | FMR-SMD Sub-Market definitions, v2.1 | Elexon, published 04/02/2026, implemented 06/02/2026 | https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-smd-sub-market-definitions | Defines a "Sub-Market" and its parameters, including "Auction contract length". |
| S6 | FLX CP003 "Revision of standard product variants for Scheduled Availability + Operational Utilisation" | Elexon; proposer Northern Powergrid; raised 13/02/2026; implemented 11/06/2026 | https://www.elexon.co.uk/flexibility-markets/change-proposals/flx-cp003/ | Status: Implemented. |
| S7 | Flexibility Market Catalogue | Elexon | https://www.elexon.co.uk/flexibility-markets/implementation-monitoring/flexibility-market-catalogue/ | Power BI embed; not machine-readable, not read. |
| S8 | NGED Distribution Flexibility Services Procurement Statement 2026-27 | NGED, Apr 2026 | https://dso.nationalgrid.co.uk/downloads/15141/nged-dso-distribution-flexibility-services-procurement-statement-2026-27.pdf | sha256 `a186545be937bb23...` |
| S9 | NGED Distribution Flexibility Services Procurement Report 2025-26 | NGED, May 2026 | https://dso.nationalgrid.co.uk/downloads/15152/nged-distribution-flexibility-services-procurement-report-2025-26.pdf | sha256 `fb720330a7848ce1...` |
| S10 | Unlocking the power of flexibility: deep dive | NGED, Oct 2025 | https://dso.nationalgrid.co.uk/downloads/15098/unlocking-the-power-of-flexibility-deep-dive-oct-2025-1-.pdf | Gives the Market Gateway product codes (PDF p.20). |
| S11 | NPg Distribution Flexibility Services Procurement Statement 2026-27 | Northern Powergrid, 2026 | https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202026-27.pdf | Figure 2 (sub-markets) PDF p.16; Table 9 PDF p.21. sha256 `3e7625fff95511db...` |
| S12 | NPg Distribution Flexibility Services Procurement Statement 2025-26 v2 | Northern Powergrid, 2025 | https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202025-26%20v2.pdf | sha256 `e5baffefa73c4b66...` |
| S13 | NPg ITT NPg25565, Document 2: Scope and Specification | Northern Powergrid via Piclo, Dec 2025 | https://piclo-so-docs.s3.eu-west-2.amazonaws.com/Northern+Powergrid+/2025.12/Document+2+-+Scope+and+Specification.pdf | Month-ahead tender for 05/01/2026-01/02/2026. |
| S14 | NPg ITT NPg26308, Document 2: Scope and Specification | Northern Powergrid via Piclo, Jun 2026 | https://piclo-so-docs.s3.eu-west-2.amazonaws.com/Northern+Powergrid+/06.2026/Document+2+-+Scope+and+Specification.pdf | Planned-outage mini-competition. Links "industry-standard flexibility products" to S4. |
| S15 | Distribution Flexibility Service Procurement Statement for SP Distribution PLC and SP Manweb PLC | SP Energy Networks, Apr 2026 | https://www.spenergynetworks.co.uk/userfiles/file/SP5175_SPEN_DSO_C31E_Procurement_Statement_2026_v8_003.pdf | The SPEN URL returns 403 to automated clients. Read from the Ofgem ZIP (S19), member `SP5175 SPEN DSO C31E Procurement Statement 2026 v8.pdf`. sha256 `2a5855f2fdb9b60c...` |
| S16 | Distribution Flexibility Services Procurement Statement | SP Electricity North West, Apr 2026 | https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/sp-enw-distribution-flexibility-services-procurement-statement-2026..pdf | sha256 `0556f6843c41fd64...` |
| S17 | SSEN 2026/27 Flexibility Services Procurement Statement | SSEN Distribution, Mar/Apr 2026 | https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2026-27-flexibility-services-procurement-statement.pdf | sha256 `3c1b831f5e7b758d...` |
| S18 | UKPN Flexibility Services Procurement Statement, Apr 2026 - Mar 2027 | UK Power Networks, Mar 2026 | Read from the Ofgem ZIP (S19), member `Flexibility Services Procurement Statement 2026 v1.0.pdf` | No direct UKPN URL found. sha256 `8510a804213933d1...` |
| S19 | SLC31E flexibility procurement statements 2026 to 2027 | Ofgem | https://www.ofgem.gov.uk/transparency-document/electricity-distribution-standard-licence-condition-31e-flexibility-procurement-statements-2026-2027 ; ZIP: https://www.ofgem.gov.uk/sites/default/files/2026-06/Procurement-statements-2026-2027.zip | Regulator-hosted copies of every DNO statement. ZIP sha256 `81739a486fa2e8b7...` |

## Finding 1: the standard product set

### 1a. Timeline

| Date | Event | Source |
|------|-------|--------|
| 2020-2021 | ON20 WS1A P3 defines four standard products: Sustain, Secure, Dynamic, Restore. | S1 p.7 (Table 2 and footnote 2); S3 p.9 |
| Aug 2022 | ON22 review finds the DNOs diverge, especially on Secure and Dynamic. | S3 p.10-12 |
| Dec 2023 / Feb 2024 | ENA alignment: five products with sub-parameters, which "supersedes previous releases". At least 80% of tendered flexibility is to use them from Q2 2024. | S1 p.6, p.13, p.15 |
| Dec 2024 | ENA rationalisation. Retired: SU (Blocks / Specific Periods), OU (Week Ahead) and SA+OU (2 mins). PR and VA+OU (2 and 15 mins) are kept under review through 2025. UKPN retired PR from Oct 2024. | S2 p.1-4 |
| 12/12/2025 | Elexon FMR-PD v1.0: 5 products, 9 variants (SU, PR, OU-2, OU-15, SA OU-DA, VA OU-2/15/DA/WA). | S4 (v1.0) |
| 11/06/2026 | FMR-PD v3.2 (CP003, proposed by NPg) adds SA OU-2, SA OU-15 and SA OU-WA, making 12 variants. | S4 (v3.2), S6 |
| 25/08/2026 | FMR-PD v4.2, the current version (CP005 changed the monitoring requirements; the product table is unchanged). | S4 |

### 1b. Current standard products and variants (Elexon FMR-PD v4.2, Section 2.2 Table 3, and Table 5 for the codes)

The product definitions quoted below come from the ENA use-case descriptions [S1 p.13-14]. FMR-PD
itself defines products only by parameters, which are given in the table.

- **Peak Reduction (PR):** "This product seeks a reduction in peak power utilised over time." [S1 p.13]
- **Scheduled Utilisation (SU):** "the time that flexibility is delivered has been pre-agreed in advance with the provider." [S1 p.13]
- **Operational Utilisation (OU):** "the amount of flexibility delivered is agreed nearer to real time." [S1 p.13]
- **Scheduled Availability + Operational Utilisation (SA+OU, often written SAOU or OUSA):** "procures, ahead of time, the ability of an FSP to deliver an agreed change following a network abnormality. The availability will be defined at the point of procurement and cannot be modified once the contract has been agreed." [S1 p.13]
- **Variable Availability + Operational Utilisation (VA+OU, often written VAOU or OUVA):** allows the DNO "to procure a level of contracted capacity, but then refine the requirements in terms of availability closer to the event." [S1 p.14]

| Variant code (FMR-PD) | Product | Payment structure | Availability refinement | Max response time | Utilisation instruction timing | Delivery expectation |
|---|---|---|---|---|---|---|
| SU | Scheduled Utilisation | Utilisation only | n/a | N/A | At trade | Continuous |
| PR | Peak Reduction | Utilisation only | n/a | N/A | At trade | Peak Delivery |
| OU-2 | Operational Utilisation | Utilisation only | n/a | 2 mins | Real time | Continuous |
| OU-15 | Operational Utilisation | Utilisation only | n/a | 15 mins | Real time | Continuous |
| SA OU-2 | SA + OU | Availability and utilisation | Not allowed | 2 mins | Real time | Continuous |
| SA OU-15 | SA + OU | Availability and utilisation | Not allowed | 15 mins | Real time | Continuous |
| SA OU-DA | SA + OU | Availability and utilisation | Not allowed | N/A | Operational - Day Ahead | Continuous |
| SA OU-WA | SA + OU | Availability and utilisation | Not allowed | N/A | Operational - Week Ahead | Continuous |
| VA OU-2 | VA + OU | Availability and utilisation | Week Ahead | 2 mins | Real time | Continuous |
| VA OU-15 | VA + OU | Availability and utilisation | Week Ahead | 15 mins | Real time | Continuous |
| VA OU-DA | VA + OU | Availability and utilisation | Week Ahead | N/A | Operational - Day Ahead | Continuous |
| VA OU-WA | VA + OU | Availability and utilisation | Month Ahead | N/A | Operational - Week Ahead | Continuous |

Parameters common to all 12 variants [S4 Table 3]:
- prices set at trade;
- availability requested by the DNO and accepted at trade, with no FSP changes after acceptance;
- availability paid in GBP/MW/h per settlement period;
- utilisation paid in GBP/MWh;
- no payment during the response time;
- minimum utilisation time of 30 mins.

Minimum aggregate unit size, partial acceptance and time-variable volumes are deliberately not
aligned ("-"). These parameters fill several blank MARKET_INFO and TECHNICAL columns for the DSO rows
(see new backlog item R-015).

**Naming.** ENA (2024) wrote "Operational Utilisation + Scheduled Availability". FMR-PD writes
"Scheduled Availability + Operational Utilisation". The DNOs use SAOU, SAOU_DA, SA+OU and OUSA (NPg
2025/26) for the same product. The FMR-PD names and codes should be the canonical vocabulary.

### 1c. Legacy products (pre-2024), with the nearest current product

| Legacy product | Definition (S3 p.9; same text in S1 Table 2 p.7) | Payment / timing (S3 p.10-12) | Nearest current product (inferred) |
|---|---|---|---|
| Sustain | "The Network Operator procures, ahead of time, a pre-agreed change in input or output over a defined time period to prevent a network going beyond its firm capacity." | Pre-fault; utilisation only; schedule fixed at contract | SU. The SU use-case text matches it [S1 p.13]. |
| Secure | "The Network Operator procures, ahead of time, the ability to access a pre-agreed change in Service Provider input or output based on network conditions close to real-time." | Pre-fault / planned outage; availability and utilisation; availability agreed week-ahead, 2 weeks ahead or year-ahead, depending on the DNO | SA+OU or VA+OU, depending on the DNO. UKPN calls its SAOU the "Secure (SAOU) service" [S18 PDF p.22]. SSEN still runs "Legacy-Secure services" with availability refinement [S17 PDF p.12]. |
| Dynamic | "The Network Operator procures, ahead of time, the ability of a Service Provider to deliver an agreed change in output following a network abnormality." | Post-fault; mostly availability and utilisation (UKPN: utilisation only); real-time instruction | SA+OU (2/15 min). The SA+OU use-case text reuses this wording [S1 p.13]. |
| Restore | "Following a loss of supply, the Network Operator instructs a provider to either remain off supply, or to reconnect with lower demand, or to reconnect and supply generation to support increased and faster load restoration under depleted network conditions." | Post-fault (CI/CML); utilisation only | OU. The OU use case is restoring supplies "where the regulatory funding does not allow for availability payments e.g. customer interruptions (CI)" [S1 p.13]. |

No source gives an official one-to-one conversion. The "nearest" column is an inference from the
definitions and payment structures. NGED itself reports these four as "legacy ENA products",
separate from the "standardised Market Facilitator products" [S9 PDF p.5].

## Finding 2: mapping of the 46 DSO rows

Fit codes:
- **STD**: the row maps to an FMR-PD v4.2 variant.
- **LEGACY**: a pre-2024 ENA product.
- **NON-STD**: a DNO-specific product outside FMR-PD.
- **ANOM**: the label conflicts with the source.

| ID | DNO | Current Market Name | Standard product | FMR-PD variant | Fit | Evidence and notes |
|----|-----|---------------------|------------------|----------------|-----|--------------------|
| 067 | NGED | Dynamic LT | (legacy Dynamic; nearest SA+OU) | none | LEGACY | S9 PDF p.5-6: "legacy ENA products"; 93.47 MW contracted in prior years, 0.02 MW in 2025/26. Not in the 2026-27 product list [S8 PDF p.6]. |
| 068 | NGED | OU15 | Operational Utilisation | OU-15 | STD | S8 PDF p.6, p.15 (OU_15); S10 PDF p.20 (Market Gateway code `OU_15` = "Operational Utilisation - 15min Instruction"). |
| 069 | NGED | Restore LT | (legacy Restore; nearest OU) | none | LEGACY | S9 PDF p.6: Restore shows "-" for every column (nothing contracted). Status doubtful (R-006). |
| 070 | NGED | SAOU_DA | Scheduled Availability + Operational Utilisation | SA OU-DA | STD | S8 PDF p.6, p.15; S10 PDF p.20 (`SAOU_DA` = "... Day Ahead Notice"). |
| 071 | NGED | Secure LT | (legacy Secure; nearest SA+OU or VA+OU) | none | LEGACY | S9 PDF p.6: Secure shows "-" for every column. Status doubtful (R-006). |
| 072 | NGED | SU_HV (Day Ahead) | Scheduled Utilisation | SU | STD | S8 PDF p.15: short-term market "transitioned from Week-ahead tender to Day-ahead tender, with services procured under the SU product"; S10 PDF p.20 (`SU_HV`). |
| 073 | NGED | SU_HV (Week Ahead) | Scheduled Utilisation | SU | STD | Same source: the week-ahead window has been replaced by day-ahead. Status doubtful (R-006). |
| 074 | NGED | SU_LV | Scheduled Utilisation | SU | STD | The product is SU, but the code `SU_LV` does not appear in S8, S9 or S10. NGED reports `SU`, `SU_SPP` and `SU_SEP` [S9 PDF p.6]. Check the code. |
| 075 | NPg | 1) Reinforcement optimisation LV SU Winter ahead | Scheduled Utilisation | SU | STD | S11 Fig. 2: Sub-Market 1 "LV SU procuring winter ahead". |
| 076 | NPg | 2) Reinforcement optimisation HV SAOU-WA winter+1 ahead | (as labelled: SA+OU) | SA OU-WA as labelled; SU if the label is corrected | ANOM | S11 Fig. 2: Sub-Market 2 is "LV SU procuring month ahead". The row text duplicates 077. See Finding 3. |
| 077 | NPg | 3) Reinforcement optimisation HV SAOU-WA winter+1 ahead | Scheduled Availability + Operational Utilisation | SA OU-WA | STD | S11 Fig. 2: Sub-Market 3; S11 PDF p.11 Table 4. |
| 078 | NPg | 4) Reinforcement optimisation HV SAOU-WA winter ahead | Scheduled Availability + Operational Utilisation | SA OU-WA | STD | S11 Fig. 2: Sub-Market 4. |
| 079 | NPg | 5) Reinforcement optimisation HV SAOU-WA month ahead | Scheduled Availability + Operational Utilisation | SA OU-WA | STD | S11 Fig. 2: Sub-Market 5. |
| 080 | NPg | 6) Reinforcement optimisation HV Flex Advance winter+1 ahead | (variant of SU with non-standard settlement) | none | NON-STD | S11 PDF p.9: FlexAdvance is "a variant on the standard SU product" that pays 80% of forecast value upfront. S11 PDF p.3 fn 1: "subject to approval of the requested derogation from Flexibility Market Rules on standard products". Sub-Market 6. |
| 081 | NPg | 7) Reinforcement optimisation HV Flex Advance winter ahead | (as 080) | none | NON-STD | S11 Fig. 2: Sub-Market 7. |
| 082 | NPg | 8) Planned outages HV SAOU-15 | Scheduled Availability + Operational Utilisation | SA OU-15 | STD | S11 PDF p.14 Table 7: "variant 15 mins dispatch", "Submarket 8"; S14: "dispatch 15 minutes ahead". |
| 083 | NPg | 9) Planned outages HV SAOU-15 | Scheduled Availability + Operational Utilisation | SA OU-15 | ANOM | NPg defines no Sub-Market 9. See Finding 3. |
| 084 | NPg | 10) Planned outages HV SAOU-15 | Scheduled Availability + Operational Utilisation | SA OU-15 | ANOM | NPg defines no Sub-Market 10. See Finding 3. |
| 085 | NPg | All CMZs - SU Winter Ahead | Scheduled Utilisation | SU | STD | 2025/26: "For the flexibility needs in the Summer tender we will procure the Scheduled Utilisation (SU) product" [S12 PDF p.6]. |
| 086 | NPg | HV - SAOU Month Ahead | Scheduled Availability + Operational Utilisation | SA OU-WA | STD | 2025/26 monthly month-ahead OUSA "dispatch it week ahead" [S12 PDF p.6]; HV SA+OU with week-ahead dispatch in tender NPg25565 [S13 §6.1, Table 1]. This was an NPg variant until CP003 made it standard [S6]. It is the 2025/26 equivalent of 079. |
| 087 | NPg | HV - SU Winter Ahead +1 | Scheduled Utilisation | SU | STD | 2025/26 Summer tender, HV SU for 2026/27 delivery [S12 PDF p.6-7]. NPg no longer uses SU for HV in 2026/27 [S11 PDF p.8 Table 3]. Status doubtful (R-006). |
| 088 | NPg | LV - SU Month Ahead | Scheduled Utilisation | SU | STD | Tender NPg25565 Table 2, LV SU month-ahead [S13]. It is the 2025/26 equivalent of Sub-Market 2. |
| 089 | SPEN | Operational Utilisation - 15 Minutes (Week < x <= Month) | Operational Utilisation | OU-15 | STD | OU is defined in S15 PDF p.8. SPEN's 2026/27 procurement lists only SU and OU+SA ("streamlined our product offering to 2 product types") [S15 PDF p.7-8]. Status doubtful (R-006). |
| 090 | SPEN | Operational Utilisation - 15 Minutes (Day < x <= Week) | Operational Utilisation | OU-15 | STD | As 089. |
| 091 | SPEN | Scheduled Availability + Operational Utilisation - Day Ahead | Scheduled Availability + Operational Utilisation | SA OU-DA | STD | S15 PDF p.7: "Operational Utilisation + Scheduled Availability (Procured day ahead, weekly and month ahead)". |
| 092 | SPEN | Scheduled Utilisation (SU) (Week < x <= Month) | Scheduled Utilisation | SU | STD | S15 PDF p.7: "Scheduled Utilisation (Procured Month Ahead & Day Ahead)"; monthly service windows. |
| 093 | SPEN | Scheduled Utilisation (SU) (Month < x <= Year) | Scheduled Utilisation | SU | STD | Longer windows are "Legacy Contracts (old operating model)" [S15 PDF p.7]. New procurement is month-ahead only, so this is probably legacy contracts (R-006). |
| 094 | SPENW | Operational Utilisation + 15 mins (Week < x <= Month) | Operational Utilisation | OU-15 | STD | Monthly tenders use PR, SU and OU [S16 PDF p.10]; OU response time is 2 or 15 minutes [S16 PDF p.11]. |
| 095 | SPENW | Operational Utilisation + 15 mins (Month < x <= Year) | Operational Utilisation | OU-15 | STD | Long-term (bi-annual) tenders use all four products [S16 PDF p.10]. |
| 096 | SPENW | Operational Utilisation + 2 mins (Week < x <= Month) | Operational Utilisation | OU-2 | STD | S16 PDF p.10-11. |
| 097 | SPENW | Operational Utilisation + 2 mins (Month < x <= Year) | Operational Utilisation | OU-2 | STD | S16 PDF p.10-11. |
| 098 | SPENW | Peak Reduction (Week < x <= Month) | Peak Reduction | PR | STD | S16 PDF p.10-11. PR is under retirement review [S2 p.1-2]. |
| 099 | SPENW | Peak Reduction (PR) (Month < x <= Year) | Peak Reduction | PR | STD | S16 PDF p.10-11. |
| 100 | SPENW | Scheduled Utilisation (Week < x <= Month) | Scheduled Utilisation | SU | STD | S16 PDF p.10-11. |
| 101 | SPENW | Scheduled Utilisation (SU) (Month < x <= Year) | Scheduled Utilisation | SU | STD | S16 PDF p.10-11. |
| 102 | SPENW | Variable Availability Operational Utilisation + 15 mins | Variable Availability + Operational Utilisation | VA OU-15 | STD | S16 PDF p.11: VA+OU response time "either two (2) or fifteen (15) minutes". Long-term tenders only, as VA+OU is not in the monthly list [S16 PDF p.10]. |
| 103 | SPENW | Variable Availability Operational + 2 mins | Variable Availability + Operational Utilisation | VA OU-2 | STD | As 102. The name is missing "Utilisation" (R-011). The 2-minute variant exists [S16 PDF p.11; S4 Table 5 "VA OU-2"; S2 p.2 "ENWL" uses VA+OU 2 minutes]. |
| 104 | SSEN | OU Long-Term | Operational Utilisation | OU-2 | STD | S17 PDF p.6: "Operational Utilisation (OU) - 2 mins ... procured where requirements for post-fault services are identified, throughout the procurement year". The "Long-Term" label is not confirmed. |
| 105 | SSEN | SAOU Long-Term | Scheduled Availability + Operational Utilisation | SA OU-DA | STD | S17 PDF p.4: long-term rounds procure SAOU "to cover within-year and month-ahead requirements"; PDF p.6: "SAOU - day-ahead". |
| 106 | SSEN | SAOU Month-Ahead | Scheduled Availability + Operational Utilisation | SA OU-DA | STD | S17 PDF p.4: "At month-ahead bidding rounds we then tender for a Scheduled Availability and Operational Utilisation product". |
| 107 | SSEN | SU Day-Ahead | Scheduled Utilisation | SU | STD | S17 PDF p.4: "in our day-ahead bidding rounds we procure Scheduled Utilisation". |
| 108 | SSEN | SU Season-Ahead | Scheduled Utilisation | SU | STD | S17 PDF p.4: SU for "HV/LV network requirements a season ahead of need". |
| 109 | SSEN | VAOU Long-Term | Variable Availability + Operational Utilisation | VA OU-WA | STD | S17 PDF p.4, p.6: VAOU for EHV "1-3 years ahead of need"; "VAOU - week-ahead". |
| 110 | UKPN | Scheduled Availability + Operational Utilisation - Day Ahead (Long - Term) | Scheduled Availability + Operational Utilisation | SA OU-DA | STD | S18 PDF p.6: "[SAOU]: Contracts are awarded through long-term tenders ... with utilisation confirmed during day-ahead auctions". |
| 111 | UKPN | Scheduled Utilisation (Day Ahead) | Scheduled Utilisation | SU | STD | S18 PDF p.6: "Scheduled Utilisation (Day-Ahead) [SU]". |
| 112 | UKPN | Scheduled Utilisation (Long-Term) | Scheduled Utilisation | SU | STD | S18 PDF p.6: "(Long-Term) Scheduled Utilisation [LTSU]". |

Counts (46 rows in total):
- Standard variant: 41 rows. Three of these (076, 083, 084) are also flagged ANOM: the product is
  standard but the row itself is questionable.
- LEGACY: 3 (067, 069, 071).
- NON-STD: 2 (080, 081).

By variant:

| Variant | Rows |
|---------|------|
| SU | 15, or 16 if 076 is corrected (Change 3) |
| SA OU-WA | 4, or 5 if 076 stays as labelled |
| SA OU-DA | 5 |
| SA OU-15 | 3 |
| OU-15 | 5 |
| OU-2 | 3 |
| PR | 2 |
| VA OU-15 | 1 |
| VA OU-2 | 1 |
| VA OU-WA | 1 |

Two FMR-PD variants have no row: SA OU-2 and VA OU-DA.

## Finding 3: the NPg numbered tender lines (IDs 075-084) and 085-088

NPg's 2026-27 statement says: "The choice of product and further details such as how far ahead we
are procuring creates what are known as sub-markets within our market for flexibility services. The
sub-markets we intend to operate in 2026-27 are set out in Figure 2" [S11 PDF p.8]. Figure 2 [S11
PDF p.16] lists exactly 8 sub-markets. The CSV line numbers match them as follows:

| CSV ID and line | NPg 2026-27 sub-market (S11 Fig. 2) | Product / variant | Auction contract length (S11 Fig. 2) | Match |
|---|---|---|---|---|
| 075 "1)" LV SU winter ahead | Sub-Market 1: LV SU, procuring winter ahead | SU | Month < x <= Year | exact |
| 076 "2)" HV SAOU-WA winter+1 ahead | Sub-Market 2: **LV SU, procuring month ahead** | SU | Week < x <= Month | **conflict**: the CSV text is a copy of line 3) |
| 077 "3)" HV SAOU-WA winter+1 ahead | Sub-Market 3: HV SAOU+WA, procuring winter+1 ahead | SA OU-WA | Month < x <= Year | exact |
| 078 "4)" HV SAOU-WA winter ahead | Sub-Market 4: HV SAOU+WA, procuring winter ahead | SA OU-WA | Month < x <= Year | exact |
| 079 "5)" HV SAOU-WA month ahead | Sub-Market 5: HV SAOU+WA, procuring month ahead | SA OU-WA | Week < x <= Month | exact |
| 080 "6)" HV Flex Advance winter+1 ahead | Sub-Market 6: HV FlexAdvance, procuring winter+1 ahead | SU with FlexAdvance settlement and verification (non-standard) | Month < x <= Year | exact |
| 081 "7)" HV Flex Advance winter ahead | Sub-Market 7: HV FlexAdvance, procuring winter ahead | as 080 | Month < x <= Year | exact |
| 082 "8)" Planned outages HV SAOU-15 | Sub-Market 8: planned outage HV CMZs, procuring 8 weeks ahead | SA OU-15 | Week < x <= Month | exact (see note) |
| 083 "9)" Planned outages HV SAOU-15 | none | SA OU-15 | - | **no Sub-Market 9** |
| 084 "10)" Planned outages HV SAOU-15 | none | SA OU-15 | - | **no Sub-Market 10** |

Note on Sub-Market 8: the heading of Figure 2 says "HV SAOU+WA", but the figure's variant row says
"15 mins". The statement's Table 7 says "variant 15 mins dispatch ... Submarket 8" [S11 PDF p.14], and
Table 9 says "SAOU_15" [S11 PDF p.21]. The NPg26308 ITT says "dispatch 15 minutes ahead" [S14 p.2].
The CSV value `SAOU-15` is therefore correct, and the "+WA" in NPg's heading is NPg's own slip.

**Conclusion for goal 3.**
- **076 vs 077:** they are not two products. 077 is Sub-Market 3. 076 sits where Sub-Market 2 (LV SU
  month-ahead) should be, but carries line 3's text. It is most likely a copy-and-paste error when
  the rows were made. **Medium confidence:** the original source of the CSV rows is unknown. It may
  be Elexon's Flexibility Market Catalogue [S7], which this run could not read.
- **082-084:** these are one product variant (SA OU-15) for one use case (planned outages). NPg
  tenders it "primarily through the April tender with additional tenders if required" [S11 PDF p.3].
  Table 9 shows delivery in both 2026/27 and 2027/28 [S11 PDF p.21], and a separate June 2026
  mini-competition (NPg26308) was held [S14]. 083 and 084 are therefore procurement windows (tender
  rounds or delivery years) of Sub-Market 8, or plain duplicates. They are not distinct products.
- **085-088:** these are NPg's 2025/26 sub-markets [S12, S13], so the CSV holds two regulatory years
  of NPg procurement side by side. 086 (HV SAOU month-ahead) and 088 (LV SU month-ahead) are the
  2025/26 versions of 2026/27 Sub-Markets 5 and 2.

## Finding 4: evidence bearing on R-001 Question 4 (granularity)

- **Elexon uses a three-level hierarchy.** It defines Product (5) and Variant (12) in FMR-PD [S4].
  FMR-SMD then defines a **Sub-Market** as "a specific segment of the overall Flexibility Market,
  distinguished by a specific System Operator, procuring a specific Product within a specific time
  period", which "may be built of multiple distinct geographic zones, operating in different
  directions" [S5 §1]. The parameters of each sub-market include "Auction contract length",
  procurement platform, operational platform and instruction trigger [S5 Table 2]. The CSV's
  `Contract Length Band` values (`Week < x <= Month` etc.) use the same banding that FMR-SMD and NPg
  use for "Auction contract length" [S11 Fig. 2]. This suggests the DSO rows were taken from the
  Elexon catalogue or from DNO sub-market tables.
- **The 46 DSO rows are sub-markets, not products.** Grouped by DNO and variant, they collapse to
  **25 DNO-product rows**:

  | DNO | Product rows | Variants |
  |-----|--------------|----------|
  | NGED | 6 | Dynamic-legacy, Restore-legacy, Secure-legacy, OU-15, SA OU-DA, SU |
  | NPg | 4 | SU, SA OU-WA, SA OU-15, FlexAdvance |
  | SPEN | 3 | OU-15, SA OU-DA, SU |
  | SPENW | 6 | OU-15, OU-2, PR, SU, VA OU-15, VA OU-2 |
  | SSEN | 4 | OU-2, SA OU-DA, SU, VA OU-WA |
  | UKPN | 2 | SA OU-DA, SU |

  The remaining 21 rows are windows: horizon, contract-length band or regulatory year.
- **Consistency with the recorded answer.** If Question 4 is (or becomes) "one row per product
  family with child windows", this is the same structure Elexon uses. In that case the child table
  could be named `SUB_MARKET` (rather than `PROCUREMENT_WINDOW`) and its columns could mirror FMR-SMD
  Table 2. That would make later reconciliation with Elexon's catalogue straightforward.
- **If the answer is one row per tender line,** the variant column proposed below (Change 1) is still
  needed to make the rows comparable.
- **Wording to correct in R-001 Change 12:**
  - "Sustain / Secure / Dynamic / Restore families and their SU / SAOU / VAOU / OU payment
    structures" should read "the five FMR-PD standard products (SU, PR, OU, SA+OU, VA+OU) and their
    12 variants; Sustain/Secure/Dynamic/Restore are superseded legacy products".
  - The proposed column `ena_standard_product` should reference Elexon FMR-PD rather than ENA.

## Changes

### Change 1 (structural, needs approval): add standard-product classification to KEY_DATA

Add three columns to `KEY_DATA.csv` after `Contract Length Band`. They would be blank for non-DSO rows.

| Column (current header style) | snake_case name (per R-001 Q3) | Allowed values | Source |
|---|---|---|---|
| `Standard Product` | `standard_product_code` | `SU`, `PR`, `OU`, `SAOU`, `VAOU` (blank if none) | S4 §2.2 |
| `Standard Variant` | `standard_variant_code` | the 12 FMR-PD codes in Finding 1b, plus `LEGACY-SUSTAIN`, `LEGACY-SECURE`, `LEGACY-DYNAMIC`, `LEGACY-RESTORE`, `NPG-FLEXADVANCE` | S4 Table 5; S3; S11 |
| `Product Fit` | `product_fit` | `standard`, `legacy`, `non_standard` | this proposal |

Alternatively, defer the columns to Phase 2. In that case the contents of Finding 1b and 1c become the
seed rows of two lookups, `LK_DSO_STANDARD_PRODUCT` (5 rows) and `LK_DSO_PRODUCT_VARIANT` (17 rows).
They are input for R-009.

### Change 2: values for the new columns (applies only if Change 1 is approved)

| File | Key (ID) | Column | Current | Proposed | Source |
|------|----------|--------|---------|----------|--------|
| KEY_DATA.csv | 067 | Standard Product / Standard Variant / Product Fit | (new) | (blank) / LEGACY-DYNAMIC / legacy | S9 PDF p.5-6; S3 p.9 |
| KEY_DATA.csv | 068 | as above | (new) | OU / OU-15 / standard | S8 PDF p.6; S10 PDF p.20 |
| KEY_DATA.csv | 069 | as above | (new) | (blank) / LEGACY-RESTORE / legacy | S9 PDF p.5-6; S3 p.9 |
| KEY_DATA.csv | 070 | as above | (new) | SAOU / SA OU-DA / standard | S8 PDF p.6; S10 PDF p.20 |
| KEY_DATA.csv | 071 | as above | (new) | (blank) / LEGACY-SECURE / legacy | S9 PDF p.5-6; S3 p.9 |
| KEY_DATA.csv | 072 | as above | (new) | SU / SU / standard | S8 PDF p.15; S10 PDF p.20 |
| KEY_DATA.csv | 073 | as above | (new) | SU / SU / standard | S8 PDF p.15 |
| KEY_DATA.csv | 074 | as above | (new) | SU / SU / standard | S8 PDF p.6; S9 PDF p.6 |
| KEY_DATA.csv | 075 | as above | (new) | SU / SU / standard | S11 PDF p.16 |
| KEY_DATA.csv | 076 | as above | (new) | **hold until Change 3 is decided** (SU if renamed, SAOU / SA OU-WA if kept) | S11 PDF p.16 |
| KEY_DATA.csv | 077, 078, 079 | as above | (new) | SAOU / SA OU-WA / standard | S11 PDF p.11, p.16; S6 |
| KEY_DATA.csv | 080, 081 | as above | (new) | (blank) / NPG-FLEXADVANCE / non_standard | S11 PDF p.3, p.9, p.16 |
| KEY_DATA.csv | 082, 083, 084 | as above | (new) | SAOU / SA OU-15 / standard | S11 PDF p.14, p.21; S14 |
| KEY_DATA.csv | 085, 087, 088 | as above | (new) | SU / SU / standard | S12 PDF p.6-7; S13 |
| KEY_DATA.csv | 086 | as above | (new) | SAOU / SA OU-WA / standard | S12 PDF p.6; S13 §6.1; S6 |
| KEY_DATA.csv | 089, 090 | as above | (new) | OU / OU-15 / standard | S15 PDF p.8 |
| KEY_DATA.csv | 091 | as above | (new) | SAOU / SA OU-DA / standard | S15 PDF p.7 |
| KEY_DATA.csv | 092, 093 | as above | (new) | SU / SU / standard | S15 PDF p.7 |
| KEY_DATA.csv | 094, 095 | as above | (new) | OU / OU-15 / standard | S16 PDF p.10-11 |
| KEY_DATA.csv | 096, 097 | as above | (new) | OU / OU-2 / standard | S16 PDF p.10-11 |
| KEY_DATA.csv | 098, 099 | as above | (new) | PR / PR / standard | S16 PDF p.10-11 |
| KEY_DATA.csv | 100, 101 | as above | (new) | SU / SU / standard | S16 PDF p.10-11 |
| KEY_DATA.csv | 102 | as above | (new) | VAOU / VA OU-15 / standard | S16 PDF p.11 |
| KEY_DATA.csv | 103 | as above | (new) | VAOU / VA OU-2 / standard | S16 PDF p.11; S4 Table 5 |
| KEY_DATA.csv | 104 | as above | (new) | OU / OU-2 / standard | S17 PDF p.6 |
| KEY_DATA.csv | 105, 106 | as above | (new) | SAOU / SA OU-DA / standard | S17 PDF p.4, p.6 |
| KEY_DATA.csv | 107, 108 | as above | (new) | SU / SU / standard | S17 PDF p.4 |
| KEY_DATA.csv | 109 | as above | (new) | VAOU / VA OU-WA / standard | S17 PDF p.4, p.6 |
| KEY_DATA.csv | 110 | as above | (new) | SAOU / SA OU-DA / standard | S18 PDF p.6 |
| KEY_DATA.csv | 111, 112 | as above | (new) | SU / SU / standard | S18 PDF p.6 |

The rows marked LEGACY leave `Standard Product` blank on purpose, because they are not FMR-PD
products. The nearest current product is recorded in Finding 1c and should go in the lookup's
definition text, not in the row.

### Change 3 (data correction, needs human confirmation): NPg ID 076

| File | Key | Column | Current | Proposed | Source |
|------|-----|--------|---------|----------|--------|
| all six CSVs | 076 | Market Name | `2) Reinforcement optimisation HV SAOU-WA winter+1 ahead` | `2) Reinforcement optimisation LV SU month ahead` | S11 PDF p.16 (Figure 2, Sub-Market 2) |

Confidence is medium. If the human knows the original source of the row (for example a catalogue
export), check it first. If the row really was meant as a second SA OU-WA line, it is a duplicate of
077 and should be removed or turned into a window, not renamed.

_Main-session note (2026-11-23): the human confirmed that the rows came from the Elexon catalogue.
So the 076 name probably matches what the catalogue said when the rows were copied, and is not a
typing error in this database. Hold Change 3 until someone has checked the catalogue entry by eye.
Do not rename 076 on the strength of the NPg statement alone._

### Change 4 (flag only, no value change yet): NPg IDs 083 and 084

Put this text in KEY_DATA `Notes` for 083 and 084: `Not a distinct product: NPg defines no
Sub-Market 9/10 (2026-27 statement Fig. 2); same variant (SA OU-15) and use case as 082 - procurement
window or duplicate. See R-008.` Source: S11 PDF p.14, p.16, p.21.

When Question 4 is applied, merge 082-084 into one NPg/SA OU-15 product row and record the windows
(the April 2026 tender, NPg26308 in June 2026, and the 2027/28 delivery) in the child table. Until
then, the human may prefer to delete 083 and 084 instead. That decision is left open.

### Change 5 (sourced fill of blank values): NPg `Contract Length Band`

| File | Key | Column | Current | Proposed | Source |
|------|-----|--------|---------|----------|--------|
| KEY_DATA.csv | 075 | Contract Length Band | (blank) | Month < x <= Year | S11 PDF p.16 |
| KEY_DATA.csv | 076 | Contract Length Band | (blank) | Week < x <= Month (only if Change 3 is accepted) | S11 PDF p.16 |
| KEY_DATA.csv | 077 | Contract Length Band | (blank) | Month < x <= Year | S11 PDF p.16 |
| KEY_DATA.csv | 078 | Contract Length Band | (blank) | Month < x <= Year | S11 PDF p.16 |
| KEY_DATA.csv | 079 | Contract Length Band | (blank) | Week < x <= Month | S11 PDF p.16 |
| KEY_DATA.csv | 080 | Contract Length Band | (blank) | Month < x <= Year | S11 PDF p.16 |
| KEY_DATA.csv | 081 | Contract Length Band | (blank) | Month < x <= Year | S11 PDF p.16 |
| KEY_DATA.csv | 082 | Contract Length Band | (blank) | Week < x <= Month | S11 PDF p.16 |

### Change 6 (flag for R-006, no change here): rows whose `Status = Live` is doubtful

| ID | Why | Source |
|----|-----|--------|
| 067, 069, 071 | NGED legacy ENA products. Restore and Secure have no contracted volume; Dynamic has only prior-year contracts. Not in NGED's 2026-27 product list. | S9 PDF p.5-6; S8 PDF p.6 |
| 073 | NGED's short-term market moved from week-ahead to day-ahead. | S8 PDF p.15; S9 PDF p.3 |
| 087 | NPg no longer procures SU for HV in 2026/27 (it uses SAOU_WA and FlexAdvance). | S11 PDF p.8 |
| 085-088 | 2025/26 sub-markets. They may be closed, or superseded by 075-084. | S12; S11 |
| 089, 090 | OU-15 is not in SPEN's 2026/27 product list. | S15 PDF p.7-8 |
| 093 | SPEN's long-term SU is "legacy contracts (old operating model)". | S15 PDF p.7 |

### Change 7 (wording fix in another proposal, needs approval)

In `research/proposals/2026-11-23-R-001-database-structure-review.md`, Change 12:
- Replace the product-family sentence and the 403 caveat with a reference to Elexon FMR-PD v4.2 [S4]
  and to this proposal.
- Rename `ena_standard_product` to `standard_variant_code`, referencing `LK_DSO_PRODUCT_VARIANT`.

## Confidence and caveats

- **High confidence:** the product set and variant parameters. They are taken verbatim from the
  current Elexon rule (S4), cross-checked against ENA 2024 (S1) and ENA Dec 2024 (S2), and every DNO
  statement (S8, S11, S15-S18) names the same five products.
- **High confidence:** the mappings for NGED 068/070/072, NPg 075 and 077-082, SPENW, SSEN 105-109
  and UKPN. The DNO's own statement names the product.
- **Medium confidence:**
  - 074 (the code `SU_LV` was not found);
  - 104 (SSEN "OU Long-Term": SSEN describes OU 2 mins as procured "throughout the procurement year");
  - 089/090 (SPEN OU-15 not in its 2026/27 list);
  - 085-088 (attributed to 2025/26 by matching descriptions, not by a numbered list).
- **Medium confidence:** the 076 correction and the 083/084 interpretation. The original source of
  the CSV rows is unknown. Elexon's Flexibility Market Catalogue (S7) is the most likely source and
  would settle all three, but it is a Power BI embed that this run could not read.
- **Inferred, not sourced as a mapping:** the "nearest current product" for the legacy Secure,
  Dynamic, Restore and Sustain products (Finding 1c). It rests on matching definitions and payment
  structures. Secure in particular varies by DNO.
- **Internal inconsistencies in sources:**
  - FMR-PD v4.2's summary says "comes into force in May 2026" and "February 2026", while Table 1 gives
    an Implementation Date of 31/03/2027 (that date applies to CP005's monitoring changes).
  - NPg's Figure 2 heading "SAOU+WA" for Sub-Market 8 conflicts with its own "15 mins" variant.
- **Access notes:**
  - energynetworks.org (S1 direct URL) and spenergynetworks.co.uk (S15) return 403 to automated
    clients; Wayback (S1) and the Ofgem ZIP (S15, S18) were used instead.
  - The PDF download of FMR-PD returned HTTP 500; the HTML text was used.
  - A human can open the direct links in a browser to verify.
- **Out of scope but noticed:**
  - Every DSO row has `Direction = Up/Down`. Most DSO sub-markets are demand turn-down / generation
    turn-up only, and FMR-SMD and NGED split DTD/GTU from DTU/GTD. NGED has separate codes such as
    `SU_HV_DTUGTD` [S10 PDF p.20].
  - Some DSO products are missing from the CSV:
    - SSEN "Legacy-Secure" [S17 PDF p.12];
    - NGED `SU_SPP` and `SU_SEP` [S9 PDF p.6];
    - SSEN's non-standard "LMA Interim Payment" service [S4 derogation table];
    - SPEN's day-ahead DTU at the B6 boundary [S15].
  - These have been logged as new backlog items.
