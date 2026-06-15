import os
import geopandas as gpd

BAD_FIELDS = [
'001_000582',
'003_000535',
'003_000536',
'003_000537',
'003_000538',
'003_000539',
'003_000540',
'003_000541',
'003_000542',
'003_000544',
'003_000545',
'003_000546',
'003_000547',
'003_000548',
'003_000549',
'003_000550',
'003_000551',
'003_000552',
'003_000553',
'003_000554',
'003_000555',
'003_000556',
'003_000557',
'003_000558',
'003_000559',
'003_000560',
'003_000561',
'003_000562',
'003_000563',
'003_000564',
'003_000565',
'003_000566',
'003_000567',
'003_000687',
'003_000688',
'003_000689',
'003_000690',
'003_000691',
'003_001104',
'003_001105',
'003_001106',
'003_001107',
'003_001108',
'003_001109',
'003_001110',
'003_001111',
'003_001112',
'003_001113',
'003_001114',
'003_001745',
'003_001746',
'003_001747',
'003_001748',
'009_000323',
'013_000001',
'013_000002',
'013_000003',
'013_000041',
'013_000047',
'013_000048',
'013_000049',
'013_000050',
'013_000051',
'013_000052',
'013_000085',
'013_000086',
'013_000389',
'029_000329',
'029_000680',
'029_000681',
'029_000693',
'031_001391',
'031_001529',
'031_001532',
'031_001533',
'031_001535',
'031_001907',
'031_001908',
'031_001909',
'031_001910',
'031_001911',
'031_001917',
'031_001918',
'031_001919',
'031_001922',
'031_001956',
'031_001960',
'031_001965',
'031_001966',
'031_001967',
'031_001968',
'031_001969',
'031_001970',
'031_001971',
'031_001976',
'043_000160',
'045_000055',
'049_001337',
'067_001200',
'067_001957',
'073_000359',
'073_000468',
'073_000640',
'073_001521',
'081_000425',
'081_000431',
'081_000432',
'081_000433',
'081_000434',
'081_000435',
'081_000436',
'081_000808',
'083_000353',
'083_000355',
'085_000018',
'085_000019',
'085_000022',
'085_000035',
'085_000273',
'087_000578',
'089_000037',
'089_000039',
'097_000822',
'097_000834',
'097_000838',
'097_000850',
'097_000867',
'097_000873',
'097_000878',
'097_000881',
'097_000890',
'097_000891',
'097_000892',
'097_000893',
'097_000896',
'097_000897',
'097_000898',
'097_001107',
'097_001108',
'097_001110',
'097_001112',
'097_001113',
'097_001114',
'097_001115',
'097_001116',
'097_001117',
'097_001118',
'097_001119',
'097_001120',
'097_001122',
'097_001128',
'097_001129',
'097_001132',
'097_001142',
'099_001340',
'099_001619',
'099_001966',
'099_002021',
'099_002022',
'099_002023',
'099_002040',
'099_002041',
'099_002042',
'099_002043',
'099_002044',
'099_002045',
'099_002048',
'099_002049',
'099_002050',
'099_002051',
'099_002052',
'099_002053',
'099_002054',
'099_002055',
'099_002056',
'099_002251',
'105_000717',
'111_003574',
]

def sid_v1_cleanup(in_dir, infile=None, savefile=True, out_dir=None, outfile=None):
    """ Takes in published SID v1.0, cleans up some identified issues, returns cleaned data in GeoDataFrame.

    Data available at https://mslservices.mt.gov/Geographic_Information/Data/DataList/datalist_Details.aspx?did=%7Bf33bc611-8d4e-4d92-ae99-49762dec888b%7D

    Corrections addressed:
      - geometry simplified to remove vertices closer than 1 meter apart.
      - removal of unreasonably small fields (less than 0.1 acres or 400 m^2; n=58)
      - removal of duplicate set of Jefferson County fields (n=562)
      - removal of additional visually identified duplicate fields (n=178), FIDs listed in BAD_FIELDS.

    Args:
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

    # STEP 0: LOAD IN SHAPEFILE AND SIMPLIFY GEOMETRIES

    # Load and format data
    sid = gpd.read_file(sid_file)
    sid = sid.to_crs("EPSG:5071")
    sid.index = sid['FID_1']
    sid = sid.drop(['FID_1'], axis=1)

    # remove vertices closer than 1 meter apart.
    # This dramatically reduces the file size without sacrificing precision.
    sid['geometry'] = sid['geometry'].simplify(1)

    # STEP 1: IDENTIFY AND REMOVE TINY FIELDS

    # identify tiny fields
    size = 0.1  # Area in acres used as cutoff threshold for unreasonably small fields.
    tiny_fields = sid[sid['New_Acres'] < size].index

    # remove tiny fields
    sid = sid.drop(tiny_fields)

    # STEP 2: FIX JEFFERSON COUNTY DUPLICATION
    jeffco = sid[sid['COUNTYNAME'] == 'Jefferson'].sort_index()
    sid = sid.drop(jeffco.iloc[int(len(jeffco) / 2):].index)

    # STEP 3: REMOVE ADDITIONAL DUPLICATED/ERRONEOUS FIELDS
    clean_sid = sid.drop(BAD_FIELDS)

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

    return clean_sid


if __name__ == '__main__':
    sid_dir = 'C:/Downloads'
    new_sid = sid_v1_cleanup(sid_dir, savefile=True)
