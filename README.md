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
the 2020. This information helps differentiate irrigated from non-irrigated crops.

We processed NAIP imagery from the NAIP Box repository at https://nrcs.app.box.com/v/naip/folder/126986234491. This 
data was downloaded, county-by-county, unzipped, and processed into usable imagery using prep/mrsid.py. 
This processing script requires accesss to the LizardTech MrSID Decoding Software Development Kit 
(we used MrSID_DSDK-9.5.4.4709-rhel6.x86-64.gcc531),
and to Open Source Geospatial Foundation's Geoaptial Data Abstraction Library (GDAL).
Since the .sid files provided by the NAIP repository are so large, we found the best way to process them was by 
decoding subsections of the imagery (i.e., tiles) and writing them to .tif with 'gdal_translate'. This is followed 
in the script with a call to 'gdalbuildvrt' to create an image pyramid that allows for speedy rendering of the 
imagery at various zoom levels. The resulting 'catalog.vrt' file was then imported into QGIS and used as an imagery
base layer during data editing. There are likely proprietary solutions to this problem, as well.

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
    - Is discrete. Each discernable field is discretized in a single object. Multi-field objects, such as is common
        in the FLU data, must be split into individual fields.

The lengthy process of editing attributes and field geometries led to a GIS dataset for each county in Montana. The 
following section describes the unification of that data in a single source, and the addition of further attributes 
describing higher-level information.

Output Data:

The 'process' code is designed to unify, standardize, and clean the 

The code is designed to merge the county-based shapefiles of irrigated area created by MT DNRC during several 
internships from 2018 - 2024 that used Google Earth Engine and USDA FSA NAIP imagery to update existing 
sources of agricultural field boundaries. The final project working on the data was done from 2021 - 2024, 
and used 2019/2020 NAIP imagery for irrigation type classification and boundary geometry editing. 

