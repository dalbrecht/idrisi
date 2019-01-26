from flask import Flask
from flask_cors import CORS
import sqlite3
from flask import g
import json

app = Flask(__name__)
CORS(app)

DATABASE = '../geodata/data/places.db'


def connect_db():
    return sqlite3.connect(DATABASE)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/lookup/<geoname>')
def lookup_geoname(geoname):
    """Accepts a somewhat precise geoname and returns the records that match"""
    query = """
    SELECT 
        geoname_id,
        name,
        latitude,
        longitude,
        country_code,
        admin1_code 
    FROM geonames 
    WHERE name LIKE ?"""

    conn = g.db
    cursor = conn.cursor()
    rows = cursor.execute(query, [geoname])
    output = list()
    for row in rows:
        output.append({
            "geoname_id": row[0],
            "name": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "admin1_code": row[4]
        })
    return json.dumps(output)

if __name__ == '__main__':
    app.run()
