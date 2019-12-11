import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt


def db_initialize():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    # reflect an existing database into a new model

    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)

    print(Base.classes.keys)


    # Save reference to the table
    Measurement = Base.classes.measurement
    Station = Base.classes.station
    #####
    session = Session(engine)

    return session, Measurement, Station

# Flask Setup
app = Flask(__name__)
#######################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session, Measurement, Station = db_initialize()
    # Calculate the date 1 year ago from the last data point in the database
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate = dt.datetime.strptime(str(lastdate[0]), '%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    lastyear =  lastdate - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date>=lastyear).\
        order_by(Measurement.date.asc()).all()

    return jsonify({k:v for k,v in results})

@app.route("/api/v1.0/stations")
def stations():
    session, Measurement, Station = db_initialize()
    results = session.query(Station.name,Station.station)

    return jsonify({k:v for k,v in results})



@app.route("/api/v1.0/tobs")
def tobs():
    session, Measurement, Station = db_initialize()
    # Calculate the date 1 year ago from the last data point in the database
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate = dt.datetime.strptime(str(lastdate[0]), '%Y-%m-%d')


    # Perform a query to retrieve the data and precipitation scores
    lastyear =  lastdate - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date>=lastyear).\
        order_by(Measurement.date.asc()).all()
   
    return jsonify({k:v for k,v in results})


@app.route("/api/v1.0/<start>")
def start(start):
    session, Measurement, Station = db_initialize()
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs).label("min temp"),
    func.avg(Measurement.tobs).label("mean temp"),func.max(Measurement.tobs).label("max temp"))\
        .filter(Measurement.date>=start_date).all()
    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session, Measurement, Station = db_initialize()
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate = dt.datetime.strptime(str(lastdate[0]), '%Y-%m-%d')

    if end_date > lastdate:  
        return("The last date is out of range")

    else:
        results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
        .filter(Measurement.date.between(start_date, end_date)).all()
        return(jsonify(results))
    

if __name__ == '__main__':
    app.run(debug=True)