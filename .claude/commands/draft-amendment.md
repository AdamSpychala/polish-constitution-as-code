# /draft-amendment — Draft an amendment from a policy intention

The user describes what they want to achieve (a policy goal or intention), and
this skill reviews the entire constitution to identify which articles need
changing, checks for overlaps and conflicts, and produces both the executable
code changes and the formal legal amendment text.

## Input

`$ARGUMENTS` — a natural-language description of the intended change, in Polish
or English. Examples:

- "Lower the voting age to 16"
- "Add a right to clean environment"
- "Remove parliamentary immunity for corruption offences"
- "Zmienić kadencję prezydenta na 4 lata"

If no argument given, ask the user to describe their intention.

## Process

### Step 1: Understand the intention

Parse the user's description and identify:
- **The policy goal** — what outcome do they want?
- **The legal mechanism** — what constitutional concept(s) does this touch?
  (rights, powers, procedures, institutions, prohibitions, etc.)
- **Scope** — is this a narrow change (one article) or structural (multiple
  chapters)?

### Step 2: Full constitutional review

Search the ENTIRE codebase for related provisions. This is the critical step
that prevents conflicts and finds overlaps.

a) **Keyword search** across all chapter modules and types:
   ```
   grep -rn '<relevant terms>' src/konstytucja/
   ```

b) **Article reference search** — check the AKN XML for all articles that
   mention related concepts:
   ```
   grep -i '<relevant terms>' akn/konstytucja_rp.xml
   ```

c) **Cross-reference analysis** — for each article found, check if it
   references other articles (look for "ust.", "art.", "w związku z",
   "z zastrzeżeniem", "o którym mowa w"). Follow the chain.

d) **Type/error analysis** — search `common/types.py` and `common/errors.py`
   for related domain concepts.

e) **Test analysis** — check test files for existing test scenarios that would
   be affected by the change.

### Step 3: Impact report

Before writing any code, present the user with an impact analysis:

```
## Impact Analysis: <short title>

### Articles directly affected
| Article | Current provision | Proposed change |
|---------|------------------|-----------------|
| Art. N  | <summary>        | <what changes>  |

### Articles with overlaps or conflicts
| Article | Overlap/conflict | Resolution |
|---------|-----------------|------------|
| Art. M  | <description>   | <how to handle> |

### Cross-references to update
- Art. X references Art. N — <needs update? yes/no>

### Transitional provisions needed?
<yes/no and why>

### Potential unintended consequences
- <bullet list>
```

Ask the user to confirm the scope before proceeding. If the user has already
confirmed or the scope is obvious, proceed directly.

### Step 4: Determine the change set

For each affected article, decide:
- **Modify** — change existing text (most common)
- **Add** — add new paragraph or new article
- **Repeal** — remove a provision (rare, mark as repealed, don't delete code)

### Step 5: Generate code changes

For EACH affected article, follow the standard 6-file pattern from
`/text-to-amendment`:

a) **Frozen dataclass** in `common/types.py` (if new domain concept needed)
b) **Error class** in `common/errors.py` (if new violation type needed)
c) **Re-exports** in `common/__init__.py`
d) **Validation function** in the appropriate chapter module, with bilingual
   docstring containing the PROPOSED text (clearly marked as proposed)
e) **Tests** in the test file — valid cases + violation cases
f) **AKN XML** update in `akn/konstytucja_rp.xml`

If MULTIPLE articles are affected, handle them in article-number order.

### Step 6: Generate formal amendment text

After all code is written, produce the formal legislative text:

```
USTAWA
z dnia ... r.
o zmianie Konstytucji Rzeczypospolitej Polskiej

Art. 1.
W Konstytucji Rzeczypospolitej Polskiej z dnia 2 kwietnia 1997 r.
(Dz.U. Nr 78, poz. 483, z późn. zm.) wprowadza się następujące zmiany:

1) art. N otrzymuje brzmienie:
   "Art. N. <new text>";

2) w art. M ust. P otrzymuje brzmienie:
   "<new text>";

[if transitional provisions needed]
Art. 2.
<transitional provisions>

Art. [last].
Ustawa wchodzi w życie po upływie ... od dnia ogłoszenia.
```

Then the English translation:

```
ACT
of ... [date]
amending the Constitution of the Republic of Poland

Article 1.
The following amendments shall be made to the Constitution of the Republic
of Poland of 2 April 1997 (Journal of Laws No. 78, item 483, as amended):

1) Article N shall read as follows:
   "Article N. <new text>";
...
```

### Step 7: Create branch and commit

Branch name:
```
feat/nowelizacja-proposal-YYYY-artNN-short-description
```

Use the CURRENT year. Use `proposal` since this is a user-drafted amendment.
If multiple articles are affected, use the lowest article number.

Commit message:
```
feat(chapter_XX): Draft amendment — <short description>

Affects: Art. N, Art. M, Art. P
Intent: <one-line summary of policy goal>
```

### Step 8: Run validation

Execute `/validate-amendment` checks:
- `uv run pytest -v` — all tests pass
- `uv run ruff check src tests` — clean
- `uv run mypy src` — clean
- Every raise has `article=` parameter
- All docstrings are bilingual
- All new types are frozen

### Step 9: Ask user about PR

After validation passes, ask the user:

> "Amendment drafted and validated on branch `feat/nowelizacja-proposal-...`.
> Want me to push and open a PR?"

**Only proceed if the user confirms.** Do NOT push or create a PR without
explicit approval.

If the user confirms:

1. Push the branch: `git push -u origin <branch-name>`
2. Create a PR using the nowelizacja template at
   `.github/PULL_REQUEST_TEMPLATE/nowelizacja.md`:
   - Fill in all template fields:
     - Article(s) affected, date, Dz.U. citation (or "Proposed — YYYY")
     - Polish and English text from docstrings (in collapsible sections)
     - Before/after comparison table
     - Code changes checklist (mark completed items)
     - Validation results (mark passing checks)
     - Scholarly notes: include the impact analysis from Step 3
   - Use `gh pr create --title "..." --body "..."` with the filled template
3. Return the PR URL to the user

If the user declines, confirm the branch is ready and remind them they can
push and create a PR later.

## Mandatory Rules

- ALWAYS review the entire constitution before writing code. Missed overlaps
  create contradictions.
- ALWAYS present the impact analysis before coding (unless scope is trivial).
- Mark all proposed text clearly — in docstrings use:
  `[projekt nowelizacji — YYYY]` / `[proposed amendment — YYYY]`
- If the change would require a referendum (touches Chapter I, II, or XII per
  Art. 235(6)), note this explicitly in the output.
- Integer arithmetic for votes, Decimal for money, frozen dataclasses — all
  standard project rules apply.
- If modifying an EXISTING function, preserve the original text in a comment
  or docstring section labeled "Previous version" for traceability.
