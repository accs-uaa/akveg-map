# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Initialization for Geospatial Processing Module
# Author: Timm Nawrocki
# Last Updated: 2021-02-24
# Usage: Individual functions have varying requirements. All functions that use arcpy must be executed in an ArcGIS Pro Python 3.6 distribution.
# Description: This initialization file imports modules in the package so that the contents are accessible.
# ---------------------------------------------------------------------------

# Import functions from modules
from package_GeospatialProcessing.arcpyGeoprocessing import arcpy_geoprocessing
from package_GeospatialProcessing.calculateClimateMean import calculate_climate_mean
from package_GeospatialProcessing.calculateTopographicProperties import calculate_topographic_properties
from package_GeospatialProcessing.correctNoData import correct_no_data
from package_GeospatialProcessing.createBufferedTiles import create_buffered_tiles
from package_GeospatialProcessing.createCompositeDEM import create_composite_dem
from package_GeospatialProcessing.createGridIndices import create_grid_indices
from package_GeospatialProcessing.convertFireHistory import convert_fire_history
from package_GeospatialProcessing.downloadFromCSV import download_from_csv
from package_GeospatialProcessing.downloadFromDrive import download_from_drive
from package_GeospatialProcessing.extractCategoricalMaps import extract_categorical_maps
from package_GeospatialProcessing.extractToStudyArea import extract_to_study_area
from package_GeospatialProcessing.interpolateRaster import interpolate_raster
from package_GeospatialProcessing.formatClimateGrids import format_climate_grids
from package_GeospatialProcessing.calculateLSTWarmthIndex import calculate_lst_warmth_index
from package_GeospatialProcessing.formatSiteData import format_site_data
from package_GeospatialProcessing.listFromDrive import list_from_drive
from package_GeospatialProcessing.mergeElevationTiles import merge_elevation_tiles
from package_GeospatialProcessing.mergeSpectralTiles import merge_spectral_tiles
from package_GeospatialProcessing.parseSiteData import parse_site_data
from package_GeospatialProcessing.partitionResults import partition_results
from package_GeospatialProcessing.postprocessAbundance import postprocess_abundance
from package_GeospatialProcessing.recentFireHistory import recent_fire_history
from package_GeospatialProcessing.reprojectInteger import reproject_integer
from package_GeospatialProcessing.selectLocation import select_location
