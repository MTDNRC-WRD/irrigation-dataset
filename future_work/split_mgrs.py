import os
from collections import OrderedDict

import fiona
from rtree import index
from shapely.geometry import shape


def split_by_mgrs(shapes, tiles_path, out_dir):
    """attribute source code, split into MGRS tiles"""
    out_features = []
    tiles = []
    idx = index.Index()
    in_features = []
    for _file, code in shapes:
        with fiona.open(_file) as src:
            print(_file, src.crs)
            meta = src.meta
            meta['schema'] = {'type': 'Feature', 'properties': OrderedDict(
                [('OBJECTID', 'int:9'), ('SOURCECODE', 'str')]), 'geometry': 'Polygon'}
            [in_features.append((code, f)) for f in src]

    with fiona.open(tiles_path, 'r') as mgrs:
        [idx.insert(i, shape(tile['geometry']).bounds) for i, tile in enumerate(mgrs)]
        for code, f in in_features:
            try:
                point = shape(f['geometry']).centroid
                for j in idx.intersection(point.coords[0]):
                    if point.within(shape(mgrs[j]['geometry'])):
                        tile = mgrs[j]['properties']['MGRS_TILE']
                        if tile not in tiles:
                            tiles.append(tile)
                        break
                f['properties'] = OrderedDict([('SOURCECODE', code),
                                               ('MGRS_TILE', tile)])
                out_features.append(f)
            except AttributeError as e:
                print(e)

    codes = [x[1] for x in shapes]
    for code in codes:
        for tile in tiles:
            dir_ = os.path.join(out_dir, tile)
            if not os.path.isdir(out_dir):
                os.mkdir(out_dir)
            if not os.path.isdir(dir_):
                os.mkdir(dir_)
            file_name = '{}_{}'.format(tile, code)
            print(dir_, file_name)
            out_shape = os.path.join(dir_, '{}.shp'.format(file_name))
            with fiona.open(out_shape, 'w', **meta) as output:
                ct = 0
                for feat in out_features:
                    if feat['properties']['MGRS_TILE'] == tile and feat['properties']['SOURCECODE'] == code:
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
            if ct == 0:
                [os.remove(os.path.join(dir_, x)) for x in os.listdir(dir_) if file_name in x]
                print('Not writing {}'.format(file_name))
            else:
                print('wrote {}, {} features'.format(out_shape, ct))


if __name__ == '__main__':

    d = '/media/research/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'
    if not os.path.isdir(d):
        d = '/home/dgketchum/data/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'

    sid = os.path.join(d, 'sid', 'statewide_irrigation_dataset_15FEB2024.shp')
    clu = os.path.join(d, 'clu_wgs', 'mt.shp')

    l = [(sid, 'MTDNRC'), (clu, 'CLU')]
    mgrs = os.path.join(d, 'MGRS')
    split = os.path.join(mgrs, 'split')

    tiles_shp = os.path.join(d, 'MGRS_TILE.shp')

    split_by_mgrs(l, tiles_shp, split)
# ========================= EOF ====================================================================
