"""Rozdział XII: Zmiana Konstytucji / Chapter XII: Amendments (Art. 235).

Pełna maszyna stanów procedury zmiany Konstytucji.
Full state machine for the constitutional amendment procedure.
"""

from dataclasses import dataclass, field

from konstytucja.common.errors import AmendmentError, MajorityError, QuorumError
from konstytucja.common.types import (
    AmendmentStage,
    Chamber,
    MajorityType,
    VoteRecord,
)
from konstytucja.common.voting import passes_vote

# Art. 235 ust. 1: Who can initiate
INITIATORS = ("1/5 Sejm deputies", "Senate", "President")

# Chapters that can trigger a referendum (Art. 235 ust. 6)
REFERENDUM_CHAPTERS = {1, 2, 12}  # I, II, XII


@dataclass
class AmendmentProcess:
    """State machine for the Art. 235 amendment procedure.

    Art. 235:
    ust. 1: Projekt ustawy o zmianie Konstytucji może przedłożyć co najmniej
    1/5 ustawowej liczby posłów, Senat lub Prezydent Rzeczypospolitej.
    ust. 2: Zmiana Konstytucji następuje w drodze ustawy uchwalonej
    w jednakowym brzmieniu przez Sejm i następnie w terminie nie dłuższym
    niż 60 dni przez Senat.
    ust. 3: Pierwsze czytanie projektu ustawy o zmianie Konstytucji może
    odbyć się nie wcześniej niż trzydziestego dnia od dnia przedłożenia
    Sejmowi projektu ustawy.
    ust. 4: Ustawę o zmianie Konstytucji uchwala Sejm większością co najmniej
    2/3 głosów w obecności co najmniej połowy ustawowej liczby posłów
    oraz Senat bezwzględną większością głosów w obecności co najmniej
    połowy ustawowej liczby senatorów.
    ust. 5: Uchwalenie przez Sejm ustawy zmieniającej przepisy rozdziałów I,
    II lub XII Konstytucji może odbyć się nie wcześniej niż sześćdziesiątego
    dnia po pierwszym czytaniu projektu tej ustawy.
    ust. 6: Jeżeli ustawa o zmianie Konstytucji dotyczy przepisów rozdziału I,
    II lub XII, podmioty określone w ust. 1 mogą zażądać, w terminie 45 dni
    od dnia uchwalenia ustawy przez Senat, przeprowadzenia referendum
    zatwierdzającego.

    Art. 235:
    (1): A bill to amend the Constitution may be submitted by at least 1/5
    of the statutory number of Deputies, the Senate, or the President.
    (2): Amendments shall be made by means of a statute adopted in identical
    wording by the Sejm and then, within 60 days, by the Senate.
    (3): The first reading of a bill to amend the Constitution may take place
    no sooner than 30 days after submission to the Sejm.
    (4): The Sejm adopts by at least 2/3 majority with quorum; the Senate
    by absolute majority with quorum.
    (5): If the bill amends Chapters I, II, or XII, the Sejm vote may not
    take place sooner than 60 days after the first reading.
    (6): If the bill concerns Chapters I, II, or XII, the initiators may
    request a confirmatory referendum within 45 days of Senate adoption.
    """

    title: str
    initiator: str
    affected_chapters: set[int] = field(default_factory=set)
    stage: AmendmentStage = AmendmentStage.INITIATED
    referendum_requested: bool = False

    def __post_init__(self) -> None:
        if self.initiator not in INITIATORS:
            raise AmendmentError(
                f"Invalid initiator '{self.initiator}': "
                f"must be one of {INITIATORS}",
                article="235(1)",
            )

    @property
    def touches_protected_chapters(self) -> bool:
        """Whether this amendment affects Chapters I, II, or XII."""
        return bool(self.affected_chapters & REFERENDUM_CHAPTERS)

    def first_reading(self) -> None:
        """Move to first reading in the Sejm (Art. 235 ust. 3).

        Must be at least 30 days after submission (caller responsible
        for timing check — we validate the state transition).
        """
        if self.stage != AmendmentStage.INITIATED:
            raise AmendmentError(
                f"Cannot start first reading from stage {self.stage.name}",
                article="235(3)",
            )
        self.stage = AmendmentStage.FIRST_READING_SEJM

    def sejm_vote(self, vote: VoteRecord) -> None:
        """Sejm votes on the amendment (Art. 235 ust. 4).

        Requires 2/3 majority with quorum.
        """
        if self.stage != AmendmentStage.FIRST_READING_SEJM:
            raise AmendmentError(
                f"Cannot hold Sejm vote from stage {self.stage.name}",
                article="235(4)",
            )
        assert vote.chamber == Chamber.SEJM
        try:
            passes_vote(vote, MajorityType.TWO_THIRDS)
        except (QuorumError, MajorityError):
            self.stage = AmendmentStage.REJECTED
            raise
        self.stage = AmendmentStage.SEJM_PASSED

    def senate_vote(self, vote: VoteRecord) -> None:
        """Senate votes on the amendment (Art. 235 ust. 4).

        Requires absolute majority with quorum.
        Within 60 days of Sejm passage (caller responsible for timing).
        """
        if self.stage != AmendmentStage.SEJM_PASSED:
            raise AmendmentError(
                f"Cannot hold Senate vote from stage {self.stage.name}",
                article="235(4)",
            )
        assert vote.chamber == Chamber.SENATE
        try:
            passes_vote(vote, MajorityType.ABSOLUTE)
        except (QuorumError, MajorityError):
            self.stage = AmendmentStage.REJECTED
            raise
        self.stage = AmendmentStage.SENATE_PASSED

    def request_referendum(self) -> None:
        """Request a confirmatory referendum (Art. 235 ust. 6).

        Only available for amendments to Chapters I, II, or XII.
        Must be requested within 45 days of Senate adoption.
        """
        if self.stage != AmendmentStage.SENATE_PASSED:
            raise AmendmentError(
                f"Cannot request referendum from stage {self.stage.name}",
                article="235(6)",
            )
        if not self.touches_protected_chapters:
            raise AmendmentError(
                "Referendum only available for amendments to Chapters I, II, or XII",
                article="235(6)",
            )
        self.referendum_requested = True
        self.stage = AmendmentStage.REFERENDUM_REQUESTED

    def referendum_result(self, approved: bool) -> None:
        """Record the referendum result (Art. 235 ust. 6)."""
        if self.stage != AmendmentStage.REFERENDUM_REQUESTED:
            raise AmendmentError(
                f"Cannot record referendum result from stage {self.stage.name}",
                article="235(6)",
            )
        if approved:
            self.stage = AmendmentStage.REFERENDUM_PASSED
        else:
            self.stage = AmendmentStage.REJECTED

    def president_sign(self) -> None:
        """President signs the amendment (Art. 235 ust. 7).

        Art. 235 ust. 7: Prezydent Rzeczypospolitej podpisuje ustawę
        w ciągu 21 dni od dnia przedstawienia i zarządza jej ogłoszenie.

        Art. 235(7): The President signs within 21 days and orders publication.
        """
        allowed_stages = {
            AmendmentStage.SENATE_PASSED,
            AmendmentStage.REFERENDUM_PASSED,
        }
        if self.stage not in allowed_stages:
            raise AmendmentError(
                f"Cannot sign from stage {self.stage.name}",
                article="235(7)",
            )
        # If protected chapters and no referendum was requested, signing is okay
        # (the 45-day window expired without request)
        self.stage = AmendmentStage.PRESIDENT_SIGNS

    def complete(self) -> None:
        """Mark the amendment as adopted."""
        if self.stage != AmendmentStage.PRESIDENT_SIGNS:
            raise AmendmentError(
                f"Cannot complete from stage {self.stage.name}",
                article="235",
            )
        self.stage = AmendmentStage.ADOPTED
