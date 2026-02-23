"""Rozdział V: Prezydent RP / Chapter V: The President (Art. 126–145).

Warunki wybieralności, kadencja, weto, podpisanie ustawy.
Eligibility, term limits, veto, signing of bills.
"""

from datetime import date

from konstytucja.common.errors import EligibilityError
from konstytucja.common.types import (
    Chamber,
    Citizen,
    MajorityType,
    VoteRecord,
)
from konstytucja.common.voting import passes_vote

# Art. 127 ust. 2: 5-year term, max 2 consecutive terms
PRESIDENTIAL_TERM_YEARS: int = 5
"""Art. 127 ust. 2: Prezydent Rzeczypospolitej jest wybierany na
pięcioletnią kadencję i może być ponownie wybrany tylko raz.

The President is elected for a 5-year term and may be re-elected
only once.
"""

MAX_PRESIDENTIAL_TERMS: int = 2
"""Art. 127 ust. 2: …może być ponownie wybrany tylko raz.

May be re-elected only once (maximum 2 consecutive terms).
"""

# Art. 127 ust. 3: minimum 100,000 citizen signatures to register
MIN_SIGNATURES: int = 100_000


def check_presidential_eligibility(
    citizen: Citizen,
    election_date: date,
    signatures: int = 0,
) -> bool:
    """Verify eligibility for the presidency (Art. 127).

    Art. 127 ust. 1: Prezydent Rzeczypospolitej jest wybierany przez Naród.
    Art. 127(1): The President shall be elected by the Nation.

    Art. 127 ust. 3: Na Prezydenta Rzeczypospolitej może być wybrany
    obywatel polski, który najpóźniej w dniu wyborów kończy 35 lat
    i korzysta z pełni praw wyborczych do Sejmu. Kandydata zgłasza
    co najmniej 100 000 obywateli mających prawo wybierania do Sejmu.

    Art. 127(3): Any Polish citizen who has attained 35 years of age and
    has full electoral rights to the Sejm may be elected President.
    A candidate shall be nominated by at least 100,000 citizens having
    the right to vote in Sejm elections.

    Note: "full electoral rights to the Sejm" implies Art. 99(3)
    [nowelizacja 2009] — a person convicted by final judgment for an
    intentional crime prosecuted ex officio lacks full electoral rights.

    Conditions:
    - Polish citizen
    - At least 35 years old on election day
    - Full electoral rights (no Art. 99(3) disqualification)
    - At least 100,000 supporting signatures
    """
    errors: list[str] = []

    if not citizen.polish_citizen:
        errors.append("must be a Polish citizen")
    if citizen.age_at(election_date) < 35:
        errors.append(f"must be at least 35 (is {citizen.age_at(election_date)})")
    if citizen.criminal_record:
        errors.append(
            "lacks full electoral rights: convicted by final judgment for an "
            "intentional crime prosecuted ex officio (Art. 99(3), nowelizacja 2009)"
        )
    if signatures < MIN_SIGNATURES:
        errors.append(
            f"needs at least {MIN_SIGNATURES:,} signatures (has {signatures:,})"
        )

    if errors:
        raise EligibilityError(
            f"{citizen.name} ineligible for presidency: {'; '.join(errors)}",
            article="127(3)",
        )
    return True


def president_signs_bill() -> bool:
    """President signs a bill within 21 days (Art. 122 ust. 2).

    Art. 122 ust. 2: Prezydent Rzeczypospolitej podpisuje ustawę w ciągu
    21 dni od dnia przedstawienia i zarządza jej ogłoszenie w Dzienniku Ustaw.

    Art. 122(2): The President shall sign a bill within 21 days of its
    submission and shall order its publication in the Journal of Laws.
    """
    return True


def president_vetoes_bill() -> bool:
    """President vetoes a bill (Art. 122 ust. 5).

    Art. 122 ust. 5: Jeżeli Prezydent Rzeczypospolitej nie wystąpił
    z wnioskiem do Trybunału Konstytucyjnego, może z umotywowanym wnioskiem
    przekazać ustawę Sejmowi do ponownego rozpatrzenia.

    Art. 122(5): If the President has not made a referral to the Constitutional
    Tribunal, he may refer the bill, with a reasoned request, to the Sejm
    for reconsideration.
    """
    return True


def sejm_overrides_veto(vote: VoteRecord) -> bool:
    """Check if the Sejm overrides a presidential veto (Art. 122 ust. 5).

    Art. 122 ust. 5: Po ponownym uchwaleniu ustawy przez Sejm większością
    3/5 głosów w obecności co najmniej połowy ustawowej liczby posłów,
    Prezydent Rzeczypospolitej w ciągu 7 dni podpisuje ustawę.

    Art. 122(5): After re-passage of the bill by the Sejm by a three-fifths
    majority vote in the presence of at least half the statutory number of
    Deputies, the President shall sign the bill within 7 days.

    Requires: 3/5 majority in the Sejm with quorum.
    """
    assert vote.chamber == Chamber.SEJM, "Veto override vote must be from the Sejm"
    return passes_vote(vote, MajorityType.THREE_FIFTHS)


# ---------------------------------------------------------------------------
# Term limits — Art. 127(2)
# ---------------------------------------------------------------------------


def validate_presidential_term(consecutive_terms_served: int) -> bool:
    """Check whether a candidate can run given prior terms served.

    Art. 127 ust. 2: Prezydent Rzeczypospolitej jest wybierany na
    pięcioletnią kadencję i może być ponownie wybrany tylko raz.

    Art. 127(2): The President is elected for a 5-year term and may
    be re-elected only once.

    Args:
        consecutive_terms_served: Number of consecutive terms already served.

    Returns:
        True if another term is permissible.

    Raises:
        EligibilityError: If the candidate has already served the maximum.
    """
    if consecutive_terms_served >= MAX_PRESIDENTIAL_TERMS:
        raise EligibilityError(
            f"A President may serve at most {MAX_PRESIDENTIAL_TERMS} "
            f"consecutive terms (Art. 127(2)). "
            f"Already served: {consecutive_terms_served}.",
            article="127(2)",
        )
    return True
