import sqlite3
import matplotlib
matplotlib.use("TkAgg")

from matplotlib import pyplot as plt
import cartopy.crs as ccrs

import shapely
from shapely.geometry import Point
from descartes import PolygonPatch
import json
from shapely.geometry import shape
import logging
import cartopy.feature as cfeature

logging.basicConfig()
DATABASE = '../geodata/data/adm1.db'
conn = sqlite3.connect(DATABASE)


def full_frame(width=None, height=None):
    import matplotlib as mpl
    mpl.rcParams['savefig.pad_inches'] = 0
    figsize = None if width is None else (width, height)
    fig = plt.figure(figsize=figsize)
    ax = plt.axes([0,0,1,1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale(tight=True)


def load_shapes():
    print('load shapes')
    c = conn.cursor()
    query = "SELECT mapcolor9, GEOJSON, ISO_A2 FROM adm1_shapes"
    rows = c.execute(query)
    shapes = list()
    for row in rows:
        # print(repr(row))

        place_shape = shape(json.loads(row[1]))
        # print(place_shape)
        shapes.append((int(row[0]), place_shape, row[2]))
    return shapes


def load_places():
    print('loading spaces')
    c = conn.cursor()
    # I'm fliping lat and long, not sure why
    query = "SELECT PlaceName, Long, Lat, Country From places_visited"
    rows = c.execute(query)
    points = list()
    for row in rows:
        points.append((row[0], Point(row[1], row[2]), row[3]))
    return points


def parse_hex(color_hex):
    r = int(color_hex[1:3], 16) / 256.0
    g = int(color_hex[3:5], 16) / 256.0
    b = int(color_hex[5:], 16) / 256.0
    return r, g, b


def tint(start_tuple, end_tuple, ratio):
    delta_r = end_tuple[0] - start_tuple[0]
    delta_b = end_tuple[1] - start_tuple[1]
    delta_g = end_tuple[2] - start_tuple[2]

    out = (start_tuple[0] + (delta_r * ratio),
            start_tuple[1] + (delta_g * ratio),
            start_tuple[2] + (delta_b * ratio))
    return out


def build_color_sequence(starthex, endhex, steps):
    start = parse_hex(starthex)
    end = parse_hex(endhex)
    outs = []
    for step in range(0, steps + 1):
        outs.append( tint(start, end, step/steps))
    return outs


chicago = (-87.65005, 41.85003)
chi_point = Point(chicago)

points = load_places()

visited_countries = set([x[2] for x in points])

full_frame()
fig = plt.figure(figsize=(10, 5))
print('figd')

ax = fig.add_subplot(1, 1, 1, projection=ccrs.EqualEarth())
ax.set_global()
ax.outline_patch.set_edgecolor('#20232A')
ax.outline_patch.set_linewidth(.2)
grid_transform = ccrs.PlateCarree()

# ax.stock_img()
# ax.coastlines()
ax.background_patch.set_facecolor('#FFFFFF')
color13 = build_color_sequence("#ACBEBE", "#F4F4EF", 9)

#visited_tint = parse_hex('#A01D26')
visited_tint = parse_hex('#A01D26')     # Fire Engine Red
# visited_tint = parse_hex('#5A5F37')   # Grass Green
# visited_tint = parse_hex('#217CA3')   # Cerulean Blue
# visited_tint = parse_hex('#265C00')   # Emerald
# visited_tint = parse_hex('#752A07')     # Charred
# visited_tint = parse_hex('#CB6318')     # Seeds


city_point = '#20232A'
# Colors =


def test_shape(shape_obj, pointslist):
    for p in pointslist:
        if shape_obj.contains(p[1]):
            return True

    return False


for shape in load_shapes():

    if test_shape(shape[1], points):
        color = tint(visited_tint, color13[shape[0]], 0)

    elif shape[2] in visited_countries:
        color = tint(visited_tint, color13[shape[0]], .3)

    else:
        color = color13[shape[0]]

    patch = PolygonPatch(shape[1],
                         facecolor=color,
                         ec=(1, 1, 1),
                         lw=.1,
                         transform=grid_transform)
    ax.add_patch(patch)

ax.add_feature(cfeature.LAKES,
               facecolor=(1, 1, 1),
               lw=0)
ax.add_feature(cfeature.RIVERS,
               edgecolor=(1, 1, 1),
               lw=.2)

for point in points:
    patch = PolygonPatch(
        point[1].buffer(.5),
        facecolor=city_point,
        lw=.1,
        ec=(1, 1, 1),
        transform=grid_transform,
        zorder=2)
    ax.add_patch(patch)

    patch = PolygonPatch(
        chi_point.buffer(.5),
        facecolor=city_point,
        lw=.2,
        ec=(1, 1, 1),
        transform=grid_transform)
    ax.add_patch(patch)

# plt.show()
plt.savefig(
    "map.jpg",
    format="jpg",
    transparent=True,
    frameon=False,
)
