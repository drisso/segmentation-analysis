import json

import geopandas as gpd

with open(
    "data/TCGA-02-0001-01Z-00-DX1.83fce43e-42ac-4dcd-b156-2908e75f2e47.geojson",
    encoding="utf-8",
) as f:
    features = json.load(f)

gdf = gpd.GeoDataFrame.from_features(features)
gdf["minx"] = gdf["bbox"].str[0].str[0]
gdf["miny"] = gdf["bbox"].str[0].str[1]
gdf["maxx"] = gdf["bbox"].str[1].str[0]
gdf["maxy"] = gdf["bbox"].str[1].str[1]
gdf = gdf.drop(columns=["bbox"])
gdf.to_parquet(
    "data/TCGA-02-0001-01Z-00-DX1.83fce43e-42ac-4dcd-b156-2908e75f2e47.parquet"
)
