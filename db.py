from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
metadata = MetaData()
# Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = sessionmaker(bind=engine)
session = Session()