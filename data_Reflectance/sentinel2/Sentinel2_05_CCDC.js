/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Start of Growing Season (May 25, 2019) Composite of Sentinel 2 Imagery
Author: Timm Nawrocki, Matt Macander; Alaska Center for Conservation Science, ABR Inc.-Environmental Research and Services
Last Updated: 2021-02-25
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a predicted normal composite representing the start of growing season as May 25, 2019, using the Continuous Change Detection and Classification (CCDC) algorithm for bands 1-12 plus Enhanced Vegetation Index-2 (EVI2), Normalized Burn Ratio (NBR), Normalized Difference Moisture Index (NDMI), Normalized Difference Snow Index (NDSI), Normalized Difference Vegetation Index (NDVI), and Normalized Difference Water Index (NDWI) using the Sentinel-2 Top-Of-Atmosphere image collection (2015-2020). Pixels that could not be predicted using CCDC are filled from a median composite for May 15-June 30 2015-2020.
---------------------------------------------------------------------------*/


// 1. DEFINE GEOGRAPHIES

// Define an area of interest geometry.
var areaOfInterest = /* color: #0b4a8b */ee.Geometry.Polygon(
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

// Define a test area.
var areaTest = /* color: #98ff00 */ee.Geometry.Polygon(
        [[[-158.47612110126832, 60.107664453356165],
          [-158.45483509052613, 59.916504163066996],
          [-157.90139881122926, 59.90824259997804],
          [-157.9309245680652, 60.115192097201366]]]);

// 2. DEFINE FUNCTIONS

// Load Temporal Segmentation API.
var temporalSegmentation = require('users/wiell/temporalSegmentation:temporalSegmentation')

// Define a function to quality control clouds and cirrus.
function maskS2clouds(image) {
	var qa = image.select('QA60');
	// Bits 10 and 11 are clouds and cirrus, respectively.
	var cloudBitMask = 1 << 10;
	var cirrusBitMask = 1 << 11;
	//Both flags should be set to zero, indicating clear conditions.
	var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
		.and(qa.bitwiseAnd(cirrusBitMask).eq(0));
	return image.updateMask(mask);
}

// Define a function for EVI-2 calculation.
function addEVI2(image) {
  // Assign variables to the red and green Sentinel-2 bands.
  var red = image.select('B4');
  var green = image.select('B3');
  //Compute the Enhanced Vegetation Index-2 (EVI2).
  var evi2Calc = red.subtract(green).divide(red.add(green.multiply(2.4)).add(1)).rename('EVI2');
  // Return the masked image with an EVI-2 band.
  return image.addBands(evi2Calc);
}

// Define a function for NBR calculation.
function addNBR(image) {
  //Compute the Normalized Burn Ratio (NBR).
  var nbrCalc = image.normalizedDifference(['B8', 'B12']).rename('NBR');
  // Return the masked image with an NBR band.
  return image.addBands(nbrCalc);
}

// Define a function for NDMI calculation.
function addNDMI(image) {
  //Compute the Normalized Difference Moisture Index (NDMI).
  var ndmiCalc = image.normalizedDifference(['B8', 'B11']).rename('NDMI');
  // Return the masked image with an NDMI band.
  return image.addBands(ndmiCalc);
}

// Define a function for NDSI calculation.
function addNDSI(image) {
  //Compute the Normalized Difference Snow Index (NDSI).
  var ndsiCalc = image.normalizedDifference(['B3', 'B11']).rename('NDSI');
  // Return the masked image with an NDSI band.
  return image.addBands(ndsiCalc);
}

// Define a function for NDVI calculation.
function addNDVI(image) {
  //Compute the Normalized Difference Vegetation Index (NDVI).
  var ndviCalc = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  // Return the masked image with an NDVI band.
  return image.addBands(ndviCalc);
}

// Define a function for NDWI calculation.
function addNDWI(image) {
  //Compute the Normalized Difference Water Index (NDWI).
  var ndwiCalc = image.normalizedDifference(['B3', 'B8']).rename('NDWI');
  // Return the masked image with an NDWI band.
  return image.addBands(ndwiCalc);
}

// 3. CREATE CLOUD-REDUCED IMAGE COMPOSITE

// Define select spectral bands.
var bands = ['B2','B3','B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'EVI2', 'NBR', 'NDMI', 'NDSI', 'NDVI', 'NDWI']

// Import Sentinel 2 Top-Of-Atmosphere Reflectance within study area, date range, and cloud percentage.
var s2 = ee.ImageCollection('COPERNICUS/S2')
              .filterBounds(areaOfInterest)
              .filter(ee.Filter.calendarRange(2015, 2020, 'year'))
							.filter(ee.Filter.calendarRange(5, 10, 'month'))
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40));

// Filter clouds from image collection and add all metrics.
var cloudReducedS2 = s2.map(maskS2clouds)
    .map(addEVI2)
    .map(addNBR)
    .map(addNDMI)
    .map(addNDSI)
    .map(addNDVI)
    .map(addNDWI)
    .select(bands);

// 4. CREATE A MEDIAN COMPOSITE

// Filter image collection for median composite.
var filter_1 = ee.Filter.date('2015-05-15', '2015-06-30')
var filter_2 = ee.Filter.date('2016-05-15', '2016-06-30')
var filter_3 = ee.Filter.date('2017-05-15', '2017-06-30')
var filter_4 = ee.Filter.date('2018-05-15', '2018-06-30')
var filter_5 = ee.Filter.date('2019-05-15', '2019-06-30')
var filter_6 = ee.Filter.date('2020-05-15', '2020-06-30')
var filter_all = ee.Filter.or(filter_1, filter_2, filter_3, filter_4, filter_5, filter_6)
var compositeS2 = cloudReducedS2
    .filter(filter_all);

// Make a median composite from the image collection.
var median_composite = compositeS2
    .median();

// Add a source band to the median composite.
var mask = median_composite.select('NDVI').gt(-999999);
var median_composite = median_composite.addBands(mask.multiply(0).add(2)
    .toFloat()
    .rename('source'));
print('Median Composite:', median_composite);

// 5. CREATE PREDICTED IMAGE USING CCDC

// Filter image collection for CCDC.
var filter_1 = ee.Filter.date('2015-05-25', '2015-09-30')
var filter_2 = ee.Filter.date('2016-05-25', '2016-09-30')
var filter_3 = ee.Filter.date('2017-05-25', '2017-09-30')
var filter_4 = ee.Filter.date('2018-05-25', '2018-09-30')
var filter_5 = ee.Filter.date('2019-05-25', '2019-09-30')
var filter_6 = ee.Filter.date('2020-05-25', '2020-09-30')
var filter_all = ee.Filter.or(filter_1, filter_2, filter_3, filter_4, filter_5, filter_6)
var ccdcS2 = cloudReducedS2
    .filter(filter_all);

// Define parameters for CCDC.
var changeDetection = {
  collection: ccdcS2,
  breakpointBands: bands,
  tmaskBands: ['B3', 'B12'],
  minObservations: 6,
  chiSquareProbability: .99,
  minNumOfYearsScaler: 1.33,
  dateFormat: 1,
  lambda: 20,
  maxIterations: 25000
}

// Run CCDC.
var results = ee.Algorithms.TemporalSegmentation.Ccdc(changeDetection)
print('CCDC Results:', results)

// Set image prediction date.
var inputDate = '2019-05-25'

// Predict image for date using CCDC results.
var segments = temporalSegmentation.Segments(results, 1); // Create temporal segments
var segment = segments.findByDate(inputDate);
var fit_image = segment.fit({date: inputDate, harmonics: 3, extrapolateMaxDays: 30});

// Add a source band to fitted image.
var mask = fit_image.select('NDVI').gt(-999999);
var fit_image = fit_image.addBands(mask.multiply(0).add(1)
    .toFloat()
    .rename('source'));
print('Fitted Image:', fit_image);

// 6. COMPOSITE PREDICTED IMAGE WITH MEDIAN IMAGE

// Create an image collection of the CCDC predicted image and the median composite.
var compositeCollection = ee.ImageCollection.fromImages(
  [fit_image, median_composite]);

// Combine results collection with first non-null reducer.
var final_composite = compositeCollection.reduce(ee.Reducer.firstNonNull())
print('Final Composite:', final_composite)

// Export a test image.
Export.image.toAsset({
  image: final_composite,
  description: 'test_20190525',
  assetId: 'users/twnawrocki/test_20190525',
  region: areaTest,
  scale: 10,
  maxPixels: 1e12
});

// 7. VISUALIZE RESULTS

// Add image to the map.
Map.centerObject(areaTest);
var rgbVis = {
  min: 0,
  max: 3000,
  bands: ['B4_first', 'B3_first', 'B2_first']
};
var firVis = {
  min:0,
  max: [3500, 6000, 2000],
  bands: ['B11_first','B8_first','B4_first']
};
var ndviVis = {
  min: -1,
  max: 1,
  palette: ['blue', 'white', 'green'],
  bands: ['NDVI_first']
};
var sourceVis = {
  min: 1,
  max: 2,
  bands: ['source_first']
}
var testAsset = ee.Image('users/twnawrocki/test_20190525')
Map.addLayer(testAsset, rgbVis, 'Test Composite RGB');
Map.addLayer(testAsset, firVis, 'Test Composite FIR');
Map.addLayer(testAsset, ndviVis, 'Test Composite NDVI');
Map.addLayer(testAsset, sourceVis, 'Test Source');

// 8. EXPORT RESULTS TO DRIVE

// Create a single band image for Sentinel-2 bands 2-8, 8a, 11-12, and the additional bands calculated above.
var band_2_blue = ee.Image(final_composite).select(['B2_first']).divide(10000).rename('B2');
var band_3_green = ee.Image(final_composite).select(['B3_first']).divide(10000).rename('B3');
var band_4_red = ee.Image(final_composite).select(['B4_first']).divide(10000).rename('B4');
var band_5_redEdge1 = ee.Image(final_composite).select(['B5_first']).divide(10000).rename('B5');
var band_6_redEdge2 = ee.Image(final_composite).select(['B6_first']).divide(10000).rename('B6');
var band_7_redEdge3 = ee.Image(final_composite).select(['B7_first']).divide(10000).rename('B7');
var band_8_nearInfrared = ee.Image(final_composite).select(['B8_first']).divide(10000).rename('B8');
var band_8a_redEdge4 = ee.Image(final_composite).select(['B8A_first']).divide(10000).rename('B8A');
var band_11_shortInfrared1 = ee.Image(final_composite).select(['B11_first']).divide(10000).rename('B11');
var band_12_shortInfrared2 = ee.Image(final_composite).select(['B12_first']).divide(10000).rename('B12');
var evi2 = ee.Image(final_composite).select(['EVI2_first']).rename('EVI2');
var nbr = ee.Image(final_composite).select(['NBR_first']).rename('NBR');
var ndmi = ee.Image(final_composite).select(['NDMI_first']).rename('NDMI');
var ndsi = ee.Image(final_composite).select(['NDSI_first']).rename('NDSI');
var ndvi = ee.Image(final_composite).select(['NDVI_first']).rename('NDVI');
var ndwi = ee.Image(final_composite).select(['NDWI_first']).rename('NDWI');
var source = ee.Image(final_composite).select(['source_first']).rename('source');

// Export images to Google Drive.
Export.image.toDrive({
  image: band_2_blue,
  description: 'Sent2_05_2_blue',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_3_green,
  description: 'Sent2_05_3_green',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_4_red,
  description: 'Sent2_05_4_red',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_5_redEdge1,
  description: 'Sent2_05_5_redEdge1',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_6_redEdge2,
  description: 'Sent2_05_6_redEdge2',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_7_redEdge3,
  description: 'Sent2_05_7_redEdge3',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8_nearInfrared,
  description: 'Sent2_05_8_nearInfrared',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8a_redEdge4,
  description: 'Sent2_05_8a_redEdge4',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_11_shortInfrared1,
  description: 'Sent2_05_11_shortInfrared1',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_12_shortInfrared2,
  description: 'Sent2_05_12_shortInfrared2',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: evi2,
  description: 'Sent2_05_evi2',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: nbr,
  description: 'Sent2_05_nbr',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndmi,
  description: 'Sent2_05_ndmi',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndsi,
  description: 'Sent2_05_ndsi',
  folder: 'Beringia_Sentinel-2_May',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndvi,
  description: 'Sent2_05_ndvi',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndwi,
  description: 'Sent2_05_ndwi',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: source,
  description: 'Sent2_05_source',
  folder: 'Beringia_Sentinel-2_May',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
