/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Median Growing-season Composite Sentinel 1 SAR for 2015-2019
Author: Timm Nawrocki, Alaska Center for Conservation Science
Created on: 2020-05-22
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces median composites using ascending orbitals for the VV and VH polarizations from Sentinel-1.
---------------------------------------------------------------------------*/

// Define an area of interest property for Point Lay.
var areaOfInterest = /* color: #d63000 */ee.Geometry.Polygon(
    [[[-157.162890625, 71.50564609039189],
        [-162.52421875, 70.41644456151228],
        [-166.91875, 68.95235404370442],
        [-168.85234375, 65.59693300115998],
        [-166.655078125, 61.15632806263397],
        [-163.93046875, 59.23481658275705],
        [-161.908984375, 58.18500989237897],
        [-163.5414063911573, 56.86160790214102],
        [-159.55454560145273, 55.28284174551137],
        [-157.514453125, 55.84121174850002],
        [-152.592578125, 58.918656670521514],
        [-144.155078125, 59.77005911617141],
        [-135.45390625, 59.81428022698168],
        [-132.553515625, 59.83636880524493],
        [-132.553515625, 60.29685638676382],
        [-132.498583984375, 60.6002902266264],
        [-132.564501953125, 61.02887047386469],
        [-132.630419921875, 61.56180016128955],
        [-132.608447265625, 62.19867206950478],
        [-132.718310546875, 62.967557980145465],
        [-132.67866018176562, 63.9504835044207],
        [-132.76744907435707, 64.59567908628253],
        [-132.86210425806223, 65.60385081139084],
        [-132.90604957056223, 66.91280852626836],
        [-133.34550269556223, 69.47294574968633],
        [-134.44413550806223, 69.83959953895578],
        [-136.81718238306223, 69.28723396277756],
        [-139.98124488306223, 69.83959953895578],
        [-143.05741675806223, 70.28909472095481],
        [-150.00077613306223, 70.67085955600184],
        [-153.25272925806223, 71.07403538133154]]]);

// Import the Sentinel-1 Image Collection VV and VH polarizations within study area and date range
var sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(areaOfInterest)
    .filter(ee.Filter.calendarRange(2015, 2019, 'year'))
    .filter(ee.Filter.calendarRange(6, 8, 'month'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    .sort('system:time_start');
print("Sentinel 1 (date-filtered:", sentinel1);

// Create a VV and VH composite from ascending orbits
var vv = sentinel1.select('VV').median()
var vh = sentinel1.select('VH').median()
print(vv)
print(vh)

// Add image to the map.
Map.centerObject(areaOfInterest);
Map.addLayer(vv, {min: -30, max: 0}, 'vv');
Map.addLayer(vh, {min: -30, max: 0}, 'vh');

// Export images to Google Drive.
Export.image.toDrive({
    image: vv,
    description: 'Sent1_vv',
    folder: 'Beringia_Sentinel1',
    scale: 10,
    region: areaOfInterest,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vh,
    description: 'Sent1_vh',
    folder: 'Beringia_Sentinel1',
    scale: 10,
    region: areaOfInterest,
    maxPixels: 1e12
});