import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt 
import calendar
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo = False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#flask setup
app = Flask(__name__)

@app.route('/')
def welcome():
    return(
    f"Available Routes:<br/>"
    f"The dates and temperature observations from the last year:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"List of stations from the dataset:<br/>"
    f"/api/v1.0/stations<br/>"
    f"List of Temperature Observations (tobs) for the previous year:<br/>"
    f"/api/v1.0/tobs<br/>"
    f"List of the minimum temperature, the average temperature, and the max temperature for a given start(i.e.2017-1-1):<br/>"
    f"/api/v1.0/<start><br/>"
    f"List of the minimum temperature, the average temperature, and the max temperature for a given start and end(i.e.2017-01-01/2017-02-07):<br/>"
    f"/api/v1.0/<start>/<end><br/>"
   )
   
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    last_pres_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_pres_date_format = dt.datetime.strptime(last_pres_date,"%Y-%m-%d")
    year = last_pres_date_format.year
    if(calendar.isleap(year)):
        first_pres_date = last_pres_date_format - dt.timedelta(days = 366)
    else:
        first_pres_date = last_pres_date_format - dt.timedelta(days = 365)
    
	
    twelve_month_pres_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date > first_pres_date).order_by(Measurement.date).all()

    session.close()
    
    prcp_list = []
    for date,prcp in twelve_month_pres_data:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Prcp'] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station).all()
    session.close()
    stations_list = []
    for station in stations:
        stations_dict = {}
        stations_dict['Station'] = station.station
        stations_dict["Station Name"] = station.name
        stations_dict["Latitude"] = station.latitude
        stations_dict["Longitude"] = station.longitude
        stations_dict["Elevation"] = station.elevation
        stations_list.append(stations_dict)

    return jsonify (stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_pres_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_pres_date_format = dt.datetime.strptime(last_pres_date,"%Y-%m-%d")
    year = last_pres_date_format.year
    if(calendar.isleap(year)):
        first_pres_date = last_pres_date_format - dt.timedelta(days = 366)
    else:
        first_pres_date = last_pres_date_format - dt.timedelta(days = 365)
    twelve_month_tobs = session.query(
    Measurement.tobs,
    Measurement.date,
    Measurement.station).filter(Measurement.date > first_pres_date).all()
    session.close()

    temp_list = []
    for temp in twelve_month_tobs:
        temp_dict = {}
        temp_dict['Station'] = temp.station
        temp_dict['Date'] = temp.date
        temp_dict['Temp'] = temp.tobs
        temp_list.append(temp_dict)

    return jsonify (temp_list)

@app.route("/api/v1.0/<start>")
def start_temp(start=None):
    
    session = Session(engine)
    start_temps = session.query(
    func.min(Measurement.tobs), 
    func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    start_list = list()
    for temp_min, temp_avg, temp_max in start_temps:
        start_dict = {}
        start_dict["Min Temp"] = temp_min
        start_dict["Max Temp"] = temp_avg
        start_dict["Avg Temp"] = temp_max
        start_list.append(start_dict)

    return jsonify (start_list)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start=None,end=None):
    session = Session(engine)
    temps = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)).filter(Measurement.date >= start,Measurement.date <= end).all()
    session.close()
    
    temp_list = []
    for temp_min, temp_avg, temp_max in temps:
        temp_dict = {}
        temp_dict["Min Temp"] = temp_min
        temp_dict["Avg Temo"] = temp_avg
        temp_dict["Max Temp"] = temp_max
        temp_list.append(temp_dict)

    return jsonify ({'Data':temp_list})

if __name__ == '__main__':
    app.run(debug=True)