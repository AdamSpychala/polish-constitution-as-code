# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                              # install dependencies (dev group includes pytest, ruff, mypy)
uv run pytest -v                     # run all 411 tests
uv run pytest tests/test_chapter_04_sejm_senate.py -v   # run tests for one chapter
uv run pytest -k "test_quorum" -v    # run tests matching a keyword
uv run ruff check src tests          # lint (line-length 100, target py312)
uv run ruff format src tests         # auto-format
uv run mypy src                      # type-check (strict mode)
uv run python examples/demo.py       # run 19 interactive scenarios
```

Requires Python 3.12+. Zero external runtime dependencies (stdlib only). Dev dependencies: pytest >= 8.0, ruff >= 0.8, mypy >= 1.13.

## Architecture

The Polish Constitution of 1997 encoded as executable Python. Each constitutional rule becomes a function that returns `True` on success or raises a typed exception citing the violated article.

### Core pattern

Every public function follows the same contract:
- Validates a constitutional rule (eligibility, majority, debt ceiling, etc.)
- Returns `True` if the rule is satisfied
- Raises a specific `ConstitutionalError` subclass with an `article` field on violation
- Includes bilingual docstrings: original Polish constitutional text first, then English translation

### Module layout

- `src/konstytucja/common/types.py` — Domain model: 13 enums + 11 frozen dataclasses. All dataclasses are `frozen=True`.
- `src/konstytucja/common/errors.py` — 21 exception classes, all inheriting `ConstitutionalError(message, article=)`.
- `src/konstytucja/common/voting.py` — Quorum check and 4 majority types (simple, absolute, 2/3, 3/5). All vote math uses integer arithmetic to avoid float rounding.
- `src/konstytucja/common/__init__.py` — Re-exports everything from types, errors, and voting.
- `src/konstytucja/chapter_XX_*.py` — One module per constitutional chapter (12 total), articles mapped in order.
- `src/konstytucja/legislative_process.py` — Bill lifecycle state machine (17 stages). Enforces valid stage transitions; invalid transitions raise `LegislativeProcessError`.
- `tests/conftest.py` — Shared pytest fixtures (citizens, vote records, bills, finances, emergencies).
- `tests/test_chapter_XX_*.py` — One test file per chapter module, plus `test_common_voting.py` and `test_legislative_process.py`.
- `akn/konstytucja_rp.xml` — Akoma Ntoso 3.0 XML of the constitution (bilingual, machine-readable).

### State machines

`LegislativeProcess` and the amendment process in `chapter_12_amendments.py` use mutable `stage` fields on dataclasses with transition methods that validate the current stage before advancing. Each transition appends to a `history` list for audit trailing. `GovernmentFormation` in `chapter_06_council_of_ministers.py` follows the same pattern for the 3-attempt formation process.

### Key design decisions

- **Integer arithmetic for votes**: `votes_for * 3 >= total * 2` instead of float division. No rounding edge cases.
- **`Decimal` for money**: Debt ceiling math (`chapter_10_public_finances`) uses `Decimal` for exact results at any scale.
- **Frozen dataclasses**: All domain types are immutable. State machines are the only mutable objects.
- **Ruff ignores RUF002/RUF003**: Allows Unicode en-dashes in article range strings (e.g., "Art. 1–29").

### Adding a new rule

1. Add types to `common/types.py`, errors to `common/errors.py`, re-export in `common/__init__.py`.
2. Implement the rule function in the matching `chapter_XX_*.py` module with bilingual docstring and article reference.
3. Add tests in `tests/test_chapter_XX_*.py` covering both valid and violation cases.
