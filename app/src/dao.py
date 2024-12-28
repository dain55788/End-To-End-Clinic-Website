import os

from cloudinary.provisioning import user
from flask_login import current_user

from app.src.models import User, QuyDinh, HoaDon, PhieuKham, Thuoc, ThuocTrongPhieuKham
from app.src.models import Arrangement, ArrList
from flask import render_template, redirect
from app import app, db, data
from datetime import datetime, timedelta, date
import hashlib
import json


def load_arrangement_list(appointment_date=None):
    query = ArrList.query

    if appointment_date:
        query = query.filter(ArrList.appointment_date.contains(appointment_date))
        return query.first()
    return None


def add_arrlist(appointment_date, patient_quantity, description):
    arr_list = ArrList(appointment_date=appointment_date,
                       patient_quantity=patient_quantity, description=description)
    db.session.add(arr_list)
    db.session.commit()
    return arr_list.id_arr_list


def auth_user(phone, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.phone.__eq__(phone), User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def get_user_by_id(id_patient):
    return User.query.get(id_patient)


def add_user(name, username, gender, password, phone):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, gender=gender, password=password, phone=phone)

    db.session.add(u)
    db.session.commit()


def check_user_phone(phone):
    u = User.query.filter(User.phone.__eq__(phone))
    return u.first().get_id()


def check_exist_arrlist(appointment_date):
    appointment_date = str(appointment_date)
    # Query to get valid arrlist id so that arrangements can refer to
    arr_lists = ArrList.query.all()
    for arr_list in arr_lists:
        arr_list.appointment_date = str(arr_list.appointment_date)
        if arr_list.appointment_date.__eq__(appointment_date):
            return True
    return False


def get_valid_id_arrlist(appointment_date):
    if check_exist_arrlist(appointment_date):
        arrlist = ArrList.query.filter(ArrList.appointment_date.__eq__(appointment_date))
        return arrlist.first().get_id()
    return None


def add_arrangement(email, gender, name, appointment_date, address, description, id_arr_list, id_nurse=None):
    phone = current_user.phone
    id_patient = check_user_phone(phone)
    id_arr_list = get_valid_id_arrlist(appointment_date)
    result_msg = None
    patient_limit = db.session.query(QuyDinh.GiaTri).first().GiaTri
    sc_msg = None

    if id_arr_list is None:  # empty arrangement list according to date or id array list
        id_arr_list = add_arrlist(appointment_date, patient_quantity=1, description="")
        arr = Arrangement(id_arr_list=id_arr_list, id_patient=id_patient, phone=phone, email=email, gender=gender,
                          patient_name=name, appointment_date=appointment_date, address=address,
                          description=description)
        db.session.add(arr)
        db.session.commit()
        sc_msg = "Thông tin của bạn đã được ghi nhận, BeSTRONG sẽ liên hệ bạn sớm nhé!!"
    else:  # exists id arr list ịn the ArrList
        # Get the current ArrList
        arr_list = ArrList.query.filter_by(id_arr_list=id_arr_list).first()

        # Check if patient limit is exceeded
        if arr_list.patient_quantity >= patient_limit:
            result_msg = "Số bệnh nhân trong ngày đã vượt mức quy định của BeSTRONG, " \
                         "vui lòng chọn ngày khác bạn nhé <3"
            return result_msg, sc_msg  # Stop if the current arrlist patient quantity exceeds patient limit
        # Increment patient quantity
        else:
            arr_list.patient_quantity += 1

            arr = Arrangement(id_arr_list=id_arr_list, id_patient=id_patient, phone=phone, email=email, gender=gender,
                              patient_name=name, appointment_date=appointment_date, address=address, description=description)
            db.session.add(arr)
            db.session.commit()
            sc_msg = "Thông tin của bạn đã được ghi nhận, BeSTRONG sẽ liên hệ bạn sớm nhé!!"
    return result_msg, sc_msg


def retrieve_arrangement_info(arr_list: ArrList):
    # matching_arrangements = db.session.query(Arrangement).filter(
    #     Arrangement.id_arr_list.__eq__(arr_list.id_arr_list)
    # ).all()
    matching_arrangements = db.session.query(Arrangement).filter_by(id_arr_list=arr_list.id_arr_list).all()
    return matching_arrangements


def save_arrangements_to_json(valid_arrangements):
    # Prepare the data to be written to JSON
    arrangements_data = {
        "sum_number_of_arrangements": len(valid_arrangements),
        "arrangements": valid_arrangements
    }

    # Write data to a JSON file
    json_file_path = r"C:\Users\ASUS\OneDrive\Desktop\PrivateClinic\Private-Clinic-Website\app\data\arrangements.json"

    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(arrangements_data, file, indent=4, ensure_ascii=False)


def retrieve_user_arrangements(phone):
    query = Arrangement.query

    if phone:
        query = Arrangement.query.filter(Arrangement.phone.__eq__(phone))
        return query.all()

    return None


def check_unique_phone(phone):
    user = db.session.query(User).filter_by(phone=phone).first()

    return user is None  # True if no user found, i.e., phone is unique


# Thanh toan hoa don:
def is_pay(hoadon_id=None):
    p = HoaDon.query.get(hoadon_id).TinhTrangThanhToan
    if p:
        return True
    return False


def load_bills(kw=None):
    query = HoaDon.query
    if kw:
        query = query.filter(HoaDon.ID.contains(kw))
    return query.all()


# Quan Ly Thuoc:
def change_quydinh_benhnhan(giatri):
    item = QuyDinh.query.filter_by(id='1').first()
    item.GiaTri = giatri
    db.session.commit()
    return redirect('admin/quydinhview')


def change_quydinh_tienkham(giatri):
    item = QuyDinh.query.filter_by(id='2').first()
    item.GiaTri = giatri
    db.session.commit()
    return redirect('/admin/quydinhview')


# Lap Phieu Kham
def load_thuoc():
    return Thuoc.query.all()
def them_phieu_kham(ngay, benh,doc,sdt):
    tienKham = QuyDinh.query.get(2).GiaTri
    hd = HoaDon(TienThuoc=0, TienKham=tienKham, TinhTrangThanhToan=False)
    db.session.add(hd)
    db.session.commit()
    benhnhan = User.query.filter_by(phone=sdt).first()
    pk = PhieuKham(NgayLapPhieu=ngay, LoaiBenh=benh,BacSiLapPhieu= doc,BenhNhan_id= benhnhan.id_patient , HoaDon_ID=hd.ID)
    db.session.add(pk)
    db.session.commit()
    return pk.ID


def cap_nhat_tien_thuoc(phieu_id, tien):
    phieu = PhieuKham.query.filter(PhieuKham.ID == phieu_id).first()
    hoadon = HoaDon.query.get(phieu.HoaDon_ID)
    hoadon.TienThuoc = tien
    db.session.commit()


def tao_thuoc_trong_phieu_kham(ten, SoLuong, CachDung, phieu_id):
    thuoc = Thuoc.query.filter(Thuoc.TenThuoc.contains(ten)).first()
    DrugInReport = ThuocTrongPhieuKham(Thuoc_ID=thuoc.ID, PhieuKham_ID=phieu_id, LieuLuong=SoLuong,
                                       CachDung=CachDung)
    db.session.add(DrugInReport)
    db.session.commit()
    return float(thuoc.GiaThuoc * SoLuong)
