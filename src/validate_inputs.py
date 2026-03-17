"""
CONFIGURATION VALIDATION MODULE
============================================================

Responsible for:

• validating user configuration parameters
• filling missing parameters with default values
• normalizing input formats
• preparing derived parameters used by the generator

This module performs NO symbolic generation.

Output:
    validated configuration stored in `self.params`

------------------------------------------------------------
Author: Jan Laksar
------------------------------------------------------------
"""

# ============================================================
# Configuration object
# ============================================================

class AoutvarConfig:

    # ============================================================
    # Default parameter values
    # ============================================================

    DEFAULTS = {
        # Machine
        "pole_pairs": 2,
        "num_phases": 3,
        # Mechanical    
        "motion_setup": "Moving1",
        "rotation_sign": 1,
        "mechanical_offset_deg": 0.0,
        "slot_number": 0,
        "layers": 0,
        "coil_pitch": 0,
        # Excitation
        "excitation_type": "current",
        # Phase system   
        "phase_base_name": "Phase",
        "phase_index_style": "upper",
        "custom_phase_names": None,

        # Harmonics
        "harmonic_orders": [1],

        # Inductances
        "include_inductances": True,
        "inductance_mode": "full",

        # Winding parameters
    }

    # ============================================================
    # Validation rules
    # ============================================================

    VALIDATION_RULES = {
        "pole_pairs": {
            "condition": lambda v: isinstance(v, int) and v > 0,
        },
        "num_phases": {
            "condition": lambda v: isinstance(v, int) and v >= 2,
        },
        "motion_setup": {
            "condition": lambda v: True,   # only existence check
        },
        "rotation_sign": {
            "condition": lambda v: v in (-1, 1),
        },
        "mechanical_offset_deg": {
            "condition": lambda v: isinstance(v, (int, float)) or v == "auto",
        },
        "slot_number": {
            "condition": lambda v: isinstance(v, (int)),
        },
        "layers": {
            "condition": lambda v: isinstance(v, (int)),
        },
        "coil_pitch": {
            "condition": lambda v: isinstance(v, (int)),
        },
        "excitation_type": {
            "condition": lambda v: v in ("current", "voltage"),
            "transform": str.lower,
        },
        "phase_base_name": {
            "condition": lambda v: True,   # only existence check
        },
        "phase_index_style": {
            "condition": lambda v: v in ("upper", "lower", "number"),
            "transform": str.lower,
        },
        "custom_phase_names": {
            "condition": lambda v: True,   # only existence check
        },
        "harmonic_orders": {
            "transform": lambda v: [v] if isinstance(v, int) else v,
            "condition": lambda v: isinstance(v, list)
                          and len(v) > 0
                          and all(isinstance(h, int) and h > 0 for h in v)
        },
        "include_inductances": {
            "condition": lambda v: True,   # only existence check
        },
        "inductance_mode": {
            "condition": lambda v: v in ("full", "main"),
            "transform": str.lower,
        },
        "resistance_stat": {
            "condition": lambda v: isinstance(v, (int, float)),
        },
        "inductance_endw": {
            "condition": lambda v: isinstance(v, (int, float)),
        },
    }

    # ============================================================
    # Initialization
    # ============================================================

    def __init__(self, user_config: dict):

        if not isinstance(user_config, dict):
            raise TypeError("Configuration must be a dictionary.")

        self._raw = user_config
        self.params = {}

        print("\n--- Checking configuration ---\n")

        self._validate()

        if self.params["mechanical_offset_deg"] == "auto":
            self._validate_winding()

    # ============================================================
    # Parameter validation
    # ============================================================

    def _validate(self):
        """
        Iterate over all validation rules and validate parameters.
        Missing parameters are automatically filled with default values.
        """
        for key, rule in self.VALIDATION_RULES.items():

            condition = rule["condition"]
            transform = rule.get("transform")

            self._validate_general(key, condition, transform)

        # Print final configuration
        self._print_final_config()
        self._build_phase_names()
            
    def _validate_general(self, key, condition, transform=None):
        """
        General validation function.
        Steps:
        1. Get parameter value or use default if the parameter is missing
        2. Apply optional transformation (e.g. string normalization)
        3. Check validity condition
        4. If invalid → replace with default value
        """

        # Check if the parameter exists
        if key not in self._raw:
            value = self.DEFAULTS[key]
            print(
                f"[INFO] Parameter '{key}' not provided.\n"
                f" Using default value: {value}\n"
            )
        else:
            value=self._raw[key]
        
        # Apply transformation if defined
        if transform is not None:
            try:
                value = transform(value)
            except Exception:
                return self._use_default(key, value)

        # Validate the value    
        if not condition(value):
            return self._use_default(key, value)
        
        # Store validated value
        self.params[key] = value
        return value
    
    def _use_default(self, key, value):
        """
        Replace invalid parameter value with default.
        """
        default = self.DEFAULTS[key]
        print(
            f"[INFO] Invalid {key}: {value}\n"
            f" using default value: {default}\n"
        )
        self.params[key] = default
        return default
    
    # ============================================================
    # Phase naming system
    # ============================================================

    def _build_phase_names(self):
        m = self.params["num_phases"]
        base = self.params["phase_base_name"]
        style = self.params["phase_index_style"]
        custom = self.params["custom_phase_names"]

        if custom:
            self.params["phase_names"] = custom
            self.params["phase_codes"] = custom
            return

        names = []
        codes = []
        for k in range(m):
            if style == "upper":
                idx = chr(ord('A') + k)

            elif style == "lower":
                idx = chr(ord('a') + k)

            elif style == "number":
                idx = str(k + 1)

            else:
                raise ValueError("Invalid phase_index_style")

            names.append(f"{base}{idx}")
            codes.append(idx)

        self.params["phase_names"] = names
        self.params["phase_codes"] = codes

    # ============================================================
    # Winding validation for automatic mechanical offset
    # ============================================================

    def _validate_winding(self):
        Q = self.params["slot_number"]
        u2 = self.params["layers"]
        ys = self.params["coil_pitch"]

        if Q <= 0 or u2 <= 0 or ys <= 0:
            print("[INFO] Slot_number, layers and step_winding must be positive integers.\n"
                  "Automatic calculation of mechanical offset is disabled due to invalid winding parameters. Using 0 deg.")
            self.params["mechanical_offset_deg"] = 0.0
            return
            
        if u2 == 1 and ys % 2 == 0:
            print("[INFO] For single-layer winding the step_winding must be odd.\n"
                  "Automatic calculation of mechanical offset is disabled due to invalid winding parameters. Using 0 deg.")
            self.params["mechanical_offset_deg"] = 0.0

    # ============================================================
    # Configuration summary
    # ============================================================

    def _print_final_config(self):
        """
        Print final validated configuration used by the program.
        """
        print("\n========== Simulation configuration ==========")
        print("\n[INFO] Final configuration used:\n")
        for key in (self.params):
            print(f"  {key}: {self.params[key]}")
        print("==============================================\n")