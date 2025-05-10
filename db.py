from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqlconnector://root:121004@localhost/school_management")
metadata = MetaData() 
Session = sessionmaker(bind=engine)
session = Session()
