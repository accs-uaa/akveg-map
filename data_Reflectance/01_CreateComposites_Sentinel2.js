/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Cloud-reduced Seasonal Median Composites of Sentinel 2 Imagery circa 2017-2021
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2021-10-21
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a set of cloud-reduced median composite for bands 1-12 plus Enhanced Vegetation Index-2 (EVI2), Normalized Burn Ratio (NBR), Normalized Difference Moisture Index (NDMI), Normalized Difference Snow Index (NDSI), Normalized Difference Vegetation Index (NDVI), Normalized Difference Water Index (NDWI) using the Sentinel-2 Surface Reflectance and Top-Of-Atmosphere image collections. Composites are centered around June 10, July 30, August 20, and September 15.
---------------------------------------------------------------------------*/

// 1. DEFINE PROPERTIES

// Define an area of interest geometry.
var aoi = /* color: #0b4a8b */ee.Geometry.Polygon(
        [[[-136.94652621058978, 69.33001796032033],
          [-143.09886996058978, 70.3298935335601],
          [-150.08617464808978, 70.71089859691716],
          [-157.07347933558978, 71.5354051106333],
          [-162.52269808558978, 70.4478895856191],
          [-166.91722933558978, 69.01754200819833],
          [-169.0043419330834, 65.6362155284739],
          [-166.6752403705834, 61.15983078429893],
          [-164.2582481830834, 59.28345395931592],
          [-159.6439903705834, 57.03553383925198],
          [-165.8842247455834, 54.921653862539145],
          [-164.6537559955834, 54.05378214039293],
          [-157.4467247455834, 55.91923469817123],
          [-152.70532503025723, 58.916395794530516],
          [-135.0470549436822, 60.0251848338009],
          [-134.58877239675192, 65.97383322118833],
          [-135.1531950041738, 69.83531851993344]]]);

// Define properties
var start_year = 2015
var end_year = 2021
var start_month = 5
var end_month = 10
var cloud_threshold = 40

// 2. DEFINE FUNCTIONS

// Define a function to mask image edges
function mask_edges(image) {
  var mask = image.select('B8A').mask().updateMask(image.select('B9').mask());
  return image.updateMask(mask);
}

// Define a function to mask clouds using cloud probability
function mask_cloud_probability(image) {
  var clouds = ee.Image(image.get('cloud_mask')).select('probability');
  var mask = clouds.lt(cloud_threshold);
  return image.updateMask(mask);
}

// Define a function to mask clouds and cirrus using QA band
function mask_cloud_cirrus(image) {
	var qa = image.select('QA60');
	// Bits 10 and 11 are clouds and cirrus, respectively.
	var cloud_bit_mask = 1 << 10;
	var cirrus_bit_mask = 1 << 11;
	//Both flags should be set to zero, indicating clear conditions.
	var mask = qa.bitwiseAnd(cloud_bit_mask).eq(0)
		.and(qa.bitwiseAnd(cirrus_bit_mask).eq(0));
	return image.updateMask(mask);
}

// Define a function for EVI-2 calculation.
function add_EVI2(image) {
  // Assign variables to the red and green Sentinel-2 bands.
  var red = image.select('B4');
  var green = image.select('B3');
  //Compute the Enhanced Vegetation Index-2 (EVI2).
  var evi2_calc = red.subtract(green)
    .divide(red.add(green.multiply(2.4)).add(1))
    .rename('EVI2');
  // Return the masked image with an EVI-2 band.
  return image.addBands(evi2_calc);
}

// Define a function for NBR calculation.
function add_NBR(image) {
  //Compute the Normalized Burn Ratio (NBR).
  var nbr_calc = image.normalizedDifference(['B8', 'B12'])
    .rename('NBR');
  // Return the masked image with an NBR band.
  return image.addBands(nbr_calc);
}

// Define a function for NDMI calculation.
function add_NDMI(image) {
  //Compute the Normalized Difference Moisture Index (NDMI).
  var ndmi_calc = image.normalizedDifference(['B8', 'B11'])
    .rename('NDMI');
  // Return the masked image with an NDMI band.
  return image.addBands(ndmi_calc);
}

// Define a function for NDSI calculation.
function add_NDSI(image) {
  //Compute the Normalized Difference Snow Index (NDSI).
  var ndsi_calc = image.normalizedDifference(['B3', 'B11'])
    .rename('NDSI');
  // Return the masked image with an NDSI band.
  return image.addBands(ndsi_calc);
}

// Define a function for NDVI calculation.
function add_NDVI(image) {
  //Compute the Normalized Difference Vegetation Index (NDVI).
  var ndvi_calc = image.normalizedDifference(['B8', 'B4'])
    .rename('NDVI');
  // Return the masked image with an NDVI band.
  return image.addBands(ndvi_calc);
}

// Define a function for NDWI calculation.
function add_NDWI(image) {
  //Compute the Normalized Difference Water Index (NDWI).
  var ndwi_calc = image.normalizedDifference(['B3', 'B8'])
    .rename('NDWI');
  // Return the masked image with an NDWI band.
  return image.addBands(ndwi_calc);
}

// 3. CREATE CLOUD-REDUCED IMAGE COLLECTION

// Define select spectral bands.
var bands = ['B2',
            'B3',
            'B4',
            'B5',
            'B6',
            'B7',
            'B8',
            'B8A',
            'B11',
            'B12',
            'EVI2',
            'NBR',
            'NDMI',
            'NDSI',
            'NDVI',
            'NDWI']

// Import Sentinel 2 Cloud Probability
var s2_cloud = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
  .filterBounds(aoi)
  .filter(ee.Filter.calendarRange(start_year, end_year, 'year'))
  .filter(ee.Filter.calendarRange(start_month, end_month, 'month'));

// Import Sentinel-2 Level 2A Data
var s2 = ee.ImageCollection('COPERNICUS/S2')
  .filterBounds(aoi)
  .filter(ee.Filter.calendarRange(start_year, end_year, 'year'))
  .filter(ee.Filter.calendarRange(start_month, end_month, 'month'))
  .map(mask_edges);
var s2_sr = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterBounds(aoi)
  .filter(ee.Filter.calendarRange(start_year, end_year, 'year'))
  .filter(ee.Filter.calendarRange(start_month, end_month, 'month'))
  .map(mask_edges);

// Join imagery and cloud probability datasets
var s2_join = ee.Join.saveFirst('cloud_mask').apply({
  primary: s2,
  secondary: s2_cloud,
  condition:
      ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
});
var s2sr_join = ee.Join.saveFirst('cloud_mask').apply({
  primary: s2_sr,
  secondary: s2_cloud,
  condition:
      ee.Filter.equals({leftField: 'system:index', rightField: 'system:index'})
});

// Mask the Sentinel-2 imagery
var s2_masked = ee.ImageCollection(s2_join)
  .map(mask_cloud_probability)
  .map(mask_cloud_cirrus)
  .map(add_EVI2)
  .map(add_NBR)
  .map(add_NDMI)
  .map(add_NDSI)
  .map(add_NDVI)
  .map(add_NDWI)
  .select(bands);
var s2sr_masked = ee.ImageCollection(s2sr_join)
  .map(mask_cloud_probability)
  .map(mask_cloud_cirrus)
  .map(add_EVI2)
  .map(add_NBR)
  .map(add_NDMI)
  .map(add_NDSI)
  .map(add_NDVI)
  .map(add_NDWI)
  .select(bands);

// 4. CREATE MEDIAN COMPOSITES

// Filter image collection targeted around June 10.
var filter_june = ee.Filter.or(
  ee.Filter.date('2015-05-20', '2015-06-30'),
  ee.Filter.date('2016-05-20', '2016-06-30'),
  ee.Filter.date('2017-05-20', '2017-06-30'),
  ee.Filter.date('2018-05-20', '2018-06-30'),
  ee.Filter.date('2019-05-20', '2019-06-30'),
  ee.Filter.date('2020-05-20', '2020-06-30'),
  ee.Filter.date('2021-05-20', '2021-06-30'));
var collection_june = s2sr_masked.filter(filter_june);

// Filter image collection targeted around July 30.
var filter_july = ee.Filter.or(
  ee.Filter.date('2015-06-20', '2015-08-20'),
  ee.Filter.date('2016-06-20', '2016-08-20'),
  ee.Filter.date('2017-06-20', '2017-08-20'),
  ee.Filter.date('2018-06-20', '2018-08-20'),
  ee.Filter.date('2019-06-20', '2019-08-20'),
  ee.Filter.date('2020-06-20', '2020-08-20'),
  ee.Filter.date('2021-06-20', '2021-08-20'));
var collection_july = s2sr_masked.filter(filter_july);

// Filter image collection targeted around August 20.
var filter_august = ee.Filter.or(
  ee.Filter.date('2015-07-15', '2015-09-25'),
  ee.Filter.date('2016-07-15', '2016-09-25'),
  ee.Filter.date('2017-07-15', '2017-09-25'),
  ee.Filter.date('2018-07-15', '2018-09-25'),
  ee.Filter.date('2019-07-15', '2019-09-25'),
  ee.Filter.date('2020-07-15', '2020-09-25'),
  ee.Filter.date('2021-07-15', '2021-09-25'));
var collection_august = s2sr_masked.filter(filter_august);

//Filter image collection targeted around September 15.
var filter_september = ee.Filter.or(
  ee.Filter.date('2015-08-20', '2015-10-10'),
  ee.Filter.date('2016-08-20', '2016-10-10'),
  ee.Filter.date('2017-08-20', '2017-10-10'),
  ee.Filter.date('2018-08-20', '2018-10-10'),
  ee.Filter.date('2019-08-20', '2019-10-10'),
  ee.Filter.date('2020-08-20', '2020-10-10'),
  ee.Filter.date('2021-08-20', '2021-10-10'));
var collection_september = s2_masked.filter(filter_september);

// Make median composites from the image collections.
var median_june = collection_june.median();
var median_july = collection_july.median();
var median_august = collection_august.median();
var median_september = collection_september.median();

// Define visualizations.
var rgbVis = {
  min: 0,
  max: 3000,
  bands: ['B4', 'B3', 'B2']
};
var firVis = {
  min:0,
  max: [3500, 6000, 2000],
  bands: ['B11','B8','B4']
};

// Add image to the map.
Map.addLayer(median_june, firVis, 'June 10 SR Median Composite');
Map.addLayer(median_july, firVis, 'July 30 SR Median Composite');
Map.addLayer(median_august, firVis, 'August 20 SR Median Composite');
Map.addLayer(median_september, firVis, 'September 15 TOA Median Composite')

// 5. EXPORT DATA

// Create single band images for June median.
var june_2_blue = ee.Image(median_june).select(['B2']);
var june_3_green = ee.Image(median_june).select(['B3']);
var june_4_red = ee.Image(median_june).select(['B4']);
var june_5_redEdge1 = ee.Image(median_june).select(['B5']);
var june_6_redEdge2 = ee.Image(median_june).select(['B6']);
var june_7_redEdge3 = ee.Image(median_june).select(['B7']);
var june_8_nearInfrared = ee.Image(median_june).select(['B8']);
var june_8a_redEdge4 = ee.Image(median_june).select(['B8A']);
var june_11_shortInfrared1 = ee.Image(median_june).select(['B11']);
var june_12_shortInfrared2 = ee.Image(median_june).select(['B12']);
var june_evi2 = ee.Image(median_june).select(['EVI2']);
var june_nbr = ee.Image(median_june).select(['NBR']);
var june_ndmi = ee.Image(median_june).select(['NDMI']);
var june_ndsi = ee.Image(median_june).select(['NDSI']);
var june_ndvi = ee.Image(median_june).select(['NDVI']);
var june_ndwi = ee.Image(median_june).select(['NDWI']);

// Create single band images for July median.
var july_2_blue = ee.Image(median_july).select(['B2']);
var july_3_green = ee.Image(median_july).select(['B3']);
var july_4_red = ee.Image(median_july).select(['B4']);
var july_5_redEdge1 = ee.Image(median_july).select(['B5']);
var july_6_redEdge2 = ee.Image(median_july).select(['B6']);
var july_7_redEdge3 = ee.Image(median_july).select(['B7']);
var july_8_nearInfrared = ee.Image(median_july).select(['B8']);
var july_8a_redEdge4 = ee.Image(median_july).select(['B8A']);
var july_11_shortInfrared1 = ee.Image(median_july).select(['B11']);
var july_12_shortInfrared2 = ee.Image(median_july).select(['B12']);
var july_evi2 = ee.Image(median_july).select(['EVI2']);
var july_nbr = ee.Image(median_july).select(['NBR']);
var july_ndmi = ee.Image(median_july).select(['NDMI']);
var july_ndsi = ee.Image(median_july).select(['NDSI']);
var july_ndvi = ee.Image(median_july).select(['NDVI']);
var july_ndwi = ee.Image(median_july).select(['NDWI']);

// Create single band images for August median.
var august_2_blue = ee.Image(median_august).select(['B2']);
var august_3_green = ee.Image(median_august).select(['B3']);
var august_4_red = ee.Image(median_august).select(['B4']);
var august_5_redEdge1 = ee.Image(median_august).select(['B5']);
var august_6_redEdge2 = ee.Image(median_august).select(['B6']);
var august_7_redEdge3 = ee.Image(median_august).select(['B7']);
var august_8_nearInfrared = ee.Image(median_august).select(['B8']);
var august_8a_redEdge4 = ee.Image(median_august).select(['B8A']);
var august_11_shortInfrared1 = ee.Image(median_august).select(['B11']);
var august_12_shortInfrared2 = ee.Image(median_august).select(['B12']);
var august_evi2 = ee.Image(median_august).select(['EVI2']);
var august_nbr = ee.Image(median_august).select(['NBR']);
var august_ndmi = ee.Image(median_august).select(['NDMI']);
var august_ndsi = ee.Image(median_august).select(['NDSI']);
var august_ndvi = ee.Image(median_august).select(['NDVI']);
var august_ndwi = ee.Image(median_august).select(['NDWI']);

// Create single band images for September median.
var september_2_blue = ee.Image(median_september).select(['B2']);
var september_3_green = ee.Image(median_september).select(['B3']);
var september_4_red = ee.Image(median_september).select(['B4']);
var september_5_redEdge1 = ee.Image(median_september).select(['B5']);
var september_6_redEdge2 = ee.Image(median_september).select(['B6']);
var september_7_redEdge3 = ee.Image(median_september).select(['B7']);
var september_8_nearInfrared = ee.Image(median_september).select(['B8']);
var september_8a_redEdge4 = ee.Image(median_september).select(['B8A']);
var september_11_shortInfrared1 = ee.Image(median_september).select(['B11']);
var september_12_shortInfrared2 = ee.Image(median_september).select(['B12']);
var september_evi2 = ee.Image(median_september).select(['EVI2']);
var september_nbr = ee.Image(median_september).select(['NBR']);
var september_ndmi = ee.Image(median_september).select(['NDMI']);
var september_ndsi = ee.Image(median_september).select(['NDSI']);
var september_ndvi = ee.Image(median_september).select(['NDVI']);
var september_ndwi = ee.Image(median_september).select(['NDWI']);

// Export images for June to Google Drive.
Export.image.toDrive({
  image: june_2_blue,
  description: 'Sent2_06_2_blue',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_3_green,
  description: 'Sent2_06_3_green',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_4_red,
  description: 'Sent2_06_4_red',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_5_redEdge1,
  description: 'Sent2_06_5_redEdge1',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_6_redEdge2,
  description: 'Sent2_06_6_redEdge2',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_7_redEdge3,
  description: 'Sent2_06_7_redEdge3',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_8_nearInfrared,
  description: 'Sent2_06_8_nearInfrared',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_8a_redEdge4,
  description: 'Sent2_06_8a_redEdge4',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_11_shortInfrared1,
  description: 'Sent2_06_11_shortInfrared1',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_12_shortInfrared2,
  description: 'Sent2_06_12_shortInfrared2',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_evi2,
  description: 'Sent2_06_evi2',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_nbr,
  description: 'Sent2_06_nbr',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_ndmi,
  description: 'Sent2_06_ndmi',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_ndsi,
  description: 'Sent2_06_ndsi',
  folder: 'Sent2_June',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_ndvi,
  description: 'Sent2_06_ndvi',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: june_ndwi,
  description: 'Sent2_06_ndwi',
  folder: 'Sent2_June',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});

// Export images for July to Google Drive.
Export.image.toDrive({
  image: july_2_blue,
  description: 'Sent2_07_2_blue',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_3_green,
  description: 'Sent2_07_3_green',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_4_red,
  description: 'Sent2_07_4_red',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_5_redEdge1,
  description: 'Sent2_07_5_redEdge1',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_6_redEdge2,
  description: 'Sent2_07_6_redEdge2',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_7_redEdge3,
  description: 'Sent2_07_7_redEdge3',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_8_nearInfrared,
  description: 'Sent2_07_8_nearInfrared',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_8a_redEdge4,
  description: 'Sent2_07_8a_redEdge4',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_11_shortInfrared1,
  description: 'Sent2_07_11_shortInfrared1',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_12_shortInfrared2,
  description: 'Sent2_07_12_shortInfrared2',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_evi2,
  description: 'Sent2_07_evi2',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_nbr,
  description: 'Sent2_07_nbr',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_ndmi,
  description: 'Sent2_07_ndmi',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_ndsi,
  description: 'Sent2_07_ndsi',
  folder: 'Sent2_July',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_ndvi,
  description: 'Sent2_07_ndvi',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: july_ndwi,
  description: 'Sent2_07_ndwi',
  folder: 'Sent2_July',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});

// Export images for August to Google Drive.
Export.image.toDrive({
  image: august_2_blue,
  description: 'Sent2_08_2_blue',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_3_green,
  description: 'Sent2_08_3_green',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_4_red,
  description: 'Sent2_08_4_red',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_5_redEdge1,
  description: 'Sent2_08_5_redEdge1',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_6_redEdge2,
  description: 'Sent2_08_6_redEdge2',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_7_redEdge3,
  description: 'Sent2_08_7_redEdge3',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_8_nearInfrared,
  description: 'Sent2_08_8_nearInfrared',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_8a_redEdge4,
  description: 'Sent2_08_8a_redEdge4',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_11_shortInfrared1,
  description: 'Sent2_08_11_shortInfrared1',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_12_shortInfrared2,
  description: 'Sent2_08_12_shortInfrared2',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_evi2,
  description: 'Sent2_08_evi2',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_nbr,
  description: 'Sent2_08_nbr',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_ndmi,
  description: 'Sent2_08_ndmi',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_ndsi,
  description: 'Sent2_08_ndsi',
  folder: 'Sent2_August',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_ndvi,
  description: 'Sent2_08_ndvi',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: august_ndwi,
  description: 'Sent2_08_ndwi',
  folder: 'Sent2_August',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});

// Export images for September to Google Drive.
Export.image.toDrive({
  image: september_2_blue,
  description: 'Sent2_09_2_blue',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_3_green,
  description: 'Sent2_09_3_green',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_4_red,
  description: 'Sent2_09_4_red',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_5_redEdge1,
  description: 'Sent2_09_5_redEdge1',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_6_redEdge2,
  description: 'Sent2_09_6_redEdge2',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_7_redEdge3,
  description: 'Sent2_09_7_redEdge3',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_8_nearInfrared,
  description: 'Sent2_09_8_nearInfrared',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_8a_redEdge4,
  description: 'Sent2_09_8a_redEdge4',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_11_shortInfrared1,
  description: 'Sent2_09_11_shortInfrared1',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_12_shortInfrared2,
  description: 'Sent2_09_12_shortInfrared2',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_evi2,
  description: 'Sent2_09_evi2',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_nbr,
  description: 'Sent2_09_nbr',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_ndmi,
  description: 'Sent2_09_ndmi',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_ndsi,
  description: 'Sent2_09_ndsi',
  folder: 'Sent2_September',
  scale: 20,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_ndvi,
  description: 'Sent2_09_ndvi',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: september_ndwi,
  description: 'Sent2_09_ndwi',
  folder: 'Sent2_September',
  scale: 10,
  region: aoi,
  maxPixels: 1e12
});
