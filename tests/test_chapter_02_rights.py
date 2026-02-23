"""Tests for Chapter II: Rights and Freedoms (Art. 30–86)."""

import pytest

from konstytucja.chapter_02_rights import validate_extradition, validate_rights_restriction
from konstytucja.common.errors import ExtraditionError, RightsRestrictionError
from konstytucja.common.types import ExtraditionRequest, RightsRestriction


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


# ---------------------------------------------------------------------------
# Art. 55: Extradition [nowelizacja 2006]
# ---------------------------------------------------------------------------


class TestArt55Extradition:
    """Art. 55 [2006 amendment]: Extradition rules."""

    def test_non_citizen_allowed(self):
        """Non-Polish citizens may be extradited (no Art. 55(1) protection)."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Germany",
            court_approved=True,
        )
        assert validate_extradition(req) is True

    def test_polish_citizen_blocked_by_default(self):
        """Art. 55(1): Extradition of a Polish citizen is prohibited by default."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Germany",
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="prohibited") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(1)"

    def test_polish_citizen_eaw_allowed(self):
        """Art. 55(2): Polish citizen extradited under EAW/treaty if conditions met."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Germany",
            based_on_ratified_treaty=True,
            act_committed_abroad=True,
            double_criminality=True,
            court_approved=True,
        )
        assert validate_extradition(req) is True

    def test_polish_citizen_eaw_missing_abroad(self):
        """Art. 55(2)(1): Act must be committed outside Poland."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Germany",
            based_on_ratified_treaty=True,
            act_committed_abroad=False,
            double_criminality=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="outside Polish territory"):
            validate_extradition(req)

    def test_polish_citizen_eaw_missing_double_criminality(self):
        """Art. 55(2)(2): Double criminality required."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="France",
            based_on_ratified_treaty=True,
            act_committed_abroad=True,
            double_criminality=False,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="Polish law"):
            validate_extradition(req)

    def test_polish_citizen_eaw_both_conditions_missing(self):
        """Art. 55(2): Both conditions (1) and (2) reported when missing."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Spain",
            based_on_ratified_treaty=True,
            act_committed_abroad=False,
            double_criminality=False,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError) as exc_info:
            validate_extradition(req)
        msg = str(exc_info.value)
        assert "outside Polish territory" in msg
        assert "Polish law" in msg
        assert exc_info.value.article == "55(2)"

    def test_icc_genocide_bypasses_conditions(self):
        """Art. 55(3): ICC request for genocide bypasses Art. 55(2) conditions."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="International Criminal Court",
            based_on_ratified_treaty=True,
            international_judicial_body=True,
            genocide_or_war_crime=True,
            act_committed_abroad=False,   # not required for Art. 55(3)
            double_criminality=False,     # not required for Art. 55(3)
            court_approved=True,
        )
        assert validate_extradition(req) is True

    def test_icc_non_genocide_falls_through(self):
        """Art. 55(3) only applies to genocide/war crimes/aggression."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="International Criminal Court",
            based_on_ratified_treaty=True,
            international_judicial_body=True,
            genocide_or_war_crime=False,
            act_committed_abroad=False,
            double_criminality=False,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError):
            validate_extradition(req)

    def test_icc_without_treaty_falls_through(self):
        """Art. 55(3) requires treaty basis even for ICC."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="International Criminal Court",
            based_on_ratified_treaty=False,
            international_judicial_body=True,
            genocide_or_war_crime=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="prohibited"):
            validate_extradition(req)

    def test_political_nonviolent_blocked(self):
        """Art. 55(4): Political nonviolent offence — absolute prohibition."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Belarus",
            political_nonviolent_offense=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="political") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(4)"

    def test_human_rights_violation_blocked(self):
        """Art. 55(4): Extradition violating human rights — absolute prohibition."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Country X",
            violates_human_rights=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="human rights") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(4)"

    def test_political_blocks_even_with_treaty(self):
        """Art. 55(4) takes precedence over Art. 55(2) treaty-based extradition."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Some State",
            based_on_ratified_treaty=True,
            act_committed_abroad=True,
            double_criminality=True,
            political_nonviolent_offense=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="political"):
            validate_extradition(req)

    def test_court_approval_required(self):
        """Art. 55(5): Court must approve admissibility."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Germany",
            court_approved=False,
        )
        with pytest.raises(ExtraditionError, match="court") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(5)"

    def test_court_approval_checked_before_citizen_rules(self):
        """Art. 55(5) is checked even for non-citizens."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Germany",
            court_approved=False,
        )
        with pytest.raises(ExtraditionError) as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(5)"

    def test_art55_4_checked_before_court(self):
        """Art. 55(4) absolute prohibitions are checked before Art. 55(5) court."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Country X",
            political_nonviolent_offense=True,
            court_approved=False,
        )
        with pytest.raises(ExtraditionError) as exc_info:
            validate_extradition(req)
        # Art. 55(4) should fire first, not 55(5)
        assert exc_info.value.article == "55(4)"

    def test_human_rights_blocks_even_with_treaty(self):
        """Art. 55(4) human-rights prohibition overrides treaty-based extradition."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="Some State",
            based_on_ratified_treaty=True,
            act_committed_abroad=True,
            double_criminality=True,
            violates_human_rights=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="human rights") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(4)"

    def test_icc_genocide_blocked_by_human_rights(self):
        """Art. 55(4) blocks even ICC genocide requests that violate human rights."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=True,
            requesting_state_or_body="International Criminal Court",
            based_on_ratified_treaty=True,
            international_judicial_body=True,
            genocide_or_war_crime=True,
            violates_human_rights=True,
            court_approved=True,
        )
        with pytest.raises(ExtraditionError, match="human rights") as exc_info:
            validate_extradition(req)
        assert exc_info.value.article == "55(4)"

    def test_non_citizen_no_treaty_needed(self):
        """Non-citizens can be extradited without treaty basis (Art. 55(1) is citizen-only)."""
        req = ExtraditionRequest(
            subject_is_polish_citizen=False,
            requesting_state_or_body="Country Y",
            based_on_ratified_treaty=False,
            court_approved=True,
        )
        assert validate_extradition(req) is True
