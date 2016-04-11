# Python script to regroup and reproject VDL bus lines into a WGS84 geojson file

import requests, json, pprint, pyproj
from pyproj import Proj

describe_url = "http://opendata.vdl.lu/odaweb/index.jsp?describe=1"

data_sets = requests.get(describe_url).json()

bus_ids = {}

# for every vdl dataset check if name begins with "Ligne" and put into dict by keeping that name
for data_set in data_sets["data"]:
    if data_set["i18n"]["fr"]["name"].startswith("Ligne"):
        bus_ids[data_set["i18n"]["fr"]["name"]] = data_set["id"]

# fill a dict containing all the geojson objects of the lines
geojson_objects = {}
for name in bus_ids:
    url = "http://opendata.vdl.lu/odaweb/?cat=%s" % bus_ids[name]
    geojson_objects[name] = requests.get(url).json()

# merge all the geojson objects into one
output = geojson_objects[geojson_objects.keys()[0]]
for name in geojson_objects:
    features = geojson_objects[name]['features']
    for f in features:
        f["properties"]["_ligne"] = name
    if features not in output['features']:
        output['features'].extend(features)


#reproject to LL84
p1 = Proj(init="EPSG:2169")
p2 = Proj(init="EPSG:4326")


def __reproject(_p):
    ll = pyproj.transform(p1, p2, _p[0], _p[1])
    _p[0] = round(ll[0], 6)
    _p[1] = round(ll[1], 6)
    return _p

if "crs" in output:
    del output["crs"]
for f in output['features']:
    if "bbox" in f:
        del f["bbox"]
    if f["geometry"]["type"] == "Point":
        if f["geometry"]["coordinates"][0] < 1000:
            continue
        p = f["geometry"]["coordinates"]
        p = __reproject(p)
    else:
        if f["geometry"]["coordinates"][0][0] < 1000:
            continue
        for p in f["geometry"]["coordinates"]:
            p = __reproject(p)

with open('output.geojson', 'w') as outfile:
    json.dump(output, outfile)