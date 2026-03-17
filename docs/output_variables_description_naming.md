
# Output Variables Description and Naming Convention

The name of the exported .aoutvar file and the names of the variables follow standardized conventions described in this file.

## Output File Name

The name of the output file is compound from following parts:

*dq_{number_of_phases}ph_{number_of_polepairs}pp_{Source_type}source_h{list_of_harmonics}_Lmatrix_{Inductance_mode}_{rotation}.aoutvar*

where:
- Source type: I: current, V: voltage
- Inductance mode: main: only the main (self) inductances, full: all inductances including the cross coupling
- rotation: CCW: positive (counter-clockwise), CW: negative (clockwise)

## Supporting Phase Variables
All supporting variables referring to the individual phases are named consistently, independent of the specific phase names. They are numbered, starting from 0. Additionally, the harmonic component is added as the last number of the variable.
Examples:
cos0_1: cosinus function for the 1st winding, 1st harmonic
sin4_3: sinus function for the 5th winding, 3rd harmonic
L1d_1: *d*-axis inductance of the 2nd winding, 1st harmonic
L2q_3: *q*-axis inductance of the 3rd winding, 3rd harmonic

## Rotating *d*-*q* Variables (flux linkages, voltages, currents)
Standard naming contains name, axis, and harmonic component, as:
I_d1: *d*-axis, 1st harmonic current
Flux_d3: *d*-axis, 3rd harmonic flux linkage
Flux_e_q1: *q*-axis, 1st harmonic excitation flux linkage (see `docs/Theoretical Background.pdf`)
V_q3:  *q*-axis, 3rd harmonic voltage

## Line-Line Voltages, Phase Voltages, and Terminal Voltages
The line-line voltages are named according to the relative phase names in the model. The maximum possible voltages are used (i.e., the opposite voltages in multiphase systems). The line-line voltages are:

*V_{front_phase_name}{back_phase_name}*

### Current Source

In the case of the Current source, the phase voltages are not known, and they are calculated from the total induced voltage and from the voltage drops on the phase resistance *Rs* and endwinding inductance *Lew*. These voltages are named as:

*V_{phase_name}*

This voltage includes the non-rotating components, so it is actually the inverter's phase voltage (leg voltage). The terminal phase voltage is calculated from the line-line voltages, and it is named as:

*Vterm_{phase_name}*

For more information, see section *Voltage Source* in `docs/Theoretical Background.pdf`.
