"""Tests for common voting logic (Art. 120)."""

import pytest

from konstytucja.common.errors import MajorityError, QuorumError
from konstytucja.common.types import Chamber, MajorityType, VoteRecord
from konstytucja.common.voting import check_majority, check_quorum, passes_vote


class TestQuorum:
    """Art. 120: at least half the statutory number must be present."""

    def test_quorum_met_sejm(self, sejm_simple_majority):
        check_quorum(sejm_simple_majority)  # should not raise

    def test_quorum_not_met_sejm(self, sejm_no_quorum):
        with pytest.raises(QuorumError, match="Quorum not met"):
            check_quorum(sejm_no_quorum)

    def test_quorum_exact_boundary(self):
        """Exactly 230 of 460 = quorum met."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=30)
        check_quorum(vote)  # 230 present, 230 needed

    def test_quorum_one_below(self):
        """229 of 460 = quorum NOT met."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=29)
        with pytest.raises(QuorumError):
            check_quorum(vote)

    def test_quorum_senate(self, senate_simple_majority):
        check_quorum(senate_simple_majority)  # 100 present of 100

    def test_quorum_senate_below(self):
        vote = VoteRecord(chamber=Chamber.SENATE, votes_for=30, votes_against=10)
        with pytest.raises(QuorumError):
            check_quorum(vote)


class TestSimpleMajority:
    """Art. 120: more votes for than against."""

    def test_passes(self, sejm_simple_majority):
        assert check_majority(sejm_simple_majority, MajorityType.SIMPLE) is True

    def test_fails_tied(self):
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=200, votes_abstain=30)
        with pytest.raises(MajorityError, match="Simple majority"):
            check_majority(vote, MajorityType.SIMPLE)

    def test_fails_less(self):
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=100, votes_against=200, votes_abstain=30)
        with pytest.raises(MajorityError):
            check_majority(vote, MajorityType.SIMPLE)

    def test_abstentions_dont_count(self):
        """100 for, 99 against, 231 abstain — simple majority passes."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=100, votes_against=99, votes_abstain=231)
        assert check_majority(vote, MajorityType.SIMPLE) is True


class TestAbsoluteMajority:
    """More than half of statutory members (> 230 for Sejm, > 50 for Senate)."""

    def test_sejm_passes(self, sejm_absolute_majority):
        assert check_majority(sejm_absolute_majority, MajorityType.ABSOLUTE) is True

    def test_sejm_fails_at_230(self):
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=230, votes_against=100, votes_abstain=50)
        with pytest.raises(MajorityError, match="Absolute majority"):
            check_majority(vote, MajorityType.ABSOLUTE)

    def test_senate_passes(self, senate_absolute_majority):
        assert check_majority(senate_absolute_majority, MajorityType.ABSOLUTE) is True

    def test_senate_fails_at_50(self):
        vote = VoteRecord(chamber=Chamber.SENATE, votes_for=50, votes_against=30, votes_abstain=10)
        with pytest.raises(MajorityError):
            check_majority(vote, MajorityType.ABSOLUTE)


class TestTwoThirdsMajority:
    """2/3 of those present: votes_for * 3 >= total_present * 2."""

    def test_passes(self, sejm_two_thirds):
        assert check_majority(sejm_two_thirds, MajorityType.TWO_THIRDS) is True

    def test_exact_boundary(self):
        """200 for of 300 present: 200*3=600 >= 300*2=600 — passes."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=100)
        assert check_majority(vote, MajorityType.TWO_THIRDS) is True

    def test_just_below(self):
        """199 for of 300 present: 199*3=597 < 300*2=600 — fails."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=199, votes_against=101)
        with pytest.raises(MajorityError, match="Two-thirds"):
            check_majority(vote, MajorityType.TWO_THIRDS)


class TestThreeFifthsMajority:
    """3/5 of those present: votes_for * 5 >= total_present * 3."""

    def test_passes(self, sejm_three_fifths):
        assert check_majority(sejm_three_fifths, MajorityType.THREE_FIFTHS) is True

    def test_exact_boundary(self):
        """276 for of 460 present: 276*5=1380 >= 460*3=1380 — passes."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=276, votes_against=184)
        assert check_majority(vote, MajorityType.THREE_FIFTHS) is True

    def test_just_below(self):
        """275 for of 460 present: 275*5=1375 < 460*3=1380 — fails."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=275, votes_against=185)
        with pytest.raises(MajorityError, match="Three-fifths"):
            check_majority(vote, MajorityType.THREE_FIFTHS)


class TestPassesVote:
    """Integration: quorum + majority together."""

    def test_full_pass(self, sejm_simple_majority):
        assert passes_vote(sejm_simple_majority) is True

    def test_quorum_fails_first(self, sejm_no_quorum):
        with pytest.raises(QuorumError):
            passes_vote(sejm_no_quorum)

    def test_skip_quorum(self):
        """When require_quorum=False, only majority matters."""
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=10, votes_against=5)
        assert passes_vote(vote, require_quorum=False) is True
