#!/usr/bin/env python

import grass.script as gscript


def main():
    os.chdir('C:/Users/jnlpu/Documents/Studium/Geographie/5. Semester/FOSSGIS/fossgis_ws19_assignment4')
    # Weighted Overlay Analysis Hazard
    gscript.run_command('r.mapcalc', overwrite=True, expression='Hazard = Probability@FireRiskAnalysis*a + SlopeCategorized@FireRiskAnalysis*b + LandcoverCategorized@FireRiskAnalysis*c')
    # Risk Analysis 
    gscript.run_command('r.mapcalc', overwrite=True, expression='Risk = Hazard@FireRiskAnalysis * Exposure@FireRiskAnalysis * Proximity@FireRiskAnalysis')

if __name__ == '__main__':
    main()
