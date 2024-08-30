import sqlite3
import requests
from tqdm import tqdm

from flask import Flask, request
import json 
import numpy as np
import pandas as pd

# Define a function to create connection for reusability purpose
def make_connection():
    connection = sqlite3.connect('austin_bikeshare.db')
    return connection

# Make a connection
conn = make_connection()

app = Flask(__name__) 


@app.route('/')
def home():
    return 'Hello World'

# API get ALL stations
@app.route('/stations/')
def route_all_stations():
    conn = make_connection()
    stations = get_all_stations(conn)
    return stations.to_json()
    


# API get station by id
@app.route('/stations/<station_id>')
def route_stations_id(station_id):
    conn = make_connection()
    station = get_station_id(station_id, conn)
    return station.to_json()



# api get all trip
@app.route('/trips/')
def route_all_trips():
    
    take = request.args.get('take') 
    skip = request.args.get('skip') 
    
    conn = make_connection()
    trips = get_all_trips(take, skip, conn)
    return trips.to_json()



#api tes POST data
@app.route('/json', methods=['POST']) 
def json_example():
    
    req = request.get_json(force=True) # Parse the incoming json data as Dictionary
    
    name = req['name']
    age = req['age']
    address = req['address']
    
    return (f'''Hello {name}, your age is {age}, and your address in {address}
            ''')

#api add station data
@app.route('/stations/add', methods=['POST']) 
def route_add_station():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)
    
    conn = make_connection()
    result = insert_into_stations(data, conn)
    return result


#api add trip data
@app.route('/trips/add', methods=['POST']) 
def route_add_trip():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)
    
    conn = make_connection()
    result = insert_into_trips(data, conn)
    return result

# api get avg trip duration in minutes 
@app.route('/trips/avg_duration')
def route_avg_duration():
    conn = make_connection()
    avg_dur = get_avg(conn)
    return avg_dur.to_json()


# api get average trip duration by bike_id
@app.route('/trips/avg_duration/<bike_id>')
def avg_duration_by_bike_id(bike_id):
    conn = make_connection()
    avg = get_avg_duration_by_bike_id(bike_id, conn)
    return avg.to_json()


# api get total bike by station
@app.route('/stations/totalbike', methods=['POST']) 
def route_total_bike():
    req = request.get_json(force=True) # Parse the incoming json data as Dictionary
    
    station_id = req['station_id']
    start_or_end = req['start_or_end']
    
    
    conn = make_connection()
    result = get_total_bike(station_id, start_or_end, conn)
    return result.to_json()




#=================== functions ================================#
def get_all_stations(conn):
    query = f"""SELECT * FROM stations"""
    result = pd.read_sql_query(query, conn)
    return result

def get_station_id(station_id, conn):
    query = f"""SELECT * FROM stations WHERE station_id = {station_id}"""
    result = pd.read_sql_query(query, conn)
    return result

def get_all_trips(take, skip, conn):
    query = f"""SELECT * FROM trips limit {take} offset {skip}"""
    result = pd.read_sql_query(query, conn)
    return result

def get_trip_id(trip_id, conn):
    query = f"""SELECT * FROM trips WHERE station_id = {trip_id}"""
    result = pd.read_sql_query(query, conn)
    return result

def insert_into_stations(data, conn):
    query = f"""INSERT INTO stations values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def insert_into_trips(data, conn):
    query = f"""INSERT INTO trips values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def get_avg(conn):
    q = f"""
        Select avg(duration_minutes) as average_duration_in_minutes FROM trips
        """
    result = pd.read_sql_query(q, conn)
    return result

def get_avg_duration_by_bike_id(bike_id, conn):
    q = f"""
            Select avg(duration_minutes) as average_duration_in_minutes FROM trips WHERE bikeid = {bike_id}
        """
    result = pd.read_sql_query(q, conn)
    return result

def get_total_bike(stationid, start_or_end, conn):
    
    if start_or_end == 'start' :
        point = "t.start_station_id"
    else:
        point = "t.end_station_id"
    
    query = f"""
            SELECT s.station_id, s.name as station_name, s.address as station_address, count(t.bikeid) as total_bike
                FROM trips as t 
                Left Join stations as s
                on {point} = s.station_id
                WHERE {point} = {stationid}
                Group By s.station_id
        """
    result = pd.read_sql_query(query, conn)
    return result

if __name__ == '__main__':
    app.run(debug=True, port=5000)