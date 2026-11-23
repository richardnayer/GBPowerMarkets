"""R-007: apply Phase 1 (Changes 1-4) of research/proposals/2026-11-23-R-001-database-structure-review.md.

ONE-OFF SCRIPT - already applied on 2026-11-23. Kept as a record of exactly what was changed.
It rewrites the CSVs in CSV/ and overwrites research/change_log.csv. Re-running it against the
current files stops at the first assert (KEY_DATA already has the renamed header) before any write.
Original files: research/backups/2026-11-23-pre-phase1/.
"""
import csv, io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
CSVD = os.path.join(ROOT, 'CSV')
DATE = '2026-11-23'; ITEM = 'R-007'
PROP = 'research/proposals/2026-11-23-R-001-database-structure-review.md'
log = []
def L(file, id_, col, old, new, reason):
    log.append([DATE, ITEM, file, id_, col, old, new, reason])

def read(name):
    b = open(os.path.join(CSVD, name + '.csv'), 'rb').read()
    return list(csv.reader(io.StringIO(b.decode('utf-8-sig'), newline='')))
def write(name, rows):
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\r\n').writerows(rows)
    with open(os.path.join(CSVD, name + '.csv'), 'wb') as fh:
        fh.write(('\ufeff' + out.getvalue()).encode('utf-8'))

C1 = f'R-001 Change 1 (approved {DATE}); {PROP}'
C2 = f'R-001 Change 2 (approved {DATE}); header typo, source: the file itself'
C3 = f'R-001 Change 3 (approved {DATE}); market-name typo, source: the files themselves'
C4 = f'R-001 Change 4 (approved {DATE})'

# ---------- KEY_DATA ----------
kd = read('KEY_DATA')
hdr = kd[0]
assert hdr[8] == 'Notes' and len(hdr) == 9
hdr[8] = 'Contract Length Band'; hdr.append('Notes')
L('KEY_DATA.csv', '(header)', 'Notes', 'Notes', 'Contract Length Band', C2 + '; column holds contract-length bands')
L('KEY_DATA.csv', '(header)', 'Notes', '(absent)', 'Notes (new empty free-text column after Contract Length Band)', C2)
for r in kd[1:]:
    r.append('')
name_fix = {
    '100': ('Scheduled Utilisation ', 'Scheduled Utilisation', 'trailing space removed'),
    '102': ('Variable Availabiulity Operational Utilisation + 15 mins', 'Variable Availability Operational Utilisation + 15 mins', 'spelling Availabiulity -> Availability'),
    '103': ('Variable Availabiulity Operational + 2 mins', 'Variable Availability Operational + 2 mins', 'spelling Availabiulity -> Availability only; insertion of "Utilisation" deferred: not confirmed from an SPENW primary source'),
    '092': ('Schedule Utilisation (SU)', 'Scheduled Utilisation (SU)', 'Schedule -> Scheduled'),
    '111': ('Schedule Utilisation (Day Ahead)', 'Scheduled Utilisation (Day Ahead)', 'Schedule -> Scheduled'),
}
NP = C4 + '; "Nordpool" -> "Nord Pool", the exchange\'s own spelling: https://www.nordpoolgroup.com/'
for r in kd[1:]:
    if r[0] in name_fix:
        old, new, why = name_fix[r[0]]
        assert r[1] == old, (r[0], r[1]); r[1] = new
        L('KEY_DATA.csv', r[0], 'Market Name', old, new, C3 + '; ' + why)
    if r[3] == 'Nordpool':
        r[3] = 'Nord Pool'; L('KEY_DATA.csv', r[0], 'Market Operator', 'Nordpool', 'Nord Pool', NP)
spen = [r[0] for r in kd[1:] if r[3] == 'SPEN']; spenw = [r[0] for r in kd[1:] if r[3] == 'SPENW']
L('KEY_DATA.csv', ';'.join(spen), 'Market Operator', 'SPEN', 'SPEN (unchanged)', C4 + '; definition recorded only (no lookup table until Phase 2): SPEN = SP Energy Networks (DNO licensees SP Distribution plc and SP Manweb plc)')
L('KEY_DATA.csv', ';'.join(spenw), 'Market Operator', 'SPENW', 'SPENW (unchanged)', C4 + '; definition recorded only (no lookup table until Phase 2): SPENW = SP Electricity North West, formerly Electricity North West Ltd, renamed 4 Aug 2025 under Iberdrola ownership. Sources: https://www.iberdrola.com/press-room/news/detail/sp-electricity-north-west-unveiled-new-name-visual-identity-part-iberdrola-group ; https://www.enwl.co.uk/about-us/')
write('KEY_DATA', kd)
kd_ids = [r[0] for r in kd[1:]]; kd_names = {r[0]: r[1] for r in kd[1:]}

# ---------- child files ----------
hdr_fix = {
    'MARKET_INFO': {'Market Structue': 'Market Structure', 'Parent Child Oders': 'Parent-Child Orders',
                    'Max Generations': 'Max Parent-Child Generations', 'Max Parents per Child2': 'Max Parents per Child',
                    'Availability': 'Availability Payment', 'Utilisation': 'Utilisation Payment'},
    'DISPATCH': {'Post-Faul': 'Post-Fault'},
    'TECHNICAL': {'Ramp Rate Lower Bound [s-1]': 'Ramp Rate Lower Bound [pu/s]'},
}
hdr_note = {'Ramp Rate Lower Bound [pu/s]': '; unit interpretation (fraction of contracted MW per second) to be confirmed against NESO service terms in R-005: https://www.neso.energy/industry-information/balancing-services/frequency-response-services',
            'Availability Payment': '; column records whether an availability payment exists',
            'Utilisation Payment': '; column records whether a utilisation payment exists'}
desc_fix = {'035': ('Epiry', 'Expiry'), '063': ('minushed', 'minutes')}
for name in ['MARKET_INFO', 'TECHNICAL', 'DISPATCH', 'PARTICIPANTS', 'DESCRIPTION']:
    f = name + '.csv'
    rows = read(name); hdr = rows[0]; data = rows[1:]
    assert len(data) == 111 and hdr[0] == 'Market Name'
    for j, h in enumerate(hdr):
        if h in hdr_fix.get(name, {}):
            hdr[j] = hdr_fix[name][h]
            L(f, '(header)', h, h, hdr[j], C2 + hdr_note.get(hdr[j], ''))
    new = [['ID'] + hdr]
    L(f, '(all rows)', 'ID', '(absent)', 'ID column added as first column, back-filled by position (child rows 1-28 -> 001-028; row 29 -> 029 and 030; rows 30-111 -> 031-112)', C1)
    for i, r in enumerate(data):
        if i < 28: ids = [kd_ids[i]]
        elif i == 28: ids = ['029', '030']
        else: ids = [kd_ids[i + 1]]
        for id_ in ids:
            row = [id_] + list(r)
            if id_ == '030':
                assert all(c == '' for c in r[1:])
                L(f, '030', '(row)', '(absent)', 'new row "Capacity Market (T-4)", all other cells blank (duplicated from blank "Capacity Market" child row)', C1 + '; KEY_DATA.csv ID 030')
                row[1] = 'Capacity Market (T-4)'
            elif id_ == '029':
                row[1] = 'Capacity Market (T-1)'
                L(f, '029', 'Market Name', r[0], row[1], C1 + '; split of blank child row; KEY_DATA.csv ID 029')
            elif id_ == '025':
                row[1] = kd_names['025']
                L(f, '025', 'Market Name', r[0], row[1], C1 + '; case aligned with KEY_DATA.csv ID 025 (NESO usage)')
            elif id_ in name_fix:
                old, nw, why = name_fix[id_]
                assert row[1] == old, (f, id_, row[1]); row[1] = nw
                L(f, id_, 'Market Name', old, nw, C3 + '; ' + why)
            if name == 'MARKET_INFO':
                ph = new[0]
                pi = ph.index('Pricing Structure'); ui = ph.index('Payment Unit')
                if row[pi] in ('Pay as Clear', 'Pay-as-Cleared'):
                    L(f, id_, 'Pricing Structure', row[pi], 'Pay-as-Clear', C4 + '; one spelling for pay-as-clear pricing')
                    row[pi] = 'Pay-as-Clear'
                if '\u00a3' in row[ui]:
                    nv = row[ui].replace('\u00a3', 'GBP')
                    L(f, id_, 'Payment Unit', row[ui], nv, C4 + '; ISO 4217 currency code GBP replaces the pound sign (ASCII-safe): https://www.iso.org/iso-4217-currency-codes.html')
                    row[ui] = nv
            if name == 'DESCRIPTION' and id_ in desc_fix:
                a, b = desc_fix[id_]; si = new[0].index('Summary Paragraph')
                assert row[si].count(a) == 1
                old = row[si]; row[si] = old.replace(a, b)
                L(f, id_, 'Summary Paragraph', old, row[si], f'R-001 Change 3 note (approved {DATE}); unambiguous text typo "{a}" -> "{b}"')
            assert row[1] == kd_names[id_], (f, id_, row[1], kd_names[id_])
            new.append(row)
    write(name, new)

with open(os.path.join(ROOT, 'research', 'change_log.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, lineterminator='\r\n')
    w.writerow(['date', 'backlog_item', 'file', 'id', 'column', 'old_value', 'new_value', 'reason/source'])
    w.writerows(log)
print('change_log rows:', len(log))
