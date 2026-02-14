"""Rozdział I: Rzeczpospolita / Chapter I: The Republic (Art. 1–29).

Zasady ustrojowe, trójpodział władzy, organy państwowe.
Fundamental principles, separation of powers, state organs.
"""

from enum import Enum, auto

from konstytucja.common.types import Branch


class Principle(Enum):
    """Zasady ustrojowe RP / Fundamental principles of the Republic.

    Art. 1: Rzeczpospolita Polska jest dobrem wspólnym wszystkich obywateli.
    Art. 1: The Republic of Poland shall be the common good of all its citizens.

    Art. 2: Rzeczpospolita Polska jest demokratycznym państwem prawnym,
    urzeczywistniającym zasady sprawiedliwości społecznej.
    Art. 2: The Republic of Poland shall be a democratic state ruled by law
    and implementing the principles of social justice.
    """
    COMMON_GOOD = auto()                # Art. 1 — dobro wspólne
    DEMOCRATIC_RULE_OF_LAW = auto()     # Art. 2 — demokratyczne państwo prawne
    SOCIAL_JUSTICE = auto()             # Art. 2 — sprawiedliwość społeczna
    SOVEREIGNTY_OF_NATION = auto()      # Art. 4 — władza zwierzchnia należy do Narodu
    SEPARATION_OF_POWERS = auto()       # Art. 10 — podział i równowaga władz
    POLITICAL_PLURALISM = auto()        # Art. 11 — wolność tworzenia partii
    DECENTRALIZATION = auto()           # Art. 15 — decentralizacja władzy publicznej
    LOCAL_SELF_GOVERNMENT = auto()      # Art. 16 — samorząd terytorialny
    RELIGIOUS_NEUTRALITY = auto()       # Art. 25 — bezstronność władz publicznych


class StateOrgan(Enum):
    """Organy państwowe / State organs referenced in the Constitution."""
    SEJM = auto()
    SENATE = auto()
    PRESIDENT = auto()
    COUNCIL_OF_MINISTERS = auto()       # Rada Ministrów
    PRIME_MINISTER = auto()            # Prezes Rady Ministrów
    CONSTITUTIONAL_TRIBUNAL = auto()   # Trybunał Konstytucyjny
    SUPREME_COURT = auto()             # Sąd Najwyższy
    NIK = auto()                       # Najwyższa Izba Kontroli
    NBP = auto()                       # Narodowy Bank Polski
    RPO = auto()                       # Rzecznik Praw Obywatelskich (Ombudsman)


# Art. 10: mapping of branches to their organs
BRANCH_ORGANS: dict[Branch, list[StateOrgan]] = {
    Branch.LEGISLATIVE: [StateOrgan.SEJM, StateOrgan.SENATE],
    Branch.EXECUTIVE: [StateOrgan.PRESIDENT, StateOrgan.COUNCIL_OF_MINISTERS],
    Branch.JUDICIAL: [StateOrgan.CONSTITUTIONAL_TRIBUNAL, StateOrgan.SUPREME_COURT],
}


def organs_for_branch(branch: Branch) -> list[StateOrgan]:
    """Return the state organs belonging to a given branch.

    Art. 10: Ustrój Rzeczypospolitej Polskiej opiera się na podziale
    i równowadze władzy ustawodawczej, władzy wykonawczej i władzy sądowniczej.

    Art. 10: The system of government of the Republic of Poland shall be based
    on the separation of and balance between the legislative, executive, and
    judicial powers.
    """
    return BRANCH_ORGANS[branch]


def branch_of_organ(organ: StateOrgan) -> Branch | None:
    """Return the branch a given organ belongs to, or None if independent."""
    for branch, organs in BRANCH_ORGANS.items():
        if organ in organs:
            return branch
    return None
