#!/usr/bin/env python

import grass.script as gscript
import os
# os.chdir()

def main():
    os.chdir('C:/Users/jnlpu/Documents/Studium/Geographie/5. Semester/FOSSGIS/fossgis_ws19_assignment4')
    # import and merge rasters, import vector layers
    gscript.run_command('r.import', overwrite=True, input='corine_landcover_2018/CLC2018_tarragona.tif', output='landcover')
    gscript.run_command('r.import', overwrite=True, input='dem/N40E000.hgt', output='DEM1')
    gscript.run_command('r.import', overwrite=True, input='dem/N41E000.hgt', output='DEM2')
    gscript.run_command('r.import', overwrite=True, input='dem/N41E001.hgt', output='DEM3')
    gscript.run_command('r.patch', overwrite=True, input=['DEM1@FireRiskAnalysis','DEM2@FireRiskAnalysis','DEM3@FireRiskAnalysis'], output='mosaicDEM')
    gscript.run_command('v.import', overwrite=True, input='fire_incidents/fire_archive_V1_89293.shp', output='Wildfire_Incidents')
    gscript.run_command('v.import', overwrite=True, input='osm/buildings.geojson', output='buildings')
    gscript.run_command('v.import', overwrite=True, input='osm/fire_stations.geojson', output='firebrigade')
    # calculate and reclassify slope
    gscript.run_command('r.slope.aspect', overwrite=True, elevation='mosaicDEM@FireRiskAnalysis', slope='slope')
    gscript.run_command('r.reclass', overwrite=True, input='slope@FireRiskAnalysis', output='Slope1', rules='dem/Slope_Rules.txt')
    gscript.run_command('r.resample', overwrite=True, input='Slope1@FireRiskAnalysis', output='SlopeCategorized')
    # reclassify landcover
    gscript.run_command('r.reclass', overwrite=True, input='landcover@FireRiskAnalysis', output='landcover_Cat', rules='corine_landcover_2018/rules.txt')
    gscript.run_command('r.resample', overwrite=True, input='landcover_Cat@FireRiskAnalysis', output='LandcoverCategorized')
    # wildfire probability
    gscript.run_command('v.mkgrid', overwrite=True, map='Grid', box=[1000,1000])
    gscript.run_command('v.vect.stats', overwrite=True, points='Wildfire_Incidents@FireRiskAnalysis', areas='Grid@FireRiskAnalysis', count_column='fire_count')
    gscript.run_command('v.to.rast', overwrite=True, input='Grid@FireRiskAnalysis', type='area', output='Grid_Raster', use='attr', attribute_column='fire_count')
    gscript.run_command('r.mapcalc', overwrite=True, expression='Probability1 = (if (Grid_Raster@FireRiskAnalysis > 15, 15, Grid_Raster@FireRiskAnalysis) * 100 / 15)')
    gscript.run_command('r.null', overwrite=True, map='Probability1@FireRiskAnalysis', null=1)
    gscript.run_command('r.reclass', overwrite=True, input='Probability1@FireRiskAnalysis', output='Probability_Cat', rules='fire_incidents/probability_rules.txt')
    gscript.run_command('r.resample', overwrite=True, input='Probability_Cat@FireRiskAnalysis', output='Probability')
    # exposure
    gscript.run_command('v.mkgrid', overwrite=True, map='Grid2', box=[1000,1000])
    gscript.run_command('v.vect.stats', overwrite=True, points='buildings@FireRiskAnalysis', areas='Grid2@FireRiskAnalysis', type='centroid', count_column='building_count')
    gscript.run_command('v.to.rast', overwrite=True, input='Grid2@FireRiskAnalysis', type='area', output='Grid_Raster2', use='attr', attribute_column='building_count')
    gscript.run_command('r.reclass', overwrite=True, input='Grid_Raster2@FireRiskAnalysis', output='Exposure1', rules='osm/buildings_rules.txt') # I chose a classification loosely based on a exponential function looking at the data
    gscript.run_command('r.resample', overwrite=True, input='Exposure1@FireRiskAnalysis', output='Exposure')
    # proximity
    gscript.run_command('v.to.rast', overwrite=True, input='firebrigade@FireRiskAnalysis', output='firebrigadeRaster', type='centroid', use='attr', attribute_column='cat')
    gscript.run_command('r.mapcalc', overwrite=True, expression='Firebrigades = if (firebrigadeRaster@FireRiskAnalysis > 0, 1, firebrigadeRaster@FireRiskAnalysis)')
    gscript.run_command('r.grow.distance', overwrite=True, input='Firebrigades@FireRiskAnalysis', distance='Proximity1') # Values till ~75000
    gscript.run_command('r.reclass', overwrite=True, input='Proximity1@FireRiskAnalysis', output='Proximity_Cat', rules='osm/firebrigade_rules.txt') # a simply logical categorisation based on the personal opinion on distances and the data
    gscript.run_command('r.resample', overwrite=True, input='Proximity_Cat@FireRiskAnalysis', output='Proximity')
if __name__ == '__main__':
    main()
