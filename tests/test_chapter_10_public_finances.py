"""Tests for Chapter X: Public Finances (Art. 216–227)."""

from decimal import Decimal

import pytest

from konstytucja.chapter_10_public_finances import (
    NBP_MONETARY_POLICY_COUNCIL_MEMBERS,
    NBP_PRESIDENT_TERM_YEARS,
    check_debt_ceiling,
    debt_ratio,
    remaining_capacity,
    validate_currency_issuance,
    validate_nbp_independence,
)
from konstytucja.common.errors import CentralBankError, DebtCeilingError
from konstytucja.common.types import PublicDebt


class TestDebtCeiling:
    """Art. 216(5): Public debt may not exceed 3/5 of GDP."""

    def test_within_ceiling(self, healthy_finances):
        assert check_debt_ceiling(healthy_finances) is True

    def test_at_ceiling(self, ceiling_finances):
        """Exactly 3/5 is allowed (not exceeded)."""
        assert check_debt_ceiling(ceiling_finances) is True

    def test_over_ceiling(self, over_ceiling_finances):
        with pytest.raises(DebtCeilingError, match="exceeds 3/5"):
            check_debt_ceiling(over_ceiling_finances)

    def test_zero_debt(self):
        state = PublicDebt(debt=Decimal("0"), gdp=Decimal("1000"))
        assert check_debt_ceiling(state) is True

    def test_zero_gdp(self):
        state = PublicDebt(debt=Decimal("100"), gdp=Decimal("0"))
        with pytest.raises(DebtCeilingError, match="GDP must be positive"):
            check_debt_ceiling(state)

    def test_just_over_ceiling(self):
        """600.01 / 1000 = 0.60001 > 0.6 — exceeds."""
        state = PublicDebt(debt=Decimal("600.01"), gdp=Decimal("1000"))
        with pytest.raises(DebtCeilingError):
            check_debt_ceiling(state)

    def test_large_numbers(self):
        """Real-world scale: PLN billions."""
        state = PublicDebt(
            debt=Decimal("1_500_000_000_000"),
            gdp=Decimal("3_000_000_000_000"),
        )
        assert check_debt_ceiling(state) is True  # 0.5 ratio


class TestRemainingCapacity:
    """How much more debt is permissible."""

    def test_healthy(self, healthy_finances):
        cap = remaining_capacity(healthy_finances)
        assert cap == Decimal("100")  # 600 - 500

    def test_at_ceiling(self, ceiling_finances):
        cap = remaining_capacity(ceiling_finances)
        assert cap == Decimal("0")

    def test_over_ceiling(self, over_ceiling_finances):
        cap = remaining_capacity(over_ceiling_finances)
        assert cap == Decimal("0")  # clamped to 0


class TestDebtRatio:
    """Debt-to-GDP ratio."""

    def test_ratio(self, healthy_finances):
        assert debt_ratio(healthy_finances) == Decimal("0.5")

    def test_zero_gdp(self):
        state = PublicDebt(debt=Decimal("100"), gdp=Decimal("0"))
        with pytest.raises(DebtCeilingError):
            debt_ratio(state)


# ---------------------------------------------------------------------------
# NBP — Art. 227
# ---------------------------------------------------------------------------


class TestNbpConstants:
    """Art. 227: NBP term and composition constants."""

    def test_nbp_president_term_is_6_years(self):
        assert NBP_PRESIDENT_TERM_YEARS == 6

    def test_monetary_policy_council_has_10_members(self):
        assert NBP_MONETARY_POLICY_COUNCIL_MEMBERS == 10


class TestNbpIndependence:
    """Art. 227(1): NBP has exclusive right to set monetary policy."""

    def test_nbp_sets_monetary_policy(self):
        assert validate_nbp_independence("NBP") is True

    def test_polish_name_accepted(self):
        assert validate_nbp_independence("Narodowy Bank Polski") is True

    def test_english_name_accepted(self):
        assert validate_nbp_independence("National Bank of Poland") is True

    def test_government_cannot_set_monetary_policy(self):
        with pytest.raises(CentralBankError, match="exclusive domain"):
            validate_nbp_independence("Council of Ministers")

    def test_sejm_cannot_set_monetary_policy(self):
        with pytest.raises(CentralBankError):
            validate_nbp_independence("Sejm")

    def test_error_references_article_227(self):
        with pytest.raises(CentralBankError) as exc_info:
            validate_nbp_independence("Government")
        assert exc_info.value.article == "227"


class TestCurrencyIssuance:
    """Art. 227(1): NBP has exclusive right to issue currency."""

    def test_nbp_issues_currency(self):
        assert validate_currency_issuance("NBP") is True

    def test_other_entity_cannot_issue(self):
        with pytest.raises(CentralBankError, match="exclusive right"):
            validate_currency_issuance("Commercial Bank")

    def test_error_references_article_227(self):
        with pytest.raises(CentralBankError) as exc_info:
            validate_currency_issuance("Ministry of Finance")
        assert exc_info.value.article == "227"
