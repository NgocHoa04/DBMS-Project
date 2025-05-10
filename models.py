from sqlalchemy import Table
from db import engine, metadata

metadata.reflect(bind=engine)

Grades = Table('Grades', metadata, autoload_with=engine)
Students = Table('Students', metadata, autoload_with=engine)
TimeSlots = Table('TimeSlots', metadata, autoload_with=engine)
Subjects = Table('Subjects', metadata, autoload_with=engine)
Teachers = Table('Teachers', metadata, autoload_with=engine)
Classes = Table('Classes', metadata, autoload_with=engine)
Classes_Teacher = Table('Classes_Teacher', metadata, autoload_with=engine)
Class_period = Table('Class_period', metadata, autoload_with=engine)
Students_Classes = Table('Students_Classes', metadata, autoload_with=engine)
Schedules = Table('Schedules', metadata, autoload_with=engine)
Money = Table('Money', metadata, autoload_with=engine)
Academic_period = Table('Academic_period', metadata, autoload_with=engine)