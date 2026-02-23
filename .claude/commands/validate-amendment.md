Validate the current branch's constitutional amendment against codebase conventions and constitutional accuracy requirements.

## Steps

### 1. Identify the amendment scope

- Run `git diff main..HEAD --stat` to list changed files
- Parse the branch name for article number and year: `feat/nowelizacja-YYYY-artNN-*`
- Read the changed files to understand what's being amended

### 2. Check file completeness

Verify ALL expected files are present in the diff. Report PASS/FAIL for each:

| Required File | What to Check |
|---------------|---------------|
| `src/konstytucja/common/types.py` | New/modified dataclass with `frozen=True` |
| `src/konstytucja/common/errors.py` | New error class inheriting `ConstitutionalError` (if needed) |
| `src/konstytucja/common/__init__.py` | All new symbols re-exported and in `__all__` |
| `src/konstytucja/chapter_XX_*.py` | New/modified validation function |
| `tests/test_chapter_XX_*.py` | New test class with valid + violation cases |

Optional (report if missing but don't fail):
| `akn/konstytucja_rp.xml` | Article XML updated |
| `tests/conftest.py` | Shared fixtures if needed |

### 3. Validate code patterns

For each changed file, check:

**common/types.py:**
- [ ] New dataclass has `@dataclass(frozen=True)`
- [ ] Docstring is bilingual (Polish first, then English)
- [ ] Docstring cites article number(s) with "Art. NN"
- [ ] Fields have comments referencing article paragraphs

**common/errors.py:**
- [ ] New error class inherits from `ConstitutionalError`
- [ ] Docstring is bilingual and cites article range

**common/__init__.py:**
- [ ] All new types from `types.py` are imported
- [ ] All new errors from `errors.py` are imported
- [ ] All new symbols appear in `__all__` in alphabetical order

**chapter_XX_*.py:**
- [ ] Function returns `bool` (True on success)
- [ ] Function raises typed `ConstitutionalError` subclass on failure
- [ ] Every `raise` includes `article=` parameter with specific paragraph
- [ ] Docstring contains full Polish constitutional text (matching Dziennik Ustaw)
- [ ] Docstring contains full English translation
- [ ] Polish text appears before English text in docstring
- [ ] Integer arithmetic for vote comparisons (no float division)
- [ ] `Decimal` for any financial calculations
- [ ] No external dependencies used

**tests/test_chapter_XX_*.py:**
- [ ] Test class named `TestArtNN*` matching the article number
- [ ] At least one test for the valid/success case (`assert ... is True`)
- [ ] At least one test per distinct `raise` path in the implementation
- [ ] Tests use `pytest.raises` with `match=` for violation cases
- [ ] Tests verify `exc_info.value.article` matches expected article string
- [ ] Test docstrings reference the specific article paragraph being tested

**akn/konstytucja_rp.xml (if changed):**
- [ ] `eId` follows `art_NN` pattern
- [ ] Paragraph eIds follow `art_NN__para_M`
- [ ] Both `<p>` (Polish) and `<p xml:lang="en">` (English) elements present
- [ ] `<num>` elements present for article and paragraphs

### 4. Check article reference consistency

- Extract all `article="..."` values from the implementation
- Extract all `Art. NN` references from docstrings
- Verify they are consistent (same article numbers throughout)
- Verify they match the branch name's article number

### 5. Run automated checks

Execute and report results:
```bash
uv run pytest -v                    # All tests pass
uv run ruff check src tests         # No lint errors
uv run ruff format --check src tests # Formatting correct
uv run mypy src                     # Type checking passes
```

### 6. Coverage analysis

For each `raise` statement in the new/modified validation function:
- Find the corresponding test that triggers it
- Report any uncovered raise paths as FAIL

## Output Format

Report as a structured checklist:

```
## Amendment Validation Report: Art. NN (YYYY)

### File Completeness
- [PASS] common/types.py — NewDataclass added
- [PASS] common/errors.py — NewError added
- [FAIL] common/__init__.py — NewError not in __all__
...

### Code Pattern Checks
- [PASS] Dataclass is frozen
- [PASS] Bilingual docstrings
- [FAIL] Missing article= in raise on line 42
...

### Test Coverage
- [PASS] 3/3 raise paths covered
- [PASS] Valid case tested
...

### Automated Checks
- [PASS] pytest: 415 passed
- [PASS] ruff check: clean
- [PASS] mypy: clean
...

### Summary
X/Y checks passed. [READY FOR REVIEW / NEEDS FIXES]
```
