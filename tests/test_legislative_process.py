"""Tests for the legislative process state machine (Art. 118–122)."""

import pytest

from konstytucja.common.errors import LegislativeProcessError, MajorityError
from konstytucja.common.types import Bill, BillStage, Chamber, VoteRecord
from konstytucja.legislative_process import LegislativeProcess


@pytest.fixture
def process():
    """A fresh legislative process."""
    bill = Bill(title="Ustawa o podatku VAT", sponsor="Council of Ministers")
    return LegislativeProcess(bill=bill)


@pytest.fixture
def sejm_pass_vote():
    return VoteRecord(chamber=Chamber.SEJM, votes_for=250, votes_against=180, votes_abstain=10)


@pytest.fixture
def sejm_fail_vote():
    return VoteRecord(chamber=Chamber.SEJM, votes_for=150, votes_against=200, votes_abstain=80)


@pytest.fixture
def senate_pass_vote():
    return VoteRecord(chamber=Chamber.SENATE, votes_for=55, votes_against=40, votes_abstain=5)


@pytest.fixture
def senate_reject_vote():
    return VoteRecord(chamber=Chamber.SENATE, votes_for=55, votes_against=40, votes_abstain=5)


@pytest.fixture
def sejm_absolute_vote():
    return VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=100, votes_abstain=50)


@pytest.fixture
def sejm_three_fifths_vote():
    return VoteRecord(chamber=Chamber.SEJM, votes_for=280, votes_against=160, votes_abstain=20)


class TestHappyPath:
    """Standard bill lifecycle: Sejm -> Senate accepts -> President signs."""

    def test_full_lifecycle(self, process, sejm_pass_vote, senate_pass_vote):
        process.begin_sejm_deliberation()
        assert process.stage == BillStage.SEJM_DELIBERATION

        process.sejm_vote(sejm_pass_vote)
        assert process.stage == BillStage.SEJM_PASSED

        process.send_to_senate()
        assert process.stage == BillStage.SENATE_DELIBERATION

        process.senate_accepts()
        assert process.stage == BillStage.SENATE_PASSED

        process.send_to_president()
        assert process.stage == BillStage.PRESIDENT_REVIEW

        process.president_signs()
        assert process.stage == BillStage.SIGNED

        process.enact()
        assert process.stage == BillStage.ENACTED
        assert len(process.history) == 7


class TestSenateAmendments:
    """Senate amends, Sejm overrides (Art. 121 ust. 3)."""

    def test_override_senate_amendments(
        self, process, sejm_pass_vote, senate_pass_vote, sejm_absolute_vote,
    ):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_amends(senate_pass_vote)
        assert process.stage == BillStage.SENATE_AMENDED

        process.sejm_override_senate(sejm_absolute_vote)
        assert process.stage == BillStage.SEJM_OVERRIDE_VOTE

        process.send_to_president()
        process.president_signs()
        process.enact()
        assert process.stage == BillStage.ENACTED


class TestSenateRejection:
    """Senate rejects, Sejm overrides (Art. 121 ust. 3)."""

    def test_override_senate_rejection(
        self, process, sejm_pass_vote, senate_reject_vote, sejm_absolute_vote,
    ):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_rejects(senate_reject_vote)
        assert process.stage == BillStage.SENATE_REJECTED

        process.sejm_override_senate(sejm_absolute_vote)
        process.send_to_president()
        process.president_signs()
        process.enact()
        assert process.stage == BillStage.ENACTED


class TestPresidentialVeto:
    """Art. 122(5): Presidential veto and 3/5 override."""

    def test_veto_and_override(
        self, process, sejm_pass_vote, senate_pass_vote, sejm_three_fifths_vote,
    ):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_vetoes()
        assert process.stage == BillStage.VETOED

        process.sejm_override_veto(sejm_three_fifths_vote)
        assert process.stage == BillStage.VETO_OVERRIDDEN

        process.enact()
        assert process.stage == BillStage.ENACTED

    def test_veto_override_fails(self, process, sejm_pass_vote, senate_pass_vote):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_vetoes()

        weak_vote = VoteRecord(
            chamber=Chamber.SEJM, votes_for=250, votes_against=180, votes_abstain=10,
        )
        with pytest.raises(MajorityError):
            process.sejm_override_veto(weak_vote)
        assert process.stage == BillStage.REJECTED


class TestConstitutionalTribunal:
    """Art. 122(3)–(4): President refers to Tribunal, Tribunal rules."""

    def test_refer_to_tribunal(self, process, sejm_pass_vote, senate_pass_vote):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_refers_to_tribunal()
        assert process.stage == BillStage.REFERRED_TO_TRIBUNAL


class TestTribunalFlow:
    """Art. 122(4): Tribunal verdict and subsequent flow."""

    def _get_to_tribunal(self, process, sejm_pass_vote):
        """Helper: advance a bill to REFERRED_TO_TRIBUNAL stage."""
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_refers_to_tribunal()

    def test_tribunal_constitutional_returns_to_president(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_constitutional()
        assert process.stage == BillStage.PRESIDENT_REVIEW

    def test_tribunal_constitutional_then_sign_and_enact(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_constitutional()
        process.president_signs()
        process.enact()
        assert process.stage == BillStage.ENACTED

    def test_tribunal_unconstitutional_rejects_bill(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_unconstitutional()
        assert process.stage == BillStage.REJECTED

    def test_cannot_call_constitutional_from_wrong_stage(self, process):
        with pytest.raises(LegislativeProcessError):
            process.tribunal_rules_constitutional()

    def test_cannot_call_unconstitutional_from_wrong_stage(self, process):
        with pytest.raises(LegislativeProcessError):
            process.tribunal_rules_unconstitutional()

    def test_full_lifecycle_with_tribunal(self, process, sejm_pass_vote):
        """Full lifecycle: Sejm -> Senate -> President -> Tribunal -> sign -> enacted."""
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_refers_to_tribunal()
        process.tribunal_rules_constitutional()
        process.president_signs()
        process.enact()
        assert process.stage == BillStage.ENACTED
        assert len(process.history) == 9

    def test_tribunal_history_entry_constitutional(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_constitutional()
        assert "constitutional" in process.history[-1].lower()

    def test_tribunal_history_entry_unconstitutional(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_unconstitutional()
        assert "unconstitutional" in process.history[-1].lower()


class TestPartialUnconstitutionality:
    """Art. 122(4): Partial unconstitutionality — sign with exclusions or return to Sejm."""

    def _get_to_tribunal(self, process, sejm_pass_vote):
        """Helper: advance a bill to REFERRED_TO_TRIBUNAL stage."""
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_refers_to_tribunal()

    def test_partially_unconstitutional_stage(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        assert process.stage == BillStage.PARTIALLY_UNCONSTITUTIONAL

    def test_sign_with_exclusions(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_signs_with_exclusions()
        assert process.stage == BillStage.SIGNED

    def test_sign_with_exclusions_then_enact(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_signs_with_exclusions()
        process.enact()
        assert process.stage == BillStage.ENACTED

    def test_return_to_sejm(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_returns_to_sejm()
        assert process.stage == BillStage.SEJM_DELIBERATION

    def test_return_to_sejm_full_cycle(self, process, sejm_pass_vote):
        """Bill returned to Sejm can go through the full process again."""
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_returns_to_sejm()

        # Second pass through Sejm/Senate/President
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_signs()
        process.enact()
        assert process.stage == BillStage.ENACTED

    def test_cannot_sign_with_exclusions_from_wrong_stage(self, process):
        with pytest.raises(LegislativeProcessError):
            process.president_signs_with_exclusions()

    def test_cannot_return_to_sejm_from_wrong_stage(self, process):
        with pytest.raises(LegislativeProcessError):
            process.president_returns_to_sejm()

    def test_cannot_partially_unconstitutional_from_wrong_stage(self, process):
        with pytest.raises(LegislativeProcessError):
            process.tribunal_rules_partially_unconstitutional()

    def test_history_records_partial_ruling(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        assert "partially" in process.history[-1].lower()

    def test_history_records_exclusion_signing(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_signs_with_exclusions()
        assert "exclusion" in process.history[-1].lower()

    def test_history_records_return_to_sejm(self, process, sejm_pass_vote):
        self._get_to_tribunal(process, sejm_pass_vote)
        process.tribunal_rules_partially_unconstitutional()
        process.president_returns_to_sejm()
        assert "sejm" in process.history[-1].lower()

    def test_full_lifecycle_with_exclusions(self, process, sejm_pass_vote):
        """Full lifecycle count: 9 transitions for sign-with-exclusions path."""
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        process.president_refers_to_tribunal()
        process.tribunal_rules_partially_unconstitutional()
        process.president_signs_with_exclusions()
        process.enact()
        assert process.stage == BillStage.ENACTED
        assert len(process.history) == 9


class TestSejmRejection:
    """Sejm rejects the bill."""

    def test_sejm_rejects(self, process, sejm_fail_vote):
        process.begin_sejm_deliberation()
        with pytest.raises(MajorityError):
            process.sejm_vote(sejm_fail_vote)
        assert process.stage == BillStage.REJECTED


class TestInvalidTransitions:
    """Cannot skip stages in the process."""

    def test_cannot_send_to_senate_before_sejm(self, process):
        with pytest.raises(LegislativeProcessError):
            process.send_to_senate()

    def test_cannot_sign_before_president_review(self, process):
        with pytest.raises(LegislativeProcessError):
            process.president_signs()

    def test_cannot_enact_from_president_review(self, process, sejm_pass_vote, senate_pass_vote):
        process.begin_sejm_deliberation()
        process.sejm_vote(sejm_pass_vote)
        process.send_to_senate()
        process.senate_accepts()
        process.send_to_president()
        with pytest.raises(LegislativeProcessError):
            process.enact()
