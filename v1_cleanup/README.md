# SID V1.0 Cleanup

The Montana Statewide Irrigation Dataset (SID) is an ongoing project, with the anticipation of future versions that 
are more comprehensive and contain fewer errors. In the meantime, this file serves as a recognition/catalog of errors
in the existing dataset. Additionally, when feasible, the code in 'v1_cleanup.py' is designed to correct these errors.

Data available at: https://mslservices.mt.gov/Geographic_Information/Data/DataList/datalist_Details.aspx?did=%7Bf33bc611-8d4e-4d92-ae99-49762dec888b%7D
(Last updated 4/8/24)

#### General Improvements
- Geometry simplified to remove polygon vertices less than 1 meter apart. These close vertices are often artifacts of the curve-drawing process for circular fields. The simplification speeds up computation and reduces storage without sacrificing accuracy.

#### Errors corrected with 'v1_cleanup.py':
- Removal of unreasonably small fields (areas less than 0.1 acres or 400 m^2, 58 identified in V1.0 SID)
- removal of duplicate set of Jefferson County fields (n=562)
- removal of additional visually identified duplicate fields (n=178), FIDs listed in BAD_FIELDS.

#### Errors to be corrected in future SID versions:
- Duplicated/miscategorized fields:
  - Fields duplicated near county borders (Ex: duplicated fields near boundary between Park and Sweet Grass Counties, partially addressed)
  - Fields in the wrong county (Ex: fields near county boundaries defined by rivers)
  - Conflicting field boundaries in duplicated fields.
  - Multipolygon fields