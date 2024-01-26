import os

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from utils.county_codes import county_codes

FIELDS = ['fid', 'itype', 'usage', 'mapped_by', 'geometry']
DTYPES = [np.int64, str, np.int64, str, Polygon]
NODATA = [None, 'UNK', 1, 'DK', None]


def standardize_county_shapefiles(root, out_dir):
    codes = county_codes()

    files = [os.path.join(root, x) for x in os.listdir(root) if x.endswith('.shp')]

    for co, v in codes.items():

        print(co)
        shp = [x for x in files if co in x]
        if len(shp) != 1:
            print(co, v['NAME'], 'is missing')
            continue

        df = gpd.read_file(shp[0])
        cols = ['_'.join(x.lower().split(' ')) for x in df.columns]

        if not all([c in cols for c in FIELDS]):
            missing = [c for c in FIELDS if c not in cols]
            print(co, v['NAME'], 'has missing attributes: {}'.format(missing))
            print('attributes: {}\n'.format(cols))
            continue

        df.columns = cols
        df = df[FIELDS]

        for i, c in enumerate(FIELDS):
            try:
                df[c] = df[c].astype(DTYPES[i])
            except pd.errors.IntCastingNaNError:
                try:
                    if np.count_nonzero(np.isnan(df[c].values)) > 0:
                        df[c].fillna(NODATA[i], inplace=True)
                except ValueError as e:
                    if c == 'fid':
                        df[c] = list(range(df.shape[0]))
                    else:
                        raise TypeError('Unhandled exception ({}) for {} in {} {}'.format(e, c, co, v['NAME']))

            except TypeError as e:
                if c == 'geometry':
                    pass
                else:
                    raise TypeError('Unhandled exception ({}) for {} in {} {}'.format(e, c, co, v['NAME']))

        _file = os.path.join(out_dir, '{}_{}.shp'.format(co, v['NAME'].replace(' ', '_')))
        df.to_file(_file)


if __name__ == '__main__':
    d = '/media/research/IrrigationGIS/Montana/geointernship/progress/wgs'
    # o = '/media/research/IrrigationGIS/Montana/geointernship/standardized_county'
    o = '/media/research/IrrigationGIS/Montana/dalby/statewide_irrigation_dataset_provisional_25JAN2024'
    standardize_county_shapefiles(d, o)

    s = '/media/research/IrrigationGIS/Montana/geointernship/statewide_irrigation_dataset_v1.shp'
# ========================= EOF ====================================================================
