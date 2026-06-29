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
        rot = "CW"
    else:
        rot = "CCW"

    if inputs["excitation_type"] == "voltage":
        source = "V"
    else:
        source = "I"

    harmonics = sorted(inputs["harmonic_orders"])

    harmonics_str = "".join(str(h) for h in harmonics)

    filename = f"dq_{m}ph_{p}pp_{source}source_h{harmonics_str}_Lmatrix_{IndMatrix}_{rot}.aoutvar"
    filepath = f"{output_dir}/{filename}"

    # exports the dictionary to a Python file
    filename="output_vars.py"
    output_vars = {
        name: var["expression"]
        for name, var in variables.items()
    }
    with open(filename, "w") as f:
        f.write("output_vars = {\n")
        for k, v in output_vars.items():
            f.write(f"    '{k}': \"{v}\",\n")
        f.write("}\n")

    # create strings for export from dictionary variables to create .aoutvar file
    lines = []
    for name, var in variables.items():
        expr = var["expression"]
        
        if not var["is_constant"]:
            expr = f"'{expr}'"
        else:
            expr = str(expr)
        
        unit = var["unit"]
        db_flag = var["db_flag"]

        line = f"{name} {expr} Double {unit} {db_flag}"
        lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return filepath