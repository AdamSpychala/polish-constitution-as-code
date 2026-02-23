Show the status of the current constitutional amendment branch.

## Steps

1. **Check branch name.** Verify current branch matches `feat/nowelizacja-*` pattern. Extract the year and article number from the name.

2. **Show diff summary.** Run `git diff main..HEAD --stat` to list files changed and lines added/removed.

3. **Show commit history.** Run `git log main..HEAD --oneline` to list commits on this branch.

4. **Parse the amendment.** Read the relevant chapter module to identify:
   - Which validation function(s) were added/modified
   - Which articles are referenced (from `article=` params and docstrings)
   - The Polish title of the amendment (from the docstring)

5. **Count tests.** Read the test file to count how many new test cases were added.

6. **Show file checklist.** Report which of the required files have been modified:

```
## Amendment Status: Art. NN — [Title] (YYYY)
Branch: feat/nowelizacja-YYYY-artNN-description

### Files Modified
- [x] common/types.py — NewDataclass
- [x] common/errors.py — NewError
- [x] common/__init__.py — re-exports updated
- [x] chapter_XX_*.py — validate_new_rule()
- [x] tests/test_chapter_XX_*.py — N test cases
- [ ] akn/konstytucja_rp.xml — not yet updated

### Commits (N total)
- abc1234 feat(chapter_XX): description

### Summary
N files changed, +X/-Y lines
N new test cases
Missing: [list of unchecked items above]
```

$ARGUMENTS
