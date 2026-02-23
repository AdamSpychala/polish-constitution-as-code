"""Shared types for the constitutional code.

Typy współdzielone — enumy, dataklasy, aliasy typów.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum, auto

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Chamber(Enum):
    """Izba parlamentu / Chamber of parliament."""
    SEJM = "Sejm"
    SENATE = "Senat"


class MajorityType(Enum):
    """Typy większości przewidziane w Konstytucji.

    Majority types specified in the Constitution.
    """
    SIMPLE = auto()       # Art. 120: zwykła większość
    ABSOLUTE = auto()     # > 1/2 ustawowej liczby
    TWO_THIRDS = auto()   # 2/3 głosów
    THREE_FIFTHS = auto() # 3/5 głosów


class Branch(Enum):
    """Trójpodział władzy / Separation of powers (Art. 10)."""
    LEGISLATIVE = "władza ustawodawcza"
    EXECUTIVE = "władza wykonawcza"
    JUDICIAL = "władza sądownicza"


class LegalActType(Enum):
    """Typy aktów prawnych / Types of legal acts (Art. 87)."""
    CONSTITUTION = auto()
    STATUTE = auto()              # ustawa
    RATIFIED_TREATY = auto()      # ratyfikowana umowa międzynarodowa
    REGULATION = auto()           # rozporządzenie
    LOCAL_ACT = auto()            # akt prawa miejscowego


class EmergencyType(Enum):
    """Rodzaje stanów nadzwyczajnych / Types of emergency (Art. 228)."""
    MARTIAL_LAW = "stan wojenny"       # Art. 229
    STATE_OF_EMERGENCY = "stan wyjątkowy"  # Art. 230
    NATURAL_DISASTER = "stan klęski żywiołowej"  # Art. 232


class GovernmentFormationStage(Enum):
    """Etapy tworzenia rządu / Government formation stages (Art. 154–155)."""
    PRESIDENT_DESIGNATES = auto()     # Art. 154(1): President designates PM
    CONFIDENCE_VOTE = auto()          # Art. 154(2): Sejm vote of confidence
    SEJM_ELECTS = auto()              # Art. 155(1): Sejm elects PM if first attempt fails
    PRESIDENT_APPOINTS_RETRY = auto() # Art. 155(2): President appoints, Sejm votes simple majority
    APPOINTED = auto()
    FAILED = auto()                   # Sejm dissolved (Art. 155(2))


class CourtType(Enum):
    """Rodzaje sądów / Types of courts (Art. 175)."""
    SUPREME = "Sąd Najwyższy"
    COMMON = "sądy powszechne"
    ADMINISTRATIVE = "sądy administracyjne"
    MILITARY = "sądy wojskowe"


class LocalGovernmentTier(Enum):
    """Jednostki samorządu terytorialnego / Local government tiers."""
    GMINA = "gmina"         # commune — Art. 164(1): basic unit
    POWIAT = "powiat"       # county
    WOJEWODZTWO = "województwo"  # voivodeship


class OversightOrgan(Enum):
    """Organy kontroli państwowej / State oversight organs (Art. 202–215)."""
    NIK = "Najwyższa Izba Kontroli"           # Art. 202–207
    RPO = "Rzecznik Praw Obywatelskich"        # Art. 208–212
    KRRIT = "Krajowa Rada Radiofonii i Telewizji"  # Art. 213–215


class TribunalCaseType(Enum):
    """Types of matters the Tribunal adjudicates (Art. 188).

    Rodzaje spraw rozpatrywanych przez Trybunał Konstytucyjny.
    """
    STATUTE_CONFORMITY = "conformity of statute with Constitution"
    TREATY_CONFORMITY = "conformity of international agreement with Constitution"
    REGULATION_CONFORMITY = "conformity of regulation with Constitution/statutes"
    PARTY_AIMS = "conformity of aims of political party with Constitution"


class TribunalVerdictType(Enum):
    """Possible outcomes of Tribunal review.

    Możliwe rozstrzygnięcia Trybunału Konstytucyjnego.
    """
    CONSTITUTIONAL = "constitutional"
    UNCONSTITUTIONAL = "unconstitutional"
    PARTIALLY_UNCONSTITUTIONAL = "partially unconstitutional"


class BillStage(Enum):
    """Etapy procesu legislacyjnego / Legislative process stages."""
    INITIATED = auto()
    SEJM_DELIBERATION = auto()
    SEJM_PASSED = auto()
    SENATE_DELIBERATION = auto()
    SENATE_PASSED = auto()
    SENATE_AMENDED = auto()
    SENATE_REJECTED = auto()
    SEJM_OVERRIDE_VOTE = auto()
    PRESIDENT_REVIEW = auto()
    SIGNED = auto()
    VETOED = auto()
    VETO_OVERRIDE_VOTE = auto()
    VETO_OVERRIDDEN = auto()
    REFERRED_TO_TRIBUNAL = auto()
    PARTIALLY_UNCONSTITUTIONAL = auto()
    ENACTED = auto()
    REJECTED = auto()


class AmendmentStage(Enum):
    """Etapy zmiany Konstytucji / Amendment procedure stages (Art. 235)."""
    INITIATED = auto()
    FIRST_READING_SEJM = auto()
    SEJM_PASSED = auto()
    SENATE_PASSED = auto()
    REFERENDUM_REQUESTED = auto()
    REFERENDUM_PASSED = auto()
    PRESIDENT_SIGNS = auto()
    ADOPTED = auto()
    REJECTED = auto()


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Citizen:
    """Obywatel RP / Polish citizen."""
    name: str
    date_of_birth: date
    polish_citizen: bool = True
    # Art. 99(3) [nowelizacja 2009]: prawomocny wyrok za przestępstwo
    # umyślne ścigane z oskarżenia publicznego
    criminal_record: bool = False

    @property
    def age_on(self) -> _AgeLookup:
        """Return an age-lookup helper: citizen.age_on[date]."""
        return _AgeLookup(self.date_of_birth)

    def age_at(self, on_date: date) -> int:
        """Wiek w dniu / Age on a given date."""
        born = self.date_of_birth
        age = on_date.year - born.year
        if (on_date.month, on_date.day) < (born.month, born.day):
            age -= 1
        return age


class _AgeLookup:
    """Helper so you can write citizen.age_on[some_date]."""

    def __init__(self, dob: date):
        self._dob = dob

    def __getitem__(self, on_date: date) -> int:
        age = on_date.year - self._dob.year
        if (on_date.month, on_date.day) < (self._dob.month, self._dob.day):
            age -= 1
        return age


@dataclass(frozen=True)
class VoteRecord:
    """Wynik głosowania / Vote record."""
    chamber: Chamber
    votes_for: int
    votes_against: int
    votes_abstain: int = 0
    statutory_members: int | None = None  # ustawowa liczba członków

    @property
    def total_present(self) -> int:
        return self.votes_for + self.votes_against + self.votes_abstain

    @property
    def members(self) -> int:
        """Statutory number of members for the chamber."""
        if self.statutory_members is not None:
            return self.statutory_members
        match self.chamber:
            case Chamber.SEJM:
                return 460
            case Chamber.SENATE:
                return 100


@dataclass(frozen=True)
class Bill:
    """Projekt ustawy / Legislative bill."""
    title: str
    sponsor: str
    urgent: bool = False


@dataclass(frozen=True)
class PublicDebt:
    """Stan finansów publicznych / Public finance state (Art. 216)."""
    debt: Decimal
    gdp: Decimal


@dataclass(frozen=True)
class EmergencyDeclaration:
    """Wprowadzenie stanu nadzwyczajnego / Emergency declaration (Art. 228)."""
    emergency_type: EmergencyType
    start_date: date
    duration_days: int
    reason: str


@dataclass(frozen=True)
class RightsRestriction:
    """Ograniczenie praw i wolności / Rights restriction proposal (Art. 31 ust. 3).

    The five conditions for a constitutionally valid restriction:
    1. by_statute — only by statute (ustawa)
    2. necessary_in_democratic_state — necessary in a democratic state
    3. legitimate_aim — pursues a legitimate aim (security, public order,
       environment, health, public morals, or freedoms of others)
    4. proportionate — proportionate to the aim pursued
    5. preserves_essence — does not affect the essence of the right
    """
    description: str
    by_statute: bool = False
    necessary_in_democratic_state: bool = False
    legitimate_aim: bool = False
    proportionate: bool = False
    preserves_essence: bool = False


@dataclass(frozen=True)
class TribunalVerdict:
    """Result of Constitutional Tribunal adjudication (Art. 190).

    Orzeczenie Trybunału Konstytucyjnego.
    Art. 190 ust. 1: Orzeczenia Trybunału Konstytucyjnego mają moc
    powszechnie obowiązującą i są ostateczne.
    """
    case_type: TribunalCaseType
    verdict: TribunalVerdictType
    reasoning: str
    unconstitutional_provisions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Minister:
    """Członek Rady Ministrów / Member of the Council of Ministers (Art. 147)."""
    name: str
    role: str  # e.g. "Prime Minister", "Minister of Finance"


@dataclass(frozen=True)
class CouncilOfMinisters:
    """Rada Ministrów / Council of Ministers (Art. 147).

    Art. 147: Rada Ministrów składa się z Prezesa Rady Ministrów
    i ministrów.
    The Council of Ministers consists of the Prime Minister and ministers.
    """
    prime_minister: Minister
    ministers: tuple[Minister, ...]


@dataclass(frozen=True)
class Judge:
    """Sędzia / Judge (Art. 179).

    Art. 179: Sędziowie są powoływani przez Prezydenta Rzeczypospolitej,
    na wniosek Krajowej Rady Sądownictwa.
    Judges are appointed by the President on the proposal of the
    National Council of the Judiciary.
    """
    name: str
    court_type: CourtType
    appointed_by_president: bool = True  # Art. 179
    krs_nominated: bool = True           # Art. 179


@dataclass(frozen=True)
class LocalGovernmentUnit:
    """Jednostka samorządu terytorialnego / Local government unit (Art. 164).

    Art. 164 ust. 1: Podstawową jednostką samorządu terytorialnego jest gmina.
    The commune (gmina) shall be the basic unit of local government.
    """
    name: str
    tier: LocalGovernmentTier
    term_years: int = 4  # Art. 169(2)


@dataclass(frozen=True)
class OversightAppointment:
    """Powołanie na stanowisko organu kontroli / Oversight organ appointment.

    Art. 205, 209, 214: Appointments to NIK, RPO, KRRiT.
    """
    organ: OversightOrgan
    name: str
    sejm_approved: bool = False
    senate_approved: bool = False
