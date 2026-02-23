"""Tests for Chapter V: The President (Art. 126–145)."""

from datetime import date

import pytest

from konstytucja.chapter_05_president import (
    MAX_PRESIDENTIAL_TERMS,
    PRESIDENTIAL_TERM_YEARS,
    check_presidential_eligibility,
    sejm_overrides_veto,
    validate_presidential_term,
)
from konstytucja.common.errors import EligibilityError, MajorityError
from konstytucja.common.types import Chamber, Citizen, VoteRecord


class TestPresidentialEligibility:
    """Art. 127(3): President must be 35+, Polish citizen, 100K signatures."""

    def test_eligible(self, adult_citizen, election_date):
        assert check_presidential_eligibility(
            adult_citizen, election_date, signatures=100_000,
        ) is True

    def test_too_young(self, election_date):
        citizen = Citizen(
            name="Young Candidate",
            date_of_birth=date(1995, 1, 1),
            polish_citizen=True,
        )
        with pytest.raises(EligibilityError, match="at least 35"):
            check_presidential_eligibility(citizen, election_date, signatures=100_000)

    def test_not_polish(self, foreign_citizen, election_date):
        with pytest.raises(EligibilityError, match="Polish citizen"):
            check_presidential_eligibility(
                foreign_citizen, election_date, signatures=100_000,
            )

    def test_criminal_record(self, convicted_citizen, election_date):
        with pytest.raises(EligibilityError, match="intentional crime"):
            check_presidential_eligibility(
                convicted_citizen, election_date, signatures=100_000,
            )

    def test_insufficient_signatures(self, adult_citizen, election_date):
        with pytest.raises(EligibilityError, match="signatures"):
            check_presidential_eligibility(
                adult_citizen, election_date, signatures=99_999,
            )

    def test_exactly_100k_signatures(self, adult_citizen, election_date):
        assert check_presidential_eligibility(
            adult_citizen, election_date, signatures=100_000,
        ) is True

    def test_exactly_35_on_election_day(self, election_date):
        citizen = Citizen(
            name="Exact 35",
            date_of_birth=date(1990, 10, 15),
            polish_citizen=True,
        )
        assert check_presidential_eligibility(
            citizen, election_date, signatures=100_000,
        ) is True

    def test_multiple_failures(self, election_date):
        citizen = Citizen(
            name="Multiple Failures",
            date_of_birth=date(2000, 1, 1),
            polish_citizen=False,
            criminal_record=True,
        )
        with pytest.raises(EligibilityError) as exc_info:
            check_presidential_eligibility(citizen, election_date, signatures=50)
        msg = str(exc_info.value)
        assert "Polish citizen" in msg
        assert "at least 35" in msg
        assert "intentional crime" in msg
        assert "signatures" in msg


class TestVetoOverride:
    """Art. 122(5): 3/5 majority needed to override presidential veto."""

    def test_override_passes(self, sejm_three_fifths):
        assert sejm_overrides_veto(sejm_three_fifths) is True

    def test_override_fails(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=275,
            votes_against=185,
        )
        with pytest.raises(MajorityError, match="Three-fifths"):
            sejm_overrides_veto(vote)

    def test_override_exact_three_fifths(self):
        """276 of 460 = 3/5 exactly."""
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=276,
            votes_against=184,
        )
        assert sejm_overrides_veto(vote) is True


# ---------------------------------------------------------------------------
# Term limits — Art. 127(2)
# ---------------------------------------------------------------------------


class TestPresidentialTermLimits:
    """Art. 127(2): 5-year term, maximum 2 consecutive terms."""

    def test_term_is_5_years(self):
        assert PRESIDENTIAL_TERM_YEARS == 5

    def test_max_terms_is_2(self):
        assert MAX_PRESIDENTIAL_TERMS == 2

    def test_first_term_allowed(self):
        assert validate_presidential_term(0) is True

    def test_second_term_allowed(self):
        assert validate_presidential_term(1) is True

    def test_third_term_rejected(self):
        with pytest.raises(EligibilityError, match="2 consecutive terms"):
            validate_presidential_term(2)

    def test_fourth_term_rejected(self):
        with pytest.raises(EligibilityError):
            validate_presidential_term(3)

    def test_error_references_article_127(self):
        with pytest.raises(EligibilityError) as exc_info:
            validate_presidential_term(2)
        assert exc_info.value.article == "127(2)"
