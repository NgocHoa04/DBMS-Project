import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import numpy as np
import os
import select
from db import session, engine
from sqlalchemy import Table, func, and_
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sklearn.linear_model import LinearRegression
from models import Grades, Students, Subjects, Teachers, Classes, Classes_Teacher, Class_period, Students_Classes, Schedules, Money, Academic_period

def generate_scorecard(student_id: int, term: int = None, year: int = None):
    q = session.query(
        Grades.c.GradeID,
        Grades.c.StudentID,
        Students.c.StudentName.label('Student Name'),
        Subjects.c.SubjectName.label('Subject Name'),
        Grades.c.Score,
        Grades.c.Weight,
        Classes.c.ClassName.label('Class Name'),
        Academic_period.c.Term.label('Term'),
        Academic_period.c.Year.label('Year')
    ).join(Students, Students.c.StudentID == Grades.c.StudentID
    ).join(Subjects, Subjects.c.SubjectID == Grades.c.SubjectID
    ).join(Academic_period, Academic_period.c.PerId == Grades.c.PerId
    ).join(Students_Classes, Students_Classes.c.StudentID == Students.c.StudentID
    ).join(Classes, Classes.c.ClassID == Students_Classes.c.id
    ).filter(Grades.c.StudentID == student_id)


    if term is not None:
        q = q.filter(Academic_period.c.Term == term)
    if year is not None:
        q = q.filter(Academic_period.c.Year == year)

    q = q.order_by(Academic_period.c.Term, Academic_period.c.Year)
    q = q.distinct()

    df = pd.read_sql(q.statement, engine)
    session.close()

    if df.empty:
        print(f"No data found for student {student_id} in the term {term} of the {year}.")
        return f"No data found for student {student_id} in the term {term} of the {year}."
    # df = df.set_index('GradeID')
    

    df['Weighted Score'] = df['Score'] * df['Weight']
    overall_score = df['Weighted Score'].sum() / df['Weight'].sum()
    # print(f"Overall Score: {overall_score}")


    output_pdf = f"scorecards/scorecard_{student_id}.pdf"
    os.makedirs("scorecards", exist_ok=True)

    doc = SimpleDocTemplate(output_pdf, pagesize = A4)
    styles = getSampleStyleSheet()
    title = f"Scorecard: Student {student_id} - {df['Student Name'].iloc[0]}"
    if term or year:
        title += f"  ({term or ''} / {year or ''})"
    elems = [Paragraph(title, styles['Title'])]

    elems.append(Paragraph(f"<b>CLASS:</b> {df['Class Name'].iloc[0]}", styles['Normal']))

    df = df.drop(columns=["Weight"])
    df = df.drop(columns=["Weighted Score"])
    df = df.drop(columns=["Student Name", 'GradeID', 'StudentID'])
    df_pdf = df.drop(columns=["Class Name"])
    table_data = [df_pdf.columns.tolist()] + df_pdf.values.tolist()

    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elems.append(t)
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(f"<b>GPA:</b> {overall_score:.2f}", styles['Normal']))

    doc.build(elems)
    # print(df)
    return df

def generate_class_performances_per_each_class(class_name: str, term: int = None, year: int = None):
    class_info = session.query(
        Classes.c.ClassName,
        Academic_period.c.Term,
        Academic_period.c.Year
    ).join(Class_period, Class_period.c.ClassID == Classes.c.ClassID
    ).join(Academic_period, Class_period.c.PerID == Academic_period.c.PerId
    ).filter(
        Classes.c.ClassName == class_name,
        Academic_period.c.Term == term,
        Academic_period.c.Year == year
    ).first()

    if not class_info:
        raise ValueError(f"No class or academic period matches {class_name} - Term {term}, Year {year}.")

    q = session.query(
        Students.c.StudentID,
        Students.c.StudentName,
        Subjects.c.SubjectName,
        Grades.c.Score,
        Grades.c.Weight,
        Classes.c.ClassName,
        Academic_period.c.Term,
        Academic_period.c.Year
    ).join(Grades, Grades.c.StudentID == Students.c.StudentID
    ).join(Subjects, Subjects.c.SubjectID == Grades.c.SubjectID
    ).join(Students_Classes, Students_Classes.c.StudentID == Students.c.StudentID
    ).join(Class_period, Class_period.c.id == Students_Classes.c.Class_perID
    ).join(Classes, Classes.c.ClassID == Class_period.c.ClassID
    ).join(Academic_period, Academic_period.c.PerId == Class_period.c.PerID
    ).filter(
        Classes.c.ClassName == class_name,
        Academic_period.c.Term == term,
        Academic_period.c.Year == year
    )

    df = pd.read_sql(q.statement, engine)

    if df.empty:
        raise ValueError("No grade data available for the selected class period.")

    df['Weighted Score'] = df['Score'] * df['Weight']
    total_weight = df['Weight'].sum()
    if total_weight == 0:
        overall_score = 0
    else:
        overall_score = df['Weighted Score'].sum() / total_weight

    df['Class Average Score'] = overall_score

    df = df.drop(columns=["Weight", "Weighted Score", "StudentID", "SubjectName", "Score", "StudentName"])
    df = df.drop_duplicates()
    print(df)

    return df

def top_students_per_class(class_name: str, term: int, year: int, top_n: int):
    class_info = session.query(
        Classes.c.ClassName,
        Academic_period.c.Term,
        Academic_period.c.Year
    ).join(Class_period, Class_period.c.ClassID == Classes.c.ClassID
    ).join(Academic_period, Class_period.c.PerID == Academic_period.c.PerId
    ).filter(
        Classes.c.ClassName == class_name,
        Academic_period.c.Term == term,
        Academic_period.c.Year == year
    ).first()

    if not class_info:
        raise ValueError(f"No class or academic period matches {class_name} - Term {term}, Year {year}.")

    q = session.query(
        Students.c.StudentID,
        Students.c.StudentName,
        func.round(func.avg(Grades.c.Score), 2).label('Average Score')
    ).join(Grades, Grades.c.StudentID == Students.c.StudentID
    ).join(Students_Classes, Students_Classes.c.StudentID == Students.c.StudentID
    ).join(Class_period, Class_period.c.id == Students_Classes.c.Class_perID
    ).join(Classes, Classes.c.ClassID == Class_period.c.ClassID
    ).join(Academic_period, Academic_period.c.PerId == Class_period.c.PerID
    ).filter(
        Classes.c.ClassName == class_name,
        Academic_period.c.Term == term,
        Academic_period.c.Year == year
    ).group_by(Students.c.StudentID, Students.c.StudentName).order_by(func.avg(Grades.c.Score).desc()).limit(top_n)

    df = pd.read_sql(q.statement, engine)
    session.close()

    if df.empty:
        raise ValueError("No grade data available for the selected class period.")

    print(df)
    return df

def generate_class_average_per_subjects(class_name: str, term: int, year: int):
    q = session.query(
        Classes.c.ClassName.label('Class Name'),
        Subjects.c.SubjectName.label('Subject Name'),
        (func.sum(Grades.c.Score * Grades.c.Weight) / func.sum(Grades.c.Weight)).label('AverageScore')
    ).join(Class_period, Class_period.c.ClassID == Classes.c.ClassID
    ).join(Students_Classes, Students_Classes.c.Class_perID == Class_period.c.id
    ).join(Students, Students.c.StudentID == Students_Classes.c.StudentID
    ).join(Grades, and_(
        Grades.c.StudentID == Students.c.StudentID,
        Grades.c.PerId == Class_period.c.PerID
    )).join(Subjects, Subjects.c.SubjectID == Grades.c.SubjectID
    ).join(Academic_period, Academic_period.c.PerId == Class_period.c.PerID
    ).filter(
        Classes.c.ClassName == class_name,
        Academic_period.c.Term == term,
        Academic_period.c.Year == year
    ).group_by(
        Classes.c.ClassName,
        Subjects.c.SubjectName
    ).order_by(
        Classes.c.ClassName,
        Subjects.c.SubjectName
    )

    df = pd.read_sql(q.statement, engine)

    if df.empty:
        raise ValueError("No grade data available for the specified term and year.")

    df = df.drop(columns= ['Class Name'])
    print(df)
    return df

def generate_teacher_load(term: int, year: int):
    academic_period = session.query(Academic_period.c.PerId
                        ).filter_by(Term=term, Year=year
                        ).first()

    if not academic_period:
        raise ValueError(f"Not found term {term}, {year}.")

    per_id = academic_period.PerId

    q = session.query(
        Teachers.c.TeacherID,
        Teachers.c.TeacherName.label("Teacher Name"),
        func.count(func.distinct(Class_period.c.id)).label("Number of Classes"),
        func.count(Students_Classes.c.StudentID).label("Number of Students")
    ).join(Classes_Teacher,
           Teachers.c.TeacherID == Classes_Teacher.c.TeacherID
    ).join(Class_period,
           Classes_Teacher.c.Class_perID == Class_period.c.id
    ).join(Students_Classes,
           Class_period.c.id == Students_Classes.c.Class_perID
    ).filter(Class_period.c.PerID == per_id,
    ).group_by(Teachers.c.TeacherID, Teachers.c.TeacherName)

    df = pd.read_sql(q.statement, engine)
    session.close()

    output_excel: str = "teacher_load.xlsx"

    if df.empty:
        raise ValueError("No data found for the selected term and year.")
    
    df.to_excel(output_excel, index=False)
    print(df)
    return df
#################################################################################################################

if __name__ == "__main__":
    # generate_scorecard(1)
    # generate_class_performances_per_each_class('Grade 1', 1, 2024)
    # top_students_per_class('Grade 3', 2, 2024, 3)
    # generate_class_performance_per_subject('Art', 2, 2024)
    # generate_class_average_per_subjects('Grade 1', 1, 2024)
    # generate_teacher_load(1, 2024)
    # generate_teacher_load(2, 1, 2024, "teacher_load.xlsx")
    # plot_score_trend(1, 1, 2024, subject_id=1, output_png="trend.png")