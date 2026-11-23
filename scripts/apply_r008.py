"""Apply the approved CSV changes from the R-008 proposal (Changes 4 and 5) to CSV/KEY_DATA.csv.

ONE-OFF SCRIPT. Approved by the human on 2026-11-23; see
research/proposals/2026-11-23-R-008-dso-product-taxonomy.md. Change 7 and the SUB_MARKET naming
only edit the R-001 proposal text. Changes 1-2 are folded into R-009, and Change 3 (ID 076) is on hold.

Fills 9 cells, each of which must be blank beforehand, keeping the UTF-8 BOM and CRLF line endings.
Appends 9 rows to research/change_log.csv, then checks that no other cell changed.
Run:  python scripts/apply_r008.py --dry-run   (checks only)
      python scripts/apply_r008.py             (apply)
"""
import argparse, csv, datetime, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
KD = os.path.join(ROOT, 'CSV', 'KEY_DATA.csv')
LOG = os.path.join(ROOT, 'research', 'change_log.csv')
S11 = ('https://www.northernpowergrid.com/sites/default/files/assets/'
       'Distribution%20Flexibility%20Services%20Procurement%20Statement%202026-27.pdf')
CLB = 'Contract Length Band'
C5 = 'R-008 Change 5 (approved 2026-11-23): NPg Sub-Market {}; source: ' + S11 + ' (Figure 2, PDF p.16)'
C4 = ('R-008 Change 4 (approved 2026-11-23): flag only, no value changed; source: ' + S11 +
      ' (Figure 2 PDF p.16; PDF p.14 and p.21)')
NOTE = ('Not a distinct product: NPg 2026-27 statement (Fig. 2) defines no Sub-Market 9 or 10. Same variant '
        '(SA OU-15) and use case as MEC-0082, so a further tender round or a duplicate. Flagged by R-008; '
        'to be merged into MEC-0082 as a sub-market in Phase 3.')
EDITS = [  # (ID, column, new value, reason/source)
    ('MEC-0075', CLB, 'Month < x <= Year', C5.format(1)),
    ('MEC-0077', CLB, 'Month < x <= Year', C5.format(3)),
    ('MEC-0078', CLB, 'Month < x <= Year', C5.format(4)),
    ('MEC-0079', CLB, 'Week < x <= Month', C5.format(5)),
    ('MEC-0080', CLB, 'Month < x <= Year', C5.format(6)),
    ('MEC-0081', CLB, 'Month < x <= Year', C5.format(7)),
    ('MEC-0082', CLB, 'Week < x <= Month', C5.format(8)),
    ('MEC-0083', 'Notes', NOTE, C4),
    ('MEC-0084', 'Notes', NOTE, C4),
]


def read_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def parse(b):
    return list(csv.reader(io.StringIO(b.decode('utf-8-sig'), newline='')))


def serialise(rows):
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\r\n').writerows(rows)
    return ('﻿' + out.getvalue()).encode('utf-8')


def changed_cells(old, new):
    return {(o[0], old[0][j]) for o, n in zip(old[1:], new[1:]) for j in range(len(o)) if o[j] != n[j]}


def main():
    ap = argparse.ArgumentParser(description='Apply R-008 Changes 4 and 5 to KEY_DATA.csv.')
    ap.add_argument('--dry-run', action='store_true', help='run every check without writing anything')
    a = ap.parse_args()
    today = datetime.date.today().isoformat()

    raw = read_bytes(KD)
    old = parse(raw)
    assert serialise(old) == raw, 'KEY_DATA.csv would not round-trip byte-for-byte'
    hdr = old[0]
    new = [list(r) for r in old]
    by_id = {r[0]: r for r in new[1:]}
    log_add = []
    for id_, col, val, why in EDITS:
        j = hdr.index(col)
        assert by_id[id_][j] == '', f'{id_} [{col}] is not blank: {by_id[id_][j]!r}'
        by_id[id_][j] = val
        log_add.append([today, 'R-008', 'KEY_DATA.csv', id_, col, '', val, why])
    want = {(i, c) for i, c, _, _ in EDITS}
    assert changed_cells(old, new) == want, 'unexpected cells changed'
    assert len(old) == len(new) and new[0] == hdr

    log_raw = read_bytes(LOG)
    log_rows = parse(log_raw)
    assert serialise(log_rows) == log_raw, 'change_log.csv would not round-trip byte-for-byte'
    print(f'Checks pass: {len(EDITS)} blank cells to fill in KEY_DATA.csv; no other cell changes.')
    if a.dry_run:
        print('DRY RUN: nothing written.')
        return

    with open(KD, 'wb') as fh:
        fh.write(serialise(new))
    with open(LOG, 'wb') as fh:
        fh.write(serialise(log_rows + log_add))

    disk = read_bytes(KD)
    ok = (disk.startswith(b'\xef\xbb\xbf') and disk.count(b'\n') == disk.count(b'\r\n')
          and changed_cells(old, parse(disk)) == want
          and parse(read_bytes(LOG)) == log_rows + log_add)
    print('Written. Re-read check (BOM, CRLF, only the 9 cells changed, 9 log rows appended):',
          'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
