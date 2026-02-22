"""Rozdział II: Wolności, prawa i obowiązki / Chapter II: Rights and Freedoms (Art. 30–86).

Art. 31 ust. 3 — test proporcjonalności ograniczenia praw i wolności.
Art. 31(3) — proportionality test for restricting rights and freedoms.

Art. 55 [nowelizacja 2006] — zasady ekstradycji.
Art. 55 [2006 amendment] — extradition rules.
"""

from konstytucja.common.errors import ExtraditionError, RightsRestrictionError
from konstytucja.common.types import ExtraditionRequest, RightsRestriction


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


# ---------------------------------------------------------------------------
# Extradition — Art. 55 [nowelizacja z 8 września 2006 r.]
# ---------------------------------------------------------------------------


def validate_extradition(request: ExtraditionRequest) -> bool:
    """Validate an extradition request against Art. 55.

    Art. 55 [zmieniony ustawą z dnia 8 września 2006 r., Dz.U. 2006 nr 200
    poz. 1471]:

    Art. 55 ust. 1: Ekstradycja obywatela polskiego jest zakazana,
    z wyjątkiem przypadków określonych w ust. 2 i 3.

    Art. 55 ust. 2: Ekstradycja obywatela polskiego może być dokonana na
    wniosek innego państwa lub sądowego organu międzynarodowego, jeżeli
    możliwość taka wynika z ratyfikowanej przez Rzeczpospolitą Polską umowy
    międzynarodowej lub ustawy wykonującej akt prawa stanowiony przez
    organizację międzynarodową, której Rzeczpospolita Polska jest członkiem,
    pod warunkiem że czyn objęty wnioskiem o ekstradycję:
      1) został popełniony poza terytorium Rzeczypospolitej Polskiej, oraz
      2) stanowił przestępstwo według prawa Rzeczypospolitej Polskiej lub
         stanowiłby przestępstwo według prawa Rzeczypospolitej Polskiej
         w razie popełnienia na terytorium Rzeczypospolitej Polskiej,
         zarówno w czasie jego popełnienia, jak i w chwili złożenia wniosku.

    Art. 55 ust. 3: Nie wymaga spełnienia warunków określonych w ust. 2
    pkt 1 i 2 ekstradycja mająca nastąpić na wniosek sądowego organu
    międzynarodowego powołanego na podstawie ratyfikowanej przez
    Rzeczpospolitą Polską umowy międzynarodowej, w związku z objętą
    jurysdykcją tego organu zbrodnią ludobójstwa, zbrodnią przeciwko
    ludzkości, zbrodnią wojenną lub zbrodnią agresji.

    Art. 55 ust. 4: Ekstradycja jest zakazana, jeżeli dotyczy osoby
    podejrzanej o popełnienie bez użycia przemocy przestępstwa z przyczyn
    politycznych lub jeżeli jej dokonanie będzie naruszać wolności i prawa
    człowieka i obywatela.

    Art. 55 ust. 5: W sprawie dopuszczalności ekstradycji orzeka sąd.

    ---

    Art. 55(1): Extradition of a Polish citizen is prohibited, except as
    specified in paragraphs 2 and 3.

    Art. 55(2): Extradition of a Polish citizen may be granted upon request
    of a foreign state or international judicial body, if such possibility
    stems from a ratified international treaty or a statute implementing a
    legal instrument of an international organization of which Poland is a
    member, provided that the act covered by the request:
      1) was committed outside the territory of Poland, and
      2) constituted an offence under Polish law or would have constituted
         an offence under Polish law if committed in Poland, both at the
         time of commission and at the time the request is made.

    Art. 55(3): The conditions of paragraph 2(1) and 2(2) are not required
    for extradition upon request of an international judicial body
    established under a ratified international treaty, in connection with
    genocide, crimes against humanity, war crimes, or crimes of aggression
    within its jurisdiction.

    Art. 55(4): Extradition is prohibited if it concerns a person suspected
    of committing, without use of force, an offence for political reasons,
    or if granting it would violate human rights and freedoms.

    Art. 55(5): The court shall decide on the admissibility of extradition.

    Args:
        request: The extradition request to evaluate.

    Returns:
        True if the extradition is constitutionally permissible.

    Raises:
        ExtraditionError: with details of which rule is violated.
    """
    # Art. 55(4): absolute prohibitions — apply to all persons
    if request.political_nonviolent_offense:
        raise ExtraditionError(
            "Extradition prohibited: concerns a nonviolent political offence "
            "(przestępstwo bez użycia przemocy z przyczyn politycznych)",
            article="55(4)",
        )

    if request.violates_human_rights:
        raise ExtraditionError(
            "Extradition prohibited: would violate human rights and freedoms "
            "(naruszenie wolności i praw człowieka i obywatela)",
            article="55(4)",
        )

    # Art. 55(5): court must approve admissibility
    if not request.court_approved:
        raise ExtraditionError(
            "Extradition inadmissible: court has not ruled on admissibility "
            "(sąd nie orzekł o dopuszczalności ekstradycji)",
            article="55(5)",
        )

    # Non-citizens: no further constitutional restrictions
    if not request.subject_is_polish_citizen:
        return True

    # Art. 55(3): ICC/international tribunal exception for gravest crimes
    if (
        request.international_judicial_body
        and request.based_on_ratified_treaty
        and request.genocide_or_war_crime
    ):
        return True

    # Art. 55(2): treaty-based extradition with conditions
    if request.based_on_ratified_treaty:
        failures: list[str] = []
        if not request.act_committed_abroad:
            failures.append(
                "act was not committed outside Polish territory (Art. 55(2)(1))"
            )
        if not request.double_criminality:
            failures.append(
                "act does not constitute an offence under Polish law (Art. 55(2)(2))"
            )
        if failures:
            detail = "; ".join(failures)
            raise ExtraditionError(
                f"Extradition of Polish citizen denied: {detail}",
                article="55(2)",
            )
        return True

    # Art. 55(1): default prohibition for Polish citizens
    raise ExtraditionError(
        "Extradition of a Polish citizen is prohibited "
        "(ekstradycja obywatela polskiego jest zakazana)",
        article="55(1)",
    )
