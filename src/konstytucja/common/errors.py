"""Constitutional error hierarchy.

Hierarchia błędów konstytucyjnych.
Every violation of a constitutional rule raises a typed exception
that references the specific article being violated.
"""


class ConstitutionalError(Exception):
    """Base exception for all constitutional violations.

    Bazowy wyjątek dla wszystkich naruszeń konstytucyjnych.
    """

    def __init__(self, message: str, article: str | None = None):
        self.article = article
        prefix = f"Art. {article}: " if article else ""
        super().__init__(f"{prefix}{message}")


class QuorumError(ConstitutionalError):
    """Brak kworum — quorum not met.

    Art. 120: Sejm uchwala ustawy zwykłą większością głosów
    w obecności co najmniej połowy ustawowej liczby posłów.
    """


class MajorityError(ConstitutionalError):
    """Wymagana większość nieosiągnięta — required majority not reached."""


class EligibilityError(ConstitutionalError):
    """Niespełnienie warunków wybieralności — eligibility criteria not met.

    Art. 99 (Sejm/Senate), Art. 127 (President).
    """


class LegalHierarchyError(ConstitutionalError):
    """Naruszenie hierarchii źródeł prawa — legal hierarchy violation.

    Art. 87–94: Konstytucja is the supreme law.
    """


class DebtCeilingError(ConstitutionalError):
    """Przekroczenie limitu długu publicznego — public debt ceiling exceeded.

    Art. 216 ust. 5: Nie wolno zaciągać pożyczek lub udzielać gwarancji
    i poręczeń finansowych, w następstwie których państwowy dług publiczny
    przekroczy 3/5 wartości rocznego produktu krajowego brutto.
    """


class EmergencyPowerError(ConstitutionalError):
    """Naruszenie zasad stanu nadzwyczajnego — emergency power violation.

    Art. 228–234.
    """


class AmendmentError(ConstitutionalError):
    """Naruszenie procedury zmiany Konstytucji — amendment procedure violation.

    Art. 235.
    """


class LegislativeProcessError(ConstitutionalError):
    """Naruszenie procesu legislacyjnego — legislative process violation.

    Art. 118–122.
    """


class RightsRestrictionError(ConstitutionalError):
    """Nieproporcjonalne ograniczenie praw — disproportionate rights restriction.

    Art. 31 ust. 3: Ograniczenia w zakresie korzystania z konstytucyjnych
    wolności i praw mogą być ustanawiane tylko w ustawie…
    """


class GovernmentFormationError(ConstitutionalError):
    """Naruszenie procedury tworzenia rządu — government formation violation.

    Art. 154–155.
    """


class NoConfidenceError(ConstitutionalError):
    """Naruszenie zasad wotum nieufności — no-confidence vote violation.

    Art. 158–159.
    """


class LocalGovernmentError(ConstitutionalError):
    """Naruszenie zasad samorządu terytorialnego — local government violation.

    Art. 163–172.
    """


class OversightError(ConstitutionalError):
    """Naruszenie zasad organów kontroli — oversight organ violation.

    Art. 202–215.
    """


class JudicialError(ConstitutionalError):
    """Naruszenie niezależności sądów — judicial independence violation.

    Art. 173–187.
    """


class IncompatibilityError(ConstitutionalError):
    """Naruszenie zakazu łączenia stanowisk — incompatibility of offices.

    Art. 103: Mandatu posła nie można łączyć z funkcją…
    """


class ImmunityError(ConstitutionalError):
    """Naruszenie immunitetu parlamentarnego — parliamentary immunity violation.

    Art. 105.
    """


class ReferendumError(ConstitutionalError):
    """Naruszenie zasad referendum — referendum violation.

    Art. 125.
    """


class StateTribunalError(ConstitutionalError):
    """Naruszenie zasad Trybunału Stanu — State Tribunal violation.

    Art. 198–201.
    """


class CentralBankError(ConstitutionalError):
    """Naruszenie niezależności banku centralnego — central bank independence violation.

    Art. 227.
    """


class TribunalError(ConstitutionalError):
    """Naruszenie zasad Trybunału Konstytucyjnego — Constitutional Tribunal violation.

    Art. 188–197.
    """


class ExtraditionError(ConstitutionalError):
    """Naruszenie zasad ekstradycji — extradition rule violation.

    Art. 55 [zmieniony nowelizacją z 8 września 2006 r.].
    Art. 55 [amended 8 September 2006].
    """
