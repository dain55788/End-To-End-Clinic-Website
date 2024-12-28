from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.src.models import HoaDon, PhieuKham, ThuocTrongPhieuKham, Thuoc, DonVi, LoaiThuoc

current_year = datetime.now().year
one_year_ago = datetime.now() - timedelta(days=365)
start_of_year = datetime(current_year, 1, 1)
end_of_year = datetime(current_year, 12, 31)


def sum_revenue(lists):
    s = 0
    for i in lists:
        s += i[-1]
    return s


# lấy các tháng có dl
def get_months_of_data():
    query = db.session.query(func.day(PhieuKham.NgayLapPhieu)).distinct()
    return query.all()


def revenue_stats(month=None, from_date=None, to_date=None):
    p = (
        db.session.query(PhieuKham.NgayLapPhieu, func.count(PhieuKham.ID), func.sum(HoaDon.TienKham + HoaDon.TienThuoc))
        .join(HoaDon, HoaDon.ID == PhieuKham.HoaDon_ID).group_by(PhieuKham.NgayLapPhieu).order_by(
            PhieuKham.NgayLapPhieu))
    if month:
        p = p.filter(func.month(PhieuKham.NgayLapPhieu) == month, func.year(PhieuKham.NgayLapPhieu) == current_year,
                     PhieuKham.NgayLapPhieu.__ge__(one_year_ago))
    if from_date:
        p = p.filter(PhieuKham.NgayLapPhieu.__ge__(from_date))
    if to_date:
        p = p.filter(PhieuKham.NgayLapPhieu.__le__(to_date))

    return p.all()


def revenue_stats_by_month(year=None):
    p = ((db.session.query(func.month(PhieuKham.NgayLapPhieu), func.count(PhieuKham.ID),
                           func.sum(HoaDon.TienKham + HoaDon.TienThuoc))
          .join(HoaDon, HoaDon.ID == PhieuKham.HoaDon_ID)
          .group_by(func.month(PhieuKham.NgayLapPhieu))
          .order_by(func.month(PhieuKham.NgayLapPhieu)))
         .filter(func.year(PhieuKham.NgayLapPhieu) == year))
    return p.all()


def drug_stats(month=None, from_date=None, to_date=None):
    p = ((db.session.query(Thuoc.TenThuoc, DonVi.TenDonVi, Thuoc.SoLuong, func.count(ThuocTrongPhieuKham.Thuoc_ID))
          .join(PhieuKham, PhieuKham.ID == ThuocTrongPhieuKham.PhieuKham_ID)
          .join(Thuoc, Thuoc.ID == ThuocTrongPhieuKham.Thuoc_ID)
          .join(DonVi, DonVi.ID == Thuoc.DonVi_ID)
          .group_by(Thuoc.TenThuoc, DonVi.TenDonVi, Thuoc.SoLuong))
         .filter(func.year(PhieuKham.NgayLapPhieu) == current_year))
    if month:
        p = p.filter(func.month(PhieuKham.NgayLapPhieu) == month)
    if from_date:
        p = p.filter(PhieuKham.NgayLapPhieu.__ge__(from_date))
    if to_date:
        p = p.filter(PhieuKham.NgayLapPhieu.__le__(to_date))

    return p.all()


def drug_stats_by_month(year=None):
    p = (db.session.query(func.month(PhieuKham.NgayLapPhieu), Thuoc.TenThuoc, DonVi.TenDonVi,
                          func.count(ThuocTrongPhieuKham.Thuoc_ID))
         .join(PhieuKham, PhieuKham.ID == ThuocTrongPhieuKham.PhieuKham_ID)
         .join(Thuoc, Thuoc.ID == ThuocTrongPhieuKham.Thuoc_ID)
         .join(DonVi, DonVi.ID == Thuoc.DonVi_ID)
         .group_by(func.month(PhieuKham.NgayLapPhieu), Thuoc.TenThuoc, DonVi.TenDonVi)
         .order_by(func.month(PhieuKham.NgayLapPhieu))
         .filter(func.year(PhieuKham.NgayLapPhieu) == year))
    return p.all()


def load_thuoc_donvi_loaithuoc():
    p = ((db.session.query(Thuoc.TenThuoc, LoaiThuoc.TenLoaiThuoc, Thuoc.SoLuong, DonVi.TenDonVi, Thuoc.GiaThuoc))
         .join(LoaiThuoc, Thuoc.LoaiThuoc_ID == LoaiThuoc.ID)
         .join(DonVi, Thuoc.DonVi_ID == DonVi.ID))
    return p.all()


# Xu ly thanh toan:
def load_thuoc_trong_hoa_don(hoadon_id):
    if hoadon_id:
        query = (
            db.session.query(Thuoc.TenThuoc, DonVi.TenDonVi, ThuocTrongPhieuKham.LieuLuong,
                             Thuoc.GiaThuoc, func.sum(Thuoc.GiaThuoc * ThuocTrongPhieuKham.LieuLuong))
            .join(Thuoc, Thuoc.ID == ThuocTrongPhieuKham.Thuoc_ID)
            .join(DonVi, DonVi.ID == Thuoc.DonVi_ID)
            .group_by(Thuoc.TenThuoc, DonVi.TenDonVi, ThuocTrongPhieuKham.LieuLuong, Thuoc.GiaThuoc)
            .filter(ThuocTrongPhieuKham.PhieuKham_ID.__eq__(hoadon_id)))
        return query.all()


def load_bills_data(kw=None, date=None):
    query = (db.session.query(HoaDon.ID, PhieuKham.NgayLapPhieu,
                              func.sum(Thuoc.GiaThuoc * ThuocTrongPhieuKham.LieuLuong), HoaDon.TinhTrangThanhToan)
             .join(HoaDon, HoaDon.ID == PhieuKham.HoaDon_ID)
             .join(ThuocTrongPhieuKham, ThuocTrongPhieuKham.PhieuKham_ID == PhieuKham.ID)
             .join(Thuoc, Thuoc.ID == ThuocTrongPhieuKham.Thuoc_ID)
             .group_by(HoaDon.ID, PhieuKham.NgayLapPhieu).order_by(-HoaDon.ID))
    if kw:
        query = query.filter(HoaDon.ID.contains(kw))
    if date:
        query = query.filter(PhieuKham.NgayLapPhieu.__eq__(date))
    return query.all()
