# DBMS-Project
## Generate scorecards
- Input: StudentID, term, year
- Output: df --> table in interface
- view: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường. cho phép tải xuống file pdf

## View class student
- Input: classID, term, year
- Output: df --> table in interface
- view: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## View top students overall
- Input: (top), term year
- Output: df --> table in interface
- View: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## view top students per subject
- Input: subjectName, (top), term, year
- Output: df --> table in interface
- View: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## View schedule for hiệu trưởng
- Input: ngày, tháng, năm
- Output: df --> table in interface
- View: lịch họp, lịch dạy ( hiển thị mặc định là ngày hôm nay)

## View teacher load summaries: hiệu trưởng xem được dữ liệu của toàn bộ giáo viên trong trường (id, tên, có bao nhiêu lớp, có bao nhiêu học sinh)
- Input: term, year
- Output:df --> table in interface
- View: Danh sách toàn bộ giáo viên trong trường ( khi lọc term, year --> hiển thị theo term, year), cho phép tải xuống file excel.

## View Class performance per subject
- Input: SubjectID, term, year
- Output: df --> Graph in interface
- View: cho phép nhập vào input. Khi chưa nhập, màn hình hiển thị điểm trung bình từng môn của từng lớp. Khi nhập, lọc dữ liệu --> chọn nút tạo graph để hiển thị graph 

## View class performance 
- Input: class name, term, year
- Output: overall score of all students in class:  df --> graph ( overall_scroce/100)
- View: cho phép chọn class name, khi chưa chọn class name thì hiển thị thông tin học sinh của toàn trường. Khi chọn class name, term, year --> graph overall score of all student in class.
  
## view top student in class performance
- Input: className, top_n, term, year ( optional)
- Output: df --> table in interface
- View: cho phép nhập vào input. Nếu không nhập vào input (trừ class) --> hiển thị toàn bộ học sinh và gpa của học sinh trong lớp được chọn (optional: không nhập gì cả: hiển thị học sinh và gpa của học sinh trong trường)

## View Money(graphic)
- Input: term, year
- Output: df --> graph
- View: bảng money --> khi chọn graph --> hiển thị graph (biểu đồ tròn: có debt, paid)
