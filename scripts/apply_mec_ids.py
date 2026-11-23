"""Rename mechanism IDs 001-112 to MEC-0001..MEC-0112 in all six CSVs (R-001 Change 1a).

ONE-OFF SCRIPT. Approved by the human on 2026-11-23; see Change 1a in
research/proposals/2026-11-23-R-001-database-structure-review.md.

Steps:
  1. Check that all six files in CSV/ have ID as their first column, with the same three-digit IDs
     in the same order, and that each file would be rewritten byte-for-byte except for the ID cells.
  2. Copy the six CSVs and research/change_log.csv to research/backups/<date>-pre-mec-ids/ and
     confirm each copy by SHA-256.
  3. Rewrite the ID column only (same number, `MEC-` + 4 digits), keeping the UTF-8 BOM and CRLF.
  4. Append one mapping row per ID to research/change_log.csv.
  5. Re-read everything and check that nothing except the ID column changed.

Run:  python scripts/apply_mec_ids.py R-0XX --dry-run   (all checks, writes nothing)
      python scripts/apply_mec_ids.py R-0XX             (apply)
Re-running after it has been applied stops at the first check, before any write.
"""
import argparse, csv, datetime, hashlib, io, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
CSVD = os.path.join(ROOT, 'CSV')
LOG = os.path.join(ROOT, 'research', 'change_log.csv')
FILES = ['KEY_DATA', 'MARKET_INFO', 'TECHNICAL', 'DISPATCH', 'PARTICIPANTS', 'DESCRIPTION']
LOG_HEADER = ['date', 'backlog_item', 'file', 'id', 'column', 'old_value', 'new_value', 'reason/source']
PROP = 'research/proposals/2026-11-23-R-001-database-structure-review.md'
REASON = ('R-001 Change 1a (approved 2026-11-23): prefixed permanent ID, same number; '
          f'applies to the ID column of all six CSVs; {PROP}')


def read_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def write_bytes(path, b):
    with open(path, 'wb') as fh:
        fh.write(b)


def parse(b):
    return list(csv.reader(io.StringIO(b.decode('utf-8-sig'), newline='')))


def serialise(rows):
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\r\n').writerows(rows)
    return ('﻿' + out.getvalue()).encode('utf-8')


ok = True


def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok &= bool(cond)


def verify(old, new, ids, mapping):
    want = [mapping[i] for i in ids]
    names = {r[0]: r[1] for r in new['KEY_DATA'][1:]}
    for n in FILES:
        o, w = old[n], new[n]
        check(w[0] == o[0], f'{n}: header unchanged')
        check([r[0] for r in w[1:]] == want, f'{n}: IDs are {want[0]}..{want[-1]} in the original order')
        check(all(re.fullmatch(r'MEC-\d{4}', r[0]) for r in w[1:]), f'{n}: every ID matches MEC-NNNN')
        check(len(o) == len(w) and all(a[1:] == b[1:] for a, b in zip(o[1:], w[1:])),
              f'{n}: every non-ID cell unchanged')
        mi = w[0].index('Market Name')
        check(all(r[mi] == names[r[0]] for r in w[1:]), f'{n}: Market Name matches KEY_DATA for every ID')


def main():
    ap = argparse.ArgumentParser(description='Rename mechanism IDs to MEC-NNNN (R-001 Change 1a).')
    ap.add_argument('item', help='backlog item recorded in the change log, e.g. R-013')
    ap.add_argument('--dry-run', action='store_true', help='run every check without writing anything')
    a = ap.parse_args()
    if not re.fullmatch(r'R-\d{3}', a.item):
        sys.exit(f'Bad backlog item {a.item!r}; expected e.g. R-013')
    today = datetime.date.today().isoformat()

    # 1. pre-checks
    paths = {n: os.path.join(CSVD, n + '.csv') for n in FILES}
    raw = {n: read_bytes(p) for n, p in paths.items()}
    old = {n: parse(b) for n, b in raw.items()}
    ids = [r[0] for r in old['KEY_DATA'][1:]]
    assert all(re.fullmatch(r'\d{3}', i) for i in ids), 'KEY_DATA IDs are not all 3-digit numbers (already renamed?)'
    assert len(set(ids)) == len(ids), 'duplicate IDs in KEY_DATA'
    for n in FILES:
        assert old[n][0][0] == 'ID', f'{n}: first column is not ID'
        assert [r[0] for r in old[n][1:]] == ids, f'{n}: IDs differ from KEY_DATA'
        assert serialise(old[n]) == raw[n], f'{n}: would not round-trip byte-for-byte'
    mapping = {i: f'MEC-{int(i):04d}' for i in ids}

    log_raw = read_bytes(LOG)
    log_rows = parse(log_raw)
    assert log_rows[0] == LOG_HEADER, f'unexpected change_log header {log_rows[0]}'
    assert serialise(log_rows) == log_raw, 'change_log.csv would not round-trip byte-for-byte'

    # old IDs mentioned inside other cells are reported, never changed
    notes = []
    for n in FILES:
        hdr = old[n][0]
        for r in old[n][1:]:
            for j, c in enumerate(r[1:], 1):
                hits = [h for h in re.findall(r'(?<!\d)\d{3}(?!\d)', c) if h in mapping]
                if hits:
                    notes.append(f'  {n} {r[0]} [{hdr[j]}]: contains {hits}')
    print(f'Cells mentioning a 3-digit number in 001-{ids[-1]} (left unchanged; check by eye): {len(notes)}')
    print('\n'.join(notes))

    new = {n: [old[n][0]] + [[mapping[r[0]]] + r[1:] for r in old[n][1:]] for n in FILES}
    new_log = log_rows + [[today, a.item, '(all six CSVs)', i, 'ID', i, mapping[i], REASON] for i in ids]

    print('\n=== Checks on the planned result (in memory) ===')
    verify(old, new, ids, mapping)
    if not ok:
        sys.exit('\nOVERALL: FAIL - nothing written')
    if a.dry_run:
        print(f'\nDRY RUN: all checks pass. Would rename {len(ids)} IDs in {len(FILES)} files and append '
              f'{len(ids)} rows to research/change_log.csv ({len(log_rows) - 1} -> {len(new_log) - 1}). Nothing written.')
        return

    # 2. backup
    bdir = os.path.join(ROOT, 'research', 'backups', f'{today}-pre-mec-ids')
    if os.path.exists(bdir):
        sys.exit(f'Backup folder already exists, stopping: {bdir}')
    os.makedirs(bdir)
    for p in list(paths.values()) + [LOG]:
        dst = os.path.join(bdir, os.path.basename(p))
        shutil.copy2(p, dst)
        assert hashlib.sha256(read_bytes(dst)).digest() == hashlib.sha256(read_bytes(p)).digest(), dst
    print(f'\nBacked up 7 files to {os.path.relpath(bdir, ROOT)} (SHA-256 confirmed)')

    # 3-4. write
    for n in FILES:
        write_bytes(paths[n], serialise(new[n]))
    write_bytes(LOG, serialise(new_log))

    # 5. re-read and verify what is on disk
    print('\n=== Checks on the files as written ===')
    disk = {n: read_bytes(paths[n]) for n in FILES}
    for n in FILES:
        b = disk[n]
        check(b.startswith(b'\xef\xbb\xbf'), f'{n}: UTF-8 BOM present')
        check(b.count(b'\n') == b.count(b'\r\n') and b.endswith(b'\r\n'), f'{n}: CRLF line endings only')
    verify(old, {n: parse(b) for n, b in disk.items()}, ids, mapping)
    log_disk = parse(read_bytes(LOG))
    check(log_disk[:len(log_rows)] == log_rows, 'change_log.csv: existing rows unchanged')
    check(len(log_disk) == len(log_rows) + len(ids), f'change_log.csv: {len(ids)} rows appended')
    print('\nOVERALL:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
