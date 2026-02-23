Read the git diff of the current branch against `main` and generate formal legal amendment text based on the code changes.

## Process

1. **Discover the diff.** Run `git diff main..HEAD --stat` and `git diff main..HEAD` to identify all changed files and their contents.

2. **Parse article references.** Look for these patterns in the diff:
   - `article="NN"` parameters in `raise XxxError(...)` calls
   - `Art. NN` references in docstrings and comments
   - Branch name pattern `feat/nowelizacja-YYYY-artNN-*` for metadata (year, article number)
   - New dataclass docstrings in `common/types.py` that cite articles

3. **Read full context.** For each changed function in `src/konstytucja/chapter_*.py`, read the complete function including its full bilingual docstring. The docstring IS the constitutional text — extract it verbatim.

4. **Read the pre-amendment version.** Check `akn/konstytucja_rp.xml` for the original article text (before the amendment). If the article doesn't exist in the XML yet, note that this amendment adds a new provision.

5. **Generate three outputs:**

### Output 1: Formal Polish Amendment Text

Use the standard Polish legislative drafting format ("ustawa o zmianie Konstytucji"):

```
USTAWA
z dnia [date from branch name or docstring] r.
o zmianie Konstytucji Rzeczypospolitej Polskiej

(Dz.U. [citation if found in docstrings])

Art. 1.
W Konstytucji Rzeczypospolitej Polskiej z dnia 2 kwietnia 1997 r.
(Dz.U. Nr 78, poz. 483, z późn. zm.) art. [N] otrzymuje brzmienie:

"Art. [N].
[full text extracted from docstrings — Polish paragraphs only]"

Art. 2.
Ustawa wchodzi w życie po upływie 30 dni od dnia ogłoszenia.
```

- For multi-paragraph articles, use "ust." numbering (ust. 1, ust. 2, etc.)
- For points within paragraphs, use "pkt" numbering (pkt 1, pkt 2, etc.)
- If adding a new article (not modifying), use "dodaje się art. [N] w brzmieniu:"
- If modifying specific paragraphs, use "art. [N] ust. [M] otrzymuje brzmienie:"

### Output 2: English Translation

Produce a parallel English translation following the same structure, using the English text from the bilingual docstrings.

### Output 3: Akoma Ntoso XML Fragment

Generate an `<article>` element in Akoma Ntoso 3.0 format matching the schema in `akn/konstytucja_rp.xml`:

```xml
<article eId="art_NN">
  <num>Art. NN.</num>
  <paragraph eId="art_NN__para_1">
    <num>1.</num>
    <content>
      <p>[Polish text]</p>
      <p xml:lang="en">[English text]</p>
    </content>
  </paragraph>
  <!-- additional paragraphs -->
</article>
```

- Use `eId="art_NN"` for articles, `eId="art_NN__para_M"` for paragraphs
- Include both `<p>` (Polish, default) and `<p xml:lang="en">` (English)
- For single-paragraph articles, use `<content>` directly instead of `<paragraph>`

## Rules

- The Polish text MUST come from the docstrings in the code — those contain the authoritative constitutional text.
- If the docstring cites a Dziennik Ustaw reference (e.g., "Dz.U. 2006 nr 200 poz. 1471"), include it.
- If the branch name contains a year, use that as the amendment year.
- Mark any interpretive choices with `[NOTA INTERPRETACYJNA / INTERPRETIVE NOTE: ...]`.
- If the diff modifies an existing function's docstring (changing existing constitutional text), show both "before" (from the XML or main branch) and "after" versions.

$ARGUMENTS
