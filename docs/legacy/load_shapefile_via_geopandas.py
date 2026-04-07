import sqlite3
import fiona
import json
shape = fiona.open("../geodata/data/natural_earth_data/ne_10m_admin_1_states_provinces.shp")
print(shape.schema)

# first feature of the shapefile
# first = shape.next()
cols = set()
shape_records = list()
for s in shape:
    record = dict()
    for prop, value in s["properties"].items():
        cols.add(prop)
        record[prop] = str(value)
    record["GEOJSON"] = json.dumps(s["geometry"])
    shape_records.append(record)

col_defs = list()
defaults = dict()
for x in cols:
    print(x)
    col_defs.append(x + ' TEXT')
    defaults[x] = None

print(cols)
colstr = ', '.join(col_defs)

create_str = "CREATE TABLE adm1_shapes ( " + colstr + ", GEOJSON TEXT)"
print(create_str)
conn = sqlite3.connect('../geodata/data/adm1.db')
c = conn.cursor()
c.execute("DROP TABLE adm1_shapes")
c.execute(create_str)
conn.commit()


def post_row(conn, tablename, rec):
    keys = ','.join(rec.keys())
    question_marks = ','.join(list('?'*len(rec)))
    values = tuple(rec.values())
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)


for s in shape_records:
    post_row(conn, "adm1_shapes", s)
    conn.commit()
