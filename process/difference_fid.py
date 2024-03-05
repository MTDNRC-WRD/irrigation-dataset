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
    new_fields = []
    new_invalid_geo = []
    old_invalid_geo = []

    for s in l:

        print(os.path.basename(s))
        odf = gpd.read_file(s)
        odf.set_index(keys='fid', inplace=True)

        for i, r in odf.iterrows():
            og = r['geometry']

            try:
                a = og.area
            except shapely.errors.GEOSException as e:
                print('{} {}'.format(i, e))
                old_invalid_geo.append(i)
                continue
            except AttributeError as e:
                print('{} {}'.format(i, e))
                old_invalid_geo.append(i)
                continue

            try:
                ng = df.loc[i, 'geometry']
            except KeyError:
                print('{} not in new data ({} features)'.format(i, odf.shape[0]))
                new_missing.append(i)
                continue

            try:
                a = ng.area
            except shapely.errors.GEOSException as e:
                print('{} {}'.format(i, e))
                new_invalid_geo.append(i)
                continue
            except AttributeError as e:
                print('{} {}'.format(i, e))
                new_invalid_geo.append(i)
                continue

            in_both.append(i)
            check = og.intersects(ng)

            if check:
                aligned.append(i)
            else:
                not_aligned.append(i)

    for i, r in df.iterrows():
        if i not in in_both:
            new_fields.append(i)

    dct = {'new_missing': new_missing,
           'new_fields': new_fields,
           'in_both': in_both,
           'aligned': aligned,
           'not_aligned': not_aligned,
           'old_geo_exception': old_invalid_geo,
           'new_geo_exception': new_invalid_geo}

    with open(json_out, 'w') as fp:
        json.dump(dct, fp, indent=4)


if __name__ == '__main__':
    old_ = '/home/dgketchum/Downloads/sid/provisional'
    new_ = ('/media/research/IrrigationGIS/Montana/statewide_irrigation_dataset/'
            'statewide_irrigation_dataset_15FEB2024.shp')
    json_o = '/home/dgketchum/Downloads/sid/discrepencies.json'
    check_fid_spatial(old_, new_, json_o)

# ========================= EOF ====================================================================
