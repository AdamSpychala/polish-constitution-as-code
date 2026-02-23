"""Rozdział IV: Sejm i Senat / Chapter IV: The Sejm and Senate (Art. 95–125).

Warunki wybieralności, uchwalanie ustaw, kompetencje izb, immunitet,
incompatibilitas, referendum.
Eligibility, bill passage, chamber competences, immunity,
incompatibility of offices, national referendum.
"""

from datetime import date

from konstytucja.common.errors import (
    EligibilityError,
    ImmunityError,
    IncompatibilityError,
    ReferendumError,
)
from konstytucja.common.types import (
    Chamber,
    Citizen,
    MajorityType,
    VoteRecord,
)
from konstytucja.common.voting import passes_vote

# ---------------------------------------------------------------------------
# Composition (Art. 95–98)
# ---------------------------------------------------------------------------

SEJM_DEPUTIES: int = 460
"""Art. 96 ust. 1: Sejm składa się z 460 posłów.

The Sejm consists of 460 Deputies.
"""

SENATE_SENATORS: int = 100
"""Art. 97 ust. 1: Senat składa się z 100 senatorów.

The Senate consists of 100 Senators.
"""

SEJM_TERM_YEARS: int = 4
"""Art. 98 ust. 1: Sejm i Senat są wybierane na czteroletnie kadencje.

The Sejm and Senate are elected for 4-year terms.
"""

# ---------------------------------------------------------------------------
# Incompatibilitas — Art. 103
# ---------------------------------------------------------------------------

INCOMPATIBLE_WITH_DEPUTY: tuple[str, ...] = (
    "Senator",
    "President of the National Bank of Poland",
    "President of the Supreme Chamber of Control",
    "Commissioner for Citizens' Rights",
    "Commissioner for Children's Rights",
    "Member of the Council for Monetary Policy",
    "Member of the National Council of Radio Broadcasting and Television",
    "Ambassador",
    "Civil servant",
    "Soldier on active duty",
    "Police officer",
    "Security services officer",
)
"""Art. 103: Mandatu posła nie można łączyć z funkcją Prezesa Narodowego
Banku Polskiego, Prezesa Najwyższej Izby Kontroli, Rzecznika Praw
Obywatelskich, Rzecznika Praw Dziecka i ich zastępców, członka Rady
Polityki Pieniężnej, członka Krajowej Rady Radiofonii i Telewizji,
ambasadora oraz z zatrudnieniem w Kancelarii Sejmu, Kancelarii Senatu,
Kancelarii Prezydenta Rzeczypospolitej lub z zatrudnieniem w administracji
rządowej. Zakaz ten nie dotyczy członków Rady Ministrów i sekretarzy stanu
w administracji rządowej.

A Deputy's mandate may not be held jointly with the above offices.
"""

# ---------------------------------------------------------------------------
# Eligibility (Art. 99)
# ---------------------------------------------------------------------------


def check_sejm_eligibility(citizen: Citizen, election_date: date) -> bool:
    """Verify eligibility for the Sejm (Art. 99 ust. 1, 3).

    Art. 99 ust. 1: Wybrany do Sejmu może być obywatel polski mający prawo
    wybierania, który najpóźniej w dniu wyborów kończy 21 lat.

    Art. 99(1): Every Polish citizen having the right to vote who has attained
    21 years of age by the day of elections may be elected to the Sejm.

    Art. 99 ust. 3 [dodany nowelizacją z 7 maja 2009 r., Dz.U. 2009 nr 114
    poz. 946]: Wybraną do Sejmu lub do Senatu nie może być osoba skazana
    prawomocnym wyrokiem na karę pozbawienia wolności za przestępstwo umyślne
    ścigane z oskarżenia publicznego.

    Art. 99(3) [added by amendment of 7 May 2009]: A person sentenced to
    imprisonment by a final judgment for an intentional crime prosecuted
    ex officio may not be elected to the Sejm or the Senate.

    Conditions:
    - Polish citizen
    - At least 21 years old on election day
    - No criminal conviction for intentional crime prosecuted ex officio
      (Art. 99(3), 2009 amendment)
    """
    errors: list[str] = []

    if not citizen.polish_citizen:
        errors.append("must be a Polish citizen")
    if citizen.age_at(election_date) < 21:
        errors.append(f"must be at least 21 (is {citizen.age_at(election_date)})")
    if citizen.criminal_record:
        errors.append(
            "convicted by final judgment for an intentional crime prosecuted "
            "ex officio (Art. 99(3), nowelizacja 2009)"
        )

    if errors:
        raise EligibilityError(
            f"{citizen.name} ineligible for Sejm: {'; '.join(errors)}",
            article="99(1)",
        )
    return True


def check_senate_eligibility(citizen: Citizen, election_date: date) -> bool:
    """Verify eligibility for the Senate (Art. 99 ust. 2, 3).

    Art. 99 ust. 2: Wybrany do Senatu może być obywatel polski mający prawo
    wybierania, który najpóźniej w dniu wyborów kończy 30 lat.

    Art. 99(2): Every Polish citizen having the right to vote who has attained
    30 years of age by the day of elections may be elected to the Senate.

    Art. 99 ust. 3 [dodany nowelizacją z 7 maja 2009 r.]: see
    check_sejm_eligibility docstring for full text.

    Art. 99(3) [added by amendment of 7 May 2009]: A person sentenced to
    imprisonment by a final judgment for an intentional crime prosecuted
    ex officio may not be elected to the Sejm or the Senate.
    """
    errors: list[str] = []

    if not citizen.polish_citizen:
        errors.append("must be a Polish citizen")
    if citizen.age_at(election_date) < 30:
        errors.append(f"must be at least 30 (is {citizen.age_at(election_date)})")
    if citizen.criminal_record:
        errors.append(
            "convicted by final judgment for an intentional crime prosecuted "
            "ex officio (Art. 99(3), nowelizacja 2009)"
        )

    if errors:
        raise EligibilityError(
            f"{citizen.name} ineligible for Senate: {'; '.join(errors)}",
            article="99(2)",
        )
    return True


# ---------------------------------------------------------------------------
# Bill passage (Art. 120–121)
# ---------------------------------------------------------------------------


def sejm_passes_bill(vote: VoteRecord) -> bool:
    """Check if the Sejm passes a bill by simple majority with quorum.

    Art. 120: Sejm uchwala ustawy zwykłą większością głosów w obecności
    co najmniej połowy ustawowej liczby posłów.

    Art. 120: The Sejm shall pass bills by a simple majority vote, in the
    presence of at least half the statutory number of Deputies.
    """
    assert vote.chamber == Chamber.SEJM, "Vote must be from the Sejm"
    return passes_vote(vote, MajorityType.SIMPLE)


def senate_passes_bill(vote: VoteRecord) -> bool:
    """Check if the Senate passes a bill (absolute majority to reject/amend).

    Art. 121 ust. 3: Uchwałę Senatu odrzucającą ustawę albo poprawkę
    zaproponowaną w uchwale Senatu uważa się za przyjętą, jeżeli Sejm nie
    odrzuci jej bezwzględną większością głosów.

    Art. 121(3): A resolution of the Senate rejecting a bill, or an amendment
    proposed in a Senate resolution, shall be considered accepted unless the
    Sejm rejects it by an absolute majority vote.
    """
    assert vote.chamber == Chamber.SENATE, "Vote must be from the Senate"
    return passes_vote(vote, MajorityType.SIMPLE)


def sejm_overrides_senate(vote: VoteRecord) -> bool:
    """Check if the Sejm overrides a Senate rejection/amendment.

    Art. 121 ust. 3: requires absolute majority in the Sejm to override.
    """
    assert vote.chamber == Chamber.SEJM, "Override vote must be from the Sejm"
    return passes_vote(vote, MajorityType.ABSOLUTE)


# ---------------------------------------------------------------------------
# Incompatibilitas — Art. 103
# ---------------------------------------------------------------------------


def check_incompatibility(office: str) -> bool:
    """Check whether an office is incompatible with a parliamentary mandate.

    Art. 103 ust. 1: Mandatu posła nie można łączyć z funkcją…
    A Deputy's mandate may not be held jointly with certain offices.

    Art. 108: Applies correspondingly to Senators.

    Args:
        office: The office the deputy/senator is attempting to hold.

    Raises:
        IncompatibilityError: If the office is incompatible with a mandate.
    """
    if office in INCOMPATIBLE_WITH_DEPUTY:
        raise IncompatibilityError(
            f"A parliamentary mandate cannot be held jointly with the office "
            f"of '{office}'.",
            article="103",
        )
    return True


# ---------------------------------------------------------------------------
# Parliamentary immunity — Art. 105
# ---------------------------------------------------------------------------


def validate_parliamentary_immunity(
    chamber: Chamber,
    consent_given: bool,
) -> bool:
    """Check whether prosecution of a deputy/senator is permitted.

    Art. 105 ust. 2: Od dnia ogłoszenia wyników wyborów do dnia wygaśnięcia
    mandatu poseł nie może być pociągnięty bez zgody Sejmu do
    odpowiedzialności karnej.

    Art. 105(2): From the day of announcement of election results until the
    day of expiry of the mandate, a Deputy cannot be held criminally
    accountable without the consent of the Sejm.

    Art. 108: Applies correspondingly to Senators (with Senate consent).

    Args:
        chamber: Which chamber's consent is required.
        consent_given: Whether the chamber has given consent.

    Raises:
        ImmunityError: If prosecution is attempted without consent.
    """
    if not consent_given:
        chamber_name = "Sejm" if chamber == Chamber.SEJM else "Senate"
        raise ImmunityError(
            f"Criminal prosecution requires consent of the {chamber_name}. "
            f"Immunity protects the member until consent is granted.",
            article="105",
        )
    return True


# ---------------------------------------------------------------------------
# National referendum — Art. 125
# ---------------------------------------------------------------------------

REFERENDUM_BINDING_TURNOUT = 2
"""Art. 125 ust. 3: Jeżeli w referendum ogólnokrajowym wzięło udział więcej
niż połowa uprawnionych do głosowania, wynik referendum jest wiążący.

If more than half of those eligible to vote participate, the result is binding.
The threshold is expressed as: eligible * 2 > total_eligible (i.e. >50%).
"""


def validate_referendum(
    votes_for: int,
    votes_against: int,
    eligible_voters: int,
) -> bool:
    """Validate a national referendum result (Art. 125).

    Art. 125 ust. 1: W sprawach o szczególnym znaczeniu dla państwa może
    być przeprowadzone referendum ogólnokrajowe.

    Art. 125(1): A nationwide referendum may be held in respect of matters
    of particular importance to the State.

    Art. 125 ust. 3: The result is binding if turnout exceeds 50%.

    Args:
        votes_for: Votes in favour.
        votes_against: Votes against.
        eligible_voters: Total number of eligible voters.

    Returns:
        True if the referendum passes with binding turnout.

    Raises:
        ReferendumError: If turnout is insufficient or the motion fails.
    """
    if eligible_voters <= 0:
        raise ReferendumError(
            "Number of eligible voters must be positive.",
            article="125",
        )

    total_votes = votes_for + votes_against

    # Art. 125(3): binding only if turnout > 50%
    if total_votes * 2 <= eligible_voters:
        raise ReferendumError(
            f"Referendum not binding: turnout {total_votes}/{eligible_voters} "
            f"does not exceed 50%.",
            article="125(3)",
        )

    if votes_for <= votes_against:
        raise ReferendumError(
            f"Referendum rejected: {votes_for} for vs {votes_against} against.",
            article="125",
        )

    return True
