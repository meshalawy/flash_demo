import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point, box
from shapely.wkt import loads as load_wkt
from shapely.wkb import loads as load_wkb
from shapely import geos
from sklearn.model_selection import train_test_split


# EBIRD
# FILE_NAME = "/Users/mmusleh/Downloads/TurboReg_experiments/data_different_sizes/21330/data_grid_ready.csv"

 
# df = pd.read_csv(FILE_NAME)
# geometry=[load_wkt(geom.split(";")[1]).centroid for geom in df.st_asewkt]
# df["lon"] = [g.centroid.x for g in geometry]
# df["lat"] = [g.centroid.y for g in geometry]
# values = df.observed
# df["color"] = ['#1C233F' if v ==1 else '#CAC9C7' for v in values ]

# gdf = GeoDataFrame(df, geometry=geometry)

# train, test = train_test_split(gdf, test_size=0.2, random_state=123456)


# minx, miny, maxx, maxy = (test.total_bounds)
# midx = minx + (maxx-minx)/2
# midy = miny + (maxy-miny)/2
# q1 = box(minx, midy, midx , maxy)
# q2 = box(midx, midy , maxx, maxy)
# q3 = box(minx, miny , midx, midy)
# q4 = box(midx, miny , maxx, midy)


# train_str = ""
# test_str = ""

# for i, x in train.iterrows():
#     train_str += f'{{"lat":{x.lat}, "lon":{x.lon}, "value":{x.observed}, "obs":{x.observers_avg_high}, "dur":{x.duration_avg_high}, "dist":{x.distance_avg_high}, "color":"{x.color}" }},\n'

# for i, x in test.iterrows():
#     test_str += f'{{"lat":{x.lat}, "lon":{x.lon}, "value":{x.observed}, "obs":{x.observers_avg_high}, "dur":{x.duration_avg_high}, "dist":{x.distance_avg_high}, "color":"{x.color}" }},\n'

# for n, q in enumerate([q1,q2,q3,q4]) :
#     with open (f'q{n}', 'w+') as w: 
#         w.write(str(q.centroid))
#         w.write(str(q))
#         for i, x in test[test.within(q)].iterrows():
#             w.write(f'{{"lat":{x.lat}, "lon":{x.lon}, "value":{x.observed}, "obs":{x.observers_avg_high}, "dur":{x.duration_avg_high}, "dist":{x.distance_avg_high}, "color":"{x.color}" }},\n')

# # for id, lat,long, value, obs, dur, dist, color in zip(df.id, lats, longs, values,
# #     df.observers_avg_high,
# #     df.duration_avg_high,
# #     df.distance_avg_high, colors):
# #     item = f'{{"lat":{lat}, "long":{long}, "value":{value}, "obs":{obs}, "dur":{dur}, "dist":{dist}, "color":"{color}" }},\n'
# #     if id in df2.id:
# #         train += item
# #     else: 
# #         test += item


# with open('train', 'w+') as w:
#     w.write(train_str)

# with open('test', 'w+') as w:
#     w.write(test_str)


# #####################################################################################################
# Land Cover OLD
# 
# Shell commands: NOT PYTHON 
#  # echo "COPY (SELECT id, val, dem, slp, dist, ST_AsEWKT(st_transform(geom,4326)) from mn_data_normalized_train_15807) TO STDOUT with CSV HEADER" | PGPASSWORD=postgisisfun psql -h cs-spatial-314 -d land_cover -U dmlab -o "land_cover_data_train_15807.csv"
#  # echo "COPY (SELECT id, val, dem, slp, dist, ST_AsEWKT(st_transform(geom,4326)) from mn_data_normalized_test_15807) TO STDOUT with CSV HEADER" | PGPASSWORD=postgisisfun psql -h cs-spatial-314 -d land_cover -U dmlab -o "land_cover_data_test_15807.csv"

# FILE_NAME = "/Users/mmusleh/git/flash_demo/ignore/land_cover_data_test_15807.csv"


# df = pd.read_csv(FILE_NAME)
# geometry=[load_wkt(geom.split(";")[1]) for geom in df.st_asewkt]
# longs = [g.centroid.x for g in geometry]
# lats = [g.centroid.y for g in geometry]
# values = [0 if v==82 else (1 if v in [41,42,43] else 2) for v in df.val]

# # 0: crops, 1: forest, 2: others
# colors = ['yellow' if v==0 else ('green' if v==1 else 'blue') for v in values]

# for lat,long, value, color in zip(lats, longs, values, colors):
#     print(f'{{"lat":{lat}, "long":{long}, "value":{value}, "color": "{color}" }},')



# LAND COVER NEW

FILE_NAME = "/Users/mmusleh/git/flash_demo/ignore/land_cover_data_test_15807.csv"
df = pd.read_csv(FILE_NAME)
geometry=[load_wkt(geom.split(";")[1]).centroid for geom in df.st_asewkt]
df["lon"] = [g.centroid.x for g in geometry]
df["lat"] = [g.centroid.y for g in geometry]
values = [0 if v==82 else (1 if v in [41,42,43] else 2) for v in df.val]

# # 0: crops, 1: forest, 2: others
colors = ['#A9AE85' if v==0 else ('#729565' if v==1 else "#73A7CC") for v in values]
df['value'] = values
df["color"] = colors

gdf = GeoDataFrame(df, geometry=geometry)

minx, miny, maxx, maxy = (gdf.total_bounds)
midx = minx + (maxx-minx)/2
midy = miny + (maxy-miny)/2
q1 = box(minx, midy, midx , maxy)
q2 = box(midx, midy , maxx, maxy)
q3 = box(minx, miny , midx, midy)
q4 = box(midx, miny , maxx, midy)



for n, q in enumerate([q1,q2,q3,q4]) :
    with open (f'q{n}', 'w+') as w: 
        w.write(str(q.centroid))
        w.write(str(q))
        for i, x in gdf[gdf.within(q)].iterrows():
            w.write(f'{{"lat":{x.lat}, "lon":{x.lon}, "value":{x.value}, "color":"{x.color}" }},\n')
