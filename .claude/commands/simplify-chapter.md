# /simplify-chapter — Plain-language restatement of an entire chapter

Rewrite all implemented articles in a constitutional chapter in plain, modern
language — preserving exact legal meaning while making it accessible.

## Input

`$ARGUMENTS` — a chapter number (Arabic: `1`–`12`, or Roman: `I`–`XII`).
If no number given, ask: "Which chapter should I simplify? (1–12)"

## Steps

### 1. Map the chapter

| Input | Chapter | Articles | Module |
|-------|---------|----------|--------|
| 1 / I | Rzeczpospolita | 1–29 | `chapter_01_republic.py` |
| 2 / II | Wolności, prawa i obowiązki | 30–86 | `chapter_02_rights.py` |
| 3 / III | Źródła prawa | 87–94 | `chapter_03_sources_of_law.py` |
| 4 / IV | Sejm i Senat | 95–125 | `chapter_04_sejm_senate.py` |
| 5 / V | Prezydent | 126–145 | `chapter_05_president.py` |
| 6 / VI | Rada Ministrów | 146–162 | `chapter_06_council_of_ministers.py` |
| 7 / VII | Samorząd terytorialny | 163–172 | `chapter_07_local_government.py` |
| 8 / VIII | Sądy i Trybunały | 173–201 | `chapter_08_courts.py` |
| 9 / IX | Organy kontroli | 202–215 | `chapter_09_oversight.py` |
| 10 / X | Finanse publiczne | 216–227 | `chapter_10_public_finances.py` |
| 11 / XI | Stany nadzwyczajne | 228–234 | `chapter_11_emergency.py` |
| 12 / XII | Zmiana Konstytucji | 235–243 | `chapter_12_amendments.py` |

### 2. Find implemented articles

Read `src/konstytucja/<module>.py` and identify all functions that reference
articles via `article=` in raises or `Art. N` in docstrings.

Also check `akn/konstytucja_rp.xml` for articles in this chapter's range
that may have text but no code implementation yet.

List which articles are implemented and which are not.

### 3. Simplify each implemented article

For each article found, apply the same process as `/simplify-article`:

a) Extract the original bilingual text from the docstring
b) Identify archaisms, legalese, cross-references, implicit assumptions
c) Write a plain-language restatement in both Polish and English
d) Preserve exact legal meaning

### 4. Output format

```
## Rozdział <N> / Chapter <N>: <Polish name> / <English name>

Articles implemented: <list>
Articles not yet in code: <list>

---

### Art. <N1> — <title>

**Original (Polish):** <text>
**Simplified (Polish):** <text>

**Original (English):** <text>
**Simplified (English):** <text>

**Changes:** <what was simplified>

---

### Art. <N2> — <title>
...
```

End with:

> **Note:** This simplification is for readability only. It is NOT a proposed
> amendment. The original constitutional text remains the binding version.
> Articles not yet implemented in code are skipped.

### 5. Offer to draft as amendment

After presenting all simplifications, ask the user:

> "Want me to turn any of these simplifications into formal amendment
> proposals? Specify which article(s), or say 'all' for the whole chapter."

**Only proceed if the user confirms.** If they confirm, invoke the
`/draft-amendment` skill for each selected article with the simplified text
as the intention. Each will:
- Create a branch, generate code, run validation, and ask about a PR
- If multiple articles are selected, group them in a single branch as one
  amendment act (matching how real omnibus amendments work)
