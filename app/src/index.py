import random
from datetime import date, timedelta
from dotenv import load_dotenv
from flask import render_template, request, redirect, jsonify, session
import dao
from app import app, login, db
from flask_login import login_user, logout_user, login_required, current_user
from app.src.models import User, QuyDinh, HoaDon
from app.src.models import UserRole
import pdfkit
from flask import make_response
from datetime import datetime
from payos import PaymentData, PayOS
import os


@app.route("/")
def index():
    return render_template('TrangChu/mainPage.html')


@app.route("/login", methods=['get', 'post'])
def login_process():
    err_msg = None
    err_msg1 = None
    if current_user.is_authenticated:
        return redirect('/')
    if request.method.__eq__('POST'):
        phone = request.form.get('phone')
        password = request.form.get('password')
        if not phone or not password:
            err_msg = '*Vui lòng nhập đầy đủ thông tin!!'
        else:
            user = dao.auth_user(phone=phone, password=password)
            if user:
                login_user(user=user)
                return redirect('/')
            else:
                err_msg1 = '*Số điện thoại hoặc mật khẩu KHÔNG khớp!!'

    return render_template('LogIn/login.html', err_msg=err_msg, err_msg1=err_msg1)


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/')


@app.route("/register", methods=['get', 'post'])
def register_process():
    err_msg = None
    err_msg1 = None  # len(password) >= 8
    err_msg2 = None  # empty fullname and usernane field
    err_msg3 = None
    err_msg4 = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        username = request.form.get('username')
        gender = request.form.get('gender')
        fname = request.form.get('name')
        phone = request.form.get('phone')
        if not username or not fname or not gender:
            err_msg2 = '*Vui lòng nhập đầy đủ thông tin!!'
        elif not password or len(password) < 8:
            err_msg1 = '*Mật khẩu có độ dài tối thiểu là 8!!'
        elif not password.__eq__(confirm):
            err_msg = '*Mật khẩu KHÔNG khớp!!'
        elif not request.form.get('accept-terms'):
            err_msg3 = '*Bạn cần chấp nhận Điều khoản sử dụng!!'
        elif not dao.check_unique_phone(phone):
            err_msg4 = '*Số điện thoại đã được sử dụng!!'
        else:
            data = request.form.copy()
            # ADD the function to check if the "Điều khoản" button is clicked

            del data['confirm']
            del data['accept-terms']
            dao.add_user(**data)
            return redirect('/login')

    return render_template('Register/register.html', err_msg=err_msg, err_msg1=err_msg1,
                           err_msg2=err_msg2, err_msg3=err_msg3, err_msg4=err_msg4)


@app.route("/user-profile")
def user_profile():
    user_arrangements = []
    err_msg = None
    success_msg = None
    user_arrangements = dao.retrieve_user_arrangements(current_user.phone)

    return render_template('User/UserProfile.html', user_arrangements=user_arrangements, err_msg=err_msg,
                           success_msg=success_msg, current_user=current_user)


# Handling case of user login
login.login_view = 'login_process'


@app.route("/dangKyLich", methods=['get', 'post'])
@login_required
def dang_ky_lich():  # chưa xử lý ràng buộc về quy định số bệnh nhân trong ngày
    err_msg = None
    sc_msg = False
    id_arr_list = None
    result_msg = None
    if request.method.__eq__('POST'):
        email = request.form.get('email')
        gender = request.form.get('gender')
        fname = request.form.get('name')
        date = request.form.get('appointment_date')
        if not fname or not gender or not date or not email:
            err_msg = '*Vui lòng nhập đầy đủ thông tin!!'
        else:
            data = request.form.copy()
            del data['phone']
            if dao.check_exist_arrlist(date):
                id_arr_list = dao.get_valid_id_arrlist(date)

            result_msg, sc_msg = dao.add_arrangement(id_arr_list=id_arr_list, **data)

    return render_template('DatLichKham/dangKyLich.html', err_msg=err_msg, sc_msg=sc_msg, result_msg=result_msg)


@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


def load_user(user_id):
    return User.get(user_id)


# xử lý trang lập phiếu y tá
@app.route("/lap_phieu")
def lap_phieu():
    return render_template('LapPhieu/lap_phieu.html')


# Xử lý trang thanh toán hóa đơn
# Hoa Don Chuc Nang
@app.route("/thanh_toan/<int:bill_id>", methods=['GET', 'POST'])
def bill_detail(bill_id):
    thuocs = utils.load_thuoc_trong_hoa_don(bill_id)
    sum = utils.sum_revenue(thuocs)
    tienkham = QuyDinh.query.get(2).GiaTri
    tinhtrangthanhtoan = dao.is_pay(bill_id)
    tongtien = int(sum + tienkham)
    session['tongtien'] = tongtien
    session['bill_id'] = bill_id
    return render_template('ThanhToan/chitiethoadon.html', tinhtrangthanhtoan=tinhtrangthanhtoan,
                           sum=sum, tienkham=tienkham, thuocs=thuocs, mahoadon=bill_id)


@app.route('/thanh_toan', methods=['GET', 'POST'])
def bill_process():
    kw = request.args.get('billID')
    date = request.args.get('billDate')
    bills = utils.load_bills_data(kw=kw, date=date)
    tienkham = QuyDinh.query.get(2).GiaTri
    return render_template('ThanhToan/thungan.html', tienkham=tienkham, bills=bills)


# Xử lý trang lập danh sách khám
@app.route("/lap_danh_sach", methods=["GET", "POST"])
def danh_sach_kham():
    appointment_date = None  # request data field in the database
    matched_arrangements = []
    err_message = None

    # Handle the button Xem
    if request.method == 'POST' and 'viewBtn' in request.form:
        appointment_date = request.form.get('date')
        arr = dao.load_arrangement_list(appointment_date=appointment_date)  # collect data with the requested field

        if arr:
            matched_arrangements = dao.retrieve_arrangement_info(arr)
            # Store matched_arrangements in session
            session['matched_arrangements'] = [
                {
                    'email': arr.email,
                    'patient_name': arr.patient_name,
                    'gender': arr.gender,
                    'address': arr.address,
                    'phone': arr.phone,
                    'appointment_date': arr.appointment_date.strftime('%Y-%m-%d') if isinstance(arr.appointment_date,
                                                                                                date) else arr.appointment_date
                } for arr in matched_arrangements
            ]
        else:
            err_message = "KHÔNG CÓ LỊCH KHÁM NÀO HÔM NAY!!"

    return render_template('LapDanhSach/lapdanhsach.html', matched_arrangements=matched_arrangements,
                           err_message=err_message, appointment_date=appointment_date)


# Handle the button Lap danh sach
@app.route('/save_arrangements', methods=['POST'])
def save_arrangements():
    try:
        # Assuming you're storing the matched_arrangements in session
        valid_arrangements = session.get('matched_arrangements', [])

        if valid_arrangements:
            dao.save_arrangements_to_json(valid_arrangements)
            return jsonify({'success': True, 'message': 'Danh sách khám đã được lưu thành công!!'})
        else:
            return jsonify({'success': False, 'message': 'Không có dữ liệu lịch khám để lưu!!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})


# Save valid arrangements to pdf:
@app.route("/download_pdf")
def download_pdf():
    try:
        # Configuration for PDF file parser
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

        # Get arrangements from session
        arrangements = session.get('matched_arrangements', [])

        if not arrangements:
            return "Không có dữ liệu để tạo Danh Sách Khám!!", 400

        # Create HTML content for PDF
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 20px;
                }}
                th, td {{ 
                    border: 1px solid black; 
                    padding: 8px; 
                    text-align: left;
                }}
                th {{ 
                    background-color: #f2f2f2;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .date {{
                    text-align: right;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>DANH SÁCH KHÁM BỆNH</h1>
            </div>
            <div class="date">
                Ngày: {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')}
            </div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ Tên</th>
                        <th>Số Điện Thoại</th>
                        <th>Giới Tính</th>
                        <th>Địa Chỉ</th>
                        <th>Ngày Khám</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Add data rows
        for idx, arr in enumerate(arrangements, 1):
            html_content += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{arr['patient_name']}</td>
                        <td>{arr['phone']}</td>
                        <td>{arr['gender']}</td>
                        <td>{arr['address']}</td>
                        <td>{arr['appointment_date']}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Configure PDF options
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
        }

        # Generate PDF
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=danh_sach_kham.pdf'

        return response

    except Exception as e:
        return f"Lỗi khi tạo PDF: {str(e)}", 500


# ADMIN:
@app.route('/login-admin', methods=['POST'])
def login_admin_process():
    phone = request.form.get('phone')
    password = request.form.get('password')
    user = dao.auth_user(phone=phone, password=password, role=UserRole.ADMIN)
    if user:
        login_user(user=user)
    return redirect('/admin')


# QUAN LY THUOC
@app.route("/update", methods=['post'])
def quydinh_process():
    if 'btnCnBenhNhan' in request.form:
        giatri = request.form.get('ipBenhNhanMoi')
        if giatri:
            return dao.change_quydinh_benhnhan(giatri)
    elif 'btnCnTienKham' in request.form:
        giatri = request.form.get('ipTienMoi')
        if giatri:
            return dao.change_quydinh_tienkham(giatri)
    return redirect('/admin/quydinhview')


# THANH TOÁN SỬ DỤNG PAYOS:
load_dotenv()
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CHECKSUM_KEY = os.getenv("CHECKSUM_KEY")
payOS = PayOS(client_id=CLIENT_ID, api_key=API_KEY, checksum_key=CHECKSUM_KEY)


@app.route("/create_payment_link", methods=['POST'])
def create_payment():
    domain = "http://127.0.0.1:5000"  # Xác định domain nội bộ (local) để sử dụng làm URL cho việc hủy hoặc hoàn tất thanh toán.

    try:
        payment_data = PaymentData(orderCode=random.randint(1000, 99999), amount=session['tongtien'],
                                   description=f"THANH TOAN HOA DON THUOC",
                                   cancelUrl=f"{domain}/cancel.html", returnUrl=f"{domain}/success.html")
        payou_create_payment = payOS.createPaymentLink(payment_data)

        return jsonify(payou_create_payment.to_json())
    except Exception as e:
        return jsonify(error=str(e)), 403


# Lap Phieu Kham
@app.route("/phieukham", methods=['GET', 'POST'])
def phieu_kham():
    thuoc = dao.load_thuoc()

    if request.method.__eq__('POST'):
        tong_thuoc = 0
        tien_thuoc = 0
        ngay = request.form.get('dateForm')
        benh = request.form.get('disease-txt')
        doc = request.form.get('docName')
        sdt = request.form.get('sdt')
        data = request.form.copy()
        # grouped_data = [data_list[i:i + 3] for i in range(0, len(data_list), 3)]
        del data['docName']
        del data['sdt']
        del data['dateForm']
        del data['disease-txt']
        data_list = list(data.items())
        grouped_data = [data_list[i:i + 3] for i in range(0, len(data_list), 3)]
        id = int(dao.them_phieu_kham(ngay, benh,doc,sdt))
        for group in grouped_data:

            for key, value in group:
                if 'medicine' in key:
                    medicine = value
                if 'med-instruct' in key:
                    instruct = value
                if 'med-number' in key:
                    num = float(value)
                    tien_thuoc = dao.tao_thuoc_trong_phieu_kham(medicine, num, instruct, id)
                    tong_thuoc = tien_thuoc + tong_thuoc

        dao.cap_nhat_tien_thuoc(id, tong_thuoc)
    return render_template('LapPhieuKham/phieukham.html', thuocs=thuoc)


if __name__ == '__main__':
    from app.src import admin, utils

    app.run(debug=1)
