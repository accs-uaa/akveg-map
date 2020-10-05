/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Median Growing-season Composite Sentinel 1 SAR for 2015-2020
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2020-10-04
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces median composites using ascending orbitals for the VV and VH polarizations from Sentinel-1.
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

// Import the Sentinel-1 Image Collection VV and VH polarizations within study area and date range
var sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(areaOfInterest)
    .filter(ee.Filter.calendarRange(2015, 2020, 'year'))
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