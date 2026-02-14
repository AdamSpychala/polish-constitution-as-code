"""Legislative process state machine (Art. 118–122).

Maszyna stanów procesu legislacyjnego.
Bill lifecycle from initiation through presidential signature.
"""

from dataclasses import dataclass, field

from konstytucja.common.errors import LegislativeProcessError, MajorityError, QuorumError
from konstytucja.common.types import (
    Bill,
    BillStage,
    Chamber,
    MajorityType,
    VoteRecord,
)
from konstytucja.common.voting import passes_vote

# Art. 118 ust. 1–2: Who can initiate legislation
INITIATORS = (
    "Deputies",                      # posłowie (group of 15)
    "Senate",                        # Senat
    "President",                     # Prezydent
    "Council of Ministers",          # Rada Ministrów
    "Citizens (100,000 signatures)", # 100 000 obywateli (Art. 118 ust. 2)
)


@dataclass
class LegislativeProcess:
    """State machine for the Art. 118–122 legislative process.

    Art. 118 ust. 1: Inicjatywa ustawodawcza przysługuje posłom, Senatowi,
    Prezydentowi Rzeczypospolitej i Radzie Ministrów.
    Art. 118 ust. 2: Inicjatywa ustawodawcza przysługuje również grupie
    co najmniej 100 000 obywateli mających prawo wybierania do Sejmu.

    Art. 119: Sejm rozpatruje projekt ustawy w trzech czytaniach.
    Art. 120: Sejm uchwala ustawy zwykłą większością głosów.
    Art. 121: Ustawę uchwaloną przez Sejm Marszałek Sejmu przekazuje Senatowi.
    Art. 122: Prezydent podpisuje lub stosuje weto.
    """

    bill: Bill
    stage: BillStage = BillStage.INITIATED
    history: list[str] = field(default_factory=list)

    def _transition(self, new_stage: BillStage, note: str = "") -> None:
        self.history.append(f"{self.stage.name} -> {new_stage.name}: {note}")
        self.stage = new_stage

    def _require_stage(self, *expected: BillStage, article: str) -> None:
        if self.stage not in expected:
            expected_names = ", ".join(s.name for s in expected)
            raise LegislativeProcessError(
                f"Cannot proceed: bill is at {self.stage.name}, "
                f"expected {expected_names}",
                article=article,
            )

    # --- Sejm ---

    def begin_sejm_deliberation(self) -> None:
        """Start three readings in the Sejm (Art. 119)."""
        self._require_stage(BillStage.INITIATED, article="119")
        self._transition(BillStage.SEJM_DELIBERATION, "Three readings begin")

    def sejm_vote(self, vote: VoteRecord) -> None:
        """Sejm votes on the bill (Art. 120).

        Simple majority, quorum required.
        """
        self._require_stage(BillStage.SEJM_DELIBERATION, article="120")
        assert vote.chamber == Chamber.SEJM
        try:
            passes_vote(vote, MajorityType.SIMPLE)
        except (QuorumError, MajorityError):
            self._transition(BillStage.REJECTED, "Sejm rejected")
            raise
        self._transition(BillStage.SEJM_PASSED, f"Passed {vote.votes_for}-{vote.votes_against}")

    # --- Senate ---

    def send_to_senate(self) -> None:
        """Marshal of the Sejm sends the bill to the Senate (Art. 121 ust. 1).

        Art. 121 ust. 1: Ustawę uchwaloną przez Sejm Marszałek Sejmu
        przekazuje Senatowi.
        Art. 121 ust. 2: Senat w ciągu 30 dni od dnia przekazania ustawy
        może ją przyjąć bez zmian, uchwalić poprawki albo uchwalić
        odrzucenie jej w całości.

        Senate has 30 days to act. If it doesn't, bill is deemed adopted.
        """
        self._require_stage(BillStage.SEJM_PASSED, article="121(1)")
        self._transition(BillStage.SENATE_DELIBERATION, "Sent to Senate")

    def senate_accepts(self) -> None:
        """Senate accepts the bill without changes."""
        self._require_stage(BillStage.SENATE_DELIBERATION, article="121(2)")
        self._transition(BillStage.SENATE_PASSED, "Senate accepted without changes")

    def senate_amends(self, vote: VoteRecord) -> None:
        """Senate passes amendments (simple majority)."""
        self._require_stage(BillStage.SENATE_DELIBERATION, article="121(2)")
        assert vote.chamber == Chamber.SENATE
        passes_vote(vote, MajorityType.SIMPLE)
        self._transition(BillStage.SENATE_AMENDED, "Senate proposed amendments")

    def senate_rejects(self, vote: VoteRecord) -> None:
        """Senate votes to reject the bill entirely."""
        self._require_stage(BillStage.SENATE_DELIBERATION, article="121(2)")
        assert vote.chamber == Chamber.SENATE
        passes_vote(vote, MajorityType.SIMPLE)
        self._transition(BillStage.SENATE_REJECTED, "Senate rejected")

    # --- Sejm override of Senate ---

    def sejm_override_senate(self, vote: VoteRecord) -> None:
        """Sejm overrides Senate rejection/amendments (Art. 121 ust. 3).

        Requires absolute majority in the Sejm.
        """
        self._require_stage(
            BillStage.SENATE_AMENDED,
            BillStage.SENATE_REJECTED,
            article="121(3)",
        )
        assert vote.chamber == Chamber.SEJM
        try:
            passes_vote(vote, MajorityType.ABSOLUTE)
        except (QuorumError, MajorityError):
            self._transition(BillStage.REJECTED, "Sejm failed to override Senate")
            raise
        self._transition(BillStage.SEJM_OVERRIDE_VOTE, "Sejm overrode Senate")

    # --- President ---

    def send_to_president(self) -> None:
        """Send the bill to the President for signature (Art. 122)."""
        self._require_stage(
            BillStage.SENATE_PASSED,
            BillStage.SEJM_OVERRIDE_VOTE,
            article="122",
        )
        self._transition(BillStage.PRESIDENT_REVIEW, "Sent to President")

    def president_signs(self) -> None:
        """President signs the bill (Art. 122 ust. 2). 21-day deadline."""
        self._require_stage(BillStage.PRESIDENT_REVIEW, article="122(2)")
        self._transition(BillStage.SIGNED, "President signed")

    def president_vetoes(self) -> None:
        """President vetoes the bill (Art. 122 ust. 5)."""
        self._require_stage(BillStage.PRESIDENT_REVIEW, article="122(5)")
        self._transition(BillStage.VETOED, "President vetoed")

    def president_refers_to_tribunal(self) -> None:
        """President refers the bill to the Constitutional Tribunal (Art. 122 ust. 3).

        Art. 122 ust. 3: Prezydent Rzeczypospolitej przed podpisaniem ustawy
        może wystąpić do Trybunału Konstytucyjnego z wnioskiem w sprawie
        zgodności ustawy z Konstytucją.

        Art. 122(3): Before signing a bill, the President may refer it to the
        Constitutional Tribunal for adjudication on its conformity with the
        Constitution.
        """
        self._require_stage(BillStage.PRESIDENT_REVIEW, article="122(3)")
        self._transition(BillStage.REFERRED_TO_TRIBUNAL, "Referred to Tribunal")

    # --- Constitutional Tribunal verdict ---

    def tribunal_rules_constitutional(self) -> None:
        """Tribunal finds the bill constitutional (Art. 122 ust. 4).

        Art. 122 ust. 4: Jeżeli Trybunał Konstytucyjny nie orzeknie
        o niezgodności ustawy z Konstytucją, Prezydent podpisuje ustawę.

        If the Tribunal does not rule the statute unconstitutional,
        the President shall sign the bill — cannot refuse.
        """
        self._require_stage(BillStage.REFERRED_TO_TRIBUNAL, article="122(4)")
        self._transition(
            BillStage.PRESIDENT_REVIEW,
            "Tribunal: constitutional — returns to President",
        )

    def tribunal_rules_unconstitutional(self) -> None:
        """Tribunal finds the bill unconstitutional (Art. 122 ust. 4).

        Art. 122 ust. 4: Jeżeli Trybunał Konstytucyjny orzeknie
        o niezgodności z Konstytucją ustawy, Prezydent odmawia
        podpisania ustawy.

        If the Tribunal rules the statute unconstitutional,
        the President shall refuse to sign.
        """
        self._require_stage(BillStage.REFERRED_TO_TRIBUNAL, article="122(4)")
        self._transition(
            BillStage.REJECTED,
            "Tribunal: unconstitutional — President refuses signature",
        )

    def tribunal_rules_partially_unconstitutional(self) -> None:
        """Tribunal finds the bill partially unconstitutional (Art. 122 ust. 4).

        Art. 122 ust. 4 zd. 2–3: Jeżeli jednak niezgodność z Konstytucją
        dotyczy poszczególnych przepisów ustawy, a Trybunał Konstytucyjny
        nie orzeknie, że są one nierozerwalnie związane z całą ustawą,
        Prezydent, po zasięgnięciu opinii Marszałka Sejmu, podpisuje ustawę
        z pominięciem przepisów uznanych za niezgodne z Konstytucją albo
        zwraca ustawę Sejmowi w celu usunięcia niezgodności.

        If the unconstitutionality concerns particular provisions and the
        Tribunal does not rule them inseparable from the whole act, the
        President — after consulting the Marshal of the Sejm — either:
        (a) signs the bill excluding the unconstitutional provisions, or
        (b) returns the bill to the Sejm for removal of the unconstitutionality.
        """
        self._require_stage(BillStage.REFERRED_TO_TRIBUNAL, article="122(4)")
        self._transition(
            BillStage.PARTIALLY_UNCONSTITUTIONAL,
            "Tribunal: partially unconstitutional — President decides",
        )

    def president_signs_with_exclusions(self) -> None:
        """President signs the bill excluding unconstitutional provisions (Art. 122 ust. 4).

        Art. 122 ust. 4: Prezydent podpisuje ustawę z pominięciem przepisów
        uznanych za niezgodne z Konstytucją.

        The President signs the bill with the unconstitutional provisions
        excluded.
        """
        self._require_stage(BillStage.PARTIALLY_UNCONSTITUTIONAL, article="122(4)")
        self._transition(
            BillStage.SIGNED,
            "President signed with exclusion of unconstitutional provisions",
        )

    def president_returns_to_sejm(self) -> None:
        """President returns the bill to the Sejm for amendment (Art. 122 ust. 4).

        Art. 122 ust. 4: Prezydent zwraca ustawę Sejmowi w celu usunięcia
        niezgodności.

        The President returns the bill to the Sejm so that the
        unconstitutional provisions can be removed or corrected.
        """
        self._require_stage(BillStage.PARTIALLY_UNCONSTITUTIONAL, article="122(4)")
        self._transition(
            BillStage.SEJM_DELIBERATION,
            "Returned to Sejm for removal of unconstitutionality",
        )

    # --- Veto override ---

    def sejm_override_veto(self, vote: VoteRecord) -> None:
        """Sejm overrides the presidential veto (Art. 122 ust. 5).

        Requires 3/5 majority with quorum.
        """
        self._require_stage(BillStage.VETOED, article="122(5)")
        assert vote.chamber == Chamber.SEJM
        try:
            passes_vote(vote, MajorityType.THREE_FIFTHS)
        except (QuorumError, MajorityError):
            self._transition(BillStage.REJECTED, "Veto override failed")
            raise
        self._transition(BillStage.VETO_OVERRIDDEN, "Veto overridden by 3/5 Sejm")

    # --- Enactment ---

    def enact(self) -> None:
        """Bill becomes law after signature or veto override."""
        self._require_stage(
            BillStage.SIGNED,
            BillStage.VETO_OVERRIDDEN,
            article="122",
        )
        self._transition(BillStage.ENACTED, "Published in Dziennik Ustaw")
