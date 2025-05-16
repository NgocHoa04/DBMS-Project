from sqlalchemy import create_engine, Column, Integer, String, Date, DECIMAL, ForeignKey, select, exists
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import requests
import os
from dotenv import load_dotenv
from db import session, engine
from models import Grades, Students, Subjects, Teachers, Classes, Classes_Teacher, Class_period, Students_Classes, Schedules, Money, Academic_period, StudentLocation
from sqlalchemy import text
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()
API_KEY = os.getenv("API_KEY")
geolocator = Nominatim(user_agent="school_geocoder_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_students_without_location():
    sql = text("""
        SELECT StudentID, Address
        FROM Students
        WHERE StudentID NOT IN (SELECT StudentID FROM Student_Locations)
    """)
    with engine.connect() as conn:
        result = conn.execute(sql)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def upsert_location(student_id, latitude, longitude):
    sql = text("""
        INSERT INTO Student_Locations (StudentID, Latitude, Longitude)
        VALUES (:student_id, :lat, :lon)
        ON DUPLICATE KEY UPDATE Latitude = :lat, Longitude = :lon
    """)
    with engine.begin() as conn:
        conn.execute(sql, {"student_id": student_id, "lat": latitude, "lon": longitude})

def update_all_locations():
    df = get_students_without_location()
    print(f"Having {len(df)} Students who must change address")

    for idx, row in df.iterrows():
        student_id = row['StudentID']
        address = row['Address']
        if not address:
            print(f"StudentID {student_id} no has address, skipping...")
            continue
        
        try:
            location = geocode(address)
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"Geocode '{address}' -> (lat: {lat}, lon: {lon})")
                upsert_location(student_id, lat, lon)
            else:
                print(f"Not found coordinate for: {address}")
        except Exception as e:
            print(f"Error geocode address '{address}': {e}")

if __name__ == "__main__":
    update_all_locations()
