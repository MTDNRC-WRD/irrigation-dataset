# irrigation-dataset
Code for the Montana Statewide Irrigation Dataset

This is the code associated with the creation of the first version of an expertly edited vector polygon 
coverage of Montana's irrigation-equipped fields.

Input Data:

The 'prep' code was used to prepare imagery for use by map editors:

We used imagery from the National Agricultural Imagery Program (NAIP): https://naip-usdaonline.hub.arcgis.com/
as a high-resolution data set that allowed workers to determine irrigation type and precise irrigated field boundaries.
We also used Google Earth Engine (https://earthengine.google.com/) to process Normalized Vegetation Density Index
(NDVI) over various time scales to help determine the crop phenology over one or more growing seasons on or around 
the year 2020. This information helps differentiate irrigated from non-irrigated crops.

We processed NAIP imagery from the NAIP Box repository at https://nrcs.app.box.com/v/naip/folder/126986234491. This 
data was downloaded, county-by-county, unzipped, and processed into usable imagery using prep/mrsid.py. 
This processing script requires accesss to the LizardTech MrSID Decoding Software Development Kit 
(we used MrSID_DSDK-9.5.4.4709-rhel6.x86-64.gcc531),
and to Open Source Geospatial Foundation's Geoaptial Data Abstraction Library (GDAL).
Since the .sid files provided by the NAIP repository are so large, we found the best way to process them was by 
decoding subsections of the imagery (i.e., tiles) and writing them to .tif with 'gdal_translate'. This is followed 
in the script with a call to 'gdalbuildvrt' to create an image pyramid that allows for speedy rendering of the 
imagery at various zoom levels. The resulting 'catalog.vrt' file was then imported into QGIS and used as an imagery
base layer during data editing. This approach uses only free software, there are likely proprietary solutions 
to this problem, as well.

The imagery in Google Earth Engine can be displayed by users here: 
    https://code.earthengine.google.com/50355d5df32c54d8d0baf088143b18af

Manual Editing:

For the most part, we edited 2019 Montana Department of Revenue 'Final Land Unit' (FLU) data to meet our specifications, 
but in extensive areas had access to previous DNRC work that we also integrated into the final layer. 

This was done by hand in QGIS with simple editing tools. The specifications were as follows:

Create a comprehensive coverage of Montana's irrigation-equipped agricultural fields that

- Is flat. There must be no 'overlapping' field objects. Each irrigated location must be part of one and only one
    vector polygon field object.
- Is attributed by irrigation type. All fields are attributed with their irrigation type:
    P - Center Pivot Irrigation.
    S - Sprinkler Irrigation.
    F - Flood irrigation.
- Is attributed by confidence in usage:
    3. Highest confidence, high usage.
    2. Medium confidence, medium usage.
    1. Low confidence, low usage.
- Is discrete. Each discernable field is discretized in a single object. Multi-field objects, such as is common
    in the FLU data, must be split into individual fields.

The lengthy process of editing attributes and field geometries led to a GIS dataset for each county in Montana, with the
exception of Carter, Fallon, and Wibaux Counties, where no irrigation was detected. The following section describes 
the unification of that data in a single source, and the addition of further attributes 
describing higher-level information.

Output Data:

The 'process' code is designed to unify, standardize, and clean the county-by-by county product of the 
editor's work and produce a publication-ready, single dataset (i.e., a shapefile of the entire state).

The code is designed to merge the county-based shapefiles of irrigated area created by MT DNRC during several 
internships from 2018 to 2024 that used Google Earth Engine and USDA FSA NAIP imagery to update existing 
sources of agricultural field boundaries. The final project working on the data was done from 2021 to 2024, 
and used 2019/2020 NAIP imagery for irrigation type classification and boundary geometry editing. 

Future Work:

We realized early on in the project that we did not have enough time or resources to enable accurate digitizing and 
attibution of the unmapped irrigated agriculture in Montana. FLU and existing DNRC data sources are quite comprehensive 
in the larger river valleys and irrigated districts, which cover the majority of irrigated lands in the state. However,
in some regions, e.g. in the small creek tributaries of the Tongue River. See for example the riparian areas on 
Pumpkin, Cottonwood, and Horkan Creeks, just south and west of Volberg, MT. This is a good example of where FLU only 
maps several fields, while close visual inspection of high resolution imagery and time series of NDVI indicate that
there are dozens of fields that are likely irrigated at least infrequently. This is foremost indicated by the presence 
of small reservoirs and ditches. Further inspection using existing landcover information, such as 
IrrMapper (https://www.mdpi.com/2072-4292/12/14/2328) and USDA's Cropland Data Layer 
(https://www.tandfonline.com/doi/full/10.1080/10106049.2011.562309), show detections of irrigation and crops likely
to be irrigated (cord, alfalfa, and barley).
