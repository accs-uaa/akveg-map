/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Mean Monthly Land Surface Temperature MODIS Terra 2010-2019
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2021-01-05
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a decadal monthly mean land surface temperature for May-September 2010-2019 at 1x1 km resolution from MODIS Terra data.
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

// Select the MODIS Land Surface Temperature collection for years 2010 to 2019
var lstCollection = ee.ImageCollection("MODIS/006/MOD11A2")
  .filter(ee.Filter.calendarRange(2010, 2019, 'year'));

// Subset monthly collections for each month May-September
var lstMay = lstCollection
  .filter(ee.Filter.calendarRange(5, 5, 'month'))
  .select('LST_Day_1km')
  .reduce(ee.Reducer.median());
var lstJune = lstCollection
  .filter(ee.Filter.calendarRange(6, 6, 'month'))
  .select('LST_Day_1km')
  .reduce(ee.Reducer.median());
var lstJuly = lstCollection
  .filter(ee.Filter.calendarRange(7, 7, 'month'))
  .select('LST_Day_1km')
  .reduce(ee.Reducer.median());
var lstAugust = lstCollection
  .filter(ee.Filter.calendarRange(8, 8, 'month'))
  .select('LST_Day_1km')
  .reduce(ee.Reducer.median());
var lstSeptember = lstCollection
  .filter(ee.Filter.calendarRange(9, 9, 'month'))
  .select('LST_Day_1km')
  .reduce(ee.Reducer.median());

// Add monthly land surface temperature to the code editor view window
var landSurfaceTemperatureVis = {
  min: 14000.0,
  max: 16000.0,
  palette: [
    '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
    '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
    '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
    'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
    'ff0000', 'de0101', 'c21301', 'a71001', '911003'
  ],
};
Map.setCenter(-148.434, 63.2, 4);
Map.addLayer(
  lstMay, landSurfaceTemperatureVis,
  'May');
Map.addLayer(
  lstJune, landSurfaceTemperatureVis,
  'June');
Map.addLayer(
  lstJuly, landSurfaceTemperatureVis,
  'July');
Map.addLayer(
  lstAugust, landSurfaceTemperatureVis,
  'August');
Map.addLayer(
  lstSeptember, landSurfaceTemperatureVis,
  'September');

// Export images to Google Drive.
Export.image.toDrive({
  image: lstMay,
  description: 'MODIS_05May_meanLST',
  folder: 'Beringia_MODIS',
  scale: 1000,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: lstJune,
  description: 'MODIS_06June_meanLST',
  folder: 'Beringia_MODIS',
  scale: 1000,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: lstJuly,
  description: 'MODIS_07July_meanLST',
  folder: 'Beringia_MODIS',
  scale: 1000,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: lstAugust,
  description: 'MODIS_08August_meanLST',
  folder: 'Beringia_MODIS',
  scale: 1000,
  region: areaOfInterest,
  maxPixels: 1e12
});
Export.image.toDrive({
  image: lstSeptember,
  description: 'MODIS_09September_meanLST',
  folder: 'Beringia_MODIS',
  scale: 1000,
  region: areaOfInterest,
  maxPixels: 1e12
});
