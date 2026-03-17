from validate_inputs import AoutvarConfig
from symbolic_builder import SymbolicBuilder
from mech_offset import compute_mech_offset_from_winding
from write import write_aoutvar

def run(CONFIG):

    print("\n======================================")
    print(" AOUTVAR GENERATOR STARTED")
    print("======================================")

    # 1) Validate configuration
    inputs = AoutvarConfig(CONFIG)

    # 2) Automatically compute the electrical offset of the winding - if chosen
    if inputs.params["mechanical_offset_deg"] == "auto":
        inputs = compute_mech_offset_from_winding(inputs)

    # 2) Build symbolic variables
    builder = SymbolicBuilder(inputs.params)

    # 3) Write output file
    write_aoutvar( builder.variables, inputs.params)

    print("\n[OK] output.aoutvar successfully created.")
    print("======================================\n")

