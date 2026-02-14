"""Tests for Chapter VI — Council of Ministers (Art. 146–162).

Covers composition, confidence votes, constructive no-confidence,
PM confidence requests, minister liability, individual minister
no-confidence, and government formation state machine.
"""

import pytest

from konstytucja.chapter_06_council_of_ministers import (
    MIN_DEPUTIES_FOR_MINISTER_NO_CONFIDENCE,
    MINISTER_LIABILITY_MAJORITY,
    GovernmentFormation,
    validate_confidence_request,
    validate_confidence_vote,
    validate_constructive_no_confidence,
    validate_council_composition,
    validate_individual_minister_no_confidence,
    validate_minister_liability,
)
from konstytucja.common.errors import GovernmentFormationError, NoConfidenceError
from konstytucja.common.types import (
    Chamber,
    CouncilOfMinisters,
    GovernmentFormationStage,
    MajorityType,
    Minister,
    VoteRecord,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Art. 156: Minister liability majority."""

    def test_liability_majority_is_three_fifths(self):
        assert MINISTER_LIABILITY_MAJORITY == MajorityType.THREE_FIFTHS


# ---------------------------------------------------------------------------
# Council composition — Art. 147
# ---------------------------------------------------------------------------


class TestCouncilComposition:
    """Art. 147: Council must have PM + at least one minister."""

    def test_valid_council(self, sample_council):
        assert validate_council_composition(sample_council) is True

    def test_pm_wrong_role_rejected(self):
        pm = Minister(name="Jan Kowalski", role="Deputy PM")
        council = CouncilOfMinisters(
            prime_minister=pm,
            ministers=(Minister(name="Anna Nowak", role="Minister of Finance"),),
        )
        with pytest.raises(GovernmentFormationError, match="Prime Minister"):
            validate_council_composition(council)

    def test_no_ministers_rejected(self):
        pm = Minister(name="Jan Kowalski", role="Prime Minister")
        council = CouncilOfMinisters(prime_minister=pm, ministers=())
        with pytest.raises(GovernmentFormationError, match="at least one minister"):
            validate_council_composition(council)

    def test_error_references_article_147(self):
        pm = Minister(name="Jan", role="Prime Minister")
        council = CouncilOfMinisters(prime_minister=pm, ministers=())
        with pytest.raises(GovernmentFormationError) as exc_info:
            validate_council_composition(council)
        assert exc_info.value.article == "147"


# ---------------------------------------------------------------------------
# Confidence vote — Art. 154(2)
# ---------------------------------------------------------------------------


class TestConfidenceVote:
    """Art. 154(2): Absolute majority with quorum required."""

    def test_passes_with_absolute_majority(self, sejm_absolute_majority):
        assert validate_confidence_vote(sejm_absolute_majority) is True

    def test_fails_without_absolute_majority(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=190,
            votes_abstain=50,
        )
        with pytest.raises(GovernmentFormationError, match="Confidence vote failed"):
            validate_confidence_vote(vote)

    def test_fails_without_quorum(self, sejm_no_quorum):
        with pytest.raises(GovernmentFormationError):
            validate_confidence_vote(sejm_no_quorum)

    def test_error_references_article_154(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=190,
            votes_abstain=50,
        )
        with pytest.raises(GovernmentFormationError) as exc_info:
            validate_confidence_vote(vote)
        assert exc_info.value.article == "154"


# ---------------------------------------------------------------------------
# Constructive no-confidence — Art. 158
# ---------------------------------------------------------------------------


class TestConstructiveNoConfidence:
    """Art. 158: Absolute majority + named successor required."""

    def test_passes_with_valid_vote_and_successor(self, sejm_absolute_majority):
        assert (
            validate_constructive_no_confidence(
                sejm_absolute_majority, "Maria Nowa"
            )
            is True
        )

    def test_fails_without_successor(self, sejm_absolute_majority):
        with pytest.raises(NoConfidenceError, match="name a successor"):
            validate_constructive_no_confidence(sejm_absolute_majority, "")

    def test_fails_with_whitespace_successor(self, sejm_absolute_majority):
        with pytest.raises(NoConfidenceError, match="name a successor"):
            validate_constructive_no_confidence(sejm_absolute_majority, "   ")

    def test_fails_without_absolute_majority(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=220,
            votes_against=200,
            votes_abstain=20,
        )
        with pytest.raises(NoConfidenceError, match="no-confidence vote failed"):
            validate_constructive_no_confidence(vote, "Maria Nowa")

    def test_error_references_article_158(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=220,
            votes_against=200,
            votes_abstain=20,
        )
        with pytest.raises(NoConfidenceError) as exc_info:
            validate_constructive_no_confidence(vote, "Maria Nowa")
        assert exc_info.value.article == "158"


# ---------------------------------------------------------------------------
# PM confidence request — Art. 160
# ---------------------------------------------------------------------------


class TestConfidenceRequest:
    """Art. 160: Simple majority with quorum suffices."""

    def test_passes_with_simple_majority(self, sejm_simple_majority):
        assert validate_confidence_request(sejm_simple_majority) is True

    def test_fails_without_majority(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=210,
            votes_abstain=30,
        )
        with pytest.raises(NoConfidenceError, match="Confidence request failed"):
            validate_confidence_request(vote)

    def test_fails_without_quorum(self, sejm_no_quorum):
        with pytest.raises(NoConfidenceError):
            validate_confidence_request(sejm_no_quorum)

    def test_error_references_article_160(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=210,
            votes_abstain=30,
        )
        with pytest.raises(NoConfidenceError) as exc_info:
            validate_confidence_request(vote)
        assert exc_info.value.article == "160"


# ---------------------------------------------------------------------------
# Minister liability — Art. 156
# ---------------------------------------------------------------------------


class TestMinisterLiability:
    """Art. 156: 3/5 of statutory members for State Tribunal referral."""

    def test_passes_with_three_fifths(self):
        # 3/5 of 460 = 276
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=276,
            votes_against=150,
            votes_abstain=34,
        )
        assert validate_minister_liability(vote) is True

    def test_fails_below_three_fifths(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=275,
            votes_against=150,
            votes_abstain=35,
        )
        with pytest.raises(NoConfidenceError, match="3/5"):
            validate_minister_liability(vote)

    def test_error_references_article_156(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=100,
            votes_against=300,
            votes_abstain=60,
        )
        with pytest.raises(NoConfidenceError) as exc_info:
            validate_minister_liability(vote)
        assert exc_info.value.article == "156"


# ---------------------------------------------------------------------------
# Individual minister no-confidence — Art. 159
# ---------------------------------------------------------------------------


class TestIndividualMinisterNoConfidence:
    """Art. 159: Individual minister no-confidence (69 deputies + simple majority)."""

    def test_min_signatories_constant(self):
        assert MIN_DEPUTIES_FOR_MINISTER_NO_CONFIDENCE == 69

    def test_passes_with_valid_signatures_and_majority(self, sejm_simple_majority):
        assert (
            validate_individual_minister_no_confidence(
                sejm_simple_majority, signatories=69
            )
            is True
        )

    def test_fails_with_insufficient_signatories(self, sejm_simple_majority):
        with pytest.raises(NoConfidenceError, match="69"):
            validate_individual_minister_no_confidence(
                sejm_simple_majority, signatories=68
            )

    def test_fails_without_majority(self):
        vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=210,
            votes_abstain=30,
        )
        with pytest.raises(NoConfidenceError, match="no-confidence vote failed"):
            validate_individual_minister_no_confidence(vote, signatories=69)

    def test_error_references_article_159(self):
        with pytest.raises(NoConfidenceError) as exc_info:
            validate_individual_minister_no_confidence(
                VoteRecord(chamber=Chamber.SEJM, votes_for=250, votes_against=180),
                signatories=10,
            )
        assert exc_info.value.article == "159"


# ---------------------------------------------------------------------------
# Government formation — Art. 154–155
# ---------------------------------------------------------------------------


class TestGovernmentFormation:
    """Art. 154–155: Three-attempt government formation state machine."""

    def test_initial_stage(self):
        gf = GovernmentFormation()
        assert gf.stage == GovernmentFormationStage.PRESIDENT_DESIGNATES

    def test_first_attempt_success(self):
        gf = GovernmentFormation()
        gf.president_designates()
        assert gf.stage == GovernmentFormationStage.CONFIDENCE_VOTE

        vote = VoteRecord(
            chamber=Chamber.SEJM, votes_for=231, votes_against=200, votes_abstain=10
        )
        gf.sejm_confidence_first_attempt(vote)
        assert gf.stage == GovernmentFormationStage.APPOINTED

    def test_first_attempt_failure_moves_to_sejm_elects(self):
        gf = GovernmentFormation()
        gf.president_designates()
        vote = VoteRecord(
            chamber=Chamber.SEJM, votes_for=200, votes_against=230, votes_abstain=10
        )
        gf.sejm_confidence_first_attempt(vote)
        assert gf.stage == GovernmentFormationStage.SEJM_ELECTS

    def test_second_attempt_success(self):
        gf = GovernmentFormation()
        gf.president_designates()
        gf.sejm_confidence_first_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.sejm_elects_pm(
            VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=200)
        )
        assert gf.stage == GovernmentFormationStage.APPOINTED

    def test_second_attempt_failure_moves_to_third(self):
        gf = GovernmentFormation()
        gf.president_designates()
        gf.sejm_confidence_first_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.sejm_elects_pm(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        assert gf.stage == GovernmentFormationStage.PRESIDENT_APPOINTS_RETRY

    def test_third_attempt_success(self):
        gf = GovernmentFormation()
        gf.president_designates()
        gf.sejm_confidence_first_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.sejm_elects_pm(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.president_appoints_third_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=240, votes_against=200)
        )
        assert gf.stage == GovernmentFormationStage.APPOINTED

    def test_third_attempt_failure_dissolution(self):
        gf = GovernmentFormation()
        gf.president_designates()
        gf.sejm_confidence_first_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.sejm_elects_pm(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        gf.president_appoints_third_attempt(
            VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
        )
        assert gf.stage == GovernmentFormationStage.FAILED

    def test_wrong_stage_raises_error(self):
        gf = GovernmentFormation()
        with pytest.raises(GovernmentFormationError):
            gf.sejm_confidence_first_attempt(
                VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=200)
            )

    def test_sejm_elects_wrong_stage_raises(self):
        gf = GovernmentFormation()
        gf.president_designates()
        with pytest.raises(GovernmentFormationError):
            gf.sejm_elects_pm(
                VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=200)
            )
