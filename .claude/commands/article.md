# /article — Look up a constitutional article

Given an article number, display everything the codebase knows about it:
legal text, Python implementation, tests, types, errors, and AKN XML status.

## Input

The user provides an article number, e.g. `/article 55` or `/article 38`.
Parse the number from `$ARGUMENTS`. If no number given, ask for one.

## Steps

### 1. Map article to chapter module

Use this table:

| Articles | Chapter | Module |
|----------|---------|--------|
| 1–29 | I: Rzeczpospolita | `chapter_01_republic.py` |
| 30–86 | II: Wolności, prawa i obowiązki | `chapter_02_rights.py` |
| 87–94 | III: Źródła prawa | `chapter_03_sources_of_law.py` |
| 95–125 | IV: Sejm i Senat | `chapter_04_sejm_senate.py` |
| 126–145 | V: Prezydent | `chapter_05_president.py` |
| 146–162 | VI: Rada Ministrów | `chapter_06_council_of_ministers.py` |
| 163–172 | VII: Samorząd terytorialny | `chapter_07_local_government.py` |
| 173–201 | VIII: Sądy i Trybunały | `chapter_08_courts.py` |
| 202–215 | IX: Organy kontroli | `chapter_09_oversight.py` |
| 216–227 | X: Finanse publiczne | `chapter_10_public_finances.py` |
| 228–234 | XI: Stany nadzwyczajne | `chapter_11_emergency.py` |
| 235–243 | XII: Zmiana Konstytucji | `chapter_12_amendments.py` |

Also check `legislative_process.py` for Art. 118–122 references.

### 2. Find the implementation

Search for the article number in the chapter module:
- `grep -n 'article="<N>' src/konstytucja/<module>` — find raise statements
- `grep -n 'Art. <N>' src/konstytucja/<module>` — find docstring references
- Identify the function(s) that implement this article

### 3. Extract legal text

Read the function's docstring. Extract:
- **Polish text** (appears first, after "Art. N ust. ..." or "Art. N:")
- **English text** (appears after the Polish block)
- Note any amendment references (nowelizacja dates, Druk numbers)

### 4. Find types and errors

Search for the article number in:
- `src/konstytucja/common/types.py` — related dataclass(es)
- `src/konstytucja/common/errors.py` — related error class(es)

### 5. Find tests

Search in the matching test file:
- `grep -n 'Art.*<N>\|art.*<N>\|article.*<N>' tests/test_<module>.py`
- Count test methods in the relevant test class
- List test names

### 6. Check AKN XML

Search `akn/konstytucja_rp.xml` for `eId="art_<N>"`:
- If present: show the XML element (or confirm it exists with paragraph count)
- If absent: note it as "not yet in AKN XML"

## Output format

```
## Art. <N> — <Polish title> / <English title>

### Legal text
**Polish:** <full text from docstring>
**English:** <full text from docstring>
[Amendment: <reference if any>]

### Implementation
**Module:** `src/konstytucja/<module>.py`
**Function:** `<function_name>()` (lines <start>–<end>)
**Returns:** `True` on success
**Raises:** `<ErrorClass>` with `article="<N>"` on violation

### Types
- `<DataclassName>` — <one-line description>

### Tests
**File:** `tests/test_<module>.py`
**Class:** `Test<ClassName>` (<N> tests)
- `test_<name>` — <docstring first line>
- ...

### AKN XML
<Status: present with N paragraphs / not yet added>
```
