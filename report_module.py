import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import numpy as np
import os
import select
from db import session, engine
from sqlalchemy import Table, func, and_, MetaData
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from models import Grades, Students, Subjects, Teachers, Classes, Classes_Teacher, Class_period, Students_Classes, Schedules, Money, Academic_period
from sqlalchemy import text

# CLASS MANAGEMENT
def generate_scorecard(student_id: int, term: int = None, year: int = None):
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc("sp_get_scorecard", [student_id, term, year])

        results = []
        for result in cursor.stored_results():
            rows = result.fetchall()
            col_names = result.column_names
            for row in rows:
                results.append(dict(zip(col_names, row)))

    finally:
        cursor.close()
        conn.close()

    if not results:
        print(f"No data found for student {student_id} in the term {term} of the {year}.")
        return f"No data found for student {student_id} in the term {term} of the {year}."



    df = pd.DataFrame(results)
    # print(df.columns)
    df = df.rename(columns={"StudentName": "Student Name", "ClassName": "Class Name", "SubjectName": "Subject Name", "TeacherName": "Teacher Name"})
    # print(df.columns)
    df['Weighted Score'] = df['Score'] * df['Weight']
    overall_score = df['Weighted Score'].sum() / df['Weight'].sum()

    output_pdf = f"scorecards/scorecard_{student_id}.pdf"
    os.makedirs("scorecards", exist_ok=True)

    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    title = f"Scorecard: Student {student_id} - {df['Student Name'].iloc[0]}"
    if term or year:
        title += f"  ({term or ''} / {year or ''})"
    elems = [Paragraph(title, styles['Title'])]

    elems.append(Paragraph(f"<b>CLASS:</b> {df['Class Name'].iloc[0]}", styles['Normal']))

    df = df.drop(columns=["Weight"])
    df = df.drop(columns=["Weighted Score"])
    df3 = df["Student Name"]
    df3 = df3.drop_duplicates()
    df = df.drop(columns=["Student Name", 'StudentID'])
    df_pdf = df.drop(columns=["Class Name"])
    df2 = df["Class Name"]
    df2 = df2.drop_duplicates()
    df = df.drop(columns=["Class Name"])
    table_data = [df_pdf.columns.tolist()] + df_pdf.values.tolist()


    # print(df)
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

    return df2.iloc[0], df3.iloc[0], df, float(overall_score)

def generate_class_average_score(class_name: str, term: int, year: int):
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc("sp_get_class_average_score", [class_name, term, year])

        results = []
        for result in cursor.stored_results():
            rows = result.fetchall()
            col_names = result.column_names
            for row in rows:
                results.append(dict(zip(col_names, row)))

    finally:
        cursor.close()
        conn.close()

    if not results:
        msg = f"No data found for class '{class_name}' in term {term} of year {year}."
        return msg

    df = pd.DataFrame(results)
    df = df.rename(columns={
        "ClassName": "Class Name",
        "Term": "Term",
        "Year": "Year",
        "AverageScore": "Average Score"
    })

    print(df)
    return df

def top_students_per_class(class_name: str, term: int, year: int, top_n: int):
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc("sp_class_summary", [class_name, term, year, top_n])

        results = []
        result_sets = cursor.stored_results()

        class_gpa_result = next(result_sets)
        class_gpa_row = class_gpa_result.fetchone()
        class_gpa = class_gpa_row[0] if class_gpa_row else None

        top_students_result = next(result_sets)
        rows = top_students_result.fetchall()
        col_names = top_students_result.column_names
        top_students = [dict(zip(col_names, row)) for row in rows]

    finally:
        cursor.close()
        conn.close()

    if not top_students:
        raise ValueError(f"No data found for class {class_name} in Term {term}, Year {year}.")

    df = pd.DataFrame(top_students)
    df = df.rename(columns={
        "StudentName": "Student Name",
        "ClassName": "Class Name",
        "Term": "Term",
        "Year": "Year",
        "AvgScore": "Average Score"
    })
    # print(df)
    return df



if __name__ == "__main__":
    # scorecard = generate_scorecard(1, 1, 2024)
    # print(scorecard)
    # generate_class_average_score("Grade 1", 1, 2024)
    top_students_per_class("Grade 1", 1, 2024, 5)
