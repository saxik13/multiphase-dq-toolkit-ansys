def write_aoutvar(variables, inputs, output_dir="."):
    """
    Writes variables to an .aoutvar file.

    Parameters
    ----------
    variables : list[str]
        Lines prepared by builder (builder.variables)
    inputs : dict
        User inputs containing phases, source and harmonic_orders
    output_dir : str
        Directory where the file will be written
    """

    m = inputs["num_phases"]
    p = inputs["pole_pairs"]
    RotSign = inputs["rotation_sign"]
    IndMatrix = inputs["inductance_mode"]
    if RotSign == -1:
        rot = "CCW"
    else:
        rot = "CW"

    if inputs["excitation_type"] == "voltage":
        source = "V"
    else:
        source = "I"

    harmonics = sorted(inputs["harmonic_orders"])

    harmonics_str = "".join(str(h) for h in harmonics)

    filename = f"dq_{m}ph_{p}pp_{source}source_h{harmonics_str}_Lmatrix_{IndMatrix}_{rot}.aoutvar"
    filepath = f"{output_dir}/{filename}"

    with open(filepath, "w", encoding="utf-8") as f:
        for line in variables:
            f.write(line + "\n")

    return filepath