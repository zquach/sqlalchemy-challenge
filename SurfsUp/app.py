# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################

# Create database engine and session (adjust to your actual database URI)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">Precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">Stations</a><br/>'
        f'<a href="/api/v1.0/tobs">TOBS</a><br/>'
        f'<a href="/api/v1.0/&lt;start&gt;">Start Date</a><br/>'
        f'<a href="/api/v1.0/&lt;start&gt;/&lt;end&gt;">Start to End Date</a><br/>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform the query
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary with date as key and precipitation as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    print(f"Precipitation Results - {precipitation_dict}")
    print("Out of Precipitation Section")
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query all stations
    stations_data = session.query(station.station).all()
    # Close the session
    session.close()    
    # Convert the query results to a list
    stations_list = [station[0] for station in stations_data]
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station))\
                                 .group_by(measurement.station)\
                                 .order_by(func.count(measurement.station).desc())\
                                 .first()[0]

    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the temperature observations for the most active station for the last year
    tobs_data = session.query(measurement.date, measurement.tobs)\
                       .filter(measurement.station == most_active_station)\
                       .filter(measurement.date >= one_year_ago)\
                       .all()
    
    # Convert the query results to a list
    tobs_list = [tobs[1] for tobs in tobs_data]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Query to calculate min, max, and avg temperature for dates greater than or equal to the start date
    temp_stats = session.query(
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)
    ).filter(measurement.date >= start).all()
    
    # Convert the query result to a dictionary
    temp_stats_dict = {
        "TMIN": temp_stats[0][0],
        "TMAX": temp_stats[0][1],
        "TAVG": temp_stats[0][2]
    }
    
    return jsonify(temp_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Query to calculate min, max, and avg temperature for dates between the start and end date
    temp_stats = session.query(
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)
    ).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Convert the query result to a dictionary
    temp_stats_dict = {
        "TMIN": temp_stats[0][0],
        "TMAX": temp_stats[0][1],
        "TAVG": temp_stats[0][2]
    }
    
    return jsonify(temp_stats_dict)

if __name__ == '__main__':
    app.run(debug=True)