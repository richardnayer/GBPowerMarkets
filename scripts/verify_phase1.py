"""R-007: verify Phase 1 of the R-001 proposal.

Read-only. Checks that all six CSVs in CSV/ share IDs 001-112, that names match KEY_DATA, that
BOM/CRLF formatting is preserved, and diffs the files against research/backups/2026-11-23-pre-phase1/.
Run:  python scripts/verify_phase1.py
"""
import csv, io, os
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
NEW = os.path.join(ROOT, 'CSV'); OLD = os.path.join(ROOT, 'research', 'backups', '2026-11-23-pre-phase1')
FILES = ['KEY_DATA', 'MARKET_INFO', 'TECHNICAL', 'DISPATCH', 'PARTICIPANTS', 'DESCRIPTION']
def raw(d, n): return open(os.path.join(d, n + '.csv'), 'rb').read()
def rows(d, n): return list(csv.reader(io.StringIO(raw(d, n).decode('utf-8-sig'), newline='')))
ok = True
def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg); ok &= bool(cond)

expected = [f'{i:03d}' for i in range(1, 113)]
kd = rows(NEW, 'KEY_DATA'); kdn = {r[0]: r[1] for r in kd[1:]}
for n in FILES:
    b = raw(NEW, n); rs = rows(NEW, n)
    check(b.startswith(b'\xef\xbb\xbf'), f'{n}: UTF-8 BOM present')
    check(b.count(b'\n') == b.count(b'\r\n') and b.endswith(b'\r\n'), f'{n}: CRLF line endings only')
    check(rs[0][0] == 'ID', f'{n}: first column is ID')
    ids = [r[0] for r in rs[1:]]
    check(len(rs) - 1 == 112, f'{n}: 112 data rows (got {len(rs)-1})')
    check(ids == expected, f'{n}: ID set/order is 001-112')
    check(max(Counter(ids).values()) == 1, f'{n}: IDs unique')
    check(len(set(len(r) for r in rs)) == 1, f'{n}: consistent column count ({len(rs[0])})')
    mi = rs[0].index('Market Name')
    bad = [(r[0], r[mi]) for r in rs[1:] if r[mi] != kdn[r[0]]]
    check(not bad, f'{n}: Market Name matches KEY_DATA for every ID {bad[:3]}')

# diff against backup, aligned by ID
print('\n=== Diff vs backup (cell level, aligned by ID) ===')
kd_old = rows(OLD, 'KEY_DATA'); old_ids = [r[0] for r in kd_old[1:]]
for n in FILES:
    o = rows(OLD, n); nw = rows(NEW, n)
    if n == 'KEY_DATA':
        ohdr = o[0]; odata = {r[0]: r for r in o[1:]}
    else:
        ohdr = ['ID'] + o[0]; odata = {}
        for i, r in enumerate(o[1:]):
            ids = [old_ids[i]] if i < 28 else (['029', '030'] if i == 28 else [old_ids[i + 1]])
            for id_ in ids: odata[id_] = ['(new)' if id_ == '030' else id_] + r
    nhdr = nw[0]
    hd = [(j, ohdr[j] if j < len(ohdr) else '(absent)', nhdr[j]) for j in range(len(nhdr)) if j >= len(ohdr) or ohdr[j] != nhdr[j]]
    print(f'{n}: header changes: {hd}')
    cnt = 0
    for r in nw[1:]:
        orow = odata[r[0]]
        for j in range(len(nhdr)):
            if j == 0 and n != 'KEY_DATA':
                continue  # ID column is new
            ov = orow[j] if j < len(orow) else '(absent)'
            if j == len(ohdr) and n == 'KEY_DATA':
                if r[j] != '': print(f'  UNEXPECTED non-empty new Notes {r[0]}')
                continue
            if ov != r[j]:
                cnt += 1; print(f'  {r[0]} [{nhdr[j]}]: {ov!r} -> {r[j]!r}')
    print(f'  {n}: {cnt} changed cells; rows old={len(o)-1} new={len(nw)-1}')

cl = list(csv.reader(open(os.path.join(ROOT, 'research', 'change_log.csv'), encoding='utf-8-sig', newline='')))
print(f'\nchange_log.csv: {len(cl)-1} rows, header={cl[0]}')
print('\nOVERALL:', 'PASS' if ok else 'FAIL')
