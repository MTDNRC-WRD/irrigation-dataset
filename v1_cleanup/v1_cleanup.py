import os
import geopandas as gpd


def sid_v1_cleanup(in_dir, infile=None, savefile=True, out_dir=None, outfile=None):
    """ Takes in the published SID v1.0, cleans up some identified issues, and returns cleaned data in GeoDataFrame.
    Data available at https://mslservices.mt.gov/Geographic_Information/Data/DataList/datalist_Details.aspx?did=%7Bf33bc611-8d4e-4d92-ae99-49762dec888b%7D
    Corrections addressed: removal of unreasonably small fields (<500m^2)

    Params:
    in_dir: str, path to local directory where SID shapefile is stored.
    infile: str, optional, name of SID shapefile. If None, use 'Montana_Statewide_Irrigation_Dataset.shp'.
    savefile: bool, optional, If True, save cleaned data to new SID shapefile.
    out_dir: str, optional, path to local directory where cleaned SID shapefile is saved.
    If None, file is saved to same directory as indicated by in_dir.
    out_file: str, optional, name of cleaned SID shapefile.
    If None, use 'Montana_Statewide_Irrigation_Dataset_Cleaned.shp'.

    Returns GeoDataFrame of cleaned data.
    """
    # Establish location/name of SID shapefile
    if infile:
        sid_file = os.path.join(in_dir, infile)
    else:
        sid_file = os.path.join(in_dir, 'Montana_Statewide_Irrigation_Dataset.shp')

    # STEP 1: IDENTIFY AND REMOVE TINY FIELDS
    size = 500  # Area in m^2 used as cutoff threshold for unreasonably small fields.
    # When defined as area less than...
    # 1 m^2: 18 fields identified in dataset.
    # 100 m^2: 47 fields.
    # 500 m^2: 62 fields.
    # 1000 m^2: 73 fields.

    # identify tiny fields
    sid = gpd.read_file(sid_file)
    sid = sid.to_crs("EPSG:5071")
    sid.index = sid['FID_1']
    sid = sid.drop(['FID_1'], axis=1)
    sid['area_m2'] = sid['geometry'].area
    tiny_fields = sid[sid['area_m2'] < size].index

    # remove tiny fields
    clean_sid = sid.drop(tiny_fields)

    if savefile:
        # Establish location/name of output SID shapefile
        if out_dir:
            if outfile:
                out = os.path.join(out_dir, outfile)
            else:
                out = os.path.join(out_dir, 'Montana_Statewide_Irrigation_Dataset_Cleaned.shp')
        else:
            if outfile:
                out = os.path.join(in_dir, outfile)
            else:
                out = os.path.join(in_dir, 'Montana_Statewide_Irrigation_Dataset_Cleaned.shp')
        # Save cleaned data to new shapefile
        clean_sid.to_file(out)

    return clean_sid  # Do I always want it to output the gdf?


if __name__ == '__main__':
    sid_dir = 'C:/Users/CND571/Downloads'
    new_sid = sid_v1_cleanup(sid_dir, savefile=False)
