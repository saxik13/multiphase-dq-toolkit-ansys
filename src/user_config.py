"""
AOUTVAR GENERATOR
-----------------
USER CONFIGURATION FILE
-----------------------
Edit CONFIG below and run this file.

All unspecified parameters will use safe defaults.
See README for detailed explanation of each parameter.
"""

CONFIG = {
    # 1) MACHINE DEFINITION

    # Number of pole pairs (mandatory): Integer
    "pole_pairs": 2,
    # Number of phases (mandatory): Integer
    "num_phases": 3,

    # 2) MECHANICAL SETTINGS

    # Name of motion setup in Ansys
    # Default: "Moving1"
    "motion_setup": "Moving1",
    
    # Rotation direction:
    # +1 = positive (CCW)
    # -1 = negative (CW)
    # Default: +1
    "rotation_sign": -1,

    
    # Additional mechanical offset in degrees
    # "auto" - automatically calculates when number of slots, winding layers and winding step are defined
    # Default: 0.0
    "mechanical_offset_deg": 0.0,

    # Additional winding information for the automatic mechanical offset calcualtion
    # layers == number of coil sides per slot: 1 or 2
    # coil pitch in number of slots: MUST be odd number of a single-layer winding
    # Default: 0
    "slot_number": 30,
    "layers": 2,
    "coil_pitch": 5,

    # 3) EXCITATION TYPE
    # "Current" (default)
    # "Voltage"
    "excitation_type": "Voltage",

    # 4) PHASE NAMING

    # Base name for automatic phase naming (case sensitive)
    # Default: "Phase"
    "phase_base_name": "Phase",

    # Index style:
    # "upper"   → PhaseA, PhaseB, PhaseC
    # "lower"   → Phasea, Phaseb, Phasec
    # "number"  → Phase1, Phase2, Phase3
    # Default: "upper"
    "phase_index_style": "upper",

    # Optional: explicit phase names
    # Example:
    # ["U1","V1","W1","U2","V2","W2"]
    # None
    # If provided, this overrides base name and index style.
    "custom_phase_names": None,

    # 5) HARMONIC SUBSPACES
    # Spatial harmonic orders ν
    # Example:
    # [1]        → fundamental only
    # [1, 3]     → fundamental + 3rd harmonic subspace
    # [1, 5, 7]  → extended harmonic analysis
    # Default: [1]
    "harmonic_orders": [1],

    # 6) INDUCTANCE PROJECTION
 
    # Generate inductance expressions (Ld, Lq)
    # Default: True
    # False
    "include_inductances": True,

    # Inductance mode:
    # "full"  → full projection including cross-coupling
    # "main"  → only main diagonal Ld and Lq
    # Default: "full"
    "inductance_mode": "main",

    # 7) OPTIONALS - values which can be used in the "Current" Excitation type to calculate the terminal voltages
    # Stator winding resistance [Ohm]
    # Default: 0
    "resistance_stat": 1,
    # Endwinding inductance [H]
    # Default: 0
    "inductance_endw": 1e-6,
}


# ============================================================
# DO NOT MODIFY BELOW THIS LINE
# ============================================================

from run import run

def main():
    run(CONFIG)

if __name__ == "__main__":
    main()
