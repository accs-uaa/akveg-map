# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Get Z Factor
# Author: Timm Nawrocki
# Last Updated: 2019-12-05
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Get Z Factor" is a function that selects an appropriate scaling factor relative to the xy units of the input spatial reference and the z units of the raster value. This function is adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Define function to select Z Factor
def getZFactor(elevation, z_unit):
    """
    Description: creates a DEM from individual DEM tiles
    Inputs: 'elevation' -- an input raster digital elevation model in a projected spatial reference
            'z_unit' -- a string value of either 'Meter' or 'Foot' representing the vertical unit of the elevation raster
    Returned Value: Returns a raster dataset on disk
    Preconditions: requires an input DEM in a projected spatial reference
    """

    # Import packages
    import arcpy

    # Describe the type of spatial reference
    description = arcpy.Describe(elevation)
    spatial_reference = description.spatialReference
    reference_type = spatial_reference.type

    # Warn user and quit script if the elevation raster is in a geographic spatial reference
    if reference_type == "Geographic":
        print('Elevation raster must be in a projected spatial reference, not a geographic spatial reference. Ending script.')
        quit()
    # For projected spatial references, select appropriate Z Factor based on xy and z units
    else:
        reference_unit = spatial_reference.linearUnitName
        if reference_unit != z_unit:
            # If reference unit is meters, then vertical unit is in feet
            if reference_unit == "Meter":
                zFactor = 0.3048
            # If reference unit is not meters, then it is feet and the vertical unit is meters (uncommon)
            else:
                zFactor = 3.28084
        # If the reference unit and z unit are the same then the z factor is 1
        else:
            zFactor = 1.0

    return zFactor
