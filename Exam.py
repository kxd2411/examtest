from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
from random import shuffle
from pywebio.output import put_html
put_html('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">')

import pyodbc

current_user = None


def connect_db():
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=ADMIN;DATABASE=TEST')
    return cnxn

def get_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_questions():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    conn.close()
    return questions
from pywebio.output import put_loading

def get_quiz_sets():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_sets")
    quiz_sets = cursor.fetchall()
    conn.close()
    return quiz_sets

def get_questions_by_quiz_set(quiz_set_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE quiz_set_id = ?", (quiz_set_id,))
    questions = cursor.fetchall()
    conn.close()
    return questions

def select_quiz_set():
    quiz_sets = get_quiz_sets()
    options = [{"label": quiz_set[1], "value": quiz_set[0]} for quiz_set in quiz_sets]
    selected_quiz_set_id = select("Vui lòng chọn bộ đề thi:", options=options)
    return selected_quiz_set_id
    
    

def show_loading_message():
    with use_scope('loading', clear=True):
        put_loading(shape='grow', color='primary')
        put_html("<strong>Vui lòng chờ...</strong>")

def hide_loading_message():
    with use_scope('loading', clear=True):
        pass

def login():
    global current_user
    put_html('<div class="container">')
    while True:
        user_info = input_group("Đăng nhập", [
            input("Tên đăng nhập", name="username", required=True),
            input("Mật khẩu", name="password", type="password", required=True)
        ])
        show_loading_message()
        user = get_user(user_info['username'], user_info['password'])
        if user:
            current_user = user
            return user
        else:
            popup("Thông báo", "Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.")

def display_user():
    global current_user
    clear()
    put_html('<div class="container">')
    put_row([
            put_image("https://portal.vietcombank.com.vn/Resources/v3/img/logo.png", width="150px")])
    put_row([
            put_column([
                put_html('<div class="text-left"><strong>Chào mừng,</strong> %s!</div>' % current_user[3])]),
            put_column([
                put_buttons([{'label': 'Chọn bài thi', 'style': 'primary', 'size': 'lg', 'value': 'quiz'}], onclick=[quiz])], size="auto"),
            put_column([
                
                put_buttons([{'label': "Đăng xuất", 'style': 'danger', 'size': 'lg', 'value': 'logout'}], onclick=[logout])], size="auto")
            ])
    put_html('</div>')



# Lưu kết quả bài thi
def save_quiz_result(user_id, quiz_set_id, score, answers):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quiz_results (user_id, quiz_set_id, score, answers) VALUES (?, ?, ?, ?)", (user_id, quiz_set_id, score, answers))
    conn.commit()
    conn.close()

# Lấy kết quả bài thi
def get_quiz_results(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_results WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

from datetime import datetime, timedelta
from threading import Thread
import time

# Đặt thời gian làm bài thi
time_limit = 30 * 60

def quiz():
    selected_quiz_set_id = select_quiz_set()
    questions = get_questions_by_quiz_set(selected_quiz_set_id)
    shuffle(questions)  # Xáo trộn danh sách câu hỏi
    score = 0
    user_answers = []
    completed = False  # Đánh dấu xem người dùng đã hoàn thành bài thi hay chưa
    
    # Hiển thị đồng hồ đếm ngược
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=time_limit)

   
    def countdown():
        nonlocal completed
        put_row([
        put_column([    
            put_html("<span id='timer_label'>Thời gian: </span><strong><span id='timer' style='font-weight: bold;'></span></strong></h2>")]).style('text-align: center'),
        ])
        while datetime.now() < end_time and not completed:
            time_left = end_time - datetime.now()
            timer = time_left - timedelta(microseconds=time_left.microseconds)         
            put_html(f"<script>document.getElementById('timer').innerHTML='{timer}';</script>")
            time.sleep(1)
        if not completed:
            # Hết thời gian làm bài
            completed = True
            put_text("Đã hết thời gian làm bài.")
            put_buttons(['Xem lại bài thi'], onclick=[lambda: review(questions, user_answers)])
            save_quiz_result(current_user[0], score, ','.join(user_answers))
            clear_content()

    Thread(target=countdown).start()

    def end_quiz():
        nonlocal completed
        completed = True
        put_text("Bạn đã kết thúc bài thi sớm.")
        put_buttons(['Xem lại bài thi'], onclick=[lambda: review(questions, user_answers)])
        save_quiz_result(current_user[0], score, ','.join(user_answers))
        clear_content()

    for i, question in enumerate(questions):
        choices = [question[2], question[3], question[4], question[5]]
        answer = radio(f"Câu {i + 1}: {question[1]}", options=choices)

        # Kiểm tra nếu người dùng không chọn câu trả lời
        if answer is None:
            user_answers.append("Không trả lời")  # Lưu câu trả lời "Không trả lời" của người dùng
        else:
            user_answers.append(answer)  # Lưu câu trả lời của người dùng

            if answer == question[6]:
                score += 1

    completed = True  # Đánh dấu là người dùng đã hoàn thành bài thi
    put_text("Kết quả: %d/%d" % (score, len(questions)))
    save_quiz_result(current_user[0], selected_quiz_set_id, score, ','.join(user_answers))
    put_buttons(['Xem lại bài thi'], onclick=[lambda: review(questions, user_answers)])
    clear_content()

def show_past_quizzes():
    
    clear()
    put_row([
        put_column([    
            put_image("https://portal.vietcombank.com.vn/Resources/v3/img/logo.png", width="150px")]).style('text-align: left'),
        put_column([
            put_html("<h1>LỊCH SỬ THI</h1>")]).style('text-align: center'),    
        put_column([
            put_buttons(['Quay lại'], onclick=[back])]).style('text-align: right')
        ])
          
    results = get_quiz_results(current_user[0])
    # Sắp xếp kết quả bài thi theo thời gian tạo (từ mới nhất đến cũ nhất)
    results = sorted(results, key=lambda x: x[4], reverse=True)
    for i, result in enumerate(results):
        # Chuyển đổi thời gian tạo thành chuỗi định dạng
        created_at = result[4].strftime("%H:%M:%S %d-%m-%Y ")
        put_html(f"Lần thi: {i + 1} - Số câu đúng: {result[2]} - Thời gian: <strong>{created_at}</strong>")
        put_buttons(['Xem lại'], onclick=[lambda r=result: review(get_questions(),  r[3].split(','))])
        put_html("<hr>")

#Xem lại bài thi    
def review(questions, user_answers):
    clear() 
       
    put_row([
        put_column([    
            put_image("https://portal.vietcombank.com.vn/Resources/v3/img/logo.png", width="150px")]).style('text-align: left'),
        put_column([
            put_html("<h1>KẾT QUẢ BÀI THI</h1>")]).style('text-align: center'),    
        put_column([
            put_buttons(['Quay lại'], onclick=[display_user])]).style('text-align: right')
        ])
    
    # Kiểm tra xem user_answers có đủ phần tử để truy xuất không
    if len(user_answers) < len(questions):
        user_answers.extend(["Không trả lời"] * (len(questions) - len(user_answers)))

    # Định nghĩa CSS cho kiểu in đậm
    put_html("<style>strong { font-weight: bold; }</style>")

# Định nghĩa CSS cho kiểu in nghiêng màu đỏ
    put_html("<style>em { font-style: italic; color: red; }</style>")

    for i, question in enumerate(questions):
        put_text(f"Câu {i + 1}: {question[1]}")
        options = [f"A. {question[2].strip()}",f"B. {question[3].strip()}",f"C. {question[4].strip()}",f"D. {question[5].strip()}"]
        user_answer = user_answers[i]
        correct_answer = question[6].strip()

        for option in options:
            
            if option[3:] == user_answer:
                # Làm nổi bật câu trả lời người dùng đã chọn bằng kiểu in đậm
                put_html("<strong>{}</strong>".format(option))
            else:
                # Nếu câu trả lời của người dùng không chính xác, in nghiêng câu trả lời đúng bằng kiểu in nghiêng màu đỏ
                if option[3:] == correct_answer:
                    put_html("<em>{}</em>".format(option))
                else:
                    put_text(option)
            
        # Thêm một dòng trống giữa các câu hỏi
        put_html("<hr>")


def clear_content():
    with use_scope("content", clear=True):
        pass

#Nút quay lại
def back():
    clear()
    display_user()
#Nút quay lại lịch sử bài thi
def back():
    clear()
    display_user()
# Đăng xuất
def logout():
    global current_user
    clear()
    current_user = None
    main()

# Đăng ký
def register():
    user_info = input_group("Đăng ký", [
        input("Tên đăng nhập", name="username", required=True),
        input("Mật khẩu", name="password", type="password", required=True),
        input("Họ và tên", name="fullname", required=True),
    ])
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)", (user_info['username'], user_info['password'], user_info['fullname']))
    conn.commit()
    conn.close()
    popup("Thông báo", "Đăng ký thành công. Vui lòng đăng nhập.")
    

# Quản lý TK
def manage_account():
    global current_user
    user_info = input_group("Quản lý tài khoản", [
        input("Tên đăng nhập", name="username", value=current_user[1], readonly=True),
        input("Mật khẩu", name="password", type="password", value=current_user[2]),
        input("Tên đầy đủ", name="full_name", value=current_user[3], required=True)
    ])
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ?, full_name = ? WHERE id = ?", (user_info['password'], user_info['full_name'], current_user[0]))
    conn.commit()
    conn.close()
    current_user = (current_user[0], current_user[1], user_info['password'], user_info['full_name'])
    popup("Thông báo", "Cập nhật thông tin tài khoản thành công!")

# Main
def main():
    global current_user
    put_row([
        put_column([    
            put_image("https://portal.vietcombank.com.vn/Resources/v3/img/logo.png", width="150px")]).style('text-align: left'),
        put_column([
            put_html("<h1>ONLINE TEST</h1>")]).style('text-align: center'),    
        put_column([
            put_buttons(['Đăng ký'], onclick=[register])]).style('text-align: right')
        ])
    if not current_user:
        user = login()
        clear_content()
        display_user()
if __name__ == "__main__":
    main()



  