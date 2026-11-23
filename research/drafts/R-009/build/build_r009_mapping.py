"""Build research/drafts/R-009/VALUE_MAPPING.csv and check it covers every current value in CSV/.

Each mapping row: file, column, current_value, mechanism_ids, target_table, target_column, proposed_code,
mapping_status (clean | flag | fill | hold | unmapped | deferred), note.
Run: python -I build_r009_mapping.py <repo_root>
"""
import csv, io, os, sys

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'research', 'drafts', 'R-009')


def load(name):
    with open(os.path.join(ROOT, 'CSV', name + '.csv'), encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def ids(spec):
    """'1-9,22' -> ['MEC-0001', ..., 'MEC-0009', 'MEC-0022']"""
    out = []
    for part in spec.split(','):
        a, _, b = part.partition('-')
        for n in range(int(a), int(b or a) + 1):
            out.append(f'MEC-{n:04d}')
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


LKC, LKG, ORG = 'LK_MECHANISM_CLASS', 'LK_CATEGORY', 'ORGANISATIONS'
SRC_TRADING = 'https://www.neso.energy/industry-information/balancing-services/trading'
SRC_DFS = 'https://www.neso.energy/industry-information/balancing-services/demand-flexibility-service-dfs'
# (file, column, current_value, id spec, target_table, target_column, code, status, note)
M = [
    # ---- KEY_DATA Market Type -> mechanism class + category
    ('KEY_DATA', 'Market Type', 'Frequency Response', '1-9', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Frequency Response', '1-9', LKG, 'Category', 'frequency_response', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Reserve', '10-17', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Reserve', '10-17', LKG, 'Category', 'reserve', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Thermal', '18-20', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Thermal', '18-20', LKG, 'Category', 'thermal_constraint', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Voltage', '21', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Voltage', '21', LKG, 'Category', 'voltage', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Voltage', '22-23', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Voltage', '22-23', LKG, 'Category', 'stability', 'flag',
     'Stability Markets buy inertia and short-circuit level, not voltage support (SRC-0033).'),
    ('KEY_DATA', 'Market Type', 'Restoration', '24-25', LKC, 'Mechanism Class', 'so_ancillary_service', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Restoration', '24-25', LKG, 'Category', 'restoration', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '26', LKC, 'Mechanism Class', 'balancing_mechanism', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '26', LKG, 'Category', 'energy', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '27', LKC, 'Mechanism Class', 'so_ancillary_service', 'flag',
     'NESO Trading is forward bilateral trading under Grid Trade Master Agreements, listed as a separate NESO balancing service, not part of the BM: ' + SRC_TRADING),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '27', LKG, 'Category', 'energy', 'flag', 'See class note.'),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '28', LKC, 'Mechanism Class', 'so_ancillary_service', 'flag',
     'DFS is a separate NESO balancing service (an in-merit margin tool), not a BM action: ' + SRC_DFS),
    ('KEY_DATA', 'Market Type', 'Balancing Mechanism', '28', LKG, 'Category', 'energy', 'flag',
     'NESO says DFS replaces the Local Constraint Market from 7 Oct 2026 (SRC-0036), so thermal_constraint may also apply.'),
    ('KEY_DATA', 'Market Type', 'Forwards', '29-30', LKC, 'Mechanism Class', 'capacity_mechanism', 'flag',
     'Re-typed: the Capacity Market is a capacity payment scheme, not a forward contract (SRC-0022).'),
    ('KEY_DATA', 'Market Type', 'Forwards', '29-30', LKG, 'Category', 'capacity_adequacy', 'flag', 'SRC-0022.'),
    ('KEY_DATA', 'Market Type', 'Forwards', '31', LKC, 'Mechanism Class', 'revenue_support_scheme', 'flag',
     'Re-typed: CfD is a government revenue support scheme (SRC-0021).'),
    ('KEY_DATA', 'Market Type', 'Forwards', '31', LKG, 'Category', 'investment_support', 'flag', 'SRC-0021.'),
    ('KEY_DATA', 'Market Type', 'Forwards', '32', LKC, 'Mechanism Class', 'revenue_support_scheme', 'flag',
     'Re-typed: LDES cap and floor is a regulated revenue support regime (SRC-0023).'),
    ('KEY_DATA', 'Market Type', 'Forwards', '32', LKG, 'Category', 'investment_support', 'flag', 'SRC-0023.'),
    ('KEY_DATA', 'Market Type', 'Forwards', '33-34', LKC, 'Mechanism Class', 'otc_bilateral', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Forwards', '33-34', LKG, 'Category', 'energy', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Futures', '35-56', LKC, 'Mechanism Class', 'exchange_derivative', 'clean',
     'MEC-0035 and MEC-0037 are options; the class covers futures and options.'),
    ('KEY_DATA', 'Market Type', 'Futures', '35-56', LKG, 'Category', 'energy', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Wholesale Spot', '57-60,62-65', LKC, 'Mechanism Class', 'exchange_auction', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Wholesale Spot', '57-60,62-65', LKG, 'Category', 'energy', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Wholesale Spot', '61,66', LKC, 'Mechanism Class', 'exchange_continuous', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'Wholesale Spot', '61,66', LKG, 'Category', 'energy', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'DSO Flex Market', '67-112', LKC, 'Mechanism Class', 'dso_flexibility', 'clean', ''),
    ('KEY_DATA', 'Market Type', 'DSO Flex Market', '67-68,70-112', LKG, 'Category', 'thermal_constraint', 'flag',
     'Medium confidence: DNO statements describe reinforcement deferral and outage cover, i.e. thermal capacity needs.'),
    ('KEY_DATA', 'Market Type', 'DSO Flex Market', '69', LKG, 'Category', 'thermal_constraint', 'flag',
     'Legacy Restore is about restoring supplies after a distribution fault; `restoration` (system-level) is the alternative.'),
    # ---- KEY_DATA Market Operator -> ORGANISATIONS
    ('KEY_DATA', 'Market Operator', 'NESO', '1-28', ORG, 'Market Operator', 'ORG-0001', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'NESO', '29-31', ORG, 'Market Operator', 'ORG-0001', 'flag',
     'NESO is the EMR delivery body, not the operator. Full role set (DESNZ policy owner, LCCC/ESC counterparty, EMRS settlement) to go in MECHANISM_ORG_ROLE (R-020).'),
    ('KEY_DATA', 'Market Operator', 'EEX', '40-56', ORG, 'Market Operator', 'ORG-0012', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'NPg', '75-88', ORG, 'Market Operator', 'ORG-0016', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'SPENW', '94-103', ORG, 'Market Operator', 'ORG-0018', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'NGED', '67-74', ORG, 'Market Operator', 'ORG-0014', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'SSEN', '104-109', ORG, 'Market Operator', 'ORG-0020', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'ICE', '35-39', ORG, 'Market Operator', 'ORG-0013', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'EPEX Spot', '57-61', ORG, 'Market Operator', 'ORG-0010', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'Nord Pool', '62-66', ORG, 'Market Operator', 'ORG-0011', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'SPEN', '89-93', ORG, 'Market Operator', 'ORG-0017', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'UKPN', '110-112', ORG, 'Market Operator', 'ORG-0021', 'clean', ''),
    ('KEY_DATA', 'Market Operator', 'Brokers & Bilaterals', '33-34', ORG, 'Market Operator', '', 'unmapped',
     'Not an organisation. OTC deals have no operator; the otc_bilateral class records how they trade. Leave blank.'),
    ('KEY_DATA', 'Market Operator', '', '32', ORG, 'Market Operator', 'ORG-0008', 'fill',
     'New value for a blank cell: DESNZ tasked Ofgem with implementing the LDES cap and floor regime (SRC-0023).'),
    # ---- Status
    ('KEY_DATA', 'Status', 'Live', '1-17,19,24-29,31-112', 'LK_STATUS', 'Status', 'live', 'clean',
     'Doubtful statuses are passed to R-006 (e.g. MEC-0019: NESO says DFS replaces LCM from 7 Oct 2026, SRC-0036).'),
    ('KEY_DATA', 'Status', 'Planned', '20-23', 'LK_STATUS', 'Status', 'planned', 'clean',
     'R-006: NESO launched its first long-term (Y-4) stability tender in 2025 (SRC-0033), so MEC-0023 may no longer be planned.'),
    ('KEY_DATA', 'Status', '', '18,30', 'LK_STATUS', 'Status', '', 'unmapped', 'Blank today; R-006.'),
    # ---- Commodity
    ('KEY_DATA', 'Commodity', 'Active Power', '1-9,12-20,24-28,33,57-112', 'LK_COMMODITY', 'Commodity', 'active_power', 'clean', ''),
    ('KEY_DATA', 'Commodity', 'Active Power Capacity', '10-11', 'LK_COMMODITY', 'Commodity', 'active_power', 'flag',
     'Under the recommended option the energy/availability split is carried by MARKET_INFO Availability Payment (yes for both rows).'),
    ('KEY_DATA', 'Commodity', 'Reactive Power', '21', 'LK_COMMODITY', 'Commodity', 'reactive_power', 'clean', ''),
    ('KEY_DATA', 'Commodity', 'Reactive Power', '22-23', 'LK_COMMODITY', 'Commodity', 'stability', 'flag',
     'Stability Markets buy inertia and short-circuit level (SRC-0033).'),
    ('KEY_DATA', 'Commodity', 'Financial Futures', '35-39', 'LK_COMMODITY', 'Commodity', 'active_power', 'flag',
     '"Financial" describes settlement, not commodity. ICE UK Base futures are physically delivered via ECVNs (SRC-0010); record settlement in LK_SETTLEMENT_TYPE (R-020).'),
    ('KEY_DATA', 'Commodity', 'Financial Futures', '40-56', 'LK_COMMODITY', 'Commodity', 'active_power', 'flag',
     'EEX lists GB Power Futures as "Cash settlement / Physical fulfilment" (SRC-0009); settlement type to LK_SETTLEMENT_TYPE (R-020).'),
    ('KEY_DATA', 'Commodity', 'Financial Forwards', '34', 'LK_COMMODITY', 'Commodity', 'active_power', 'flag',
     'Ofgem: OTC Financial trades have no physical delivery and hedge spot prices (SRC-0041); settlement type to LK_SETTLEMENT_TYPE (R-020).'),
    ('KEY_DATA', 'Commodity', '', '29-30', 'LK_COMMODITY', 'Commodity', 'firm_capacity', 'fill',
     'New value: the Capacity Market pays for reliable capacity (SRC-0022).'),
    ('KEY_DATA', 'Commodity', '', '31', 'LK_COMMODITY', 'Commodity', 'active_power', 'fill',
     'New value: CfD generators are paid per unit of electricity produced (SRC-0021).'),
    ('KEY_DATA', 'Commodity', '', '32', 'LK_COMMODITY', 'Commodity', '', 'unmapped', 'LDES cap and floor: left for R-002.'),
    # ---- Direction
    ('KEY_DATA', 'Direction', 'Up', '2,4,6,9,10,12,14', 'LK_DIRECTION', 'Direction', 'up', 'clean', ''),
    ('KEY_DATA', 'Direction', 'Down', '1,3,5,11,13,15,18', 'LK_DIRECTION', 'Direction', 'down', 'clean', ''),
    ('KEY_DATA', 'Direction', 'Up/Down', '7-8', 'LK_DIRECTION', 'Direction', 'both', 'clean', ''),
    ('KEY_DATA', 'Direction', 'Up/Down', '67-112', 'LK_DIRECTION', 'Direction', 'both', 'flag',
     'Most DSO sub-markets are demand turn-down / generation turn-up only (up); R-013 checks each row.'),
    ('KEY_DATA', 'Direction', 'Flat', '57-66', 'LK_DIRECTION', 'Direction', 'both', 'flag',
     'Decision D6: participants can buy or sell, so both (recommended); alternative not_applicable.'),
    ('KEY_DATA', 'Direction', 'N/A', '34,40-56', 'LK_DIRECTION', 'Direction', 'not_applicable', 'clean', ''),
    ('KEY_DATA', 'Direction', 'N/A', '35-39', 'LK_DIRECTION', 'Direction', 'not_applicable', 'flag',
     'ICE UK electricity futures are physically delivered (SRC-0010); both may fit better. R-005.'),
    ('KEY_DATA', 'Direction', '', '16-17,19-33', 'LK_DIRECTION', 'Direction', '', 'unmapped', 'Blank today; R-005.'),
    # ---- Contract Length Band
    ('KEY_DATA', 'Contract Length Band', 'Month < x <= Year', '75,77,78,80,81,93,95,97,99,101', 'LK_CONTRACT_LENGTH_BAND', 'Contract Length Band', 'month_to_year', 'clean', ''),
    ('KEY_DATA', 'Contract Length Band', 'Week < x <= Month', '79,82,89,92,94,96,98,100', 'LK_CONTRACT_LENGTH_BAND', 'Contract Length Band', 'week_to_month', 'clean', ''),
    ('KEY_DATA', 'Contract Length Band', 'Day < x <= Week', '90', 'LK_CONTRACT_LENGTH_BAND', 'Contract Length Band', 'day_to_week', 'clean', ''),
    ('KEY_DATA', 'Contract Length Band', 'Less Than or Equal to a Day', '91', 'LK_CONTRACT_LENGTH_BAND', 'Contract Length Band', 'le_day', 'clean', ''),
    # ---- MARKET_INFO
    ('MARKET_INFO', 'Market Platform', 'NESO Enduring Auction Capability (EAC) & Single Market Platform (SMP)', '1-7,9-11', ORG, 'platform role', 'ORG-0001', 'flag',
     'EAC and SMP are NESO systems, not organisations (SRC-0039, SRC-0040); NESO spells it "Single Markets Platform". System names are lost unless decision D4 adds a platform table.'),
    ('MARKET_INFO', 'Market Platform', 'EPEX Spot', '57-60', ORG, 'platform role', 'ORG-0010', 'clean', ''),
    ('MARKET_INFO', 'Market Platform', 'Nord Pool', '62-63', ORG, 'platform role', 'ORG-0011', 'clean', ''),
    ('MARKET_INFO', 'Market Platform', 'Nord Pool / EUPHEMIA', '64-65', ORG, 'platform role', 'ORG-0011', 'flag',
     'EUPHEMIA is a price-coupling algorithm, not an organisation; record it as an attribute (D4).'),
    ('MARKET_INFO', 'Pricing Structure', 'Pay-as-Clear', '1-7,9-11,57-65', 'LK_PRICING_RULE', 'Pricing Structure', 'pay_as_clear', 'deferred', 'Lookup file drafted in R-020.'),
    ('MARKET_INFO', 'Auction Type', 'Closed Double Sided', '1-7,9-11,59-60,62-63', 'LK_AUCTION_TYPE', 'Auction Type', 'sealed_double_sided', 'deferred', 'Lookup file drafted in R-020.'),
    ('MARKET_INFO', 'Market Structure', 'One-to-Many', '1-7,9-11', '(none)', 'Market Structure', 'one_to_many', 'deferred', 'No lookup in R-001 Change 6; R-020 to propose LK_MARKET_STRUCTURE or drop the column.'),
    ('MARKET_INFO', 'Market Structure', 'Many-to-Many', '57-60,62-65', '(none)', 'Market Structure', 'many_to_many', 'deferred', 'As above.'),
    ('MARKET_INFO', 'Market Objective', 'Maximise Social Welfare', '1-7,9-11,62-64', '(none)', 'Market Objective', 'maximise_social_welfare', 'deferred', 'No lookup in Change 6; R-020.'),
    ('MARKET_INFO', 'Market Objective', 'Nor', '65', '(none)', 'Market Objective', '', 'unmapped', 'Truncated value; R-005.'),
    ('MARKET_INFO', 'Market Co-Optimisation', 'Yes: Response & Reserve', '1-7,9-11', 'LK_YESNO', 'Market Co-Optimisation', 'yes', 'flag',
     'The "Response & Reserve" part becomes co_optimised_with relationship rows (R-001 Change 13).'),
    ('MARKET_INFO', 'Availability Payment', 'Yes', '1-6,9-11', 'LK_YESNO', 'Availability Payment', 'yes', 'clean', ''),
    ('MARKET_INFO', 'Utilisation Payment', 'No', '1-6,9', 'LK_YESNO', 'Utilisation Payment', 'no', 'clean', ''),
    ('MARKET_INFO', 'Utilisation Payment', 'Yes (via. BM)', '10-11', 'LK_YESNO', 'Utilisation Payment', 'yes', 'flag',
     '"via BM" moves to Notes or a settles_via relationship (R-001 Change 13).'),
    ('MARKET_INFO', 'Parent-Child Orders', 'Yes', '1-6,9-11,57-60', 'LK_YESNO', 'Parent-Child Orders', 'yes', 'clean', ''),
    ('MARKET_INFO', 'Block Orders', 'Yes', '57-60', 'LK_YESNO', 'Block Orders', 'yes', 'clean', ''),
    # ---- DISPATCH
    ('DISPATCH', 'Dispatcher', 'Self', '1-7,9,33,57-66', '(none)', 'Dispatcher', 'self', 'deferred', 'Not an organisation; R-001 Change 10 allows `self` (Phase 3).'),
    ('DISPATCH', 'Dispatcher', 'NESO', '10-11', ORG, 'Dispatcher', 'ORG-0001', 'clean', ''),
    ('DISPATCH', 'Dispatcher', 'N/A', '34-56', '(none)', 'Dispatcher', 'not_applicable', 'clean', ''),
    ('DISPATCH', 'Dispatch Type', 'Auto', '1-7,9', '(none)', 'Dispatch Type', 'automatic_frequency', 'deferred', 'R-001 Change 10 codes (Phase 3).'),
    ('DISPATCH', 'Dispatch Type', 'BOA/OBP', '10-11', '(none)', 'Dispatch Type', 'boa;obp', 'flag', 'Multi-valued; R-001 Change 10 (Phase 3).'),
    ('DISPATCH', 'Dispatch Type', 'Self', '33,57-66', '(none)', 'Dispatch Type', 'self_dispatch', 'deferred', 'R-001 Change 10 (Phase 3).'),
    ('DISPATCH', 'Dispatch Type', 'N/A', '34-56', '(none)', 'Dispatch Type', 'not_applicable', 'deferred', 'R-001 Change 10 (Phase 3).'),
    ('DISPATCH', 'Pre-Fault', 'Yes', '3-7,10-11,33,57-66', 'LK_YESNO', 'Pre-Fault', 'yes', 'clean', ''),
    ('DISPATCH', 'Pre-Fault', 'No', '1-2,9,12-13', 'LK_YESNO', 'Pre-Fault', 'no', 'clean', ''),
    ('DISPATCH', 'Pre-Fault', 'N/A', '34-56', 'LK_YESNO', 'Pre-Fault', 'not_applicable', 'clean', ''),
    ('DISPATCH', 'Post-Fault', 'Yes', '1-2,7,9-13', 'LK_YESNO', 'Post-Fault', 'yes', 'clean', ''),
    ('DISPATCH', 'Post-Fault', 'No', '3-6,57-66', 'LK_YESNO', 'Post-Fault', 'no', 'clean', ''),
    ('DISPATCH', 'Post-Fault', 'N/A', '33-56', 'LK_YESNO', 'Post-Fault', 'not_applicable', 'clean', ''),
    # ---- PARTICIPANTS
    ('PARTICIPANTS', 'BMUs', 'Yes', '1-6,9-11', 'LK_YESNO', 'BMUs', 'yes', 'clean', ''),
    ('PARTICIPANTS', 'Non-BMUs', 'Yes', '1-6,9-11', 'LK_YESNO', 'Non-BMUs', 'yes', 'clean', ''),
    ('PARTICIPANTS', 'Generation', 'Yes', '1-6,9', 'LK_YESNO', 'Generation', 'yes', 'clean', ''),
    ('PARTICIPANTS', 'Demand', 'Yes', '1-6,9', 'LK_YESNO', 'Demand', 'yes', 'clean', ''),
    ('PARTICIPANTS', 'Storage', 'Yes', '1-6,9', 'LK_YESNO', 'Storage', 'yes', 'clean', ''),
    ('PARTICIPANTS', 'Suppliers', 'No?', '1-6', 'LK_YESNO', 'Suppliers', 'no', 'flag',
     'R-001 Change 7: record the doubt as confidence low, not in the value.'),
    ('PARTICIPANTS', 'Aggregation', 'GSP', '1-6,10-11', 'LK_AGGREGATION_LEVEL', 'Aggregation', 'gsp', 'deferred',
     'Lookup file in R-020; check whether the service terms mean GSP or GSP Group.'),
    ('PARTICIPANTS', 'Aggregation', 'National', '9', 'LK_AGGREGATION_LEVEL', 'Aggregation', 'national', 'deferred', 'Lookup file in R-020.'),
]

# Columns whose every value must be covered (blank included only where listed in M)
COVER = {
    'KEY_DATA': ['Market Type', 'Market Operator', 'Status', 'Commodity', 'Direction', 'Contract Length Band'],
    'MARKET_INFO': ['Market Platform', 'Pricing Structure', 'Auction Type', 'Market Structure', 'Market Objective',
                    'Market Co-Optimisation', 'Availability Payment', 'Utilisation Payment', 'Parent-Child Orders',
                    'Block Orders'],
    'DISPATCH': ['Dispatcher', 'Dispatch Type', 'Pre-Fault', 'Post-Fault'],
    'PARTICIPANTS': ['BMUs', 'Non-BMUs', 'Generation', 'Demand', 'Storage', 'Suppliers', 'Aggregation'],
}
data = {f: load(f) for f in COVER}
problems = []
for f, cols in COVER.items():
    for col in cols:
        actual = {}
        for r in data[f]:
            actual.setdefault(r[col], set()).add(r['ID'])
        # one target per (value, ids) is enough for coverage; Market Type has two targets
        mapped = {}
        for mf, mc, val, spec, *_ in M:
            if mf == f and mc == col:
                mapped.setdefault(val, set()).update(ids(spec))
        for val, idset in actual.items():
            if val == '' and val not in mapped:
                continue  # blank and not mentioned = stays blank
            if mapped.get(val) != idset:
                problems.append((f, col, val, sorted(idset ^ mapped.get(val, set()))))
        for val in mapped:
            if val not in actual:
                problems.append((f, col, val, 'value not in data'))
# Market Type: both targets must cover the same IDs
for tgt in (LKC, LKG):
    got = {}
    for mf, mc, val, spec, tt, *_ in M:
        if mc == 'Market Type' and tt == tgt:
            got.setdefault(val, set()).update(ids(spec))
    for r in data['KEY_DATA']:
        if r['ID'] not in got.get(r['Market Type'], set()):
            problems.append(('KEY_DATA', 'Market Type', tgt, r['ID']))
assert not problems, problems

rows = [['file', 'column', 'current_value', 'mechanism_ids', 'target_table', 'target_column', 'proposed_code',
         'mapping_status', 'note']]
for mf, mc, val, spec, tt, tc, code, st, note in M:
    rows.append([mf + '.csv', mc, val if val else '(blank)', rng(ids(spec)), tt, tc, code, st, note])
out = io.StringIO(newline='')
csv.writer(out, lineterminator='\r\n').writerows(rows)
with open(os.path.join(OUT, 'VALUE_MAPPING.csv'), 'wb') as fh:
    fh.write(('﻿' + out.getvalue()).encode('utf-8'))
from collections import Counter
print('mapping rows:', len(rows) - 1, Counter(r[7] for r in rows[1:]))
