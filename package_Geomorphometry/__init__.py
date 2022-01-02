# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Initialization for Geomorphometry Module
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Individual functions have varying requirements. All functions that use arcpy must be executed in an ArcGIS Pro Python 3.6 distribution.
# Description: This initialization file imports modules in the package so that the contents are accessible. The functions in this package are adapted from Geomorphometry and Gradient Metrics Toolbox 2.0 by Jeff Evans and Jim Oakleaf (2014) available at https://github.com/jeffreyevans/GradientMetrics
# ---------------------------------------------------------------------------

# Import functions from modules
from package_Geomorphometry.calculateAspect import calculate_aspect
from package_Geomorphometry.calculateExposure import calculate_exposure
from package_Geomorphometry.calculateFlow import calculate_flow
from package_Geomorphometry.calculateHeatLoad import calculate_heat_load
from package_Geomorphometry.calculateIntegerElevation import calculate_integer_elevation
from package_Geomorphometry.calculatePosition import calculate_position
from package_Geomorphometry.calculateRadiation import calculate_radiation
from package_Geomorphometry.calculateRoughness import calculate_roughness
from package_Geomorphometry.calculateSlope import calculate_slope
from package_Geomorphometry.calculateSurfaceArea import calculate_surface_area
from package_Geomorphometry.calculateSurfaceRelief import calculate_surface_relief
from package_Geomorphometry.calculateWetness import calculate_wetness
from package_Geomorphometry.getZFactor import get_z_factor
