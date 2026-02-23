Convert a legal amendment text into code changes for the polish-constitution-as-code repository.

## Input

The user provides constitutional amendment text (in Polish, English, or both). This can be:
- A formal "ustawa o zmianie Konstytucji" text
- An informal description of the proposed amendment
- A Dziennik Ustaw citation (e.g., "Dz.U. 2006 nr 200 poz. 1471")
- A reference to a historical proposal (e.g., "Druk nr 993 from 2006")

$ARGUMENTS

## Process

### Step 1: Parse the amendment

Identify from the input:
- Which article(s) are affected
- The year of enactment (or "proposal" if hypothetical/rejected)
- Whether it modifies existing text or adds new provisions
- The full Polish text of the amendment
- The English translation (generate if not provided)

### Step 2: Map articles to chapter modules

Use these ranges to find the correct module:
- Art. 1–29 → `chapter_01_republic.py`
- Art. 30–86 → `chapter_02_rights.py`
- Art. 87–94 → `chapter_03_sources_of_law.py`
- Art. 95–125 → `chapter_04_sejm_senate.py`
- Art. 126–145 → `chapter_05_president.py`
- Art. 146–162 → `chapter_06_council_of_ministers.py`
- Art. 163–172 → `chapter_07_local_government.py`
- Art. 173–201 → `chapter_08_courts.py`
- Art. 202–215 → `chapter_09_oversight.py`
- Art. 216–227 → `chapter_10_public_finances.py`
- Art. 228–234 → `chapter_11_emergency.py`
- Art. 235 → `chapter_12_amendments.py`

### Step 3: Read existing code

Read the current versions of:
- The chapter module to understand existing functions and imports
- `src/konstytucja/common/types.py` for existing dataclasses
- `src/konstytucja/common/errors.py` for existing exception classes
- `src/konstytucja/common/__init__.py` for the re-export list
- The test file for the chapter
- `tests/conftest.py` for existing fixtures

### Step 4: Create branch

```
feat/nowelizacja-YYYY-artNN-short-description
```

Use `nowelizacja-proposal` for hypothetical or rejected amendments.

### Step 5: Generate code changes

Follow the existing patterns exactly:

**a) Frozen dataclass in `common/types.py`** (if new domain concept needed):
```python
@dataclass(frozen=True)
class NewConcept:
    """Polish description / English description (Art. NN).

    Art. NN [zmieniony nowelizacją z DD MMMM YYYY r.]:
    [Full Polish text]

    Art. NN [amended DD Month YYYY]:
    [Full English text]
    """
    field_name: type
    optional_field: type = default  # Art. NN(M): comment
```

**b) Error class in `common/errors.py`** (if new violation type needed):
```python
class NewViolationError(ConstitutionalError):
    """Polish description — English description.

    Art. NN.
    """
```

**c) Re-exports in `common/__init__.py`**:
- Add new types to the import from `types` module
- Add new errors to the import from `errors` module
- Add both to `__all__` list in alphabetical order

**d) Validation function in chapter module**:
```python
def validate_new_rule(param: NewType) -> bool:
    """Validate against Art. NN.

    Art. NN ust. M: [Full Polish constitutional text].

    Art. NN(M): [Full English translation].

    Args:
        param: Description.

    Returns:
        True if the rule is satisfied.

    Raises:
        NewError: with details of which rule is violated.
    """
    if violation_condition:
        raise NewError(
            "Descriptive message (Polish term in parentheses)",
            article="NN(M)",
        )
    return True
```

**e) Test class in `tests/test_chapter_XX_*.py`**:
```python
class TestArtNNDescription:
    """Art. NN [year amendment]: Short description."""

    def test_valid_case(self):
        """Description of what makes this valid."""
        assert validate_new_rule(valid_input) is True

    def test_violation_specific_paragraph(self):
        """Art. NN(M): description of violation."""
        with pytest.raises(NewError, match="key phrase") as exc_info:
            validate_new_rule(invalid_input)
        assert exc_info.value.article == "NN(M)"
```

**f) AKN XML update** in `akn/konstytucja_rp.xml`:
- Add or replace the `<article eId="art_NN">` element
- Include bilingual `<p>` elements

### Step 6: Create initial commit

```
feat(chapter_XX): Encode Art. NN [amendment year] — short description
```

### Step 7: Ask user about PR

After committing, ask the user:

> "Amendment committed on branch `feat/nowelizacja-...`. Want me to push and
> open a PR?"

**Only proceed if the user confirms.** Do NOT push or create a PR without
explicit approval.

If the user confirms:

1. Push the branch: `git push -u origin <branch-name>`
2. Create a PR using the nowelizacja template at
   `.github/PULL_REQUEST_TEMPLATE/nowelizacja.md`:
   - Fill in the template fields (article number, legal reference, Polish/English
     text from docstrings, before/after table, code changes checklist, validation
     results)
   - Use `gh pr create --title "..." --body "..."` with the filled template
3. Return the PR URL to the user

If the user declines, just confirm the branch is ready for later.

## Mandatory Rules

- ALL dataclasses MUST be `frozen=True`
- ALL vote math MUST use integer arithmetic (`votes_for * 3 >= total * 2`, never float division)
- ALL financial math MUST use `Decimal`
- ALL docstrings MUST be bilingual: Polish text first, then English translation
- ALL error raises MUST include `article=` parameter
- Re-export ALL new public symbols through `common/__init__.py` in alphabetical order
- Follow ruff config: line-length 100, target py312, allow RUF002/RUF003 for Unicode
- Every test must verify both the return value AND the `article` field on exceptions
