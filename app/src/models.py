from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Date, DateTime
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import relationship
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin
import datetime
from datetime import datetime


class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2  # Patient
    DOCTOR = 3
    NURSE = 4
    CASHIER = 5


class User(db.Model, UserMixin):
    id_patient = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=False, unique=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    arrangement = relationship('Arrangement', backref='user', lazy=True)  # Backref tới bảng Arrangement

    def get_id(self):
        return self.id_patient

    def is_doctor(self):
        return self.user_role == UserRole.DOCTOR

    def is_nurse(self):
        return self.user_role == UserRole.NURSE

    def is_user(self):
        return self.user_role == UserRole.USER

    def is_admin(self):
        return self.user_role == UserRole.ADMIN

    def is_cashier(self):
        return self.user_role == UserRole.CASHIER


class Admin(User):
    __tablename__ = 'NguoiQuanTri'
    id_admin = Column(Integer, ForeignKey(User.id_patient), primary_key=True, nullable=False)
    QuyenHan = Column(String(50))
    __mapper_args__ = {
            'polymorphic_identity': 'nurse',
            'inherit_condition': id_admin == User.id_patient,
        }


class Doctor(User):
    __tablename__ = 'BacSi'
    id_doctor = Column(Integer, ForeignKey(User.id_patient), primary_key=True, nullable=False)
    ChuyenNganh = Column(String(50))
    HocVi = Column(String(50))
    GioLamViec = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'nurse',
        'inherit_condition': id_doctor == User.id_patient,
    }


class Nurse(User):
    __tablename__ = 'YTa'
    id_nurse = Column(Integer, ForeignKey(User.id_patient), primary_key=True, nullable=False)
    ChucVu = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'nurse',
        'inherit_condition': id_nurse == User.id_patient,
    }


class ThuNgan(User):
    __tablename__ = 'ThuNgan'
    id_cashier = Column(Integer, ForeignKey(User.id_patient), primary_key=True, nullable=False)
    ChucVu = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'thu ngan',
        'inherit_condition': id_cashier == User.id_patient,
    }


class ArrList(db.Model):
    id_arr_list = Column(Integer, primary_key=True, autoincrement=True)
    appointment_date = Column(Date, nullable=False, unique=True)
    patient_quantity = Column(Integer, nullable=False)
    # tinh_trang_thanh_toan = Column(Boolean)
    description = Column(String(255), nullable=True)
    arrangement = relationship('Arrangement', backref='arrlist', lazy=True)

    def get_id(self):
        return self.id_arr_list


class Arrangement(db.Model):
    id_arrangement = Column(Integer, primary_key=True, autoincrement=True)
    id_arr_list = Column(Integer, ForeignKey(ArrList.id_arr_list), nullable=True)  # Reference to an arrangement list
    id_patient = Column(Integer, ForeignKey(User.id_patient), nullable=False)  # Khóa ngoại tham chiếu User.id_patient
    id_nurse = Column(Enum(UserRole), default=UserRole.NURSE, nullable=True)  # nullable
    phone = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=False)
    patient_name = Column(String(50), nullable=False)
    appointment_date = Column(Date, nullable=False)
    address = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    def to_dict(self):
        return {
            'id_arrangement': self.id_arrangement,
            'patient_name': self.patient_name,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address
        }


# ADMIN VA THUOC
class DonVi(db.Model):
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenDonVi = Column(String(50), unique=True)
    SoLuong = Column(Integer)
    MoTa = Column(String(50))
    Thuocs = relationship('Thuoc', backref='donvi', lazy=True)

    def __str__(self):
        return self.TenDonVi


class LoaiThuoc(db.Model):
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenLoaiThuoc = Column(String(50), nullable=False, unique=True)
    Thuocs = relationship('Thuoc', backref='loaithuoc', lazy=True)

    def __str__(self):
        return self.TenLoaiThuoc


class Thuoc(db.Model):
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenThuoc = Column(String(50), unique=True)
    LoaiThuoc_ID = Column(Integer, ForeignKey(LoaiThuoc.ID), nullable=False)
    DonVi_ID = Column(Integer, ForeignKey(DonVi.ID), nullable=False)
    GiaThuoc = Column(Integer)
    SoLuong = Column(Integer)
    ThuocTrongPhieuKham = relationship('ThuocTrongPhieuKham', backref='thuoc', lazy=True)


class HoaDon(db.Model):
    __tablename__ = 'hoadon'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TienKham = Column(DOUBLE)
    TienThuoc = Column(DOUBLE)
    TinhTrangThanhToan = Column(Boolean)
    # mqh 1-1
    phieukham = relationship("PhieuKham", back_populates="hoadon", uselist=False)
    # dung back_populates thay the cho backref

    def set_state(self):
        self.TinhTrangThanhToan = 1


class QuyDinh(db.Model):
    ID = Column(Integer, primary_key=True, autoincrement=True)
    TenQuyDinh = Column(String(50), nullable=False, unique=True)
    GiaTri = Column(Integer)
    MoTa = Column(String(100))


class PhieuKham(db.Model):
    __tablename__ = 'phieukham'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NgayLapPhieu = Column(DateTime)
    ThuocTrongPhieuKhams = relationship('ThuocTrongPhieuKham', backref='phieukham', lazy=True)
    LoaiBenh = Column(String(50))
    # Tạo mối quan hệ 1-1
    HoaDon_ID = Column(Integer, ForeignKey(HoaDon.ID), unique=True)
    hoadon = relationship("HoaDon", back_populates="phieukham", uselist=False)
    BacSiLapPhieu = Column(String(50), nullable=True, default="")
    BenhNhan_id = Column(Integer, ForeignKey(User.id_patient), nullable=True)
    # dung back_populates thay the cho backref


class ThuocTrongPhieuKham(db.Model):
    PhieuKham_ID = Column(Integer, ForeignKey(PhieuKham.ID), primary_key=True, nullable=False)
    Thuoc_ID = Column(Integer, ForeignKey(Thuoc.ID), primary_key=True, nullable=False)
    LieuLuong = Column(Integer)
    CachDung = Column(String(50))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # u = User(username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN, gender="Nam", phone='0000000000')
        # db.session.add(u)
        #
        # l1 = LoaiThuoc(TenLoaiThuoc='Thảo Dược')
        # dv1 = DonVi(TenDonVi='Vĩ', SoLuong=12, MoTa='1 vi = 12 vien')
        # db.session.add(l1)
        # db.session.add(dv1)
        #
        # t1 = Thuoc(TenThuoc="Thuốc Độc", LoaiThuoc_ID=1, DonVi_ID=1, GiaThuoc=200000, SoLuong=10)
        # t2 = Thuoc(TenThuoc="Thuốc Giải", LoaiThuoc_ID=1, DonVi_ID=1, GiaThuoc=5000000, SoLuong=3)
        # db.session.add_all([t1, t2])
        # q1 = QuyDinh(TenQuyDinh='Số Bệnh Nhân Khám', MoTa='Số Bệnh Nhân Khám Trong Ngày', GiaTri=40)
        # q2 = QuyDinh(TenQuyDinh='Số Tiền Khám', MoTa='Số Tiền Khám', GiaTri=100000)
        # db.session.add_all([q1, q2])
        #
        # # Tính tiền thuốc và lấy tiền khám từ db
        # hd1 = HoaDon(TienThuoc=300000, TienKham=100000, TinhTrangThanhToan=True)
        # hd2 = HoaDon(TienThuoc=299000, TienKham=100000, TinhTrangThanhToan=True)
        # hd3 = HoaDon(TienThuoc=594000, TienKham=100000, TinhTrangThanhToan=True)
        # hd4 = HoaDon(TienThuoc=388000, TienKham=100000, TinhTrangThanhToan=True)
        # hd5 = HoaDon(TienThuoc=186000, TienKham=100000, TinhTrangThanhToan=True)
        # hd6 = HoaDon(TienThuoc=789000, TienKham=100000, TinhTrangThanhToan=True)
        # db.session.add_all([hd1, hd2, hd3, hd4, hd5, hd6])
        #
        # ngaypk1 = datetime(2024, 12, 6)
        # pk1 = PhieuKham(NgayLapPhieu=ngaypk1, HoaDon_ID=1)
        # ngaypk2 = datetime(2024, 11, 14)
        # pk2 = PhieuKham(NgayLapPhieu=ngaypk2, HoaDon_ID=2)
        # ngaypk3 = datetime(2024, 12, 19)
        # pk3 = PhieuKham(NgayLapPhieu=ngaypk3, HoaDon_ID=3)
        # ngaypk4 = datetime(2024, 10, 6)
        # pk4 = PhieuKham(NgayLapPhieu=ngaypk1, HoaDon_ID=4)
        # ngaypk5 = datetime(2024, 9, 14)
        # pk5 = PhieuKham(NgayLapPhieu=ngaypk2, HoaDon_ID=5)
        # ngaypk6 = datetime(2024, 12, 19)
        # pk6 = PhieuKham(NgayLapPhieu=ngaypk3, HoaDon_ID=6)
        # db.session.add_all([pk1, pk2, pk3, pk4, pk5, pk6])
        #
        # Drug1InReport1 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='1', LieuLuong='10',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug2InReport1 = ThuocTrongPhieuKham(Thuoc_ID='2', PhieuKham_ID='1', LieuLuong='2',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug1InReport2 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='2', LieuLuong='3',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug1InReport3 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='3', LieuLuong='5',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug1InReport4 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='4', LieuLuong='10',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug2InReport4 = ThuocTrongPhieuKham(Thuoc_ID='2', PhieuKham_ID='4', LieuLuong='2',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug1InReport5 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='5', LieuLuong='3',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # Drug1InReport6 = ThuocTrongPhieuKham(Thuoc_ID='1', PhieuKham_ID='6', LieuLuong='5',
        #                                      CachDung='Dùng Sau Khi Ăn')
        # db.session.add_all(
        #     [Drug1InReport1, Drug2InReport1, Drug1InReport2, Drug1InReport3, Drug1InReport4, Drug2InReport4,
        #      Drug1InReport5, Drug1InReport6])
        db.session.commit()
