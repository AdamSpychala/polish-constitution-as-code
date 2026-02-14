"""Rozdział II: Wolności, prawa i obowiązki / Chapter II: Rights and Freedoms (Art. 30–86).

Art. 31 ust. 3 — test proporcjonalności ograniczenia praw i wolności.
Art. 31(3) — proportionality test for restricting rights and freedoms.
"""

from konstytucja.common.errors import RightsRestrictionError
from konstytucja.common.types import RightsRestriction


def validate_rights_restriction(restriction: RightsRestriction) -> bool:
    """Validate a proposed restriction of constitutional rights against Art. 31(3).

    Art. 31 ust. 3: Ograniczenia w zakresie korzystania z konstytucyjnych
    wolności i praw mogą być ustanawiane tylko w ustawie i tylko wtedy,
    gdy są konieczne w demokratycznym państwie dla jego bezpieczeństwa
    lub porządku publicznego, bądź dla ochrony środowiska, zdrowia i
    moralności publicznej, albo wolności i praw innych osób. Ograniczenia
    te nie mogą naruszać istoty wolności i praw.

    Art. 31(3): Any limitation upon the exercise of constitutional freedoms
    and rights may be imposed only by statute, and only when necessary in a
    democratic state for the protection of its security or public order, or
    to protect the natural environment, health or public morals, or the
    freedoms and rights of other persons. Such limitations shall not violate
    the essence of freedoms and rights.

    Five cumulative conditions:
    1. By statute (only a ustawa can restrict rights)
    2. Necessary in a democratic state
    3. Pursues a legitimate aim
    4. Proportionate to the aim
    5. Preserves the essence of the right

    Args:
        restriction: The proposed restriction to evaluate.

    Returns:
        True if the restriction is constitutionally valid.

    Raises:
        RightsRestrictionError: with details of which conditions fail.
    """
    failures: list[str] = []

    if not restriction.by_statute:
        failures.append("not established by statute (ustawa)")
    if not restriction.necessary_in_democratic_state:
        failures.append("not necessary in a democratic state")
    if not restriction.legitimate_aim:
        failures.append("does not pursue a legitimate aim (security, public order, "
                        "environment, health, public morals, or freedoms of others)")
    if not restriction.proportionate:
        failures.append("not proportionate to the aim pursued")
    if not restriction.preserves_essence:
        failures.append("violates the essence of the freedom or right")

    if failures:
        detail = "; ".join(failures)
        raise RightsRestrictionError(
            f"Restriction '{restriction.description}' fails Art. 31(3): {detail}",
            article="31(3)",
        )

    return True
