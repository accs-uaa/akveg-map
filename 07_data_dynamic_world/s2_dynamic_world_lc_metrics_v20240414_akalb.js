// v20250414
// Step 2
// Mosaic MGRS Outputs
// Viz and Sanity Check
// Export to 50 km AKVEG tiles (3338, Alaska Albers)

  var dwVisParams = {
    min: 0,  max: 8,
    palette: [
      '#419BDF',  // 0 - Water
      '#397D49',  // 1 - Trees
      '#88B053',  // 2 - Grass
      '#7A87C6',  // 3 - Flooded Vegetation
      '#E49635',  // 4 - Crops
      '#DFC35A',  // 5 - Shrub & Scrub
      '#C4281B',  // 6 - Built Area
      '#A59B8F',  // 7 - Bare Ground
      '#B39FE1'   // 8 - Snow & Ice
    ]
  };

var transform = "[10, 0.0, 5, 0.0, -10, 5]";
var crs = 'EPSG:3338';
var version = 'v20250414';

// In batch processing, comment/uncomment from rows below to identify subsets of tiles to submit at one time
// Filtering AKVEG tiles by H (columns) below keeps individual script runs limited to <200 tiles
var   // minH = 1, maxH = 5,
  // minH = 6, maxH = 34,
  // minH = 35, maxH = 38, 
  // minH = 39, maxH = 40,
  // minH = 41, maxH = 44,
  // minH = 45, maxH = 49,
  // minH = 50, maxH = 50, 
  // minH = 51, maxH = 52,
  // minH = 53, maxH = 58,
  // minH = 59, maxH = 62, 
  // minH = 63, maxH = 67, 
  minH = 68, maxH = 75, 
  
  // V 1 to 99 means no filtering on AKVEG V (rows)
  minV = 1, maxV = 99;
  // minV = 27, maxV = 27;

// 2024-07-26 Ran thru H67v26
// var   minH = 67, maxH = 67, 
//   minV = 27, maxV = 99;
// var   minH = 66, maxH = 67, 
//   minV = 1, maxV = 99;
  
// Alternate method using wildcard match, e.g. to catch-up on a few missing tiles
// match = 'AK100H18',  
var manualList = [
  'AK050H01V31',
  // 'AK050H65V25',
  // 'AK050H66V28',
  // 'AK050H66V29',
  ];

//////////////////////////////////
// Mosaic monthly MGRS tiles
// From https://code.earthengine.google.com/bdb731ec03a1c9cf2ed8b09f6359c429
// https://code.earthengine.google.com/?scriptPath=users%2Fmmacander%2Fakveg_map%3Adynamic_world_metrics%2Fs2_dynamic_world_lc_metrics_v20250414

var dw_counts_plain_gcs_05 = ee.ImageCollection('projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b')
  .filter(ee.Filter.equals('month', '05'))
  // .map(function(img) {return img.int16()})
  .mosaic();
var dw_counts_plain_gcs_06 = ee.ImageCollection('projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b')
  .filter(ee.Filter.equals('month', '06'))
  // .map(function(img) {return img.int16()})
  .mosaic();
var dw_counts_plain_gcs_07 = ee.ImageCollection('projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b')
  .filter(ee.Filter.equals('month', '07'))
  // .map(function(img) {return img.int16()})
  .mosaic();
var dw_counts_plain_gcs_08 = ee.ImageCollection('projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b')
  .filter(ee.Filter.equals('month', '08'))
  // .map(function(img) {return img.int16()})
  .mosaic();
var dw_counts_plain_gcs_09 = ee.ImageCollection('projects/akveg-map/assets/dynamic_world_metrics/s2_dw_monthly_counts_mgrs_v20250414b')
  .filter(ee.Filter.equals('month', '09'))
  // .map(function(img) {return img.int16()})
  .mosaic();

print('dw_counts_plain_gcs_07', dw_counts_plain_gcs_07);

//////////////////////////////////
// Summarize monthly MGRS tiles
var dw_counts_plain_gcs_56789 = ee.ImageCollection([
  dw_counts_plain_gcs_05, 
  dw_counts_plain_gcs_06, 
  dw_counts_plain_gcs_07, 
  dw_counts_plain_gcs_08,
  dw_counts_plain_gcs_09,
  ])
  .sum();
  
Map.addLayer(dw_counts_plain_gcs_56789, {}, 'dw_counts_plain_gcs_56789', false);
Map.addLayer(dw_counts_plain_gcs_56789.geometry(), {}, 'dw_counts_plain_gcs_56789 bnds', false);

var dw_counts = dw_counts_plain_gcs_56789.select('^n_.*'); //select all bands that start in prefix)  

var dw_n = dw_counts.reduce(ee.Reducer.sum()).rename('n');
var dw_n_nonsnow = dw_n.subtract(dw_counts.select('n_snow_and_ice')).rename('n_nonsnow');

var dw_pct_snowfree = dw_counts
  .select(dw_counts.bandNames().filter(ee.Filter.neq('item', 'n_snow_and_ice')))
  .divide(dw_n_nonsnow)
  .multiply(100)
  .regexpRename('^n_', 'pct_nonsnow_');

var dw_pct_snow = dw_counts
  .select('n_snow_and_ice')
  .divide(dw_n)
  .multiply(100)
  .rename('pct_snow');
  
var waterTotal = dw_pct_snowfree.select('pct_nonsnow_water').add(dw_pct_snowfree.select('pct_nonsnow_flooded_vegetation')).rename('pct_nonsnow_water_and_flooded');
var dw_pct = dw_pct_snowfree
  // .addBands(waterTotal)
  .addBands(dw_pct_snow);

Map.addLayer(dw_pct.updateMask(dw_pct.select('pct_nonsnow_shrub_and_scrub','pct_nonsnow_tree','pct_nonsnow_grass').reduce(ee.Reducer.sum()).divide(100)), {min:0, max:100, bands:['pct_nonsnow_shrub_and_scrub','pct_nonsnow_tree','pct_nonsnow_grass']}, 'dw_p_snowfree shrub/tree/grass plain gcs 56789', true);
Map.addLayer(dw_pct.updateMask(dw_pct.select('pct_nonsnow_flooded_vegetation','pct_nonsnow_water').reduce(ee.Reducer.sum()).divide(100)), {min:0, max:100, bands:['pct_nonsnow_flooded_vegetation','pct_nonsnow_flooded_vegetation','pct_nonsnow_water']}, 'dw_p_snowfree allWater/flooded/water plain gcs 56789', true);

//Extract Dominant DW class for each pixel
// var bandNames = dw_p_snowfree.bandNames();
var arrayImage = dw_counts.toArray();
var maxValue = arrayImage.arrayReduce({reducer: ee.Reducer.max(), axes: [0]});
var maxBandIndex = arrayImage.arrayArgmax();

var modal_dw = maxBandIndex.arrayFlatten([['max_band_index']]).rename('modal_dw_class');
var modal_count = maxValue.arrayGet([0]).rename('modal_dw_class_count');
var modal_pct = modal_count
  .divide(dw_n)
  .multiply(100)
  .rename('pct_modal_dw');

Map.addLayer(modal_dw, dwVisParams, 'snowfree dw modal class gcs', false);
Map.addLayer(modal_pct, {min:0, max:100}, 'modal_pct', false);

//Extract Dominant non-snow DW class for each pixel
// var bandNames = dw_p_snowfree.bandNames();
var arrayImage = dw_counts
  .select(dw_counts.bandNames().filter(ee.Filter.neq('item', 'n_snow_and_ice')))
  .addBands(dw_counts.select('n_water').gte(0).rename('n_snow_and_ice'))
  .toArray();
var maxValue = arrayImage.arrayReduce({reducer: ee.Reducer.max(), axes: [0]});
var maxBandIndex = arrayImage.arrayArgmax();

var modal_nonsnow_dw = maxBandIndex.arrayFlatten([['max_band_index']]).rename('modal_nonsnow_dw_class');
var modal_nonsnow_count = maxValue.arrayGet([0]).rename('modal_nonsnow_dw_class_count');
var modal_nonsnow_pct = modal_nonsnow_count
  .divide(dw_n_nonsnow)
  .multiply(100)
  .rename('pct_modal_nonsnow_dw');

Map.addLayer(modal_nonsnow_dw, dwVisParams, 'snowfree dw modal class gcs', false);
Map.addLayer(modal_nonsnow_pct, {min:0, max:100}, 'modal_nonsnow_pct', false);

var dw_metrics = dw_pct.addBands(modal_pct).addBands(modal_nonsnow_pct).addBands(modal_dw).addBands(modal_nonsnow_dw).addBands(dw_n);
Map.addLayer(dw_metrics, {min:0, max:100, bands:['pct_nonsnow_shrub_and_scrub','pct_nonsnow_tree','pct_nonsnow_grass']}, 'dw metrics 56789 nomask', false);

var dw_metrics_export = dw_metrics.round().min(ee.Image(254)).byte();
Map.addLayer(dw_metrics_export, {min:0, max:100, bands:['pct_nonsnow_shrub_and_scrub','pct_nonsnow_tree','pct_nonsnow_grass']}, 'dw metrics 56789 nomask byte', false);

var region = ee.FeatureCollection('projects/akveg-map/assets/study_areas/MentastaLake_MapDomain_3338');

Export.image.toCloudStorage({
  image: dw_metrics_export,
  description: 's2_dw_counts_56789_'+'MentastaLake'+'_'+version,
  bucket: 'akveg-data',
  fileNamePrefix: 's2_dw_v1_metrics/s2_dw_pct_akalb_sa_'+version+'/s2_dw_pct_56789_akalb_MentastaLake_'+version,
  // dimensions: dimensions,
  // region: ee.Feature(region).bounds(0.001, 'EPSG:'+epsg),
  region: region.bounds(0.001, crs),
  crs: crs,
  // crs: crs,
  crsTransform: transform,
  maxPixels: 1e12,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true, noData: 255},
});

throw('stop');

// Runs monthly water metrics by AKVEG tile
function dw_monthly_water_metrics(regionName) {
  print(regionName);
  var region = akveg_100km
    .filter(ee.Filter.equals('gridID', regionName)).first();
  var clipper = region.geometry().intersection(sa_clip);
  // var region = ee.Feature(seward_box);
  // var clipper = seward_box;
  
  if (verbose) {  Map.addLayer(region.geometry(), {}, 'region', false);}
  if (verbose) {  Map.addLayer(clipper, {}, 'clipper', false);}

  var epsg = region.get('epsg').getInfo();
  var transform = region.getString('transform').getInfo();
  var dimensions = region.getString('dimensions').getInfo();
  print(epsg, transform, dimensions);
  // var epsg = 3338;
  // print(region, epsg);
  var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    // .filter(ee.Filter.calendarRange(startDoy, endDoy, 'day_of_year'))
    .filterBounds(region.geometry())
    .linkCollection(s2_l1c, [], ['SENSING_ORBIT_NUMBER'])
    // .linkCollection(csPlus, ['cs', 'cs_cdf'])
    .map(function(img) {
      var doy = img.date().getRelative('day', 'year').add(1);
      // var doySnowYear = ee.Number(doy).add(doy.lt(snowYearTransitionDoy).multiply(365));
      // return img.addBands(ee.Image.constant(doySnowYear).rename('doy').int16())
      return img.addBands(ee.Image.constant(doy).rename('doy').int16())
        .set('doy', doy);
    });

  // Apply sun angle doy mask
  if (sunElevationMask) {
    return dw
    .map(function(img) {return img.updateMask(img.gte(earliest_solar_doy))})
    .map(function(img) {return img.updateMask(img.lte(latest_solar_doy))});
  }
  
  // if (verbose) {  print('dw before daily mosaic', dw); }
  dw = dailyMosaics(dw);
  if (verbose) {  print('dw after daily mosaic', dw); }
  // if (verbose) { print('dw bounds', dw.size(), dw.limit(5));}
  if (verbose) {Map.addLayer(dw, {}, 'dw after daily mosaic', false); }
  dw_water = dw.select('label').map(function(img) {
    return img
      .addBands(img.select('label').eq(0).selfMask().rename('water'))
      .addBands(img.select('label').eq(3).selfMask().rename('flooded_vegetation'))
      .addBands(img.select('label').eq(8).selfMask().rename('snow_and_ice'))
      .addBands(img.select('label').remap(
        [0,1,2,3,4,5,6,7,8],
        [0,1,1,0,1,1,1,1,0]).selfMask().rename('nonwater'))
      .select('water','flooded_vegetation','snow_and_ice','nonwater')
  });

  var dw_water = dw_water
    .filter(ee.Filter.calendarRange(5,5,'month'))
    .count()
    .regexpRename('^', 'n_water_05_')
    .addBands(dw_water
      .filter(ee.Filter.calendarRange(6,6,'month'))
      .count()
      .regexpRename('^', 'n_water_06_'))
    .addBands(dw_water
    .filter(ee.Filter.calendarRange(7,7,'month'))
    .count()
    .regexpRename('^', 'n_water_07_'))
    .addBands(dw_water
    .filter(ee.Filter.calendarRange(8,8,'month'))
    .count()
    .regexpRename('^', 'n_water_08_'))
    .addBands(dw_water
    .filter(ee.Filter.calendarRange(9,9,'month'))
    .count()
    .regexpRename('^', 'n_water_09_'));
  print(dw_water);
  Map.addLayer(dw_water.unmask(0), {min:0, max:10, bands:['n_water_06_water','n_water_07_water','n_water_08_water']}, 'dw_water monthly');
  //empty image to ensure there is at least one image in filtered ic
  // var dwLabelEmptyCollection = ee.ImageCollection(dwLabelTimeSeries.first().updateMask(ee.Image(0)));
  if (exportAsset) {
    Export.image.toAsset({
    image: dw_water.uint16().unmask(0).clip(clipper),//.updateMask(mask),//.unmask(0),
    description: 's2_dw_monthly_water_v20240709_'+regionName, 
    assetId: 'projects/akveg-map/assets/dynamic_world_metrics/s2_monthly_water_counts_v20240709/s2_dw_monthly_water_v20240709_'+regionName,
    // region: clipper,
    dimensions: dimensions,
    crs: 'EPSG:'+epsg,
    crsTransform: transform,
    maxPixels: 1e12,
  });
  }

  return dw_counts;
}
