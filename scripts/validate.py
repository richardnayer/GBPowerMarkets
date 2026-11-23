#!/usr/bin/env python3
"""Validate the CSV files in CSV/ against CSV/datapackage.json (backlog item R-010).

Python standard library only (no frictionless-py, no pandas). Python 3.8 or later.

Usage
  python scripts/validate.py                 check the working tree
  python scripts/validate.py --staged        check the copies staged in git (used by the pre-commit hook)
  python scripts/validate.py --package PATH  check another datapackage.json
  python scripts/validate.py --max-shown N   list at most N problems per check (default 20; 0 = all)

Exit status: 0 = no errors (warnings are allowed), 1 = errors found, 2 = the validator could not run.

What is checked
  Files (per resource)
    F1  the file exists, starts with a UTF-8 byte order mark, is valid UTF-8, uses one line-ending
        style throughout (CRLF as written by our scripts, or LF as stored by git: human decision D3),
        and every row has as many cells as the header
    F2  the header matches the declared fields (schema fieldsMatch; default exact = same names, same order)
  Table Schema (Frictionless Data Package v2, https://datapackage.org/standard/table-schema/)
    F3  types and formats: string (default, uri, email, uuid), integer, number, boolean, date, time,
        datetime, year, duration, list, any
    F4  constraints: required, unique, pattern, enum, minimum, maximum, exclusiveMinimum,
        exclusiveMaximum, minLength, maxLength. Patterns are XML Schema style, so implicitly anchored:
        they are tested with re.fullmatch.
    F5  primary key: present and unique in every row
    F6  foreign keys resolve. A null (missing) value is not checked, as in Frictionless. For a
        list-typed field, every item must resolve (a project extension).
  Package
    P1  the descriptor is well formed: unique resource and field names; keys name declared fields;
        each foreign key points at a declared resource and at that resource's primary key or a unique
        field (SQLite needs this for the R-018 build); types are supported
    P2  every *.csv file in the package folder is declared as a resource
  Cross-table rules that a Table Schema cannot express (project rules; see the R-010 proposal)
    X1  the six mechanism files have the same IDs in the same order
    X2  Market Name in each child mechanism file matches key_data for the same ID
    X3  key_data Standard Variant is filled only when Mechanism Class is dso_flexibility (error);
        a dso_flexibility row without one is a warning
    X4  lk_dso_product_variant: a standard variant has product_code and no nearest_product_code;
        a legacy or non-standard product has nearest_product_code and no product_code
    X5  lk_contract_length_band: min_duration_exclusive < max_duration_inclusive (error); the bands
        should join up without gaps or overlaps (warning)
    X6  organisations: valid_from <= valid_to; no row is its own parent or predecessor, and the
        chains have no loops; a predecessor's valid_to is before its successor's valid_from
    X7  sources: url is an absolute http(s) URL unless source_type is internal; a publisher written
        as an ORG- ID must exist (a publisher given as a plain name is a warning)
    X8  sources: reuse_terms is blank for a non-internal source (warning)
    X9  every source is referenced by at least one foreign key (warning; the message says whether
        it is mentioned in free text instead)
    X10 every MEC-/ORG-/SRC- ID mentioned in a text cell (not a key column) exists (warning)
    X11 a live mechanism's Market Operator is a former name, i.e. has valid_to set (warning)
  The report ends with the next free ID for each prefixed table.

Import use (for example by the R-018 SQLite build):
  from validate import WorkingTree, load_package, read_table
  pkg = load_package(WorkingTree(), 'CSV/datapackage.json')   # dict; pkg['_dir'] is the folder
  table = read_table(WorkingTree(), pkg, resource)           # Table: header, rows, records, typed
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import subprocess
import sys
import uuid
from collections import Counter, OrderedDict, defaultdict
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repository root
DEFAULT_PACKAGE = 'CSV/datapackage.json'                              # relative to ROOT
BOM = b'\xef\xbb\xbf'
REQUIRE_BOM = True            # project convention (R-001 Question 6): every CSV starts with a BOM
SUPPORTED_TYPES = {'string', 'integer', 'number', 'boolean', 'date', 'time', 'datetime', 'year',
                   'duration', 'list', 'any'}
MECHANISM_CHILDREN = ['market_info', 'technical', 'dispatch', 'participants', 'description']
ID_TOKEN = re.compile(r'\b(MEC|ORG|SRC)-[0-9]{4}\b')


# --------------------------------------------------------------------------------------------
# Where files come from: the working tree, or the git index (staged copies)
# --------------------------------------------------------------------------------------------
class WorkingTree:
    label = 'working tree'

    def read(self, relpath):
        path = os.path.join(ROOT, relpath)
        if not os.path.isfile(path):
            return None
        with open(path, 'rb') as fh:
            return fh.read()

    def list_dir(self, reldir):
        path = os.path.join(ROOT, reldir)
        return sorted(os.listdir(path)) if os.path.isdir(path) else []


class GitIndex:
    """Staged copies, with the working-tree filters (such as end-of-line conversion) applied, so the
    result is what a checkout of the commit would give on this machine."""
    label = 'git index (staged files)'

    def __init__(self):
        out = self._git('rev-parse', '--show-toplevel')
        if out is None:
            raise RuntimeError('not inside a git repository, or git is not installed')
        self.top = out.decode('utf-8').strip()

    @staticmethod
    def _git(*args, cwd=ROOT):
        try:
            res = subprocess.run(('git',) + args, cwd=cwd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        except OSError:
            return None
        return res.stdout if res.returncode == 0 else None

    def _rel(self, relpath):
        return os.path.relpath(os.path.join(ROOT, relpath), self.top).replace(os.sep, '/')

    def read(self, relpath):
        return self._git('cat-file', '--filters', ':' + self._rel(relpath), cwd=self.top)

    def list_dir(self, reldir):
        prefix = self._rel(reldir).rstrip('/') + '/'
        out = self._git('ls-files', '-z', '--', prefix, cwd=self.top) or b''
        names = []
        for p in out.decode('utf-8').split('\0'):
            if p.startswith(prefix) and '/' not in p[len(prefix):]:
                names.append(p[len(prefix):])
        return sorted(names)


# --------------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------------
class Report:
    def __init__(self, max_shown=20):
        self.max_shown = max_shown
        self.items = []          # (level, scope, check, message)
        self.notes = OrderedDict()   # scope -> summary text, e.g. "112 rows"
        self.infos = []

    def error(self, scope, check, msg):
        self.items.append(('ERROR', scope, check, msg))

    def warn(self, scope, check, msg):
        self.items.append(('WARN', scope, check, msg))

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)

    def render(self, header_lines):
        out = list(header_lines) + ['']
        scopes = [s for s in OrderedDict.fromkeys(i[1] for i in self.items) if s not in self.notes]
        scopes += list(self.notes)
        w_scope = max([len(s) for s in scopes] + [10]) + 2
        w_note = max([len(n) for n in self.notes.values()] + [10]) + 2
        for scope in scopes:
            mine = [i for i in self.items if i[1] == scope]
            ne = sum(1 for i in mine if i[0] == 'ERROR')
            nw = len(mine) - ne
            status = 'OK' if not mine else ', '.join(
                x for x in (f'{ne} error(s)' if ne else '', f'{nw} warning(s)' if nw else '') if x)
            note = self.notes.get(scope, '')
            out.append(f'{scope:<{w_scope}}{note:<{w_note}}{status}')
            groups = OrderedDict()
            for level, _, check, msg in mine:
                groups.setdefault((level, check), []).append(msg)
            for (level, check), msgs in groups.items():
                shown = msgs if not self.max_shown else msgs[:self.max_shown]
                for m in shown:
                    out.append(f'    {level:<5} [{check}] {m}')
                if len(msgs) > len(shown):
                    out.append(f'    {level:<5} [{check}] ... and {len(msgs) - len(shown)} more')
        if self.infos:
            out.append('')
            out.extend(self.infos)
        ne, nw = self.count('ERROR'), self.count('WARN')
        out.append('')
        out.append(f'Summary: {ne} error(s), {nw} warning(s).')
        out.append('RESULT: ' + ('FAIL' if ne else 'PASS'))
        return '\n'.join(out)


# --------------------------------------------------------------------------------------------
# Type casting (Frictionless Table Schema v2 lexical forms)
# --------------------------------------------------------------------------------------------
RE_INT = re.compile(r'[+-]?[0-9]+')
RE_NUM = re.compile(r'[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]+)?|NaN|INF|-INF')
RE_DATE = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')
RE_TIME = re.compile(r'[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})?')
RE_DATETIME = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?'
                         r'(Z|[+-][0-9]{2}:[0-9]{2})?')
# XML Schema duration (PnYnMnDTnHnMnS); at least one component; T must be followed by a component
RE_DURATION = re.compile(r'-?P(?=[0-9]|T[0-9])([0-9]+Y)?([0-9]+M)?([0-9]+D)?'
                         r'(T(?=[0-9])([0-9]+H)?([0-9]+M)?([0-9]+(\.[0-9]+)?S)?)?')
RE_EMAIL = re.compile(r'[^@\s]+@[^@\s]+\.[^@\s]+')
RE_URI_SCHEME = re.compile(r'[A-Za-z][A-Za-z0-9+.\-]*:')


class CastError(ValueError):
    pass


def duration_seconds(text):
    """Approximate length of an ISO 8601 / XML Schema duration in seconds, for ordering only
    (a year is 365.2425 days and a month is a twelfth of that)."""
    m = RE_DURATION.fullmatch(text)
    if not m:
        raise CastError(f'{text!r} is not an ISO 8601 duration')
    y, mo, d, _, h, mi, s, _ = m.groups()
    day = 86400.0
    sign = -1 if text.startswith('-') else 1
    total = (int(y[:-1]) * 365.2425 * day if y else 0) + (int(mo[:-1]) * 30.436875 * day if mo else 0)
    total += (int(d[:-1]) * day if d else 0) + (int(h[:-1]) * 3600 if h else 0)
    total += (int(mi[:-1]) * 60 if mi else 0) + (float(s[:-1]) if s else 0)
    return sign * total


def _cast_scalar(ftype, fmt, raw, field):
    if ftype in ('string', 'any'):
        if ftype == 'string' and fmt == 'uri':
            if not RE_URI_SCHEME.match(raw) or any(c.isspace() for c in raw):
                raise CastError(f'{raw!r} is not a URI')
            parts = urlsplit(raw)
            if parts.scheme in ('http', 'https') and not parts.netloc:
                raise CastError(f'{raw!r} is not a URI (no host)')
        elif ftype == 'string' and fmt == 'email':
            if not RE_EMAIL.fullmatch(raw):
                raise CastError(f'{raw!r} is not an email address')
        elif ftype == 'string' and fmt == 'uuid':
            try:
                uuid.UUID(raw)
            except ValueError:
                raise CastError(f'{raw!r} is not a UUID')
        return raw
    if ftype == 'integer':
        txt = raw.replace(field['groupChar'], '') if field.get('groupChar') else raw
        if not RE_INT.fullmatch(txt):
            raise CastError(f'{raw!r} is not an integer')
        return int(txt)
    if ftype == 'number':
        txt = raw.replace(field['groupChar'], '') if field.get('groupChar') else raw
        if field.get('decimalChar', '.') != '.':
            txt = txt.replace(field['decimalChar'], '.')
        if not RE_NUM.fullmatch(txt):
            raise CastError(f'{raw!r} is not a number')
        return float(txt)
    if ftype == 'boolean':
        trues = field.get('trueValues', ['true', 'True', 'TRUE', '1'])
        falses = field.get('falseValues', ['false', 'False', 'FALSE', '0'])
        if raw in trues:
            return True
        if raw in falses:
            return False
        raise CastError(f'{raw!r} is not a boolean')
    if ftype == 'date':
        try:
            if fmt in ('default', None):
                if not RE_DATE.fullmatch(raw):
                    raise ValueError
                return datetime.date.fromisoformat(raw)
            if fmt == 'any':
                return datetime.date.fromisoformat(raw)
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            raise CastError(f'{raw!r} is not a date (YYYY-MM-DD)')
    if ftype == 'time':
        if not RE_TIME.fullmatch(raw):
            raise CastError(f'{raw!r} is not a time (HH:MM:SS)')
        try:
            return datetime.time.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            raise CastError(f'{raw!r} is not a valid time')
    if ftype == 'datetime':
        if not RE_DATETIME.fullmatch(raw):
            raise CastError(f'{raw!r} is not a datetime (YYYY-MM-DDTHH:MM:SS)')
        try:
            return datetime.datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            raise CastError(f'{raw!r} is not a valid datetime')
    if ftype == 'year':
        if not re.fullmatch(r'[0-9]{4}', raw):
            raise CastError(f'{raw!r} is not a year')
        return int(raw)
    if ftype == 'duration':
        duration_seconds(raw)
        return raw
    raise CastError(f'unsupported type {ftype!r}')


def cast_value(field, raw):
    """Cast one non-missing cell to its logical value. Raises CastError."""
    ftype = field.get('type', 'any')
    fmt = field.get('format', 'default')
    if ftype == 'list':
        items = raw.split(field.get('delimiter', ','))
        itype = field.get('itemType', 'string')
        return [_cast_scalar(itype, 'default', it, field) for it in items]
    return _cast_scalar(ftype, fmt, raw, field)


def missing_values(schema, field):
    mv = field.get('missingValues', schema.get('missingValues', ['']))
    return {m['value'] if isinstance(m, dict) else m for m in mv}


# --------------------------------------------------------------------------------------------
# Package and table loading
# --------------------------------------------------------------------------------------------
def load_package(source, relpath):
    raw = source.read(relpath)
    if raw is None:
        raise FileNotFoundError(f'{relpath} not found in the {source.label}')
    pkg = json.loads(raw.decode('utf-8-sig'))
    pkg['_dir'] = os.path.dirname(relpath)
    return pkg


class Table:
    def __init__(self, resource):
        self.resource = resource
        self.name = resource.get('name', '?')
        self.header = []
        self.rows = []         # list of (line_number, [raw cells])
        self.records = []      # list of dict: field name -> raw string
        self.typed = []        # list of dict: field name -> logical value (None when missing)
        self.ok = False        # file was found and parsed

    def key_of(self, i):
        pk = pk_fields(self.resource)
        rec = self.records[i]
        return '/'.join(rec.get(f, '') for f in pk) if pk else f'row {i + 1}'


def pk_fields(resource):
    pk = resource.get('schema', {}).get('primaryKey', [])
    return [pk] if isinstance(pk, str) else list(pk)


def read_table(source, pkg, resource, report=None):
    """Read one resource. Problems go to `report` (if given) under checks F1-F4."""
    t = Table(resource)
    scope = t.name
    schema = resource.get('schema', {})
    fields = schema.get('fields', [])
    dialect = resource.get('dialect', {})

    def err(check, msg):
        if report:
            report.error(scope, check, msg)

    relpath = os.path.join(pkg['_dir'], resource.get('path', '')).replace(os.sep, '/')
    data = source.read(relpath)
    if data is None:
        err('F1 file', f'{relpath} not found in the {source.label}')
        return t
    if REQUIRE_BOM and not data.startswith(BOM):
        err('F1 BOM', 'file does not start with a UTF-8 byte order mark')
    # Human decision D3 (2026-11-23): the dialect's CRLF is the form our scripts write, but LF is
    # also accepted, because git stores LF and Linux/macOS checkouts and release downloads get LF.
    # A file must use one style throughout; a mix, or a bare CR, is an error.
    term = dialect.get('lineTerminator', '\r\n').encode('ascii')
    if term in (b'\r\n', b'\n'):
        crlf = data.count(b'\r\n')
        bare_lf = data.count(b'\n') - crlf
        bare_cr = data.count(b'\r') - crlf
        if bare_cr:
            err('F1 line endings', f'{bare_cr} bare CR line ending(s); use CRLF or LF')
        if crlf and bare_lf:
            err('F1 line endings', f'mixed line endings ({crlf} CRLF and {bare_lf} LF); use one '
                f'style throughout the file')
        ending = b'\r\n' if crlf and not bare_lf else b'\n'
        if data and not data.endswith(ending):
            err('F1 line endings', 'last line does not end with a line ending')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        err('F1 encoding', f'not valid UTF-8 ({e})')
        return t

    reader = csv.reader(io.StringIO(text, newline=''), delimiter=dialect.get('delimiter', ','),
                        quotechar=dialect.get('quoteChar', '"'),
                        doublequote=dialect.get('doubleQuote', True), strict=True)
    try:
        all_rows = []
        for row in reader:
            all_rows.append((reader.line_num, row))
    except csv.Error as e:
        err('F1 csv', f'line {reader.line_num}: {e}')
        return t
    if not all_rows:
        err('F1 file', 'file is empty (no header)')
        return t
    t.header = all_rows[0][1]
    t.rows = all_rows[1:]

    # F2 header
    names = [f.get('name') for f in fields]
    match = schema.get('fieldsMatch', 'exact')
    if match == 'exact':
        if t.header != names:
            missing = [n for n in names if n not in t.header]
            extra = [h for h in t.header if h not in names]
            detail = []
            if missing:
                detail.append(f'declared but not in file: {missing}')
            if extra:
                detail.append(f'in file but not declared: {extra}')
            if not missing and not extra:
                detail.append('same names in a different order')
            err('F2 header', 'header does not match the declared fields (' + '; '.join(detail) + ')')
            return t
    elif match == 'equal':
        if sorted(t.header) != sorted(names) or len(set(t.header)) != len(t.header):
            err('F2 header', f'header fields {t.header} are not the declared fields {names}')
            return t
    else:
        err('F2 header', f'fieldsMatch {match!r} is not supported by this validator')
        return t

    width = len(t.header)
    for line, row in t.rows:
        if row == []:
            err('F1 csv', f'line {line}: blank line')
            continue
        if len(row) != width:
            err('F1 csv', f'line {line}: {len(row)} cells, header has {width}')
            continue
        t.records.append(dict(zip(t.header, row)))
    t.ok = True

    # F3 types, F4 constraints (per cell)
    byname = {f['name']: f for f in fields}
    lines = [ln for ln, row in t.rows if row != [] and len(row) == width]
    for i, rec in enumerate(t.records):
        typed = {}
        for name in t.header:
            field = byname[name]
            raw = rec[name]
            where = f'line {lines[i]} ({t.key_of(i)}), {name!r}'
            cons = field.get('constraints', {})
            if raw in missing_values(schema, field):
                typed[name] = None
                if cons.get('required'):
                    err('F4 required', f'{where}: value is required')
                continue
            try:
                val = cast_value(field, raw)
            except CastError as e:
                err('F3 type', f'{where}: {e} (type {field.get("type", "any")})')
                typed[name] = None
                continue
            typed[name] = val
            for problem in check_constraints(field, raw, val):
                err('F4 ' + problem[0], f'{where}: {problem[1]}')
        t.typed.append(typed)

    # F4 unique (per field)
    for field in fields:
        if field.get('constraints', {}).get('unique'):
            seen = Counter(rec[field['name']] for rec, ty in zip(t.records, t.typed)
                           if ty.get(field['name']) is not None)
            for val, n in seen.items():
                if n > 1:
                    err('F4 unique', f'{field["name"]!r}: {val!r} appears {n} times')
    return t


def check_constraints(field, raw, val):
    cons = field.get('constraints', {})
    out = []
    pat = cons.get('pattern')
    if pat is not None:
        try:
            if not re.fullmatch(pat, raw):
                out.append(('pattern', f'{raw!r} does not match the pattern {pat}'))
        except re.error as e:
            out.append(('pattern', f'bad pattern {pat!r}: {e}'))
    if 'enum' in cons:
        allowed = []
        for e in cons['enum']:
            try:
                allowed.append(cast_value(field, e) if isinstance(e, str) else e)
            except CastError:
                allowed.append(e)
        if val not in allowed:
            out.append(('enum', f'{raw!r} is not one of {cons["enum"]}'))
    for key in ('minLength', 'maxLength'):
        if key in cons:
            n = len(val) if isinstance(val, (str, list)) else len(raw)
            if (key == 'minLength' and n < cons[key]) or (key == 'maxLength' and n > cons[key]):
                out.append((key, f'length {n} breaks {key} {cons[key]}'))
    for key, test in (('minimum', lambda v, b: v >= b), ('maximum', lambda v, b: v <= b),
                      ('exclusiveMinimum', lambda v, b: v > b),
                      ('exclusiveMaximum', lambda v, b: v < b)):
        if key in cons:
            bound = cons[key]
            try:
                if field.get('type') == 'duration':
                    ok = test(duration_seconds(raw), duration_seconds(bound))
                else:
                    b = cast_value(field, bound) if isinstance(bound, str) else bound
                    ok = test(val, b)
            except (CastError, TypeError):
                out.append((key, f'cannot compare {raw!r} with {key} {bound!r}'))
                continue
            if not ok:
                out.append((key, f'{raw!r} breaks {key} {bound}'))
    return out


# --------------------------------------------------------------------------------------------
# Package-level checks
# --------------------------------------------------------------------------------------------
def check_descriptor(pkg, report):
    scope = 'package'
    resources = pkg.get('resources')
    if not isinstance(resources, list) or not resources:
        report.error(scope, 'P1 descriptor', 'resources must be a non-empty list')
        return False
    names = [r.get('name') for r in resources]
    for n, c in Counter(names).items():
        if c > 1:
            report.error(scope, 'P1 descriptor', f'resource name {n!r} is used {c} times')
    byname = {r.get('name'): r for r in resources}
    for r in resources:
        rn = r.get('name')
        if not isinstance(rn, str) or not re.fullmatch(r'[a-z0-9._\-]+', rn):
            report.error(scope, 'P1 descriptor', f'resource name {rn!r} must be lower-case letters, '
                         'digits, ".", "-" or "_"')
        path = r.get('path')
        if not isinstance(path, str) or os.path.isabs(path) or '\\' in path or \
                '..' in path.split('/'):
            report.error(scope, 'P1 descriptor', f'{rn}: path {path!r} must be a relative POSIX path '
                         'inside the package folder')
        schema = r.get('schema')
        if not isinstance(schema, dict):
            report.error(scope, 'P1 descriptor', f'{rn}: schema must be an inline object')
            continue
        fields = schema.get('fields', [])
        fnames = [f.get('name') for f in fields]
        for n, c in Counter(fnames).items():
            if c > 1:
                report.error(scope, 'P1 descriptor', f'{rn}: field {n!r} is declared {c} times')
        for f in fields:
            ftype = f.get('type', 'any')
            if ftype not in SUPPORTED_TYPES:
                report.error(scope, 'P1 descriptor', f'{rn}.{f.get("name")}: type {ftype!r} is not '
                             'supported by this validator')
            if ftype == 'list' and f.get('itemType', 'string') not in SUPPORTED_TYPES - {'list', 'any'}:
                report.error(scope, 'P1 descriptor', f'{rn}.{f.get("name")}: bad itemType')
            if 'description' not in f:
                report.warn(scope, 'P1 descriptor', f'{rn}.{f.get("name")}: no description '
                            '(the data dictionary needs one)')
        for k in pk_fields(r):
            if k not in fnames:
                report.error(scope, 'P1 descriptor', f'{rn}: primary key field {k!r} is not declared')
        for fk in schema.get('foreignKeys', []):
            local = fk.get('fields', [])
            local = [local] if isinstance(local, str) else local
            ref = fk.get('reference', {})
            target_name = ref.get('resource') or rn          # omitted or "" = self-reference
            target_fields = ref.get('fields', [])
            target_fields = [target_fields] if isinstance(target_fields, str) else target_fields
            for k in local:
                if k not in fnames:
                    report.error(scope, 'P1 descriptor', f'{rn}: foreign key field {k!r} is not declared')
            target = byname.get(target_name)
            if target is None:
                report.error(scope, 'P1 descriptor', f'{rn}: foreign key {local} points at unknown '
                             f'resource {target_name!r}')
                continue
            if len(local) != len(target_fields):
                report.error(scope, 'P1 descriptor', f'{rn}: foreign key {local} -> {target_fields}: '
                             'field counts differ')
            tfields = {f.get('name'): f for f in target.get('schema', {}).get('fields', [])}
            for k in target_fields:
                if k not in tfields:
                    report.error(scope, 'P1 descriptor', f'{rn}: foreign key target {target_name}.{k} '
                                 'is not declared')
            uniques = [pk_fields(target)] + [[n] for n, f in tfields.items()
                                             if f.get('constraints', {}).get('unique')]
            uniques += [list(u) for u in target.get('schema', {}).get('uniqueKeys', [])]
            if sorted(target_fields) not in [sorted(u) for u in uniques]:
                report.error(scope, 'P1 descriptor', f'{rn}: foreign key target {target_name}.'
                             f'{target_fields} is not a primary key or unique field')
    return True


def check_undeclared_files(source, pkg, report):
    declared = {os.path.normpath(os.path.join(pkg['_dir'], r.get('path', '')))
                for r in pkg.get('resources', [])}
    for name in source.list_dir(pkg['_dir']):
        if name.lower().endswith('.csv'):
            if os.path.normpath(os.path.join(pkg['_dir'], name)) not in declared:
                report.error('package', 'P2 undeclared file', f'{name} is in the package folder but '
                             'is not declared in datapackage.json')


def check_primary_and_foreign_keys(tables, report):
    for name, t in tables.items():
        if not t.ok:
            continue
        pk = pk_fields(t.resource)
        if pk:
            seen = defaultdict(list)
            for i, rec in enumerate(t.records):
                key = tuple(rec[k] for k in pk)
                if any(t.typed[i].get(k) is None for k in pk):
                    report.error(name, 'F5 primary key', f'row {i + 1}: primary key {pk} is blank')
                    continue
                seen[key].append(i + 1)
            for key, rows in seen.items():
                if len(rows) > 1:
                    report.error(name, 'F5 primary key', f'{"/".join(pk)} {"/".join(key)!r} appears in '
                                 f'data rows {rows}')
        schema = t.resource.get('schema', {})
        fdefs = {f['name']: f for f in schema.get('fields', [])}
        for fk in schema.get('foreignKeys', []):
            local = fk.get('fields', [])
            local = [local] if isinstance(local, str) else local
            ref = fk.get('reference', {})
            target_name = ref.get('resource') or name
            tf = ref.get('fields', [])
            tf = [tf] if isinstance(tf, str) else tf
            target = tables.get(target_name)
            if target is None or not target.ok:
                continue
            valid = {tuple(rec[k] for k in tf) for rec in target.records}
            label = f'{",".join(local)} -> {target_name}.{",".join(tf)}'
            for i, rec in enumerate(t.records):
                if any(t.typed[i].get(k) is None for k in local):
                    continue
                if len(local) == 1 and fdefs[local[0]].get('type') == 'list':
                    items = rec[local[0]].split(fdefs[local[0]].get('delimiter', ','))
                    bad = [it for it in items if (it,) not in valid]
                else:
                    key = tuple(rec[k] for k in local)
                    bad = [] if key in valid else ['/'.join(key)]
                for b in bad:
                    report.error(name, 'F6 foreign key', f'{t.key_of(i)}: {b!r} not found ({label})')


# --------------------------------------------------------------------------------------------
# Cross-table rules (X1-X11)
# --------------------------------------------------------------------------------------------
def cross_table_rules(tables, report):
    def ok(n):
        return n in tables and tables[n].ok
    scope = 'cross-table rules'

    # X1, X2: the mechanism files line up with key_data
    if ok('key_data'):
        kd = tables['key_data']
        kd_ids = [r['ID'] for r in kd.records]
        kd_names = {r['ID']: r['Market Name'] for r in kd.records}
        for child in MECHANISM_CHILDREN:
            if not ok(child):
                continue
            ids = [r['ID'] for r in tables[child].records]
            if ids != kd_ids:
                missing = [x for x in kd_ids if x not in set(ids)]
                extra = [x for x in ids if x not in set(kd_ids)]
                first = next((i for i, (a, b) in enumerate(zip(kd_ids, ids)) if a != b), None)
                detail = []
                if missing:
                    detail.append(f'missing {missing[:10]}')
                if extra:
                    detail.append(f'not in key_data {extra[:10]}')
                if not missing and not extra and first is not None:
                    detail.append(f'order differs from row {first + 1} ({ids[first]} vs {kd_ids[first]})')
                if len(ids) != len(kd_ids):
                    detail.append(f'{len(ids)} rows vs {len(kd_ids)}')
                report.error(scope, 'X1 mechanism IDs', f'{child}: IDs differ from key_data ('
                             + '; '.join(detail) + ')')
            for r in tables[child].records:
                if r['ID'] in kd_names and r.get('Market Name') != kd_names[r['ID']]:
                    report.error(scope, 'X2 market name', f'{child} {r["ID"]}: '
                                 f'{r.get("Market Name")!r} differs from key_data '
                                 f'{kd_names[r["ID"]]!r}')

        # X3 Standard Variant only on dso_flexibility rows
        for r in kd.records:
            cls, var = r.get('Mechanism Class', ''), r.get('Standard Variant', '')
            if var and cls != 'dso_flexibility':
                report.error(scope, 'X3 standard variant', f'key_data {r["ID"]}: Standard Variant '
                             f'{var!r} is set but Mechanism Class is {cls!r} (only dso_flexibility '
                             'rows may have one)')
            elif cls == 'dso_flexibility' and not var:
                report.warn(scope, 'X3 standard variant', f'key_data {r["ID"]}: dso_flexibility row '
                            'has no Standard Variant (on hold, or not yet researched?)')

        # X11 live mechanism run by a former name
        if ok('organisations'):
            ended = {o['org_id']: o['valid_to'] for o in tables['organisations'].records
                     if o.get('valid_to')}
            for r in kd.records:
                op = r.get('Market Operator', '')
                if r.get('Status') == 'live' and op in ended:
                    report.warn(scope, 'X11 former operator', f'key_data {r["ID"]}: live, but its '
                                f'Market Operator {op} is a former name (valid_to {ended[op]})')

    # X4 DSO variant: product_code vs nearest_product_code
    if ok('lk_dso_product_variant'):
        for r in tables['lk_dso_product_variant'].records:
            fit, prod, near = r.get('product_fit'), r.get('product_code'), r.get('nearest_product_code')
            if fit == 'standard' and (not prod or near):
                report.error(scope, 'X4 dso variant', f'lk_dso_product_variant {r["code"]}: a standard '
                             'variant needs product_code and no nearest_product_code')
            if fit != 'standard' and (prod or not near):
                report.error(scope, 'X4 dso variant', f'lk_dso_product_variant {r["code"]}: a '
                             f'{fit} product needs nearest_product_code and no product_code')

    # X5 contract length bands
    if ok('lk_contract_length_band'):
        bands = []
        for r in tables['lk_contract_length_band'].records:
            try:
                lo = duration_seconds(r['min_duration_exclusive'])
                hi = duration_seconds(r['max_duration_inclusive'])
            except (CastError, KeyError):
                continue     # already reported as F3
            if lo >= hi:
                report.error(scope, 'X5 contract band', f'lk_contract_length_band {r["code"]}: '
                             f'min {r["min_duration_exclusive"]} is not below max '
                             f'{r["max_duration_inclusive"]}')
            bands.append((lo, r))
        bands.sort(key=lambda b: b[0])
        for (_, a), (_, b) in zip(bands, bands[1:]):
            if a['max_duration_inclusive'] != b['min_duration_exclusive']:
                report.warn(scope, 'X5 contract band', f'lk_contract_length_band: {a["code"]} ends at '
                            f'{a["max_duration_inclusive"]} but {b["code"]} starts at '
                            f'{b["min_duration_exclusive"]} (gap or overlap)')

    # X6 organisations
    if ok('organisations'):
        orgs = {o['org_id']: o for o in tables['organisations'].records}
        for o in orgs.values():
            oid, vf, vt = o['org_id'], o.get('valid_from'), o.get('valid_to')
            if vf and vt and vf > vt:
                report.error(scope, 'X6 organisations', f'{oid}: valid_from {vf} is after valid_to {vt}')
            for col in ('parent_org_id', 'predecessor_org_id'):
                if o.get(col) == oid:
                    report.error(scope, 'X6 organisations', f'{oid}: {col} points at itself')
            pred = orgs.get(o.get('predecessor_org_id', ''))
            if pred and pred.get('valid_to') and vf and not pred['valid_to'] < vf:
                report.error(scope, 'X6 organisations', f'{oid}: starts {vf}, but its predecessor '
                             f'{pred["org_id"]} runs to {pred["valid_to"]}')
        for col in ('parent_org_id', 'predecessor_org_id'):
            loops = set()
            for start in orgs:
                seen, cur = [], start
                while cur in orgs and orgs[cur].get(col):
                    if cur in seen:
                        cycle = seen[seen.index(cur):]
                        if frozenset(cycle) not in loops:
                            loops.add(frozenset(cycle))
                            report.error(scope, 'X6 organisations', f'{col} chain loops: '
                                         + ' -> '.join(cycle + [cur]))
                        break
                    seen.append(cur)
                    cur = orgs[cur][col]

    # X7, X8 sources
    if ok('sources'):
        org_ids = {o['org_id'] for o in tables['organisations'].records} if ok('organisations') else None
        for s in tables['sources'].records:
            sid, internal = s['source_id'], s.get('source_type') == 'internal'
            url = s.get('url', '')
            parts = urlsplit(url)
            if not internal and not (parts.scheme in ('http', 'https') and parts.netloc):
                report.error(scope, 'X7 sources', f'{sid}: url {url!r} is not an absolute http(s) URL '
                             '(only internal sources may use a repository path)')
            pub = s.get('publisher', '')
            if re.fullmatch(r'ORG-[0-9]{4}', pub):
                if org_ids is not None and pub not in org_ids:
                    report.error(scope, 'X7 sources', f'{sid}: publisher {pub} is not in organisations')
            elif pub:
                report.warn(scope, 'X7 sources', f'{sid}: publisher {pub!r} is a name, not an ORG- ID')
            if not internal and not s.get('reuse_terms'):
                report.warn(scope, 'X8 reuse terms', f'{sid}: reuse_terms is blank (R-019)')

        # X9 every source is referenced by a foreign key
        used = set()
        for name, t in tables.items():
            if not t.ok:
                continue
            for fk in t.resource.get('schema', {}).get('foreignKeys', []):
                if (fk.get('reference', {}).get('resource') or name) != 'sources':
                    continue
                local = fk.get('fields', [])
                local = [local] if isinstance(local, str) else local
                for rec in t.records:
                    for k in local:
                        used.update(x for x in rec.get(k, '').split(';') if x)
        mentioned = defaultdict(set)      # source ID -> 'table.column' cells that mention it
        for name, t in tables.items():
            if t.ok:
                for rec in t.records:
                    for col, val in rec.items():
                        for m in re.finditer(r'SRC-[0-9]{4}', val):
                            if not (name == 'sources' and col == 'source_id'):
                                mentioned[m.group(0)].add(f'{name}.{col}')
        for s in tables['sources'].records:
            sid = s['source_id']
            if sid in used:
                continue
            where = sorted(mentioned.get(sid, ()))
            if where:
                report.warn(scope, 'X9 unused source', f'{sid}: no foreign key refers to it; it is '
                            f'mentioned only in free text ({", ".join(where)})')
            else:
                report.warn(scope, 'X9 unused source', f'{sid}: nothing in the package refers to it')

    # X10 ID tokens in text cells resolve
    known = set()
    for t in tables.values():
        if t.ok:
            for rec in t.records:
                for k in pk_fields(t.resource):
                    known.add(rec.get(k, ''))
    for name, t in tables.items():
        if not t.ok:
            continue
        skip = set(pk_fields(t.resource))           # keys, and foreign keys (checked by F6)
        for fk in t.resource.get('schema', {}).get('foreignKeys', []):
            f = fk.get('fields', [])
            skip.update([f] if isinstance(f, str) else f)
        for i, rec in enumerate(t.records):
            for col, val in rec.items():
                if col in skip:
                    continue
                for m in ID_TOKEN.finditer(val):
                    if m.group(0) not in known:
                        report.warn(scope, 'X10 dangling ID', f'{name} {t.key_of(i)}, {col!r}: '
                                    f'mentions {m.group(0)}, which does not exist')


def next_free_ids(tables):
    """Next free number for each ID prefix, taken from the table that owns the IDs (the first table
    whose primary key uses the prefix and is not itself a foreign key)."""
    out, done = [], set()
    for name, t in tables.items():
        pk = pk_fields(t.resource)
        if not t.ok or len(pk) != 1:
            continue
        fk_fields = {f for fk in t.resource.get('schema', {}).get('foreignKeys', [])
                     for f in ([fk.get('fields')] if isinstance(fk.get('fields'), str)
                               else fk.get('fields', []))}
        if pk[0] in fk_fields:
            continue
        nums, prefix, width = [], None, None
        for rec in t.records:
            m = re.fullmatch(r'([A-Z]{3})-([0-9]+)', rec.get(pk[0], ''))
            if m:
                prefix, width = m.group(1), len(m.group(2))
                nums.append(int(m.group(2)))
        if nums and prefix not in done:
            done.add(prefix)
            out.append(f'{prefix}-{max(nums) + 1:0{width}d} ({name})')
    return out


# --------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------
def validate(source, package_relpath, max_shown=20):
    report = Report(max_shown)
    pkg = load_package(source, package_relpath)
    if not check_descriptor(pkg, report):
        return report, pkg, {}
    check_undeclared_files(source, pkg, report)
    tables = OrderedDict()
    for res in pkg['resources']:
        t = read_table(source, pkg, res, report)
        tables[t.name] = t
        report.notes[t.name] = f'{res.get("path", "")}: {len(t.records)} rows'
    check_primary_and_foreign_keys(tables, report)
    report.notes['cross-table rules'] = 'X1-X11'
    cross_table_rules(tables, report)
    ids = next_free_ids(tables)
    if ids:
        report.infos.append('Next free IDs: ' + ', '.join(ids))
    return report, pkg, tables


def main(argv=None):
    ap = argparse.ArgumentParser(description='Validate CSV/ against CSV/datapackage.json (R-010).')
    ap.add_argument('--package', default=DEFAULT_PACKAGE,
                    help='path to datapackage.json, relative to the repository root '
                         f'(default {DEFAULT_PACKAGE})')
    ap.add_argument('--staged', action='store_true',
                    help='check the copies staged in git instead of the working tree')
    ap.add_argument('--max-shown', type=int, default=20,
                    help='problems listed per check and table (0 = all; default 20)')
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors='replace')
    except AttributeError:
        pass
    relpath = os.path.relpath(os.path.abspath(os.path.join(ROOT, args.package)), ROOT)
    relpath = relpath.replace(os.sep, '/')
    try:
        source = GitIndex() if args.staged else WorkingTree()
        report, pkg, tables = validate(source, relpath, args.max_shown)
    except (OSError, RuntimeError, ValueError) as e:     # JSON errors are ValueErrors
        print(f'validate.py: cannot run: {e}', file=sys.stderr)
        return 2
    header = ['GB Power Markets: data validation (scripts/validate.py, R-010)',
              f'Package: {relpath.replace(os.sep, "/")} ({len(pkg.get("resources", []))} resources), '
              f'read from the {source.label}']
    print(report.render(header))
    return 1 if report.count('ERROR') else 0


if __name__ == '__main__':
    sys.exit(main())
