"""Tests for Chapter XI: Emergency Powers (Art. 228–234)."""

from datetime import date

import pytest

from konstytucja.chapter_11_emergency import (
    NON_RESTRICTABLE_ARTICLES,
    check_election_allowed,
    check_emergency_rights_restriction,
    elections_blocked_during_emergency,
    validate_declaration,
    validate_extension,
)
from konstytucja.common.errors import EmergencyPowerError
from konstytucja.common.types import EmergencyDeclaration, EmergencyType


class TestValidateDeclaration:
    """Art. 228–232: Emergency declaration validation."""

    def test_valid_state_of_emergency(self, valid_emergency):
        assert validate_declaration(valid_emergency) is True

    def test_valid_natural_disaster(self, valid_natural_disaster):
        assert validate_declaration(valid_natural_disaster) is True

    def test_state_of_emergency_exceeds_90_days(self):
        decl = EmergencyDeclaration(
            emergency_type=EmergencyType.STATE_OF_EMERGENCY,
            start_date=date(2025, 1, 1),
            duration_days=91,
            reason="Threat",
        )
        with pytest.raises(EmergencyPowerError, match="cannot exceed 90 days"):
            validate_declaration(decl)

    def test_natural_disaster_exceeds_30_days(self):
        decl = EmergencyDeclaration(
            emergency_type=EmergencyType.NATURAL_DISASTER,
            start_date=date(2025, 6, 1),
            duration_days=31,
            reason="Flooding",
        )
        with pytest.raises(EmergencyPowerError, match="cannot exceed 30 days"):
            validate_declaration(decl)

    def test_martial_law_no_max(self):
        """Martial law has no explicit constitutional duration limit."""
        decl = EmergencyDeclaration(
            emergency_type=EmergencyType.MARTIAL_LAW,
            start_date=date(2025, 1, 1),
            duration_days=365,
            reason="External aggression",
        )
        assert validate_declaration(decl) is True

    def test_zero_duration(self):
        decl = EmergencyDeclaration(
            emergency_type=EmergencyType.STATE_OF_EMERGENCY,
            start_date=date(2025, 1, 1),
            duration_days=0,
            reason="Something",
        )
        with pytest.raises(EmergencyPowerError, match="Duration must be positive"):
            validate_declaration(decl)

    def test_empty_reason(self):
        decl = EmergencyDeclaration(
            emergency_type=EmergencyType.STATE_OF_EMERGENCY,
            start_date=date(2025, 1, 1),
            duration_days=30,
            reason="",
        )
        with pytest.raises(EmergencyPowerError, match="Reason must be provided"):
            validate_declaration(decl)


class TestExtension:
    """Art. 230: Extension limits."""

    def test_valid_extension(self):
        assert validate_extension(EmergencyType.STATE_OF_EMERGENCY, 60) is True

    def test_state_of_emergency_extension_exceeds_60(self):
        with pytest.raises(EmergencyPowerError, match="cannot exceed 60 days"):
            validate_extension(EmergencyType.STATE_OF_EMERGENCY, 61)

    def test_natural_disaster_extension_exceeds_60(self):
        with pytest.raises(EmergencyPowerError, match="cannot exceed 60 days"):
            validate_extension(EmergencyType.NATURAL_DISASTER, 61)

    def test_martial_law_unlimited_extension(self):
        assert validate_extension(EmergencyType.MARTIAL_LAW, 365) is True

    def test_zero_extension(self):
        with pytest.raises(EmergencyPowerError, match="positive"):
            validate_extension(EmergencyType.STATE_OF_EMERGENCY, 0)


class TestElectionBlocking:
    """Art. 228(7): No elections during emergency + 90 days after."""

    def test_during_emergency(self, valid_emergency):
        """Election during the emergency period is blocked."""
        assert elections_blocked_during_emergency(
            valid_emergency, date(2025, 2, 1),
        ) is True

    def test_within_90_days_after(self, valid_emergency):
        """Emergency ends April 1, blocked until June 30."""
        assert elections_blocked_during_emergency(
            valid_emergency, date(2025, 6, 30),
        ) is True

    def test_after_cooling_period(self, valid_emergency):
        """Emergency ends April 1 + 90 days = July 1. July 2 is allowed."""
        assert elections_blocked_during_emergency(
            valid_emergency, date(2025, 7, 2),
        ) is False

    def test_check_election_allowed_raises(self, valid_emergency):
        with pytest.raises(EmergencyPowerError, match="Elections cannot be held"):
            check_election_allowed(valid_emergency, date(2025, 3, 1))

    def test_check_election_allowed_passes(self, valid_emergency):
        assert check_election_allowed(valid_emergency, date(2025, 7, 2)) is True


# ---------------------------------------------------------------------------
# Non-restrictable rights — Art. 233
# ---------------------------------------------------------------------------


class TestNonRestrictableRights:
    """Art. 233: Rights that cannot be restricted during emergency."""

    def test_non_restrictable_articles_set(self):
        assert 30 in NON_RESTRICTABLE_ARTICLES  # human dignity
        assert 38 in NON_RESTRICTABLE_ARTICLES  # protection of life
        assert 45 in NON_RESTRICTABLE_ARTICLES  # access to court
        assert 53 in NON_RESTRICTABLE_ARTICLES  # conscience and religion

    @pytest.mark.parametrize("article", sorted(NON_RESTRICTABLE_ARTICLES))
    def test_non_restrictable_during_martial_law(self, article):
        with pytest.raises(EmergencyPowerError, match="cannot be restricted"):
            check_emergency_rights_restriction(article, EmergencyType.MARTIAL_LAW)

    @pytest.mark.parametrize("article", sorted(NON_RESTRICTABLE_ARTICLES))
    def test_non_restrictable_during_state_of_emergency(self, article):
        with pytest.raises(EmergencyPowerError, match="cannot be restricted"):
            check_emergency_rights_restriction(
                article, EmergencyType.STATE_OF_EMERGENCY
            )

    def test_restrictable_article_allowed_during_martial_law(self):
        """Art. 50 (home inviolability) is NOT in the protected list."""
        assert (
            check_emergency_rights_restriction(50, EmergencyType.MARTIAL_LAW) is True
        )

    def test_restrictable_during_state_of_emergency(self):
        assert (
            check_emergency_rights_restriction(50, EmergencyType.STATE_OF_EMERGENCY)
            is True
        )

    def test_natural_disaster_less_restrictive(self):
        """Art. 233(3) applies to natural disasters, which has a different
        (narrower) list. Art. 30 rights are allowed to check during natural
        disaster since Art. 233(1) only applies to martial law and state
        of emergency."""
        assert (
            check_emergency_rights_restriction(30, EmergencyType.NATURAL_DISASTER)
            is True
        )

    def test_error_references_article_233(self):
        with pytest.raises(EmergencyPowerError) as exc_info:
            check_emergency_rights_restriction(30, EmergencyType.MARTIAL_LAW)
        assert exc_info.value.article == "233"
