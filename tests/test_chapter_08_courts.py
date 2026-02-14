"""Tests for Chapter VIII — Courts and Tribunals (Art. 173–201).

Covers ordinary courts (Art. 173–187), the Constitutional Tribunal
(Art. 188–197), and the State Tribunal (Art. 198–201).
"""

import pytest

from konstytucja.chapter_08_courts import (
    COURT_TYPES,
    KRS_MEMBERS,
    KRS_TERM_YEARS,
    MIN_INSTANCES,
    PETITIONERS,
    STATE_TRIBUNAL_MEMBERS,
    STATE_TRIBUNAL_SUBJECTS,
    TRIBUNAL_JUDGES,
    TRIBUNAL_TERM_YEARS,
    check_two_instance_requirement,
    validate_judge_appointment,
    validate_judicial_independence,
    validate_petitioner,
    validate_state_tribunal_composition,
    validate_state_tribunal_subject,
    validate_tribunal_verdict,
    verdict_is_final,
)
from konstytucja.common.errors import JudicialError, StateTribunalError, TribunalError
from konstytucja.common.types import (
    CourtType,
    Judge,
    TribunalCaseType,
    TribunalVerdict,
    TribunalVerdictType,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestTribunalComposition:
    """Art. 194: Tribunal composition."""

    def test_tribunal_has_15_judges(self):
        assert TRIBUNAL_JUDGES == 15

    def test_tribunal_term_is_9_years(self):
        assert TRIBUNAL_TERM_YEARS == 9


# ---------------------------------------------------------------------------
# Petitioners (Art. 191)
# ---------------------------------------------------------------------------


class TestPetitioners:
    """Art. 191: Who may bring cases before the Tribunal."""

    def test_petitioners_count(self):
        assert len(PETITIONERS) == 11

    @pytest.mark.parametrize("petitioner", PETITIONERS)
    def test_valid_petitioner_accepted(self, petitioner):
        validate_petitioner(petitioner)  # should not raise

    def test_president_is_valid_petitioner(self):
        validate_petitioner("President")

    def test_speaker_of_sejm_is_valid(self):
        validate_petitioner("Speaker of the Sejm")

    def test_speaker_of_senate_is_valid(self):
        validate_petitioner("Speaker of the Senate")

    def test_prime_minister_is_valid(self):
        validate_petitioner("Prime Minister")

    def test_50_deputies_is_valid(self):
        validate_petitioner("50 Deputies")

    def test_30_senators_is_valid(self):
        validate_petitioner("30 Senators")

    def test_first_president_supreme_court_is_valid(self):
        validate_petitioner("First President of the Supreme Court")

    def test_president_supreme_admin_court_is_valid(self):
        validate_petitioner("President of the Supreme Administrative Court")

    def test_prosecutor_general_is_valid(self):
        validate_petitioner("Prosecutor General")

    def test_nik_president_is_valid(self):
        validate_petitioner("President of the Supreme Chamber of Control")

    def test_rpo_is_valid(self):
        validate_petitioner("Commissioner for Citizens' Rights")

    def test_random_citizen_rejected(self):
        with pytest.raises(TribunalError, match="not authorised"):
            validate_petitioner("Jan Kowalski")

    def test_empty_string_rejected(self):
        with pytest.raises(TribunalError):
            validate_petitioner("")

    def test_individual_deputy_rejected(self):
        with pytest.raises(TribunalError):
            validate_petitioner("1 Deputy")

    def test_political_party_rejected(self):
        with pytest.raises(TribunalError):
            validate_petitioner("Prawo i Sprawiedliwość")

    def test_error_references_article_191(self):
        with pytest.raises(TribunalError) as exc_info:
            validate_petitioner("Nobody")
        assert exc_info.value.article == "191"

    def test_error_lists_valid_petitioners(self):
        with pytest.raises(TribunalError, match="President"):
            validate_petitioner("Nobody")


# ---------------------------------------------------------------------------
# Verdict validation
# ---------------------------------------------------------------------------


class TestTribunalVerdict:
    """Verdict internal consistency validation."""

    def test_constitutional_verdict_valid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="The statute conforms to the Constitution.",
        )
        validate_tribunal_verdict(verdict)  # should not raise

    def test_unconstitutional_verdict_valid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.UNCONSTITUTIONAL,
            reasoning="The statute violates Art. 2.",
        )
        validate_tribunal_verdict(verdict)  # should not raise

    def test_partially_unconstitutional_with_provisions_valid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Art. 5 of the statute violates the Constitution.",
            unconstitutional_provisions=("Art. 5",),
        )
        validate_tribunal_verdict(verdict)  # should not raise

    def test_partially_unconstitutional_multiple_provisions(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Multiple provisions violate the Constitution.",
            unconstitutional_provisions=("Art. 3", "Art. 7", "Art. 12"),
        )
        validate_tribunal_verdict(verdict)  # should not raise

    def test_partially_unconstitutional_without_provisions_invalid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Something is unconstitutional.",
        )
        with pytest.raises(TribunalError, match="must specify which provisions"):
            validate_tribunal_verdict(verdict)

    def test_unconstitutional_with_provisions_invalid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.UNCONSTITUTIONAL,
            reasoning="The entire act is unconstitutional.",
            unconstitutional_provisions=("Art. 5",),
        )
        with pytest.raises(TribunalError, match="entire act is struck down"):
            validate_tribunal_verdict(verdict)

    def test_constitutional_with_provisions_invalid(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="Constitutional.",
            unconstitutional_provisions=("Art. 5",),
        )
        with pytest.raises(TribunalError, match="cannot list unconstitutional"):
            validate_tribunal_verdict(verdict)

    def test_treaty_conformity_case_type(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.TREATY_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="Treaty conforms.",
        )
        validate_tribunal_verdict(verdict)

    def test_regulation_conformity_case_type(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.REGULATION_CONFORMITY,
            verdict=TribunalVerdictType.UNCONSTITUTIONAL,
            reasoning="Regulation violates the statute.",
        )
        validate_tribunal_verdict(verdict)

    def test_party_aims_case_type(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.PARTY_AIMS,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="Party aims conform.",
        )
        validate_tribunal_verdict(verdict)

    def test_verdict_is_frozen_dataclass(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="OK.",
        )
        with pytest.raises(AttributeError):
            verdict.reasoning = "changed"  # type: ignore[misc]

    def test_verdict_error_references_article_190(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Bad.",
        )
        with pytest.raises(TribunalError) as exc_info:
            validate_tribunal_verdict(verdict)
        assert exc_info.value.article == "190"


# ---------------------------------------------------------------------------
# Verdict finality (Art. 190)
# ---------------------------------------------------------------------------


class TestVerdictFinality:
    """Art. 190: Tribunal judgments are universally binding and final."""

    def test_constitutional_verdict_is_final(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="Conforms to the Constitution.",
        )
        assert verdict_is_final(verdict) is True

    def test_unconstitutional_verdict_is_final(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.UNCONSTITUTIONAL,
            reasoning="Violates Art. 2.",
        )
        assert verdict_is_final(verdict) is True

    def test_partial_verdict_is_final(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Art. 5 violates the Constitution.",
            unconstitutional_provisions=("Art. 5",),
        )
        assert verdict_is_final(verdict) is True

    def test_finality_rejects_invalid_verdict(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL,
            reasoning="Bad verdict.",
        )
        with pytest.raises(TribunalError):
            verdict_is_final(verdict)

    def test_finality_rejects_constitutional_with_provisions(self):
        verdict = TribunalVerdict(
            case_type=TribunalCaseType.STATUTE_CONFORMITY,
            verdict=TribunalVerdictType.CONSTITUTIONAL,
            reasoning="OK.",
            unconstitutional_provisions=("Art. 1",),
        )
        with pytest.raises(TribunalError):
            verdict_is_final(verdict)


# ---------------------------------------------------------------------------
# Enum coverage
# ---------------------------------------------------------------------------


class TestEnumValues:
    """Ensure enum values are stable and accessible."""

    def test_tribunal_case_types(self):
        assert len(TribunalCaseType) == 4

    def test_tribunal_verdict_types(self):
        assert len(TribunalVerdictType) == 3

    def test_case_type_values(self):
        assert TribunalCaseType.STATUTE_CONFORMITY.value == (
            "conformity of statute with Constitution"
        )
        assert TribunalCaseType.TREATY_CONFORMITY.value == (
            "conformity of international agreement with Constitution"
        )
        assert TribunalCaseType.REGULATION_CONFORMITY.value == (
            "conformity of regulation with Constitution/statutes"
        )
        assert TribunalCaseType.PARTY_AIMS.value == (
            "conformity of aims of political party with Constitution"
        )

    def test_verdict_type_values(self):
        assert TribunalVerdictType.CONSTITUTIONAL.value == "constitutional"
        assert TribunalVerdictType.UNCONSTITUTIONAL.value == "unconstitutional"
        assert TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL.value == "partially unconstitutional"


# ---------------------------------------------------------------------------
# Ordinary courts — constants (Art. 175–187)
# ---------------------------------------------------------------------------


class TestCourtConstants:
    """Art. 175, 176, 187: Court structure constants."""

    def test_four_court_types(self):
        assert len(COURT_TYPES) == 4

    def test_court_types_include_supreme(self):
        assert CourtType.SUPREME in COURT_TYPES

    def test_court_types_include_common(self):
        assert CourtType.COMMON in COURT_TYPES

    def test_court_types_include_administrative(self):
        assert CourtType.ADMINISTRATIVE in COURT_TYPES

    def test_court_types_include_military(self):
        assert CourtType.MILITARY in COURT_TYPES

    def test_min_instances_is_2(self):
        assert MIN_INSTANCES == 2

    def test_krs_has_25_members(self):
        assert KRS_MEMBERS == 25

    def test_krs_term_is_4_years(self):
        assert KRS_TERM_YEARS == 4


# ---------------------------------------------------------------------------
# Judge appointment — Art. 179
# ---------------------------------------------------------------------------


class TestJudgeAppointment:
    """Art. 179: Appointed by President on KRS proposal."""

    def test_valid_appointment(self, sample_judge):
        assert validate_judge_appointment(sample_judge) is True

    def test_not_appointed_by_president_rejected(self):
        judge = Judge(
            name="Jan Sędzia",
            court_type=CourtType.COMMON,
            appointed_by_president=False,
            krs_nominated=True,
        )
        with pytest.raises(JudicialError, match="President"):
            validate_judge_appointment(judge)

    def test_not_krs_nominated_rejected(self):
        judge = Judge(
            name="Jan Sędzia",
            court_type=CourtType.COMMON,
            appointed_by_president=True,
            krs_nominated=False,
        )
        with pytest.raises(JudicialError, match="Krajowa Rada"):
            validate_judge_appointment(judge)

    def test_error_references_article_179(self):
        judge = Judge(
            name="Jan",
            court_type=CourtType.COMMON,
            appointed_by_president=False,
        )
        with pytest.raises(JudicialError) as exc_info:
            validate_judge_appointment(judge)
        assert exc_info.value.article == "179"

    def test_judge_is_frozen(self, sample_judge):
        with pytest.raises(AttributeError):
            sample_judge.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Judicial independence — Art. 178
# ---------------------------------------------------------------------------


class TestJudicialIndependence:
    """Art. 178: Subject only to Constitution and statutes."""

    def test_constitution_and_statutes_accepted(self):
        assert validate_judicial_independence("Constitution and statutes") is True

    def test_polish_formulation_accepted(self):
        assert validate_judicial_independence("Konstytucja i ustawy") is True

    def test_executive_orders_rejected(self):
        with pytest.raises(JudicialError, match="independent"):
            validate_judicial_independence("executive orders")

    def test_party_instructions_rejected(self):
        with pytest.raises(JudicialError, match="independent"):
            validate_judicial_independence("party instructions")

    def test_error_references_article_178(self):
        with pytest.raises(JudicialError) as exc_info:
            validate_judicial_independence("ministerial directives")
        assert exc_info.value.article == "178"


# ---------------------------------------------------------------------------
# Two-instance requirement — Art. 176
# ---------------------------------------------------------------------------


class TestTwoInstanceRequirement:
    """Art. 176: Court proceedings must have at least two instances."""

    def test_two_instances_valid(self):
        assert check_two_instance_requirement(2) is True

    def test_three_instances_valid(self):
        assert check_two_instance_requirement(3) is True

    def test_one_instance_rejected(self):
        with pytest.raises(JudicialError, match="at least 2"):
            check_two_instance_requirement(1)

    def test_zero_instances_rejected(self):
        with pytest.raises(JudicialError, match="at least 2"):
            check_two_instance_requirement(0)

    def test_error_references_article_176(self):
        with pytest.raises(JudicialError) as exc_info:
            check_two_instance_requirement(1)
        assert exc_info.value.article == "176"


# ---------------------------------------------------------------------------
# State Tribunal — Art. 198–201
# ---------------------------------------------------------------------------


class TestStateTribunalConstants:
    """Art. 198–199: State Tribunal subjects and composition."""

    def test_state_tribunal_has_19_members(self):
        assert STATE_TRIBUNAL_MEMBERS == 19

    def test_state_tribunal_subjects_count(self):
        assert len(STATE_TRIBUNAL_SUBJECTS) == 9

    def test_president_is_subject(self):
        assert "President" in STATE_TRIBUNAL_SUBJECTS

    def test_prime_minister_is_subject(self):
        assert "Prime Minister" in STATE_TRIBUNAL_SUBJECTS

    def test_minister_is_subject(self):
        assert "Minister" in STATE_TRIBUNAL_SUBJECTS


class TestStateTribunalSubject:
    """Art. 198: Validate who is subject to State Tribunal jurisdiction."""

    @pytest.mark.parametrize("subject", STATE_TRIBUNAL_SUBJECTS)
    def test_valid_subjects_accepted(self, subject):
        assert validate_state_tribunal_subject(subject) is True

    def test_random_citizen_rejected(self):
        with pytest.raises(StateTribunalError, match="not subject"):
            validate_state_tribunal_subject("Jan Kowalski")

    def test_error_lists_valid_subjects(self):
        with pytest.raises(StateTribunalError, match="President"):
            validate_state_tribunal_subject("Nobody")

    def test_error_references_article_198(self):
        with pytest.raises(StateTribunalError) as exc_info:
            validate_state_tribunal_subject("Nobody")
        assert exc_info.value.article == "198"


class TestStateTribunalComposition:
    """Art. 199: State Tribunal composition validation."""

    def test_valid_composition(self):
        assert validate_state_tribunal_composition(19, from_outside_parliament=True) is True

    def test_wrong_member_count_rejected(self):
        with pytest.raises(StateTribunalError, match="19"):
            validate_state_tribunal_composition(15, from_outside_parliament=True)

    def test_members_from_parliament_rejected(self):
        with pytest.raises(StateTribunalError, match="outside"):
            validate_state_tribunal_composition(19, from_outside_parliament=False)

    def test_error_references_article_199(self):
        with pytest.raises(StateTribunalError) as exc_info:
            validate_state_tribunal_composition(10, from_outside_parliament=True)
        assert exc_info.value.article == "199"
