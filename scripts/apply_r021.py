"""R-021: apply the approved R-009 drafts (lookups, ORGANISATIONS, SOURCES, value mapping) to CSV/.

ONE-OFF SCRIPT. Human decisions 2026-11-23: R-009 D1-D11 approved, with D8 amended to add only
`Standard Variant`, plus two human changes. All are recorded under "Human decisions" in
research/proposals/2026-11-23-R-009-lookups-and-organisations.md.

Steps:
  1. Add 12 new tables to CSV/ from research/drafts/R-009/:
     - ORGANISATIONS, with licence_id dropped (D2);
     - SOURCES, with the "Reuse:" text moved from notes into a new reuse_terms column (D1);
     - 10 LK_* lookups. LK_CONTRACT_LENGTH_BAND gets min/max duration columns (human change 1).
  2. Convert text to codes in place (D10), using VALUE_MAPPING.csv. A column is converted only if
     every non-blank value in it can be converted now. Columns whose lookup comes later (R-020,
     Phase 3) are left untouched.
  3. KEY_DATA: replace Market Type with Mechanism Class and Category, and add Standard Variant (D8).
  4. Where a mapping drops a qualifier (e.g. "Yes (via. BM)"), copy it into the row's Notes.
  5. Back up first. Log every change in research/change_log.csv: one row per
     file / column / old value / new value, with the IDs joined by ';'. Then check the result.

Run:  python scripts/apply_r021.py --dry-run   (all checks, writes nothing)
      python scripts/apply_r021.py             (apply)
Re-running after it has been applied stops at the first check, before any write.
"""
import argparse, csv, datetime, hashlib, io, os, re, shutil, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
CSVD = os.path.join(ROOT, 'CSV')
DRAFT = os.path.join(ROOT, 'research', 'drafts', 'R-009')
LOG = os.path.join(ROOT, 'research', 'change_log.csv')
PROP = 'research/proposals/2026-11-23-R-009-lookups-and-organisations.md'
ITEM = 'R-021'
APPROVAL = 'R-009 decisions D1-D11 approved 2026-11-23 (D8 amended: Standard Variant only)'
OLD_FILES = ['KEY_DATA', 'MARKET_INFO', 'TECHNICAL', 'DISPATCH', 'PARTICIPANTS', 'DESCRIPTION']
LOOKUPS = ['LK_CATEGORY', 'LK_COMMODITY', 'LK_CONTRACT_LENGTH_BAND', 'LK_DIRECTION',
           'LK_DSO_PRODUCT_VARIANT', 'LK_DSO_STANDARD_PRODUCT', 'LK_MECHANISM_CLASS', 'LK_ORG_TYPE',
           'LK_STATUS', 'LK_YESNO']
NEW_FILES = ['ORGANISATIONS', 'SOURCES'] + LOOKUPS

# (file, source column, target column) -> target table ('ORG' = ORGANISATIONS.org_id)
CONVERT = {
    ('KEY_DATA', 'Market Type', 'Mechanism Class'): 'LK_MECHANISM_CLASS',
    ('KEY_DATA', 'Market Type', 'Category'): 'LK_CATEGORY',
    ('KEY_DATA', 'Market Operator', 'Market Operator'): 'ORG',
    ('KEY_DATA', 'Status', 'Status'): 'LK_STATUS',
    ('KEY_DATA', 'Commodity', 'Commodity'): 'LK_COMMODITY',
    ('KEY_DATA', 'Direction', 'Direction'): 'LK_DIRECTION',
    ('KEY_DATA', 'Contract Length Band', 'Contract Length Band'): 'LK_CONTRACT_LENGTH_BAND',
    **{('MARKET_INFO', c, c): 'LK_YESNO' for c in
       ['Market Co-Optimisation', 'Availability Payment', 'Utilisation Payment', 'Parent-Child Orders',
        'Block Orders']},
    **{('DISPATCH', c, c): 'LK_YESNO' for c in ['Pre-Fault', 'Post-Fault']},
    **{('PARTICIPANTS', c, c): 'LK_YESNO' for c in
       ['BMUs', 'Non-BMUs', 'Generation', 'Demand', 'Storage', 'Suppliers']},
}
# Left as text until their lookups exist (reported, not changed).
DEFERRED = {('MARKET_INFO', 'Market Platform'): 'LK_PLATFORM and MECHANISM_ORG_ROLE (R-020)',
            ('MARKET_INFO', 'Pricing Structure'): 'LK_PRICING_RULE (R-020)',
            ('MARKET_INFO', 'Auction Type'): 'LK_AUCTION_TYPE (R-020)',
            ('MARKET_INFO', 'Market Structure'): 'R-020',
            ('MARKET_INFO', 'Market Objective'): 'R-020',
            ('DISPATCH', 'Dispatcher'): 'R-020 / Phase 3 Change 10',
            ('DISPATCH', 'Dispatch Type'): 'Phase 3 Change 10',
            ('PARTICIPANTS', 'Aggregation'): 'LK_AGGREGATION_LEVEL (R-020)'}
# Mappings that drop part of a value: the dropped part is kept in the row's Notes.
QUALIFIER = {
    ('MARKET_INFO', 'Market Co-Optimisation', 'Yes: Response & Reserve'):
        'Co-optimised with Response & Reserve (was "Yes: Response & Reserve"; to become '
        'co_optimised_with relationships, R-001 Change 13).',
    ('MARKET_INFO', 'Utilisation Payment', 'Yes (via. BM)'):
        'Utilisation is paid via the Balancing Mechanism (was "Yes (via. BM)"; to become a '
        'settles_via relationship, R-001 Change 13).',
    ('PARTICIPANTS', 'Suppliers', 'No?'):
        'Suppliers = no is low confidence (was "No?"; to move to a confidence field, R-001 Change 7).',
}
# Approved mappings to blank: not an organisation; the otc_bilateral class carries the meaning.
ALLOWED_TO_BLANK = {('KEY_DATA', 'Market Operator', 'Brokers & Bilaterals')}
KD_HEADER = ['ID', 'Market Name', 'Mechanism Class', 'Category', 'Market Operator', 'Acronym', 'Status',
             'Commodity', 'Direction', 'Contract Length Band', 'Standard Variant', 'Notes']
# Human change 1: ISO 8601 durations; the lower bound is exclusive and the upper bound inclusive.
CLB = {'le_day': ('Up to 1 day', 'P0D', 'P1D'),
       'day_to_week': ('More than 1 day, up to 1 week', 'P1D', 'P7D'),
       'week_to_month': ('More than 1 week, up to 1 month', 'P7D', 'P1M'),
       'month_to_year': ('More than 1 month, up to 1 year', 'P1M', 'P1Y')}


def read_bytes(p):
    with open(p, 'rb') as fh:
        return fh.read()


def parse(b):
    return list(csv.reader(io.StringIO(b.decode('utf-8-sig'), newline='')))


def serialise(rows):
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\r\n').writerows(rows)
    return ('﻿' + out.getvalue()).encode('utf-8')


def load(path):
    b = read_bytes(path)
    rows = parse(b)
    assert serialise(rows) == b, f'{path} would not round-trip byte-for-byte'
    return rows


def expand(ids):
    out = []
    for part in [p.strip() for p in ids.split(';') if p.strip()]:
        m = re.fullmatch(r'MEC-(\d{4})\.\.MEC-(\d{4})', part)
        out += [f'MEC-{i:04d}' for i in range(int(m.group(1)), int(m.group(2)) + 1)] if m else [part]
    return out


def as_dicts(rows):
    return [dict(zip(rows[0], r)) for r in rows[1:]]


ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok &= bool(cond)


def main():
    ap = argparse.ArgumentParser(description='Apply the approved R-009 drafts to CSV/ (R-021).')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    today = datetime.date.today().isoformat()

    # ---------- load ----------
    for n in NEW_FILES:
        assert not os.path.exists(os.path.join(CSVD, n + '.csv')), f'CSV/{n}.csv already exists (already applied?)'
    old = {n: load(os.path.join(CSVD, n + '.csv')) for n in OLD_FILES}
    assert old['KEY_DATA'][0][2] == 'Market Type', 'KEY_DATA already restructured (already applied?)'
    draft = {n: load(os.path.join(DRAFT, n + '.csv')) for n in NEW_FILES + ['VALUE_MAPPING', 'KEY_DATA_DSO_COLUMNS']}
    log_raw = read_bytes(LOG)
    log_rows = parse(log_raw)
    assert serialise(log_rows) == log_raw, 'change_log.csv would not round-trip'
    log_add = []

    # ---------- 1. new tables ----------
    new_tables = {}
    org = draft['ORGANISATIONS']
    li = org[0].index('licence_id')
    assert all(r[li] == '' for r in org[1:]), 'licence_id is not blank everywhere'
    new_tables['ORGANISATIONS'] = [[c for j, c in enumerate(r) if j != li] for r in org]
    src = draft['SOURCES']
    ni = src[0].index('notes')
    out = [src[0] + ['reuse_terms']]
    moved = 0
    for r in src[1:]:
        note = r[ni]
        assert note.count('Reuse:') <= 1, r[0]
        if 'Reuse:' in note:
            before, after = note.split('Reuse:')
            r = list(r)
            r[ni] = before.strip()
            out.append(r + [after.strip()])
            moved += 1
        else:
            out.append(list(r) + [''])
    new_tables['SOURCES'] = out
    for n in LOOKUPS:
        new_tables[n] = [list(r) for r in draft[n]]
    clb = new_tables['LK_CONTRACT_LENGTH_BAND']
    assert clb[0] == ['code', 'label', 'definition', 'source_id'] and {r[0] for r in clb[1:]} == set(CLB)
    clb[0] += ['min_duration_exclusive', 'max_duration_inclusive']
    for r in clb[1:]:
        label, lo, hi = CLB[r[0]]
        r[1] = label
        r += [lo, hi]
    for n in NEW_FILES:
        extra = {'ORGANISATIONS': '; licence_id dropped (D2)',
                 'SOURCES': f'; reuse terms moved from notes to new reuse_terms column for {moved} rows (D1)',
                 'LK_CONTRACT_LENGTH_BAND': '; labels reworded and min_duration_exclusive / '
                                            'max_duration_inclusive (ISO 8601) added (human change 1, 2026-11-23)'}.get(n, '')
        log_add.append([today, ITEM, n + '.csv', '(new file)', '(all)', '(absent)',
                        f'new table, {len(new_tables[n]) - 1} rows, from research/drafts/R-009/{n}.csv{extra}',
                        f'{APPROVAL}; {PROP}'])

    codes = {n: {r[0] for r in new_tables[n][1:]} for n in LOOKUPS}
    codes['ORG'] = {r[0] for r in new_tables['ORGANISATIONS'][1:]}
    src_ids = {r[0] for r in new_tables['SOURCES'][1:]}

    # ---------- 2-3. conversions ----------
    vm = defaultdict(dict)  # (file, column, target_column) -> {(value, id): (code, status, note)}
    for r in as_dicts(draft['VALUE_MAPPING']):
        f = r['file'][:-4]
        for id_ in expand(r['mechanism_ids']):
            vm[(f, r['column'], r['target_column'])][(r['current_value'], id_)] = (
                r['proposed_code'], r['mapping_status'], r['note'])
    new = {n: [list(x) for x in old[n]] for n in OLD_FILES}
    converted = {}  # (file, target column) -> {id: new value}
    groups = defaultdict(list)  # (file, column, old, new, reason) -> [ids]
    for (f, col, tcol), target in CONVERT.items():
        m = vm[(f, col, tcol)]
        assert m, f'no mapping rows for {f}.{col} -> {tcol}'
        hdr = old[f][0]
        ci = hdr.index(col)
        res = {}
        for r in old[f][1:]:
            id_, v = r[0], r[ci]
            key = ('(blank)' if v == '' else v, id_)
            if key in m:
                code, status, note = m[key]
                assert status in ('clean', 'flag', 'fill', 'unmapped'), (f, col, v, id_, status)
                if status == 'unmapped':
                    assert code == '' and (v == '' or (f, col, v) in ALLOWED_TO_BLANK), (f, col, v, id_)
                nv = code
                reason = f'{APPROVAL}; VALUE_MAPPING {status}' + (f': {note}' if note else '') + f'; {PROP}'
            else:
                assert v == '', f'no mapping for {f}.{col} = {v!r} ({id_})'
                nv, reason = '', ''
            assert nv == '' or nv in codes[target], (f, tcol, nv)
            res[id_] = nv
            if nv != v or col != tcol:
                if not (v == '' and nv == ''):
                    groups[(f, tcol, v, nv, reason)].append(id_)
        converted[(f, tcol)] = res

    # Standard Variant (D8 amended)
    lk_var = {r['code']: r for r in as_dicts(new_tables['LK_DSO_PRODUCT_VARIANT'])}
    sv = {}
    for r in as_dicts(draft['KEY_DATA_DSO_COLUMNS']):
        v = r['Standard Variant']
        if v:
            assert v in lk_var, v
            assert r['Standard Product'] == lk_var[v]['product_code'], (r['ID'], r['Standard Product'], v)
            sv[r['ID']] = v
            groups[('KEY_DATA', 'Standard Variant', '', v,
                    f'{APPROVAL}; R-008 Change 2 via R-009 KEY_DATA_DSO_COLUMNS; {r["source_id"]} {r["locator"]}; {PROP}')].append(r['ID'])
        else:
            assert r['ID'] == 'MEC-0076', r['ID']  # on hold (R-008 Change 3)
    print(f'Standard Variant: {len(sv)} rows filled; MEC-0076 on hold')

    # rebuild KEY_DATA
    kd_old = as_dicts(old['KEY_DATA'])
    kd_new = [KD_HEADER]
    for r in kd_old:
        id_ = r['ID']
        row = {**r}
        for (f, tcol), res in converted.items():
            if f == 'KEY_DATA':
                row[tcol] = res[id_]
        row['Standard Variant'] = sv.get(id_, '')
        kd_new.append([row[c] for c in KD_HEADER])
    new['KEY_DATA'] = kd_new
    log_add.append([today, ITEM, 'KEY_DATA.csv', '(header)', 'Market Type', 'Market Type',
                    '(removed; replaced by Mechanism Class and Category)', f'{APPROVAL} (D10); {PROP}'])
    for c in ['Mechanism Class', 'Category', 'Standard Variant']:
        log_add.append([today, ITEM, 'KEY_DATA.csv', '(header)', c, '(absent)', c + ' (new column)',
                        f'{APPROVAL} (D8, D10, D11); {PROP}'])

    # other files: in-place conversion + qualifiers to Notes
    for f in ['MARKET_INFO', 'DISPATCH', 'PARTICIPANTS']:
        hdr = new[f][0]
        for r in new[f][1:]:
            for (ff, tcol), res in converted.items():
                if ff == f:
                    r[hdr.index(tcol)] = res[r[0]]
        if 'Notes' in hdr:
            ni = hdr.index('Notes')
            for r, o in zip(new[f][1:], old[f][1:]):
                for (qf, qc, qv), text in QUALIFIER.items():
                    if qf == f and o[hdr.index(qc)] == qv:
                        before = r[ni]
                        r[ni] = (before + ' ' if before else '') + text
                        groups[(f, 'Notes', before, r[ni],
                                f'{APPROVAL}; qualifier kept from {qc} = "{qv}" when that value became a code; {PROP}')].append(r[0])
    for (f, col, ov, nv, reason), ids in sorted(groups.items()):
        log_add.append([today, ITEM, f + '.csv', ';'.join(ids), col, ov if ov else '(blank)',
                        nv if nv else '(blank)', reason])

    # ---------- checks on the planned result ----------
    print('\n=== Checks on the planned result ===')
    check_all(old, new, new_tables, converted, codes, src_ids, sv)
    for (f, c), why in DEFERRED.items():
        vals = sorted({r[old[f][0].index(c)] for r in old[f][1:]} - {''})
        print(f'DEFERRED {f}.{c} left as text ({why}): {vals}')
    print(f'change_log rows to append: {len(log_add)}')
    if not ok:
        sys.exit('\nOVERALL: FAIL - nothing written')
    if a.dry_run:
        print('\nDRY RUN: all checks pass. Nothing written.')
        return

    # ---------- backup, write ----------
    bdir = os.path.join(ROOT, 'research', 'backups', f'{today}-pre-r021')
    if os.path.exists(bdir):
        sys.exit(f'Backup folder already exists, stopping: {bdir}')
    os.makedirs(bdir)
    for p in [os.path.join(CSVD, n + '.csv') for n in OLD_FILES] + [LOG]:
        dst = os.path.join(bdir, os.path.basename(p))
        shutil.copy2(p, dst)
        assert hashlib.sha256(read_bytes(dst)).digest() == hashlib.sha256(read_bytes(p)).digest(), dst
    print(f'\nBacked up 7 files to {os.path.relpath(bdir, ROOT)} (SHA-256 confirmed)')
    for n, rows in list(new_tables.items()) + [(n, new[n]) for n in OLD_FILES if new[n] != old[n]]:
        with open(os.path.join(CSVD, n + '.csv'), 'wb') as fh:
            fh.write(serialise(rows))
    with open(LOG, 'wb') as fh:
        fh.write(serialise(log_rows + log_add))

    # ---------- re-read and check what is on disk ----------
    print('\n=== Checks on the files as written ===')
    disk = {}
    for n in OLD_FILES + NEW_FILES:
        b = read_bytes(os.path.join(CSVD, n + '.csv'))
        check(b.startswith(b'\xef\xbb\xbf') and b.count(b'\n') == b.count(b'\r\n'), f'{n}: BOM and CRLF')
        disk[n] = parse(b)
    check_all(old, {n: disk[n] for n in OLD_FILES}, {n: disk[n] for n in NEW_FILES}, converted, codes, src_ids, sv)
    check(parse(read_bytes(LOG)) == log_rows + log_add, f'change_log.csv: {len(log_add)} rows appended, existing rows unchanged')
    print('\nOVERALL:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


def check_all(old, new, tables, converted, codes, src_ids, sv):
    # IDs, row order and untouched cells
    touched = {(f, c) for (f, c) in converted} | {('KEY_DATA', 'Standard Variant')}
    for n in OLD_FILES:
        o, w = old[n], new[n]
        check([r[0] for r in o[1:]] == [r[0] for r in w[1:]], f'{n}: same {len(o) - 1} IDs in the same order')
        od, wd = as_dicts(o), as_dicts(w)
        diffs = []
        for a_, b_ in zip(od, wd):
            for c in w[0]:
                if (n, c) in touched or c == 'Notes':
                    continue
                if a_.get(c) != b_.get(c):
                    diffs.append((a_['ID'], c))
        check(not diffs, f'{n}: every cell outside the converted columns and Notes is unchanged {diffs[:3]}')
        if 'Notes' in w[0] and 'Notes' in o[0]:
            bad = [a_['ID'] for a_, b_ in zip(od, wd) if not b_['Notes'].startswith(a_['Notes'])]
            check(not bad, f'{n}: Notes only appended to, never overwritten {bad[:3]}')
    kd = as_dicts(new['KEY_DATA'])
    check(new['KEY_DATA'][0] == KD_HEADER, 'KEY_DATA: new header layout')
    check(all(r['Mechanism Class'] and r['Category'] for r in kd), 'KEY_DATA: every row has a Mechanism Class and Category')
    check(all((r['Standard Variant'] != '') == (r['ID'] in sv) for r in kd)
          and all(r['Mechanism Class'] == 'dso_flexibility' for r in kd if r['Standard Variant']),
          'KEY_DATA: Standard Variant filled only on dso_flexibility rows, as drafted')
    for (f, _, tcol), target in CONVERT.items():
        rows = as_dicts(new[f])
        bad = [(r['ID'], r[tcol]) for r in rows if r[tcol] and r[tcol] not in codes[target]]
        check(not bad, f'{f}.{tcol}: every non-blank value is a code in {target} {bad[:3]}')
    # references inside the new tables
    for n, rows in tables.items():
        d = as_dicts(rows)
        if 'source_id' in rows[0] and n != 'SOURCES':
            bad = [r['source_id'] for r in d if r['source_id'] and not set(r['source_id'].replace(';', ' ').split()) <= src_ids]
            check(not bad, f'{n}: every source_id resolves in SOURCES {bad[:3]}')
    orgs = as_dicts(tables['ORGANISATIONS'])
    bad = [r['org_id'] for r in orgs if r['org_type'] not in codes['LK_ORG_TYPE']
           or (r['parent_org_id'] and r['parent_org_id'] not in codes['ORG'])
           or (r['predecessor_org_id'] and r['predecessor_org_id'] not in codes['ORG'])]
    check(not bad, f'ORGANISATIONS: org_type, parent_org_id and predecessor_org_id resolve {bad[:3]}')
    check('licence_id' not in tables['ORGANISATIONS'][0], 'ORGANISATIONS: licence_id dropped (D2)')
    check(tables['SOURCES'][0][-1] == 'reuse_terms', 'SOURCES: reuse_terms column added (D1)')


if __name__ == '__main__':
    main()
