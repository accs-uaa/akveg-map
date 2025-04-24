// Copied from GEE 2025-04-23
// v20250414
// Revisited and fixed image edge artifacts on export
// (Required math to put clip polygon bounding box on the snap raster)

// v20250321
// Use updated minimal MGRS tiles extents to generate interim outputs using only one MGRS tile of S2 at a time
// Minimal means the overlap between adjacent tiles is minimized
// Used ArcPro Remove Overlaps (thiessen) followed by 100 m geodesic buffer.

// v20250319
// Regenerate lc and seasonal water frequency outputs with cut-off date of 2024-12-31
// Export to GCS for full AKVeg study area includind adjacent Yukon

// v20240709
// Seasonal water frequency metrics for water and flooded_vegetation classes
// Stored as raw counts by month (May-Sept)
// snow_and_ice class is ambiguous 
// So typically water frequency will be calculated as count of water label (and/or flooded_vegetation) divided by count of all non-snow labels

// v20240626
// Uses parsed/standardized snow metrics result to partition observations into snow and snow-free season
// Raw calculations of count of each DW class within within snow-free and snow season (to avoid potential lc artifacts during snow season low light)

// https://code.earthengine.google.com/?scriptPath=users%2Fmmacander%2Fakveg_map%3Adynamic_world_metrics%2Fs2_dynamic_world_lc_metrics_v20250414_mgrs.js
// https://code.earthengine.google.com/16999ded2815d3e4dbeb71f0198b1a6a
// 05b_data_dynamic_world/s2_dynamic_world_lc_metrics_v20250414_mgrs.js

var version = 'v20250414';

var verbose = false, 
  exportGCS = true;

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

var s2_l1c = ee.ImageCollection("COPERNICUS/S2_HARMONIZED");

var s2_l1c_props = ee.List([
  "DATATAKE_IDENTIFIER",
  "SPACECRAFT_NAME",
  "GENERATION_TIME",
  "DATASTRIP_ID",
  "PROCESSING_BASELINE",
  "SENSING_ORBIT_NUMBER",
  "SENSING_ORBIT_DIRECTION",
  "GRANULE_ID",
  "MGRS_TILE",
  "PRODUCT_ID",
  "DATATAKE_TYPE",
]);

print(s2_l1c_props);

////////////////////////
// Study Areas

// Study area for AK-VegMap, including Yukon portion and SE AK
var akveg_akYuk = ee.FeatureCollection('projects/akveg-map/assets/regions/AlaskaYukon_MapDomain_3338_v20230330');
var sa = akveg_akYuk;

// Use MGRS tiles (minimal overlap version)
var akveg_100km = ee.FeatureCollection('projects/akveg-map/assets/tiles/AKVEG_100km_tiles_3338_v20230325');
var s2_mgrs = ee.FeatureCollection('projects/akveg-map/assets/tiles/s2_mgrs_for_gee_akveg_v20250321_3338_remOvTh_gbuff100m');

Map.addLayer(s2_mgrs, {}, 's2_mgrs', false);

// Larger study area to use for clipping
// Removes unneeded ocean but leaves in adjacent land so tiles can be used for later analyses
// with a larger study area, e.g. ABoVE domain
var sa_clip = ee.FeatureCollection('projects/akveg-map/assets/regions/ABoVE_Alaska_3parts_Buff10km_BuffMinus5km_Simplify5km_4326_v20230328')
  .union(1).first().geometry();

// Set of MGRS tiles that overlap study area
var s2_mgrs_sa = s2_mgrs
  .filterBounds(sa);
Map.addLayer(s2_mgrs_sa, {}, 's2_mgrs_sa');
print(s2_mgrs_sa);

////////////////////
// Get tile list
// UTM / EPSG codes 32659, 32660, 32601 to 32608
// Uncomment one EPSG filter row at a time
// Returns a manageable number of tiles to run at once 
// (using Run All! button from Open Earth Engine Extension)
var regionList = s2_mgrs
  .filterBounds(sa)
  // .filter(ee.Filter.inList('rowNum', rows))
  .filter(ee.Filter.lte('epsg', '32603')).toList(200)
  // .filter(ee.Filter.eq('epsg', '32604')).toList(200)
  // .filter(ee.Filter.eq('epsg', '32605')).toList(200)
  // .filter(ee.Filter.eq('epsg', '32606')).toList(200)
  // .filter(ee.Filter.eq('epsg', '32607')).toList(200)
  // .filter(ee.Filter.gte('epsg', '32608')).toList(200)
  .map(function(f) {return ee.Feature(f).getString('name')})

print(regionList);
// For debug/test specify one manually
// regionList = ee.List(['06VUQ']);
regionList = ee.List(['03UUV']); // Error on month 05 on first run
// regionList = ee.List(['01UCS']); // Error on month 06 on first run

print('tiles_sa subset size', regionList.size(), regionList);

// Calculate Monthly Metrics by tile
// Save to Asset
var run_monthly_metrics = true;
if (run_monthly_metrics) {
var result_run_monthly_metrics = regionList
  // .slice(0,1)  //uncomment to run full set
  .getInfo().map(dw_monthly_metrics);
}

///////////////////////
///////////////////////
// FUNCTIONS

// Runs monthly metrics by tile
// Save as monthly GeoTIFF
function dw_monthly_metrics(regionName) {
  print(regionName);
  var region = s2_mgrs
    .filter(ee.Filter.equals('name', regionName)).first();
  var clipper = region.geometry().intersection(sa_clip);
  // var region = ee.Feature(seward_box);
  // var clipper = seward_box;
  
  if (verbose) {  Map.addLayer(region.geometry(), {}, 'region', false);}
  if (verbose) {  Map.addLayer(clipper, {}, 'clipper', false);}

  var epsg = region.get('epsg').getInfo();
  var transform = region.getString('transform').getInfo();
  var dimensions = region.getString('dimensions').getInfo();
  
  // var region_proj = ee.Feature(region).transform('EPSG:'+epsg, 0.1);
  // var clipper_proj = clipper.transform('EPSG:'+epsg, 0.1);
  if (verbose) {    print(epsg, transform, dimensions); }
  
  var crs = ee.Projection('EPSG:'+epsg, ee.List([10,0,0,0,-10,0]));
  var scale = crs.nominalScale();
  
  if(verbose) {print('crs, scale', crs, scale);}
  
  // Compute bounding box aligned to pixel grid
  var bounds = ee.Feature(region).bounds(0.001, crs);  // bounds in target projection
  if(verbose) {print(bounds);}
  if(verbose) {print(bounds.geometry().coordinates());}
  var snapped = ee.List(bounds
    .geometry()
    .coordinates()
    .get(0))
    .map(function(coord) {
      var x = ee.List(coord).get(0);
      var y = ee.List(coord).get(1);
      return [ee.Number(x).divide(scale).floor().multiply(scale),
              ee.Number(y).divide(scale).floor().multiply(scale)];
    });
  
  if(verbose) {print(snapped);}
  var snappedRegion = ee.Geometry.Polygon({
    coords: [snapped], 
    proj: crs,
    geodesic: false,
    evenOdd: true});
  if(verbose) {print(snappedRegion);}
  
  dw_monthly_metrics_monthly(regionName, 5, region, snappedRegion, clipper, epsg, transform, dimensions);
  dw_monthly_metrics_monthly(regionName, 6, region, snappedRegion, clipper, epsg, transform, dimensions);
  dw_monthly_metrics_monthly(regionName, 7, region, snappedRegion, clipper, epsg, transform, dimensions);
  dw_monthly_metrics_monthly(regionName, 8, region, snappedRegion, clipper, epsg, transform, dimensions);
  dw_monthly_metrics_monthly(regionName, 9, region, snappedRegion, clipper, epsg, transform, dimensions);
  return regionName;
  }
  
function dw_monthly_metrics_monthly(regionName, monthNum, region, snappedRegion, clipper, epsg, transform, dimensions) {
  // var epsg = 3338;
  // print(region, epsg);
  var monthNum0 = ee.Number(monthNum).format('%02d').getInfo();
  var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
    // .filter(ee.Filter.calendarRange(startDoy, endDoy, 'day_of_year'))
    .filterBounds(region.geometry())
    // .filterBounds(region)
    .filter(ee.Filter.calendarRange(monthNum, monthNum, 'month'))
    .select('label')
    .linkCollection(s2_l1c, [], s2_l1c_props)
    // .linkCollection(s2_l1c, [], ['SENSING_ORBIT_NUMBER','MGRS_TILE'])
    .filter(ee.Filter.eq('MGRS_TILE', regionName));

  if (verbose) {  print('dw before daily mosaic', dw); }
  
  // dw = dailyMosaics(dw);
  // if (verbose) {  print('dw after daily mosaic', dw); }
  
  // Remove duplicates without mosaic
  // Works for single MGRS tile only
  // https://gis.stackexchange.com/questions/336257/filter-out-duplicate-sentinel-2-images-form-earth-engine-image-collection-by-dat
  // Generate a List to compare dates
  var lista = dw.toList(dw.size())
  
  // Add in the end of the list a dummy image
  // set it to a date (1 milli into unix time) that won't match even if there is only one date present
  var imagen = ee.Image(lista.get(0))
    .set('system:time_start', 1); 
  lista = lista.add(imagen)
  
  var detectar_duplicador = function(imagen){
    var esduplicado = ee.String("")
    var numero = lista.indexOf(imagen)
    var imagen1 = ee.Image(lista.get(numero.add(1)))
    //Compare the image(0) in the ImageCollection with the image(1) in the List
    var fecha1 = imagen.date().format("Y-M-d")
    var fecha2 = imagen1.date().format("Y-M-d")
    var estado = ee.Algorithms.IsEqual(fecha1,fecha2)
    esduplicado = ee.String(ee.Algorithms.If({condition: estado, 
                    trueCase: "duplicate",
  
                    falseCase: "not duplicate"}));
  
      return imagen.set({"duplicate": esduplicado})
  }
  
  dw = dw.map(detectar_duplicador)
  dw = dw.filter(ee.Filter.eq("duplicate","not duplicate"));
  if (verbose) {  print('dw after duplicate removal', dw); }
  
  // if (verbose) { print('dw bounds', dw.size(), dw.limit(5));}
  if (verbose) {Map.addLayer(dw, {}, 'dw after daily mosaic', false); }
  
  var dw_binary = dw.map(function(img) {
    return img.select('label').rename('water').eq(0)
      .addBands(img.select('label').rename('tree').eq(1))
      .addBands(img.select('label').rename('grass').eq(2))
      .addBands(img.select('label').rename('flooded_vegetation').eq(3))
      .addBands(img.select('label').rename('crops').eq(4))
      .addBands(img.select('label').rename('shrub_and_scrub').eq(5))
      .addBands(img.select('label').rename('built').eq(6))
      .addBands(img.select('label').rename('bare').eq(7))
      .addBands(img.select('label').rename('snow_and_ice').eq(8))
      .selfMask();
  });

  var dw_counts = dw_binary
    .count()
    .regexpRename('^', 'n_');
    // .set('system:time_start', ee.Date.fromYMD(2001, monthNum, 1).millis(), 
    //     'system:time_end',   ee.Date.fromYMD(2001, monthNum, 1).advance(1,'month').millis());
  if (verbose) { print(dw_counts); }
  if (verbose) { Map.addLayer(dw_counts.unmask(0), {min:0, max:10}, 'dw_counts monthly '+monthNum ); }
  
  //empty image to ensure there is at least one image in filtered ic
  // var dwLabelEmptyCollection = ee.ImageCollection(dwLabelTimeSeries.first().updateMask(ee.Image(0)));
  if(exportGCS) {
    // var exportImage = dw_counts.unmask(0, false).clip(clipper).int16();
    // var exportImageMask = exportImage.select(0).mask().eq(1);
    // exportImage = exportImage.updateMask(exportImageMask).unmask(65535, false);
    var exportImage = dw_counts
      .unmask(0, false)
      // .reproject(crs, transform)
      .clip(clipper)
      .unmask(65535, false)
      .uint16();
    // var exportImageMask = exportImage.select(0).mask().eq(1);
    // exportImage = exportImage.updateMask(exportImageMask).unmask(65535, false);
    if (verbose) {
      Map.addLayer(exportImage, {}, 'exportImage', false);
      Map.addLayer(snappedRegion, {}, 'snappedRegion', true);
    }
    Export.image.toCloudStorage({
      image: exportImage,
      description: 's2_dw_counts_month'+monthNum0+'_'+regionName+'_'+version,
      bucket: 'akveg-data',
      fileNamePrefix: 's2_dw_v1_metrics/s2_dw_monthly_counts_mgrs_'+version+'b/s2_dw_counts_mgrs_month'+monthNum0+'_'+regionName+'_'+version,
      // dimensions: dimensions,
      // region: ee.Feature(region).bounds(0.001, 'EPSG:'+epsg),
      region: snappedRegion,
      crs: 'EPSG:'+epsg,
      // crs: crs,
      crsTransform: transform,
      maxPixels: 1e12,
      fileFormat: 'GeoTIFF',
      formatOptions: {cloudOptimized: true, noData: 65535},
    });
  }

  return dw_counts;
}
