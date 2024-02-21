import pandas as pd
import geopandas as gpd

import ee

IRR = 'projects/ee-dgketchum/assets/IrrMapper/IrrMapperComp'


def get_cdl(fields, desc, key='FID'):
    plots = ee.FeatureCollection(fields)
    crops, first = None, True
    cdl_years = [x for x in range(2018, 2023)]

    _selectors = [key]

    for y in cdl_years:

        image = ee.Image('USDA/NASS/CDL/{}'.format(y))
        crop = image.select('cropland')
        _name = 'crop_{}'.format(y)
        _selectors.append(_name)
        if first:
            crops = crop.rename(_name)
            first = False
        else:
            crops = crops.addBands(crop.rename(_name))

    modes = crops.reduceRegions(collection=plots,
                                reducer=ee.Reducer.mode(),
                                scale=30)

    out_ = 'cdl_{}'.format(desc)
    task = ee.batch.Export.table.toCloudStorage(
        modes,
        description=out_,
        bucket='wudr',
        fileNamePrefix=out_,
        fileFormat='CSV',
        selectors=_selectors)

    task.start()


if __name__ == '__main__':
    project = '047_lake'
    fields_ = 'users/dgketchum/fields/lake_co_wudr_15FEB2024'

    description = '{}_irr'.format(project)
    # get_cdl(fields_, description, debug=True)

# ========================= EOF ====================================================================
