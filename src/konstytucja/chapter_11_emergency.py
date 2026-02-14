"""Rozdział XI: Stany nadzwyczajne / Chapter XI: Extraordinary Measures (Art. 228–234).

Rodzaje stanów nadzwyczajnych, ograniczenia czasowe, blokowanie wyborów.
Types of emergencies, duration limits, election blocking.
"""

from datetime import date, timedelta

from konstytucja.common.errors import EmergencyPowerError
from konstytucja.common.types import EmergencyDeclaration, EmergencyType

# Maximum durations in days (Art. 230, 232)
MAX_DURATION: dict[EmergencyType, int] = {
    EmergencyType.MARTIAL_LAW: -1,           # no explicit max (Art. 229)
    EmergencyType.STATE_OF_EMERGENCY: 90,    # Art. 230: max 90 days
    EmergencyType.NATURAL_DISASTER: 30,      # Art. 232: max 30 days
}

# Extension limits
MAX_EXTENSION: dict[EmergencyType, int] = {
    EmergencyType.MARTIAL_LAW: -1,           # no explicit limit
    EmergencyType.STATE_OF_EMERGENCY: 60,    # Art. 230: extension max 60 days
    EmergencyType.NATURAL_DISASTER: 60,      # Art. 232: extension max 60 days
}


def validate_declaration(decl: EmergencyDeclaration) -> bool:
    """Validate an emergency declaration against constitutional limits.

    Art. 228 ust. 1: W sytuacjach szczególnych zagrożeń, jeżeli zwykłe
    środki konstytucyjne są niewystarczające, może zostać wprowadzony
    odpowiedni stan nadzwyczajny: stan wojenny, stan wyjątkowy lub stan
    klęski żywiołowej.

    Art. 228(1): In situations of particular danger, where ordinary
    constitutional measures are inadequate, either of the following
    extraordinary measures may be introduced: martial law, a state of
    emergency, or a state of natural disaster.

    Art. 228 ust. 3: Zasady działania organów władzy publicznej oraz zakres,
    w jakim mogą zostać ograniczone wolności i prawa człowieka i obywatela
    w czasie poszczególnych stanów nadzwyczajnych, określa ustawa.

    Checks:
    - Duration does not exceed constitutional maximum.
    - Reason is provided (Art. 228 ust. 1: particular danger).
    """
    max_days = MAX_DURATION[decl.emergency_type]

    if max_days > 0 and decl.duration_days > max_days:
        raise EmergencyPowerError(
            f"{decl.emergency_type.value} cannot exceed {max_days} days "
            f"(requested {decl.duration_days})",
            article="230" if decl.emergency_type == EmergencyType.STATE_OF_EMERGENCY else "232",
        )

    if decl.duration_days <= 0:
        raise EmergencyPowerError(
            "Duration must be positive",
            article="228",
        )

    if not decl.reason.strip():
        raise EmergencyPowerError(
            "Reason must be provided (Art. 228 ust. 1: particular danger required)",
            article="228(1)",
        )

    return True


def validate_extension(
    emergency_type: EmergencyType,
    extension_days: int,
) -> bool:
    """Validate an extension of an emergency state.

    Art. 230 ust. 1: Stan wyjątkowy może być wprowadzony na czas oznaczony,
    nie dłuższy niż 90 dni, a jego przedłużenie może nastąpić tylko raz,
    na czas nie dłuższy niż 60 dni.

    Art. 230(1): A state of emergency may be declared for a definite period
    not exceeding 90 days, and an extension thereof may be made only once,
    for a period not exceeding 60 days.
    """
    max_ext = MAX_EXTENSION[emergency_type]

    if extension_days <= 0:
        raise EmergencyPowerError(
            "Extension duration must be positive",
            article="228",
        )

    if max_ext > 0 and extension_days > max_ext:
        raise EmergencyPowerError(
            f"{emergency_type.value} extension cannot exceed {max_ext} days "
            f"(requested {extension_days})",
            article="230" if emergency_type == EmergencyType.STATE_OF_EMERGENCY else "232",
        )

    return True


def elections_blocked_during_emergency(
    decl: EmergencyDeclaration,
    proposed_election_date: date,
) -> bool:
    """Check if elections are blocked during or shortly after an emergency.

    Art. 228 ust. 7: W czasie stanu nadzwyczajnego oraz w ciągu 90 dni
    po jego zakończeniu nie mogą być przeprowadzane wybory do Sejmu, Senatu,
    organów samorządu terytorialnego oraz wybory Prezydenta Rzeczypospolitej.
    Kadencje tych organów ulegają odpowiedniemu przedłużeniu.

    Art. 228(7): During a period of introduction of extraordinary measures,
    as well as within the period of 90 days following their termination,
    the following shall not be held: elections to the Sejm, Senate,
    local government organs, or elections for the President.

    Returns:
        True if the election is blocked; False if it can proceed.
    """
    emergency_end = decl.start_date + timedelta(days=decl.duration_days)
    blocked_until = emergency_end + timedelta(days=90)

    return proposed_election_date <= blocked_until


def check_election_allowed(
    decl: EmergencyDeclaration,
    proposed_election_date: date,
) -> bool:
    """Raise if an election is proposed during a blocked period.

    Args:
        decl: The active emergency declaration.
        proposed_election_date: The date of the proposed election.

    Returns:
        True if the election is allowed.

    Raises:
        EmergencyPowerError: if the election falls within the blocked period.
    """
    if elections_blocked_during_emergency(decl, proposed_election_date):
        emergency_end = decl.start_date + timedelta(days=decl.duration_days)
        blocked_until = emergency_end + timedelta(days=90)
        raise EmergencyPowerError(
            f"Elections cannot be held until {blocked_until} "
            f"(90 days after emergency ends on {emergency_end})",
            article="228(7)",
        )
    return True


# ---------------------------------------------------------------------------
# Non-restrictable rights during emergency — Art. 233
# ---------------------------------------------------------------------------

NON_RESTRICTABLE_RIGHTS: tuple[str, ...] = (
    "human dignity (Art. 30)",
    "citizenship (Art. 34, 36)",
    "protection of life (Art. 38)",
    "humane treatment (Art. 39)",  # prohibition of torture
    "criminal liability (Art. 40-41)",  # nullum crimen, nulla poena sine lege
    "access to court (Art. 45)",
    "personal interests (Art. 47)",
    "conscience and religion (Art. 53)",
    "petition (Art. 63)",
    "family and children (Art. 48, 72)",
)
"""Art. 233 ust. 1: Ustawa określająca zakres ograniczeń wolności i praw
człowieka i obywatela w stanie wojennym i wyjątkowym nie może ograniczać
wolności i praw określonych w art. 30, art. 34 i art. 36, art. 38,
art. 39, art. 40 i art. 41 ust. 4, art. 42, art. 45, art. 47, art. 53,
art. 63, art. 48 i art. 72.

Art. 233(1): A statute specifying the scope of limitations on rights
during martial law or a state of emergency may NOT restrict the rights
specified in the listed articles. These rights are absolutely protected.
"""

NON_RESTRICTABLE_ARTICLES: frozenset[int] = frozenset(
    {30, 34, 36, 38, 39, 40, 41, 42, 45, 47, 48, 53, 63, 72}
)
"""The set of article numbers whose rights cannot be restricted during
martial law or state of emergency (Art. 233(1)).
"""


def check_emergency_rights_restriction(
    article_number: int,
    emergency_type: EmergencyType,
) -> bool:
    """Check whether a right may be restricted during an emergency.

    Art. 233 ust. 1: Lists rights that CANNOT be restricted during
    martial law (stan wojenny) or state of emergency (stan wyjątkowy).

    Art. 233 ust. 3: During a state of natural disaster (stan klęski
    żywiołowej), the restrictions are more limited — only certain rights
    from Art. 233(3) may be restricted.

    Args:
        article_number: The constitutional article defining the right.
        emergency_type: The type of emergency in effect.

    Returns:
        True if the right MAY be restricted (i.e. it is not protected).

    Raises:
        EmergencyPowerError: If the right is non-restrictable under Art. 233.
    """
    if (
        emergency_type
        in (EmergencyType.MARTIAL_LAW, EmergencyType.STATE_OF_EMERGENCY)
        and article_number in NON_RESTRICTABLE_ARTICLES
    ):
        raise EmergencyPowerError(
            f"Art. {article_number} rights cannot be restricted during "
            f"{emergency_type.value} (Art. 233(1) — absolutely protected).",
            article="233",
        )
    return True
