"""Chapter VI — The Council of Ministers (Art. 146–162).

Rozdział VI — Rada Ministrów i administracja rządowa.

This module encodes the rules governing the composition of the Council
of Ministers, government formation procedure, confidence and no-confidence
votes, individual minister no-confidence, and minister liability.
"""

from dataclasses import dataclass

from konstytucja.common.errors import (
    GovernmentFormationError,
    NoConfidenceError,
)
from konstytucja.common.types import (
    CouncilOfMinisters,
    GovernmentFormationStage,
    MajorityType,
    VoteRecord,
)
from konstytucja.common.voting import check_quorum, passes_vote

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MINISTER_LIABILITY_MAJORITY: MajorityType = MajorityType.THREE_FIFTHS
"""Art. 156 ust. 2: Uchwała o pociągnięciu członka Rady Ministrów do
odpowiedzialności przed Trybunałem Stanu jest podejmowana na wniosek
Prezydenta Rzeczypospolitej lub co najmniej 115 posłów większością
3/5 ustawowej liczby członków Sejmu.

A resolution to bring a member of the Council of Ministers to
accountability before the State Tribunal requires a 3/5 majority
of the statutory number of Sejm members.
"""

# ---------------------------------------------------------------------------
# Council composition — Art. 147
# ---------------------------------------------------------------------------


def validate_council_composition(council: CouncilOfMinisters) -> bool:
    """Validate that the Council of Ministers has a valid composition.

    Art. 147: Rada Ministrów składa się z Prezesa Rady Ministrów i ministrów.
    The Council of Ministers consists of the Prime Minister and ministers.

    The PM must hold the "Prime Minister" role, and there must be at least
    one additional minister.

    Raises:
        GovernmentFormationError: If the composition is invalid.
    """
    if council.prime_minister.role != "Prime Minister":
        raise GovernmentFormationError(
            "The head of the Council of Ministers must hold the role "
            "'Prime Minister' (Prezes Rady Ministrów).",
            article="147",
        )
    if not council.ministers:
        raise GovernmentFormationError(
            "The Council of Ministers must include at least one minister "
            "in addition to the Prime Minister.",
            article="147",
        )
    return True


# ---------------------------------------------------------------------------
# Confidence vote — Art. 154(2)
# ---------------------------------------------------------------------------


def validate_confidence_vote(vote: VoteRecord) -> bool:
    """Validate a confidence vote for the Council of Ministers.

    Art. 154 ust. 2: Prezes Rady Ministrów, w ciągu 14 dni od dnia
    powołania przez Prezydenta Rzeczypospolitej, przedstawia Sejmowi program
    działania Rady Ministrów z wnioskiem o udzielenie jej wotum zaufania.
    Wotum zaufania Sejm uchwala bezwzględną większością głosów w obecności
    co najmniej połowy ustawowej liczby posłów.

    The Sejm grants a vote of confidence by an absolute majority of votes
    in the presence of at least half the statutory number of Deputies.

    Raises:
        GovernmentFormationError: If the vote does not meet requirements.
    """
    try:
        return passes_vote(vote, MajorityType.ABSOLUTE)
    except Exception as e:
        raise GovernmentFormationError(
            f"Confidence vote failed: {e}",
            article="154",
        ) from e


# ---------------------------------------------------------------------------
# Constructive no-confidence — Art. 158
# ---------------------------------------------------------------------------


def validate_constructive_no_confidence(
    vote: VoteRecord, successor: str
) -> bool:
    """Validate a constructive vote of no confidence.

    Art. 158 ust. 1: Sejm wyraża Radzie Ministrów wotum nieufności
    większością ustawowej liczby posłów na wniosek zgłoszony przez co
    najmniej 46 posłów i wskazujący imiennie kandydata na Prezesa Rady
    Ministrów.

    The Sejm expresses a vote of no confidence by a majority of the
    statutory number of Deputies (absolute majority), with the motion
    naming a successor candidate for Prime Minister.

    Args:
        vote: The Sejm vote record.
        successor: Name of the proposed new Prime Minister.

    Raises:
        NoConfidenceError: If requirements are not met.
    """
    if not successor or not successor.strip():
        raise NoConfidenceError(
            "A constructive no-confidence motion must name a successor "
            "candidate for Prime Minister (Art. 158 requires the motion "
            "to identify the candidate by name).",
            article="158",
        )
    try:
        return passes_vote(vote, MajorityType.ABSOLUTE)
    except Exception as e:
        raise NoConfidenceError(
            f"Constructive no-confidence vote failed: {e}",
            article="158",
        ) from e


# ---------------------------------------------------------------------------
# PM confidence request — Art. 159
# ---------------------------------------------------------------------------


def validate_confidence_request(vote: VoteRecord) -> bool:
    """Validate a confidence vote requested by the Prime Minister.

    Art. 159 ust. 1: Sejm może wyrazić ministrowi wotum nieufności.
    Wniosek o wyrażenie wotum nieufności może być zgłoszony przez co
    najmniej 69 posłów. Przepis art. 158 ust. 2 stosuje się odpowiednio.

    Art. 160: Prezes Rady Ministrów może zwrócić się do Sejmu o wyrażenie
    Radzie Ministrów wotum zaufania. Udzielenie wotum zaufania Radzie
    Ministrów następuje większością głosów w obecności co najmniej połowy
    ustawowej liczby posłów.

    When the PM requests a vote of confidence, a simple majority
    (with quorum) suffices.

    Raises:
        NoConfidenceError: If the vote fails.
    """
    try:
        return passes_vote(vote, MajorityType.SIMPLE)
    except Exception as e:
        raise NoConfidenceError(
            f"Confidence request failed: {e}",
            article="160",
        ) from e


# ---------------------------------------------------------------------------
# Minister liability — Art. 156
# ---------------------------------------------------------------------------


def validate_minister_liability(vote: VoteRecord) -> bool:
    """Validate a vote to refer a minister to the State Tribunal.

    Art. 156 ust. 2: Uchwała o pociągnięciu członka Rady Ministrów do
    odpowiedzialności przed Trybunałem Stanu jest podejmowana na wniosek
    Prezydenta Rzeczypospolitej lub co najmniej 115 posłów większością
    3/5 ustawowej liczby członków Sejmu.

    A resolution to hold a Council member accountable before the State
    Tribunal requires a 3/5 majority of the statutory number of Sejm
    members.

    Raises:
        NoConfidenceError: If the required majority is not met.
    """
    check_quorum(vote)
    # 3/5 of statutory members (460) = 276
    required = vote.members * 3
    actual = vote.votes_for * 5
    if actual < required:
        raise NoConfidenceError(
            f"State Tribunal referral requires 3/5 of statutory members "
            f"({vote.members}): need {(vote.members * 3 + 4) // 5} votes, "
            f"got {vote.votes_for}.",
            article="156",
        )
    return True


# ---------------------------------------------------------------------------
# Individual minister no-confidence — Art. 159
# ---------------------------------------------------------------------------

MIN_DEPUTIES_FOR_MINISTER_NO_CONFIDENCE: int = 69
"""Art. 159 ust. 1: Wniosek o wyrażenie wotum nieufności może być zgłoszony
przez co najmniej 69 posłów.

A motion to express no confidence in an individual minister may be
submitted by at least 69 Deputies.
"""


def validate_individual_minister_no_confidence(
    vote: VoteRecord,
    signatories: int,
) -> bool:
    """Validate a no-confidence vote against an individual minister.

    Art. 159 ust. 1: Sejm może wyrazić ministrowi wotum nieufności.
    Wniosek o wyrażenie wotum nieufności może być zgłoszony przez co
    najmniej 69 posłów.

    Art. 159(1): The Sejm may express a vote of no confidence in a
    minister. A motion requires at least 69 Deputies.
    Simple majority with quorum suffices.

    Args:
        vote: The Sejm vote record.
        signatories: Number of Deputies who signed the motion.

    Raises:
        NoConfidenceError: If the motion or vote does not meet requirements.
    """
    if signatories < MIN_DEPUTIES_FOR_MINISTER_NO_CONFIDENCE:
        raise NoConfidenceError(
            f"A motion of no confidence in a minister requires at least "
            f"{MIN_DEPUTIES_FOR_MINISTER_NO_CONFIDENCE} Deputies' signatures, "
            f"got {signatories}.",
            article="159",
        )
    try:
        return passes_vote(vote, MajorityType.SIMPLE)
    except Exception as e:
        raise NoConfidenceError(
            f"Individual minister no-confidence vote failed: {e}",
            article="159",
        ) from e


# ---------------------------------------------------------------------------
# Government Formation State Machine — Art. 154–155
# ---------------------------------------------------------------------------


@dataclass
class GovernmentFormation:
    """State machine for the government formation procedure (Art. 154–155).

    Art. 154 ust. 1: Prezydent Rzeczypospolitej desygnuje Prezesa Rady
    Ministrów, który proponuje skład Rady Ministrów. Prezydent Rzeczypospolitej
    powołuje Prezesa Rady Ministrów wraz z pozostałymi członkami Rady Ministrów.

    Art. 154(1): The President designates a PM, who proposes the Council.
    Art. 154(2): PM presents programme, Sejm votes confidence (absolute majority).
    Art. 155(1): If first attempt fails, Sejm itself elects a PM (absolute majority).
    Art. 155(2): If that fails too, President appoints PM and Council; Sejm votes
    by simple majority. If this also fails, President shortens Sejm's term.

    Three-attempt formation process:
    1. President designates → Sejm confidence (absolute majority)
    2. Sejm elects PM → confidence (absolute majority)
    3. President appoints → Sejm confidence (simple majority) → or dissolution
    """

    stage: GovernmentFormationStage = GovernmentFormationStage.PRESIDENT_DESIGNATES

    def _require_stage(
        self, *expected: GovernmentFormationStage, article: str
    ) -> None:
        if self.stage not in expected:
            expected_names = ", ".join(s.name for s in expected)
            raise GovernmentFormationError(
                f"Cannot proceed: formation is at {self.stage.name}, "
                f"expected {expected_names}.",
                article=article,
            )

    def president_designates(self) -> None:
        """President designates PM candidate (Art. 154(1)).

        Art. 154 ust. 1: Prezydent desygnuje Prezesa Rady Ministrów.
        """
        self._require_stage(
            GovernmentFormationStage.PRESIDENT_DESIGNATES,
            article="154(1)",
        )
        self.stage = GovernmentFormationStage.CONFIDENCE_VOTE

    def sejm_confidence_first_attempt(self, vote: VoteRecord) -> None:
        """Sejm votes confidence — first attempt (Art. 154(2)).

        Absolute majority required.
        If it fails, moves to second attempt (Sejm elects).
        """
        self._require_stage(
            GovernmentFormationStage.CONFIDENCE_VOTE,
            article="154(2)",
        )
        try:
            passes_vote(vote, MajorityType.ABSOLUTE)
            self.stage = GovernmentFormationStage.APPOINTED
        except Exception:
            self.stage = GovernmentFormationStage.SEJM_ELECTS

    def sejm_elects_pm(self, vote: VoteRecord) -> None:
        """Sejm elects PM — second attempt (Art. 155(1)).

        Art. 155 ust. 1: W razie niepowołania Rady Ministrów w trybie
        art. 154 ust. 3 Sejm w ciągu 14 dni od upływu terminów określonych
        w art. 154 ust. 1 lub ust. 2 wybiera Prezesa Rady Ministrów oraz
        proponowanych przez niego członków Rady Ministrów bezwzględną
        większością głosów.

        Art. 155(1): The Sejm elects a PM by absolute majority within 14 days.
        If it fails, moves to third attempt (President appoints).
        """
        self._require_stage(
            GovernmentFormationStage.SEJM_ELECTS,
            article="155(1)",
        )
        try:
            passes_vote(vote, MajorityType.ABSOLUTE)
            self.stage = GovernmentFormationStage.APPOINTED
        except Exception:
            self.stage = GovernmentFormationStage.PRESIDENT_APPOINTS_RETRY

    def president_appoints_third_attempt(self, vote: VoteRecord) -> None:
        """President appoints, Sejm votes — third attempt (Art. 155(2)).

        Art. 155 ust. 2: W razie niepowołania Rady Ministrów w trybie
        art. 155 ust. 1 Prezydent Rzeczypospolitej w ciągu 14 dni powołuje
        Prezesa Rady Ministrów i na jego wniosek pozostałych członków Rady
        Ministrów oraz odbiera od nich przysięgę. Sejm w ciągu 14 dni od
        dnia powołania Rady Ministrów przez Prezydenta Rzeczypospolitej
        udziela jej wotum zaufania większością głosów.

        Art. 155(2): Simple majority. If it fails, President shortens
        the Sejm's term (dissolution).
        """
        self._require_stage(
            GovernmentFormationStage.PRESIDENT_APPOINTS_RETRY,
            article="155(2)",
        )
        try:
            passes_vote(vote, MajorityType.SIMPLE)
            self.stage = GovernmentFormationStage.APPOINTED
        except Exception:
            self.stage = GovernmentFormationStage.FAILED
