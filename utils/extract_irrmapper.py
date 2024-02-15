import ee

IRR = 'projects/ee-dgketchum/assets/IrrMapper/IrrMapperComp'


def get_irrigation(fields, desc, debug=False):
    plots = ee.FeatureCollection(fields)
    irr_coll = ee.ImageCollection(IRR)

    _selectors = ['FID']
    first = True

    area, irr_img = ee.Image.pixelArea(), None

    for year in range(1987, 2022):

        irr = irr_coll.filterDate('{}-01-01'.format(year),
                                  '{}-12-31'.format(year)).select('classification').mosaic()

        irr = irr.lt(1)

        _name = 'irr_{}'.format(year)
        _selectors.append(_name)

        if first:
            irr_img = irr.rename(_name)
            first = False
        else:
            irr_img = irr_img.addBands(irr.rename(_name))

    means = irr_img.reduceRegions(collection=plots,
                                  reducer=ee.Reducer.mean(),
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


if __name__ == '__main__':
    ee.Authenticate()
    ee.Initialize(project='ee-dgketchum')

    project = '047_lake'
    fields_ = 'users/dgketchum/fields/lake_co_wudr_15FEB2024'

    description = '{}_irr'.format(project)
    get_irrigation(fields_, description, debug=True)


# ========================= EOF ====================================================================
