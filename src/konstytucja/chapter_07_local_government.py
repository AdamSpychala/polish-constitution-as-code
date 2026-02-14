"""Chapter VII — Local Government (Art. 163–172).

Rozdział VII — Samorząd terytorialny.

This module encodes rules governing local government units, the principle
that gmina is the basic unit, supervision limited to legality, and
conditions for dissolution.
"""

from konstytucja.common.errors import LocalGovernmentError
from konstytucja.common.types import LocalGovernmentTier, LocalGovernmentUnit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOCAL_TERM_YEARS: int = 4
"""Art. 169 ust. 2: Wybory do organów stanowiących samorządu terytorialnego
są powszechne, równe, bezpośrednie i odbywają się w głosowaniu tajnym.
Kadencja organów stanowiących wynosi 4 lata.

Elections to the constitutive organs of local government are universal, equal,
direct and conducted by secret ballot. The term of office is 4 years.
"""

BASIC_UNIT: LocalGovernmentTier = LocalGovernmentTier.GMINA
"""Art. 164 ust. 1: Podstawową jednostką samorządu terytorialnego jest gmina.

The commune (gmina) is the basic unit of local government.
"""

# ---------------------------------------------------------------------------
# Unit validation — Art. 164
# ---------------------------------------------------------------------------


def validate_local_unit(unit: LocalGovernmentUnit) -> bool:
    """Validate a local government unit.

    Art. 164 ust. 1: Podstawową jednostką samorządu terytorialnego jest gmina.
    Art. 164 ust. 2: Inne jednostki samorządu regionalnego albo lokalnego
    i regionalnego określa ustawa.

    The commune (gmina) is the basic unit of local government.
    Other units of regional or local and regional government are
    specified by statute.

    Validates that the unit has a name, a valid tier, and appropriate
    term length.

    Raises:
        LocalGovernmentError: If the unit is invalid.
    """
    if not unit.name or not unit.name.strip():
        raise LocalGovernmentError(
            "A local government unit must have a name.",
            article="164",
        )
    if unit.term_years != LOCAL_TERM_YEARS:
        raise LocalGovernmentError(
            f"Term of constitutive organs must be {LOCAL_TERM_YEARS} years "
            f"(Art. 169(2)), got {unit.term_years}.",
            article="169",
        )
    return True


# ---------------------------------------------------------------------------
# Supervision — Art. 171
# ---------------------------------------------------------------------------


def check_supervision_legality(action: str, by_statute: bool) -> bool:
    """Check that supervision of local government is limited to legality.

    Art. 171 ust. 1: Działalność samorządu terytorialnego podlega nadzorowi
    z punktu widzenia legalności.

    The activity of local government is subject to supervision only from
    the standpoint of legality.

    Args:
        action: Description of the supervisory action.
        by_statute: Whether the supervision is based on a statutory provision.

    Raises:
        LocalGovernmentError: If the supervision is not based on statute
            (i.e. exceeds the legality criterion).
    """
    if not by_statute:
        raise LocalGovernmentError(
            f"Supervision of local government must be limited to legality "
            f"(based on statute). Action '{action}' lacks a statutory basis.",
            article="171",
        )
    return True


# ---------------------------------------------------------------------------
# Dissolution — Art. 171(3)
# ---------------------------------------------------------------------------


def validate_dissolution(
    tier: LocalGovernmentTier, persistent_violation: bool
) -> bool:
    """Validate dissolution of a local government constitutive organ.

    Art. 171 ust. 3: Sejm, na wniosek Prezesa Rady Ministrów, może
    rozwiązać organ stanowiący samorządu terytorialnego, jeżeli organ
    ten rażąco narusza Konstytucję lub ustawy.

    The Sejm, on motion of the Prime Minister, may dissolve a constitutive
    organ of local government if that organ persistently violates the
    Constitution or statutes.

    Args:
        tier: The tier of local government being dissolved.
        persistent_violation: Whether there is a persistent constitutional
            or statutory violation.

    Raises:
        LocalGovernmentError: If the dissolution is not justified by a
            persistent violation.
    """
    if not persistent_violation:
        raise LocalGovernmentError(
            f"Dissolution of a {tier.value} constitutive organ requires "
            f"persistent violation of the Constitution or statutes.",
            article="171",
        )
    return True
