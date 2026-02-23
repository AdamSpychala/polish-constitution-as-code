## Nowelizacja: Art. [NUMBER] — [Short Title]

### Legal Reference

- **Article(s) affected:** Art. XX
- **Enacted:** [Date] / **Proposed:** [Date or "Hypothetical"]
- **Dziennik Ustaw:** [e.g., Dz.U. 2006 nr 200 poz. 1471]
- **Subject:** [One-sentence summary]

### Constitutional Text

<details>
<summary>Polish (tekst polski)</summary>

[Full text of the amended article(s) in Polish, as it appears in the code docstrings]

</details>

<details>
<summary>English (translation)</summary>

[Full English translation, as it appears in the code docstrings]

</details>

### What Changed

| Before (pre-amendment) | After (post-amendment) |
|------------------------|------------------------|
| [Old rule or "N/A — new provision"] | [New rule] |

### Code Changes

- [ ] `common/types.py` — [New dataclass / modified field]
- [ ] `common/errors.py` — [New error class]
- [ ] `common/__init__.py` — [Re-exports added]
- [ ] `chapter_XX_*.py` — [New/modified validation function]
- [ ] `tests/test_chapter_XX_*.py` — [N test cases: N valid, N violation]
- [ ] `akn/konstytucja_rp.xml` — [Article XML updated]

### Validation Checklist

- [ ] `uv run pytest -v` — all tests pass
- [ ] `uv run ruff check src tests` — no lint errors
- [ ] `uv run mypy src` — type checking passes
- [ ] Bilingual docstrings (Polish first, then English)
- [ ] `article=` in all error raises
- [ ] Frozen dataclasses (`@dataclass(frozen=True)`)
- [ ] Integer arithmetic for vote math (no floats)
- [ ] `Decimal` for financial math
- [ ] Legal text matches official Dziennik Ustaw publication

### Scholarly Notes

[Optional: interpretive choices made, ambiguities resolved, comparison with other legal systems, citations to constitutional scholarship, reason the amendment was enacted/proposed/rejected]
