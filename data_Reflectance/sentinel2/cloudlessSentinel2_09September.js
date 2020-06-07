/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Cloud-reduced Greenest Pixel Composite Sentinel 2 Imagery for September 2015-2019
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2019-03-19
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a cloud-reduced greenest pixel composite (based on maximum NDVI) for bands 1-12 plus Enhanced Vegetation Index-2 (EVI2), Normalized Burn Ratio (NBR), Normalized Difference Moisture Index (NDMI), Normalized Difference Snow Index (NDSI), Normalized Difference Vegetation Index (NDVI), Normalized Difference Water Index (NDWI) using the Sentinel2 Top-Of-Atmosphere (TOA) reflectance image collection filtered to the month of September from 2015 through 2018. See Chander et al. 2009 for a description of the TOA reflectance method. The best pixel selection is based on maximum NDVI for all metrics to ensure uniform pixel selection from all bands.
- EVI-2 was calculated as (Red - Green) / (Red + [2.4 x Green] + 1), where Red is Landsat 8 Band 4 and Green is Landsat 8 Band 3.
- NBR was calculated as (NIR - SWIR2) / (NIR + SWIR2), where NIR (near infrared) is Landsat 8 Band 5 and SWIR2 (short-wave infrared 2) is Landsat 8 Band 7, using the Google Earth Engine normalized difference algorithm.
- NDMI was calculated as (NIR - SWIR1)/(NIR + SWIR1), where NIR (near infrared) is Landsat 8 Band 5 and SWIR1 (short-wave infrared 1) is Landsat 8 Band 6, using the Google Earth Engine normalized difference algorithm.
- NDSI was calculated as (Green - SWIR1) / (Green + SWIR1), where Green is Landsat 8 Band 3 and SWIR1 (short-wave infrared 1) is Landsat 8 Band 6, using the Google Earth Engine normalized difference algorithm.
- NDVI was calculated as (NIR - Red)/(NIR + Red), where NIR (near infrared) is Landsat 8 Band 5 and Red is Landsat 8 Band 4, using the Google Earth Engine normalized difference algorithm.
- NDWI was calculated as (Green - NIR)/(Green + NIR), where Green is Landsat 8 Band 3 and NIR (near infrared) is Landsat 8 Band 5, using the Google Earth Engine normalized difference algorithm.
---------------------------------------------------------------------------*/

// Define an area of interest geometry.
var areaOfInterest = /* color: #d63000 */ee.Geometry.Polygon(
        [[[-157.162890625, 71.50564609039189],
          [-162.52421875, 70.41644456151228],
          [-166.91875, 68.95235404370442],
          [-168.85234375, 65.59693300115998],
          [-166.655078125, 61.15632806263397],
          [-163.93046875, 59.23481658275705],
          [-161.908984375, 58.18500989237897],
          [-157.514453125, 55.84121174850002],
          [-152.592578125, 58.918656670521514],
          [-144.155078125, 59.77005911617141],
          [-135.45390625, 59.81428022698168],
          [-129.389453125, 59.8363688052449],
          [-122.09453124999999, 59.8584427406498],
          [-120.63334960937499, 61.53563010419206],
          [-120.61137695312499, 61.74437380441509],
          [-120.76518554687499, 61.85340117447247],
          [-122.85258789062499, 62.28054652518679],
          [-123.05034179687499, 63.28538282787206],
          [-125.03217580676562, 64.97339644746218],
          [-130.66483863306223, 67.52534863145183],
          [-132.99394019556223, 67.52534863145183],
          [-133.34550269556223, 69.47294574968633],
          [-134.44413550806223, 69.83959953895578],
          [-136.81718238306223, 69.28723396277756],
          [-139.98124488306223, 69.83959953895578],
          [-143.05741675806223, 70.28909472095481],
          [-150.00077613306223, 70.67085955600184],
          [-153.25272925806223, 71.07403538133154]]]);

// Define a function to quality control clouds and cirrus
var maskS2clouds = function(image) {
  var qa_layer = image.select('QA60');
  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa_layer.bitwiseAnd(cloudBitMask).eq(0)
  .and(qa_layer.bitwiseAnd(cirrusBitMask).eq(0));
  // Return the masked image collection
  return image.updateMask(mask).divide(10000);
}

// Define a function for EVI-2 calculation.
var addEVI2 = function(image) {
  // Assign variables to the red and green Landsat 8 bands.
  var red = image.select('B4');
  var green = image.select('B3');
  //Compute the Enhanced Vegetation Index-2 (EVI2).
  var evi2Calc = red.subtract(green).divide(red.add(green.multiply(2.4)).add(1)).rename('EVI2');
  // Return the masked image with an EVI-2 band.
  return image.addBands(evi2Calc);
};

// Define a function for NDSI calculation.
var addNBR = function(image) {
  //Compute the Normalized Burn Ratio (NBR).
  var nbrCalc = image.normalizedDifference(['B8', 'B12']).rename('NBR');
  // Return the masked image with an NBR band.
  return image.addBands(nbrCalc);
};

// Define a function for NDMI calculation.
var addNDMI = function(image) {
  //Compute the Normalized Difference Moisture Index (NDMI).
  var ndmiCalc = image.normalizedDifference(['B8', 'B11']).rename('NDMI');
  // Return the masked image with an NDMI band.
  return image.addBands(ndmiCalc);
};

// Define a function for NDSI calculation.
var addNDSI = function(image) {
  //Compute the Normalized Difference Snow Index (NDSI).
  var ndsiCalc = image.normalizedDifference(['B3', 'B11']).rename('NDSI');
  // Return the masked image with an NDSI band.
  return image.addBands(ndsiCalc);
};

// Define a function for NDVI calculation.
var addNDVI = function(image) {
  //Compute the Normalized Burn Ratio (NBR).
  var ndviCalc = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  // Return the masked image with an NBR band.
  return image.addBands(ndviCalc);
};

// Define a function for NDWI calculation.
var addNDWI = function(image) {
  //Compute the Normalized Difference Water Index (NDWI).
  var ndwiCalc = image.normalizedDifference(['B3', 'B8']).rename('NDWI');
  // Return the masked image with an NDWI band.
  return image.addBands(ndwiCalc);
};

// Import Sentinel 2 TOA Reflectance (ortho-rectified) within study area, date range, and cloud mask. Add NDVI.
var cloudlessCollection = ee.ImageCollection("COPERNICUS/S2")
							.filterBounds(areaOfInterest)
							.filter(ee.Filter.calendarRange(2015, 2019, 'year'))
							.filter(ee.Filter.calendarRange(9, 9, 'month'))
							.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
							.map(maskS2clouds)
							.map(addNDVI)

// Make a greenest pixel composite from the image collection based on NDVI.
var compositeGreenest = cloudlessCollection.qualityMosaic('NDVI');

// Add bands to the greenest pixel composite for EVI-2, NBR, NDMI, NDSI, NDWI.
var compositeGreenest = addEVI2(compositeGreenest);
var compositeGreenest = addNBR(compositeGreenest);
var compositeGreenest = addNDMI(compositeGreenest);
var compositeGreenest = addNDSI(compositeGreenest);
var compositeGreenest = addNDWI(compositeGreenest);
print('Greenest Pixel NDVI:', compositeGreenest)

// Add image to the map.
Map.centerObject(areaOfInterest);
var rgbVis = {
  min: 0.0,
  max: 0.3,
  bands: ['B4', 'B3', 'B2'],
};
Map.addLayer(compositeGreenest, rgbVis, 'Greenest pixel composite');

// Create a single band image for Landsat 8 bands 1-7 and the additional bands calculated above.
var band_2_blue = ee.Image(compositeGreenest).select(['B2']);
var band_3_green = ee.Image(compositeGreenest).select(['B3']);
var band_4_red = ee.Image(compositeGreenest).select(['B4']);
var band_5_redEdge1 = ee.Image(compositeGreenest).select(['B5']);
var band_6_redEdge2 = ee.Image(compositeGreenest).select(['B6']);
var band_7_redEdge3 = ee.Image(compositeGreenest).select(['B7']);
var band_8_nearInfrared = ee.Image(compositeGreenest).select(['B8']);
var band_8a_redEdge4 = ee.Image(compositeGreenest).select(['B8A']);
var band_11_shortInfrared1 = ee.Image(compositeGreenest).select(['B11']);
var band_12_shortInfrared2 = ee.Image(compositeGreenest).select(['B12']);
var evi2 = ee.Image(compositeGreenest).select(['EVI2']);
var nbr = ee.Image(compositeGreenest).select(['NBR']);
var ndmi = ee.Image(compositeGreenest).select(['NDMI']);
var ndsi = ee.Image(compositeGreenest).select(['NDSI']);
var ndvi = ee.Image(compositeGreenest).select(['NDVI']);
var ndwi = ee.Image(compositeGreenest).select(['NDWI']);

// Export images to Google Drive.
Export.image.toDrive({
  image: band_2_blue,
  description: 'Sent2_09September_2_blue',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_3_green,
  description: 'Sent2_09September_3_green',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_4_red,
  description: 'Sent2_09September_4_red',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_5_redEdge1,
  description: 'Sent2_09September_5_redEdge1',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_6_redEdge2,
  description: 'Sent2_09September_6_redEdge2',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_7_redEdge3,
  description: 'Sent2_09September_7_redEdge3',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8_nearInfrared,
  description: 'Sent2_09September_8_nearInfrared',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_8a_redEdge4,
  description: 'Sent2_09September_8a_redEdge4',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_11_shortInfrared1,
  description: 'Sent2_09September_11_shortInfrared1',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: band_12_shortInfrared2,
  description: 'Sent2_09September_12_shortInfrared2',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: evi2,
  description: 'Sent2_09September_evi2',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: nbr,
  description: 'Sent2_09September_nbr',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndmi,
  description: 'Sent2_09September_ndmi',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndsi,
  description: 'Sent2_09September_ndsi',
  folder: 'Beringia_Sentinel-2',
  scale: 20,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndvi,
  description: 'Sent2_09September_ndvi',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: ndwi,
  description: 'Sent2_09September_ndwi',
  folder: 'Beringia_Sentinel-2',
  scale: 10,
  region: areaOfInterest,
  maxPixels: 1e12
});