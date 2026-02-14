"""Rozdział X: Finanse publiczne / Chapter X: Public Finances (Art. 216–227).

Limit długu publicznego — 3/5 PKB, Narodowy Bank Polski.
Public debt ceiling — 3/5 of GDP, National Bank of Poland.
"""

from decimal import Decimal

from konstytucja.common.errors import CentralBankError, DebtCeilingError
from konstytucja.common.types import PublicDebt

# Art. 216 ust. 5: 3/5 ratio expressed as Decimal for precision
DEBT_CEILING_RATIO = Decimal("3") / Decimal("5")  # 0.6


def check_debt_ceiling(state: PublicDebt) -> bool:
    """Check that public debt does not exceed 3/5 of annual GDP.

    Art. 216 ust. 5: Nie wolno zaciągać pożyczek lub udzielać gwarancji
    i poręczeń finansowych, w następstwie których państwowy dług publiczny
    przekroczy 3/5 wartości rocznego produktu krajowego brutto.
    Sposób obliczania wartości rocznego produktu krajowego brutto oraz
    państwowego długu publicznego określa ustawa.

    Art. 216(5): It shall not be permissible to contract loans or provide
    guarantees and financial sureties which would engender a national public
    debt exceeding three-fifths of the value of the annual gross domestic
    product. The method of calculating the value of the annual gross domestic
    product and national public debt shall be specified by statute.

    Uses Decimal arithmetic to avoid floating-point errors.
    Integer comparison: debt * 5 <= gdp * 3.

    Args:
        state: Current public finance state.

    Returns:
        True if within the ceiling.

    Raises:
        DebtCeilingError: if debt exceeds 3/5 of GDP.
    """
    if state.gdp <= 0:
        raise DebtCeilingError(
            f"GDP must be positive (got {state.gdp})",
            article="216(5)",
        )

    # Integer-style comparison: debt * 5 > gdp * 3 means violation
    if state.debt * 5 > state.gdp * 3:
        ratio = state.debt / state.gdp
        raise DebtCeilingError(
            f"Public debt ({state.debt}) exceeds 3/5 of GDP ({state.gdp}): "
            f"ratio = {ratio:.4f}, max = {DEBT_CEILING_RATIO}",
            article="216(5)",
        )
    return True


def remaining_capacity(state: PublicDebt) -> Decimal:
    """Calculate how much additional debt is permissible.

    Returns:
        The remaining borrowing capacity before hitting the ceiling.
        Returns Decimal('0') if already at or over the limit.
    """
    ceiling = state.gdp * DEBT_CEILING_RATIO
    remaining = ceiling - state.debt
    return max(remaining, Decimal("0"))


def debt_ratio(state: PublicDebt) -> Decimal:
    """Calculate the current debt-to-GDP ratio.

    Returns:
        debt / gdp as a Decimal.
    """
    if state.gdp <= 0:
        raise DebtCeilingError(
            f"GDP must be positive (got {state.gdp})",
            article="216(5)",
        )
    return state.debt / state.gdp


# ---------------------------------------------------------------------------
# National Bank of Poland — Art. 227
# ---------------------------------------------------------------------------

NBP_PRESIDENT_TERM_YEARS: int = 6
"""Art. 227 ust. 3: Prezes Narodowego Banku Polskiego jest powoływany
na 6 lat.

The President of the NBP is appointed for a 6-year term.
"""

NBP_MONETARY_POLICY_COUNCIL_MEMBERS: int = 10
"""Art. 227 ust. 5: Organy Narodowego Banku Polskiego: Prezes NBP,
Rada Polityki Pieniężnej, Zarząd.
Rada składa się z Prezesa NBP jako przewodniczącego oraz 9 członków.

The Monetary Policy Council consists of the NBP President (chair)
plus 9 members (3 by Sejm, 3 by Senate, 3 by President) = 10 total.
"""


def validate_nbp_independence(monetary_policy_by: str) -> bool:
    """Check that monetary policy is set exclusively by the NBP.

    Art. 227 ust. 1: Centralnym bankiem państwa jest Narodowy Bank Polski.
    Przysługuje mu wyłączne prawo emisji pieniądza oraz ustalania i
    realizowania polityki pieniężnej. Narodowy Bank Polski odpowiada za
    wartość polskiego pieniądza.

    Art. 227(1): The NBP is the central bank. It has the exclusive right
    to issue currency and to formulate and implement monetary policy.
    The NBP is responsible for the value of Polish currency.

    Args:
        monetary_policy_by: The entity claiming to set monetary policy.

    Raises:
        CentralBankError: If monetary policy is claimed by a non-NBP entity.
    """
    allowed = {"NBP", "Narodowy Bank Polski", "National Bank of Poland"}
    if monetary_policy_by not in allowed:
        raise CentralBankError(
            f"Monetary policy is the exclusive domain of the NBP "
            f"(Art. 227(1)). '{monetary_policy_by}' cannot set monetary policy.",
            article="227",
        )
    return True


def validate_currency_issuance(issuer: str) -> bool:
    """Check that currency is issued exclusively by the NBP.

    Art. 227 ust. 1: Przysługuje mu wyłączne prawo emisji pieniądza.
    The NBP has the exclusive right to issue currency.

    Args:
        issuer: The entity claiming to issue currency.

    Raises:
        CentralBankError: If currency issuance is claimed by a non-NBP entity.
    """
    allowed = {"NBP", "Narodowy Bank Polski", "National Bank of Poland"}
    if issuer not in allowed:
        raise CentralBankError(
            f"Only the NBP has the exclusive right to issue currency "
            f"(Art. 227(1)). '{issuer}' cannot issue currency.",
            article="227",
        )
    return True
