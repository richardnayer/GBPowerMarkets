# Schema metadata (datapackage.json), validator and pre-commit hook
**Backlog item:** R-010
**Status:** approved 2026-11-23 with D3 amended; D7 (installing the hook) deferred by the human. See "Human decisions" at the end.
**Date:** 2026-11-23

## Summary

R-001 Question 6 (decided 2026-11-23) settled the storage design. The CSVs are the master copy, a Frictionless
`datapackage.json` describes them, a standard-library validator checks them, and the validator runs as a git
pre-commit hook. This run built those three pieces. No CSV data file was changed.

| File | What it is |
|---|---|
| `CSV/datapackage.json` | Frictionless Data Package v2 descriptor for all 18 CSVs: 146 fields, each with a type, a `description` (this is the data dictionary) and constraints; 18 primary keys; 42 foreign keys |
| `scripts/validate.py` | Stdlib-only validator (Python 3.8+). It checks the files, the Table Schema and 11 cross-table rules, prints a report, and exits 1 on any error |
| `scripts/hooks/pre-commit` | Runs `validate.py --staged` when a commit touches `CSV/` or the validator. **Not installed** (see D7) |

**Result on today's data: PASS, 0 errors and 12 warnings.** None of the warnings is a broken value. They are known
gaps (MEC-0076), two free-text publishers, and nine sources that no row links to in a machine-readable way
(Findings 2-4). One repository-level problem was found: git stores the CSVs with LF line endings, so the CRLF rule
holds only in Windows checkouts (Finding 1, D3).

Testing: 29 mutation tests each broke one thing in a scratch copy of `CSV/`, and every one was reported by the
expected check. The hook was also tested end to end in a throwaway repository in the scratchpad: a clean index
passes; a broken staged file fails; a fix made in the working tree but not staged still fails; staging the fix
passes. The project's `.git/` was not touched.

## Decisions needed

"Approve the recommendations" is a valid answer.

| # | Decision | Recommended | Alternatives |
|---|---|---|---|
| D1 | Adopt the three files as drafted | Approve. The human commits them, with `git add --chmod=+x scripts/hooks/pre-commit` so the hook is executable on Linux/macOS | Request changes |
| D2 | `not_applicable` / `unknown`: codes or missing values? (section 2) | **Codes.** `missingValues` is `[""]` only, so a blank means not yet researched. Revisit numeric columns in Phase 3 | Declare them as `missingValues`, as the R-009 note suggested |
| D3 | Line endings in git (Finding 1) | Add a `.gitattributes` with `CSV/*.csv text eol=crlf` and `scripts/hooks/pre-commit text eol=lf`. The index already holds LF, so there is no data churn. Review it with the BOM before publication (R-019) | `CSV/*.csv -text` (store the CRLF bytes; needs `git add --renormalize CSV/`, which rewrites every line once); or relax the validator to accept LF |
| D4 | Required fields (section 1.4) | Confirm the list as drafted | Relax individual fields |
| D5 | `SOURCES.publisher` holds two names, not ORG- IDs (Finding 3) | Make it a strict foreign key: add Companies House to ORGANISATIONS, and allow a blank publisher only for `internal` sources (R-032) | Split it into `publisher_org_id` and `publisher_name`; or keep it mixed (today's rule X7) |
| D6 | Coded columns with no lookup (Finding 5) | Add small sourced lookups (R-032), consistent with "foreign keys, not enums" | Write `enum` lists into the schema for these closed internal lists |
| D7 | Install the hook | Human action, after D1: `git config core.hooksPath scripts/hooks` (undo: `git config --unset core.hooksPath`). On Linux/macOS, apply D3 first, or every CSV commit will fail the CRLF check | Run `python scripts/validate.py` by hand instead |
| D8 | Error and warning levels | As drafted: X3 (blank variant on a DSO row), X7 (publisher given as a name), X8, X9, X10 and X11 are warnings; everything else is an error. Make X9 an error once CITATIONS exists (R-023) | Promote or demote individual rules |

## Changes

### 1. `CSV/datapackage.json`

**1.1 Standard.** Frictionless Data Package v2 (`$schema` `https://datapackage.org/profiles/2.0/datapackage.json`).
Sources: https://datapackage.org/standard/data-package/, https://datapackage.org/standard/data-resource/,
https://datapackage.org/standard/table-schema/, https://datapackage.org/standard/table-dialect/.
- Each resource has `name`, `path`, `type: table`, `format: csv`, `mediatype`, `encoding: utf-8` and an explicit
  dialect with `lineTerminator: "\r\n"`.
- Resource names are lower-case (`key_data`, `lk_yesno`), as the spec recommends. They are also the table names
  for the R-018 SQLite build.
- Each schema has `fieldsMatch: exact` (same names in the same order), `missingValues: [""]`, `primaryKey` and
  `foreignKeys`.
- Self-references (`parent_org_id`, `predecessor_org_id`) omit `reference.resource`, as v2 requires.
- **Left out on purpose:** `licenses` and `version` (R-019; the licence is the human's choice). There is also no
  property for the BOM, because the spec has none. The spec's default is "UTF-8 (without BOM)", so the BOM is
  documented in the package description and enforced by the validator (R-001 Question 6: keep the BOM and review
  it before publication).

**1.2 Allowed values are foreign keys, never enums.** Every coded column has a foreign key to its `LK_*` lookup,
ORGANISATIONS or SOURCES. There is no `enum` anywhere, so a new code, for example a `system_charge` class for
BSUoS, needs only a lookup row. Coded columns also carry a snake_case `pattern`, which gives a clearer message for
casing slips (`Live`).

| Coded column(s) | Foreign key to |
|---|---|
| KEY_DATA Mechanism Class, Category, Status, Commodity, Direction, Contract Length Band, Standard Variant | the matching `lk_*` |
| KEY_DATA Market Operator | organisations.org_id |
| 13 yes/no columns (MARKET_INFO 5, DISPATCH 2, PARTICIPANTS 6) | lk_yesno |
| child-file `ID` (5 files) | key_data.ID |
| ORGANISATIONS org_type / parent_org_id, predecessor_org_id / source_id | lk_org_type / organisations (self) / sources |
| every lookup `source_id` | sources |
| LK_DSO_PRODUCT_VARIANT product_code, nearest_product_code | lk_dso_standard_product |

**1.3 IDs and patterns** (R-001 Change 1a): `MEC-[0-9]{4}`, `ORG-[0-9]{4}`, `SRC-[0-9]{4}`; lookup codes
`[a-z][a-z0-9_]*`.
- Patterns are written in XML Schema style, without `^` and `$`, as the Table Schema spec asks. XML Schema regexes
  are implicitly anchored and treat `^` and `$` as literal characters. The validator tests them with `re.fullmatch`.
- `registry_id` uses the general form `[A-Z]{2}-[A-Z0-9]{2,8}-[A-Za-z0-9]+` rather than R-009's
  `(GB-COH|FR-RCS)-...`. With the general form, the Norwegian and German register numbers that R-009 left blank
  (Nord Pool, EEX) can be added without a schema change. org-id.guide does not publish a formal grammar for its
  list codes, so the pattern is deliberately loose.

**1.4 Required fields (D4).**
- Every ID.
- KEY_DATA: Market Name, Mechanism Class and Category (100% filled today).
- Child files: Market Name.
- Lookups: code, label, definition and source_id. Labels are also unique. This keeps every published code backed
  by a source (R-009).
- ORGANISATIONS: name (unique), org_type and source_id.
- SOURCES: title, publisher, url, source_type, doc_type and accessed_date.

**1.5 The data as it is today.** These columns are typed as plain text with no foreign key. Each `description`
names the target.

| Column | Waiting for |
|---|---|
| MARKET_INFO Market Platform | LK_PLATFORM + MECHANISM_ORG_ROLE (R-020) |
| MARKET_INFO Auction Type, Pricing Structure | LK_AUCTION_TYPE, LK_PRICING_RULE (R-020) |
| MARKET_INFO Market Structure, Market Objective | R-020: lookup or drop |
| DISPATCH Dispatcher | ORG- ID or `self` (R-020, Change 10) |
| DISPATCH Dispatch Type | `dispatch_method` (Phase 3 Change 10) |
| PARTICIPANTS Aggregation | LK_AGGREGATION_LEVEL (R-020) |
| MARKET_INFO Payment Unit, Market Timing, Period Coverage | Phase 3 (Change 9); Payment Unit has no lookup planned yet |
| 7 empty MARKET_INFO columns (Overholding, Curve Orders, Loop/Curtailable/Linked/Exclusive Blocks, Exclusive Links) | Dropped in Phase 3 (Change 9). Their meaning is undocumented, so no yes/no key was assumed |
| DESCRIPTION Useful References; MARKET_INFO Notes URLs | SOURCES + CITATIONS (Change 5) |

These columns are typed as patterned text until Phase 3 can make them numeric:

| Column | Today | Pattern | Target |
|---|---|---|---|
| TECHNICAL Max. Initiation Time, Lag Upper Bound Tolerance, Ramp Time Upper Bound, Ramp Rate Lower Bound, Maximum Capacity | number or `N/A` | `(N/A\|[0-9]+(\.[0-9]+)?)` | number; `N/A` recoded under Change 7 |
| MARKET_INFO Market Period, Settlement Period [mins] | `30`, `60`, `30 / 60` | `[0-9]+( / [0-9]+)*` | integer, split per Change 9 |
| MARKET_INFO Maximum Block Size | `500 MW` | `[0-9]+(\.[0-9]+)? MW` | number in `max_block_size_mw` (Change 7) |
| LK_DSO_PRODUCT_VARIANT max_response_time_min | `2`, `15`, `not_applicable` | `([0-9]+\|not_applicable)` | integer |

These are strictly typed already:
- `number`: TECHNICAL Max Time to Full Delivery, Delivery Duration and Minimum Capacity;
- `integer`: the three MARKET_INFO parent-child limits;
- `date`: ORGANISATIONS valid_from/valid_to and SOURCES accessed_date;
- `duration` (ISO 8601): LK_CONTRACT_LENGTH_BAND min/max;
- `uri`: ORGANISATIONS url and SOURCES archive_url;
- SOURCES version_or_date: an ISO date prefix plus an optional bracketed version.

### 2. Missing values: the choice (D2)

**The conflict.** The R-009 note suggested declaring `not_applicable` and `unknown` as `missingValues`. But both
are real rows in LK_YESNO, and `not_applicable` is also a row in LK_DIRECTION. Each row has a definition and a
source, and 23 KEY_DATA Direction cells and 47 yes/no cells use them.

**Chosen approach: they stay codes. `missingValues` is `[""]` in every table.** Reasons:
1. **It keeps R-001 Change 7.** Change 7 defines three states: blank (not yet researched), `not_applicable`
   (researched; does not apply) and `unknown` (researched; no source). Any token listed in `missingValues` is read
   as null by typed readers such as frictionless-py and the R-018 SQLite build. That would merge "not yet
   researched" with "does not apply", the very distinction Change 7 created.
2. **The lookups stay valid.** As missing values, the lookups' own `code` cells would read as null and break their
   primary keys.
3. **Foreign keys check them.** In SQLite they resolve to labelled lookup rows, so a view can show "Not
   applicable".

**Phase 3, numeric columns.** Some numeric columns will need "does not apply". There are two ways:
- (a) a field-level `missingValues` (new in v2), e.g. `["", "not_applicable", "unknown"]`, with labels. This is
  standard and readable, but typed readers see null for all three.
- (b) keep the column numbers-only, and record `not_applicable` in CITATIONS with a note. This is Change 7's
  "blank with a citation note".

The validator already supports (a). Recommendation: decide when Phase 3 is designed.

### 3. `scripts/validate.py`

```
python scripts/validate.py            # working tree
python scripts/validate.py --staged   # the git index (staged copies, with this machine's EOL filters applied)
```
Exit codes: 0 means pass (warnings allowed), 1 means errors, 2 means the validator could not run (for example,
`datapackage.json` is missing or not staged).

| Check | What it checks |
|---|---|
| F1 | file present; UTF-8 BOM; valid UTF-8; CRLF only (including inside quoted cells); every row the header's width |
| F2 | header = declared fields (`fieldsMatch`) |
| F3-F4 | types and formats; `required`, `unique`, `pattern`, `enum`, min/max, length |
| F5-F6 | primary keys unique and filled; foreign keys resolve (a null is skipped, as in Frictionless; list-typed fields are checked item by item) |
| P1 | descriptor sanity, including that every foreign key targets a primary key or unique field (SQLite requires this) |
| P2 | every `*.csv` in `CSV/` is declared, so a new table cannot be added without a schema entry |
| X1 / X2 | the 6 mechanism files have the same IDs in the same order / Market Name matches key_data |
| X3 | Standard Variant only on `dso_flexibility` rows (error); a DSO row without one (warning) |
| X4 | LK_DSO_PRODUCT_VARIANT: a standard variant has `product_code` and no `nearest_product_code`; legacy and non-standard rows the reverse |
| X5 | contract bands: min < max (error); the bands join up with no gaps (warning) |
| X6 | ORGANISATIONS: valid_from <= valid_to; no self-reference or loop in parent/predecessor chains; a predecessor ends before its successor starts |
| X7 / X8 | SOURCES: url is absolute http(s) unless internal; an ORG- publisher resolves (a name is a warning) / reuse_terms blank (warning) |
| X9 | every source is reached by a foreign key (warning) |
| X10 | MEC-/ORG-/SRC- IDs mentioned in free text exist (warning) |
| X11 | a live mechanism's operator is a former name (warning) |

R-009's input "variant's `product_code` equals `Standard Product`" no longer applies: under amended D8 the
`Standard Product` column was never added. The report ends with the next free IDs (today MEC-0113, ORG-0036,
SRC-0046). The module can be imported (`load_package`, `read_table`, `cast_value`), so that R-018 reads typed
values exactly as the validator does.

### 4. `scripts/hooks/pre-commit`

POSIX `sh`. It skips commits that don't touch `CSV/`, `scripts/validate.py` or the hook itself. It finds Python 3.8+
(trying `python3`, `python`, then `py`; the Windows app-installer `python3` stub fails the version test and is
skipped). It then runs `validate.py --staged`, which reads the index, so unstaged edits cannot mask a problem. To
install it, see D7. To bypass it once: `git commit --no-verify`.

### 5. For R-018 (SQLite build)

- Use resource names as table names, and the double-quoted header names as columns until the Phase 3 snake_case
  rename.
- Type mapping: string, date and duration to TEXT; integer to INTEGER; number to REAL. `required` becomes
  NOT NULL, `primaryKey` becomes PRIMARY KEY, and each foreign key becomes REFERENCES.
- A blank cell becomes NULL; codes stay as text.
- Load order: sources, then lookups, then organisations, then key_data, then the child files. Load inside one
  transaction with `PRAGMA foreign_keys=ON` and `PRAGMA defer_foreign_keys=ON`, which covers the self-references
  in ORGANISATIONS.
- Run the validator first, and import its reader.
- Don't add list-valued `source_id` cells. SQLite cannot enforce them; multiple sources belong in CITATIONS
  (R-023). No list-valued cells exist today.

## Data findings

| # | Finding | Evidence | Proposed action |
|---|---|---|---|
| 1 | **Git stores the CSVs with LF.** CRLF exists only in this Windows working copy (`core.autocrlf` conversion). A Linux or macOS clone, or a raw GitHub download, gets LF and fails F1 | `git ls-files --eol CSV/` shows `i/lf w/crlf` for all 18 files; `git cat-file -p :CSV/LK_YESNO.csv` gives 371 bytes with no CR | D3. Per the git docs, `text eol=crlf` normalises to LF in the index and writes CRLF on checkout (https://git-scm.com/docs/gitattributes). CRLF is the RFC 4180 record separator (https://www.rfc-editor.org/rfc/rfc4180) |
| 2 | **Four sources are not linked to any row in `CSV/`:** SRC-0030, SRC-0043, SRC-0044 and SRC-0045. They are cited only by the per-row Standard Variant evidence in `research/drafts/R-009/KEY_DATA_DSO_COLUMNS.csv`. So no Standard Variant value has a machine-readable citation in `CSV/` yet | validator X9 | R-033: migrate that evidence into CITATIONS (R-023) |
| 3 | **Five sources are cited only in ORGANISATIONS `notes` text:** SRC-0004, SRC-0018, SRC-0023, SRC-0039 and SRC-0040. Separately, SOURCES `publisher` is free text for SRC-0002 (`Companies House`) and SRC-0042 (`This project`) | X9, X7 | R-033 (citations); D5 / R-032 (publisher) |
| 4 | SRC-0042 (internal) has a repository-relative `url` | X7 allows this for `internal` | Make it a full repository URL at publication (R-019) |
| 5 | **Coded columns with no lookup:** SOURCES `source_type`, `doc_type`; LK_DSO_PRODUCT_VARIANT `product_fit`, `payment_structure`, `availability_refinement`, `utilisation_instruction_timing`. Only a snake_case pattern checks them | schema | D6 / R-032 |
| 6 | MEC-0076 is `dso_flexibility` with no Standard Variant | X3 warning | Already on hold (R-008 Change 3, R-014) |
| 7 | Already tracked, and valid as blank ("not yet researched"): Status blank for MEC-0018/0030; Commodity blank for MEC-0032; Market Operator blank for MEC-0033/0034; Direction blank for 17 rows; MEC-0065 Market Objective `Nor`; names shared by MEC-0089/0090, 0092/0093/0101, 0094/0095 and 0096/0097 | profiling | R-005, R-006; Phase 3 Change 12 |

No cell value broke a type, pattern, key or cross-table rule.

## Follow-ups (not done here)

- **R-020's tables** (LK_PLATFORM, LK_PRICING_RULE, LK_AUCTION_TYPE, LK_AGGREGATION_LEVEL, LK_SETTLEMENT_TYPE,
  the role lookup and MECHANISM_ORG_ROLE) need resources in `datapackage.json`. The converted columns then need
  foreign keys in place of their text descriptions. Check P2 fails if a new CSV arrives without a schema entry, so
  this must be done in the same commit as R-020's apply step (R-031).
- **Phase 2 and 3 tables** (CITATIONS, CHANGE_LOG, SUB_MARKET, and so on) are added to the schema as they are
  created. Phase 3 renames will change `MECHANISM_CHILDREN` and rules X1/X2 in the validator.

## Confidence and caveats

- **High:** the descriptor matches the data (machine-checked). The checks are exercised by 29 mutation tests and an
  end-to-end hook test. The spec points cited above were read from datapackage.org on 2026-11-23.
- **Not tested here:** frictionless-py is not installed, so the descriptor has not been run through the official
  tooling. It uses only v2 features (`fieldsMatch`, `missingValues`, omitted self-reference resource), so a check
  with `frictionless validate CSV/datapackage.json` is worth running wherever that tool is available. The hook ran
  on Windows (Git for Windows `sh`), not on Linux or macOS.
- `duration` ordering in X5 uses nominal lengths (1 month is about 30.4 days), so it is approximate.
- Changes to `datapackage.json` are schema changes: future proposals that add tables or columns should list them.

## Human decisions (2026-11-23)

- **D1, D2, D4, D5, D6 and D8:** approved as recommended. D5 and D6 are carried out in R-032.
- **D3 (amended):** no `.gitattributes`. Validator check F1 now accepts LF or CRLF, provided the file uses
  one style throughout; mixed endings or a bare CR are still errors. Reasons:
  - CRLF is not what Excel needs; the BOM is.
  - git stores LF, so Linux/macOS checkouts and release downloads get LF whatever `.gitattributes` says.
  - The dialect still declares CRLF, the form our scripts write.

  Tested in a scratch copy: the all-LF files passed, and a mixed file failed. The hook needs no `eol=lf`
  rule either: git stores it with LF, and Git for Windows `sh` parses a CRLF copy without error.
- **D7:** the hook is not installed yet, at the human's request (R-034). To install it:
  `git config core.hooksPath scripts/hooks`.
