"""Draft values for the proposed KEY_DATA columns Standard Product / Standard Variant (R-008 Change 2, R-009 codes)."""
import csv, io, os, sys
ROOT = sys.argv[1]
OUT = os.path.join(ROOT, 'research', 'drafts', 'R-009')
SRC = {'nged': 'SRC-0011', 'npg': 'SRC-0012', 'spen': 'SRC-0013', 'spenw': 'SRC-0014', 'ssen': 'SRC-0015',
       'ukpn': 'SRC-0016', 'ena22': 'SRC-0029', 'fmr': 'SRC-0026'}
V = {  # id: (product, variant, source_ids, locator)
 67: ('', 'legacy_dynamic', 'SRC-0043', 'PDF p.5-6: legacy ENA product; product definition in SRC-0029 p.9'),
 68: ('ou', 'ou_15', 'SRC-0011', 'PDF p.6, p.15 (OU_15)'),
 69: ('', 'legacy_restore', 'SRC-0043', 'PDF p.5-6: legacy ENA product; product definition in SRC-0029 p.9'),
 70: ('sa_ou', 'sa_ou_da', 'SRC-0011', 'PDF p.6, p.15 (SAOU_DA)'),
 71: ('', 'legacy_secure', 'SRC-0043', 'PDF p.5-6: legacy ENA product; product definition in SRC-0029 p.9'),
 72: ('su', 'su', 'SRC-0011', 'PDF p.15'), 73: ('su', 'su', 'SRC-0011', 'PDF p.15'), 74: ('su', 'su', 'SRC-0011', 'PDF p.6; code SU_LV not found (R-008)'),
 75: ('su', 'su', 'SRC-0012', 'Figure 2, PDF p.16 (Sub-Market 1)'),
 76: ('', '', '', 'HOLD: R-008 Change 3 on hold; su if renamed to Sub-Market 2, sa_ou / sa_ou_wa if kept as labelled'),
 77: ('sa_ou', 'sa_ou_wa', 'SRC-0012', 'PDF p.11, p.16 (Sub-Market 3)'), 78: ('sa_ou', 'sa_ou_wa', 'SRC-0012', 'PDF p.16 (Sub-Market 4)'),
 79: ('sa_ou', 'sa_ou_wa', 'SRC-0012', 'PDF p.16 (Sub-Market 5)'),
 80: ('', 'npg_flexadvance', 'SRC-0012', 'PDF p.3 fn 1, p.9, p.16 (Sub-Market 6)'), 81: ('', 'npg_flexadvance', 'SRC-0012', 'PDF p.16 (Sub-Market 7)'),
 82: ('sa_ou', 'sa_ou_15', 'SRC-0012', 'PDF p.14 Table 7, p.21 (Sub-Market 8)'), 83: ('sa_ou', 'sa_ou_15', 'SRC-0012', 'PDF p.14, p.21; flagged as window/duplicate of MEC-0082'),
 84: ('sa_ou', 'sa_ou_15', 'SRC-0012', 'PDF p.14, p.21; flagged as window/duplicate of MEC-0082'),
 85: ('su', 'su', 'SRC-0044', 'PDF p.6'), 86: ('sa_ou', 'sa_ou_wa', 'SRC-0045', 'Section 6.1 and Table 1; also SRC-0044 PDF p.6; standard variant since FLX CP003 (SRC-0030)'),
 87: ('su', 'su', 'SRC-0044', 'PDF p.6-7'), 88: ('su', 'su', 'SRC-0045', 'Table 2 (LV SU month ahead)'),
 89: ('ou', 'ou_15', 'SRC-0013', 'PDF p.8'), 90: ('ou', 'ou_15', 'SRC-0013', 'PDF p.8'), 91: ('sa_ou', 'sa_ou_da', 'SRC-0013', 'PDF p.7'),
 92: ('su', 'su', 'SRC-0013', 'PDF p.7'), 93: ('su', 'su', 'SRC-0013', 'PDF p.7'),
 94: ('ou', 'ou_15', 'SRC-0014', 'PDF p.10-11'), 95: ('ou', 'ou_15', 'SRC-0014', 'PDF p.10-11'), 96: ('ou', 'ou_2', 'SRC-0014', 'PDF p.10-11'),
 97: ('ou', 'ou_2', 'SRC-0014', 'PDF p.10-11'), 98: ('pr', 'pr', 'SRC-0014', 'PDF p.10-11'), 99: ('pr', 'pr', 'SRC-0014', 'PDF p.10-11'),
 100: ('su', 'su', 'SRC-0014', 'PDF p.10-11'), 101: ('su', 'su', 'SRC-0014', 'PDF p.10-11'), 102: ('va_ou', 'va_ou_15', 'SRC-0014', 'PDF p.11'),
 103: ('va_ou', 'va_ou_2', 'SRC-0014', 'PDF p.11; FMR-PD Table 5 VA OU-2 (SRC-0026)'),
 104: ('ou', 'ou_2', 'SRC-0015', 'PDF p.6'), 105: ('sa_ou', 'sa_ou_da', 'SRC-0015', 'PDF p.4, p.6'), 106: ('sa_ou', 'sa_ou_da', 'SRC-0015', 'PDF p.4'),
 107: ('su', 'su', 'SRC-0015', 'PDF p.4'), 108: ('su', 'su', 'SRC-0015', 'PDF p.4'), 109: ('va_ou', 'va_ou_wa', 'SRC-0015', 'PDF p.4, p.6'),
 110: ('sa_ou', 'sa_ou_da', 'SRC-0016', 'PDF p.6'), 111: ('su', 'su', 'SRC-0016', 'PDF p.6'), 112: ('su', 'su', 'SRC-0016', 'PDF p.6'),
}
def load(p):
    with open(p, encoding='utf-8-sig', newline='') as fh: return list(csv.reader(fh))
kd = load(os.path.join(ROOT, 'CSV', 'KEY_DATA.csv'))
variants = {r[0]: r for r in load(os.path.join(OUT, 'LK_DSO_PRODUCT_VARIANT.csv'))[1:]}
products = {r[0] for r in load(os.path.join(OUT, 'LK_DSO_STANDARD_PRODUCT.csv'))[1:]}
srcs = {r[0] for r in load(os.path.join(OUT, 'SOURCES.csv'))[1:]}
rows = [['ID', 'Market Name', 'Market Operator', 'Standard Product', 'Standard Variant', 'product_fit (from lookup)', 'source_id', 'locator']]
dso = [r for r in kd[1:] if r[2] == 'DSO Flex Market']
assert sorted(int(r[0][4:]) for r in dso) == sorted(V), 'DSO row set differs'
for r in dso:
    p, v, s, loc = V[int(r[0][4:])]
    if v:
        assert v in variants and (p == '' or p in products) and s in srcs, r[0]
        assert variants[v][5] == p, (r[0], 'product does not match variant lookup')
    fit = variants[v][6] if v else 'hold'
    rows.append([r[0], r[1], r[3], p, v, fit, s, loc])
out = io.StringIO(newline='')
csv.writer(out, lineterminator='\r\n').writerows(rows)
with open(os.path.join(OUT, 'KEY_DATA_DSO_COLUMNS.csv'), 'wb') as fh:
    fh.write(('\ufeff' + out.getvalue()).encode('utf-8'))
from collections import Counter
print(len(rows) - 1, Counter(x[4] for x in rows[1:]), Counter(x[5] for x in rows[1:]))
