"""Tests for Chapter I: The Republic (Art. 1–29)."""

from konstytucja.chapter_01_republic import (
    Principle,
    StateOrgan,
    branch_of_organ,
    organs_for_branch,
)
from konstytucja.common.types import Branch


class TestPrinciples:
    """Art. 1–29: Fundamental principles exist as enumerated values."""

    def test_all_principles_defined(self):
        assert len(Principle) == 9

    def test_common_good(self):
        assert Principle.COMMON_GOOD.name == "COMMON_GOOD"

    def test_separation_of_powers(self):
        assert Principle.SEPARATION_OF_POWERS.name == "SEPARATION_OF_POWERS"


class TestBranches:
    """Art. 10: Separation of powers into three branches."""

    def test_three_branches(self):
        assert len(Branch) == 3

    def test_all_branches_have_organs(self):
        for branch in Branch:
            assert len(organs_for_branch(branch)) >= 2


class TestStateOrgans:
    """State organs mapped to branches."""

    def test_sejm_is_legislative(self):
        assert branch_of_organ(StateOrgan.SEJM) == Branch.LEGISLATIVE

    def test_senate_is_legislative(self):
        assert branch_of_organ(StateOrgan.SENATE) == Branch.LEGISLATIVE

    def test_president_is_executive(self):
        assert branch_of_organ(StateOrgan.PRESIDENT) == Branch.EXECUTIVE

    def test_council_of_ministers_is_executive(self):
        assert branch_of_organ(StateOrgan.COUNCIL_OF_MINISTERS) == Branch.EXECUTIVE

    def test_constitutional_tribunal_is_judicial(self):
        assert branch_of_organ(StateOrgan.CONSTITUTIONAL_TRIBUNAL) == Branch.JUDICIAL

    def test_independent_organs(self):
        """NIK, NBP, RPO are independent and not assigned to any branch."""
        assert branch_of_organ(StateOrgan.NIK) is None
        assert branch_of_organ(StateOrgan.NBP) is None
        assert branch_of_organ(StateOrgan.RPO) is None

    def test_legislative_organs(self):
        organs = organs_for_branch(Branch.LEGISLATIVE)
        assert StateOrgan.SEJM in organs
        assert StateOrgan.SENATE in organs
