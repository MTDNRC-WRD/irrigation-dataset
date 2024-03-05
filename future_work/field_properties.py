import os
import shutil
from subprocess import check_call

import ee
import fiona
import numpy as np
import pandas as pd
import geopandas as gpd

from utils.extract_cdl import get_cdl
from utils.extract_irrmapper import get_irrigation

from future_work.cdl import cdl_crops

home = os.path.expanduser('~')
conda = os.path.join(home, 'miniconda3', 'envs')
if not os.path.exists(conda):
    conda = conda.replace('miniconda3', 'miniconda')
EE = os.path.join(conda, 'gcs', 'bin', 'earthengine')
GS = '/home/dgketchum/google-cloud-sdk/bin/gsutil'

OGR = '/usr/bin/ogr2ogr'

AEA = '+proj=aea +lat_0=40 +lon_0=-96 +lat_1=20 +lat_2=60 +x_0=0 +y_0=0 +ellps=GRS80 ' \
      '+towgs84=0,0,0,0,0,0,0 +units=m +no_defs'

WGS = '+proj=longlat +datum=WGS84 +no_defs'

os.environ['GDAL_DATA'] = os.path.join(conda, 'envs/gcs/share/gdal/')


def push_fields_to_asset(_dir, tiles, asset_folder, bucket):
    missing = []
    for tile in tiles:

        # if tile not in ['12UXU']:
        #     continue

        local_files = [os.path.join(_dir, tile, '{}_CLU.{}'.format(tile, ext)) for ext in
                       ['shp', 'prj', 'shx', 'dbf']]

        if not all([os.path.exists(lf) for lf in local_files]):
            print('\n{} not found'.format(tile))
            missing.append(tile)
            continue

        bucket_dst = os.path.join(bucket, asset_folder)

        bucket_files = [os.path.join(bucket_dst, '{}_CLU.{}'.format(tile, ext)) for ext in
                        ['shp', 'prj', 'shx', 'dbf']]

        for lf, bf in zip(local_files, bucket_files):
            cmd = [GS, 'cp', lf, bf]
            check_call(cmd)

        asset_id = os.path.basename(bucket_files[0]).split('.')[0]
        ee_dst = 'users/dgketchum/fields/{}/{}'.format(asset_folder, asset_id)
        cmd = [EE, 'upload', 'table', '-f', '--asset_id={}'.format(ee_dst), bucket_files[0]]
        check_call(cmd)
        print(asset_id, bucket_files[0])

    print('\n\n\nMissing: {}'.format(missing))


def get_field_properties(tiles, src_dir, key='id', check_dir=None):
    ee.Authenticate()
    ee.Initialize(project='ee-dgketchum')

    if not check_dir:
        check_dir = ''

    for tile in tiles:
        try:
            print(tile)

            src = os.path.join(src_dir, '{}_CLU'.format(tile))

            dst_file = os.path.join(check_dir, 'mgrs_cdl', 'cdl_{}.csv'.format(tile))
            if check_dir and os.path.isfile(dst_file):
                continue
            else:
                get_cdl(src, tile, key=key)

            dst_file = os.path.join(check_dir, 'mgrs_irr', 'irr_{}.csv'.format(tile))
            if check_dir and os.path.isfile(dst_file):
                continue
            else:
                get_irrigation(src, tile, key=key)

        except ee.EEException as e:
            print('{} failed: {}'.format(tile, e))


def write_field_properties(tiles, fields, cdl_dir, irr_dir, out_dir, key='id', overwrite=False, check_geo=False):
    include_codes = [k for k in cdl_crops().keys()]
    for tile in tiles:

        if tile != '13TDL':
            continue

        out_d = os.path.join(out_dir, tile)
        out_f = os.path.join(out_d, '{}_CLU.shp'.format(tile))
        if os.path.exists(out_f) and not overwrite:
            print(os.path.basename(out_f), 'exists, skipping')
            continue

        shp = os.path.join(fields, tile, '{}_CLU.shp'.format(tile))

        try:
            df = gpd.read_file(shp)
            df.set_index(key, inplace=True)
        except fiona.errors.DriverError:
            print('Error Opening {}\n'.format(shp))
            continue

        except KeyError:
            print('KeyError: {}\n'.format(shp))

        cdl_file = os.path.join(cdl_dir, 'cdl_{}.csv'.format(tile))
        cdl = pd.read_csv(cdl_file, index_col=key)
        try:
            cdl = cdl.astype(int)
        except pd.errors.IntCastingNaNError:
            nan_ct = np.count_nonzero(np.isnan(cdl.values))
            print('{} NaN in array of {}: {}'.format(nan_ct, cdl.shape[0], tile))
            cdl.dropna(axis=0, inplace=True)
            cdl = cdl.astype(int)
        cdl = cdl.apply(lambda x: np.any([i for i in x if i in include_codes]), axis=1)
        cdl = cdl[cdl]
        if cdl.empty:
            print('No cultivation detected in {}'.format(tile))
            continue

        irr_file = os.path.join(irr_dir, 'irr_{}.csv'.format(tile))
        irr = pd.read_csv(irr_file, index_col=key)
        irr = irr[['irr_{}'.format(y) for y in range(2017, 2022)]].mean(axis=1)
        irr = irr.sort_index()
        irr = irr[irr > 0.05]
        if irr.empty:
            print('No cultivation detected in {}'.format(tile))
            continue

        match = [i for i in df.index if i in irr.index]
        df = df.loc[match]

        df.loc[match, 'irr'] = irr.loc[match]
        if not os.path.isdir(out_d):
            os.mkdir(out_d)

        if check_geo:
            g = df.iloc[0]['geometry']
            for i, r in df.iterrows():
                geo = r['geometry']
                check = geo.intersects(g)

        df.to_file(out_f)
        print('Wrote {}, {} features'.format(os.path.basename(out_f), df.shape[0]))


def copy_unfiltered(tiles, in_dir, out_dir):

    exts = ['shp', 'prj', 'shx', 'dbf']

    for tile in tiles:

        try:
            in_files = [os.path.join(in_dir, tile, '{}_MTDNRC.{}'.format(tile, ext)) for ext in exts]
            out_d = os.path.join(out_dir, tile)
            out_files = [os.path.join(out_d, '{}_MTDNRC.{}'.format(tile, ext)) for ext in exts]

            if not os.path.isdir(out_d):
                os.mkdir(out_d)

            [shutil.copyfile(i, o) for i, o in zip(in_files, out_files)]

        except Exception as e:
            print('{} failed: {}'.format(tile, e))
            continue

        print(tile)


if __name__ == '__main__':

    d = '/media/research/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'
    if not os.path.isdir(d):
        d = '/home/dgketchum/data/IrrigationGIS/Montana/statewide_irrigation_dataset/future_work_15FEB2024'

    mgrs_tiles = os.path.join(d, 'mt_mgrs_tiles.csv')
    tiles_ = list(pd.read_csv(mgrs_tiles)['MGRS_TILE'])

    mgrs = os.path.join(d, 'MGRS')
    split = os.path.join(mgrs, 'split')

    cloud_location = 'mgrs_split_clu'

    # Missing: ['11TPL', '12TTQ', '12UTV']

    # push_fields_to_asset(split, tiles_, cloud_location, 'gs://wudr')

    properties_dir = os.path.join(mgrs, 'mgrs_properties')
    field_asset_dir = 'users/dgketchum/fields/{}'.format(cloud_location)
    # get_field_properties(tiles_, field_asset_dir, key='OBJECTID', check_dir=properties_dir)

    cdl_data = os.path.join(properties_dir, 'mgrs_cdl')
    irr_data = os.path.join(properties_dir, 'mgrs_irr')

    attributed = os.path.join(mgrs, 'split_filtered')

    write_field_properties(tiles_, split, cdl_data, irr_data, attributed,
                           key='OBJECTID', overwrite=True, check_geo=True)

    # copy_unfiltered(tiles_, split, attributed)

# ========================= EOF ====================================================================
