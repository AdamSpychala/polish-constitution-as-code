"""Rozdział III: Źródła prawa / Chapter III: Sources of Law (Art. 87–94).

Hierarchia aktów prawnych i rozstrzyganie konfliktów.
Legal hierarchy and conflict resolution.
"""

from konstytucja.common.errors import LegalHierarchyError
from konstytucja.common.types import LegalActType

# Art. 87: Hierarchy of legal acts (highest to lowest)
# Konstytucja → ratyfikowana umowa → ustawa → rozporządzenie → akt prawa miejscowego
HIERARCHY: dict[LegalActType, int] = {
    LegalActType.CONSTITUTION: 0,
    LegalActType.RATIFIED_TREATY: 1,
    LegalActType.STATUTE: 2,
    LegalActType.REGULATION: 3,
    LegalActType.LOCAL_ACT: 4,
}


def rank(act_type: LegalActType) -> int:
    """Return the rank of a legal act type (lower = higher authority).

    Art. 87 ust. 1: Źródłami powszechnie obowiązującego prawa
    Rzeczypospolitej Polskiej są: Konstytucja, ustawy, ratyfikowane
    umowy międzynarodowe oraz rozporządzenia.

    Art. 87(1): The sources of universally binding law of the Republic
    of Poland shall be: the Constitution, statutes, ratified international
    agreements, and regulations.
    """
    return HIERARCHY[act_type]


def prevails(higher: LegalActType, lower: LegalActType) -> bool:
    """Check whether `higher` outranks `lower` in the legal hierarchy.

    Art. 8 ust. 1: Konstytucja jest najwyższym prawem Rzeczypospolitej Polskiej.
    Art. 8(1): The Constitution shall be the supreme law of the Republic of Poland.

    Returns:
        True if `higher` has higher or equal rank.

    Raises:
        LegalHierarchyError: if the claimed hierarchy is inverted.
    """
    if rank(higher) > rank(lower):
        raise LegalHierarchyError(
            f"{higher.name} cannot prevail over {lower.name}: "
            f"rank {rank(higher)} vs {rank(lower)}",
            article="87",
        )
    return True


def resolve_conflict(act_a: LegalActType, act_b: LegalActType) -> LegalActType:
    """Given two conflicting legal acts, return the one that prevails.

    Art. 91 ust. 2: Umowa międzynarodowa ratyfikowana za uprzednią zgodą
    wyrażoną w ustawie ma pierwszeństwo przed ustawą, jeżeli ustawy tej
    nie da się pogodzić z umową.

    Art. 91(2): An international agreement ratified upon prior consent
    granted by statute shall have precedence over statutes if such an
    agreement cannot be reconciled with the provisions of such statutes.
    """
    if rank(act_a) <= rank(act_b):
        return act_a
    return act_b


def can_regulate(act_type: LegalActType) -> bool:
    """Check whether this act type is a source of universally binding law.

    Art. 87: Only Constitution, statutes, ratified treaties, regulations,
    and local acts (within their territory) are sources of universally
    binding law.
    """
    return act_type in HIERARCHY
