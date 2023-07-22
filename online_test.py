from pywebio.input import *
from pywebio.output import *

# Khởi tạo biến để đếm điểm
score = 0

# Tạo câu hỏi
questions = [
    {
        "question": "Tính tổng 2 + 2",
        "answer": "4"
    },
    {
        "question": "Tính tích 3 x 4",
        "answer": "12"
    },
    {
        "question": "Tính phép chia 10 / 2",
        "answer": "5"
    },
    {
        "question": "Tính phép trừ 7 - 3",
        "answer": "4"
    }
]

# Đăng nhập để bắt đầu bài kiểm tra
username = input("Nhập tên của bạn:", type=TEXT)
password = input("Mật khẩu:", type=PASSWORD)

# Kiểm tra xem tên đăng nhập và mật khẩu có hợp lệ không
if username == "admin" and password == "1234":
    # Hiển thị tiêu đề và logo
    put_markdown("# Bài kiểm tra toán học")
    put_image("https://portal.vietcombank.com.vn/Resources/v3/img/logo.png")

    # Hiển thị câu hỏi và yêu cầu người dùng nhập câu trả lời
    for i, q in enumerate(questions):
        answer = input(q['question'], type=TEXT)

        # Kiểm tra xem câu trả lời có đúng không
        if answer == q['answer']:
            # Nếu câu trả lời đúng, tăng điểm số lên 1
            score += 1

    # Hiển thị kết quả và điểm số
    put_markdown("## Kết quả")
    put_text("Bạn đã trả lời đúng %d câu hỏi trong số %d câu." % (score, len(questions)))
else:
    # Nếu tên đăng nhập hoặc mật khẩu không hợp lệ, hiển thị thông báo lỗi
    put_text("Tên đăng nhập hoặc mật khẩu không đúng.")
