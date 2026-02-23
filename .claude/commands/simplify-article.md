# /simplify-article — Plain-language restatement of a constitutional article

Rewrite a single constitutional article in plain, modern language — preserving
the exact legal meaning but making it readable by non-lawyers.

## Input

`$ARGUMENTS` — an article number (e.g. `55`, `31`, `235`).
If no number given, ask: "Which article number should I simplify?"

## Steps

### 1. Find the article

Map the article number to its chapter module:

| Articles | Module |
|----------|--------|
| 1–29 | `chapter_01_republic.py` |
| 30–86 | `chapter_02_rights.py` |
| 87–94 | `chapter_03_sources_of_law.py` |
| 95–125 | `chapter_04_sejm_senate.py` |
| 126–145 | `chapter_05_president.py` |
| 146–162 | `chapter_06_council_of_ministers.py` |
| 163–172 | `chapter_07_local_government.py` |
| 173–201 | `chapter_08_courts.py` |
| 202–215 | `chapter_09_oversight.py` |
| 216–227 | `chapter_10_public_finances.py` |
| 228–234 | `chapter_11_emergency.py` |
| 235–243 | `chapter_12_amendments.py` |

### 2. Gather the original text

a) Read the **bilingual docstring** from the Python function in
   `src/konstytucja/<module>.py`. This is the authoritative legal text.
b) If not implemented, read from `akn/konstytucja_rp.xml`
   (`<article eId="art_N">`).
c) If neither exists, say so and stop.

### 3. Analyse the legal language

Before rewriting, identify:
- **Archaisms** — words/phrases that have modern equivalents
- **Legalese** — unnecessarily complex constructions
- **Cross-references** — e.g. "z zastrzeżeniem ust. 2" (subject to para. 2)
- **Implicit assumptions** — things a non-lawyer wouldn't know
- **Nested conditions** — deeply nested if/then logic

### 4. Write the simplified version

Rules:
- **Preserve meaning exactly** — do NOT change what the law says, only HOW it
  says it. The simplified text must be legally equivalent.
- **Use everyday vocabulary** — replace "stanowienie prawa" with "tworzenie
  prawa" only if meaning is preserved.
- **Unpack cross-references** — instead of "z zastrzeżeniem ust. 2", briefly
  state what ust. 2 says or use "chyba że..." (unless...).
- **Active voice** — prefer "Sejm uchwala ustawy" over "Ustawy są uchwalane
  przez Sejm".
- **Short sentences** — break long provisions into numbered points where
  the original uses semicolons or comma-separated clauses.
- **Both languages** — Polish simplified text, then English simplified text.

### 5. Output format

```
## Art. <N> — <Polish title> / <English title>

### Original (Polish)
<verbatim text from docstring>

### Simplified (Polish)
<plain-language restatement>

### Original (English)
<verbatim text from docstring>

### Simplified (English)
<plain-language restatement>

### Changes made
- <bullet list of what was simplified and why>
```

End with:

> **Note:** This simplification is for readability only. It is NOT a proposed
> amendment. The original constitutional text remains the binding version.

### 6. Offer to draft as amendment

After presenting the simplification, ask the user:

> "Want me to turn this simplification into a formal amendment proposal?
> I'll create a branch, write the code, and optionally open a PR."

**Only proceed if the user confirms.** If they confirm, invoke the
`/draft-amendment` skill with the simplified text as the intention. This will:
- Create a `feat/nowelizacja-proposal-YYYY-artNN-simplification` branch
- Generate code with the simplified text in bilingual docstrings
- Run validation
- Ask about opening a PR
