"""Tests for Chapter III: Sources of Law (Art. 87–94)."""

import pytest

from konstytucja.chapter_03_sources_of_law import (
    can_regulate,
    prevails,
    rank,
    resolve_conflict,
)
from konstytucja.common.errors import LegalHierarchyError
from konstytucja.common.types import LegalActType


class TestHierarchy:
    """Art. 87: Legal hierarchy of acts."""

    def test_constitution_is_highest(self):
        assert rank(LegalActType.CONSTITUTION) == 0

    def test_statute_above_regulation(self):
        assert rank(LegalActType.STATUTE) < rank(LegalActType.REGULATION)

    def test_treaty_above_statute(self):
        """Art. 91(2): Ratified treaties prevail over statutes."""
        assert rank(LegalActType.RATIFIED_TREATY) < rank(LegalActType.STATUTE)

    def test_local_act_is_lowest(self):
        assert rank(LegalActType.LOCAL_ACT) == max(rank(t) for t in LegalActType)

    def test_full_order(self):
        types = sorted(LegalActType, key=rank)
        assert types == [
            LegalActType.CONSTITUTION,
            LegalActType.RATIFIED_TREATY,
            LegalActType.STATUTE,
            LegalActType.REGULATION,
            LegalActType.LOCAL_ACT,
        ]


class TestPrevails:
    """Art. 8: Constitution is supreme."""

    def test_constitution_prevails_over_statute(self):
        assert prevails(LegalActType.CONSTITUTION, LegalActType.STATUTE) is True

    def test_treaty_prevails_over_statute(self):
        assert prevails(LegalActType.RATIFIED_TREATY, LegalActType.STATUTE) is True

    def test_statute_cannot_prevail_over_constitution(self):
        with pytest.raises(LegalHierarchyError):
            prevails(LegalActType.STATUTE, LegalActType.CONSTITUTION)

    def test_regulation_cannot_prevail_over_statute(self):
        with pytest.raises(LegalHierarchyError):
            prevails(LegalActType.REGULATION, LegalActType.STATUTE)

    def test_same_rank_prevails(self):
        assert prevails(LegalActType.STATUTE, LegalActType.STATUTE) is True


class TestResolveConflict:
    """Conflict resolution: higher-ranked act wins."""

    def test_constitution_vs_statute(self):
        result = resolve_conflict(LegalActType.CONSTITUTION, LegalActType.STATUTE)
        assert result == LegalActType.CONSTITUTION

    def test_statute_vs_regulation(self):
        result = resolve_conflict(LegalActType.STATUTE, LegalActType.REGULATION)
        assert result == LegalActType.STATUTE

    def test_reversed_order(self):
        result = resolve_conflict(LegalActType.REGULATION, LegalActType.STATUTE)
        assert result == LegalActType.STATUTE


class TestCanRegulate:
    """Art. 87: Sources of universally binding law."""

    def test_all_types_are_sources(self):
        for act_type in LegalActType:
            assert can_regulate(act_type) is True
