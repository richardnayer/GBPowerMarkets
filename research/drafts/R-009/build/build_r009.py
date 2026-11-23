"""Build the R-009 draft tables in research/drafts/R-009/ (UTF-8 with BOM, CRLF, csv module).

Sources and organisations are listed in a fixed order and numbered here, so cross-references in
notes use placeholders like {S:cfd} and {O:nged} that are resolved after numbering.
Run: python -I build_r009.py <repo_root>
"""
import csv, io, os, re, sys

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'research', 'drafts', 'R-009')
ACC = '2026-11-23'
OGL_GOV = 'Reuse: GOV.UK footer says all content is available under the Open Government Licence v3.0 except where otherwise stated (Crown copyright).'
OGL_OFGEM = ('Reuse: Ofgem says its material is Crown copyright and may be reused free of charge (Open Government '
             'Licence), except logos and third-party material (https://www.ofgem.gov.uk/copyright).')
NESO_WEB = ('Reuse: NESO website terms (https://www.neso.energy/terms-and-conditions) reserve the intellectual '
            'property in site content; copies for own use only. Facts and links only; definitions are paraphrased.')
NOT_CHECKED = 'Reuse: terms not checked in this run (R-019).'
R008 = 'Read in R-008 (see research/proposals/2026-11-23-R-008-dso-product-taxonomy.md, source {}).'

# ---------------------------------------------------------------- SOURCES (R-001 Change 5 columns)
# key, title, publisher(org key or text), url, source_type, doc_type, version_or_date, archive_url, notes
SOURCES = [
    ('neso_designation', 'Designation of the National Energy System Operator (NESO)', 'desnz',
     'https://www.gov.uk/government/publications/designation-of-the-national-energy-system-operator-neso',
     'primary', 'decision', '2024-09-13', '',
     'DESNZ and Ofgem decisions, all effective 1 October 2024 00:00; converts the NGESO transmission licence into '
     'the NESO Electricity System Operator Licence. ' + OGL_GOV),
    ('companies_house', 'Companies House register: company overview pages', 'Companies House',
     'https://find-and-update.company-information.service.gov.uk/', 'primary', 'dataset', '', '',
     'Company page = https://find-and-update.company-information.service.gov.uk/company/<number>. Gives registered '
     'name, number, status and previous names with dates. Pages read 2026-11-23 for 11014226, 03600574, 02366949, '
     '03782949, 08818711, 08961281, 08924703, 01528617 and the search results for 04832301. ' + NOT_CHECKED),
    ('ofgem_licensees', 'All Electricity Licensees 14/4/26', 'ofgem',
     'https://www.ofgem.gov.uk/sites/default/files/2026-03/all-electricity-licensees.pdf', 'primary', 'dataset',
     '2026-04-14', '',
     'Lists licence type, company name and company number. Electricity Distribution section: the 14 DNO licensees. '
     'Ofgem note: the lists are not formal Public Register documents and should not be relied upon. '
     'sha256 99be15c17faa2884. Landing page: https://www.ofgem.gov.uk/data/list-all-electricity-licensees-including-suppliers '
     '(not opened). ' + OGL_OFGEM),
    ('ofgem_nemo_2015', 'Final decisions on applications made by APX Commodities Limited and Nord Pool Spot AS to be designated NEMOs in GB',
     'ofgem', 'https://www.ofgem.gov.uk/sites/default/files/docs/final_decisions_on_applications_to_be_designated_a_nemo_in_gb_10122015_2.pdf',
     'primary', 'decision', '2015-12-10', '',
     'Appendix 2: Notice of Designation of Nord Pool Spot AS (Norwegian company number 984 058 098, Lysaker). '
     'Historical; the GB NEMO regime predates EU exit. sha256 1506b941dcc02722. ' + OGL_OFGEM),
    ('ofgem_nemo_2016', 'Final decision on the application made by EPEX SPOT SE to be designated a NEMO in GB', 'ofgem',
     'https://www.ofgem.gov.uk/sites/default/files/docs/2016/11/final_decisions_on_epex_spot_nemo_designation_and_revocation_of_apx_nemo_designation_in_gb.pdf',
     'primary', 'decision', '2016-11-30', '',
     'Appendix 1: EPEX SPOT SE, registered in Paris under company number 508 010 501. Historical. '
     'sha256 f6b5db083e9633ee. ' + OGL_OFGEM),
    ('nordpool_about', 'About us', 'nordpool', 'https://www.nordpoolgroup.com/en/about-us/', 'primary', 'webpage', '', '',
     'Ownership (Euronext 66%, TSO Holding 34%); footer gives Nord Pool AS, Lysaker, Norway. '
     'Reuse: the site terms page (https://www.nordpoolgroup.com/en/About-us/terms-and-conditions-for-use/) was read '
     'but no reuse statement was found.'),
    ('nordpool_da', 'Day-ahead trading', 'nordpool', 'https://www.nordpoolgroup.com/en/trading/Day-ahead-trading/',
     'primary', 'webpage', '', '',
     'Describes auction-based day-ahead trading, including day-ahead trading and a half-hour auction in the UK. '
     'Reuse: no statement found (see the About us source).'),
    ('nordpool_id', 'Intraday trading', 'nordpool', 'https://www.nordpoolgroup.com/en/trading/Intraday-trading/',
     'primary', 'webpage', '', '', 'Describes continuous intraday trading. Reuse: no statement found.'),
    ('eex_futures', 'Power futures', 'eex', 'https://www.eex.com/en/markets/power/power-futures', 'primary',
     'contract_spec', '', '',
     'Contract overview including EEX GB Power Future (1 MW, GBP 0.01/MWh tick, fulfilment listed as "Cash '
     'settlement/ Physical fulfilment"). Footer: European Energy Exchange AG, Augustusplatz 9, Leipzig. ' + NOT_CHECKED),
    ('ice_ubl', 'UK Base Electricity Future (Gregorian), product 20788778', 'ice',
     'https://www.ice.com/products/20788778/UK-Base-Electricity-Future-Gregorian', 'primary', 'contract_spec', '', '',
     'ICE Futures Europe contract UBL: physical delivery via Energy Contract Volume Notifications; clearing members '
     'as defined in the ICE Clear Europe Clearing Rules. ' + NOT_CHECKED),
    ('nged_stmt', 'Distribution Flexibility Services Procurement Statement 2026-27', 'nged',
     'https://dso.nationalgrid.co.uk/downloads/15141/nged-dso-distribution-flexibility-services-procurement-statement-2026-27.pdf',
     'primary', 'other', '2026-04', '', R008.format('S8') + ' Mentions its four licence areas. ' + NOT_CHECKED),
    ('npg_stmt', 'Distribution Flexibility Services Procurement Statement 2026-27', 'npg',
     'https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202026-27.pdf',
     'primary', 'other', '2026-04', '',
     R008.format('S11') + ' Names the Northeast and Yorkshire licence areas; FlexAdvance described on PDF p.9. ' + NOT_CHECKED),
    ('spen_stmt', 'Distribution Flexibility Service Procurement Statement for SP Distribution PLC and SP Manweb PLC', 'spen',
     'https://www.spenergynetworks.co.uk/userfiles/file/SP5175_SPEN_DSO_C31E_Procurement_Statement_2026_v8_003.pdf',
     'primary', 'other', '2026-04', '',
     R008.format('S15') + ' The SPEN URL returns 403 to automated clients; read from the Ofgem ZIP '
     '(https://www.ofgem.gov.uk/sites/default/files/2026-06/Procurement-statements-2026-2027.zip). ' + NOT_CHECKED),
    ('spenw_stmt', 'Distribution Flexibility Services Procurement Statement, April 2026', 'spenw',
     'https://www.enwl.co.uk/globalassets/future-energy/flexibility-hub/document-library/ofgem-dfp-reporting/sp-enw-distribution-flexibility-services-procurement-statement-2026..pdf',
     'primary', 'other', '2026-04', '',
     R008.format('S16') + ' Section 2.1 (PDF p.4): Iberdrola acquired 88% of Electricity North West through Scottish '
     'Power; the network has rebranded as SP Electricity North West. ' + NOT_CHECKED),
    ('ssen_stmt', '2026/27 Flexibility Services Procurement Statement', 'ssen',
     'https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/slc31e-reports--statements/slc31e--ssen-2026-27-flexibility-services-procurement-statement.pdf',
     'primary', 'other', '2026-03', '',
     R008.format('S17') + ' Back page: Scottish and Southern Electricity Networks is a trading name of SSE network '
     'companies including Scottish Hydro Electric Power Distribution plc (SC213460) and Southern Electric Power '
     'Distribution plc (04094290). ' + NOT_CHECKED),
    ('ukpn_stmt', 'Flexibility Services Procurement Statement, April 2026 - March 2027', 'ukpn',
     'https://www.ofgem.gov.uk/sites/default/files/2026-06/Procurement-statements-2026-2027.zip', 'primary', 'other',
     '2026-03', '',
     R008.format('S18') + ' No direct UKPN URL found; ZIP member "Flexibility Services Procurement Statement 2026 '
     'v1.0.pdf". Refers to "all three of our licence areas" and uses EPN, LPN and SPN. ' + NOT_CHECKED),
    ('ofgem_31e', 'Electricity Distribution Standard Licence Condition 31E: flexibility procurement statements 2026 to 2027',
     'ofgem', 'https://www.ofgem.gov.uk/transparency-document/electricity-distribution-standard-licence-condition-31e-flexibility-procurement-statements-2026-2027',
     'primary', 'webpage', '2026-06-22', '', R008.format('S19') + ' ' + OGL_OFGEM),
    ('elexon_role', "Elexon's role in facilitating flexibility markets", 'elexon',
     'https://www.elexon.co.uk/flexibility-markets/about/elexons-role/', 'primary', 'webpage', '', '',
     'States that Elexon acts as the flexibility market facilitator, appointed by Ofgem. Reuse: Elexon terms page '
     'did not load in this run; not checked (R-019).'),
    ('elexon_whatwedo', 'What we do', 'elexon', 'https://www.elexon.co.uk/what-we-do/', 'primary', 'webpage', '', '',
     'Elexon role in the wholesale, capacity and flexibility markets; the BSC was introduced under NETA (March 2001); '
     'Ofgem appointed Elexon as market facilitator in July 2024. Reuse: not checked (R-019).'),
    ('emrs_home', 'EMR Settlement Limited home page', 'emrs', 'https://www.emrsettlement.co.uk/', 'primary', 'webpage',
     '', '',
     'Who we are: EMRS is a wholly owned subsidiary of Elexon Limited and the EMR Settlement Services Provider for '
     'LCCC (CfD and Nuclear RAB counterparty) and for the Electricity Settlements Company (CM Settlement Body). ' + NOT_CHECKED),
    ('gov_cfd', 'Contracts for Difference (collection)', 'desnz',
     'https://www.gov.uk/government/collections/contracts-for-difference', 'primary', 'webpage', '2025-12-16', '',
     'Last updated 16 December 2025. LCCC (owned by DESNZ) is counterparty; the page still names National Grid ESO '
     'as CfD delivery body; Ofgem hears certain appeals; allocation rounds AR1-AR7. ' + OGL_GOV),
    ('gov_cm', 'Capacity Market (collection)', 'desnz',
     'https://www.gov.uk/government/collections/electricity-market-reform-capacity-market', 'primary', 'webpage',
     '2023-01-23', '', 'Last updated 23 January 2023. ' + OGL_GOV),
    ('ofgem_ldes_role', 'LDES Cap and Floor Regime: our role, plan, and response to the DESNZ publication', 'ofgem',
     'https://www.ofgem.gov.uk/call-for-input/ldes-cap-and-floor-regime-our-role-plan-and-response-desnz-publication',
     'primary', 'consultation', '2024-12-18', '',
     'States that DESNZ has tasked Ofgem with implementing a cap and floor regime for long duration electricity '
     'storage. ' + OGL_OFGEM),
    ('gov_desnz', 'Department for Energy Security and Net Zero (organisation page)', 'desnz',
     'https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero', 'primary', 'webpage',
     '', '', 'DESNZ is a ministerial department responsible for UK energy security, protecting billpayers and reaching net zero. ' + OGL_GOV),
    ('ofgem_about', 'About us', 'ofgem', 'https://www.ofgem.gov.uk/about-us', 'primary', 'webpage', '', '',
     'Ofgem stands for the Office of Gas and Electricity Markets; energy regulator for Great Britain; a non-ministerial '
     'government department. ' + OGL_OFGEM),
    ('fmr_pd', 'FMR-PD Product definitions, v4.2', 'elexon',
     'https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-pd-product-definitions', 'primary',
     'rulebook', '2026-08-25 (v4.2)', '',
     R008.format('S4') + ' Table 3 (parameters of the 12 variants) and Table 5 (variant codes). Text read from the HTML; '
     'the PDF download returned HTTP 500. Reuse: not checked (R-019).'),
    ('fmr_smd', 'FMR-SMD Sub-Market definitions, v2.1', 'elexon',
     'https://bscdocs.elexon.co.uk/flex-market/flexibility-market-rules/fmr-smd-sub-market-definitions', 'primary',
     'rulebook', '2026-02-04 (v2.1)', '',
     R008.format('S5') + ' Defines a Sub-Market and the parameter "Auction contract length". Reuse: not checked (R-019).'),
    ('ena_2024', 'Flexibility Products Review and Alignment, v1.0', 'ena',
     'https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf', 'primary',
     'other', '2024-02', 'https://web.archive.org/web/20240503005600/https://www.energynetworks.org/assets/images/2023/Aug/on-flexibility-products-alignment-(feb-2024).pdf',
     R008.format('S1') + ' The direct URL returns 403 to automated clients. Reuse: not checked (R-019).'),
    ('ena_2022', 'ON22-WS1A-P6 Active Power Products Review', 'ena',
     'https://www.energynetworks.org/assets/images/Resource%20library/ON22-WS1A-P6%20Active%20Power%20Products%20Review%20(01%20Aug%202022).pdf',
     'primary', 'other', '2022-08-01', '',
     R008.format('S3') + ' Defines the legacy Sustain, Secure, Dynamic and Restore products (p.9) and their payment '
     'structures (p.10-12). Reuse: not checked (R-019).'),
    ('flx_cp003', 'FLX CP003: Revision of standard product variants for Scheduled Availability + Operational Utilisation',
     'elexon', 'https://www.elexon.co.uk/flexibility-markets/change-proposals/flx-cp003/', 'primary', 'decision',
     '2026-06-11 (implemented)', '', R008.format('S6') + ' Proposed by Northern Powergrid; added SA OU-2, SA OU-15 and SA OU-WA. Reuse: not checked (R-019).'),
    ('neso_bal', 'Balancing services', 'neso', 'https://www.neso.energy/industry-information/balancing-services',
     'primary', 'webpage', '', '',
     'Index of NESO balancing services: response and reserve, constraint markets, system security, reactive power, '
     'trading, restoration, stability. ' + NESO_WEB),
    ('neso_rr', 'Response and Reserve', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/response-and-reserve', 'primary', 'webpage', '', '',
     'Frequency response controls system frequency by balancing generation and demand; reserve gives access to '
     'extra power over a range of timescales. ' + NESO_WEB),
    ('neso_stability', 'Stability market', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/stability-market', 'primary', 'webpage', '', '',
     'Stability requirements are inertia and short-circuit level; long-term (Y-4), mid-term (Y-1) and short-term (D-1) '
     'timescales; first long-term tender launched in 2025. ' + NESO_WEB),
    ('neso_esr', 'Electricity System Restoration Standard', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/electricity-system-restoration-standard',
     'primary', 'webpage', '', '',
     'Standard: restore 100% of GB demand within five days and 60% of regional demand within 24 hours after a total '
     'or partial shutdown; compliance by 31 December 2026. ' + NESO_WEB),
    ('neso_reactive', 'Reactive power services', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/reactive-power-services', 'primary', 'webpage',
     '', '', 'Keeps voltage within range by instructing units to absorb or generate reactive power. ' + NESO_WEB),
    ('neso_lcm', 'Local Constraint Market', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/local-constraint-market', 'primary', 'webpage',
     '', '',
     'LCM manages transmission constraints, including at the B6 boundary; the page says the Demand Flexibility Service '
     'replaces LCM from 7 October 2026. ' + NESO_WEB),
    ('neso_bm', 'What is the Balancing Mechanism?', 'neso',
     'https://www.neso.energy/what-we-do/systems-operations/what-balancing-mechanism', 'primary', 'webpage', '', '',
     'Defines the BM as NESO\'s primary balancing tool; an offer is to consume less or generate more, a bid to consume '
     'more or generate less. ' + NESO_WEB),
    ('grid_code_gd', 'The Grid Code: Glossary & Definitions, Issue 6 Revision 40', 'neso',
     'https://www.neso.energy/document/382376/download', 'primary', 'rulebook', '2026-05-29 (Issue 6 Rev 40)', '',
     'Definitions of Active Power, Reactive Power, Ancillary Service and Operating Reserve. Latest revision found in '
     'this run; a later one may exist. sha256 672e44b92ef9dc3a. Reuse: "(c) 2026 Copyright owned by National Energy '
     'System Operator, all rights reserved"; reproduction only as the notice allows. Definitions are paraphrased.'),
    ('neso_eac', 'Enduring Auction Capability (EAC)', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/enduring-auction-capability-eac', 'primary',
     'webpage', '', '', 'EAC delivers co-optimised day-ahead procurement of frequency response and reserve products. ' + NESO_WEB),
    ('neso_smp', 'Single Markets Platform', 'neso',
     'https://www.neso.energy/industry-information/balancing-services/single-markets-platform', 'primary', 'webpage',
     '', '', 'SMP supports onboarding to NESO markets; first release 10 February 2022. NESO\'s name is "Single Markets Platform". ' + NESO_WEB),
    ('ofgem_liquidity', 'Call for Input: Power Market Liquidity', 'ofgem',
     'https://www.ofgem.gov.uk/sites/default/files/2023-12/Call%20for%20Input%20-%20Power%20Market%20Liquidity.pdf',
     'primary', 'consultation', '2023-12-08', '',
     'Para 2.13 (PDF p.11) distinguishes OTC Physical (physical delivery) from OTC Financial (no physical delivery; a '
     'hedge against spot prices); liquidity measured over OTC and power exchanges. sha256 e44051a16d7d7965. ' + OGL_OFGEM),
    ('r001', 'R-001 Database structure review (internal design decision)', 'This project',
     'research/proposals/2026-11-23-R-001-database-structure-review.md', 'internal', 'other', '2026-11-23', '',
     'Internal vocabulary decisions: Change 6 (lookups) and Change 7 (missing values). Path is relative to the repository root.'),
    ('nged_report', 'Distribution Flexibility Services Procurement Report 2025-26', 'nged',
     'https://dso.nationalgrid.co.uk/downloads/15152/nged-distribution-flexibility-services-procurement-report-2025-26.pdf',
     'primary', 'other', '2026-05', '',
     R008.format('S9') + ' PDF p.5-6 report Dynamic, Restore and Secure as legacy ENA products, separate from the standardised Market Facilitator products. ' + NOT_CHECKED),
    ('npg_stmt_2526', 'Distribution Flexibility Services Procurement Statement 2025-26 v2', 'npg',
     'https://www.northernpowergrid.com/sites/default/files/assets/Distribution%20Flexibility%20Services%20Procurement%20Statement%202025-26%20v2.pdf',
     'primary', 'other', '2025-04', '', R008.format('S12') + ' ' + NOT_CHECKED),
    ('npg_itt_25565', 'ITT NPg25565, Document 2: Scope and Specification', 'npg',
     'https://piclo-so-docs.s3.eu-west-2.amazonaws.com/Northern+Powergrid+/2025.12/Document+2+-+Scope+and+Specification.pdf',
     'primary', 'other', '2025-12', '', R008.format('S13') + ' Month-ahead tender (HV SA+OU with week-ahead dispatch; LV SU). Hosted on Piclo. ' + NOT_CHECKED),
]

# ---------------------------------------------------------------- ORGANISATIONS
# key, name, short_name, org_type, parent, licence_id, url, valid_from, valid_to, predecessor, registry_id, source, notes
ORGS = [
    ('neso', 'National Energy System Operator Limited', 'NESO', 'system_operator', '', '', 'https://www.neso.energy/',
     '2024-10-01', '', 'ngeso', 'GB-COH-11014226', 'neso_designation',
     'GB electricity system operator; designation effective 1 October 2024 ({S:neso_designation}). Same company as '
     '{O:ngeso}, renamed (Companies House, {S:companies_house}). Runs the EAC auctions ({S:neso_eac}) and the Single '
     'Markets Platform ({S:neso_smp}). Named as CfD delivery body under its former name ({S:gov_cfd}).'),
    ('ngeso', 'National Grid Electricity System Operator Limited', 'National Grid ESO', 'system_operator', '', '', '',
     '', '2024-09-30', '', 'GB-COH-11014226', 'companies_house',
     'Registered name from 16 October 2017 until it was renamed on 1 October 2024 (Companies House 11014226). Kept '
     'so that older sources naming National Grid ESO resolve. Same registry_id as {O:neso} because it is the same company.'),
    ('elexon', 'Elexon Limited', 'Elexon', 'code_administrator', '', '', 'https://www.elexon.co.uk/', '', '', '',
     'GB-COH-03782949', 'elexon_whatwedo',
     'Administers the Balancing and Settlement Code ({S:elexon_whatwedo}); appointed by Ofgem as flexibility market '
     'facilitator ({S:elexon_role}). Registered as BSCC Limited from 13 July 1999 to 31 May 2000 (Companies House).'),
    ('emrs', 'EMR Settlement Limited', 'EMRS', 'settlement_agent', 'elexon', '', 'https://www.emrsettlement.co.uk/',
     '', '', '', 'GB-COH-08924703', 'emrs_home',
     'Wholly owned subsidiary of Elexon; EMR settlement services provider for LCCC (CfD) and for ESC (Capacity Market) ({S:emrs_home}).'),
    ('lccc', 'Low Carbon Contracts Company Ltd', 'LCCC', 'counterparty', 'desnz', '', 'https://www.lowcarboncontracts.uk/',
     '', '', '', 'GB-COH-08818711', 'gov_cfd',
     'Counterparty to CfD contracts; a private company owned by DESNZ ({S:gov_cfd}). Registered as CfD Counterparty '
     'Company Limited until 29 April 2014 (Companies House). Website not opened in this run (403).'),
    ('esc', 'Electricity Settlements Company Ltd', 'ESC', 'counterparty', '', '', '', '', '', '', 'GB-COH-08961281',
     'emrs_home',
     'Capacity Market Settlement Body ({S:emrs_home}). Parent and website not recorded: not confirmed from a primary source in this run.'),
    ('desnz', 'Department for Energy Security and Net Zero', 'DESNZ', 'government_department', '', '',
     'https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero', '', '', '', '',
     'gov_desnz',
     'UK ministerial department ({S:gov_desnz}). Publishes the CfD and Capacity Market policy pages ({S:gov_cfd}, '
     '{S:gov_cm}) and tasked Ofgem with the LDES cap and floor regime ({S:ofgem_ldes_role}). Creation date not '
     'recorded: not checked in this run.'),
    ('ofgem', 'Office of Gas and Electricity Markets', 'Ofgem', 'regulator', '', '', 'https://www.ofgem.gov.uk/', '',
     '', '', '', 'ofgem_about',
     'Energy regulator for Great Britain; a non-ministerial government department ({S:ofgem_about}). Implements the '
     'LDES cap and floor regime ({S:ofgem_ldes_role}).'),
    ('ena', 'Energy Networks Association Limited', 'ENA', 'industry_body', '', '', 'https://www.energynetworks.org/',
     '', '', '', 'GB-COH-04832301', 'ena_2024',
     'Publisher of the Open Networks flexibility product reports ({S:ena_2024}, {S:ena_2022}). Company number from a '
     'Companies House search result. Website returns 403 to automated clients.'),
    ('epex', 'EPEX SPOT SE', 'EPEX SPOT', 'exchange', '', '', 'https://www.epexspot.com/', '', '', '',
     'FR-RCS-508010501', 'ofgem_nemo_2016',
     'Power exchange registered in Paris under number 508 010 501 ({S:ofgem_nemo_2016}). KEY_DATA spells it "EPEX Spot". '
     'Website not readable by automated clients in this run.'),
    ('nordpool', 'Nord Pool AS', 'Nord Pool', 'exchange', '', '', 'https://www.nordpoolgroup.com/', '', '', '', '',
     'nordpool_about',
     'Owned by Euronext (66%) and TSO Holding (34%) ({S:nordpool_about}). Ofgem designated it as a GB NEMO in December '
     '2015 under the name Nord Pool Spot AS, Norwegian company number 984 058 098 ({S:ofgem_nemo_2015}); registry_id '
     'is left blank until the current registration is confirmed. Runs UK day-ahead and half-hour auctions ({S:nordpool_da}).'),
    ('eex', 'European Energy Exchange AG', 'EEX', 'exchange', '', '', 'https://www.eex.com/', '', '', '', '',
     'eex_futures',
     'Exchange based in Leipzig, Germany; lists EEX GB Power Futures ({S:eex_futures}). German commercial register '
     'number not checked.'),
    ('ice', 'ICE Futures Europe', 'ICE', 'exchange', '', '', 'https://www.ice.com/', '', '', '', 'GB-COH-01528617',
     'ice_ubl',
     'London derivatives exchange; lists UK Base Electricity futures (symbol UBL), which clear under the ICE Clear '
     'Europe Clearing Rules ({S:ice_ubl}). A private unlimited company (Companies House 01528617).'),
    ('nged', 'National Grid Electricity Distribution', 'NGED', 'dno', '', '', 'https://dso.nationalgrid.co.uk/',
     '2022-09-20', '', 'wpd', '', 'nged_stmt',
     'Group name for the four NGED licensees ({O:nged_em}, {O:nged_sw}, {O:nged_swest}, {O:nged_wm}), which took the '
     'NGED name on 20 September 2022 (Companies House, previous names of 03600574). The brand launch date may differ by a few days.'),
    ('wpd', 'Western Power Distribution', 'WPD', 'dno', '', '', '', '', '2022-09-19', '', '', 'companies_house',
     'Former name of {O:nged} (licensees renamed 20 September 2022, Companies House 03600574). Kept so that older sources resolve.'),
    ('npg', 'Northern Powergrid', 'NPg', 'dno', '', '', 'https://www.northernpowergrid.com/', '', '', '', '', 'npg_stmt',
     'Operates the Northeast and Yorkshire licence areas ({O:npg_ne}, {O:npg_yk}) ({S:npg_stmt}).'),
    ('spen', 'SP Energy Networks', 'SPEN', 'dno', '', '', 'https://www.spenergynetworks.co.uk/', '', '', '', '',
     'spen_stmt',
     'Procures distribution flexibility for SP Distribution plc and SP Manweb plc ({O:spd}, {O:spm}) ({S:spen_stmt}).'),
    ('spenw', 'SP Electricity North West', 'SPENW', 'dno', '', '', 'https://www.enwl.co.uk/', '2025-08-04', '', 'enw',
     '', 'spenw_stmt',
     'Brand adopted after Iberdrola, through Scottish Power, acquired 88% of Electricity North West ({S:spenw_stmt}, '
     'PDF p.4). The 4 August 2025 date comes from the Iberdrola press release cited in R-001, which returned 403 in '
     'this run. The licensee is still Electricity North West Limited ({O:enwl_ltd}).'),
    ('enw', 'Electricity North West', 'ENWL', 'dno', '', '', '', '', '2025-08-03', '', '', 'spenw_stmt',
     'Former brand of {O:spenw}. Kept so that older sources resolve.'),
    ('ssen', 'SSEN Distribution', 'SSEN', 'dno', '', '', 'https://www.ssen.co.uk/', '', '', '', '', 'ssen_stmt',
     'Distribution business trading as Scottish and Southern Electricity Networks, a trading name of SSE network '
     'companies that also covers the transmission licensee ({S:ssen_stmt}). Distribution licensees: {O:shepd}, {O:sepd}.'),
    ('ukpn', 'UK Power Networks', 'UKPN', 'dno', '', '', 'https://www.ukpowernetworks.co.uk/', '', '', '', '',
     'ukpn_stmt', 'Operates three licence areas: EPN, LPN and SPN ({O:epn}, {O:lpn}, {O:spn}) ({S:ukpn_stmt}).'),
    ('epn', 'Eastern Power Networks plc', 'EPN', 'dno_licensee', 'ukpn', '', '', '', '', '', 'GB-COH-02366906',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('lpn', 'London Power Networks plc', 'LPN', 'dno_licensee', 'ukpn', '', '', '', '', '', 'GB-COH-03929195',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('spn', 'South Eastern Power Networks plc', 'SPN', 'dno_licensee', 'ukpn', '', '', '', '', '', 'GB-COH-03043097',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('enwl_ltd', 'Electricity North West Limited', '', 'dno_licensee', 'spenw', '', '', '', '', '', 'GB-COH-02366949',
     'ofgem_licensees',
     'Electricity distribution licensee ({S:ofgem_licensees}). Previous names: Norweb plc (1989-2001), United '
     'Utilities Electricity plc/Limited (2001-2007) (Companies House).'),
    ('nged_em', 'National Grid Electricity Distribution (East Midlands) plc', '', 'dno_licensee', 'nged', '', '', '',
     '', '', 'GB-COH-02366923', 'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('nged_sw', 'National Grid Electricity Distribution (South Wales) plc', '', 'dno_licensee', 'nged', '', '', '', '',
     '', 'GB-COH-02366985', 'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('nged_swest', 'National Grid Electricity Distribution (South West) plc', '', 'dno_licensee', 'nged', '', '', '',
     '', '', 'GB-COH-02366894', 'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('nged_wm', 'National Grid Electricity Distribution (West Midlands) plc', '', 'dno_licensee', 'nged', '', '', '',
     '', '', 'GB-COH-03600574', 'ofgem_licensees',
     'Electricity distribution licensee ({S:ofgem_licensees}). Named Western Power Distribution (West Midlands) plc '
     'from 1 April 2011 to 20 September 2022 (Companies House).'),
    ('npg_ne', 'Northern Powergrid (Northeast) plc', '', 'dno_licensee', 'npg', '', '', '', '', '', 'GB-COH-02906593',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('npg_yk', 'Northern Powergrid (Yorkshire) plc', '', 'dno_licensee', 'npg', '', '', '', '', '', 'GB-COH-04112320',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}).'),
    ('shepd', 'Scottish Hydro Electric Power Distribution plc', 'SHEPD', 'dno_licensee', 'ssen', '', '', '', '', '',
     'GB-COH-SC213460', 'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}; {S:ssen_stmt}).'),
    ('sepd', 'Southern Electric Power Distribution plc', 'SEPD', 'dno_licensee', 'ssen', '', '', '', '', '',
     'GB-COH-04094290', 'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}; {S:ssen_stmt}).'),
    ('spd', 'SP Distribution plc', 'SPD', 'dno_licensee', 'spen', '', '', '', '', '', 'GB-COH-SC189125',
     'ofgem_licensees', 'Electricity distribution licensee ({S:ofgem_licensees}; {S:spen_stmt}).'),
    ('spm', 'SP Manweb plc', 'SPM', 'dno_licensee', 'spen', '', '', '', '', '', 'GB-COH-02366937', 'ofgem_licensees',
     'Electricity distribution licensee ({S:ofgem_licensees}; {S:spen_stmt}).'),
]

# ---------------------------------------------------------------- LOOKUPS (code, label, definition, source key)
LK = {}
LK['LK_ORG_TYPE'] = [
    ('system_operator', 'System operator',
     'Body licensed to run the GB electricity system in real time and to buy the balancing services it needs.', 'neso_designation'),
    ('dno', 'Distribution network operator (group)',
     'A distribution network operator as it presents itself to the market, usually a trading name covering one or more licensed distribution companies.', 'ssen_stmt'),
    ('dno_licensee', 'Distribution licensee',
     'A company that holds an Ofgem electricity distribution licence for one of the 14 regional DNO licence areas.', 'ofgem_licensees'),
    ('exchange', 'Exchange',
     'An organised trading venue that lists standard power contracts (spot or derivatives) and matches buyers and sellers.', 'ofgem_nemo_2016'),
    ('regulator', 'Regulator', 'The body that regulates the GB energy sector and its licensees.', 'ofgem_about'),
    ('government_department', 'Government department',
     'A UK government department that sets energy policy and owns government-backed schemes.', 'gov_desnz'),
    ('counterparty', 'Scheme counterparty',
     'A company that holds the contracts with scheme participants and makes or collects the scheme payments.', 'gov_cfd'),
    ('settlement_agent', 'Settlement agent',
     'A company that calculates and administers settlement of a scheme on behalf of its counterparty or settlement body.', 'emrs_home'),
    ('code_administrator', 'Code administrator',
     'A company that administers an industry code and runs the central systems and processes that the code requires.', 'elexon_whatwedo'),
    ('industry_body', 'Industry body',
     'An association of licensed companies that develops shared guidance and standards but does not run mechanisms itself.', 'ena_2024'),
]
LK['LK_MECHANISM_CLASS'] = [
    ('exchange_auction', 'Exchange auction',
     'Trading on a power exchange in which orders for each delivery period are collected until gate closure and cleared together in one run, giving one price per period.', 'nordpool_da'),
    ('exchange_continuous', 'Exchange continuous trading',
     'Trading on a power exchange in which an order is matched as soon as a compatible order arrives from the other side, so trading continues until shortly before delivery and each trade has its own price.', 'nordpool_id'),
    ('exchange_derivative', 'Exchange-traded derivative',
     'A standardised futures or options contract listed on an exchange and cleared through a clearing house, for delivery or financial settlement over a future period such as a month, quarter or season.', 'ice_ubl'),
    ('otc_bilateral', 'Over-the-counter (bilateral) contract',
     'A contract agreed directly between two parties, or through a broker, rather than on an exchange order book. It may be physically delivered or settled financially.', 'ofgem_liquidity'),
    ('so_ancillary_service', 'System operator ancillary service',
     'A service that the system operator procures or requires from generation, demand or storage to keep the transmission system secure, for example frequency response, reserve, voltage support, stability, constraint management or restoration.', 'neso_bal'),
    ('balancing_mechanism', 'Balancing Mechanism',
     "The system operator's main real-time balancing tool: participants submit offers to export more or import less, and bids to do the opposite, and the system operator accepts those it needs.", 'neso_bm'),
    ('dso_flexibility', 'DSO flexibility service',
     'A service that a distribution network operator buys from flexibility providers to manage its own network, for example to defer reinforcement or to cover outages. DNOs must publish how they procure these services.', 'ofgem_31e'),
    ('capacity_mechanism', 'Capacity mechanism',
     'A scheme that pays providers to commit capacity that will be available when the system is under stress, so that enough reliable capacity exists to meet future demand.', 'gov_cm'),
    ('revenue_support_scheme', 'Revenue support scheme',
     'A government-backed scheme that reduces long-term revenue risk for eligible projects, for example by paying the difference between an agreed strike price and a market reference price.', 'gov_cfd'),
]
LK['LK_CATEGORY'] = [
    ('energy', 'Energy', 'Buying, selling or hedging electrical energy (MWh) for delivery in a given period.', 'ofgem_liquidity'),
    ('frequency_response', 'Frequency response',
     'Fast, automatic changes in active power that follow changes in system frequency, to contain and correct frequency deviations.', 'neso_rr'),
    ('reserve', 'Reserve',
     'Extra active power, or a reduction, that the system operator can call on over minutes to hours to restore the balance between supply and demand.', 'neso_rr'),
    ('thermal_constraint', 'Thermal constraint management',
     'Actions that keep power flows within the thermal limits of network circuits or boundaries, at transmission or distribution level.', 'neso_lcm'),
    ('voltage', 'Voltage', 'Absorbing or injecting reactive power to keep network voltages within their allowed range.', 'neso_reactive'),
    ('stability', 'Stability', 'Services that help the system ride through disturbances, such as inertia and short-circuit level.', 'neso_stability'),
    ('restoration', 'Restoration', 'Capability to restore electricity supplies after a total or partial shutdown of the system.', 'neso_esr'),
    ('capacity_adequacy', 'Capacity adequacy', 'Making sure enough reliable capacity is available to meet demand at times of system stress.', 'gov_cm'),
    ('investment_support', 'Investment support',
     'Encouraging investment in new low-carbon generation or storage by reducing long-term revenue risk.', 'gov_cfd'),
]
LK['LK_STATUS'] = [
    ('live', 'Live', 'Open for participation, or still running under existing contracts, at the date given in status_as_of.', 'r001'),
    ('planned', 'Planned', 'Announced by the operator and in design or implementation, but not yet open to participants.', 'r001'),
    ('trial', 'Trial', 'Running as a time-limited trial or innovation project.', 'r001'),
    ('suspended', 'Suspended', 'Temporarily not procuring or not operating; the operator expects to resume it.', 'r001'),
    ('closed', 'Closed', 'Permanently ended or replaced. The record is kept for history.', 'r001'),
]
LK['LK_COMMODITY'] = [
    ('active_power', 'Active power and energy',
     'Real power, measured in MW, and the energy it delivers over time, measured in MWh. Covers both energy trades and MW of active-power availability or response.', 'grid_code_gd'),
    ('reactive_power', 'Reactive power',
     'The part of AC power set by the phase difference between voltage and current, measured in MVAr. It is absorbed or injected to control voltage.', 'grid_code_gd'),
    ('stability', 'Stability (inertia and short-circuit level)',
     'Contributions to system inertia and short-circuit level that help the system withstand disturbances.', 'neso_stability'),
    ('firm_capacity', 'Firm capacity',
     'A commitment to have reliable capacity (MW) available at times of system stress, paid for separately from any energy sold.', 'gov_cm'),
]
LK['LK_DIRECTION'] = [
    ('up', 'Up', 'Increases net export to the system: more generation or less demand. In the Balancing Mechanism this is the direction of an offer.', 'neso_bm'),
    ('down', 'Down', 'Reduces net export to the system: less generation or more demand. In the Balancing Mechanism this is the direction of a bid.', 'neso_bm'),
    ('both', 'Both', 'The mechanism procures, or lets participants trade, in either direction; for example energy trading, where participants can buy or sell.', 'r001'),
    ('not_applicable', 'Not applicable', 'The mechanism has no physical delivery direction, for example a cash-settled financial contract.', 'r001'),
]
LK['LK_YESNO'] = [
    ('yes', 'Yes', 'Researched: the attribute applies or the feature is present.', 'r001'),
    ('no', 'No', 'Researched: the attribute does not apply or the feature is absent.', 'r001'),
    ('not_applicable', 'Not applicable', 'Researched: the question does not apply to this mechanism.', 'r001'),
    ('unknown', 'Unknown', 'Researched, but no authoritative source was found.', 'r001'),
]
LK['LK_CONTRACT_LENGTH_BAND'] = [
    ('le_day', 'Less than or equal to a day', "The provider's delivery contract lasts one day or less.", 'fmr_smd'),
    ('day_to_week', 'Day < x <= Week', "The provider's delivery contract lasts more than a day and up to a week.", 'fmr_smd'),
    ('week_to_month', 'Week < x <= Month', "The provider's delivery contract lasts more than a week and up to a month.", 'fmr_smd'),
    ('month_to_year', 'Month < x <= Year', "The provider's delivery contract lasts more than a month and up to a year.", 'fmr_smd'),
]
LK['LK_DSO_STANDARD_PRODUCT'] = [
    # code, label, definition, source, external_code
    ('su', 'Scheduled Utilisation (SU)',
     'The provider changes its import or export at times fixed when the trade is agreed. Only delivered energy is paid (GBP/MWh); there is no availability payment.', 'fmr_pd', 'SU'),
    ('pr', 'Peak Reduction (PR)',
     'The provider lowers its peak power over a period agreed at trade, rather than delivering continuously. Only delivered energy is paid.', 'fmr_pd', 'PR'),
    ('ou', 'Operational Utilisation (OU)',
     'The DNO instructs the provider in real time, usually after a network event, and pays only for energy delivered. Variants differ by maximum response time (2 or 15 minutes).', 'fmr_pd', 'OU'),
    ('sa_ou', 'Scheduled Availability + Operational Utilisation (SA+OU)',
     'The DNO buys availability windows at trade, which cannot be changed afterwards, and then instructs utilisation within them. Availability is paid in GBP/MW/h and utilisation in GBP/MWh. DNOs also write SAOU or OUSA.', 'fmr_pd', 'SA+OU'),
    ('va_ou', 'Variable Availability + Operational Utilisation (VA+OU)',
     'Like SA+OU, but the DNO can refine which availability it needs closer to the time (week ahead, or month ahead for the week-ahead variant). DNOs also write VAOU or OUVA.', 'fmr_pd', 'VA+OU'),
]
# code, label, definition, source, external_code, product_code, product_fit, payment_structure,
# availability_refinement, max_response_time_min, utilisation_instruction_timing, nearest_product_code
NA = 'not_applicable'
LK['LK_DSO_PRODUCT_VARIANT'] = [
    ('su', 'SU: Scheduled Utilisation', 'The single standard variant of Scheduled Utilisation: delivery times and prices fixed at trade, utilisation-only payment.', 'fmr_pd', 'SU', 'su', 'standard', 'utilisation_only', NA, NA, 'at_trade', ''),
    ('pr', 'PR: Peak Reduction', 'The single standard variant of Peak Reduction: peak delivery expectation, set at trade, utilisation-only payment.', 'fmr_pd', 'PR', 'pr', 'standard', 'utilisation_only', NA, NA, 'at_trade', ''),
    ('ou_2', 'OU-2: Operational Utilisation, 2 min', 'Operational Utilisation with a maximum response time of 2 minutes from a real-time instruction.', 'fmr_pd', 'OU-2', 'ou', 'standard', 'utilisation_only', NA, '2', 'real_time', ''),
    ('ou_15', 'OU-15: Operational Utilisation, 15 min', 'Operational Utilisation with a maximum response time of 15 minutes from a real-time instruction.', 'fmr_pd', 'OU-15', 'ou', 'standard', 'utilisation_only', NA, '15', 'real_time', ''),
    ('sa_ou_2', 'SA OU-2: Scheduled Availability + OU, 2 min', 'Fixed availability bought at trade; utilisation instructed in real time with a 2-minute maximum response. Added in June 2026 by change proposal FLX CP003.', 'fmr_pd', 'SA OU-2', 'sa_ou', 'standard', 'availability_and_utilisation', 'not_allowed', '2', 'real_time', ''),
    ('sa_ou_15', 'SA OU-15: Scheduled Availability + OU, 15 min', 'Fixed availability bought at trade; utilisation instructed in real time with a 15-minute maximum response. Added in June 2026 by change proposal FLX CP003.', 'fmr_pd', 'SA OU-15', 'sa_ou', 'standard', 'availability_and_utilisation', 'not_allowed', '15', 'real_time', ''),
    ('sa_ou_da', 'SA OU-DA: Scheduled Availability + OU, day ahead', 'Fixed availability bought at trade; utilisation confirmed operationally the day before delivery.', 'fmr_pd', 'SA OU-DA', 'sa_ou', 'standard', 'availability_and_utilisation', 'not_allowed', NA, 'operational_day_ahead', ''),
    ('sa_ou_wa', 'SA OU-WA: Scheduled Availability + OU, week ahead', 'Fixed availability bought at trade; utilisation confirmed operationally the week before delivery. Added in June 2026 by change proposal FLX CP003, proposed by Northern Powergrid.', 'fmr_pd', 'SA OU-WA', 'sa_ou', 'standard', 'availability_and_utilisation', 'not_allowed', NA, 'operational_week_ahead', ''),
    ('va_ou_2', 'VA OU-2: Variable Availability + OU, 2 min', 'Availability refined week ahead; utilisation instructed in real time with a 2-minute maximum response.', 'fmr_pd', 'VA OU-2', 'va_ou', 'standard', 'availability_and_utilisation', 'week_ahead', '2', 'real_time', ''),
    ('va_ou_15', 'VA OU-15: Variable Availability + OU, 15 min', 'Availability refined week ahead; utilisation instructed in real time with a 15-minute maximum response.', 'fmr_pd', 'VA OU-15', 'va_ou', 'standard', 'availability_and_utilisation', 'week_ahead', '15', 'real_time', ''),
    ('va_ou_da', 'VA OU-DA: Variable Availability + OU, day ahead', 'Availability refined week ahead; utilisation confirmed operationally the day before delivery.', 'fmr_pd', 'VA OU-DA', 'va_ou', 'standard', 'availability_and_utilisation', 'week_ahead', NA, 'operational_day_ahead', ''),
    ('va_ou_wa', 'VA OU-WA: Variable Availability + OU, week ahead', 'Availability refined month ahead; utilisation confirmed operationally the week before delivery.', 'fmr_pd', 'VA OU-WA', 'va_ou', 'standard', 'availability_and_utilisation', 'month_ahead', NA, 'operational_week_ahead', ''),
    ('legacy_sustain', 'Sustain (legacy ENA product)', 'Pre-2024 ENA product: a change in import or export over a period agreed in advance, to keep a network within its firm capacity; utilisation-only payment. Nearest current product: SU (inferred).', 'ena_2022', 'Sustain', '', 'legacy', NA, NA, NA, NA, 'su'),
    ('legacy_secure', 'Secure (legacy ENA product)', 'Pre-2024 ENA product: the DNO buys in advance the right to call on a change in import or export close to real time, depending on network conditions; availability and utilisation payments, with availability agreed at different horizons by different DNOs. Nearest current product: SA+OU or VA+OU (inferred; varies by DNO).', 'ena_2022', 'Secure', '', 'legacy', NA, NA, NA, NA, 'sa_ou'),
    ('legacy_dynamic', 'Dynamic (legacy ENA product)', 'Pre-2024 ENA product: the DNO buys in advance the ability to call on a change in output after a network fault; mostly availability and utilisation payments. Nearest current product: SA+OU (inferred).', 'ena_2022', 'Dynamic', '', 'legacy', NA, NA, NA, NA, 'sa_ou'),
    ('legacy_restore', 'Restore (legacy ENA product)', 'Pre-2024 ENA product: after a loss of supply, the provider stays off supply or reconnects with less demand or more generation, so that supplies can be restored faster; utilisation-only payment. Nearest current product: OU (inferred).', 'ena_2022', 'Restore', '', 'legacy', NA, NA, NA, NA, 'ou'),
    ('npg_flexadvance', 'FlexAdvance (Northern Powergrid, non-standard)', 'Northern Powergrid variant of Scheduled Utilisation that pays part of the forecast value upfront; offered subject to a derogation from the Flexibility Market Rules on standard products.', 'npg_stmt', 'FlexAdvance', '', 'non_standard', NA, NA, NA, NA, 'su'),
]

LK_EXTRA_COLS = {
    'LK_DSO_STANDARD_PRODUCT': ['external_code'],
    'LK_DSO_PRODUCT_VARIANT': ['external_code', 'product_code', 'product_fit', 'payment_structure',
                               'availability_refinement', 'max_response_time_min',
                               'utilisation_instruction_timing', 'nearest_product_code'],
}

# ---------------------------------------------------------------- numbering and checks
src_id = {k[0]: f'SRC-{i:04d}' for i, k in enumerate(SOURCES, 1)}
org_id = {k[0]: f'ORG-{i:04d}' for i, k in enumerate(ORGS, 1)}
assert len(src_id) == len(SOURCES) and len(org_id) == len(ORGS), 'duplicate keys'


def fill(text):
    def rep(m):
        kind, key = m.group(1), m.group(2)
        table = src_id if kind == 'S' else org_id
        assert key in table, f'unknown {kind} key {key}'
        return table[key]
    return re.sub(r'\{([SO]):([a-z0-9_]+)\}', rep, text)


def write(name, header, rows):
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\r\n').writerows([header] + rows)
    with open(os.path.join(OUT, name), 'wb') as fh:
        fh.write(('﻿' + out.getvalue()).encode('utf-8'))


os.makedirs(OUT, exist_ok=True)
used_src = set()

src_rows = []
for k, title, pub, url, st, dt, ver, arch, notes in SOURCES:
    publisher = org_id.get(pub, pub)
    src_rows.append([src_id[k], title, publisher, url, st, dt, ver, ACC, arch, fill(notes)])
write('SOURCES.csv', ['source_id', 'title', 'publisher', 'url', 'source_type', 'doc_type', 'version_or_date',
                      'accessed_date', 'archive_url', 'notes'], src_rows)

org_rows = []
for k, name, short, otype, parent, lic, url, vf, vt, pred, reg, src, notes in ORGS:
    used_src.add(src)
    used_src.update(re.findall(r'\{S:([a-z0-9_]+)\}', notes))
    org_rows.append([org_id[k], name, short, otype, org_id[parent] if parent else '', lic, url, vf, vt,
                     org_id[pred] if pred else '', reg, src_id[src], fill(notes)])
write('ORGANISATIONS.csv', ['org_id', 'name', 'short_name', 'org_type', 'parent_org_id', 'licence_id', 'url',
                            'valid_from', 'valid_to', 'predecessor_org_id', 'registry_id', 'source_id', 'notes'],
      org_rows)

codes = {}
for name, rows in LK.items():
    extra = LK_EXTRA_COLS.get(name, [])
    out_rows = []
    seen = set()
    for r in rows:
        code, label, definition, src = r[:4]
        assert re.fullmatch(r'[a-z][a-z0-9_]*', code), (name, code)
        assert code not in seen, (name, code)
        seen.add(code)
        used_src.add(src)
        assert len(r) == 4 + len(extra), (name, code)
        out_rows.append([code, label, definition, src_id[src]] + list(r[4:]))
    codes[name] = seen
    write(name + '.csv', ['code', 'label', 'definition', 'source_id'] + extra, out_rows)

# referential checks
for r in LK['LK_DSO_PRODUCT_VARIANT']:
    assert r[5] == '' or r[5] in codes['LK_DSO_STANDARD_PRODUCT'], r[0]
    assert r[11] == '' or r[11] in codes['LK_DSO_STANDARD_PRODUCT'], r[0]
    assert r[6] in ('standard', 'legacy', 'non_standard'), r[0]
for o in ORGS:
    assert o[3] in codes['LK_ORG_TYPE'], o[0]
    assert not o[10] or re.fullmatch(r'(GB-COH|FR-RCS)-[A-Z0-9]+', o[10]), o[0]
for row in org_rows:
    assert re.fullmatch(r'ORG-\d{4}', row[0])
unused = [k for k in src_id if k not in used_src]
print('sources:', len(src_rows), 'orgs:', len(org_rows), {k: len(v) for k, v in codes.items()})
print('sources not cited by any draft row (source_id or notes):', unused)
print('ORG ids:', {k: v for k, v in org_id.items()})
print('SRC ids:', {k: v for k, v in src_id.items()})
