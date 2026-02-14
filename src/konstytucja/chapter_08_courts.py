"""Chapter VIII — Courts and Tribunals (Art. 173–201).

Rozdział VIII — Sądy i Trybunały.

This module covers:
- Ordinary courts, the Supreme Court, administrative and military courts
  (Art. 173–187)
- The Constitutional Tribunal (Trybunał Konstytucyjny, Art. 188–197)
- The State Tribunal (Trybunał Stanu, Art. 198–201)
"""

from konstytucja.common.errors import JudicialError, StateTribunalError, TribunalError
from konstytucja.common.types import (
    CourtType,
    Judge,
    TribunalVerdict,
    TribunalVerdictType,
)

# ---------------------------------------------------------------------------
# Courts — structure and independence (Art. 173–187)
# ---------------------------------------------------------------------------

COURT_TYPES: tuple[CourtType, ...] = (
    CourtType.SUPREME,
    CourtType.COMMON,
    CourtType.ADMINISTRATIVE,
    CourtType.MILITARY,
)
"""Art. 175 ust. 1: Wymiar sprawiedliwości w Rzeczypospolitej Polskiej
sprawują Sąd Najwyższy, sądy powszechne, sądy administracyjne oraz
sądy wojskowe.

Justice in the Republic of Poland is administered by the Supreme Court,
common courts, administrative courts, and military courts.
"""

MIN_INSTANCES: int = 2
"""Art. 176 ust. 1: Postępowanie sądowe jest co najmniej dwuinstancyjne.

Court proceedings have at least two instances.
"""

KRS_MEMBERS: int = 25
"""Art. 187 ust. 1: Krajowa Rada Sądownictwa składa się z 25 członków.

The National Council of the Judiciary consists of 25 members.
"""

KRS_TERM_YEARS: int = 4
"""Art. 187 ust. 3: Kadencja wybranych członków Krajowej Rady Sądownictwa
trwa 4 lata.

The term of elected members of the KRS is 4 years.
"""


def validate_judge_appointment(judge: Judge) -> bool:
    """Validate that a judge is properly appointed.

    Art. 179: Sędziowie są powoływani przez Prezydenta Rzeczypospolitej,
    na wniosek Krajowej Rady Sądownictwa, na czas nieoznaczony.

    Judges are appointed by the President of the Republic, on the proposal
    of the National Council of the Judiciary, for an indefinite period.

    Raises:
        JudicialError: If the appointment procedure is violated.
    """
    if not judge.appointed_by_president:
        raise JudicialError(
            "Judges must be appointed by the President of the Republic.",
            article="179",
        )
    if not judge.krs_nominated:
        raise JudicialError(
            "Judges must be nominated by the National Council of the "
            "Judiciary (Krajowa Rada Sądownictwa).",
            article="179",
        )
    return True


def validate_judicial_independence(subject_to: str) -> bool:
    """Check that judges are subject only to the Constitution and statutes.

    Art. 178 ust. 1: Sędziowie w sprawowaniu swojego urzędu są niezawiśli
    i podlegają tylko Konstytucji oraz ustawom.

    In the exercise of their office, judges are independent and subject
    only to the Constitution and statutes.

    Args:
        subject_to: What the judge is declared subject to (e.g.
            "Constitution and statutes", "executive orders").

    Raises:
        JudicialError: If the judge is subject to anything other than
            the Constitution and statutes.
    """
    allowed = {"Constitution and statutes", "Konstytucja i ustawy"}
    if subject_to not in allowed:
        raise JudicialError(
            f"Judges are independent and subject only to the Constitution "
            f"and statutes, not '{subject_to}'.",
            article="178",
        )
    return True


def check_two_instance_requirement(instances: int) -> bool:
    """Verify that court proceedings meet the two-instance requirement.

    Art. 176 ust. 1: Postępowanie sądowe jest co najmniej dwuinstancyjne.

    Court proceedings shall have at least two instances.

    Raises:
        JudicialError: If fewer than two instances are provided.
    """
    if instances < MIN_INSTANCES:
        raise JudicialError(
            f"Court proceedings must have at least {MIN_INSTANCES} instances "
            f"(Art. 176(1)), got {instances}.",
            article="176",
        )
    return True

# ---------------------------------------------------------------------------
# Constitutional Tribunal — composition (Art. 194)
# ---------------------------------------------------------------------------

TRIBUNAL_JUDGES: int = 15
"""Art. 194 ust. 1: Trybunał Konstytucyjny składa się z 15 sędziów.

The Constitutional Tribunal consists of 15 judges.
"""

TRIBUNAL_TERM_YEARS: int = 9
"""Art. 194 ust. 1: wybieranych indywidualnie przez Sejm na 9 lat.

Judges are individually elected by the Sejm for a term of 9 years.
"""

# ---------------------------------------------------------------------------
# Petitioners — who may bring cases (Art. 191)
# ---------------------------------------------------------------------------

PETITIONERS: tuple[str, ...] = (
    "President",
    "Speaker of the Sejm",
    "Speaker of the Senate",
    "Prime Minister",
    "50 Deputies",
    "30 Senators",
    "First President of the Supreme Court",
    "President of the Supreme Administrative Court",
    "Prosecutor General",
    "President of the Supreme Chamber of Control",
    "Commissioner for Citizens' Rights",
)
"""Art. 191 ust. 1: Podmioty uprawnione do występowania z wnioskiem.

Entities authorised to bring a case before the Constitutional Tribunal.
"""


def validate_petitioner(petitioner: str) -> None:
    """Check that the petitioner is authorised to bring a case (Art. 191).

    Art. 191 ust. 1: Z wnioskiem w sprawach, o których mowa w art. 188,
    do Trybunału Konstytucyjnego wystąpić mogą: Prezydent Rzeczypospolitej,
    Marszałek Sejmu, Marszałek Senatu, Prezes Rady Ministrów, 50 posłów,
    30 senatorów, Pierwszy Prezes Sądu Najwyższego, Prezes Naczelnego Sądu
    Administracyjnego, Prokurator Generalny, Prezes Najwyższej Izby Kontroli,
    Rzecznik Praw Obywatelskich.

    Raises:
        TribunalError: If the petitioner is not on the authorised list.
    """
    if petitioner not in PETITIONERS:
        raise TribunalError(
            f"'{petitioner}' is not authorised to petition the Constitutional Tribunal. "
            f"Authorised petitioners: {', '.join(PETITIONERS)}",
            article="191",
        )


def validate_tribunal_verdict(verdict: TribunalVerdict) -> None:
    """Validate internal consistency of a Tribunal verdict.

    Rules:
    - A PARTIALLY_UNCONSTITUTIONAL verdict must list at least one
      unconstitutional provision.
    - A fully UNCONSTITUTIONAL verdict should not list individual provisions
      (the entire act is struck down).
    - A CONSTITUTIONAL verdict should not list unconstitutional provisions.

    Raises:
        TribunalError: If the verdict is internally inconsistent.
    """
    if (
        verdict.verdict == TribunalVerdictType.PARTIALLY_UNCONSTITUTIONAL
        and not verdict.unconstitutional_provisions
    ):
        raise TribunalError(
            "A partially unconstitutional verdict must specify "
            "which provisions are unconstitutional.",
            article="190",
        )
    if (
        verdict.verdict == TribunalVerdictType.UNCONSTITUTIONAL
        and verdict.unconstitutional_provisions
    ):
        raise TribunalError(
            "A fully unconstitutional verdict should not list individual "
            "provisions — the entire act is struck down.",
            article="190",
        )
    if (
        verdict.verdict == TribunalVerdictType.CONSTITUTIONAL
        and verdict.unconstitutional_provisions
    ):
        raise TribunalError(
            "A constitutional verdict cannot list unconstitutional provisions.",
            article="190",
        )


def verdict_is_final(verdict: TribunalVerdict) -> bool:
    """Art. 190 ust. 1: Judgments are universally binding and final.

    Orzeczenia Trybunału Konstytucyjnego mają moc powszechnie obowiązującą
    i są ostateczne.

    This function validates the verdict and confirms finality.
    Always returns True for a valid verdict — the Constitution does not
    provide for appeal of Tribunal judgments.

    Raises:
        TribunalError: If the verdict is internally inconsistent.
    """
    validate_tribunal_verdict(verdict)
    return True


# ---------------------------------------------------------------------------
# State Tribunal — Trybunał Stanu (Art. 198–201)
# ---------------------------------------------------------------------------

STATE_TRIBUNAL_CHAIR: str = "First President of the Supreme Court"
"""Art. 199 ust. 1: Trybunał Stanu składa się z przewodniczącego, którym
jest Pierwszy Prezes Sądu Najwyższego…

The State Tribunal is chaired by the First President of the Supreme Court.
"""

STATE_TRIBUNAL_MEMBERS: int = 19
"""Art. 199 ust. 1: …2 zastępców przewodniczącego i 16 członków wybieranych
przez Sejm spoza grona posłów i senatorów na czas kadencji Sejmu.

The State Tribunal has a chair + 2 deputy chairs + 16 members = 19 total,
elected by the Sejm from outside its ranks for the duration of the Sejm's term.
"""

STATE_TRIBUNAL_SUBJECTS: tuple[str, ...] = (
    "President",
    "Prime Minister",
    "Minister",
    "President of the National Bank of Poland",
    "President of the Supreme Chamber of Control",
    "Member of the National Council of Radio Broadcasting and Television",
    "Commander-in-Chief of the Armed Forces",
    "Deputy",
    "Senator",
)
"""Art. 198: Za naruszenie Konstytucji lub ustawy, w związku z zajmowanym
stanowiskiem lub w zakresie swojego urzędowania, odpowiedzialność
konstytucyjną przed Trybunałem Stanu ponoszą:

Art. 198: For violations of the Constitution or statutes in connection
with their office, the following are constitutionally accountable before
the State Tribunal.

Note: Deputies and Senators (Art. 198(2)) are accountable only for
violating the prohibition on business activity involving State property.
"""


def validate_state_tribunal_subject(subject: str) -> bool:
    """Check whether a person holds an office subject to State Tribunal jurisdiction.

    Art. 198: Lists the officials who are constitutionally accountable
    before the State Tribunal (Trybunał Stanu).

    Args:
        subject: The office held by the person.

    Raises:
        StateTribunalError: If the office is not subject to State Tribunal
            jurisdiction.
    """
    if subject not in STATE_TRIBUNAL_SUBJECTS:
        raise StateTribunalError(
            f"'{subject}' is not subject to State Tribunal jurisdiction. "
            f"Accountable offices: {', '.join(STATE_TRIBUNAL_SUBJECTS)}",
            article="198",
        )
    return True


def validate_state_tribunal_composition(
    members_elected: int,
    from_outside_parliament: bool,
) -> bool:
    """Validate the composition of the State Tribunal.

    Art. 199 ust. 1–2: The State Tribunal consists of 19 members elected
    by the Sejm from outside the ranks of Deputies and Senators. At least
    half the members must have judicial qualifications.

    Args:
        members_elected: Number of members elected by the Sejm.
        from_outside_parliament: Whether members are from outside Sejm/Senate.

    Raises:
        StateTribunalError: If the composition is invalid.
    """
    if members_elected != STATE_TRIBUNAL_MEMBERS:
        raise StateTribunalError(
            f"State Tribunal must have {STATE_TRIBUNAL_MEMBERS} members "
            f"(chair + 2 deputies + 16 elected), got {members_elected}.",
            article="199",
        )
    if not from_outside_parliament:
        raise StateTribunalError(
            "State Tribunal members must be elected from outside the ranks "
            "of Deputies and Senators.",
            article="199",
        )
    return True
