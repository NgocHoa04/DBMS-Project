# DBMS-Project
## Generate scorecards
- Input: StudentID, term, year
- Output: df --> table in interface
- view: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## View class student
- Input: classID, term, year
- Output: df --> table in interface
- view: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## View top students overall
- Input: (top), term year
- Output: df --> table in interface
- View: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## view top students per subject
- Input: subjectID, (top), term, year
- Output: df --> table in interface
- View: cho phép nhập vào input. Khi chưa nhập thì màn hình hiển thị tất cả Student của trường

## View schedule for hiệu trưởng
- Input: ngày, tháng, năm
- Output: df --> table in interface
- View: lịch họp, lịch dạy ( hiển thị mặc định là ngày hôm nay)

## View teacher load summaries: hiệu trưởng xem được dữ liệu của toàn bộ giáo viên trong trường (id, tên, có bao nhiêu lớp, có bao nhiêu học sinh)
- Input: term, year
- Output:df --> table in interface
- View: Danh sách toàn bộ giáo viên trong trường ( khi lọc term, year --> hiển thị theo term, year)

## View Class performance per subject
- Input: SubjectID, term, year
- Output: df --> Graph in interface
- View: cho phép nhập vào input. Khi chưa nhập, màn hình hiển thị điểm trung bình từng môn của từng lớp. Khi nhập, lọc dữ liệu --> chọn nút tạo graph để hiển thị graph 

## View class performance per khối ( ví dụ: khối 10, 11, 12)
- Input: khối, term, year
- Output: df --> graph 
- View: chưa biết để view như nào cho hợp lý vì có nhiều trường một khối có rất nhiều lớp --> graph: rối, khó quan sát

## View Money(graphic)
- Input: term, year
- Output: df --> graph
- View: bảng money --> khi chọn graph --> hiển thị graph (biểu đồ tròn: có debt, paid)


