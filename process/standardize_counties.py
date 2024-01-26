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
        [('FID', 'str'), ('SOURCECODE', 'str'), ('COUNTY_NO', 'str'), ('COUNTYNAME', 'str'),
         ('ITYPE', 'int'), ('USAGE', 'int'), ('MAPPEDBY', 'str')]),
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


def compile_shapes(out_shape, shapes):
    out_features = []
    out_geometries = []
    err = False
    first = True
    err_count = 0
    for _file, code in shapes:
        if first:
            with fiona.open(_file) as src:
                print(_file, src.crs)
                meta = src.meta
                meta['schema'] = {'type': 'Feature', 'properties': OrderedDict(
                    [('fid', 'int:9'), ('SOURCECODE', 'str')]), 'geometry': 'Polygon'}
                raw_features = [x for x in src]
            for f in raw_features:
                f['properties']['SOURCECODE'] = code
                try:
                    base_geo = Polygon(f['geometry']['coordinates'][0])
                    out_geometries.append(base_geo)
                    out_features.append(f)
                except Exception as e:
                    try:
                        base_geo = Polygon(f['geometry']['coordinates'][0])
                        out_geometries.append(base_geo)
                        out_features.append(f)
                    except Exception as e:
                        err_count += 1
            print('base geometry errors: {}'.format(err_count))
            first = False
        else:
            f_count = 0
            add_err_count = 0
            with fiona.open(_file) as src:
                print(_file, src.crs)
                for feat in src:
                    inter = False
                    f_count += 1
                    feat['properties']['SOURCECODE'] = code

                    try:
                        poly = Polygon(feat['geometry']['coordinates'][0])
                    except Exception as e:
                        try:
                            poly = Polygon(feat['geometry']['coordinates'][0][0])
                        except Exception as e:
                            add_err_count += 1
                            err = True
                            break
                    for _, out_geo in enumerate(out_geometries):
                        if poly.centroid.intersects(out_geo):
                            inter = True
                            break
                    if not inter and not err:
                        out_features.append(feat)
                        out_geometries.append(poly)

                    if f_count % 1000 == 0:
                        if f_count == 0:
                            pass
                        else:
                            print(f_count, '{} base features'.format(len(out_features)))
                print('added geometry errors: {}'.format(add_err_count))

    with fiona.open(out_shape, 'w', **meta) as output:
        ct = 0
        for feat in out_features:
            feat = {'type': 'Feature', 'properties': OrderedDict(
                [('OBJECTID', ct), ('SOURCECODE', feat['properties']['SOURCECODE'])]),
                    'geometry': feat['geometry']}
            if not feat['geometry']:
                print('None Geo, skipping')
            elif not shape(feat['geometry']).is_valid:
                print('Invalid Geo, skipping')
            else:
                output.write(feat)
                ct += 1
        print('wrote {}'.format(out_shape))


if __name__ == '__main__':
    d = '/media/research/IrrigationGIS/Montana'
    if not os.path.isdir(d):
        d = '/home/dgketchum/data/IrrigationGIS/Montana'

    s = os.path.join(d, 'statewide_irrigation_dataset/statewide_irrigation_dataset_provisional_25JAN2024')
    o = os.path.join(d, 'statewide_irrigation_dataset/statewide_irrigation_dataset_provisional_25JAN2024.shp')
    merge_counties(s, o)
# ========================= EOF ====================================================================
