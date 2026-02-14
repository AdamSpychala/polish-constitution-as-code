"""19 interactive demo scenarios for the Polish Constitution as Code.

Run: uv run python examples/demo.py
"""

from datetime import date
from decimal import Decimal

from konstytucja.chapter_01_republic import (
    Branch,
    Principle,
    StateOrgan,
    branch_of_organ,
    organs_for_branch,
)
from konstytucja.chapter_02_rights import validate_rights_restriction
from konstytucja.chapter_03_sources_of_law import prevails, resolve_conflict
from konstytucja.chapter_04_sejm_senate import (
    check_incompatibility,
    check_sejm_eligibility,
    check_senate_eligibility,
    sejm_passes_bill,
    validate_parliamentary_immunity,
    validate_referendum,
)
from konstytucja.chapter_05_president import (
    check_presidential_eligibility,
    sejm_overrides_veto,
    validate_presidential_term,
)
from konstytucja.chapter_06_council_of_ministers import (
    GovernmentFormation,
    validate_confidence_vote,
    validate_constructive_no_confidence,
    validate_council_composition,
    validate_individual_minister_no_confidence,
)
from konstytucja.chapter_07_local_government import (
    check_supervision_legality,
    validate_dissolution,
    validate_local_unit,
)
from konstytucja.chapter_08_courts import (
    check_two_instance_requirement,
    validate_judge_appointment,
    validate_judicial_independence,
    validate_state_tribunal_subject,
)
from konstytucja.chapter_09_oversight import (
    validate_krrit_composition,
    validate_nik_appointment,
    validate_rpo_appointment,
)
from konstytucja.chapter_10_public_finances import (
    check_debt_ceiling,
    remaining_capacity,
    validate_currency_issuance,
    validate_nbp_independence,
)
from konstytucja.chapter_11_emergency import (
    check_election_allowed,
    check_emergency_rights_restriction,
    validate_declaration,
)
from konstytucja.chapter_12_amendments import AmendmentProcess
from konstytucja.common.types import (
    AmendmentStage,
    Bill,
    BillStage,
    Chamber,
    Citizen,
    CouncilOfMinisters,
    CourtType,
    EmergencyDeclaration,
    EmergencyType,
    GovernmentFormationStage,
    Judge,
    LegalActType,
    LocalGovernmentTier,
    LocalGovernmentUnit,
    Minister,
    OversightAppointment,
    OversightOrgan,
    PublicDebt,
    RightsRestriction,
    VoteRecord,
)
from konstytucja.legislative_process import LegislativeProcess


def separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def scenario_1_separation_of_powers():
    separator("Scenario 1: Separation of Powers (Art. 10)")

    for branch in Branch:
        organs = organs_for_branch(branch)
        organ_names = ", ".join(o.name for o in organs)
        print(f"  {branch.value}: {organ_names}")

    print(f"\n  Sejm belongs to: {branch_of_organ(StateOrgan.SEJM).value}")
    print(f"  NIK belongs to: {branch_of_organ(StateOrgan.NIK)} (independent)")


def scenario_2_eligibility():
    separator("Scenario 2: Eligibility Checks (Art. 99, 127)")

    jan = Citizen(name="Jan Kowalski", date_of_birth=date(1985, 6, 15))
    anna = Citizen(name="Anna Młoda", date_of_birth=date(2005, 3, 1))
    election = date(2025, 10, 15)

    # Sejm
    print("  Jan (40) for Sejm:", end=" ")
    try:
        check_sejm_eligibility(jan, election)
        print("ELIGIBLE")
    except Exception as e:
        print(f"INELIGIBLE: {e}")

    print("  Anna (20) for Sejm:", end=" ")
    try:
        check_sejm_eligibility(anna, election)
        print("ELIGIBLE")
    except Exception as e:
        print(f"INELIGIBLE: {e}")

    # President
    print("  Jan for President (150K signatures):", end=" ")
    try:
        check_presidential_eligibility(jan, election, signatures=150_000)
        print("ELIGIBLE")
    except Exception as e:
        print(f"INELIGIBLE: {e}")

    print("  Jan for President (50K signatures):", end=" ")
    try:
        check_presidential_eligibility(jan, election, signatures=50_000)
        print("ELIGIBLE")
    except Exception as e:
        print(f"INELIGIBLE: {e}")


def scenario_3_voting():
    separator("Scenario 3: Voting & Quorum (Art. 120)")

    # Passes
    vote = VoteRecord(chamber=Chamber.SEJM, votes_for=250, votes_against=180, votes_abstain=10)
    print(f"  Sejm vote: {vote.votes_for} for, {vote.votes_against} against, "
          f"{vote.votes_abstain} abstain ({vote.total_present} present)")
    try:
        sejm_passes_bill(vote)
        print("  Result: PASSED (simple majority)")
    except Exception as e:
        print(f"  Result: FAILED — {e}")

    # No quorum
    vote2 = VoteRecord(chamber=Chamber.SEJM, votes_for=100, votes_against=50, votes_abstain=5)
    print(f"\n  Sejm vote: {vote2.votes_for} for, {vote2.votes_against} against "
          f"({vote2.total_present} present)")
    try:
        sejm_passes_bill(vote2)
        print("  Result: PASSED")
    except Exception as e:
        print(f"  Result: FAILED — {e}")


def scenario_4_veto_override():
    separator("Scenario 4: Presidential Veto Override (Art. 122)")

    # Successful override
    vote = VoteRecord(chamber=Chamber.SEJM, votes_for=280, votes_against=160, votes_abstain=20)
    print(f"  Override attempt: {vote.votes_for}/{vote.total_present} = "
          f"{vote.votes_for/vote.total_present:.1%}")
    try:
        sejm_overrides_veto(vote)
        print("  Result: VETO OVERRIDDEN (3/5 majority met)")
    except Exception as e:
        print(f"  Result: VETO STANDS — {e}")

    # Failed override
    vote2 = VoteRecord(chamber=Chamber.SEJM, votes_for=250, votes_against=180, votes_abstain=30)
    print(f"\n  Override attempt: {vote2.votes_for}/{vote2.total_present} = "
          f"{vote2.votes_for/vote2.total_present:.1%}")
    try:
        sejm_overrides_veto(vote2)
        print("  Result: VETO OVERRIDDEN")
    except Exception as e:
        print(f"  Result: VETO STANDS — {e}")


def scenario_5_debt_ceiling():
    separator("Scenario 5: Debt Ceiling (Art. 216)")

    # Within ceiling
    state = PublicDebt(debt=Decimal("500_000_000_000"), gdp=Decimal("1_000_000_000_000"))
    print(f"  Debt: {state.debt:,.0f} PLN")
    print(f"  GDP:  {state.gdp:,.0f} PLN")
    print(f"  Ratio: {state.debt/state.gdp:.1%}")
    try:
        check_debt_ceiling(state)
        cap = remaining_capacity(state)
        print(f"  Status: WITHIN CEILING (remaining capacity: {cap:,.0f} PLN)")
    except Exception as e:
        print(f"  Status: VIOLATION — {e}")

    # Over ceiling
    state2 = PublicDebt(debt=Decimal("700_000_000_000"), gdp=Decimal("1_000_000_000_000"))
    print(f"\n  Debt: {state2.debt:,.0f} PLN")
    print(f"  GDP:  {state2.gdp:,.0f} PLN")
    print(f"  Ratio: {state2.debt/state2.gdp:.1%}")
    try:
        check_debt_ceiling(state2)
        print("  Status: WITHIN CEILING")
    except Exception as e:
        print(f"  Status: VIOLATION — {e}")


def scenario_6_emergency():
    separator("Scenario 6: Emergency Powers (Art. 228–234)")

    decl = EmergencyDeclaration(
        emergency_type=EmergencyType.STATE_OF_EMERGENCY,
        start_date=date(2025, 1, 1),
        duration_days=90,
        reason="Threat to constitutional order",
    )
    print(f"  Type: {decl.emergency_type.value}")
    print(f"  Duration: {decl.duration_days} days")
    validate_declaration(decl)
    print("  Declaration: VALID")

    # Elections blocked
    election_date = date(2025, 3, 15)
    print(f"\n  Proposed election: {election_date}")
    try:
        check_election_allowed(decl, election_date)
        print("  Elections: ALLOWED")
    except Exception as e:
        print(f"  Elections: BLOCKED — {e}")

    # After cooling period
    late_date = date(2025, 7, 2)
    print(f"\n  Proposed election: {late_date}")
    try:
        check_election_allowed(decl, late_date)
        print("  Elections: ALLOWED")
    except Exception as e:
        print(f"  Elections: BLOCKED — {e}")


def scenario_7_rights_restriction():
    separator("Scenario 7: Rights Restriction Test (Art. 31)")

    # Valid
    r1 = RightsRestriction(
        description="Quarantine during epidemic",
        by_statute=True,
        necessary_in_democratic_state=True,
        legitimate_aim=True,
        proportionate=True,
        preserves_essence=True,
    )
    print(f"  Restriction: {r1.description}")
    try:
        validate_rights_restriction(r1)
        print("  Result: CONSTITUTIONAL")
    except Exception as e:
        print(f"  Result: UNCONSTITUTIONAL — {e}")

    # Invalid
    r2 = RightsRestriction(
        description="Total ban on peaceful assembly",
        by_statute=True,
        necessary_in_democratic_state=False,
        legitimate_aim=True,
        proportionate=False,
        preserves_essence=False,
    )
    print(f"\n  Restriction: {r2.description}")
    try:
        validate_rights_restriction(r2)
        print("  Result: CONSTITUTIONAL")
    except Exception as e:
        print(f"  Result: UNCONSTITUTIONAL — {e}")


def scenario_8_legislative_process():
    separator("Scenario 8: Full Legislative Process (Art. 118–122)")

    bill = Bill(title="Ustawa o cyfryzacji", sponsor="Council of Ministers")
    proc = LegislativeProcess(bill=bill)
    print(f"  Bill: {bill.title}")

    proc.begin_sejm_deliberation()
    print(f"  Stage: {proc.stage.name}")

    sejm_vote = VoteRecord(chamber=Chamber.SEJM, votes_for=260, votes_against=170, votes_abstain=10)
    proc.sejm_vote(sejm_vote)
    print(f"  Sejm vote: {sejm_vote.votes_for}-{sejm_vote.votes_against} -> {proc.stage.name}")

    proc.send_to_senate()
    proc.senate_accepts()
    print(f"  Senate: accepted -> {proc.stage.name}")

    proc.send_to_president()
    proc.president_signs()
    print(f"  President: signed -> {proc.stage.name}")

    proc.enact()
    print(f"  Final: {proc.stage.name}")
    print(f"\n  History ({len(proc.history)} transitions):")
    for entry in proc.history:
        print(f"    {entry}")


def scenario_9_tribunal_review():
    separator("Scenario 9: Constitutional Tribunal Review (Art. 122, 188)")

    bill = Bill(title="Ustawa o mediach", sponsor="Deputies")
    proc = LegislativeProcess(bill=bill)
    print(f"  Bill: {bill.title}")

    proc.begin_sejm_deliberation()
    sejm_vote = VoteRecord(chamber=Chamber.SEJM, votes_for=240, votes_against=190, votes_abstain=10)
    proc.sejm_vote(sejm_vote)
    print(f"  Sejm vote: {sejm_vote.votes_for}-{sejm_vote.votes_against} -> {proc.stage.name}")

    proc.send_to_senate()
    proc.senate_accepts()
    print(f"  Senate: accepted -> {proc.stage.name}")

    proc.send_to_president()
    print(f"  President review: {proc.stage.name}")

    proc.president_refers_to_tribunal()
    print(f"  President refers to Tribunal: {proc.stage.name}")

    proc.tribunal_rules_constitutional()
    print(f"  Tribunal rules: CONSTITUTIONAL -> {proc.stage.name}")

    proc.president_signs()
    proc.enact()
    print(f"  President signs after Tribunal ruling -> {proc.stage.name}")

    print(f"\n  History ({len(proc.history)} transitions):")
    for entry in proc.history:
        print(f"    {entry}")


def scenario_10_partial_unconstitutionality():
    separator("Scenario 10: Partial Unconstitutionality (Art. 122 ust. 4)")

    # Path A: President signs with exclusions
    bill_a = Bill(title="Ustawa o ochronie danych", sponsor="Council of Ministers")
    proc_a = LegislativeProcess(bill=bill_a)
    print(f"  Path A — Sign with exclusions:")
    print(f"  Bill: {bill_a.title}")

    proc_a.begin_sejm_deliberation()
    vote = VoteRecord(chamber=Chamber.SEJM, votes_for=245, votes_against=185, votes_abstain=10)
    proc_a.sejm_vote(vote)
    proc_a.send_to_senate()
    proc_a.senate_accepts()
    proc_a.send_to_president()
    proc_a.president_refers_to_tribunal()
    proc_a.tribunal_rules_partially_unconstitutional()
    print(f"  Tribunal: PARTIALLY UNCONSTITUTIONAL -> {proc_a.stage.name}")

    proc_a.president_signs_with_exclusions()
    proc_a.enact()
    print(f"  President signs with exclusions -> {proc_a.stage.name}")

    # Path B: President returns to Sejm
    bill_b = Bill(title="Ustawa o zgromadzeniach", sponsor="Deputies")
    proc_b = LegislativeProcess(bill=bill_b)
    print(f"\n  Path B — Return to Sejm:")
    print(f"  Bill: {bill_b.title}")

    proc_b.begin_sejm_deliberation()
    proc_b.sejm_vote(vote)
    proc_b.send_to_senate()
    proc_b.senate_accepts()
    proc_b.send_to_president()
    proc_b.president_refers_to_tribunal()
    proc_b.tribunal_rules_partially_unconstitutional()
    print(f"  Tribunal: PARTIALLY UNCONSTITUTIONAL -> {proc_b.stage.name}")

    proc_b.president_returns_to_sejm()
    print(f"  President returns to Sejm -> {proc_b.stage.name}")

    proc_b.sejm_vote(vote)
    proc_b.send_to_senate()
    proc_b.senate_accepts()
    proc_b.send_to_president()
    proc_b.president_signs()
    proc_b.enact()
    print(f"  Second pass: Sejm -> Senate -> President signs -> {proc_b.stage.name}")

    print(f"\n  Path B history ({len(proc_b.history)} transitions):")
    for entry in proc_b.history:
        print(f"    {entry}")


def scenario_11_council_of_ministers():
    separator("Scenario 11: Council of Ministers (Art. 146–162)")

    # Valid council
    council = CouncilOfMinisters(
        prime_minister=Minister(name="Jan Kowalski", role="Prime Minister"),
        ministers=(
            Minister(name="Anna Nowak", role="Minister of Finance"),
            Minister(name="Piotr Wiśniewski", role="Minister of Defence"),
        ),
    )
    print(f"  PM: {council.prime_minister.name}")
    print(f"  Ministers: {len(council.ministers)}")
    validate_council_composition(council)
    print("  Composition: VALID")

    # Confidence vote — passes
    vote = VoteRecord(chamber=Chamber.SEJM, votes_for=240, votes_against=190, votes_abstain=10)
    print(f"\n  Confidence vote: {vote.votes_for} for, {vote.votes_against} against")
    try:
        validate_confidence_vote(vote)
        print("  Result: CONFIDENCE GRANTED")
    except Exception as e:
        print(f"  Result: CONFIDENCE DENIED — {e}")

    # Constructive no-confidence
    no_conf_vote = VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=200, votes_abstain=10)
    print(f"\n  No-confidence vote: {no_conf_vote.votes_for} for (successor: Maria Nowa)")
    try:
        validate_constructive_no_confidence(no_conf_vote, "Maria Nowa")
        print("  Result: NO CONFIDENCE PASSED — new PM: Maria Nowa")
    except Exception as e:
        print(f"  Result: NO CONFIDENCE FAILED — {e}")


def scenario_12_local_government():
    separator("Scenario 12: Local Government (Art. 163–172)")

    # Valid gmina
    gmina = LocalGovernmentUnit(name="Gmina Kraków", tier=LocalGovernmentTier.GMINA)
    print(f"  Unit: {gmina.name} ({gmina.tier.value})")
    validate_local_unit(gmina)
    print("  Validation: VALID")

    # Supervision — valid
    print("\n  Supervision: audit compliance (by statute)")
    check_supervision_legality("audit compliance", by_statute=True)
    print("  Result: LAWFUL")

    # Supervision — invalid
    print("\n  Supervision: political review (no statutory basis)")
    try:
        check_supervision_legality("political review", by_statute=False)
        print("  Result: LAWFUL")
    except Exception as e:
        print(f"  Result: UNLAWFUL — {e}")

    # Dissolution
    print("\n  Dissolution of gmina (persistent violation: True)")
    validate_dissolution(LocalGovernmentTier.GMINA, persistent_violation=True)
    print("  Result: DISSOLUTION VALID")

    print("\n  Dissolution of gmina (persistent violation: False)")
    try:
        validate_dissolution(LocalGovernmentTier.GMINA, persistent_violation=False)
        print("  Result: DISSOLUTION VALID")
    except Exception as e:
        print(f"  Result: DISSOLUTION INVALID — {e}")


def scenario_13_oversight_organs():
    separator("Scenario 13: Oversight Organs (Art. 202–215)")

    # NIK
    nik = OversightAppointment(
        organ=OversightOrgan.NIK,
        name="Jan Kontroler",
        sejm_approved=True,
        senate_approved=True,
    )
    print(f"  NIK President: {nik.name}")
    validate_nik_appointment(nik)
    print("  Appointment: VALID")

    # NIK — no senate consent
    nik_bad = OversightAppointment(
        organ=OversightOrgan.NIK,
        name="Piotr Bez Zgody",
        sejm_approved=True,
        senate_approved=False,
    )
    print(f"\n  NIK President: {nik_bad.name} (no Senate consent)")
    try:
        validate_nik_appointment(nik_bad)
        print("  Appointment: VALID")
    except Exception as e:
        print(f"  Appointment: INVALID — {e}")

    # RPO
    rpo = OversightAppointment(
        organ=OversightOrgan.RPO,
        name="Anna Rzecznik",
        sejm_approved=True,
        senate_approved=True,
    )
    print(f"\n  RPO: {rpo.name}")
    validate_rpo_appointment(rpo)
    print("  Appointment: VALID")

    # KRRiT
    print("\n  KRRiT composition: Sejm=2, Senate=1, President=1")
    validate_krrit_composition(2, 1, 1)
    print("  Composition: VALID")

    print("\n  KRRiT composition: Sejm=3, Senate=1, President=1")
    try:
        validate_krrit_composition(3, 1, 1)
        print("  Composition: VALID")
    except Exception as e:
        print(f"  Composition: INVALID — {e}")


def scenario_14_judicial_independence():
    separator("Scenario 14: Courts & Judicial Independence (Art. 173–187)")

    # Valid judge appointment
    judge = Judge(name="Maria Sędziak", court_type=CourtType.COMMON)
    print(f"  Judge: {judge.name} ({judge.court_type.value})")
    validate_judge_appointment(judge)
    print("  Appointment: VALID (President + KRS)")

    # Invalid appointment
    bad_judge = Judge(
        name="Jan Bez Nominacji",
        court_type=CourtType.COMMON,
        appointed_by_president=True,
        krs_nominated=False,
    )
    print(f"\n  Judge: {bad_judge.name} (no KRS nomination)")
    try:
        validate_judge_appointment(bad_judge)
        print("  Appointment: VALID")
    except Exception as e:
        print(f"  Appointment: INVALID — {e}")

    # Judicial independence
    print("\n  Subject to: Constitution and statutes")
    validate_judicial_independence("Constitution and statutes")
    print("  Independence: PRESERVED")

    print("\n  Subject to: executive orders")
    try:
        validate_judicial_independence("executive orders")
        print("  Independence: PRESERVED")
    except Exception as e:
        print(f"  Independence: VIOLATED — {e}")

    # Two-instance requirement
    print("\n  Court instances: 2")
    check_two_instance_requirement(2)
    print("  Two-instance rule: SATISFIED")

    print("\n  Court instances: 1")
    try:
        check_two_instance_requirement(1)
        print("  Two-instance rule: SATISFIED")
    except Exception as e:
        print(f"  Two-instance rule: VIOLATED — {e}")


def scenario_15_government_formation():
    separator("Scenario 15: Government Formation (Art. 154–155)")

    # First attempt succeeds
    print("  Attempt 1: President designates PM -> Sejm confidence vote")
    gf = GovernmentFormation()
    gf.president_designates()
    vote = VoteRecord(chamber=Chamber.SEJM, votes_for=231, votes_against=200, votes_abstain=10)
    gf.sejm_confidence_first_attempt(vote)
    print(f"  Vote: {vote.votes_for} for -> Stage: {gf.stage.name}")

    # Full three-attempt failure path
    print("\n  Full 3-attempt failure path:")
    gf2 = GovernmentFormation()
    gf2.president_designates()
    fail_vote = VoteRecord(chamber=Chamber.SEJM, votes_for=200, votes_against=230)
    gf2.sejm_confidence_first_attempt(fail_vote)
    print(f"  1st attempt (absolute majority): {fail_vote.votes_for} for -> {gf2.stage.name}")

    gf2.sejm_elects_pm(fail_vote)
    print(f"  2nd attempt (Sejm elects): {fail_vote.votes_for} for -> {gf2.stage.name}")

    gf2.president_appoints_third_attempt(fail_vote)
    print(f"  3rd attempt (simple majority): {fail_vote.votes_for} for -> {gf2.stage.name}")
    print("  Result: Sejm dissolved (Art. 155(2))")


def scenario_16_state_tribunal():
    separator("Scenario 16: State Tribunal (Art. 198–201)")

    # Valid subjects
    for subject in ("President", "Prime Minister", "Minister"):
        validate_state_tribunal_subject(subject)
        print(f"  {subject}: subject to State Tribunal jurisdiction")

    # Invalid subject
    print()
    try:
        validate_state_tribunal_subject("Bank Manager")
        print("  Bank Manager: subject to jurisdiction")
    except Exception as e:
        print(f"  Bank Manager: NOT subject — {e}")


def scenario_17_parliamentary_immunity():
    separator("Scenario 17: Parliamentary Immunity & Incompatibility (Art. 103, 105)")

    # Immunity
    print("  Deputy prosecution with Sejm consent: ", end="")
    validate_parliamentary_immunity(Chamber.SEJM, consent_given=True)
    print("ALLOWED")

    print("  Deputy prosecution without consent: ", end="")
    try:
        validate_parliamentary_immunity(Chamber.SEJM, consent_given=False)
        print("ALLOWED")
    except Exception as e:
        print(f"BLOCKED — {e}")

    # Incompatibility
    print("\n  Deputy + Teacher: ", end="")
    check_incompatibility("Teacher")
    print("COMPATIBLE")

    print("  Deputy + Ambassador: ", end="")
    try:
        check_incompatibility("Ambassador")
        print("COMPATIBLE")
    except Exception as e:
        print(f"INCOMPATIBLE — {e}")


def scenario_18_nbp_and_referendum():
    separator("Scenario 18: NBP & Referendum (Art. 125, 227)")

    # NBP independence
    validate_nbp_independence("NBP")
    print("  Monetary policy by NBP: VALID")

    try:
        validate_nbp_independence("Council of Ministers")
        print("  Monetary policy by Government: VALID")
    except Exception as e:
        print(f"  Monetary policy by Government: INVALID — {e}")

    validate_currency_issuance("NBP")
    print("\n  Currency issued by NBP: VALID")

    # Referendum
    print("\n  Referendum: 600K for, 400K against, 1M eligible")
    validate_referendum(600_000, 400_000, eligible_voters=1_000_000)
    print("  Result: PASSED (binding)")

    print("\n  Referendum: 300K for, 100K against, 1M eligible")
    try:
        validate_referendum(300_000, 100_000, eligible_voters=1_000_000)
        print("  Result: PASSED")
    except Exception as e:
        print(f"  Result: NOT BINDING — {e}")


def scenario_19_emergency_rights():
    separator("Scenario 19: Non-Restrictable Rights (Art. 233)")

    print("  During martial law:")
    # Art. 30 — human dignity: non-restrictable
    try:
        check_emergency_rights_restriction(30, EmergencyType.MARTIAL_LAW)
        print("    Art. 30 (human dignity): CAN be restricted")
    except Exception:
        print("    Art. 30 (human dignity): CANNOT be restricted (absolutely protected)")

    # Art. 50 — not in protected list
    check_emergency_rights_restriction(50, EmergencyType.MARTIAL_LAW)
    print("    Art. 50 (home inviolability): CAN be restricted")

    # Art. 38 — protection of life
    try:
        check_emergency_rights_restriction(38, EmergencyType.STATE_OF_EMERGENCY)
        print("    Art. 38 (right to life): CAN be restricted")
    except Exception:
        print("    Art. 38 (right to life): CANNOT be restricted (absolutely protected)")

    # Presidential term limit
    print("\n  Presidential term limits (Art. 127(2)):")
    validate_presidential_term(0)
    print("    First term: ALLOWED")
    validate_presidential_term(1)
    print("    Second term: ALLOWED")
    try:
        validate_presidential_term(2)
        print("    Third term: ALLOWED")
    except Exception as e:
        print(f"    Third term: BLOCKED — {e}")


def main():
    print("Konstytucja RP jako kod / Polish Constitution as Code")
    print("=" * 60)

    scenario_1_separation_of_powers()
    scenario_2_eligibility()
    scenario_3_voting()
    scenario_4_veto_override()
    scenario_5_debt_ceiling()
    scenario_6_emergency()
    scenario_7_rights_restriction()
    scenario_8_legislative_process()
    scenario_9_tribunal_review()
    scenario_10_partial_unconstitutionality()
    scenario_11_council_of_ministers()
    scenario_12_local_government()
    scenario_13_oversight_organs()
    scenario_14_judicial_independence()
    scenario_15_government_formation()
    scenario_16_state_tribunal()
    scenario_17_parliamentary_immunity()
    scenario_18_nbp_and_referendum()
    scenario_19_emergency_rights()

    print(f"\n{'='*60}")
    print("  All 19 scenarios completed successfully.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
