import pandas as pd
import geopandas as gpd

import ee

IRR = 'projects/ee-dgketchum/assets/IrrMapper/IrrMapperComp'


def get_irrigation(fields, desc, debug=False, key='FID', min_years=3):

    irr_min_yr_mask = None
    if min_years:
        irr_coll = ee.ImageCollection(IRR)
        coll = irr_coll.filterDate('1987-01-01', '2009-12-31').select('classification')
        remap = coll.map(lambda img: img.lt(1))
        irr_min_yr_mask = remap.sum().gte(min_years)

    plots = ee.FeatureCollection(fields)
    irr_coll = ee.ImageCollection(IRR)

    _selectors = [key]
    first = True

    area, irr_img = ee.Image.pixelArea(), None

    for year in range(1987, 2024):

        irr = irr_coll.filterDate('{}-01-01'.format(year),
                                  '{}-12-31'.format(year)).select('classification').mosaic()

        irr = irr.lt(1)
        if min_years:
            irr = irr.mask(irr_min_yr_mask)

        _name = 'irr_{}'.format(year)
        _selectors.append(_name)

        if first:
            irr_img = irr.rename(_name)
            first = False
        else:
            irr_img = irr_img.addBands(irr.rename(_name))

    irr_img = irr_img.multiply(area)
    means = irr_img.reduceRegions(collection=plots,
                                  reducer=ee.Reducer.sum(),
                                  scale=30)

    if debug:
        debug = means.filterMetadata('FID', 'equals', 2423).getInfo()

    task = ee.batch.Export.table.toCloudStorage(
        means,
        description=desc,
        bucket='wudr',
        fileNamePrefix=desc,
        fileFormat='CSV',
        selectors=_selectors)

    task.start()
    print(desc)


def infer_irrigation_usage(in_shp, irr_, out_shp):
    irr = pd.read_csv(irr_, index_col='FID')
    df = gpd.read_file(in_shp, index_col='FID')

    def usage(row):
        if row >= 0.75:
            return 3
        elif 0.4 < row < 0.75:
            return 2
        else:
            return 1

    cols = [c for c in irr.columns if int(c.split('_')[1]) in [2018, 2019, 2020, 2021]]
    irr = irr[cols].mean(axis=1)
    irr = irr.apply(lambda x: usage(x))
    match = [i for i in df.index if i in irr.index]
    df.loc[match, 'USAGE'] = irr.loc[match]

    df.to_file(out_shp)


if __name__ == '__main__':
    ee.Authenticate()
    ee.Initialize(project='ee-dgketchum')

    project = '047_lake'
    # fields_ = 'users/dgketchum/fields/lake_co_wudr_15FEB2024'
    fields_ = 'users/dgketchum/boundaries/blackfeet_res'

    description = 'blackfeet_irrmapper'
    get_irrigation(fields_, description, debug=False)

    irr_csv = '/media/research/IrrigationGIS/Montana/geointernship/Lake_047/047_lake_irr.csv'
    s = '/media/research/IrrigationGIS/Montana/geointernship/Lake_047/047_Lake_RDGP.shp'
    o = '/media/research/IrrigationGIS/Montana/geointernship/Lake_047/047_Lake.shp'
    # infer_irrigation_usage(s, irr_csv, o)

# ========================= EOF ====================================================================
