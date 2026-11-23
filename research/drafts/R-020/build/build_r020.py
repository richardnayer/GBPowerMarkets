"""Build the R-020 drafts in research/drafts/R-020/ and check them against CSV/.

Outputs (UTF-8 with BOM, CRLF, written with the csv module):
  LK_PLATFORM, LK_ORG_ROLE, LK_PRICING_RULE, LK_AUCTION_TYPE, LK_MARKET_STRUCTURE, LK_MARKET_OBJECTIVE,
  LK_CLEARING_ALGORITHM, LK_DISPATCHER, LK_AGGREGATION_LEVEL      (new lookups)
  LK_ORG_TYPE_additions, ORGANISATIONS_additions, SOURCES_additions (rows to append to existing tables)
  EXISTING_ROW_UPDATES                                             (cell edits to existing reference rows)
  MECHANISM_ORG_ROLE                                               (new table)
  VALUE_MAPPING, COLUMN_ACTIONS                                    (how to convert the remaining text columns)

Checks (the script fails if any is broken):
  * every current value in the mapped columns is covered, with exactly the IDs found in CSV/;
  * every ORG-, SRC-, MEC-, role, platform and lookup code referenced resolves;
  * on platform rows, org_id equals LK_PLATFORM.operator_org_id;
  * every new source is cited at least once; every lookup code is snake_case;
  * no duplicate (mechanism_id, org_id, role, platform_code) in MECHANISM_ORG_ROLE.

Run: python -I build_r020.py <repo_root>
"""
import csv, io, os, re, sys
from collections import Counter, defaultdict

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'research', 'drafts', 'R-020')
ACCESSED = '2026-11-23'


def load(name):
    with open(os.path.join(ROOT, 'CSV', name + '.csv'), encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def write(name, header, rows):
    buf = io.StringIO(newline='')
    w = csv.writer(buf, lineterminator='\r\n')
    w.writerow(header)
    w.writerows(rows)
    with open(os.path.join(OUT, name + '.csv'), 'wb') as fh:
        fh.write(('﻿' + buf.getvalue()).encode('utf-8'))


def ids(spec):
    """'1-9,22' -> ['MEC-0001', ..., 'MEC-0009', 'MEC-0022']"""
    out = []
    for part in spec.split(','):
        a, _, b = part.partition('-')
        out += [f'MEC-{n:04d}' for n in range(int(a), int(b or a) + 1)]
    return out


def rng(id_list):
    nums = sorted(int(i[4:]) for i in id_list)
    parts, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        parts.append(f'MEC-{start:04d}' if start == prev else f'MEC-{start:04d}..MEC-{prev:04d}')
        if n is not None:
            start = prev = n
    return '; '.join(parts)


# ----------------------------------------------------------------------------------------------------------
# New SOURCES rows (SRC-0046 onwards). Columns follow CSV/SOURCES.csv.
# ----------------------------------------------------------------------------------------------------------
NESO_TERMS = ('NESO website terms (https://www.neso.energy/terms-and-conditions) reserve the intellectual property in '
              'site content; copies for own use only. Facts and links only; definitions are paraphrased.')
OGL_LEG = ('legislation.gov.uk says all content is available under the Open Government Licence v3.0 except where '
           'otherwise stated (Crown and database right); https://www.legislation.gov.uk/help')
NOT_CHECKED = 'terms not checked in this run (R-019).'
SOURCES = [
    ('SRC-0046', 'EAC Reserve and Response Algorithm: Public description', 'ORG-0001',
     'https://www.neso.energy/document/282401/download', 'primary', 'other', '2024-06', ACCESSED, '',
     'Written by N-SIDE for NESO (N-SIDE disclaimer, PDF p.7). PDF p.8 overview table: closed double-sided auction, '
     'objective of maximising social welfare, uniform clearing price per product and service window. PDF p.4 '
     'glossary: NESO is the Buyer and Market Operator; the EAC system includes a participant portal that is part of '
     'the Single Markets Platform. PDF p.10: objective function. sha256 965d6999d0c10d09.', NESO_TERMS),
    ('SRC-0047', 'Response Services Procurement Rules, version 6', 'ORG-0001',
     'https://www.neso.energy/document/378246/download', 'primary', 'rulebook', '2026-07-31 (v6; published 2026-07-16)',
     ACCESSED, '',
     'Rules for the DC, DM and DR auctions. PDF p.10 para 9.1: matching maximises Market Welfare and sets a unique '
     'Market Clearing Price per window and product. PDF p.13 para 12.2: each contract takes the Market Clearing '
     'Price. PDF p.32 (Registration and Pre-Qualification Procedure): an Auction Unit may combine several assets only '
     'if all are in the same GSP Group; NESO may require the same Grid Supply Point instead. Listed as current on the '
     'NESO Dynamic Containment page. sha256 daf0bd2f040d8b73.', NESO_TERMS),
    ('SRC-0048', 'Quick Reserve (QR) Procurement Rules, version 4.0', 'ORG-0001',
     'https://www.neso.energy/document/378266/download', 'primary', 'rulebook',
     '2026-03-31 (v4.0; published 2026-03-16)', ACCESSED, '',
     'PDF p.9 para 10.1: matching maximises Market Welfare and sets a unique Market Clearing Price. PDF p.12 para '
     '13.2: each QR Contract takes the Market Clearing Price. PDF p.29: assets combined in one Auction Unit must be in '
     'the same GSP Group; NESO may require the same Grid Supply Point. Listed as current on the NESO Quick Reserve '
     'page. sha256 a7d21b915d453163.', NESO_TERMS),
    ('SRC-0049', 'Quick Reserve Service Terms, version 2.1', 'ORG-0001',
     'https://www.neso.energy/document/364276/download', 'primary', 'service_terms',
     '2025-09-02 (v2.1; published 2025-08-06)', ACCESSED, '',
     'PDF p.5 para 5.3: NESO issues Bid-Offer Acceptances to BM-participating QR Units. PDF p.13: NESO issues '
     'Instructions to other QR Units; PDF p.21 and p.23 refer to the Open Balancing Platform (OBP). sha256 '
     'caaf0ec61b52e960.', NESO_TERMS),
    ('SRC-0050', 'Static FFR Procurement Rules, version 2.0', 'ORG-0001',
     'https://www.neso.energy/document/384306/download', 'primary', 'rulebook',
     '2026-07-31 (v2.0; published 2026-07-13)', ACCESSED, '',
     'PDF p.9 para 9: sell orders are matched to NESO\'s buy order to maximise total auction surplus and set a Market '
     'Clearing Price per EFA block. PDF p.19: auctions run on a Designated Auction Platform chosen by NESO. PDF p.21: '
     'the Single Market Platform is NESO\'s online registration and pre-qualification platform. PDF p.22: a Static FFR '
     'Unit is a collection of one or more eligible assets; no location limit on combining assets was found in these '
     'rules. sha256 1baf853cd50f513b.', NESO_TERMS),
    ('SRC-0051', 'The Electricity Capacity Regulations 2014 (SI 2014/2043), regulations 2 and 24',
     'legislation.gov.uk (The National Archives)', 'https://www.legislation.gov.uk/uksi/2014/2043/regulation/2',
     'primary', 'statute', 'revised text, no outstanding effects shown on 2026-11-23', ACCESSED, '',
     'Reg 2(1): "Delivery Body" means the national system operator, unless its functions are transferred to an '
     'alternative delivery body; "administrative parties" are the Secretary of State, the Authority (Ofgem), the '
     'Delivery Body and the Settlement Body. Reg 24(1) (https://www.legislation.gov.uk/uksi/2014/2043/regulation/24): '
     'the Delivery Body must hold the capacity auction. "National system operator" is defined in the Energy Act 2013 '
     '(SRC-0052).', OGL_LEG),
    ('SRC-0052', 'Energy Act 2013, sections 8(3) and 27(6) (as amended)', 'legislation.gov.uk (The National Archives)',
     'https://www.legislation.gov.uk/ukpga/2013/32/section/27', 'primary', 'statute',
     'revised text; s.8(3) and s.27(6) substituted with effect from 2024-10-01', ACCESSED, '',
     'For Part 2 Chapter 2 (CfD, s.8(3): https://www.legislation.gov.uk/ukpga/2013/32/section/8) and Chapter 3 '
     '(Capacity Market, s.27(6)), "national system operator" means the person designated as the Independent System '
     'Operator and Planner under section 162 of the Energy Act 2023. Substituted by SI 2024/706 regs 1(1), 9(2) and '
     '9(4) from 1 October 2024. NESO\'s designation: SRC-0001.', OGL_LEG),
    ('SRC-0053', 'The Contracts for Difference (Allocation) Regulations 2014 (SI 2014/2011), regulation 2',
     'legislation.gov.uk (The National Archives)', 'https://www.legislation.gov.uk/uksi/2014/2011/regulation/2',
     'primary', 'statute', 'revised text, no outstanding effects shown on 2026-11-23', ACCESSED, '',
     'Reg 2: "delivery body" means the national system operator, or an alternative delivery body if its Chapter 2 '
     'functions are transferred. "National system operator": SRC-0052 (s.8(3)).', OGL_LEG),
    ('SRC-0054', 'EUPHEMIA Public Description: Single Price Coupling Algorithm', 'NEMO Committee',
     'https://www.nemo-committee.eu/assets/files/euphemia-public-description-2024.pdf', 'primary', 'other',
     '2024-08-01', ACCESSED, '',
     'PDF p.4: the PCR solution is used for both SDAC and the SIDC intraday auctions. PDF p.5: EUPHEMIA (Pan-European '
     'Hybrid Electricity Market Integration Algorithm) has been used since February 2014 to calculate allocations '
     'and prices across Europe, maximising overall economic surplus. Does not mention GB or the SEM-GB auctions. '
     'sha256 2bb27431063e2f6c.',
     '"All rights reserved" (copyright disclaimer, PDF p.1): may not be copied or reproduced without the PCR PXs\' '
     'permission. Facts only; definitions are paraphrased.'),
    ('SRC-0055', 'Continuous Trading Matching Algorithm: Public Description', 'NEMO Committee',
     'https://www.nemo-committee.eu/assets/files/public-description-continuous-trading-matching-algorithm-updated.pdf',
     'primary', 'other', '', ACCESSED, '',
     'Undated. Describes the SIDC (EU) continuous intraday matching. PDF p.15: two orders are matched at the limit '
     'price of the order that was already in the order book (price-time priority). GB is not in SIDC; used here only '
     'to define how continuous trading sets prices. sha256 2e57b40e75ce26e4.',
     '"All rights reserved" (joint IP of the SIDC NEMOs and Deutsche Borse AG). Facts only; paraphrased.'),
    ('SRC-0056', 'Flexible Power: Provider User Guide, version 1.1', 'ORG-0020',
     'https://www.ssen.co.uk/globalassets/our-services/flexibility-services-document-library/service-documentation/flexible-power---ssen-fsp-user-guide-v1.1.pdf',
     'primary', 'other', '2025-08-15 (v1.1)', ACCESSED, '',
     'PDF p.3 s.1.2: Flexible Power is a platform used by SSEN and other network operators to schedule, dispatch and '
     'settle flexibility services; most SSEN requirements are dispatched through it.', NOT_CHECKED),
    ('SRC-0057', 'Flexible Power (website home page)', 'ORG-0038', 'https://www.flexiblepower.co.uk/', 'primary',
     'webpage', '', ACCESSED, 'https://web.archive.org/web/20260115015058/https://www.flexiblepower.co.uk/',
     'Live site reset the connection; read from the Wayback Machine copy of 15 January 2026. Says Flexible Power is a '
     'joint initiative of four DNOs (NGED, Northern Powergrid, SSEN and SP Energy Networks); contracted providers use '
     'the joint portal to declare availability, receive dispatch signals and view performance and settlement '
     'reports; the Flexible Power trademark is wholly owned by National Grid Electricity Distribution. The live '
     '/about page (read 2026-11-23) is out of date: it names five DNOs including WPD and ENW and has placeholder text.',
     NOT_CHECKED),
    ('SRC-0058', 'Electron privacy notice', 'ORG-0037', 'https://electron.net/electron-privacy-policy/', 'primary',
     'webpage', '', ACCESSED, '',
     'Section 2: the data controller is Chaddenwych Services Ltd t/a Electron, Companies House number 09914060, '
     'registered office 86-90 Paul Street, London. The home page (https://electron.net/) lists ElectronConnect logins '
     'for SP Energy Networks, SP Electricity North West and SSEN.', NOT_CHECKED),
    ('SRC-0059', 'REMA Scheduling and Dispatch Assessment', 'ORG-0001', 'https://www.neso.energy/document/377331/download',
     'primary', 'other', '2026-02', ACCESSED, '',
     'PDF p.3: the REMA programme assessed self-dispatch (e.g. Balancing Mechanism reform) against central dispatch; '
     'PDF p.4: DESNZ chose not to take central dispatch forward, so GB keeps self-dispatch. sha256 21f9710f81bb8f85.',
     NESO_TERMS),
    ('SRC-0060', 'About the SEM-GB Intraday Auction (Nord Pool support article)', 'ORG-0011',
     'https://support.nordpoolgroup.com/support/solutions/articles/8000086528-about-the-sem-gb-intraday-auction',
     'primary', 'webpage', '2022-11-24 (last modified)', ACCESSED, '',
     'Nord Pool runs the SEM-GB Intraday Auction, linking GB to the SEM over the Moyle and East-West interconnectors, '
     'with two daily auctions: IDA1 (gate closure 18:30 CET, next-day delivery) and IDA2 (gate closure 09:00 CET, '
     'delivery 12:00-24:00). Does not name the clearing algorithm.',
     'no statement found (see SRC-0006).'),
]

# ----------------------------------------------------------------------------------------------------------
# New ORGANISATIONS rows (ORG-0036 onwards) and the new org type.
# ----------------------------------------------------------------------------------------------------------
ORGS = [
    ('ORG-0036', 'Piclo', 'Piclo', 'platform_provider', '', 'https://www.piclo.com/', '', '', '', '', 'SRC-0012',
     'Runs the Piclo Flex marketplace. Northern Powergrid uses it end to end, from qualification to dispatch and '
     'settlement (SRC-0012, PDF p.10); NGED uses it as a second route into its markets (SRC-0011, PDF p.6). Legal '
     'entity not confirmed from a primary source: Companies House lists Open Utility Ltd (08384033, incorporated '
     '2013) and Piclo Ltd (14266869, incorporated 2022) at the same registered office, and secondary sources say Open '
     'Utility Ltd operates Piclo. registry_id left blank until confirmed. piclo.energy redirects to piclo.com, which '
     'reset the connection in this run.'),
    ('ORG-0037', 'Chaddenwych Services Limited', 'Electron', 'platform_provider', '', 'https://electron.net/', '', '', '',
     'GB-COH-09914060', 'SRC-0058',
     'Trades as Electron (SRC-0058) and runs the ElectronConnect platform. SPEN selected it after a competitive tender '
     '(SRC-0013, PDF p.10); SPENW has used it since March 2024 (SRC-0014, PDF p.20); SSEN uses it for qualification, '
     'contracting and bidding (SRC-0015, PDF p.14). Companies House 09914060: private limited company, incorporated '
     '14 December 2015, active.'),
    ('ORG-0038', 'Flexible Power', 'Flexible Power', 'platform_provider', '', 'https://www.flexiblepower.co.uk/', '', '',
     '', '', 'SRC-0057',
     'A joint initiative of four DNOs (NGED, Northern Powergrid, SSEN and SP Energy Networks), not a company, so no '
     'registry_id. Its website says the Flexible Power trademark is wholly owned by NGED (ORG-0014) (SRC-0057, '
     'archived 15 January 2026). Used by NGED (SRC-0011) and SSEN (SRC-0015, SRC-0056) for dispatch and settlement.'),
]
ORG_TYPES = [
    ('platform_provider', 'Platform provider',
     'A company or joint initiative that runs a software platform on which buyers and providers register, trade, '
     'dispatch or settle flexibility services, without itself buying or selling the service.', 'SRC-0013'),
]

# ----------------------------------------------------------------------------------------------------------
# Lookups (code, label, definition, source_id [, extra columns])
# ----------------------------------------------------------------------------------------------------------
LK = {}
LK['LK_PLATFORM'] = (
    ['code', 'label', 'definition', 'source_id', 'operator_org_id', 'url', 'notes'],
    [
        ('neso_eac', 'NESO Enduring Auction Capability (EAC)',
         "NESO's system for its daily day-ahead auctions of frequency response and reserve. It combines a clearing "
         "algorithm that co-optimises the services, a participant portal inside the Single Markets Platform, and the "
         "processes that pass results to NESO's control room.",
         'SRC-0046', 'ORG-0001', 'https://www.neso.energy/industry-information/balancing-services/enduring-auction-capability-eac',
         'SRC-0039 lists the services auctioned on EAC (DC, DM, DR, Balancing Reserve, Quick Reserve; Slow Reserve to follow).'),
        ('neso_smp', 'NESO Single Markets Platform (SMP)',
         "NESO's online platform where providers register, set up their assets and units, and pre-qualify them for "
         "NESO balancing services. It also hosts the participant portal for EAC auctions.",
         'SRC-0040', 'ORG-0001', 'https://www.neso.energy/industry-information/balancing-services/single-markets-platform',
         'NESO\'s own spelling is "Single Markets Platform"; some NESO rules write "Single Market Platform".'),
        ('nged_market_gateway', 'NGED Market Gateway',
         "NGED's own flexibility platform. Providers use it to register, qualify, sign the overarching contract, "
         "register assets and take part in trades. It can also exchange data with third-party market platforms.",
         'SRC-0011', 'ORG-0014', 'https://dso.nationalgrid.co.uk/',
         'Described in SRC-0011, PDF p.6. No page of its own was found; the URL is the NGED DSO site.'),
        ('flexible_power', 'Flexible Power portal',
         'A portal shared by several DNOs for running contracted flexibility. Providers declare availability, '
         'receive dispatch instructions and see performance and settlement reports.',
         'SRC-0057', 'ORG-0038', 'https://www.flexiblepower.co.uk/',
         'NGED calls it the Flexible Power Portal (FPP), its core operational system (SRC-0011, PDF p.6). SSEN '
         'describes it as its dispatch platform (SRC-0015, PDF p.14 and p.26; SRC-0056).'),
        ('piclo_flex', 'Piclo Flex',
         'A third-party flexibility marketplace on which DNOs publish requirements and run competitions. Some DNOs '
         'also use it for pre-qualification, asset registration, dispatch and settlement.',
         'SRC-0012', 'ORG-0036', 'https://www.piclo.com/',
         'Northern Powergrid uses it end to end (SRC-0012, PDF p.10). SPEN stopped using it at the end of Q1 2026 '
         '(SRC-0013, PDF p.10).'),
        ('electronconnect', 'ElectronConnect',
         'A third-party flexibility market platform that DNOs use for pre-qualification, contracting and bidding. '
         'Some DNOs also use it for availability declarations, scheduling, dispatch and settlement.',
         'SRC-0014', 'ORG-0037', 'https://electron.net/',
         'SPENW: core market platform since March 2024 (SRC-0014, PDF p.20). SPEN: from April 2026 (SRC-0013, PDF '
         'p.9). SSEN: qualification, contracting and bidding (SRC-0015, PDF p.14).'),
        ('epex_localflex', 'EPEX SPOT Localflex',
         "EPEX SPOT's platform for local flexibility markets, on which a DNO publishes its needs and runs long-term "
         'and day-ahead flexibility auctions.',
         'SRC-0016', 'ORG-0010', 'https://www.epexspot.com/',
         'UK Power Networks uses it for both its long-term and day-ahead auctions (SRC-0016, PDF p.3, p.7, p.12). No '
         'Localflex page was read (epexspot.com refuses automated clients), so the URL is the EPEX SPOT home page.'),
    ])
LK['LK_ORG_ROLE'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('operator', 'Operator',
         'Runs the mechanism and sets the terms participants deal under. For a balancing or flexibility service this '
         'is the buyer (NESO or a DNO); for an exchange market it is the exchange; for a regulated regime it is the '
         'body that administers it.', 'SRC-0046'),
        ('delivery_body', 'Delivery body',
         "The body that legislation makes responsible for running a government scheme's allocation: registering "
         'applicants, checking eligibility and holding the auction or allocation round.', 'SRC-0051'),
        ('policy_owner', 'Policy owner',
         'The government department that sets the policy and legal framework for the mechanism.', 'SRC-0021'),
        ('counterparty', 'Counterparty or settlement body',
         'Holds the contracts or obligations with scheme participants and makes or collects the scheme payments, for '
         'example the CfD counterparty or the Capacity Market Settlement Body.', 'SRC-0020'),
        ('settlement_agent', 'Settlement agent',
         "Calculates and administers settlement on behalf of a scheme's counterparty or settlement body.", 'SRC-0020'),
        ('regulator', 'Regulator (named role)',
         "A regulator with a specific role in the mechanism's own rules, such as hearing appeals or amending rules. "
         'Not recorded just because the operator holds a licence.', 'SRC-0051'),
        ('market_platform', 'Market platform',
         'Runs the IT system on which participants register, pre-qualify, submit bids or orders and receive results. '
         'The system is named in platform_code where it has its own name.', 'SRC-0046'),
        ('dispatch_platform', 'Dispatch platform',
         'Runs the IT system through which the buyer sends instructions to contracted providers and receives the '
         'availability, metering or performance data used for settlement.', 'SRC-0011'),
    ])
LK['LK_PRICING_RULE'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('pay_as_clear', 'Pay-as-clear (uniform price)',
         'All accepted orders for the same product and period settle at one clearing price set by the auction, '
         'whatever price each order stated.', 'SRC-0046'),
        ('pay_as_bid', 'Pay-as-bid (own price)',
         'Each accepted order or trade settles at its own price, not at a common clearing price. In continuous '
         'trading, an incoming order trades at the price of the matching order already waiting in the order book.',
         'SRC-0055'),
    ])
LK['LK_AUCTION_TYPE'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('sealed_double_sided', 'Sealed (closed) double-sided auction',
         'Buyers and sellers both submit priced orders before gate closure. No participant sees the other orders, '
         'and all orders are cleared together in one run.', 'SRC-0046'),
    ])
LK['LK_MARKET_STRUCTURE'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('single_buyer', 'Single buyer (one-to-many)',
         'One party buys from many competing sellers, as when a system or network operator procures a service.',
         'SRC-0046'),
        ('multilateral', 'Multilateral (many-to-many)',
         'Many buyers and many sellers trade with one another through a central venue, such as an exchange auction '
         'or order book.', 'SRC-0041'),
    ])
LK['LK_MARKET_OBJECTIVE'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('maximise_social_welfare', 'Maximise social welfare',
         'The clearing algorithm chooses the accepted orders that give the largest total surplus: what the accepted '
         'buyers were willing to pay minus what the accepted sellers asked, over the accepted volumes.', 'SRC-0046'),
    ])
LK['LK_CLEARING_ALGORITHM'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('euphemia', 'EUPHEMIA',
         'The price-coupling algorithm that European power exchanges built under the Price Coupling of Regions '
         'project. It is used for EU day-ahead market coupling and EU intraday auctions, matching orders across '
         'bidding zones within network limits so as to maximise overall economic surplus. It is an algorithm, not a '
         'platform or an organisation.', 'SRC-0054'),
    ])
LK['LK_DISPATCHER'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('operator', 'Operator instructs',
         "The mechanism's operator (for example NESO or the DNO) decides when the provider delivers and sends it "
         'instructions. The operator is the org_id with role operator in MECHANISM_ORG_ROLE.', 'SRC-0049'),
        ('self', 'Self-dispatched',
         'Nobody instructs the provider. It either responds automatically to a measured signal such as system '
         'frequency, or sets its own output to meet the position it has traded, as in GB\'s self-dispatch wholesale '
         'market.', 'SRC-0059'),
        ('not_applicable', 'Not applicable',
         'Nothing is physically dispatched, for example a cash-settled financial contract.', 'SRC-0042'),
    ])
LK['LK_AGGREGATION_LEVEL'] = (
    ['code', 'label', 'definition', 'source_id'],
    [
        ('gsp_group', 'Within one GSP Group',
         'Several assets can be combined into one unit only if they are all in the same Grid Supply Point Group (a '
         'regional group of grid supply points defined in the BSC). The operator may require a single grid supply '
         'point instead.', 'SRC-0047'),
        ('national', 'Anywhere in GB',
         'Assets anywhere in Great Britain can be combined into one unit; the rules set no location limit.',
         'SRC-0050'),
    ])

# ----------------------------------------------------------------------------------------------------------
# MECHANISM_ORG_ROLE
# ----------------------------------------------------------------------------------------------------------
ROLE_ORDER = ['operator', 'delivery_body', 'policy_owner', 'counterparty', 'settlement_agent', 'regulator',
              'market_platform', 'dispatch_platform']
roles = []  # (mechanism_id, org_id, role, platform_code, valid_from, valid_to, source_id, notes)


def add(spec, org, role, src, notes, platform='', vfrom='', vto=''):
    for m in ids(spec):
        roles.append((m, org, role, platform, vfrom, vto, src, notes))


FROM_OP = 'From KEY_DATA Market Operator.'
FROM_PL = 'From MARKET_INFO Market Platform.'
# --- operators carried over from KEY_DATA (sources chosen per service family)
add('1-6,10-11', 'ORG-0001', 'operator', 'SRC-0039', FROM_OP)
add('7-8,12-17', 'ORG-0001', 'operator', 'SRC-0032', FROM_OP)
add('9', 'ORG-0001', 'operator', 'SRC-0050', FROM_OP)
add('18,20,27,28', 'ORG-0001', 'operator', 'SRC-0031', FROM_OP)
add('19', 'ORG-0001', 'operator', 'SRC-0036', FROM_OP)
add('21', 'ORG-0001', 'operator', 'SRC-0035', FROM_OP)
add('22-23', 'ORG-0001', 'operator', 'SRC-0033', FROM_OP)
add('24-25', 'ORG-0001', 'operator', 'SRC-0034', FROM_OP)
add('26', 'ORG-0001', 'operator', 'SRC-0037', FROM_OP)
add('32', 'ORG-0008', 'operator', 'SRC-0023', FROM_OP + ' DESNZ tasked Ofgem with implementing the regime (R-009 fill).')
add('35-39', 'ORG-0013', 'operator', 'SRC-0010',
    FROM_OP + ' SRC-0010 is the UK Base future (MEC-0036); the other ICE product pages were not read.')
add('40-56', 'ORG-0012', 'operator', 'SRC-0009', FROM_OP)
add('57-61', 'ORG-0010', 'operator', 'SRC-0005', FROM_OP)
add('62-63', 'ORG-0011', 'operator', 'SRC-0007', FROM_OP)
add('64-65', 'ORG-0011', 'operator', 'SRC-0060', FROM_OP)
add('66', 'ORG-0011', 'operator', 'SRC-0008', FROM_OP)
add('67-74', 'ORG-0014', 'operator', 'SRC-0011', FROM_OP)
add('75-88', 'ORG-0016', 'operator', 'SRC-0012', FROM_OP)
add('89-93', 'ORG-0017', 'operator', 'SRC-0013', FROM_OP)
add('94-103', 'ORG-0018', 'operator', 'SRC-0014', FROM_OP)
add('104-109', 'ORG-0020', 'operator', 'SRC-0015', FROM_OP)
add('110-112', 'ORG-0021', 'operator', 'SRC-0016', FROM_OP)
# --- Capacity Market (MEC-0029/0030): NESO moves from "operator" to "delivery_body"
add('29-30', 'ORG-0001', 'delivery_body', 'SRC-0051',
    FROM_OP + ' Role corrected from operator. Reg 2 makes the Delivery Body the national system operator and reg 24 '
    'requires it to hold the auction; Energy Act 2013 s.27(6) (SRC-0052) defines the national system operator as '
    'the designated ISOP from 1 October 2024, which is NESO (SRC-0001).')
add('29-30', 'ORG-0007', 'policy_owner', 'SRC-0022',
    'New. DESNZ publishes the Capacity Market policy collection; the Secretary of State is an administrative party '
    '(SRC-0051, reg 2).')
add('29-30', 'ORG-0006', 'counterparty', 'SRC-0020', 'New. ESC is the Capacity Market Settlement Body (SRC-0020).')
add('29-30', 'ORG-0004', 'settlement_agent', 'SRC-0020', 'New. EMRS provides settlement services for ESC.')
add('29-30', 'ORG-0008', 'regulator', 'SRC-0051',
    'New. "The Authority" (Ofgem) is an administrative party under reg 2.')
# --- CfD (MEC-0031)
add('31', 'ORG-0001', 'delivery_body', 'SRC-0053',
    FROM_OP + ' Role corrected from operator. Reg 2 makes the delivery body the national system operator; Energy Act '
    '2013 s.8(3) (SRC-0052) defines it as the designated ISOP from 1 October 2024, which is NESO (SRC-0001). SRC-0021 '
    'still names National Grid ESO.')
add('31', 'ORG-0007', 'policy_owner', 'SRC-0021', 'New. DESNZ publishes the CfD policy collection.')
add('31', 'ORG-0005', 'counterparty', 'SRC-0021', 'New. LCCC is the CfD counterparty.')
add('31', 'ORG-0004', 'settlement_agent', 'SRC-0020', 'New. EMRS provides settlement services for LCCC.')
add('31', 'ORG-0008', 'regulator', 'SRC-0021', 'New. Ofgem hears certain CfD appeals (SRC-0021).')
# --- LDES cap and floor (MEC-0032)
add('32', 'ORG-0007', 'policy_owner', 'SRC-0023', 'New. DESNZ tasked Ofgem with implementing the regime.')
# --- NESO EAC / SMP platforms (from MARKET_INFO)
add('1-6,10-11', 'ORG-0001', 'market_platform', 'SRC-0039', FROM_PL, 'neso_eac')
add('1-6,10-11', 'ORG-0001', 'market_platform', 'SRC-0040', FROM_PL, 'neso_smp')
add('7', 'ORG-0001', 'market_platform', 'SRC-0046',
    FROM_PL + ' FLAG: unverified. MFR is a Grid Code requirement, not one of the services listed for EAC (SRC-0039); '
    'R-001 lists this row\'s MARKET_INFO values as a probable copy-down error (R-027).', 'neso_eac')
add('7', 'ORG-0001', 'market_platform', 'SRC-0040', FROM_PL + ' FLAG: unverified, as for the EAC row (R-027).',
    'neso_smp')
add('9', 'ORG-0001', 'market_platform', 'SRC-0046',
    FROM_PL + ' FLAG: unverified. Static FFR is not among the services listed for EAC (SRC-0039); its rules say only '
    'that NESO designates the auction platform (SRC-0050, PDF p.19) (R-027).', 'neso_eac')
add('9', 'ORG-0001', 'market_platform', 'SRC-0050',
    FROM_PL + ' Static FFR registration and pre-qualification are done on the SMP (SRC-0050, PDF p.21).', 'neso_smp')
# --- exchange platforms (from MARKET_INFO; the exchange's own trading system, not separately named)
add('57-60', 'ORG-0010', 'market_platform', 'SRC-0005', FROM_PL + ' The exchange\'s own trading system.')
add('62-63', 'ORG-0011', 'market_platform', 'SRC-0007', FROM_PL + ' The exchange\'s own trading system.')
add('64-65', 'ORG-0011', 'market_platform', 'SRC-0060',
    FROM_PL + ' Was "Nord Pool / EUPHEMIA": EUPHEMIA moves to MARKET_INFO Clearing Algorithm.')
# --- DSO platforms (new fills from the 2026-27 procurement statements)
add('67-74', 'ORG-0014', 'market_platform', 'SRC-0011',
    'New. NGED Market Gateway handles registration, qualification, contracting, asset registration and trading '
    '(SRC-0011, PDF p.6).', 'nged_market_gateway')
add('67-74', 'ORG-0036', 'market_platform', 'SRC-0011',
    'New. NGED has partnered with Piclo since 2024 as a second route into its markets (SRC-0011, PDF p.6).',
    'piclo_flex')
add('67-74', 'ORG-0038', 'dispatch_platform', 'SRC-0011',
    'New. The Flexible Power Portal is NGED\'s core operational system for dispatch, performance monitoring and '
    'settlement (SRC-0011, PDF p.6 and p.22).', 'flexible_power')
add('75-88', 'ORG-0036', 'market_platform', 'SRC-0012',
    'New. NPg uses Piclo Flex from qualification and asset registration through bidding (SRC-0012, PDF p.10, p.17, '
    'p.19).', 'piclo_flex')
add('75-81,85-88', 'ORG-0036', 'dispatch_platform', 'SRC-0012',
    'New. NPg uses Piclo Flex for dispatch and settlement (SRC-0012, PDF p.10).', 'piclo_flex')
add('89-93', 'ORG-0037', 'market_platform', 'SRC-0013',
    'New. SPEN moved to ElectronConnect from April 2026; all bidding takes place there (SRC-0013, PDF p.9, p.12). Its '
    'Piclo contract ended at the end of Q1 2026 (PDF p.10).', 'electronconnect', '2026-04-01')
add('89-93', 'ORG-0037', 'dispatch_platform', 'SRC-0013',
    'New. Electron supports SPEN providers through to dispatch and settlement (SRC-0013, PDF p.9).',
    'electronconnect', '2026-04-01')
add('94-103', 'ORG-0037', 'market_platform', 'SRC-0014',
    'New. ElectronConnect has been SPENW\'s core market platform since March 2024 (SRC-0014, PDF p.20).',
    'electronconnect')
add('94-103', 'ORG-0037', 'dispatch_platform', 'SRC-0014',
    'New. Dispatch is normally by API from ElectronConnect, by email where there is no API; some services are '
    'dispatched through ANM instead (SRC-0014, PDF p.7, p.20).', 'electronconnect')
add('104-109', 'ORG-0037', 'market_platform', 'SRC-0015',
    'New. SSEN uses ElectronConnect for qualification, contracting and bidding (SRC-0015, PDF p.14-15, p.17).',
    'electronconnect')
add('104-109', 'ORG-0038', 'dispatch_platform', 'SRC-0015',
    'New. SSEN delivery and settlement run on Flexible Power (SRC-0015, PDF p.14, p.26; SRC-0056).', 'flexible_power')
add('110-112', 'ORG-0010', 'market_platform', 'SRC-0016',
    'New. UKPN runs its long-term and day-ahead tenders on EPEX SPOT Localflex (SRC-0016, PDF p.3, p.7, p.12).',
    'epex_localflex')

roles.sort(key=lambda r: (r[0], ROLE_ORDER.index(r[2]), r[3], r[1]))
role_rows = [(f'MOR-{i:06d}',) + r for i, r in enumerate(roles, 1)]

# ----------------------------------------------------------------------------------------------------------
# VALUE_MAPPING (same columns as R-009) and COLUMN_ACTIONS
# ----------------------------------------------------------------------------------------------------------
MOR = 'MECHANISM_ORG_ROLE'
EAC = 'SRC-0046 PDF p.8'
M = [
    # ---- KEY_DATA Market Operator (already ORG IDs) -> operator / delivery_body rows
    ('KEY_DATA', 'Market Operator', 'ORG-0001', '1-28', MOR, 'org_id (role operator)', 'ORG-0001', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0001', '29-31', MOR, 'org_id (role delivery_body)', 'ORG-0001', 'flag',
     'Resolves the R-009 flag: NESO is the EMR delivery body for the CM and CfD, set by legislation (SRC-0051, '
     'SRC-0053, SRC-0052). Other roles for these schemes are new rows (see MECHANISM_ORG_ROLE).'),
    ('KEY_DATA', 'Market Operator', 'ORG-0008', '32', MOR, 'org_id (role operator)', 'ORG-0008', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0013', '35-39', MOR, 'org_id (role operator)', 'ORG-0013', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0012', '40-56', MOR, 'org_id (role operator)', 'ORG-0012', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0010', '57-61', MOR, 'org_id (role operator)', 'ORG-0010', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0011', '62-66', MOR, 'org_id (role operator)', 'ORG-0011', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0014', '67-74', MOR, 'org_id (role operator)', 'ORG-0014', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0016', '75-88', MOR, 'org_id (role operator)', 'ORG-0016', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0017', '89-93', MOR, 'org_id (role operator)', 'ORG-0017', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0018', '94-103', MOR, 'org_id (role operator)', 'ORG-0018', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0020', '104-109', MOR, 'org_id (role operator)', 'ORG-0020', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ORG-0021', '110-112', MOR, 'org_id (role operator)', 'ORG-0021', 'clean', ''),
    ('KEY_DATA', 'Market Operator', '', '33-34', MOR, '(no row)', '', 'unmapped',
     'OTC deals have no operator (R-009); no role row.'),
    # ---- MARKET_INFO Market Platform -> platform rows (column then dropped)
    ('MARKET_INFO', 'Market Platform', 'NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP)',
     '1-6,10-11', MOR, 'org_id / platform_code (role market_platform)', 'ORG-0001 neso_eac; ORG-0001 neso_smp', 'clean',
     'Two rows per mechanism. EAC runs the DC, DM, DR and QR auctions (SRC-0039); SMP is the registration platform '
     '(SRC-0040).'),
    ('MARKET_INFO', 'Market Platform', 'NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP)',
     '7', MOR, 'org_id / platform_code (role market_platform)', 'ORG-0001 neso_eac; ORG-0001 neso_smp', 'flag',
     'Carried over but unverified: MFR is a Grid Code requirement, not an EAC product; probable copy-down error '
     '(R-001 data-quality list; R-027).'),
    ('MARKET_INFO', 'Market Platform', 'NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP)',
     '9', MOR, 'org_id / platform_code (role market_platform)', 'ORG-0001 neso_eac; ORG-0001 neso_smp', 'flag',
     'SMP confirmed for Static FFR (SRC-0050, PDF p.21). EAC not confirmed: SRC-0039 does not list Static FFR and its '
     'rules name only a "Designated Auction Platform" (R-027).'),
    ('MARKET_INFO', 'Market Platform', 'EPEX Spot', '57-60', MOR, 'org_id (role market_platform)', 'ORG-0010', 'clean',
     'platform_code blank: the exchange\'s own trading system.'),
    ('MARKET_INFO', 'Market Platform', 'Nord Pool', '62-63', MOR, 'org_id (role market_platform)', 'ORG-0011', 'clean',
     'platform_code blank.'),
    ('MARKET_INFO', 'Market Platform', 'Nord Pool / EUPHEMIA', '64-65', MOR, 'org_id (role market_platform)',
     'ORG-0011', 'clean', 'The "EUPHEMIA" part goes to the new Clearing Algorithm column (next row).'),
    ('MARKET_INFO', 'Market Platform', 'Nord Pool / EUPHEMIA', '64-65', 'LK_CLEARING_ALGORITHM', 'Clearing Algorithm',
     'euphemia', 'flag',
     'R-009 D4: EUPHEMIA is an algorithm attribute. No primary source found that the SEM-GB auctions still clear with '
     'EUPHEMIA (SRC-0060 names no algorithm; SRC-0054 does not mention GB). Carried over; open point R-026.'),
    ('MARKET_INFO', 'Market Platform', '', '67-74', MOR, 'org_id / platform_code', 'ORG-0014 nged_market_gateway; '
     'ORG-0036 piclo_flex (market_platform); ORG-0038 flexible_power (dispatch_platform)', 'fill', 'SRC-0011 PDF p.6, p.22.'),
    ('MARKET_INFO', 'Market Platform', '', '75-88', MOR, 'org_id / platform_code',
     'ORG-0036 piclo_flex (market_platform; dispatch_platform except MEC-0082..0084)', 'fill',
     'SRC-0012 PDF p.10: outage-support services (MEC-0082..0084) are dispatched by telephone, so no dispatch row.'),
    ('MARKET_INFO', 'Market Platform', '', '89-93', MOR, 'org_id / platform_code',
     'ORG-0037 electronconnect (market_platform; dispatch_platform), valid_from 2026-04-01', 'fill',
     'SRC-0013 PDF p.9, p.10, p.12.'),
    ('MARKET_INFO', 'Market Platform', '', '94-103', MOR, 'org_id / platform_code',
     'ORG-0037 electronconnect (market_platform; dispatch_platform)', 'fill', 'SRC-0014 PDF p.7, p.20.'),
    ('MARKET_INFO', 'Market Platform', '', '104-109', MOR, 'org_id / platform_code',
     'ORG-0037 electronconnect (market_platform); ORG-0038 flexible_power (dispatch_platform)', 'fill',
     'SRC-0015 PDF p.14, p.26; SRC-0056.'),
    ('MARKET_INFO', 'Market Platform', '', '110-112', MOR, 'org_id / platform_code',
     'ORG-0010 epex_localflex (market_platform)', 'fill', 'SRC-0016 PDF p.3, p.7, p.12.'),
    # ---- Pricing Structure
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '1-6,10-11', 'LK_PRICING_RULE', 'Pricing Structure',
     'pay_as_clear', 'clean', 'Uniform clearing price (SRC-0046 PDF p.8; SRC-0047 para 12.2; SRC-0048 para 13.2).'),
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '7', 'LK_PRICING_RULE', 'Pricing Structure', 'pay_as_clear',
     'flag', 'Probable copy-down from the EAC rows (R-027).'),
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '9', 'LK_PRICING_RULE', 'Pricing Structure', 'pay_as_clear',
     'clean', 'One Market Clearing Price per EFA block (SRC-0050 para 9.1).'),
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '57-60,62-65', 'LK_PRICING_RULE', 'Pricing Structure',
     'pay_as_clear', 'clean', 'Exchange auctions give one price per period (LK_MECHANISM_CLASS exchange_auction).'),
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '61', 'LK_PRICING_RULE', 'Pricing Structure', 'pay_as_bid',
     'flag', 'Correction. MEC-0061 is continuous trading: each trade takes the price of the order already in the book '
     '(SRC-0055 PDF p.15), as the approved exchange_continuous definition says. If rejected, clear the cell (R-005).'),
    # ---- Auction Type
    ('MARKET_INFO', 'Auction Type', 'Closed Double Sided', '1-6,10-11', 'LK_AUCTION_TYPE', 'Auction Type',
     'sealed_double_sided', 'clean', EAC + ': "Closed double-sided auction".'),
    ('MARKET_INFO', 'Auction Type', 'Closed Double Sided', '7', 'LK_AUCTION_TYPE', 'Auction Type',
     'sealed_double_sided', 'flag', 'Probable copy-down from the EAC rows (R-027).'),
    ('MARKET_INFO', 'Auction Type', 'Closed Double Sided', '9', 'LK_AUCTION_TYPE', 'Auction Type',
     'sealed_double_sided', 'clean', 'NESO buy order and provider sell orders, cleared together (SRC-0050 paras 7-9).'),
    ('MARKET_INFO', 'Auction Type', 'Closed Double Sided', '59-60,62-63', 'LK_AUCTION_TYPE', 'Auction Type',
     'sealed_double_sided', 'clean', 'Carried over; exchange day-ahead auctions take buy and sell orders.'),
    # ---- Market Structure
    ('MARKET_INFO', 'Market Structure', 'One-to-Many', '1-6,9-11', 'LK_MARKET_STRUCTURE', 'Market Structure',
     'single_buyer', 'clean', 'NESO is the only buyer (SRC-0046 PDF p.4 glossary).'),
    ('MARKET_INFO', 'Market Structure', 'One-to-Many', '7', 'LK_MARKET_STRUCTURE', 'Market Structure', 'single_buyer',
     'flag', 'Probable copy-down from the EAC rows (R-027).'),
    ('MARKET_INFO', 'Market Structure', 'Many-to-Many', '57-60,62-65', 'LK_MARKET_STRUCTURE', 'Market Structure',
     'multilateral', 'clean', ''),
    # ---- Market Objective
    ('MARKET_INFO', 'Market Objective', 'Maximise Social Welfare', '1-6,10-11', 'LK_MARKET_OBJECTIVE',
     'Market Objective', 'maximise_social_welfare', 'clean', EAC + '; SRC-0047 para 9.1.1; SRC-0048 para 10.1.1.'),
    ('MARKET_INFO', 'Market Objective', 'Maximise Social Welfare', '7', 'LK_MARKET_OBJECTIVE', 'Market Objective',
     'maximise_social_welfare', 'flag', 'Probable copy-down from the EAC rows (R-027).'),
    ('MARKET_INFO', 'Market Objective', 'Maximise Social Welfare', '9', 'LK_MARKET_OBJECTIVE', 'Market Objective',
     'maximise_social_welfare', 'clean', 'Total auction surplus is maximised (SRC-0050 para 9.2.1).'),
    ('MARKET_INFO', 'Market Objective', 'Maximise Social Welfare', '62-64', 'LK_MARKET_OBJECTIVE', 'Market Objective',
     'maximise_social_welfare', 'clean', 'Carried over; not re-verified for the Nord Pool auctions in this run (R-026).'),
    ('MARKET_INFO', 'Market Objective', 'Nor', '65', 'LK_MARKET_OBJECTIVE', 'Market Objective', '', 'unmapped',
     'Truncated value. Clear the cell (old value kept in the change log); R-026 fills it from the SEM-GB rules.'),
    # ---- Dispatcher
    ('DISPATCH', 'Dispatcher', 'Self', '1-7,9', 'LK_DISPATCHER', 'Dispatcher', 'self', 'clean',
     'Automatic response to frequency, no instruction (Dispatch Type = Auto).'),
    ('DISPATCH', 'Dispatcher', 'Self', '33,57-66', 'LK_DISPATCHER', 'Dispatcher', 'self', 'clean',
     'Participants dispatch themselves to their traded positions (SRC-0059).'),
    ('DISPATCH', 'Dispatcher', 'NESO', '10-11', 'LK_DISPATCHER', 'Dispatcher', 'operator', 'clean',
     'NESO (the operator, ORG-0001) issues BOAs or Instructions (SRC-0049 PDF p.5, p.13). The org is read from '
     'MECHANISM_ORG_ROLE, so the column holds no ORG ID.'),
    ('DISPATCH', 'Dispatcher', 'N/A', '34-56', 'LK_DISPATCHER', 'Dispatcher', 'not_applicable', 'clean',
     'MEC-0035..0039: ICE UK Base futures are physically delivered via ECVNs (SRC-0010); revisit in R-024.'),
    # ---- Aggregation
    ('PARTICIPANTS', 'Aggregation', 'GSP', '1-6', 'LK_AGGREGATION_LEVEL', 'Aggregation', 'gsp_group', 'flag',
     'The rules say GSP Group, not GSP; NESO may tighten this to one grid supply point (SRC-0047 PDF p.32).'),
    ('PARTICIPANTS', 'Aggregation', 'GSP', '10-11', 'LK_AGGREGATION_LEVEL', 'Aggregation', 'gsp_group', 'flag',
     'As above (SRC-0048 PDF p.29).'),
    ('PARTICIPANTS', 'Aggregation', 'National', '9', 'LK_AGGREGATION_LEVEL', 'Aggregation', 'national', 'flag',
     'Medium confidence: the Static FFR rules define a unit as a collection of assets and set no location limit '
     '(SRC-0050 PDF p.22), unlike the Response and QR rules.'),
]
COVER = {
    'KEY_DATA': ['Market Operator'],
    'MARKET_INFO': ['Market Platform', 'Pricing Structure', 'Auction Type', 'Market Structure', 'Market Objective'],
    'DISPATCH': ['Dispatcher'],
    'PARTICIPANTS': ['Aggregation'],
}
COLUMN_ACTIONS = [
    ('KEY_DATA.csv', 'Market Operator', 'drop',
     'After MECHANISM_ORG_ROLE is applied. The operator is then the role row with role = operator (SQLite view, R-018).',
     MOR, 'D3'),
    ('MARKET_INFO.csv', 'Market Platform', 'drop', 'After the platform rows are added to MECHANISM_ORG_ROLE.', MOR, 'D3'),
    ('MARKET_INFO.csv', 'Pricing Structure', 'convert in place', 'Text to code per VALUE_MAPPING.', 'LK_PRICING_RULE',
     'D6'),
    ('MARKET_INFO.csv', 'Auction Type', 'convert in place', 'Text to code.', 'LK_AUCTION_TYPE', 'D6'),
    ('MARKET_INFO.csv', 'Market Structure', 'convert in place', 'Text to code.', 'LK_MARKET_STRUCTURE', 'D7'),
    ('MARKET_INFO.csv', 'Market Objective', 'convert in place', 'Text to code; MEC-0065 cleared.',
     'LK_MARKET_OBJECTIVE', 'D8'),
    ('MARKET_INFO.csv', 'Clearing Algorithm', 'add', 'New column after Market Objective; MEC-0064..0065 = euphemia.',
     'LK_CLEARING_ALGORITHM', 'D9'),
    ('DISPATCH.csv', 'Dispatcher', 'convert in place', 'Text to code; no ORG IDs in this column.', 'LK_DISPATCHER',
     'D10'),
    ('PARTICIPANTS.csv', 'Aggregation', 'convert in place', 'Text to code.', 'LK_AGGREGATION_LEVEL', 'D11'),
    ('DISPATCH.csv', 'Dispatch Type', 'no change', 'Waits for Phase 3 Change 10.', '', ''),
]
UPDATES = [
    ('SOURCES.csv', 'SRC-0002', 'notes', '(append)',
     'Also read 2026-11-23 for R-020: 09914060 (Chaddenwych Services Limited), 14266869 (Piclo Ltd), 06219884 (ICE '
     'Clear Europe Limited) and the search results for "piclo" and "open utility" (Open Utility Ltd 08384033).',
     'Records the extra Companies House pages read for ORG-0036 and ORG-0037.'),
    ('ORGANISATIONS.csv', 'ORG-0014', 'notes', '(append)',
     'Owns the Flexible Power trademark (SRC-0057); runs the Market Gateway platform (SRC-0011).',
     'Links NGED to LK_PLATFORM nged_market_gateway and to ORG-0038.'),
]

# ----------------------------------------------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------------------------------------------
problems = []
kd = load('KEY_DATA')
mech_ids = {r['ID'] for r in kd}
org_ids = {r['org_id'] for r in load('ORGANISATIONS')} | {o[0] for o in ORGS}
src_ids = {r['source_id'] for r in load('SOURCES')} | {s[0] for s in SOURCES}
org_types = {r['code'] for r in load('LK_ORG_TYPE')} | {t[0] for t in ORG_TYPES}
lk_codes = {name: {row[0] for row in rows} for name, (_, rows) in LK.items()}
platform_op = {row[0]: row[4] for row in LK['LK_PLATFORM'][1]}
snake = re.compile(r'^[a-z][a-z0-9_]*$')

# numbering
for prefix, rows, first in (('SRC', SOURCES, 46), ('ORG', ORGS, 36)):
    for i, row in enumerate(rows):
        if row[0] != f'{prefix}-{first + i:04d}':
            problems.append(('numbering', row[0]))
# lookups
for name, (hdr, rows) in LK.items():
    for row in rows:
        if not snake.match(row[0]):
            problems.append(('code not snake_case', name, row[0]))
        if row[3] not in src_ids:
            problems.append(('lookup source', name, row[0], row[3]))
    if len({r[0] for r in rows}) != len(rows):
        problems.append(('duplicate code', name))
for code, op in platform_op.items():
    if op not in org_ids:
        problems.append(('platform operator', code, op))
for o in ORGS:
    if o[3] not in org_types or o[10] not in src_ids:
        problems.append(('org', o[0]))
for t in ORG_TYPES:
    if t[3] not in src_ids:
        problems.append(('org type source', t[0]))
for s in SOURCES:
    if s[2].startswith('ORG-') and s[2] not in org_ids:
        problems.append(('source publisher', s[0], s[2]))
# role rows
seen = set()
for r in role_rows:
    rid, m, org, role, plat, vf, vt, src, notes = r
    if m not in mech_ids: problems.append(('role mech', rid, m))
    if org not in org_ids: problems.append(('role org', rid, org))
    if role not in lk_codes['LK_ORG_ROLE']: problems.append(('role code', rid, role))
    if src not in src_ids: problems.append(('role source', rid, src))
    if plat:
        if plat not in lk_codes['LK_PLATFORM']: problems.append(('role platform', rid, plat))
        elif platform_op[plat] != org: problems.append(('platform/org mismatch', rid, plat, org))
        if role not in ('market_platform', 'dispatch_platform'): problems.append(('platform on non-platform role', rid))
    key = (m, org, role, plat)
    if key in seen: problems.append(('duplicate role row', key))
    seen.add(key)
# every operator in KEY_DATA has exactly one matching operator/delivery_body row
for row in kd:
    op = row['Market Operator']
    got = [r for r in role_rows if r[1] == row['ID'] and r[3] in ('operator', 'delivery_body') and r[2] == op]
    if op and len(got) != 1:
        problems.append(('operator carry-over', row['ID'], op, len(got)))
    if not op and any(r[1] == row['ID'] and r[3] == 'operator' for r in role_rows):
        problems.append(('operator on blank', row['ID']))
# value coverage
data = {f: load(f) for f in COVER}
for f, cols in COVER.items():
    for col in cols:
        actual = defaultdict(set)
        for r in data[f]:
            actual[r[col]].add(r['ID'])
        mapped = defaultdict(set)
        for mf, mc, val, spec, *_ in M:
            if mf == f and mc == col:
                mapped[val].update(ids(spec))
        for val, idset in actual.items():
            if val == '':
                if not mapped[val] <= idset:
                    problems.append((f, col, 'blank fill outside blanks', sorted(mapped[val] - idset)))
                continue
            if mapped.get(val) != idset:
                problems.append((f, col, val, sorted(idset ^ mapped.get(val, set()))))
        for val in mapped:
            if val not in actual:
                problems.append((f, col, val, 'value not in data'))
# codes in the mapping resolve to their lookup
for mf, mc, val, spec, tt, tc, code, st, note in M:
    if tt.startswith('LK_') and code and code not in lk_codes.get(tt, ()):
        problems.append(('mapping code', tt, code))
# every new source is cited somewhere
cited = Counter()
blob = ' '.join(str(x) for x in (SOURCES + ORGS + ORG_TYPES + role_rows + M + UPDATES))
for name, (_, rows) in LK.items():
    blob += ' ' + ' '.join(' '.join(r) for r in rows)
for s in SOURCES:
    uses = [r for r in role_rows if r[7] == s[0]] + [r for n, (_, rows) in LK.items() for r in rows if r[3] == s[0]] \
        + [o for o in ORGS if o[10] == s[0]] + [t for t in ORG_TYPES if t[3] == s[0]]
    if not uses and blob.count(s[0]) <= 1:
        problems.append(('source not cited', s[0]))
assert not problems, problems

# ----------------------------------------------------------------------------------------------------------
# Write
# ----------------------------------------------------------------------------------------------------------
write('SOURCES_additions', ['source_id', 'title', 'publisher', 'url', 'source_type', 'doc_type', 'version_or_date',
                            'accessed_date', 'archive_url', 'notes', 'reuse_terms'], SOURCES)
write('ORGANISATIONS_additions', ['org_id', 'name', 'short_name', 'org_type', 'parent_org_id', 'url', 'valid_from',
                                  'valid_to', 'predecessor_org_id', 'registry_id', 'source_id', 'notes'], ORGS)
write('LK_ORG_TYPE_additions', ['code', 'label', 'definition', 'source_id'], ORG_TYPES)
for name, (hdr, rows) in LK.items():
    write(name, hdr, rows)
write('MECHANISM_ORG_ROLE', ['role_id', 'mechanism_id', 'org_id', 'role', 'platform_code', 'valid_from', 'valid_to',
                             'source_id', 'notes'], role_rows)
write('VALUE_MAPPING', ['file', 'column', 'current_value', 'mechanism_ids', 'target_table', 'target_column',
                        'proposed_code', 'mapping_status', 'note'],
      [[f + '.csv', c, v if v else '(blank)', rng(ids(s)), tt, tc, code, st, note]
       for f, c, v, s, tt, tc, code, st, note in M])
write('COLUMN_ACTIONS', ['file', 'column', 'action', 'detail', 'lookup_or_table', 'decision'], COLUMN_ACTIONS)
write('EXISTING_ROW_UPDATES', ['file', 'key', 'column', 'current_value', 'proposed_value', 'reason'], UPDATES)

print('sources', len(SOURCES), 'orgs', len(ORGS), 'role rows', len(role_rows))
print('roles', Counter(r[3] for r in role_rows))
print('lookups', {k: len(v[1]) for k, v in LK.items()})
print('mapping rows', len(M), Counter(m[7] for m in M))
