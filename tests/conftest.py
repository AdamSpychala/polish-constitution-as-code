"""Shared pytest fixtures for constitutional tests."""

from datetime import date
from decimal import Decimal

import pytest

from konstytucja.common.types import (
    Bill,
    Chamber,
    Citizen,
    CouncilOfMinisters,
    CourtType,
    EmergencyDeclaration,
    EmergencyType,
    Judge,
    LocalGovernmentTier,
    LocalGovernmentUnit,
    Minister,
    OversightAppointment,
    OversightOrgan,
    PublicDebt,
    RightsRestriction,
    VoteRecord,
)

# ---------------------------------------------------------------------------
# Citizens
# ---------------------------------------------------------------------------


@pytest.fixture
def adult_citizen():
    """A 40-year-old Polish citizen with no criminal record."""
    return Citizen(
        name="Jan Kowalski",
        date_of_birth=date(1985, 6, 15),
        polish_citizen=True,
    )


@pytest.fixture
def young_citizen():
    """A 20-year-old Polish citizen."""
    return Citizen(
        name="Anna Młoda",
        date_of_birth=date(2005, 3, 1),
        polish_citizen=True,
    )


@pytest.fixture
def foreign_citizen():
    """A non-Polish citizen."""
    return Citizen(
        name="Hans Schmidt",
        date_of_birth=date(1980, 1, 1),
        polish_citizen=False,
    )


@pytest.fixture
def convicted_citizen():
    """A Polish citizen with a criminal record."""
    return Citizen(
        name="Krzysztof Winny",
        date_of_birth=date(1975, 12, 25),
        polish_citizen=True,
        criminal_record=True,
    )


# ---------------------------------------------------------------------------
# Vote records
# ---------------------------------------------------------------------------


@pytest.fixture
def sejm_simple_majority():
    """Sejm vote passing with simple majority and quorum."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=250,
        votes_against=180,
        votes_abstain=10,
    )


@pytest.fixture
def sejm_no_quorum():
    """Sejm vote without quorum."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=100,
        votes_against=50,
        votes_abstain=5,
    )


@pytest.fixture
def sejm_absolute_majority():
    """Sejm vote with absolute majority (> 230)."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=231,
        votes_against=100,
        votes_abstain=50,
    )


@pytest.fixture
def sejm_two_thirds():
    """Sejm vote with 2/3 majority."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=310,
        votes_against=80,
        votes_abstain=10,
    )


@pytest.fixture
def sejm_three_fifths():
    """Sejm vote with 3/5 majority (>= 276 of 460 present)."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=280,
        votes_against=160,
        votes_abstain=20,
    )


@pytest.fixture
def senate_simple_majority():
    """Senate vote with simple majority and quorum."""
    return VoteRecord(
        chamber=Chamber.SENATE,
        votes_for=55,
        votes_against=40,
        votes_abstain=5,
    )


@pytest.fixture
def senate_absolute_majority():
    """Senate vote with absolute majority (> 50)."""
    return VoteRecord(
        chamber=Chamber.SENATE,
        votes_for=51,
        votes_against=30,
        votes_abstain=10,
    )


# ---------------------------------------------------------------------------
# Bills
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_bill():
    """A standard legislative bill."""
    return Bill(title="Ustawa o podatkach", sponsor="Council of Ministers")


# ---------------------------------------------------------------------------
# Public finances
# ---------------------------------------------------------------------------


@pytest.fixture
def healthy_finances():
    """Public finances well within the debt ceiling."""
    return PublicDebt(debt=Decimal("500"), gdp=Decimal("1000"))


@pytest.fixture
def ceiling_finances():
    """Public finances exactly at the 3/5 ceiling."""
    return PublicDebt(debt=Decimal("600"), gdp=Decimal("1000"))


@pytest.fixture
def over_ceiling_finances():
    """Public finances exceeding the debt ceiling."""
    return PublicDebt(debt=Decimal("700"), gdp=Decimal("1000"))


# ---------------------------------------------------------------------------
# Emergency
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_emergency():
    """A valid state of emergency declaration."""
    return EmergencyDeclaration(
        emergency_type=EmergencyType.STATE_OF_EMERGENCY,
        start_date=date(2025, 1, 1),
        duration_days=90,
        reason="Threat to constitutional order",
    )


@pytest.fixture
def valid_natural_disaster():
    """A valid natural disaster declaration."""
    return EmergencyDeclaration(
        emergency_type=EmergencyType.NATURAL_DISASTER,
        start_date=date(2025, 6, 1),
        duration_days=30,
        reason="Severe flooding in southern Poland",
    )


# ---------------------------------------------------------------------------
# Rights restriction
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_restriction():
    """A rights restriction that satisfies all five Art. 31(3) conditions."""
    return RightsRestriction(
        description="Quarantine during epidemic",
        by_statute=True,
        necessary_in_democratic_state=True,
        legitimate_aim=True,
        proportionate=True,
        preserves_essence=True,
    )


@pytest.fixture
def invalid_restriction():
    """A rights restriction that fails the proportionality test."""
    return RightsRestriction(
        description="Total ban on peaceful assembly",
        by_statute=True,
        necessary_in_democratic_state=False,
        legitimate_aim=True,
        proportionate=False,
        preserves_essence=False,
    )


# ---------------------------------------------------------------------------
# Common dates
# ---------------------------------------------------------------------------


@pytest.fixture
def election_date():
    """A standard election date."""
    return date(2025, 10, 15)


# ---------------------------------------------------------------------------
# Council of Ministers (Chapter VI)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_council():
    """A valid Council of Ministers with PM + 2 ministers."""
    return CouncilOfMinisters(
        prime_minister=Minister(name="Jan Kowalski", role="Prime Minister"),
        ministers=(
            Minister(name="Anna Nowak", role="Minister of Finance"),
            Minister(name="Piotr Wiśniewski", role="Minister of Defence"),
        ),
    )


# ---------------------------------------------------------------------------
# Courts (Chapter VIII)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_judge():
    """A validly appointed common court judge."""
    return Judge(
        name="Maria Sędziak",
        court_type=CourtType.COMMON,
        appointed_by_president=True,
        krs_nominated=True,
    )


# ---------------------------------------------------------------------------
# Local government (Chapter VII)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_local_unit():
    """A valid gmina (basic local government unit)."""
    return LocalGovernmentUnit(
        name="Gmina Kraków",
        tier=LocalGovernmentTier.GMINA,
    )


# ---------------------------------------------------------------------------
# Oversight organs (Chapter IX)
# ---------------------------------------------------------------------------


@pytest.fixture
def nik_appointment():
    """A valid NIK President appointment."""
    return OversightAppointment(
        organ=OversightOrgan.NIK,
        name="Jan Kontroler",
        sejm_approved=True,
        senate_approved=True,
    )


@pytest.fixture
def rpo_appointment():
    """A valid RPO appointment."""
    return OversightAppointment(
        organ=OversightOrgan.RPO,
        name="Anna Rzecznik",
        sejm_approved=True,
        senate_approved=True,
    )
