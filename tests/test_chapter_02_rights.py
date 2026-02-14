"""Tests for Chapter II: Rights and Freedoms (Art. 30–86)."""

import pytest

from konstytucja.chapter_02_rights import validate_rights_restriction
from konstytucja.common.errors import RightsRestrictionError
from konstytucja.common.types import RightsRestriction


class TestArt31ProportionalityTest:
    """Art. 31(3): Five cumulative conditions for restricting rights."""

    def test_valid_restriction_passes(self, valid_restriction):
        assert validate_rights_restriction(valid_restriction) is True

    def test_all_conditions_must_be_met(self, invalid_restriction):
        with pytest.raises(RightsRestrictionError) as exc_info:
            validate_rights_restriction(invalid_restriction)
        msg = str(exc_info.value)
        assert "not necessary in a democratic state" in msg
        assert "not proportionate" in msg
        assert "violates the essence" in msg

    def test_not_by_statute(self):
        r = RightsRestriction(
            description="Executive order restricting movement",
            by_statute=False,
            necessary_in_democratic_state=True,
            legitimate_aim=True,
            proportionate=True,
            preserves_essence=True,
        )
        with pytest.raises(RightsRestrictionError, match="not established by statute"):
            validate_rights_restriction(r)

    def test_not_necessary(self):
        r = RightsRestriction(
            description="Unnecessary surveillance",
            by_statute=True,
            necessary_in_democratic_state=False,
            legitimate_aim=True,
            proportionate=True,
            preserves_essence=True,
        )
        with pytest.raises(RightsRestrictionError, match="not necessary"):
            validate_rights_restriction(r)

    def test_no_legitimate_aim(self):
        r = RightsRestriction(
            description="Restriction for political convenience",
            by_statute=True,
            necessary_in_democratic_state=True,
            legitimate_aim=False,
            proportionate=True,
            preserves_essence=True,
        )
        with pytest.raises(RightsRestrictionError, match="legitimate aim"):
            validate_rights_restriction(r)

    def test_not_proportionate(self):
        r = RightsRestriction(
            description="Disproportionate penalty",
            by_statute=True,
            necessary_in_democratic_state=True,
            legitimate_aim=True,
            proportionate=False,
            preserves_essence=True,
        )
        with pytest.raises(RightsRestrictionError, match="not proportionate"):
            validate_rights_restriction(r)

    def test_violates_essence(self):
        r = RightsRestriction(
            description="Total elimination of right to privacy",
            by_statute=True,
            necessary_in_democratic_state=True,
            legitimate_aim=True,
            proportionate=True,
            preserves_essence=False,
        )
        with pytest.raises(RightsRestrictionError, match="violates the essence"):
            validate_rights_restriction(r)

    def test_multiple_failures_reported(self):
        r = RightsRestriction(
            description="Terrible restriction",
            by_statute=False,
            necessary_in_democratic_state=False,
            legitimate_aim=False,
            proportionate=False,
            preserves_essence=False,
        )
        with pytest.raises(RightsRestrictionError) as exc_info:
            validate_rights_restriction(r)
        msg = str(exc_info.value)
        assert "not established by statute" in msg
        assert "not necessary" in msg
        assert "legitimate aim" in msg
        assert "not proportionate" in msg
        assert "violates the essence" in msg
