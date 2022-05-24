#Use Flask to create your routes.
from imaplib import Time2Internaldate
import json
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
engine = create_engine('sqlite:///hawaii.sqlite',connect_args={'check_same_thread': False})
connection= engine.connect()
Base= automap_base()
Base.prepare(engine,reflect=True)
Measurement= Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
date= session.query(Measurement.date).all()
app = Flask(__name__)

#/
#Home page.
#List all routes that are available.

@app.route("/")
def home():
    return(
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end><br/>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
    prcp_data = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>'2016-08-23').order_by(Measurement.date).all()
    dict= { date: prcp for date ,prcp in prcp_data}
    return jsonify(dict)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    active_station= session.query(Measurement.station, func.count(Measurement.station).label('count')).group_by(Measurement.station).all()
    stations=[]
    for station in active_station:
        stations.append(station[0])
    return jsonify(stations)


#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    active_station= session.query(Measurement.station, func.count(Measurement.station).label('count')).group_by(Measurement.station).all()
    active_station.sort(key=lambda y:y[1])
    active_station.reverse()
    active_station_Id= active_station[0][0]
    tmp_result=session.query(Measurement.tobs).filter(Measurement.station==active_station_Id).filter(Measurement.date>'2016-08-23').order_by(Measurement.date.desc()).all()
    temp_list = []
    for temp in tmp_result:
        temp_list.append(temp[0])
    tmp_result_dict ={'temp':temp_list}
    return jsonify(tmp_result_dict)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start>')
def start(start=None):
    tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>=start).all()
    tmin={'min':tobs[0][0]}
    tmax={'max' :tobs[0][1]}
    tavg={'avg': tobs[0][2]}
    return jsonify(tmin,tmax,tavg)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date.between(start,end)).all()
    tmin={'min':tobs[0][0]}
    tmax={'max' :tobs[0][1]}
    tavg={'avg': tobs[0][2]}
    return jsonify(tmin,tmax,tavg)
app.run()