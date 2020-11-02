/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Cloud-reduced Maximum NDVI Composite of Sentinel 2 Imagery for September-October 2015-2020
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2020-11-02
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a cloud-reduced maximum NDVI composite for bands 1-12 plus Enhanced Vegetation Index-2 (EVI2), Normalized Burn Ratio (NBR), Normalized Difference Moisture Index (NDMI), Normalized Difference Snow Index (NDSI), Normalized Difference Vegetation Index (NDVI), Normalized Difference Water Index (NDWI) using the Sentinel-2 Top-Of-Atmosphere image collection filtered to September 10 through end of October from 2015 through 2020.
- EVI-2 was calculated as (Red - Green) / (Red + [2.4 x Green] + 1), where Red is Sentinel-2 Band 4 and Green is Sentinel-2 Band 3.
- NBR was calculated as (NIR - SWIR2) / (NIR + SWIR2), where NIR (near infrared) is Sentinel-2 Band 8 and SWIR2 (short-wave infrared 2) is Sentinel-2 Band 12, using the Google Earth Engine normalized difference algorithm.
- NDMI was calculated as (NIR - SWIR1)/(NIR + SWIR1), where NIR (near infrared) is Sentinel-2 Band 8 and SWIR1 (short-wave infrared 1) is Sentinel-2 Band 11, using the Google Earth Engine normalized difference algorithm.
- NDSI was calculated as (Green - SWIR1) / (Green + SWIR1), where Green is Sentinel-2 Band 3 and SWIR1 (short-wave infrared 1) is Sentinel-2 Band 11, using the Google Earth Engine normalized difference algorithm.
- NDVI was calculated as (NIR - Red)/(NIR + Red), where NIR (near infrared) is Sentinel-2 Band 8 and Red is Sentinel-2 Band 4, using the Google Earth Engine normalized difference algorithm.
- NDWI was calculated as (Green - NIR)/(Green + NIR), where Green is Sentinel-2 Band 3 and NIR (near infrared) is Sentinel-2 Band 8, using the Google Earth Engine normalized difference algorithm.
---------------------------------------------------------------------------*/

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

// Create filters
var filter_1 = ee.Filter.date('2015-09-10', '2015-10-30')
var filter_2 = ee.Filter.date('2016-09-10', '2016-10-30')
var filter_3 = ee.Filter.date('2017-09-10', '2017-10-30')
var filter_4 = ee.Filter.date('2018-09-10', '2018-10-30')
var filter_5 = ee.Filter.date('2019-09-10', '2019-10-30')
var filter_6 = ee.Filter.date('2020-09-10', '2020-10-30')

// Create a combined filter
var filter_all = ee.Filter.or(filter_1, filter_2, filter_3, filter_4, filter_5, filter_6)

// Import Sentinel 2 Top-Of-Atmosphere Reflectance within study area, date range, and cloud percentage.
var s2 = ee.ImageCollection('COPERNICUS/S2')
              .filterBounds(areaOfInterest)
          		.filter(filter_all)
          		.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40));

// Define a function to quality control clouds and cirrus
function maskS2clouds(image) {
	var qa = image.select('QA60');
	// Bits 10 and 11 are clouds and cirrus, respectively.
	var cloudBitMask = 1 << 10;
	var cirrusBitMask = 1 << 11;
	//Both flags should be set to zero, indicating clear conditions.
	var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
		.and(qa.bitwiseAnd(cirrusBitMask).eq(0));
	return image.updateMask(mask).divide(10000);
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
  //Compute the Normalized Burn Ratio (NBR).
  var ndviCalc = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  // Return the masked image with an NBR band.
  return image.addBands(ndviCalc);
}

// Define a function for NDWI calculation.
function addNDWI(image) {
  //Compute the Normalized Difference Water Index (NDWI).
  var ndwiCalc = image.normalizedDifference(['B3', 'B8']).rename('NDWI');
  // Return the masked image with an NDWI band.
  return image.addBands(ndwiCalc);
}

// Filter clouds from image collection and add all metrics.
var cloudlessCollection = s2.map(maskS2clouds)
    .map(addEVI2)
    .map(addNBR)
    .map(addNDMI)
    .map(addNDSI)
    .map(addNDVI)
    .map(addNDWI);

// Make a maximum NDVI composite from the image collection.
var composite = cloudlessCollection.qualityMosaic('NDVI');
print('Maximum NDVI Composite:', composite);

// Add image to the map.
Map.centerObject(areaOfInterest);
var rgbVis = {
  min: 0.0,
  max: 0.3,
  bands: ['B4', 'B3', 'B2'],
};
Map.addLayer(composite, rgbVis, 'Maximum NDVI Composite');

// Create a single band image for Sentinel-2 bands 2-8, 8a, 11-12, and the additional bands calculated above.
var band_2_blue = ee.Image(composite).select(['B2']);
var band_3_green = ee.Image(composite).select(['B3']);
var band_4_red = ee.Image(composite).select(['B4']);
var band_5_redEdge1 = ee.Image(composite).select(['B5']);
var band_6_redEdge2 = ee.Image(composite).select(['B6']);
var band_7_redEdge3 = ee.Image(composite).select(['B7']);
var band_8_nearInfrared = ee.Image(composite).select(['B8']);
var band_8a_redEdge4 = ee.Image(composite).select(['B8A']);
var band_11_shortInfrared1 = ee.Image(composite).select(['B11']);
var band_12_shortInfrared2 = ee.Image(composite).select(['B12']);
var evi2 = ee.Image(composite).select(['EVI2']);
var nbr = ee.Image(composite).select(['NBR']);
var ndmi = ee.Image(composite).select(['NDMI']);
var ndsi = ee.Image(composite).select(['NDSI']);
var ndvi = ee.Image(composite).select(['NDVI']);
var ndwi = ee.Image(composite).select(['NDWI']);

// Export images to Google Drive.
Export.image.toDrive({
  image: band_2_blue,
  description: 'Sent2_10_2_blue',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_3_green,
  description: 'Sent2_10_3_green',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_4_red,
  description: 'Sent2_10_4_red',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_5_redEdge1,
  description: 'Sent2_10_5_redEdge1',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_6_redEdge2,
  description: 'Sent2_10_6_redEdge2',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_7_redEdge3,
  description: 'Sent2_10_7_redEdge3',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8_nearInfrared,
  description: 'Sent2_10_8_nearInfrared',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8a_redEdge4,
  description: 'Sent2_10_8a_redEdge4',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_11_shortInfrared1,
  description: 'Sent2_10_11_shortInfrared1',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_12_shortInfrared2,
  description: 'Sent2_10_12_shortInfrared2',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: evi2,
  description: 'Sent2_10_evi2',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: nbr,
  description: 'Sent2_10_nbr',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndmi,
  description: 'Sent2_10_ndmi',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndsi,
  description: 'Sent2_10_ndsi',
  folder: 'Beringia_Sentinel-2_October',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndvi,
  description: 'Sent2_10_ndvi',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndwi,
  description: 'Sent2_10_ndwi',
  folder: 'Beringia_Sentinel-2_October',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
