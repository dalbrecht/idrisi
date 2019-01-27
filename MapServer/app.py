from flask import Flask
from flask_cors import CORS
import sqlite3
from flask import g, request
import json
import sys

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


@app.route('/projects/<int:project_id>')
def get_project(project_id):

    query = """select 
                    geonames.geoname_id,
                    geonames.name,
                    geonames.latitude,
                    geonames.longitude,
                    geonames.admin1_code
                from project_geonames 
                    left join geonames 
                where project_geonames.geoname_id = geonames.geoname_id 
                    and project_geonames.project_id = ?"""

    conn = g.db
    cursor = conn.cursor()
    rows = cursor.execute(query, [project_id])
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


@app.route('/projects/', methods=["POST"])
def create_project():
    conn = g.db
    cursor = conn.cursor()
    query = """insert into projects (project_name) Values(?) """
    project_name = request.form['project_name']
    cursor.execute(query, [project_name])
    conn.commit()
    lookup_query = """SELECT project_name, project_id FROM projects WHERE project_name = ?"""
    cursor = conn.cursor()
    cursor.execute(lookup_query, [project_name])
    output = cursor.fetchone()
    return json.dumps({
        "project_name": output[0],
        "project_id": output[1]
    })


@app.route('/projects/<int:project_id>/places/', methods=["POST"])
def add_place_to_project(project_id):
    sys.stderr.write(str(dir(request)))
    data = request.get_json()
    #return json.dumps(data)
    geoname_id = data["geoname_id"]
    query = """INSERT INTO project_geonames (project_id, geoname_id) VALUES (?, ?)"""
    conn = g.db
    cursor = conn.cursor()
    cursor.execute(query, [project_id, geoname_id])


@app.route('/projects/<int:project_id>/places/<int:geoname_id>', methods=["DELETE"])
def remove_place(project_id, geoname_id):
    query = """DELETE FROM project_geonames WHERE project_id = ? and geoname_id = ?"""
    conn = g.db
    cursor = conn.cursor()
    cursor.execute(query, [project_id, geoname_id])


print(app.url_map)
if __name__ == '__main__':
    app.run(debug=True)
