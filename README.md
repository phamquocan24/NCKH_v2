Mong muốn triển khai extension và dashboard như sau:
+ Tools và framework:
_ php - laravel(với source đã có khung xương của code) và sử dụng DB MySQL
_ Python - SQL Server
_ C# - ASP .NET, entity framework

+ Thiết kế theo kiểu client - server, hoặc MVC, hoặc lấy API
+ Với giao diện:
Extension phải có xác thực login, logout, register, forget password, có thể chọn được model phát hiện
=> Sau đó phân quyền đối với user chỉ xem được danh sách của các label từng comment, thời gian phát hiện, tần xuất comment, chi tiết comment của mỗi user đó khi được điều hướng sang giao diện web. Còn đối với admin sẽ được toàn quyền là được truy cập vào giao diện web để xem được gồm dashboard, chi tiết(label, comment, thời gian, tên người commnet, tần suất), danh sách user, thêm sửa xóa user, phân quyền, xem được trang để xuất tài liệu pdf, excel, word, print

API:
Triển khai model đã huấn luyện thành FAST API trên hugging face để lấy API model, lấy cả Graph API của các nền tảng mạng xã hội để triển khai extension thành công cần phải có những yêu cầu nội dung sau:
 - DB phân quyền Admin user, comment log để lưu trữ thông tin, log của hệ thống ghi, [người dùng, role, comment 
- Trạng thái được lưu (lưu thông tin cmt đã được ktra,] 
- Xây dựng API: 4 gói chứa model, config security, FE, API: chia làm 2 endpoint: từ extension về hệ thống, API cho user admin 
- Dùng database có vector và mối quan hệ 
- Dùng ngôn ngữ python triển khai xử lý logic và thao tác khác, đặc biệt bộ dữ liệu huấn luyện model .h5, safetensor gồm 4 nhãn là 0-clean, 1-offensive, 2-hate, 3-spam
