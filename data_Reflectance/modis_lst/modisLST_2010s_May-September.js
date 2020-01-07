/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Mean Monthly Land Surface Temperature MODIS Terra 2010-2019
Author: Timm Nawrocki, Alaska Center for Conservation Science
Created on: 2020-01-06
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces a decadal monthly mean land surface temperature for May-September 2010-2019 at 1x1 km resolution from MODIS Terra data.
---------------------------------------------------------------------------*/

// Define an area of interest geometry.
var areaOfInterest = ee.Geometry.Polygon(
        [[[-124.75596461166504, 65.24782261938977],
          [-129.23838648666504, 67.13612119890176],
          [-132.05088648666504, 69.97574970758016],
          [-132.92979273666504, 69.8550208602439],
          [-135.56651148666504, 69.87015003780978],
          [-137.76377711166504, 69.62677163259121],
          [-140.53233179916504, 69.91547225054177],
          [-143.74033961166504, 70.28936994841152],
          [-148.13487086166504, 70.4958242967149],
          [-151.56260523666504, 70.91688665350067],
          [-153.75987086166504, 71.15963395390483],
          [-156.57237086166504, 71.55297830303623],
          [-158.81358179916504, 71.07430005882561],
          [-160.87901148666504, 70.68566985138149],
          [-163.12022242416504, 70.12568523860821],
          [-163.41094434628678, 69.50426825683435],
          [-164.42168653378678, 69.06907645562472],
          [-166.55303419003678, 69.02192846111325],
          [-167.16826856503678, 68.28618301659756],
          [-165.84990919003678, 67.90915951054939],
          [-164.31182325253678, 67.32347818827886],
          [-163.87237012753678, 66.74046906520739],
          [-165.10283887753678, 66.63612554976638],
          [-167.60772169003678, 66.08994658910905],
          [-168.83819044003678, 65.5135580554051],
          [-167.25615919003678, 65.18363309421102],
          [-166.42119825253678, 64.39755863669593],
          [-162.81768262753678, 64.14957835757748],
          [-161.89483106503678, 64.45446905674024],
          [-161.32354200253678, 63.99586511686167],
          [-162.07061231503678, 63.783120745391734],
          [-164.66338575253678, 63.411840776954904],
          [-166.08845855510356, 62.257638007636125],
          [-166.68172027385356, 61.66896505409583],
          [-165.82478668010356, 60.96238307995808],
          [-168.41756011760356, 60.10860817407865],
          [-167.09920074260356, 59.489662579646605],
          [-164.81404449260356, 59.667677460628035],
          [-162.17732574260356, 58.21695911762926],
          [-158.22224761760356, 57.98474175719714],
          [-161.05423808453884, 56.40258515094182],
          [-165.38285136578884, 54.68741249542895],
          [-164.72367167828884, 54.266111432246724],
          [-162.74613261578884, 54.03447866766272],
          [-158.50540995953884, 54.91538732845942],
          [-156.44689105781276, 55.4751178863458],
          [-153.81017230781276, 56.117385954208316],
          [-151.52501605781276, 57.53587890537229],
          [-150.07482074531276, 58.878535470636635],
          [-145.98790668281276, 59.70877267960307],
          [-143.52696918281276, 59.6644116824743],
          [-140.01134418281276, 59.19506318814933],
          [-136.83093870551534, 57.00172270715797],
          [-133.44714964301534, 54.30035328234322],
          [-130.34900511176534, 54.35160870545166],
          [-128.85486448676534, 55.48804986027534],
          [-129.86560667426534, 56.31335145359372],
          [-131.73328245551534, 57.64232708549437],
          [-134.15027464301534, 59.475652022862384],
          [-132.19470823676534, 59.475652022862384],
          [-128.34949339301534, 59.46449016909336],
          [-124.59216917426534, 59.46449016909336],
          [-120.37341917426534, 59.45332462784402],
          [-120.46130979926534, 61.843072859143135]]]);

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