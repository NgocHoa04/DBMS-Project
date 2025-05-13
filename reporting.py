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
    print(f"Overall Score: {overall_score}")


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

def generate_class_performances(class_per_id: int, term: int = None, year: int = None,
                               output_png: str = "class_perf.png"):
    
    class_info = session.query(
        Classes.c.ClassName,
        Academic_period.c.Term,
        Academic_period.c.Year
    ).join(Class_period, Class_period.c.ClassID == Classes.c.ClassID
    ).join(Academic_period, Class_period.c.PerID == Academic_period.c.PerId
    ).filter(Class_period.c.id == class_per_id,
             Academic_period.c.Term == term,
             Academic_period.c.Year == year
    ).first()

    if not class_info:
        raise ValueError("No class or academic period matches the given class_period_id, term, and year.")

    class_name, term_val, year_val = class_info

    q = session.query(
        Subjects.c.SubjectName,
        Grades.c.Score,
    ).join(Grades, Subjects.c.SubjectID == Grades.c.SubjectID
    ).join(Class_period, Grades.c.PerId == Class_period.c.PerID
    ).filter(Class_period.c.id == class_per_id)

    df = pd.read_sql(q.statement, engine)
    session.close()

    if df.empty:
        raise ValueError("No grade data available for the selected class period.")

    avg = df.groupby('SubjectName')['Score'].mean().sort_values()

    plt.figure()
    avg.plot(kind='bar', color='skyblue')
    plt.title(f"Performance of Class {class_name} - Term {term_val}, {year_val}")
    plt.ylabel("Average Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_png)
    # plt.show()
    plt.close()

def generate_teacher_load(teacher_id : int, term: int, year: int, output_excel: str = "teacher_load.xlsx"):
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
             Teachers.c.TeacherID == teacher_id
    ).group_by(Teachers.c.TeacherID, Teachers.c.TeacherName)

    df = pd.read_sql(q.statement, engine)
    session.close()

    if df.empty:
        raise ValueError("No data found for the selected term and year.")
    print(df)
    df.to_excel(output_excel, index=False)

def plot_score_trend(student_id: int,
                      current_term: int,
                      current_year: int,
                      subject_id: int = None,
                      output_png: str = "trend.png"):
    q = session.query(
        Grades.c.Score,
        Academic_period.c.Term,
        Academic_period.c.Year
    ).join(Academic_period,
           Grades.c.PerId == Academic_period.c.PerId
    ).filter(Grades.c.StudentID == student_id)

    if subject_id:
        q = q.filter(Grades.c.SubjectID == subject_id)

    df = pd.read_sql(q.statement, engine)
    session.close()

    if df.empty:
        raise ValueError("No grade data available for the selected student.")

    term_map = {1: 0.0, 2: 0.33, 3: 0.66}
    reverse_term_map = {0.0: 1, 0.33: 2, 0.66: 3}

    df['TimeNum'] = df['Year'] + df['Term'].map(term_map)
    df = df.sort_values('TimeNum')

    if len(df) < 4:
        raise ValueError("Need at least 4 academic terms to make a prediction.")
    
    X = df[['TimeNum']]
    y = df['Score']
    model = LinearRegression().fit(X, y)

    y_pred = model.predict(X)

    future_terms = []
    for _ in range(4):
        if current_term == 3:
            current_term = 1
            current_year += 1
        else:
            current_term += 1
        time_num = current_year + term_map[current_term]
        future_terms.append((time_num, current_term, current_year))

    future_time_nums = np.array([[t[0]] for t in future_terms])
    future_scores = model.predict(future_time_nums)

    plt.figure()
    plt.plot(df['TimeNum'], df['Score'], marker='o', label='Actual', color='blue')
    plt.plot(df['TimeNum'], y_pred, linestyle='--', label='Trend', color='orange')
    for (t, term, year), score in zip(future_terms, future_scores):
        plt.scatter([t], [score], color='red')
        plt.text(t, score + 0.3, f"{round(score,1)}\n(T{term}-{year})", ha='center', fontsize=8)

    plt.title(f"Score Trend for Student #{student_id}")
    plt.xlabel("Time (Year.Term)")
    plt.ylabel("Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_png)
    plt.show()
    plt.close()

if __name__ == "__main__":
    generate_scorecard(1)
    # generate_class_performances(1, 1, 2024, "class_perf.png")
    # generate_teacher_load(2, 1, 2024, "teacher_load.xlsx")
    # plot_score_trend(1, 1, 2024, subject_id=1, output_png="trend.png")