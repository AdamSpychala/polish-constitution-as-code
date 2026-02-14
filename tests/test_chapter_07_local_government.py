"""Tests for Chapter VII — Local Government (Art. 163–172).

Covers unit validation, supervision legality, and dissolution.
"""

import pytest

from konstytucja.chapter_07_local_government import (
    BASIC_UNIT,
    LOCAL_TERM_YEARS,
    check_supervision_legality,
    validate_dissolution,
    validate_local_unit,
)
from konstytucja.common.errors import LocalGovernmentError
from konstytucja.common.types import LocalGovernmentTier, LocalGovernmentUnit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Art. 164, 169: Basic unit and term length."""

    def test_basic_unit_is_gmina(self):
        assert BASIC_UNIT == LocalGovernmentTier.GMINA

    def test_term_is_4_years(self):
        assert LOCAL_TERM_YEARS == 4


# ---------------------------------------------------------------------------
# Unit validation — Art. 164
# ---------------------------------------------------------------------------


class TestLocalUnitValidation:
    """Art. 164: Validate local government units."""

    def test_valid_gmina(self, sample_local_unit):
        assert validate_local_unit(sample_local_unit) is True

    def test_valid_powiat(self):
        unit = LocalGovernmentUnit(
            name="Powiat Krakowski",
            tier=LocalGovernmentTier.POWIAT,
        )
        assert validate_local_unit(unit) is True

    def test_valid_wojewodztwo(self):
        unit = LocalGovernmentUnit(
            name="Województwo Małopolskie",
            tier=LocalGovernmentTier.WOJEWODZTWO,
        )
        assert validate_local_unit(unit) is True

    def test_empty_name_rejected(self):
        unit = LocalGovernmentUnit(
            name="",
            tier=LocalGovernmentTier.GMINA,
        )
        with pytest.raises(LocalGovernmentError, match="must have a name"):
            validate_local_unit(unit)

    def test_whitespace_name_rejected(self):
        unit = LocalGovernmentUnit(
            name="   ",
            tier=LocalGovernmentTier.GMINA,
        )
        with pytest.raises(LocalGovernmentError, match="must have a name"):
            validate_local_unit(unit)

    def test_wrong_term_rejected(self):
        unit = LocalGovernmentUnit(
            name="Gmina Kraków",
            tier=LocalGovernmentTier.GMINA,
            term_years=5,
        )
        with pytest.raises(LocalGovernmentError, match="4 years"):
            validate_local_unit(unit)

    def test_error_references_article_164_for_name(self):
        unit = LocalGovernmentUnit(name="", tier=LocalGovernmentTier.GMINA)
        with pytest.raises(LocalGovernmentError) as exc_info:
            validate_local_unit(unit)
        assert exc_info.value.article == "164"

    def test_error_references_article_169_for_term(self):
        unit = LocalGovernmentUnit(
            name="Gmina X", tier=LocalGovernmentTier.GMINA, term_years=3
        )
        with pytest.raises(LocalGovernmentError) as exc_info:
            validate_local_unit(unit)
        assert exc_info.value.article == "169"

    def test_unit_is_frozen(self):
        unit = LocalGovernmentUnit(
            name="Gmina Kraków", tier=LocalGovernmentTier.GMINA
        )
        with pytest.raises(AttributeError):
            unit.name = "Changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Supervision — Art. 171
# ---------------------------------------------------------------------------


class TestSupervisionLegality:
    """Art. 171: Supervision limited to legality."""

    def test_valid_supervision(self):
        assert check_supervision_legality("audit compliance", by_statute=True) is True

    def test_supervision_without_statute_rejected(self):
        with pytest.raises(LocalGovernmentError, match="legality"):
            check_supervision_legality("political review", by_statute=False)

    def test_error_includes_action_description(self):
        with pytest.raises(LocalGovernmentError, match="budget interference"):
            check_supervision_legality("budget interference", by_statute=False)

    def test_error_references_article_171(self):
        with pytest.raises(LocalGovernmentError) as exc_info:
            check_supervision_legality("overreach", by_statute=False)
        assert exc_info.value.article == "171"


# ---------------------------------------------------------------------------
# Dissolution — Art. 171(3)
# ---------------------------------------------------------------------------


class TestDissolution:
    """Art. 171(3): Dissolution for persistent violation only."""

    def test_valid_dissolution(self):
        assert (
            validate_dissolution(
                LocalGovernmentTier.GMINA, persistent_violation=True
            )
            is True
        )

    def test_dissolution_without_violation_rejected(self):
        with pytest.raises(LocalGovernmentError, match="persistent violation"):
            validate_dissolution(
                LocalGovernmentTier.GMINA, persistent_violation=False
            )

    def test_powiat_dissolution_requires_violation(self):
        with pytest.raises(LocalGovernmentError):
            validate_dissolution(
                LocalGovernmentTier.POWIAT, persistent_violation=False
            )

    def test_wojewodztwo_dissolution_with_violation(self):
        assert (
            validate_dissolution(
                LocalGovernmentTier.WOJEWODZTWO, persistent_violation=True
            )
            is True
        )

    def test_error_includes_tier_name(self):
        with pytest.raises(LocalGovernmentError, match="gmina"):
            validate_dissolution(
                LocalGovernmentTier.GMINA, persistent_violation=False
            )

    def test_error_references_article_171(self):
        with pytest.raises(LocalGovernmentError) as exc_info:
            validate_dissolution(
                LocalGovernmentTier.GMINA, persistent_violation=False
            )
        assert exc_info.value.article == "171"
