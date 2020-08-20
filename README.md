# Vegetation Foliar Cover Maps for North American Beringia
Continuous foliar cover maps of vegetation species and aggregates for North American Beringia (arctic and boreal Alaska and Yukon).

*Author*: Timm Nawrocki, Alaska Center for Conservation Science, University of Alaska Anchorage

*Created On*: 2019-10-22

*Last Updated*: 2020-08-19

*Description*: Scripts for data acquisition, data manipulation, statistical modeling, results post-processing, and accuracy assessment for the quantitative mapping of vegetation in North American Beringia.

## Getting Started

These instructions will enable you to run the Beringian Vegetation Ecological Atlas scripts. The scripts integrate multiple systems: Google Earth Engine, Python-based ArcGIS Pro, Python, R, and Google Cloud Compute. The scripts that have dependencies on ArcGIS Pro must be run on windows based machines, all other scripts are platform independent. Reproducing the results will require proper execution of all scripts. Scripts can be modified to apply to other data or study regions. Detailed instructions for each script have been included in this readme file below. Vegetation and soils observation data used for these analyses are stored in and were queried from a public, open-source [vegetation plots database](https://github.com/accs-uaa/vegetation-plots-database).

### Prerequisites

1. ArcGIS Pro 2.5.1+
   1. Python 3.6.9+
   3. numpy 1.16.5+
   4. pandas 0.25.1+
2. Access to Google Earth Engine
3. Access to Google Cloud Compute (or create virtual machines by other means or run all scripts locally)
4. Ubuntu 18.04 LTS (if provisioning virtual machines)
5. Anaconda 3.7 Build 2020.02+
   1. Python 3.7.6+
   3. numpy 1.18.1+
   4. pandas 1.0.1+
   5. seaborn 0.10.0+
   6. matplotlib 3.1.3+
   7. scikit-learn 0.22.1+
   8. lightgbm 2.3.1+
   8. google-api-python-client 1.8.3+
   9. google-auth-oauthlib 0.4.1+
   10. GPy 1.9.9+
   11. GPyOpt 1.2.6+
   12. PyDrive 1.3.1+
6. R 4.0.0+
   1. dplyr 0.8.5+
   2. raster 3.1-5+
   3. rgdal 1.4-8+
   4. sp 1.4-1+
   5. stringr 1.4.0+
   6. tidyr 1.0.2+
7. RStudio Server 1.2.5042+

### Installing

1. Install ArcGIS Pro, [Anaconda](https://www.anaconda.com/distribution/), and [R](https://www.r-project.org/) in a local environment according to the documentation provided by the originators.

3. Download or clone this repository to a folder on a drive accessible to your machine. Local drives may perform better than network drives. The structure and names of files and folders within the repository should not be altered.
4. In order to query a local version of the Alaska Vegetation Plots Database, clone the repository and follow instructions included there to set up and query the database: https://github.com/accs-uaa/vegetation-plots-database.
5. Configure access to Google Earth Engine and an appropriate Google data storage option that can be associated with Google Earth Engine. For more information, see: https://earthengine.google.com/.
6. *Optional*: Configure access to Google Cloud Compute Engine (or another provisioner of cloud computational resources) and set up virtual machines. Instructions for setting up virtual machines are included in the "cloudCompute" folder of this repository. For more information on configuring Google Cloud Compute Engine, see: https://cloud.google.com/compute/.

## Usage

This section describes the purpose of each script and gives instructions for modifying parameters to reproduce results or adapt to another project.

### 1. Data Acquisition

#### 1.1. Calculate Sentinel-1 Synthetic Aperture Radar Composites

The Earth Engine script produces median composites using ascending orbitals for the VV and VH polarizations from Sentinel-1. Composites are calculated from median values across growing season months June, July, and August from 2015 through 2019. See the Google Earth Engine Sentinel-1 SAR GRD page for more information about the source data: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD.

Script is located in (..data_Reflectance/sentinel1):

​	sentinel1_vv_vh.js

#### 1.2. Calculate Sentinel-2 Spectral Composites

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

#### 1.3. Calculate MODIS Mean Land Surface Temperature

The Earth Engine script calculates decadal monthly mean land surface temperature (LST) from MODIS Terra data collected from 2010 to 2019 (the 2010s decade) for the months May-September. All calculations are made from the 8-day, rather than daily, MODIS product. See the Google Earth Engine MODIS LST 8-Day page for more information about the source data: https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD11A2.

Script is located in (../data_Reflectance/modis_lst):

​	modisLST_2010s_May-September.js

**Instructions for Google Earth Engine:**

* In the [Google Earth Engine code editor](https://code.earthengine.google.com/), paste the earth engine script into the Javascript window. You can optionally modify and save the script in a git repository within Google Earth Engine.
* Run the script. The results can be inspected in the map window (shows a false color LST image), in the inspector, and in the console.
* Each image must be exported to a Google Drive folder (or other Google storage option) by clicking the "Run" button.
* Download the imagery from the Google storage to a local directory (see the script "DataDownload_lstMODIS.py").

#### 1.4. Download Sentinel-1 Data

Anaconda Python script downloads all files from a Google folder. The [Google API client](https://console.developers.google.com/) must be used to create a credentials file called "client_secrets.json" prior to running this script and the file must be in an accessible location specified in the script. For more information on "client_secrets.json", see the Google documentation: https://developers.google.com/api-client-library/dotnet/guide/aaa_client_secrets.

Script is located in (../data_Reflectance)

​	DataDownload_Sentinel1.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.

* *root_folder*: Specify the root folder that contains the data and project working folders.

* *data_folder*: Specify the folder where the data will be downloaded.

* *google_folder*: Specify the reference alpha-numeric id for the google folder containing the data.

* *credentials_folder*: Specify the folder that contains the "client_secrets.json" file (file name must be an exact match).

* *file_id_subset*: Specify the numeric range of files to download (this is intended to allow the task to be split across multiple machines).

#### 1.5. Download Sentinel-2 Data

Anaconda Python script downloads all files from a Google folder. Depending on amount of data to be downloaded and connection speed, this process may take days to weeks to complete. The [Google API client](https://console.developers.google.com/) must be used to create a credentials file called "client_secrets.json" prior to running this script and the file must be in an accessible location specified in the script. For more information on "client_secrets.json", see the Google documentation: https://developers.google.com/api-client-library/dotnet/guide/aaa_client_secrets.

Script is located in (../data_Reflectance)

​	DataDownload_Sentinel2.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.

* *root_folder*: Specify the root folder that contains the data and project working folders.

* *data_folder*: Specify the folder where the data will be downloaded.

* *google_folder*: Specify the reference alpha-numeric id for the google folder containing the data.

* *credentials_folder*: Specify the folder that contains the "client_secrets.json" file (file name must be an exact match).

* *file_id_subset*: Specify the numeric range of files to download (this is intended to allow the task to be split across multiple machines).

#### 1.6. Download MODIS LST Data

Anaconda Python script downloads all files from a Google folder. The [Google API client](https://console.developers.google.com/) must be used to create a credentials file called "client_secrets.json" prior to running this script and the file must be in an accessible location specified in the script. For more information on "client_secrets.json", see the Google documentation: https://developers.google.com/api-client-library/dotnet/guide/aaa_client_secrets.

Script is located in (../data_Reflectance)

​	DataDownload_lstMODIS.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.

* *root_folder*: Specify the root folder that contains the data and project working folders.

* *data_folder*: Specify the folder where the data will be downloaded.

* *google_folder*: Specify the reference alpha-numeric id for the google folder containing the data.

* *credentials_folder*: Specify the folder that contains the "client_secrets.json" file (file name must be an exact match).

#### 1.7. Download SNAP 15 km Climate Data for Northwest North America

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

#### 1.8. Download SNAP 2 km Climate Data for Northwest North America

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

#### 1.9. Download Arctic DEM 10 m Alaska Tiles

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

#### 1.10. Download Arctic DEM 10 m Canada Tiles

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

#### 1.11. Download EnvYukon DEM 30 m Yukon Tiles

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

#### 1.12. Download USGS3DEP 5 m Alaska Tiles

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

#### 1.13. Download USGS3DEP 10 m Alaska Tiles

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

#### 1.14. Download USGS3DEP 30 m Canada Tiles

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

#### 1.15. Download USGS3DEP 60 m Alaska Tiles

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

### 3. Prepare Synthetic Aperture Radar Properties

#### 3.1. Process Sentinel-1 Tiles

ArcGIS Pro Python script reprojects each tile into a specified coordinate system and converts all values to integers based on a specified scaling factor. The script converts the float rasters output by Google Earth Engine to 16-bit signed integer rasters that match the grid alignment of a snap raster.

Script is located in (../data_Reflectance)

​	SpectralComposite_ProcessSentinel1Tiles.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *unprocessed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.

#### 3.2. Create Sentinel-1 VV and VH Composites

ArcGIS Pro Python script merges tile rasters for each major grid tile. The outputs for this script are grid raster files that cover the study area and provide model-ready values.

Script is located in (../data_Reflectance)

​	SpectralComposite_CreateSentinel1Composite.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *gridded_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *grid_major*: Specify the folder containing the major grid rasters.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.

### 4. Prepare Spectral Properties Per Month

#### 4.1. Process Sentinel-2 Spectral Tiles

ArcGIS Pro Python script reprojects each spectral tile into a specified coordinate system and converts all values to integers based on a specified scaling factor. The script converts the float rasters output by Google Earth Engine to 16-bit signed integer rasters that match the grid alignment of a snap raster.

Script is located in (../data_Reflectance)

​	SpectralComposite_ProcessSentinel2Tiles.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *unprocessed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.

#### 4.2. Create Null August Area

ArcGIS Pro Python script creates a null area for August spectral tiles where sensors did not record valid data for the month. This script will likely be unnecessary in the future once the Sentinel-2 satellite system has had additional summers to record data. The null August area is used to subsequently remove erroneous data from August Sentinel-2 tiles prior to compositing tiles into grids. No erroneous data values were observed for other months.

Script is located in (../data_Reflectance)

​	SpectralComposite_CreateNullAugustArea.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *mask_folder*: Specify the folder within the "data_folder" that will contain output erroneous data mask raster.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *extent_feature*: Specify the feature class that will set the processing extent for the mask raster.
* *mask_raster*: Specify the mask raster file that will store the mask raster.
* *threshold*: Set the data value threshold that will be used to define the erroneous data. A value of 200 is suggested.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.
* *month*: Define the month-property combination that should be used to set the mask raster.
* *ranges*: Define the processed tiles that should contribute to the mask raster.

#### 4.3. Remove Erroneous August Data

ArcGIS Pro Python script converts erroneous data identified in August spectral tiles to no data.

Script is located in (../data_Reflectance)

​	SpectralComposite_RemoveAugustErroneousData.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *corrected_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *mask_raster*: Specify the mask raster file that stores the mask raster to identify erroneous data.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.
* *month*: Define the month that contains tiles that need to be corrected for erroneous data.
* *ranges_10*: Define the processed 10 m native resolution tiles that need to be corrected for erroneous data.
* *ranges_20*: Define the processed 20 m native resolution tiles that need to be corrected for erroneous data.
* *ranges_evi2*: Define the processed EVI-2 tiles that need to be corrected for erroneous data.
* *properties_10*: Define the properties at the 10 m native resolution that need to be corrected for erroneous data.
* *properties_20*: Define the properties at the 20 m native resolution that need to be corrected for erroneous data.

#### 4.4. Create Sentinel-2 Spectral Composites

ArcGIS Pro Python script merges tile rasters for each major grid tile and imputes missing data by a combination of zonal averaging and nearest neighbors. The outputs for this script are grid raster files that cover the study area and provide model-ready values.

Script is located in (../data_Reflectance)

​	SpectralComposite_CreateSentinel2Composite.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *gridded_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *grid_major*: Specify the folder containing the major grid rasters.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.

### 5. Prepare MODIS LST Summer Warmth Index

#### 5.1. Format MODIS Land Surface Temperature Summer Warmth Index

ArcGIS Pro Python script sums mean annual monthly land surface temperatures from May-September, reprojects the data into a specified projection, and extracts the data to predefined grids. The output represents a summed index of summer warmth based on land surface temperature.

Script is located in (../data_Reflectance)

​	SurfaceTemperature_FormatLST.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *unprocessed_folder*: Specify the folder within the "data_folder" that will contain the raster file inputs.
* *processed_folder*: Specify the folder within the "data_folder" that will contain the intermediate processed raster.
* *gridded_folder*: Specify the folder within the "data_folder" that will contain the raster file outputs.
* *grid_major*: Specify the folder containing the major grid rasters.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *lst_warmthindex*:  Define the lst_warmthindex raster.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.
* *months*: Define the months to sum to form the summer warmth index.
* *property*: Define the name of the MODIS LST summer warmth index property.

### 6. Prepare Climate Properties

#### 6.1. Create Mean Annual Total Precipitation Composite

ArcGIS Pro Python script sums the monthly precipitation for all months for a specified range of years and divides by the number of years to calculate mean annual total precipitation using the SNAP Alaska and Northwest Canada 2 km and 10 minute CRU-TS4.0 historic data products. The 2 km data is given priority where present, while the 10 minute data fills in the included portion of Northwest Territories.

Script is located in (../data_Climate)

​	Precipitation_CreateMeanAnnualComposite.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *data_2km*: Specify the folder that contains the CRU-TS4.0 monthly precipitation raster file inputs at the 2 km resolution.
* *data_15km*: Specify the folder that contains the CRU-TS4.0 monthly precipitation raster file inputs at the 15 km (10 minute) resolution.
* *processed_2km*: Specify the folder within the "data_folder" that will contain the 2 km resolution mean annual total precipitation.
* *processed_15km*: Specify the folder within the "data_folder" that will contain the 15 km resolution mean annual total precipitation.
* *data_10m*: Specify the folder within the "data_folder" that will contain the processed and gridded raster file outputs.
* *gridded_folder*: Specify the folder within the "data_10m" folder that will contain the gridded raster file outputs.
* *grid_major*: Specify the folder containing the major grid rasters.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *precipitation_2km*:  Define the 2 km resolution mean annual total precipitation raster.
* *precipitation_15km*: Define the 15 km resolution mean annual total precipitation raster.
* *precipitation_combined*: Define the combined multi-resolution mean annual total precipitation raster.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.
* *property*_2km: Define the name of the monthly input precipitation property for the 2 km resolution.
* *property_15km*: Define the name of the monthly input precipitation property for the 15 km resolution.
* *years*: Define a list of years in yyyy format as strings that should be included in the mean annual total precipitation calculation.

#### 6.2. Create Mean Annual Summer Warmth Index Composite

ArcGIS Pro Python script sums mean monthly temperatures for May-September across a specified range of years and divides by number of years to calculate mean annual summer warmth index using the SNAP Alaska and Northwest Canada 2 km and 10 minute CRU-TS4.0 historic data products. The 2 km data is given priority where present, while the 10 minute data fills in the included portion of Northwest Territories.

Script is located in (../data_Climate)

​	SummerWarmth_CreateMeanAnnualComposite.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data and project working folders.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *data_2km*: Specify the folder that contains the CRU-TS4.0 monthly mean temperature raster file inputs at the 2 km resolution.
* *data_15km*: Specify the folder that contains the CRU-TS4.0 monthly mean temperature raster file inputs at the 15 km (10 minute) resolution.
* *processed_2km*: Specify the folder within the "data_folder" that will contain the 2 km resolution mean annual summer warmth index.
* *processed_15km*: Specify the folder within the "data_folder" that will contain the 15 km resolution mean annual summer warmth index.
* *data_10m*: Specify the folder within the "data_folder" that will contain the processed and gridded raster file outputs.
* *gridded_folder*: Specify the folder within the "data_10m" folder that will contain the gridded raster file outputs.
* *grid_major*: Specify the folder containing the major grid rasters.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.
* *precipitation_2km*:  Define the 2 km resolution mean annual summer warmth index raster.
* *precipitation_15km*: Define the 15 km resolution mean annual summer warmth index raster.
* *precipitation_combined*: Define the combined multi-resolution mean annual summer warmth index raster.
* *geodatabase*: Specify the file geodatabase that will be used as a work space.
* *property*_2km: Define the name of the monthly input mean temperature property for the 2 km resolution.
* *property_15km*: Define the name of the monthly input mean temperature property for the 15 km resolution.
* *years*: Define a list of years in yyyy format as strings that should be included in the mean annual summer warmth index calculation.

### 7. Prepare Topographic Properties

#### 7.1. Create Composite Arctic DEM 10 m Alaska

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

#### 7.2. Create Composite Arctic DEM 10 m Canada

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

#### 7.3. Reproject EnvYukon 30 m Yukon DEM

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

#### 7.4. Create Composite USGS 3DEP 5 m Alaska DEM

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

#### 7.5. Create Composite USGS 3DEP 10 m NPR-A DEM

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

#### 7.6. Create Composite USGS 3DEP 30 m Canada DEM

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

#### 7.7. Create Composite USGS 3DEP 60 m Alaska DEM

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

#### 7.8. Create Elevation Composite

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

#### 7.9. Calculate Topographic Properties

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

### 8. Prepare Data for Prediction

#### 8.1. Extract Predictor Data to Study Area

In cases where the area of interest and study area are different, the predictor rasters developed using the above scripts must be formatted to match the extent of the study area. The study area should be a raster with the same grid and cell size as the area of interest but with an extent that matches the area of input observations and output predictions. This ArcGIS Pro Python script extracts a set of predictor datasets for specified grids to a study area to enforce the same extent on all rasters.

Script is located in (../geospatial_AnalyticGrids)

​	DataCorrection_ExtractToStudyArea.py

**Parameters that must be modified:**

* *drive*: Specify the drive letter where the data will be downloaded.
* *root_folder*: Specify the root folder that contains the data folders and working geodatabase.
* *data_folder*: Specify the folder that contains the raster file inputs and will contain the raster file outputs.
* *input_topography*: Specify the folder within "data_folder" that contains the input gridded topographic predictor rasters.
* *input_climate*: Specify the folder within the "data_folder" that contains the input gridded climate predictor rasters.
* *input_modis*: Specify the folder within the "data_folder" that contains the input gridded MODIS LST Summer Warmth Index predictor rasters.
* *input_sentinel1*: Specify the folder within the "data_folder" that contains the input gridded Sentinel-1 SAR predictor rasters.
* *input_sentinel2*: Specify the folder within the "data_folder" that contains the input gridded Sentinel-2 multispectral predictor rasters.
* *work_geodatabase*: Specify the file geodatabase that will be used as a work space.
* *grid_list*: Identify target grids that overlap the study area.
* *study_area*: Specify the manually-generated study area raster that will provide the extent (grid alignment and cell size must match the area of interest).
* *grid_major*: Specify the folder that contains the major grid raster files.
* *snap_raster*: Specify the manually-generated area of interest raster that will provide the grid alignment and cell size.

#### 8.2. Extract Predictor Data to Grids

R script extracts data from predictor rasters to regular point grids based on minor grid rasters. The script outputs csv files containing predictor data that can be processed in the prediction phase of a statistical learning model.

Script is located in (../geospatial_AnalyticGrids)

### 8. Prepare Vegetation Observations



### 9. Prepare Soils Observations



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