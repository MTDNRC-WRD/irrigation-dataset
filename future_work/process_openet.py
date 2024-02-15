import os
from subprocess import check_call

import ee
import fiona
import pandas as pd
import geopandas as gpd

from utils.extract_cdl import get_cdl
from utils.extract_irrmapper import get_irrigation

home = os.path.expanduser('~')
conda = os.path.join(home, 'miniconda3', 'envs')
if not os.path.exists(conda):
    conda = conda.replace('miniconda3', 'miniconda')
EE = os.path.join(conda, 'opnt', 'bin', 'earthengine')
GS = '/home/dgketchum/google-cloud-sdk/bin/gsutil'

OGR = '/usr/bin/ogr2ogr'

AEA = '+proj=aea +lat_0=40 +lon_0=-96 +lat_1=20 +lat_2=60 +x_0=0 +y_0=0 +ellps=GRS80 ' \
      '+towgs84=0,0,0,0,0,0,0 +units=m +no_defs'

WGS = '+proj=longlat +datum=WGS84 +no_defs'

os.environ['GDAL_DATA'] = 'miniconda3/envs/gcs/share/gdal/'


def push_fields_to_asset(_dir, tiles, bucket):
    missing = []
    for glob in tiles:

        if glob not in ['11TQN', '13UBP']:
            continue

        local_files = [os.path.join(_dir, '{}.{}'.format(glob, ext)) for ext in
                       ['shp', 'prj', 'shx', 'dbf']]

        if not all([os.path.exists(lf) for lf in local_files]):
            print('\n{} not found'.format(glob))
            missing.append(glob)
            continue

        bucket_dst = os.path.join(bucket, 'mgrs_split_clean_wgs')

        bucket_files = [os.path.join(bucket_dst, '{}.{}'.format(glob, ext)) for ext in
                        ['shp', 'prj', 'shx', 'dbf']]

        for lf, bf in zip(local_files, bucket_files):
            cmd = [GS, 'cp', lf, bf]
            check_call(cmd)

        asset_id = os.path.basename(bucket_files[0]).split('.')[0]
        ee_dst = 'users/dgketchum/fields/mgrs_split_clean_wgs/{}'.format(asset_id)
        cmd = [EE, 'upload', 'table', '-f', '--asset_id={}'.format(ee_dst), bucket_files[0]]
        check_call(cmd)
        print(asset_id, bucket_files[0])

    print('\n\n\nMissing: {}'.format(missing))


def get_field_properties(tiles, src_dir):
    for glob in tiles:
        try:
            src = os.path.join(src_dir, glob)
            get_irrigation(src, glob, key='id')
            get_cdl(src, glob, key='id')
            print(glob)
        except ee.EEException as e:
            print('{} failed: {}'.format(glob, e))


def write_field_properties(tiles, fields, cdl_dir, irr_dir, out_dir, key='id'):

    for tile in tiles:

        shp = os.path.join(fields, '{}.shp'.format(tile))

        try:
            df = gpd.read_file(shp)
            df.set_index('id', inplace=True)
        except fiona.errors.DriverError:
            print('Error Opening {}\n'.format(shp))
            continue
        except KeyError:
            print('KeyError: {}\n'.format(shp))

        cdl = pd.read_csv(os.path.join(cdl_dir, 'cdl_{}.csv'.format(tile)), index_col=key)

        irr = pd.read_csv(os.path.join(irr_dir, 'irr_{}.csv'.format(tile)), index_col=key)
        irr = irr[['irr_{}'.format(y) for y in range(2017, 2022)]].mean(axis=1)
        irr = irr.sort_index()
        irr = irr[irr > 0.0]

        match = [i for i in df.index if i in irr.index]
        df = df.loc[match]
        df.loc[match, 'irr'] = irr.loc[match]
        out_ = os.path.join(out_dir, '{}.shp'.format(tile))
        df.to_file(out_)
        print('Wrote {}'.format(out_))


if __name__ == '__main__':

    d = '/media/research/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'
    if not os.path.isdir(d):
        d = '/home/dgketchum/data/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'

    mgrs_tiles = os.path.join(d, 'mt_mgrs_tiles.csv')
    tiles_ = list(pd.read_csv(mgrs_tiles)['MGRS_TILE'])

    opnt_mgrs_fields = os.path.join(d, 'mgrs_split_clean_wgs')
    # push_fields_to_asset(opnt_mgrs_fields, tiles, 'gs://wudr')

    field_asset_dir = 'users/dgketchum/fields/mgrs_split_clean_wgs'
    # get_field_properties(tiles, field_asset_dir)

    cdl_data = os.path.join(d, 'mgrs_properties', 'mgrs_cdl')
    irr_data = os.path.join(d, 'mgrs_properties', 'mgrs_irr')

    attributed = os.path.join(d, 'mgrs_attrs')

    write_field_properties(tiles_, opnt_mgrs_fields, cdl_data, irr_data, attributed)

# ========================= EOF ====================================================================
