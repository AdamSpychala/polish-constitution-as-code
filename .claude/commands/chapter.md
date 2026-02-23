# /chapter — Overview of a constitutional chapter

Given a chapter number (or name), show all implemented articles, test coverage,
and what's missing.

## Input

The user provides a chapter identifier, e.g. `/chapter 2`, `/chapter II`,
`/chapter rights`, or `/chapter Sejm`.
Parse from `$ARGUMENTS`. If no input given, list all chapters with article counts.

## Chapter mapping

| # | Roman | Name (PL) | Name (EN) | Articles | Module | Test file |
|---|-------|-----------|-----------|----------|--------|-----------|
| 1 | I | Rzeczpospolita | The Republic | 1–29 | `chapter_01_republic.py` | `test_chapter_01_republic.py` |
| 2 | II | Wolności, prawa i obowiązki | Rights and Freedoms | 30–86 | `chapter_02_rights.py` | `test_chapter_02_rights.py` |
| 3 | III | Źródła prawa | Sources of Law | 87–94 | `chapter_03_sources_of_law.py` | `test_chapter_03_sources_of_law.py` |
| 4 | IV | Sejm i Senat | Sejm and Senate | 95–125 | `chapter_04_sejm_senate.py` | `test_chapter_04_sejm_senate.py` |
| 5 | V | Prezydent | The President | 126–145 | `chapter_05_president.py` | `test_chapter_05_president.py` |
| 6 | VI | Rada Ministrów | Council of Ministers | 146–162 | `chapter_06_council_of_ministers.py` | `test_chapter_06_council_of_ministers.py` |
| 7 | VII | Samorząd terytorialny | Local Government | 163–172 | `chapter_07_local_government.py` | `test_chapter_07_local_government.py` |
| 8 | VIII | Sądy i Trybunały | Courts and Tribunals | 173–201 | `chapter_08_courts.py` | `test_chapter_08_courts.py` |
| 9 | IX | Organy kontroli | Oversight Organs | 202–215 | `chapter_09_oversight.py` | `test_chapter_09_oversight.py` |
| 10 | X | Finanse publiczne | Public Finances | 216–227 | `chapter_10_public_finances.py` | `test_chapter_10_public_finances.py` |
| 11 | XI | Stany nadzwyczajne | States of Emergency | 228–234 | `chapter_11_emergency.py` | `test_chapter_11_emergency.py` |
| 12 | XII | Zmiana Konstytucji | Amending the Constitution | 235–243 | `chapter_12_amendments.py` | `test_chapter_12_amendments.py` |

Also: `legislative_process.py` / `test_legislative_process.py` covers Art. 118–122 procedural logic.

## Steps

### 1. Identify the chapter

Match user input against chapter number (arabic or roman), Polish name, or English name.
If ambiguous, show candidates and ask.

### 2. Read the module

Read `src/konstytucja/<module>.py`:
- List all public functions (those without `_` prefix)
- For each function, extract: name, article reference(s), one-line summary from docstring
- Note any amendment references (nowelizacja, proposed changes)

### 3. Count articles

From the `article="..."` parameters in raise statements and docstring `Art. N` references,
build a list of articles implemented in this module.

Compare against the chapter's full article range to identify gaps.

### 4. Read the test file

Read `tests/test_<module>.py`:
- List all test classes with their article references
- Count test methods per class
- Total test count

### 5. Check AKN XML coverage

Search `akn/konstytucja_rp.xml` for articles in this chapter's range.
List which are present and which are missing.

## Output format

```
## Chapter <N> (<Roman>): <Polish name> / <English name>
**Module:** `src/konstytucja/<module>.py`
**Tests:** `tests/test_<module>.py`
**Articles:** <range> (<implemented>/<total> implemented)

### Functions
| Function | Article(s) | Description |
|----------|-----------|-------------|
| `<name>()` | Art. <N> | <one-line from docstring> |
| ... | ... | ... |

### Test coverage
| Test class | Article | Tests |
|------------|---------|-------|
| `Test<Name>` | Art. <N> | <count> |
| ... | ... | ... |
**Total:** <N> tests

### AKN XML
| Article | Status |
|---------|--------|
| Art. <N> | Present (N paragraphs) / Missing |
| ... | ... |

### Gaps
- Art. <N>: not yet implemented
- Art. <N>: implemented but no AKN XML entry
```

If no chapter specified, show the summary table:

```
## Constitution Overview

| Chapter | Articles | Functions | Tests | AKN |
|---------|----------|-----------|-------|-----|
| I: Rzeczpospolita | 1–29 | <N> | <N> | <N>/<total> |
| ... | ... | ... | ... | ... |
```
