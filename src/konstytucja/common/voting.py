"""Voting and quorum logic.

Logika głosowania i kworum.

Art. 120: Sejm uchwala ustawy zwykłą większością głosów w obecności
co najmniej połowy ustawowej liczby posłów, chyba że Konstytucja
przewiduje inną większość.

Art. 120: The Sejm shall pass bills by a simple majority vote, in the
presence of at least half the statutory number of Deputies, unless the
Constitution provides otherwise.
"""

from konstytucja.common.errors import MajorityError, QuorumError
from konstytucja.common.types import MajorityType, VoteRecord


def check_quorum(vote: VoteRecord) -> None:
    """Verify quorum: at least half the statutory members present.

    Sprawdzenie kworum: co najmniej połowa ustawowej liczby członków.
    Uses integer arithmetic: present * 2 >= members.

    Raises:
        QuorumError: if quorum is not met.
    """
    if vote.total_present * 2 < vote.members:
        raise QuorumError(
            f"Quorum not met: {vote.total_present} present, "
            f"need at least {(vote.members + 1) // 2} "
            f"of {vote.members} statutory members",
            article="120",
        )


def check_majority(vote: VoteRecord, majority_type: MajorityType) -> bool:
    """Check if a vote meets the required majority type.

    Sprawdzenie, czy głosowanie osiągnęło wymaganą większość.
    All comparisons use integer arithmetic to avoid floating-point errors.

    Args:
        vote: The vote record.
        majority_type: The type of majority required.

    Returns:
        True if the majority is met.

    Raises:
        MajorityError: if the required majority is not reached.
    """
    match majority_type:
        case MajorityType.SIMPLE:
            # zwykła większość: więcej za niż przeciw (abstencje nie liczą się)
            # Simple majority: more for than against (abstentions don't count)
            passed = vote.votes_for > vote.votes_against
            if not passed:
                raise MajorityError(
                    f"Simple majority not reached: {vote.votes_for} for, "
                    f"{vote.votes_against} against",
                    article="120",
                )

        case MajorityType.ABSOLUTE:
            # bezwzględna większość: więcej niż połowa ustawowej liczby
            # Absolute majority: more than half the statutory members
            # votes_for * 2 > members
            passed = vote.votes_for * 2 > vote.members
            if not passed:
                raise MajorityError(
                    f"Absolute majority not reached: {vote.votes_for} for, "
                    f"need more than {vote.members // 2} "
                    f"of {vote.members} statutory members",
                    article="120",
                )

        case MajorityType.TWO_THIRDS:
            # 2/3 głosów: votes_for * 3 >= total_present * 2
            passed = vote.votes_for * 3 >= vote.total_present * 2
            if not passed:
                raise MajorityError(
                    f"Two-thirds majority not reached: {vote.votes_for} for "
                    f"of {vote.total_present} present",
                    article="235",
                )

        case MajorityType.THREE_FIFTHS:
            # 3/5 głosów: votes_for * 5 >= total_present * 3
            passed = vote.votes_for * 5 >= vote.total_present * 3
            if not passed:
                raise MajorityError(
                    f"Three-fifths majority not reached: {vote.votes_for} for "
                    f"of {vote.total_present} present",
                    article="120",
                )

    return True


def passes_vote(
    vote: VoteRecord,
    majority_type: MajorityType = MajorityType.SIMPLE,
    *,
    require_quorum: bool = True,
) -> bool:
    """Full vote check: quorum + majority.

    Pełna weryfikacja głosowania: kworum + wymagana większość.

    Args:
        vote: The vote record.
        majority_type: The required majority type (default: simple).
        require_quorum: Whether to check quorum (default: True).

    Returns:
        True if vote passes.

    Raises:
        QuorumError: if quorum check fails.
        MajorityError: if majority check fails.
    """
    if require_quorum:
        check_quorum(vote)
    return check_majority(vote, majority_type)
