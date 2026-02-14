"""Chapter IX — Organs of State Control and Rights Protection (Art. 202–215).

Rozdział IX — Organy kontroli państwowej i ochrony prawa.

This module encodes the rules governing the appointment and composition
of the Supreme Chamber of Control (NIK), the Commissioner for Citizens'
Rights (RPO), and the National Broadcasting Council (KRRiT).
"""

from konstytucja.common.errors import OversightError
from konstytucja.common.types import OversightAppointment, OversightOrgan

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NIK_TERM_YEARS: int = 6
"""Art. 205 ust. 1: Prezes Najwyższej Izby Kontroli jest powoływany przez
Sejm za zgodą Senatu, na 6 lat.

The President of NIK is appointed by the Sejm with the consent of the
Senate for a term of 6 years.
"""

NIK_MAX_TERMS: int = 2
"""Art. 205 ust. 1: …i może być ponownie powołany tylko raz.

…and may be reappointed only once (maximum 2 terms).
"""

RPO_TERM_YEARS: int = 5
"""Art. 209 ust. 1: Rzecznik Praw Obywatelskich jest powoływany przez Sejm
za zgodą Senatu, na 5 lat.

The Commissioner for Citizens' Rights is appointed by the Sejm with
the consent of the Senate for a term of 5 years.
"""

KRRIT_MEMBERS: dict[str, int] = {
    "Sejm": 2,
    "Senate": 1,
    "President": 1,
}
"""Art. 214 ust. 1: Członków Krajowej Rady Radiofonii i Telewizji powołuje
Sejm (2), Senat (1) i Prezydent Rzeczypospolitej (1).

Members of KRRiT are appointed: 2 by the Sejm, 1 by the Senate,
1 by the President.
"""

# ---------------------------------------------------------------------------
# NIK President appointment — Art. 205
# ---------------------------------------------------------------------------


def validate_nik_appointment(appointment: OversightAppointment) -> bool:
    """Validate appointment of the NIK President.

    Art. 205 ust. 1: Prezes Najwyższej Izby Kontroli jest powoływany
    przez Sejm za zgodą Senatu, na 6 lat, i może być ponownie powołany
    tylko raz.

    The President of NIK is appointed by the Sejm with the consent
    of the Senate for 6 years, and may be reappointed only once.

    Raises:
        OversightError: If the appointment does not meet requirements.
    """
    if appointment.organ != OversightOrgan.NIK:
        raise OversightError(
            f"Expected NIK appointment, got {appointment.organ.value}.",
            article="205",
        )
    if not appointment.sejm_approved:
        raise OversightError(
            "NIK President must be appointed by the Sejm.",
            article="205",
        )
    if not appointment.senate_approved:
        raise OversightError(
            "NIK President appointment requires Senate consent.",
            article="205",
        )
    return True


# ---------------------------------------------------------------------------
# RPO appointment — Art. 209
# ---------------------------------------------------------------------------


def validate_rpo_appointment(appointment: OversightAppointment) -> bool:
    """Validate appointment of the Commissioner for Citizens' Rights (RPO).

    Art. 209 ust. 1: Rzecznik Praw Obywatelskich jest powoływany przez
    Sejm za zgodą Senatu, na 5 lat.

    The RPO is appointed by the Sejm with the consent of the Senate
    for 5 years.

    Raises:
        OversightError: If the appointment does not meet requirements.
    """
    if appointment.organ != OversightOrgan.RPO:
        raise OversightError(
            f"Expected RPO appointment, got {appointment.organ.value}.",
            article="209",
        )
    if not appointment.sejm_approved:
        raise OversightError(
            "RPO must be appointed by the Sejm.",
            article="209",
        )
    if not appointment.senate_approved:
        raise OversightError(
            "RPO appointment requires Senate consent.",
            article="209",
        )
    return True


# ---------------------------------------------------------------------------
# KRRiT composition — Art. 214
# ---------------------------------------------------------------------------


def validate_krrit_composition(
    sejm_members: int, senate_members: int, president_members: int
) -> bool:
    """Validate the composition of the National Broadcasting Council (KRRiT).

    Art. 214 ust. 1: Członków Krajowej Rady Radiofonii i Telewizji
    powołuje Sejm (2), Senat (1) i Prezydent Rzeczypospolitej (1).

    KRRiT is composed of 4 members: 2 appointed by the Sejm,
    1 by the Senate, and 1 by the President.

    Raises:
        OversightError: If the composition does not match Art. 214.
    """
    if sejm_members != KRRIT_MEMBERS["Sejm"]:
        raise OversightError(
            f"KRRiT must have {KRRIT_MEMBERS['Sejm']} members appointed "
            f"by the Sejm, got {sejm_members}.",
            article="214",
        )
    if senate_members != KRRIT_MEMBERS["Senate"]:
        raise OversightError(
            f"KRRiT must have {KRRIT_MEMBERS['Senate']} member appointed "
            f"by the Senate, got {senate_members}.",
            article="214",
        )
    if president_members != KRRIT_MEMBERS["President"]:
        raise OversightError(
            f"KRRiT must have {KRRIT_MEMBERS['President']} member appointed "
            f"by the President, got {president_members}.",
            article="214",
        )
    return True
