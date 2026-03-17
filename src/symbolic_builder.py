"""
SYMBOLIC dq EXPRESSION GENERATOR
============================================================

Generates symbolic dq transformation expressions for
multiphase machines.

The expressions are written in a format compatible with
ANSYS Electronics Desktop (.aoutvar).

Supported features
------------------

• arbitrary number of phases
• harmonic dq subspaces
• dq projection of currents, voltages and flux linkages
• dq inductance matrices
• excitation flux calculation

All generated expressions are stored as strings and later
written to the .aoutvar file.

------------------------------------------------------------
Author: Jan Laksar
------------------------------------------------------------
"""

# ============================================================
# Imports
# ============================================================

# Third-party libraries
import numpy as np

# ============================================================
# Symbolic builder class
# ============================================================
    
class SymbolicBuilder:

    # ------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------

    def __init__(self, inputs):
        self.inputs = inputs
        self.variables = []

        self._build_transform_constants()
        self._build_theta()
        self._build_trigonometry()
        self._build_dq_projection("Flux", "FluxLinkage", "Wb")
        self._build_dq_projection("Vind", "InducedVoltage", "V")
        self._build_voltages()
        if self.inputs["excitation_type"] == "voltage":
            self._build_dq_projection("I", "Current", "A")
            self._build_dq_projection("V", "InputVoltage", "V")
        else:
            self._build_dq_projection("I", "InputCurrent", "A")
            self._build_dq_voltages()
        if self.inputs["include_inductances"]==True:
            self._build_phase_inductance_projection()
            self._build_dq_inductances()
            self._build_excitation_fluxes()
        self._build_electromagnetic_torque()

        print("\n--- Checking configuration ---\n")

    # ------------------------------------------------------------
    # Transformation constants
    # ------------------------------------------------------------

    def _build_transform_constants(self):
        cfg = self.inputs
        self.add("PolePairs",str(cfg["pole_pairs"]))
        self.add("RotSign",str(cfg["rotation_sign"]))
        self.add("MechOffsetDeg",str(cfg["mechanical_offset_deg"]))
        self.add("Rs",str(cfg["resistance_stat"]))
        self.add("Lew",str(cfg["inductance_endw"]))

    # ------------------------------------------------------------
    # Electrical rotor angle
    # ------------------------------------------------------------

    def _build_theta(self):
        motion = self.inputs["motion_setup"]
        expr = f"'RotSign*({motion}.Position - MechOffsetDeg/180*pi) * PolePairs - pi'"
        self.add("theta_el",expr,"deg","Uses20Log")

    # ------------------------------------------------------------
    # Trigonometric basis functions
    # ------------------------------------------------------------

    def _build_trigonometry(self):
        m = self.inputs["num_phases"]
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            for k in range(m):

                name_cos = f"cos{k}_{mu}"
                name_sin = f"sin{k}_{mu}"
                angle = f"{mu}*(theta_el - 2*PI*{k}/{m})"

                self.add(name_cos, f"'cos({angle})'")
                self.add(name_sin, f"'sin(-{angle})'")

    # -------------------------------------------------------------------
    # dq projection of phase currents, flux linkages and induced voltages
    # -------------------------------------------------------------------

    def _build_dq_projection(self, name, ansys_func, unit):
        m = self.inputs["num_phases"]
        phases = self.inputs["phase_names"]
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            terms_d = []
            terms_q = []
            for k, phase in enumerate(phases):
                name_cos = f"cos{k}_{mu}"
                name_sin = f"sin{k}_{mu}"
                terms_d.append(f"{ansys_func}({phase})*{name_cos}")
                terms_q.append(f"{ansys_func}({phase})*{name_sin}")

            expr_d = "'(" + " + ".join(terms_d) + f") * 2/{m}'"
            expr_q = "'(" + " + ".join(terms_q) + f") * 2/{m}'"

            self.add(f"{name}_d{mu}", expr_d, unit, "Uses20Log")
            self.add(f"{name}_q{mu}", expr_q, unit, "Uses20Log")

    # ------------------------------------------------------------
    # Projection of phase inductances
    # ------------------------------------------------------------

    def _build_phase_inductance_projection(self):
        phases = self.inputs["phase_names"]
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            for i, phase_i in enumerate(phases):
                terms_d = []
                terms_q = []
                name_d = f"L{i}d_{mu}"
                name_q = f"L{i}q_{mu}"

                for k, phase_k in enumerate(phases):
                    name_cos = f"cos{k}_{mu}"
                    name_sin = f"sin{k}_{mu}"

                    terms_d.append(f"L({phase_i},{phase_k})*{name_cos}")
                    terms_q.append(f"L({phase_i},{phase_k})*{name_sin}")

                expr_d = f"'"+" + ".join(terms_d) + f"'"
                expr_q = f"'"+" + ".join(terms_q) + f"'"

                self.add(name_d, expr_d, "nH", "Uses20Log")
                self.add(name_q, expr_q, "nH", "Uses20Log")

    # ------------------------------------------------------------
    # dq inductance matrices
    # ------------------------------------------------------------

    def _build_dq_inductances(self):
        m = self.inputs["num_phases"]
        phases = self.inputs["phase_names"]
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            for nu in harmonics:
                terms_dd = []
                terms_dq = []
                terms_qq = []
                terms_qd = []

                if mu==nu:
                    name_dd = f"Ld{mu}"
                    name_qq = f"Lq{mu}"
                else:
                    name_dd = f"Ld{mu}d{nu}"
                    name_qq = f"Lq{mu}q{nu}"
                name_dq = f"Ld{mu}q{nu}"
                name_qd = f"Lq{mu}d{nu}"

                for k in range(len(phases)):

                    coef_d = f"L{k}d_{mu}"
                    coef_q = f"L{k}q_{mu}"

                    name_cos = f"cos{k}_{nu}"
                    name_sin = f"sin{k}_{nu}"

                    # Ldd = dΨdμ / didν
                    terms_dd.append(f"{coef_d}*{name_cos}")
                    # Ldq = dΨdμ / diqν
                    terms_dq.append(f"{coef_d}*{name_sin}")
                    # Lqq = dΨqμ / diqν
                    terms_qq.append(f"{coef_q}*{name_sin}")
                    # Lqd = dΨqμ / didν
                    terms_qd.append(f"{coef_q}*{name_cos}")

                if self.inputs["inductance_mode"] == "full":
                    expr_dd = f"'(" + " + ".join(terms_dd) + f") * 2/{m}'"
                    expr_dq = f"'(" + " + ".join(terms_dq) + f") * 2/{m}'"
                    expr_qd = f"'(" + " + ".join(terms_qd) + f") * 2/{m}'"
                    expr_qq = f"'(" + " + ".join(terms_qq) + f") * 2/{m}'"
                    self.add(name_dd, expr_dd, "nH", "Uses20Log")                
                    self.add(name_dq, expr_dq, "nH", "Uses20Log")
                    self.add(name_qd, expr_qd, "nH", "Uses20Log")
                    self.add(name_qq, expr_qq, "nH", "Uses20Log")
                elif mu==nu:
                    expr_dd = f"'(" + " + ".join(terms_dd) + f") * 2/{m}'"
                    expr_qq = f"'(" + " + ".join(terms_qq) + f") * 2/{m}'"
                    self.add(name_dd, expr_dd, "nH", "Uses20Log")                
                    self.add(name_qq, expr_qq, "nH", "Uses20Log")

    # ------------------------------------------------------------
    # Excitation flux calculation
    # ------------------------------------------------------------
            
    def _build_excitation_fluxes(self):
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            terms_d = []
            terms_q = []

            for nu in harmonics:
                if mu==nu:
                    name_dd = f"Ld{mu}"
                    name_qq = f"Lq{mu}"
                else:
                    name_dd = f"Ld{mu}d{nu}"
                    name_qq = f"Lq{mu}q{nu}"
                name_dq = f"Ld{mu}q{nu}"
                name_qd = f"Lq{mu}d{nu}"

                if self.inputs["inductance_mode"]=="full":
                    terms_d.append(f"{name_dd}*I_d{nu}")
                    terms_d.append(f"{name_dq}*I_q{nu}")
                    terms_q.append(f"{name_qd}*I_d{nu}")
                    terms_q.append(f"{name_qq}*I_q{nu}")
                elif mu==nu:
                    terms_d.append(f"{name_dd}*I_d{nu}")
                    terms_q.append(f"{name_qq}*I_q{nu}")

            expr_d = " + ".join(terms_d)
            expr_q = " + ".join(terms_q)

            self.add(f"Flux_e_d{mu}",f"'Flux_d{mu} - ({expr_d})'", "''", "Uses20Log")
            self.add(f"Flux_e_q{mu}",f"'Flux_q{mu} - ({expr_q})'", "''", "Uses20Log")

    # ------------------------------------------------------------
    # Phase and terminal voltages
    # ------------------------------------------------------------
    
    def _build_voltages(self):
        m = self.inputs["num_phases"]
        phases = self.inputs["phase_names"]
        codes = self.inputs["phase_codes"]
        Dm = _build_phase_from_line_matrix(m)
        
        if m % 2 == 0:
            delta = m // 2
        else:
            delta = (m - 1) // 2

        phase_vars = []
        line_vars = []
        term_vars = []

        for k, phase_a in enumerate(phases):
            phase_b = phases[(k + delta) % m]
            code_a = codes[k]
            code_b = codes[(k + delta) % m]

            var_name_ll = f"V_{code_a}{code_b}"
            if self.inputs["excitation_type"] == "voltage":
                expr_ll = f"'InputVoltage({phase_a}) - InputVoltage({phase_b})'"
            else:
                var_name_ph = f"V_{code_a}"
                var_name_term = f"Vterm_{code_a}"
                expr_ph = f"'InducedVoltage({phase_a}) + Rs*InputCurrent({phase_a}) + Lew*ddt(InputCurrent({phase_a}))'"
                expr_ll = f"'V_{code_a} - V_{code_b}'"
                
                terms = []
                for i in range(m-1):
                    ph_a = codes[i]
                    ph_b = codes[(i + delta) % m]

                    var_ll = f"V_{ph_a}{ph_b}"

                    terms.append(f"{Dm[k,i]}*{var_ll}")

                expr_term = " + ".join(terms)
                expr_term = f"'1/{m}*({expr_term})'"

                phase_vars.append((var_name_ph, expr_ph))
                term_vars.append((var_name_term, expr_term))

            line_vars.append((var_name_ll, expr_ll))

        for name, expr in phase_vars:
            self.add(name, expr, "''", "Uses20Log")
        for name, expr in line_vars:
            self.add(name, expr, "''", "Uses20Log")
        for name, expr in term_vars:
            self.add(name, expr, "''", "Uses20Log")
    
    # ------------------------------------------------------------
    # dq projection of phase voltages for current excitation
    # ------------------------------------------------------------

    def _build_dq_voltages(self):
        m = self.inputs["num_phases"]
        phases = self.inputs["phase_names"]
        codes = self.inputs["phase_codes"]
        harmonics = self.inputs["harmonic_orders"]

        for mu in harmonics:
            terms_d = []
            terms_q = []
            for k, code in enumerate(codes):
                name_cos = f"cos{k}_{mu}"
                name_sin = f"sin{k}_{mu}"
                terms_d.append(f"V_{code}*{name_cos}")
                terms_q.append(f"V_{code}*{name_sin}")

            expr_d = "'(" + " + ".join(terms_d) + f") * 2/{m}'"
            expr_q = "'(" + " + ".join(terms_q) + f") * 2/{m}'"

            self.add(f"V_d{mu}", expr_d, "''", "Uses20Log")
            self.add(f"V_q{mu}", expr_q, "''", "Uses20Log")

    # ------------------------------------------------------------
    # dq projection of electromagnetic torque
    # ------------------------------------------------------------

    def _build_electromagnetic_torque(self):
        m = self.inputs["num_phases"]
        harmonics = self.inputs["harmonic_orders"]

        terms = []

        for mu in harmonics:
            term = f"{mu}*(Flux_d{mu}*I_q{mu} - Flux_q{mu}*I_d{mu})"
            terms.append(term)

        expr = f"'{m}/2*PolePairs*(" + " + ".join(terms) + ")'"

        self.add(f"Torque_dq", expr, "''", "Uses20Log")

    # ------------------------------------------------------------
    # Variable registration helper
    # ------------------------------------------------------------
    
    def add(self, name, expression, unit="''", db_flag="dBTypeDoesntCare"):
        self.variables.append(f"{name} {expression} Double {unit} {db_flag}")
        
# ============================================================
# Phase-to-line voltage transformation matrix
# ============================================================

def _build_phase_from_line_matrix(m):
    if m % 2 == 0:
        k = m//2
    else:
        k = (m-1)//2

    D = np.zeros((m,m))

    for i in range(m):
        D[i,i] = 1
        D[i,(i+k)%m] = -1
    D[-1,:] = 1
    Dinv = np.linalg.inv(D)
    return np.round(Dinv * m).astype(int)