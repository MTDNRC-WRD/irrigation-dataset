import os.path
from collections import OrderedDict

import numpy as np

import fiona
from shapely.geometry import Polygon, shape

FIELDS = ['fid', 'itype', 'usage', 'mapped_by', 'geometry']
DTYPES = [np.int64, str, np.int64, str, Polygon]
NODATA = [None, 'UNK', 1, 'DK', None]


def merge_counties(_dir, out_shp):
    """
    Merge various shapefile objects. This was used to join the standardized county SID shapefiles.
    :param out_shp: str output shapefile path
    :return: none
    """

    file_list = [os.path.join(_dir, x) for x in os.listdir(_dir) if x.endswith('.shp')]

    meta = fiona.open(file_list[0]).meta
    meta['schema'] = {'type': 'Feature', 'properties': OrderedDict(
        [('FID', 'str'), ('SOURCECODE', 'str'), ('COUNTY_NO', 'int'), ('COUNTYNAME', 'str'),
         ('ITYPE', 'str'), ('USAGE', 'int'), ('MAPPEDBY', 'str')]),
                      'geometry': 'Polygon'}

    with fiona.open(out_shp, 'w', **meta) as output:
        ct = 0
        none_geo = 0
        inval_geo = 0
        for s in file_list:
            print(os.path.basename(s))
            splt = s.split('/')[-1].strip('.shp').split('_')
            co_no, co_name = splt[0], '_'.join(splt[1:])
            for feat in fiona.open(s):
                if not feat['geometry']:
                    none_geo += 1
                elif not shape(feat['geometry']).is_valid:
                    inval_geo += 1
                else:
                    area = shape(feat['geometry']).area
                    if area == 0.0:
                        raise AttributeError
                    ct += 1

                    # TODO: classify sourcecode in standardization procedure
                    # source = feat['properties']['SOURCECODE']
                    source = 'MTDNRC'
                    fid = feat['properties']['fid']

                    itype = feat['properties']['itype']
                    itype = itype.upper()[0]
                    if itype not in ['P', 'S', 'F']:
                        itype = 'UNK'

                    usage = feat['properties']['usage']
                    mapped_by = feat['properties']['mapped_by']
                    feat = {'type': 'Feature', 'properties': OrderedDict(
                        [('FID', fid),
                         ('SOURCECODE', source),
                         ('COUNTY_NO', co_no),
                         ('COUNTYNAME', co_name),
                         ('ITYPE', itype),
                         ('USAGE', usage),
                         ('MAPPEDBY', mapped_by)]),
                            'geometry': feat['geometry']}
                    output.write(feat)

    print('wrote {}, {}, {} none, {} invalid'.format(out_shp, ct, none_geo, inval_geo))


if __name__ == '__main__':
    d = '/media/research/IrrigationGIS/Montana'
    if not os.path.isdir(d):
        d = '/home/dgketchum/data/IrrigationGIS/Montana'

    s = os.path.join(d, 'statewide_irrigation_dataset/statewide_irrigation_dataset_15FEB2024')
    o = os.path.join(d, 'statewide_irrigation_dataset/statewide_irrigation_dataset_15FEB2024.shp')
    merge_counties(s, o)
# ========================= EOF ====================================================================
