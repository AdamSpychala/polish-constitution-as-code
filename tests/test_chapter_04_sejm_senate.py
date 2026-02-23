"""Tests for Chapter IV: Sejm and Senate (Art. 95–125)."""

from datetime import date

import pytest

from konstytucja.chapter_04_sejm_senate import (
    INCOMPATIBLE_WITH_DEPUTY,
    SEJM_DEPUTIES,
    SEJM_TERM_YEARS,
    SENATE_SENATORS,
    check_incompatibility,
    check_sejm_eligibility,
    check_senate_eligibility,
    sejm_overrides_senate,
    sejm_passes_bill,
    senate_passes_bill,
    validate_parliamentary_immunity,
    validate_referendum,
)
from konstytucja.common.errors import (
    EligibilityError,
    ImmunityError,
    IncompatibilityError,
    MajorityError,
    QuorumError,
    ReferendumError,
)
from konstytucja.common.types import Chamber, Citizen, VoteRecord


class TestSejmEligibility:
    """Art. 99(1): Sejm eligibility — 21 years, Polish citizen."""

    def test_eligible(self, adult_citizen, election_date):
        assert check_sejm_eligibility(adult_citizen, election_date) is True

    def test_too_young(self, young_citizen, election_date):
        with pytest.raises(EligibilityError, match="at least 21"):
            check_sejm_eligibility(young_citizen, election_date)

    def test_non_citizen(self, foreign_citizen, election_date):
        with pytest.raises(EligibilityError, match="Polish citizen"):
            check_sejm_eligibility(foreign_citizen, election_date)

    def test_criminal_record(self, convicted_citizen, election_date):
        with pytest.raises(EligibilityError, match="intentional crime"):
            check_sejm_eligibility(convicted_citizen, election_date)

    def test_criminal_record_references_2009_amendment(self, convicted_citizen, election_date):
        """Art. 99(3) [nowelizacja 2009]: error message cites the amendment."""
        with pytest.raises(EligibilityError) as exc_info:
            check_sejm_eligibility(convicted_citizen, election_date)
        msg = str(exc_info.value)
        assert "nowelizacja 2009" in msg
        assert "ex officio" in msg

    def test_exactly_21_on_election_day(self):
        citizen = Citizen(
            name="Exact 21",
            date_of_birth=date(2004, 10, 15),
            polish_citizen=True,
        )
        assert check_sejm_eligibility(citizen, date(2025, 10, 15)) is True

    def test_day_before_21(self):
        citizen = Citizen(
            name="Almost 21",
            date_of_birth=date(2004, 10, 16),
            polish_citizen=True,
        )
        with pytest.raises(EligibilityError):
            check_sejm_eligibility(citizen, date(2025, 10, 15))


class TestSenateEligibility:
    """Art. 99(2): Senate eligibility — 30 years, Polish citizen."""

    def test_eligible(self, adult_citizen, election_date):
        assert check_senate_eligibility(adult_citizen, election_date) is True

    def test_too_young_for_senate(self):
        citizen = Citizen(
            name="Young Senator",
            date_of_birth=date(1996, 1, 1),
            polish_citizen=True,
        )
        with pytest.raises(EligibilityError, match="at least 30"):
            check_senate_eligibility(citizen, date(2025, 10, 15))

    def test_non_citizen(self, foreign_citizen, election_date):
        with pytest.raises(EligibilityError, match="Polish citizen"):
            check_senate_eligibility(foreign_citizen, election_date)

    def test_criminal_record(self, convicted_citizen, election_date):
        """Art. 99(3) [nowelizacja 2009]: Senate candidate cannot have criminal record."""
        with pytest.raises(EligibilityError, match="intentional crime"):
            check_senate_eligibility(convicted_citizen, election_date)

    def test_exactly_30(self):
        citizen = Citizen(
            name="Exact 30",
            date_of_birth=date(1995, 10, 15),
            polish_citizen=True,
        )
        assert check_senate_eligibility(citizen, date(2025, 10, 15)) is True


class TestBillPassage:
    """Art. 120–121: Bill passage through Sejm and Senate."""

    def test_sejm_passes(self, sejm_simple_majority):
        assert sejm_passes_bill(sejm_simple_majority) is True

    def test_sejm_no_quorum(self, sejm_no_quorum):
        with pytest.raises(QuorumError):
            sejm_passes_bill(sejm_no_quorum)

    def test_senate_passes(self, senate_simple_majority):
        assert senate_passes_bill(senate_simple_majority) is True

    def test_sejm_overrides_senate(self, sejm_absolute_majority):
        assert sejm_overrides_senate(sejm_absolute_majority) is True

    def test_sejm_fails_to_override(self):
        """230 votes is not > 230 (absolute majority needs > half)."""
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=230,
            votes_against=100,
            votes_abstain=50,
        )
        with pytest.raises(MajorityError):
            sejm_overrides_senate(vote)


# ---------------------------------------------------------------------------
# Composition constants — Art. 96–98
# ---------------------------------------------------------------------------


class TestCompositionConstants:
    """Art. 96–98: Sejm and Senate composition."""

    def test_sejm_has_460_deputies(self):
        assert SEJM_DEPUTIES == 460

    def test_senate_has_100_senators(self):
        assert SENATE_SENATORS == 100

    def test_term_is_4_years(self):
        assert SEJM_TERM_YEARS == 4


# ---------------------------------------------------------------------------
# Incompatibilitas — Art. 103
# ---------------------------------------------------------------------------


class TestIncompatibilitas:
    """Art. 103: Offices incompatible with a parliamentary mandate."""

    def test_compatible_office_accepted(self):
        assert check_incompatibility("Teacher") is True

    def test_minister_is_compatible(self):
        """Art. 103: Exception — Council of Ministers members may be deputies."""
        assert check_incompatibility("Minister of Finance") is True

    @pytest.mark.parametrize("office", INCOMPATIBLE_WITH_DEPUTY)
    def test_incompatible_offices_rejected(self, office):
        with pytest.raises(IncompatibilityError):
            check_incompatibility(office)

    def test_nbp_president_incompatible(self):
        with pytest.raises(IncompatibilityError, match="cannot be held jointly"):
            check_incompatibility("President of the National Bank of Poland")

    def test_rpo_incompatible(self):
        with pytest.raises(IncompatibilityError):
            check_incompatibility("Commissioner for Citizens' Rights")

    def test_error_references_article_103(self):
        with pytest.raises(IncompatibilityError) as exc_info:
            check_incompatibility("Ambassador")
        assert exc_info.value.article == "103"


# ---------------------------------------------------------------------------
# Parliamentary immunity — Art. 105
# ---------------------------------------------------------------------------


class TestParliamentaryImmunity:
    """Art. 105: Immunity from criminal prosecution."""

    def test_sejm_consent_given(self):
        assert validate_parliamentary_immunity(Chamber.SEJM, consent_given=True) is True

    def test_senate_consent_given(self):
        assert validate_parliamentary_immunity(Chamber.SENATE, consent_given=True) is True

    def test_sejm_no_consent_raises(self):
        with pytest.raises(ImmunityError, match="Sejm"):
            validate_parliamentary_immunity(Chamber.SEJM, consent_given=False)

    def test_senate_no_consent_raises(self):
        with pytest.raises(ImmunityError, match="Senate"):
            validate_parliamentary_immunity(Chamber.SENATE, consent_given=False)

    def test_error_references_article_105(self):
        with pytest.raises(ImmunityError) as exc_info:
            validate_parliamentary_immunity(Chamber.SEJM, consent_given=False)
        assert exc_info.value.article == "105"


# ---------------------------------------------------------------------------
# National referendum — Art. 125
# ---------------------------------------------------------------------------


class TestReferendum:
    """Art. 125: National referendum."""

    def test_passes_with_majority_and_turnout(self):
        assert validate_referendum(600_000, 400_000, eligible_voters=1_000_000) is True

    def test_fails_insufficient_turnout(self):
        with pytest.raises(ReferendumError, match="turnout"):
            validate_referendum(300_000, 100_000, eligible_voters=1_000_000)

    def test_fails_more_against_than_for(self):
        with pytest.raises(ReferendumError, match="rejected"):
            validate_referendum(400_000, 500_000, eligible_voters=1_000_000)

    def test_exact_50_percent_turnout_not_binding(self):
        """Exactly 50% is NOT binding — must exceed 50%."""
        with pytest.raises(ReferendumError, match="turnout"):
            validate_referendum(300_000, 200_000, eligible_voters=1_000_000)

    def test_just_over_50_percent_turnout(self):
        assert validate_referendum(300_001, 200_000, eligible_voters=1_000_000) is True

    def test_zero_eligible_voters_rejected(self):
        with pytest.raises(ReferendumError, match="positive"):
            validate_referendum(100, 50, eligible_voters=0)

    def test_tie_rejected(self):
        with pytest.raises(ReferendumError, match="rejected"):
            validate_referendum(500_000, 500_000, eligible_voters=1_000_000)

    def test_error_references_article_125(self):
        with pytest.raises(ReferendumError) as exc_info:
            validate_referendum(100, 200, eligible_voters=100)
        assert "125" in exc_info.value.article
