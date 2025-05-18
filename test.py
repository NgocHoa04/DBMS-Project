from report import SchoolAnalytics  # Đổi lại tên file nếu cần
import pandas as pd

def main():
    sa = SchoolAnalytics()

    # Test 1: Generate Scorecard
    # print("Testing generate_scorecard...")
    # result = sa.generate_scorecard(student_id=1, term=1, year=2024)
    # print(result)

    # # Test 2: Class average score
    # print("Testing generate_class_average_score...")
    # class_avg_df = sa.generate_class_average_score(class_name="Class A", term=1, year=2023)
    # print(class_avg_df)

    # # Test 3: Top students per class
    # print("Testing top_students_per_class...")
    # top_students_df = sa.top_students_per_class(class_name="Class A", term=1, year=2023, top_n=5)
    # print(top_students_df)

    # # Test 4: Average per subject
    # print("Testing generate_class_average_per_subjects...")
    # avg_sub_df = sa.generate_class_average_per_subjects("Class A", term=1, year=2023)
    # print(avg_sub_df)

    # # Test 5: Teacher Load
    # print("Testing generate_teacher_load...")
    # teacher_load_df = sa.generate_teacher_load(term=1, year=2023)
    # print(teacher_load_df)

    # # Test 6: Top students overall
    print("Testing top_students_overall...")
    overall_df = sa.top_students_overall(term=1, year=2024, top_n=5)
    print(overall_df)

    # # Test 7: Top students per subject
    # print("Testing top_students_per_subject...")
    # top_math_df = sa.top_students_per_subject(term=1, year=2023, top_n=5, subject_name='Math')
    # print(top_math_df)

    # # Test 8: Student Geolocation
    # print("Testing get_student_locations_df...")
    # loc_df = sa.get_student_locations_df()
    # print(loc_df.head())

if __name__ == "__main__":
    main()
