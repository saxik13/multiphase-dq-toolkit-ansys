oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()

oModule = oDesign.GetModule("OutputVariable")

vars = oModule.GetOutputVariables()

for v in vars:
    oModule.DeleteOutputVariable(v)

print("All output variables deleted.")