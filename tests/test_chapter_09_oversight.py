"""Tests for Chapter IX — Organs of State Control (Art. 202–215).

Covers NIK appointment, RPO appointment, and KRRiT composition.
"""

import pytest

from konstytucja.chapter_09_oversight import (
    KRRIT_MEMBERS,
    NIK_MAX_TERMS,
    NIK_TERM_YEARS,
    RPO_TERM_YEARS,
    validate_krrit_composition,
    validate_nik_appointment,
    validate_rpo_appointment,
)
from konstytucja.common.errors import OversightError
from konstytucja.common.types import OversightAppointment, OversightOrgan

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Art. 205, 209, 214: Term lengths and composition."""

    def test_nik_term_is_6_years(self):
        assert NIK_TERM_YEARS == 6

    def test_nik_max_terms_is_2(self):
        assert NIK_MAX_TERMS == 2

    def test_rpo_term_is_5_years(self):
        assert RPO_TERM_YEARS == 5

    def test_krrit_total_is_4(self):
        assert sum(KRRIT_MEMBERS.values()) == 4

    def test_krrit_sejm_appoints_2(self):
        assert KRRIT_MEMBERS["Sejm"] == 2

    def test_krrit_senate_appoints_1(self):
        assert KRRIT_MEMBERS["Senate"] == 1

    def test_krrit_president_appoints_1(self):
        assert KRRIT_MEMBERS["President"] == 1


# ---------------------------------------------------------------------------
# NIK appointment — Art. 205
# ---------------------------------------------------------------------------


class TestNikAppointment:
    """Art. 205: Sejm appoints with Senate consent."""

    def test_valid_appointment(self, nik_appointment):
        assert validate_nik_appointment(nik_appointment) is True

    def test_wrong_organ_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.RPO,
            name="Jan Kowalski",
            sejm_approved=True,
            senate_approved=True,
        )
        with pytest.raises(OversightError, match="NIK"):
            validate_nik_appointment(appt)

    def test_no_sejm_approval_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.NIK,
            name="Jan Kowalski",
            sejm_approved=False,
            senate_approved=True,
        )
        with pytest.raises(OversightError, match="appointed by the Sejm"):
            validate_nik_appointment(appt)

    def test_no_senate_consent_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.NIK,
            name="Jan Kowalski",
            sejm_approved=True,
            senate_approved=False,
        )
        with pytest.raises(OversightError, match="Senate consent"):
            validate_nik_appointment(appt)

    def test_error_references_article_205(self):
        appt = OversightAppointment(
            organ=OversightOrgan.NIK,
            name="Jan",
            sejm_approved=False,
            senate_approved=False,
        )
        with pytest.raises(OversightError) as exc_info:
            validate_nik_appointment(appt)
        assert exc_info.value.article == "205"


# ---------------------------------------------------------------------------
# RPO appointment — Art. 209
# ---------------------------------------------------------------------------


class TestRpoAppointment:
    """Art. 209: Sejm appoints with Senate consent."""

    def test_valid_appointment(self, rpo_appointment):
        assert validate_rpo_appointment(rpo_appointment) is True

    def test_wrong_organ_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.NIK,
            name="Anna Nowak",
            sejm_approved=True,
            senate_approved=True,
        )
        with pytest.raises(OversightError, match="RPO"):
            validate_rpo_appointment(appt)

    def test_no_sejm_approval_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.RPO,
            name="Anna Nowak",
            sejm_approved=False,
            senate_approved=True,
        )
        with pytest.raises(OversightError, match="appointed by the Sejm"):
            validate_rpo_appointment(appt)

    def test_no_senate_consent_rejected(self):
        appt = OversightAppointment(
            organ=OversightOrgan.RPO,
            name="Anna Nowak",
            sejm_approved=True,
            senate_approved=False,
        )
        with pytest.raises(OversightError, match="Senate consent"):
            validate_rpo_appointment(appt)

    def test_error_references_article_209(self):
        appt = OversightAppointment(
            organ=OversightOrgan.RPO,
            name="Anna",
            sejm_approved=False,
            senate_approved=False,
        )
        with pytest.raises(OversightError) as exc_info:
            validate_rpo_appointment(appt)
        assert exc_info.value.article == "209"


# ---------------------------------------------------------------------------
# KRRiT composition — Art. 214
# ---------------------------------------------------------------------------


class TestKrritComposition:
    """Art. 214: 2 by Sejm, 1 by Senate, 1 by President."""

    def test_valid_composition(self):
        assert validate_krrit_composition(2, 1, 1) is True

    def test_wrong_sejm_count(self):
        with pytest.raises(OversightError, match="Sejm"):
            validate_krrit_composition(3, 1, 1)

    def test_wrong_senate_count(self):
        with pytest.raises(OversightError, match="Senate"):
            validate_krrit_composition(2, 2, 1)

    def test_wrong_president_count(self):
        with pytest.raises(OversightError, match="President"):
            validate_krrit_composition(2, 1, 2)

    def test_all_zero_rejected(self):
        with pytest.raises(OversightError):
            validate_krrit_composition(0, 0, 0)

    def test_error_references_article_214(self):
        with pytest.raises(OversightError) as exc_info:
            validate_krrit_composition(0, 0, 0)
        assert exc_info.value.article == "214"
