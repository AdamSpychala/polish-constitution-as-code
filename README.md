# Konstytucja RP jako kod / Polish Constitution as Code

The Polish Constitution of 1997 (Konstytucja Rzeczypospolitej Polskiej) encoded as executable Python. Every constitutional rule — eligibility thresholds, voting majorities, legislative procedures, judicial independence, emergency powers, fiscal limits — becomes a function you can call, a constraint you can test, and a violation that raises a named exception citing the exact article.

429 tests. 12 chapters. 2 amendments. Zero external dependencies.

Based on the [official text](https://www.sejm.gov.pl/prawo/konst/polski/kon1.htm) published by the Sejm of the Republic of Poland.

## Why encode a constitution as code?

Constitutions are already rule systems. They define who can hold office, how many votes a motion needs, what rights cannot be taken away, when elections must happen. These rules have precise conditions and outcomes — exactly the things software is good at.

This project makes those rules **executable and testable**:

- **A journalist** can ask: "If the government's debt hit 61% of GDP, would that violate Art. 216?" and get an answer by running a function, not by interpreting legal prose.
- **A law student** can step through the three-attempt government formation process (Art. 154–155) and see exactly where each vote failure routes to the next stage.
- **A civic tech developer** can import `check_sejm_eligibility()` into an election information app and have the age/citizenship checks match the constitution exactly.
- **A policy analyst** can model "what if the Senate rejects this bill?" and trace the full override path through the legislative state machine.

The executable form also catches ambiguities. When you have to write `votes_for * 3 >= total * 2` instead of "two-thirds majority," you're forced to answer: does "two-thirds" mean two-thirds of those present, or of statutory members? The code resolves that question, and the test proves the answer.

## Quick Start

```bash
uv sync                          # install dependencies
uv run pytest -v                 # run all 429 tests
uv run python examples/demo.py  # run 19 interactive scenarios
```

Requires Python 3.12+. No external runtime dependencies — stdlib only.

## Usage Examples

### Check if someone can run for parliament

```python
from datetime import date
from konstytucja.chapter_04_sejm_senate import check_sejm_eligibility, check_senate_eligibility
from konstytucja.common.types import Citizen

citizen = Citizen(name="Jan Kowalski", date_of_birth=date(1985, 6, 15))

check_sejm_eligibility(citizen, date(2025, 10, 15))   # True — age 40, needs ≥21
check_senate_eligibility(citizen, date(2025, 10, 15))  # True — age 40, needs ≥30
```

A 20-year-old would raise `EligibilityError` with the message citing Art. 99.

### Run a bill through the full legislative process

```python
from konstytucja.common.types import Bill, Chamber, VoteRecord
from konstytucja.legislative_process import LegislativeProcess

bill = Bill(title="Ustawa o cyfryzacji", sponsor="Council of Ministers")
proc = LegislativeProcess(bill=bill)

proc.begin_sejm_deliberation()
proc.sejm_vote(VoteRecord(chamber=Chamber.SEJM, votes_for=260, votes_against=170, votes_abstain=10))
proc.send_to_senate()
proc.senate_accepts()           # or senate_amends() / senate_rejects()
proc.send_to_president()
proc.president_signs()          # or president_vetoes() / president_refers_to_tribunal()
proc.enact()

print(proc.stage)   # BillStage.ENACTED
print(proc.history)  # full audit trail of every transition
```

The state machine enforces valid transitions — you cannot sign before Senate review, cannot enact before signing. Every invalid transition raises `LegislativeProcessError` citing the relevant article.

### Test the debt ceiling

```python
from decimal import Decimal
from konstytucja.chapter_10_public_finances import check_debt_ceiling, remaining_capacity
from konstytucja.common.types import PublicDebt

state = PublicDebt(debt=Decimal("1_500_000_000_000"), gdp=Decimal("3_000_000_000_000"))
check_debt_ceiling(state)       # True — 50% is under the 60% ceiling
remaining_capacity(state)       # Decimal("300000000000") — how much borrowing room remains
```

At 60.01% of GDP, `check_debt_ceiling` raises `DebtCeilingError` citing Art. 216(5). All financial math uses `Decimal` — no floating-point rounding.

### Simulate government formation

```python
from konstytucja.chapter_06_council_of_ministers import GovernmentFormation
from konstytucja.common.types import Chamber, VoteRecord, GovernmentFormationStage

gf = GovernmentFormation()
gf.president_designates()

# First attempt: needs absolute majority (231/460)
vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
gf.sejm_confidence_first_attempt(vote)
print(gf.stage)  # SEJM_ELECTS — first attempt failed, moves to second

# Second attempt: Sejm elects PM, needs absolute majority
gf.sejm_elects_pm(vote)
print(gf.stage)  # PRESIDENT_APPOINTS_RETRY — second attempt failed

# Third attempt: President appoints, needs simple majority
gf.president_appoints_third_attempt(vote)
print(gf.stage)  # FAILED — all three attempts failed, Sejm dissolved (Art. 155(2))
```

### Check emergency powers

```python
from datetime import date
from konstytucja.chapter_11_emergency import (
    validate_declaration, check_election_allowed, check_emergency_rights_restriction,
)
from konstytucja.common.types import EmergencyDeclaration, EmergencyType

decl = EmergencyDeclaration(
    emergency_type=EmergencyType.STATE_OF_EMERGENCY,
    start_date=date(2025, 1, 1),
    duration_days=90,  # max allowed for this type
    reason="Threat to constitutional order",
)
validate_declaration(decl)  # True

# No elections during emergency + 90 days after
check_election_allowed(decl, date(2025, 3, 15))  # raises EmergencyPowerError
check_election_allowed(decl, date(2025, 7, 2))   # True — cooling period over

# Human dignity (Art. 30) cannot be restricted even during martial law
check_emergency_rights_restriction(30, EmergencyType.MARTIAL_LAW)  # raises EmergencyPowerError
check_emergency_rights_restriction(50, EmergencyType.MARTIAL_LAW)  # True — home inviolability can be
```

## What's Included

### All 12 Chapters of the Constitution

| Chapter | Articles | Module | What it encodes |
|---------|----------|--------|----------------|
| I | Art. 1–29 | `chapter_01_republic` | Republic principles, separation of powers (legislative/executive/judicial), mapping of state organs to branches |
| II | Art. 30–86 | `chapter_02_rights` | Proportionality test for rights restrictions — 5 cumulative conditions from Art. 31(3): by statute, necessary in a democratic state, legitimate aim, proportionate, preserves essence. Extradition rules (Art. 55, as amended 2006) — 5-paragraph framework: default prohibition for Polish citizens, EAW/treaty exceptions, ICC exception for genocide/war crimes, absolute ban for political offences, court admissibility |
| III | Art. 87–94 | `chapter_03_sources_of_law` | Legal hierarchy (Constitution > statute > ratified treaty > regulation > local act), conflict resolution per Art. 91(2) |
| IV | Art. 95–125 | `chapter_04_sejm_senate` | Sejm (460 deputies, age ≥21) and Senate (100 senators, age ≥30) eligibility, bill passage with quorum, Senate override by absolute majority, incompatibilitas (Art. 103 — 14 incompatible offices), parliamentary immunity (Art. 105), national referendum with 50% turnout binding threshold (Art. 125) |
| V | Art. 126–145 | `chapter_05_president` | Presidential eligibility (age ≥35, 100K signatures), 5-year term with 2-term limit (Art. 127(2)), bill signing, veto (overridden by 3/5 Sejm majority) |
| VI | Art. 146–162 | `chapter_06_council_of_ministers` | Government composition, 3-stage formation state machine (Art. 154–155), confidence votes (absolute majority), constructive no-confidence (absolute majority + named successor, Art. 158), individual minister no-confidence (69 deputies minimum, Art. 159), minister State Tribunal liability (3/5 majority, Art. 156) |
| VII | Art. 163–172 | `chapter_07_local_government` | Gmina as basic unit (Art. 164), 3 tiers (gmina/powiat/wojewodztwo), supervision limited to legality (Art. 171), dissolution only for persistent constitutional violations |
| VIII | Art. 173–201 | `chapter_08_courts` | 4 court types (Supreme, common, administrative, military), judicial independence (subject only to Constitution and statutes, Art. 178), judge appointment (President on KRS proposal, Art. 179), two-instance requirement (Art. 176), Constitutional Tribunal (15 judges, 9-year terms, 11 authorized petitioners), State Tribunal (19 members, jurisdiction over President/PM/ministers, Art. 198) |
| IX | Art. 202–215 | `chapter_09_oversight` | NIK appointment (Sejm + Senate consent, 6-year term, max 2 terms), RPO/Ombudsman (5-year term), KRRiT composition (2 Sejm + 1 Senate + 1 President) |
| X | Art. 216–227 | `chapter_10_public_finances` | Debt ceiling at 3/5 of GDP using `Decimal` arithmetic (Art. 216(5)), remaining borrowing capacity calculation, NBP central bank independence — exclusive monetary policy and currency issuance (Art. 227) |
| XI | Art. 228–234 | `chapter_11_emergency` | 3 emergency types with duration limits (martial law: unlimited, state of emergency: 90 days, natural disaster: 30 days), extension limits (60 days), election blocking during emergency + 90-day cooling period (Art. 228(7)), 14 non-restrictable rights during martial law/state of emergency (Art. 233) |
| XII | Art. 235 | `chapter_12_amendments` | Full amendment state machine: first reading (30-day delay), Sejm vote (2/3 majority), Senate vote (absolute majority), mandatory referendum for Chapters I/II/XII, presidential signature |

### Cross-Cutting Infrastructure

| Module | Purpose |
|--------|---------|
| `legislative_process` | Complete bill lifecycle state machine (Art. 118–122) with 17 stages: Sejm deliberation, Senate review (accept/amend/reject), presidential review (sign/veto/refer to tribunal), partial unconstitutionality handling, veto override, full audit trail |
| `common/voting` | Quorum checks (half of statutory members), 4 majority types (simple, absolute, 2/3, 3/5), all using integer arithmetic |
| `common/types` | 13 enums, 11 frozen dataclasses — the full domain model |
| `common/errors` | 22 typed exception classes, every one carrying an `article` field referencing the violated provision |
| `akn/konstytucja_rp.xml` | Akoma Ntoso 3.0 XML — machine-readable document structure with bilingual Polish/English text, cross-referenceable with the executable code |

### Error System

Every constitutional violation raises a specific, typed exception:

```python
from konstytucja.common.errors import (
    EligibilityError,        # Art. 99, 127 — age, citizenship, Art. 99(3) criminal record [2009 amendment]
    ExtraditionError,        # Art. 55 [2006 amendment] — extradition rules
    QuorumError,             # Art. 120 — insufficient members present
    MajorityError,           # various — required majority not reached
    DebtCeilingError,        # Art. 216 — public debt exceeds 3/5 of GDP
    EmergencyPowerError,     # Art. 228–234 — emergency duration, election blocking
    GovernmentFormationError,# Art. 154–155 — formation procedure violation
    NoConfidenceError,       # Art. 158–159 — no-confidence vote rules
    IncompatibilityError,    # Art. 103 — office incompatible with mandate
    ImmunityError,           # Art. 105 — prosecution without chamber consent
    JudicialError,           # Art. 173–187 — judicial independence violation
    LegislativeProcessError, # Art. 118–122 — invalid state transition
    AmendmentError,          # Art. 235 — amendment procedure violation
    # ... and 10 more
)
```

All inherit from `ConstitutionalError` and carry an `.article` attribute:

```python
try:
    check_sejm_eligibility(young_citizen, election_date)
except EligibilityError as e:
    print(e.article)  # "99"
    print(e)          # "Candidate must be at least 21 years old to run for Sejm (is 20)"
```

## Project Structure

```
law-as-code/
├── src/konstytucja/
│   ├── common/
│   │   ├── types.py          # 13 enums + 11 frozen dataclasses
│   │   ├── errors.py         # 21 exception classes with article references
│   │   ├── voting.py         # quorum + 4 majority types, integer arithmetic
│   │   └── __init__.py       # re-exports everything
│   ├── chapter_01_republic.py        # Art. 1–29
│   ├── chapter_02_rights.py          # Art. 30–86
│   ├── chapter_03_sources_of_law.py  # Art. 87–94
│   ├── chapter_04_sejm_senate.py     # Art. 95–125
│   ├── chapter_05_president.py       # Art. 126–145
│   ├── chapter_06_council_of_ministers.py  # Art. 146–162
│   ├── chapter_07_local_government.py     # Art. 163–172
│   ├── chapter_08_courts.py               # Art. 173–201
│   ├── chapter_09_oversight.py            # Art. 202–215
│   ├── chapter_10_public_finances.py      # Art. 216–227
│   ├── chapter_11_emergency.py            # Art. 228–234
│   ├── chapter_12_amendments.py           # Art. 235
│   └── legislative_process.py             # Art. 118–122
├── akn/
│   └── konstytucja_rp.xml    # Akoma Ntoso XML (bilingual)
├── tests/                     # 426 pytest tests, one file per module
├── examples/
│   └── demo.py               # 19 runnable scenarios
└── pyproject.toml
```

## Design Decisions

**Integer arithmetic for votes.** The constitution says "two-thirds majority." Does 200/300 = 0.6666... qualify? With floating point, you'd worry about rounding. Instead: `votes_for * 3 >= total * 2`. Exact. No edge cases.

**`Decimal` for money.** The debt ceiling is 3/5 of GDP. With real-world numbers (trillions of PLN), floating-point errors compound. `Decimal` gives exact results at any scale.

**Frozen dataclasses everywhere.** A `Citizen`, a `VoteRecord`, a `Bill` — once created, they don't change. This prevents accidental mutation and makes the domain objects safe to pass around.

**Fail-loud with article references.** Instead of returning `False`, violations raise typed exceptions that name the specific article. A `MajorityError` from a veto override attempt says "Art. 122" — you can look it up. This makes debugging constitutional logic as straightforward as debugging code.

**Bilingual docstrings.** Every function includes the original Polish constitutional text first, then the English translation. The code is the law, and the law is quoted in the code.

**No external dependencies.** The entire library runs on Python's standard library. `dataclasses`, `enum`, `decimal`, `datetime` — nothing to install, nothing to break.

## Practical Applications

### Civic technology

Import the library into election information tools, parliamentary monitoring dashboards, or citizen education platforms. The eligibility checks, voting thresholds, and procedural rules are ready to use as validated building blocks.

```python
# In an election information app
from konstytucja.chapter_04_sejm_senate import check_sejm_eligibility, SEJM_DEPUTIES
from konstytucja.chapter_05_president import check_presidential_eligibility, MIN_SIGNATURES

# Show users whether they can run, and what they need
```

### Legal education

The 19 demo scenarios walk through real constitutional procedures step by step. Students can modify vote counts and see how outcomes change — when does a veto override fail? How many formation attempts before the Sejm is dissolved? What happens when the Tribunal rules a bill partially unconstitutional?

### Policy simulation

Model legislative scenarios before they happen. Feed real vote distributions into the state machines and trace the consequences:

```python
# What if the Senate rejects and the Sejm can't muster absolute majority to override?
proc.senate_rejects()
try:
    proc.sejm_overrides_senate_rejection(close_vote)
except MajorityError:
    proc.reject_bill()  # bill dies
```

### Compliance checking

Validate whether proposed government actions comply with constitutional constraints:

```python
# Does this emergency declaration exceed the allowed duration?
validate_declaration(proposed_emergency)

# Would this rights restriction pass the Art. 31 proportionality test?
validate_rights_restriction(proposed_restriction)

# Is the national debt still within constitutional limits?
check_debt_ceiling(current_finances)
```

### Automated testing of legal reasoning

Use the test suite as a reference implementation. When building legal AI tools or document analysis systems, validate their outputs against the 411 tests that encode known-correct constitutional interpretations.

## How to Extend

### Adding a new constitutional rule

1. **Find the right module.** Rules go in the chapter module matching their article number. Cross-cutting rules (like the legislative process) get their own module.

2. **Add types if needed.** New enums and dataclasses go in `common/types.py`. Keep them frozen.

3. **Write the function.** Follow the existing pattern:

```python
def validate_something(param: SomeType) -> bool:
    """Art. X ust. Y: [Polish text from the Constitution].

    Art. X(Y): [English translation].

    Args:
        param: What this represents.

    Returns:
        True if valid.

    Raises:
        SomeConstitutionalError: if the rule is violated.
    """
    if violation_condition:
        raise SomeConstitutionalError(
            "Clear message explaining what went wrong",
            article="X",
        )
    return True
```

4. **Add a test.** Tests go in the matching `tests/test_chapter_XX_*.py` file. Test both the happy path and the violation:

```python
def test_valid_case(self):
    assert validate_something(valid_input) is True

def test_violation(self):
    with pytest.raises(SomeConstitutionalError, match="expected message"):
        validate_something(invalid_input)
```

5. **Export it.** Add the function to `common/__init__.py` if it's a public API.

### Adding a new error type

Add it to `common/errors.py` inheriting from `ConstitutionalError`, then add it to `common/__init__.py`:

```python
class NewViolationError(ConstitutionalError):
    """Description in Polish — description in English.
    Art. X."""
```

### Adding a state machine

Follow the patterns in `legislative_process.py` or `chapter_12_amendments.py`: a frozen dataclass with a mutable `stage` field, transition methods that validate the current stage before advancing, and a `history` list recording every transition.

### Encoding other legal systems

The architecture is portable. To encode another country's constitution or a different legal framework:

1. Replace the chapter modules with the new system's structure
2. Define new types in `common/types.py`
3. Define new error classes in `common/errors.py`
4. Keep the same patterns: frozen dataclasses, integer vote arithmetic, bilingual docstrings (adapt languages), typed exceptions with provision references

The `common/voting.py` module (quorum checks, majority types) is reusable for any parliamentary system.

## Known Limitations

- **Timing not enforced.** Deadlines (30-day first reading delay, Senate's 60-day window, President's 21-day signing period) are documented in docstrings but not enforced by the state machines. Callers are responsible for timing checks.
- **Amendments included through 2009.** The code reflects the Constitution as amended by both enacted nowelizacje: the 2006 amendment to Art. 55 (European Arrest Warrant / extradition rules) and the 2009 amendment adding Art. 99(3) (electoral eligibility restriction for persons convicted of intentional crimes). These are the only two amendments to the 1997 Constitution as of 2026.
- **Interpretive choices.** Where the constitutional text is ambiguous, the code makes a specific choice (documented in the relevant docstring). These choices follow mainstream constitutional scholarship but are not authoritative legal opinions.

## Contributing

Contributions are welcome. If you'd like to encode additional rules, improve existing ones, or adapt the framework for another legal system, please open an issue or pull request. All constitutional logic should include article references and bilingual docstrings.

## License

MIT
