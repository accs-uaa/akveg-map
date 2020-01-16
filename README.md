# Beringian Vegetation Ecological Atlas
Ecological atlas of quantitative vegetation and soils patterns for North American Beringia.

*Author*: Timm Nawrocki, Alaska Center for Conservation Science, University of Alaska Anchorage

*Created On*: 2019-10-22

*Last Updated*: 2020-01-09

*Description*: Scripts for the data aquisition, data manipulation, statistical modeling, results post-processing, and other analyses for the quantitative mapping of vegetation and soils properties in North American Beringia.

## Getting Started

These instructions will enable you to run the Beringian Vegetation Ecological Atlas scripts. The scripts integrate multiple systems: PostGreSQL database, Google Earth Engine, python-based ArcGIS Pro, Python, R, and Google Cloud Compute. The scripts that have dependencies on ArcGIS Pro must be run on windows based machines, all other scripts are platform independent. Reproducing the results will require proper execution of all scripts. Scripts can be modified to apply to other data or study regions. Detailed instructions for each script have been included in this readme file below.

### Prerequisites

1. ArcGIS Pro 2.4.3+
   1. Python 3.6.8+
   2. os
   3. numpy
   4. pandas
   5. psycopg2
2. Access to Google Earth Engine
3. Access to Google Cloud Compute (or create virtual machines by other means or run all scripts locally)
4. Ubuntu 18.04 LTS (if provisioning virtual machines)
5. Anaconda 3.7 Build 2019.10+
   1. Python 3.7.4+
   2. os
   3. numbpy 1.16.5+
   4. pandas 0.25.1+
   5. seaborn 0.9.0+
   6. matplotlib 3.1.1+
   7. scikit-learn 0.21.3+
   8. xgboost 0.90+
   9. GPy 1.9.9+
   10. GPyOpt 1.2.5+
   11. joblib 0.13.2+
   12. googleapiclient
   13. google_auth_oauthlib
   14. google
   15. time
   16. datetime
   17. pickle
6. R 3.6.1+
   1. sp 1.3-2+
   2. raster 3.0-7+
   3. rgdal 1.4-7+
   4. stringr
7. RStudio Server 1.2.5019+

### Installing

1. Install ArcGIS Pro, [Anaconda](https://www.anaconda.com/distribution/), and [R](https://www.r-project.org/) in a local environment according to the documentation provided by the originators.

2. In ArcGIS Pro, select the python management option. Using the conda install option, install the most recent version of psycopg2.
3. Download or clone this repository to a folder on a drive accessible to your machine. Local drives may perform better than network drives. The structure and names of files and folders within the repository should not be altered.
4. In order to query a local version of the Alaska Vegetation Plots Database, set up a [PostGreSQL](https://www.postgresql.org/) server and create a local instance of the database. For more information, see: https://github.com/accs-uaa/vegetation-plots-database.
5. Configure access to Google Earth Engine and an appropriate Google data storage option that can be associated with Google Earth Engine. For more information, see: https://earthengine.google.com/.
6. *Optional*: Configure access to Google Cloud Compute Engine (or another provisioner of cloud computational resources) and set up virtual machines. Instructions for setting up virtual machines are included in the "cloudCompute" folder of this repository. For more information on configuring Google Cloud Compute Engine, see: https://cloud.google.com/compute/.

## Usage

This section describes the purpose of each script and gives instructions for modifying parameters to reproduce results or adapt to another project.

### 1. Data Acquisition

#### 1.1. Calculate Sentinel-2 Spectral Composites

The Earth Engine scripts calculate and export cloud-reduced, maximum-NDVI composites for Sentinel-2 bands 2-8a and 11-12 plus the following derived metrics: enhanced vegetation index 2 (EVI-2), normalized burn ratio (NBR), normalized difference moisture index (NDMI), normalized difference snow index (NDSI), normalized difference vegetation index (NDVI), and normalized difference water index (NDWI). Because the North American Beringia study region includes latitudes greater than 65° N, all composites are calculated from the Top of Atmosphere (TOA) image collections. These scripts can be modified to calculate composites from surface reflectance image collections for study regions that are below 65° N. Composites are calculated individually for the months of May-September from years 2015-2019. See Chander et al. 2009 for a description of the TOA reflectance method. See the Google Earth Engine Sentinel-2 page for more information about the source data: https://developers.google.com/earth-engine/datasets/catalog/sentinel-2.

Scripts are located in (../data_Reflectance/sentinel2):

​	cloudlessSentinel2_05May.js

​	cloudlessSentinel2_06June.js

​	cloudlessSentinel2_07July.js

​	cloudlessSentinel2_08August.js

​	cloudlessSentinel2_09September.js

**Instructions for Google Earth Engine:**

* In the [Google Earth Engine code editor](https://code.earthengine.google.com/), paste the monthly earth engine script into the javascript window. You can optionally modify and save the script in a git repository within Google Earth Engine.

* Run the script. The results can be inspected in the map window (shows a natural color blue-green-red image), in the inspector, and in the console.
* Each image must be exported to a Google Drive folder (or other Google storage option) by clicking the "Run" button. The export requires a large amount of available storage in the Google Drive (over 10 TB) and can take several days to weeks to process.
* Download the imagery from the Google storage to a local directory (see the script "DataDownload_Sentinel2.py").

#### 1.2. Calculate MODIS Mean Land Surface Temperature

The Earth Engine script calculates decadal monthly mean land surface temperature (LST) from MODIS Terra data collected from 2010 to 2019 (the 2010s decade) for the months May-September. All calculations are made from the 8-day, rather than daily, MODIS product. See the Google Earth Engine MODIS LST 8-Day page for more information about the source data: https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD11A2.

Script is located in (../data_Reflectance/modis_lst):

​	modisLST_2010s_May-September.js

**Instructions for Google Earth Engine:**

* In the [Google Earth Engine code editor](https://code.earthengine.google.com/), paste the earth engine script into the javascript window. You can optionally modify and save the script in a git repository within Google Earth Engine.

* Run the script. The results can be inspected in the map window (shows a false color LST image), in the inspector, and in the console.
* Each image must be exported to a Google Drive folder (or other Google storage option) by clicking the "Run" button.
* Download the imagery from the Google storage to a local directory (see the script "DataDownload_lstMODIS.py").

#### 1.3. Download Sentinel-2 Data

Anaconda Python script downloads all files from a google folder. Depending on amount of data to be downloaded and connection speed, this process may take days to weeks to complete. The [Google API client](https://console.developers.google.com/) must be used to create a credentials file called "client_secrets.json" prior to running this script and the file must be in an accessible location specified in the script. For more information on "client_secrets.json", see the Google documentation: https://developers.google.com/api-client-library/dotnet/guide/aaa_client_secrets.

Script is located in (../data_Reflectance)

​	DataDownload_Sentinel2.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.

* *root_folder*: Specify the root folder that contains the data and project working folders.

* *data_folder*: Specify the folder where the data will be downloaded.

* *google_folder*: Specify the reference alpha-numeric id for the google folder containing the data.

* *credentials_folder*: Specify the folder that contains the "client_secrets.json" file (file name must be an exact match).

* *file_id_subset*: Specify the numeric range of files to download (this is intended to allow the task to be split across multiple machines).

#### 1.4. Download MODIS LST Data

Anaconda Python script downloads all files from a google folder. The [Google API client](https://console.developers.google.com/) must be used to create a credentials file called "client_secrets.json" prior to running this script and the file must be in an accessible location specified in the script. For more information on "client_secrets.json", see the Google documentation: https://developers.google.com/api-client-library/dotnet/guide/aaa_client_secrets.

Script is located in (../data_Reflectance)

​	DataDownload_Sentinel2.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.

* *root_folder*: Specify the root folder that contains the data and project working folders.

* *data_folder*: Specify the folder where the data will be downloaded.

* *google_folder*: Specify the reference alpha-numeric id for the google folder containing the data.

* *credentials_folder*: Specify the folder that contains the "client_secrets.json" file (file name must be an exact match).

#### 1.5. Download SNAP 15 km Climate Data for Northwest North America

Anaconda Python script downloads all files specified in a column of a csv file. The csv file must be created manually prior to executing this script. Climate data from the Scenarios Network for Alaska and Arctic Planning (SNAP) is publicly available through an [online data portal](http://data.snap.uaf.edu/data/). This script was originally set via the csv file to download the 15 km resolution data for Northwest North America.

Script is located in (../data_Climate)

​	DataDownload_SNAP_15km_NorthwestNorthAmerica.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.6. Download SNAP 2 km Climate Data for Northwest North America

Anaconda Python script downloads all files specified in a column of a csv file. The csv file must be created manually prior to executing this script. Climate data from the Scenarios Network for Alaska and Arctic Planning (SNAP) is publicly available through an [online data portal](http://data.snap.uaf.edu/data/). This script was originally set via the csv file to download the 2 km resolution data for Northwest North America.

Script is located in (../data_Climate)

​	DataDownload_SNAP_2km_NorthwestNorthAmerica.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.7. Download Arctic DEM 10 m Alaska Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created manually prior to executing this script from the Grid Index shapefile for the Arctic Digital Elevation Model (DEM). The Grid Index shapefile is publicly available through the [Arctic DEM website](https://www.pgc.umn.edu/data/arcticdem/). This script was originally set via the csv file to download the tiles from Alaska.

Script is located in (../data_Topography)

​	DataDownload_ArcticDEM_10m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.8. Download Arctic DEM 10 m Canada Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created manually prior to executing this script from the Grid Index shapefile for the Arctic Digital Elevation Model (DEM). The Grid Index shapefile is publicly available through the [Arctic DEM website](https://www.pgc.umn.edu/data/arcticdem/). This script was originally set via the csv file to download the tiles from Northwest Canada.

Script is located in (../data_Topography)

​	DataDownload_ArcticDEM_10m_Canada.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.9. Download EnvYukon DEM 30 m Yukon Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created manually prior to executing this script. The Yukon 30 m DEM is available from the [Environment Yukon website](https://yukon.ca/en/map-gis-data-environmental#yukon-digital-elevation-model).

Script is located in (../data_Topography)

​	DataDownload_EnvYukon_30m_Yukon.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.10. Download USGS3DEP 5 m Alaska Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created automatically through the USGS National Map Viewer web application prior to executing this script. The 5 m DEM elevation tiles can be filtered through the "Elevation Products (3DEP)" category of the [National Map Viewer](https://viewer.nationalmap.gov/basic/).

Script is located in (../data_Topography)

​	DataDownload_USGSDEM_5m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.11. Download USGS3DEP 10 m Alaska Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created automatically through the USGS National Map Viewer web application prior to executing this script. The 1/3 arc-second (approximately 10 m) DEM elevation tiles can be filtered through the "Elevation Products (3DEP)" category of the [National Map Viewer](https://viewer.nationalmap.gov/basic/).

Script is located in (../data_Topography)

​	DataDownload_USGSDEM_10m_NPRA.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.12. Download USGS3DEP 30 m Canada Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created automatically through the USGS National Map Viewer web application prior to executing this script. The 1 arc-second (approximately 30 m) DEM elevation tiles can be filtered through the "Elevation Products (3DEP)" category of the [National Map Viewer](https://viewer.nationalmap.gov/basic/).

Script is located in (../data_Topography)

​	DataDownload_USGSDEM_30m_Canada.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

#### 1.13. Download USGS3DEP 60 m Alaska Tiles

Anaconda Python script downloads all files specified in a column of a csv file. The csv file should be created automatically through the USGS National Map Viewer web application prior to executing this script. The 2 arc-second (approximately 60 m) DEM elevation tiles can be filtered through the "Elevation Products (3DEP)" category of the [National Map Viewer](https://viewer.nationalmap.gov/basic/).

Script is located in (../data_Topography)

​	DataDownload_USGSDEM_60m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the download directory and the input table.
* *input_table*: Specify the csv table that stores the download links.
* *url_column*: Specify the column name for the column within the input table that contains the download links.
* *directory*: Specify the folder within the data folder where the data will be downloaded.

### 2. Prepare Analytical Grid

#### 2.1. Create Analysis Grids

ArcGIS Pro Python script creates major and minor grid indices and overlapping grid tiles from a manually-generated study area polygon. The resulting datasets are a single feature class of major grids, a single feature class of minor grids, one raster dataset per major grid tile, and one raster dataset per minor grid tile.

Script is located in (../geospatial_AnalyticGrids)

​	GridIndex_AnalysisGrids.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that will contain the raster file outputs. A "gridMajor" and "gridMinor" folder will automatically be created within the "data_folder" to store raster grid tile outputs.
* *project_folder*: Specify the folder that contains the project GIS files.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *total_area*: Specify the manually-generated study area feature class.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *major_grid*: Specify a feature class that will be created to contain the major grid index polygons.
* *minor_grid*: Specify a feature class that will be created to contain the minor grid index polygons.

### 3. Prepare Spectral Properties Per Month

#### 3.1. Process Sentinel-2 Spectral Tiles

ArcGIS Pro Python script reprojects each spectral tile into a specified coordinate system and converts all values to integers based on a specified scaling factor. The script converts the float rasters output by Google Earth Engine to 16-bit signed integer rasters that match the grid alignment of a snap raster.

Script is located in (../data_Reflectance)

​	SpectralComposite_ProcessSpectralTiles.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *unprocessed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.

#### 3.2. Create Sentinel-2 Spectral Composites

ArcGIS Pro Python script merges tile rasters for each major grid tile and imputes missing data by a combination of zonal averaging and nearest neighbors. The outputs for this script are grid raster files that cover the study area and provide model-ready values.

### 4. Prepare Climate Properties



### 5. Prepare Topographic Properties

#### 5.1. Create Composite Arctic DEM 10 m Alaska

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster.  

Script is located in (../data_Topography)

​	ElevationInput_ArcticDEM_10m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" containing the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *arctic10m_composite*: Specify the output raster tif file.

#### 5.2. Create Composite Arctic DEM 10 m Canada

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster. 

Script is located in (../data_Topography)

​	ElevationInput_ArcticDEM_10m_Canada.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" that contains the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *arctic10m_composite*: Specify the output raster tif file.

#### 5.3. Reproject EnvYukon 30 m Yukon DEM

ArcGIS Pro Python script reprojects the EnvYukon 30 m Yukon DEM.

Script is located in (../data_Topography)

​	ElevationInput_ArcticDEM_10m_Canada.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file input and will contain the raster file output.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" containing the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *arctic10m_composite*: Specify the output raster tif file.

#### 5.4. Create Composite USGS 3DEP 5 m Alaska DEM

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster. 

Script is located in (../data_Topography)

​	ElevationInput_USGS3DEP_5m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" that contains the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *usgs5m_composite*: Specify the output raster tif file.

#### 5.5. Create Composite USGS 3DEP 10 m NPR-A DEM

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster. 

Script is located in (../data_Topography)

​	ElevationInput_USGS3DEP_10m_NPRA.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" that contains the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *usgs10m_composite*: Specify the output raster tif file.

#### 5.6. Create Composite USGS 3DEP 30 m Canada DEM

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster. 

Script is located in (../data_Topography)

​	ElevationInput_USGS3DEP_30m_Canada.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" that contains the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *canada30m_composite*: Specify the output raster tif file.

#### 5.7. Create Composite USGS 3DEP 60 m Alaska DEM

ArcGIS Pro Python script reprojects all DEM tiles and merges them into a single raster. 

Script is located in (../data_Topography)

​	ElevationInput_USGS3DEP_60m_Alaska.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *arcpy.env.workspace*: Specify the file geodatabase that will be used as a work space.
* *tile_folder*: Specify the folder within "data_folder" that contains the individual DEM tiles.
* *projected_folder*: Specify the folder within "data_folder" that will contain the projected DEM tiles.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *alaska60m_composite*: Specify the output raster tif file.

#### 5.8. Create Elevation Composite

ArcGIS Pro Python script creates a composite from multiple source DEMs based on an order of priority per major grid tile. The output of this script is a set of elevation grid raster files that cover the study area and provide model ready values.

Script is located in (../data_Topography)

​	TopographicComposite_CreateElevationComposite.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *grid_major*: Specify the folder that contains the major grid raster files.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *source_usgs_5m*: Specify the composite USGS 3DEP 5 m DEM.
* *source_usgs_30m*: Specify the composite USGS 3DEP 30 m DEM.
* *source_usgs_60m*: Specify the composite USGS 3DEP 60 m DEM.
* *source_Alaska_10m*: Specify the composite Arctic DEM 10 m DEM for Alaska.
* *source_Canada_10m*: Specify the composite Arctic DEM 10 m DEM for Canada.
* *source_Yukon_30m*: Specify the reprojected EnvYukon 30 m Yukon DEM.
* *elevation_inputs*: Specify the mosaic order of priority for the input DEMs, with the highest priority DEM listed first and the lowest priority DEM listed last.
* *mosaic_name_root*: Specify the base name of the output elevation grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.

#### 5.9. Calculate Topographic Properties

ArcGIS Pro Python script calculates aspect, compound topographic index, roughness, site exposure, mean slope, surface area, surface relief, topographic position, and topographic radiation per major grid tile from the elevation composite. The output of this script is a set of topographic grid raster files that cover the study area and provide model ready values.

Script is located in (../data_Topography)

​	TopographicComposite_CalculateTopographicProperties.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *grid_major*: Specify the folder that contains the major grid raster files.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *elevation_name_root*: Specify the base name of the elevation grid raster files.
* *aspect_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *compoundTopographic_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *roughness_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *siteExposure_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *slope_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *surfaceArea_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *surfaceRelief_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *topographicPosition_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.
* *topographicRadiation_name_root*: Specify the base name of the output grid raster files. Each elevation grid raster file will be named as the base name appended with the grid identifier.

### 6. Prepare Vegetation Observations



### 7. Prepare Soils Observations



# Packages

This section describes the packages and functions designed for the analysis of Beringian vegetation and soils. The scripts included in this section cannot be run directly. Input and output parameters are for running scripts are described in the "Usage" section above.

### 1. Geomorphometry

The Geomorphometry package includes scripts to calculate topographic properties from a DEM. All scripts in the Geomorphometry package are adapted from the [Geomorphometry and Gradient Metrics Toolbox 2.0](https://github.com/jeffreyevans/GradientMetrics) (Evans et al. 2014) and based on the gradient surface metrics described by Cushman et al. (2010).

#### 1.1. Compound Topographic

This function calculates compound topographic index, a quantification of catenary landscape position that serves as an index of steady state wetness (Gessler et al. 1995).



## Credits

### Authors

* **Timm Nawrocki** - *Alaska Center for Conservation Science, University of Alaska Anchorage*

### Usage Requirements

Usage of the scripts, packages, tools, or routines included in this repository should be cited as follows:

Nawrocki, T.W. 2020. Beringian Vegetation. Git Repository. Available: https://github.com/accs-uaa/beringian-vegetation

### Citations

Cushman, S.A., K. Gutzweiler, J.S. Evans, and K. McGarigal. 2010. The Gradient Paradigm: A conceptual and analytical framework for landscape ecology [Chapter 5]. In: Cushman, S.A., F. Huettmann (eds.). Spatial complexity, informatics, and wildlife conservation. Springer. New York, New York. 83-108.

Evans, J.S., J. Oakleaf, and S.A. Cushman. 2014. An ArcGIS Toolbox for Surface Gradient and Geomorphometric Modeling, version 2.0-0. Available: https://github.com/jeffreyevans/GradientMetrics.

Gessler, P.E., I.D. Moore, N.J. McKenzie, and P.J. Ryan. 1995. Soil-landscape modeling and spatial prediction of soil attributes. International Journal of GIS. 9:421-432.