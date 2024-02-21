import os
import json

import shapely
import geopandas as gpd


def check_fid_spatial(old, new, json_out):
    l = [os.path.join(old, f) for f in os.listdir(old) if f.endswith('.shp')]

    df = gpd.read_file(new)
    df.set_index(keys='FID', inplace=True)

    new_missing = []
    in_both = []
    aligned = []
    not_aligned = []
    nonetype_geo = []
    geos_exception = []

    for s in l:

        print(os.path.basename(s))
        odf = gpd.read_file(s)
        odf.set_index(keys='fid', inplace=True)

        for i, r in odf.iterrows():
            og = r['geometry']
            try:
                ng = df.loc[i, 'geometry']
            except KeyError:
                print('{} not in new data ({} features)'.format(i, odf.shape[0]))
                new_missing.append(i)

            in_both.append(i)

            try:
                check = og.intersects(ng)
            except AttributeError as e:
                print('{} {}'.format(i, e))
                nonetype_geo.append(i)
            except shapely.errors.GEOSException as e:
                print('{} {}'.format(i, e))
                geos_exception.append(i)

            if check:
                aligned.append(i)
            else:
                not_aligned.append(i)

    dct = {'new_missing': new_missing,
           'in_both': in_both,
           'aligned': aligned,
           'not_aligned': not_aligned,
           'nonetype_geo': nonetype_geo,
           'geos_exception': geos_exception}

    with open(json_out, 'w') as fp:
        json.dump(dct, fp, indent=4)


if __name__ == '__main__':
    old_ = '/home/dgketchum/Downloads/sid_30JAN2024/sid_29JAN2024'
    new_ = ('/media/research/IrrigationGIS/Montana/statewide_irrigation_dataset/'
            'statewide_irrigation_dataset_15FEB2024.shp')
    json_o = '/home/dgketchum/Downloads/sid/discrepencies'
    check_fid_spatial(old_, new_)

# ========================= EOF ====================================================================
