var y = 2021;
var d = y + '-01-01';
var e = y + '-12-31';

var table = ee.FeatureCollection('users/dgketchum/itype/mt_dryland');
var table2 = ee.FeatureCollection('users/dgketchum/itype/mt_itype_2019');

var naip = ee.ImageCollection('USDA/NAIP/DOQQ')
    .filterDate('2017-01-01', '2019-12-31').mosaic();
var vizParams = {
  min: 0,
  max: 255,
  gamma: [1.5, 1, 1]
};
Map.addLayer(naip, vizParams, 'NAIP', false);

// Calculate NDVI for each Landsat collection
var ndvi_l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR').map(function(image) {
  return image.select().addBands(image.normalizedDifference(['B4', 'B3']))});
var ndvi_l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').map(function(image) {
  return image.select().addBands(image.normalizedDifference(['B4', 'B3']))});
var ndvi_l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').map(function(image) {
  return image.select().addBands(image.normalizedDifference(['B4', 'B3']))});
var ndvi_l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').map(function(image) {
  return image.select().addBands(image.normalizedDifference(['B5', 'B4']))});
var ndvi = ndvi_l4.merge(ndvi_l5).merge(ndvi_l7).merge(ndvi_l8);

// if year < 2012 set ndvi_l5, if year = 2012 set ndvi_l7, if year > 2012 set ndvi_l8
var ndvi_series = ndvi.filterDate(y - 4 + '-01-01', y + '-12-31').select('nd');
var ndvi_cy = ndvi.filterDate(y + '-08-15', y + '-10-31').select('nd');
var ndvi_stats = ndvi_cy.reduce(ee.Reducer.mean().combine({
          reducer2: ee.Reducer.minMax(),
          sharedInputs: true}));
var ndvi_max = ndvi_stats.select('nd_max');


Map.addLayer(ndvi_max, {min: 0, max: 1, palette: ['red', 'orange', 'white', 'green']} , 'Lst NDVI - Max', false);
Map.addLayer(ndvi_series, {}, 'Lst NDVI Series', false);


var s = 2017 + '-05-01';
var e = 2020 + '-10-01';
var S2 = ee.ImageCollection('COPERNICUS/S2').filterDate(s, e);
var maskcloud1 = function(image) {
var QA60 = image.select(['QA60']);
return image.updateMask(QA60.lt(1));
};
var addNDVI = function(image) {
return image.addBands(image.normalizedDifference(['B8', 'B4']))};
var S2 = S2.map(addNDVI);
var ndvi = S2.select(['nd']);
var std_ndvi = ndvi.reduce(ee.Reducer.stdDev());
var max_ndvi = ndvi.max();

Map.addLayer(max_ndvi, {min: 0, max: 1, palette: ['red', 'orange', 'white', 'green']} , 'Sent NDVI - Max', false);
Map.addLayer(ndvi, {} , 'Sent NDVI Time Series', false);


var empty = ee.Image().byte();
var outlines = empty.paint({
  featureCollection: table,
  width: 2,
  color: 'Irr_2016',
});

var pallette_1 = ['05a900'];
Map.addLayer(outlines, {pallette: pallette_1}, 'Shapefile', false);

