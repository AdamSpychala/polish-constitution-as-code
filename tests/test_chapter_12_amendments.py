"""Tests for Chapter XII: Constitutional Amendments (Art. 235)."""

import pytest

from konstytucja.chapter_12_amendments import AmendmentProcess
from konstytucja.common.errors import AmendmentError, MajorityError
from konstytucja.common.types import AmendmentStage, Chamber, VoteRecord


@pytest.fixture
def standard_amendment():
    """Amendment to a non-protected chapter (e.g., Chapter IV)."""
    return AmendmentProcess(
        title="Zmiana art. 100",
        initiator="Senate",
        affected_chapters={4},
    )


@pytest.fixture
def protected_amendment():
    """Amendment to Chapter I (protected — referendum possible)."""
    return AmendmentProcess(
        title="Zmiana art. 1",
        initiator="President",
        affected_chapters={1},
    )


@pytest.fixture
def sejm_2_3_vote():
    """Sejm vote meeting 2/3 majority with quorum."""
    return VoteRecord(
        chamber=Chamber.SEJM,
        votes_for=310,
        votes_against=80,
        votes_abstain=10,
    )


@pytest.fixture
def senate_absolute_vote():
    """Senate vote meeting absolute majority with quorum."""
    return VoteRecord(
        chamber=Chamber.SENATE,
        votes_for=51,
        votes_against=30,
        votes_abstain=10,
    )


class TestAmendmentInitiation:
    """Art. 235(1): Only 1/5 Sejm deputies, Senate, or President can initiate."""

    def test_valid_initiators(self):
        for initiator in ("1/5 Sejm deputies", "Senate", "President"):
            proc = AmendmentProcess(
                title="Test", initiator=initiator, affected_chapters={4},
            )
            assert proc.stage == AmendmentStage.INITIATED

    def test_invalid_initiator(self):
        with pytest.raises(AmendmentError, match="Invalid initiator"):
            AmendmentProcess(
                title="Test", initiator="Citizens", affected_chapters={4},
            )


class TestAmendmentStateMachine:
    """Art. 235: Full amendment lifecycle."""

    def test_happy_path_standard(
        self, standard_amendment, sejm_2_3_vote, senate_absolute_vote,
    ):
        proc = standard_amendment
        proc.first_reading()
        assert proc.stage == AmendmentStage.FIRST_READING_SEJM

        proc.sejm_vote(sejm_2_3_vote)
        assert proc.stage == AmendmentStage.SEJM_PASSED

        proc.senate_vote(senate_absolute_vote)
        assert proc.stage == AmendmentStage.SENATE_PASSED

        proc.president_sign()
        assert proc.stage == AmendmentStage.PRESIDENT_SIGNS

        proc.complete()
        assert proc.stage == AmendmentStage.ADOPTED

    def test_happy_path_with_referendum(
        self, protected_amendment, sejm_2_3_vote, senate_absolute_vote,
    ):
        proc = protected_amendment
        proc.first_reading()
        proc.sejm_vote(sejm_2_3_vote)
        proc.senate_vote(senate_absolute_vote)

        proc.request_referendum()
        assert proc.stage == AmendmentStage.REFERENDUM_REQUESTED

        proc.referendum_result(approved=True)
        assert proc.stage == AmendmentStage.REFERENDUM_PASSED

        proc.president_sign()
        proc.complete()
        assert proc.stage == AmendmentStage.ADOPTED

    def test_referendum_rejected(
        self, protected_amendment, sejm_2_3_vote, senate_absolute_vote,
    ):
        proc = protected_amendment
        proc.first_reading()
        proc.sejm_vote(sejm_2_3_vote)
        proc.senate_vote(senate_absolute_vote)
        proc.request_referendum()
        proc.referendum_result(approved=False)
        assert proc.stage == AmendmentStage.REJECTED

    def test_referendum_not_available_for_non_protected(
        self, standard_amendment, sejm_2_3_vote, senate_absolute_vote,
    ):
        proc = standard_amendment
        proc.first_reading()
        proc.sejm_vote(sejm_2_3_vote)
        proc.senate_vote(senate_absolute_vote)
        with pytest.raises(AmendmentError, match="Chapters I, II, or XII"):
            proc.request_referendum()

    def test_sejm_fails_2_3(self, standard_amendment):
        proc = standard_amendment
        proc.first_reading()
        weak_vote = VoteRecord(
            chamber=Chamber.SEJM,
            votes_for=200,
            votes_against=200,
            votes_abstain=30,
        )
        with pytest.raises(MajorityError):
            proc.sejm_vote(weak_vote)
        assert proc.stage == AmendmentStage.REJECTED

    def test_senate_fails_absolute(self, standard_amendment, sejm_2_3_vote):
        proc = standard_amendment
        proc.first_reading()
        proc.sejm_vote(sejm_2_3_vote)
        weak_vote = VoteRecord(
            chamber=Chamber.SENATE,
            votes_for=50,
            votes_against=40,
            votes_abstain=5,
        )
        with pytest.raises(MajorityError):
            proc.senate_vote(weak_vote)
        assert proc.stage == AmendmentStage.REJECTED


class TestInvalidTransitions:
    """Cannot skip stages."""

    def test_cannot_sejm_vote_without_first_reading(self, standard_amendment):
        vote = VoteRecord(chamber=Chamber.SEJM, votes_for=310, votes_against=80, votes_abstain=10)
        with pytest.raises(AmendmentError, match="Cannot hold Sejm vote"):
            standard_amendment.sejm_vote(vote)

    def test_cannot_sign_before_senate(self, standard_amendment):
        standard_amendment.first_reading()
        with pytest.raises(AmendmentError, match="Cannot sign"):
            standard_amendment.president_sign()

    def test_cannot_complete_before_signing(self, standard_amendment):
        with pytest.raises(AmendmentError, match="Cannot complete"):
            standard_amendment.complete()
