"""
database.py
-----------
Konfigurasi koneksi database menggunakan SQLAlchemy.

- `engine`: Mesin database yang menghubungkan SQLAlchemy ke file SQLite.
- `SessionLocal`: Factory untuk membuat sesi database. Setiap request akan
  mendapatkan sesi sendiri (dibuat & ditutup secara independen).
- `Base`: Kelas dasar deklaratif yang diwarisi oleh semua model ORM.
  SQLAlchemy menggunakannya untuk melacak semua tabel yang terdaftar.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# URL koneksi ke SQLite. File `campus_event.db` akan dibuat otomatis
# di direktori yang sama saat aplikasi pertama kali dijalankan.
SQLALCHEMY_DATABASE_URL = "sqlite:///./campus_event.db"

# `check_same_thread=False` diperlukan untuk SQLite agar bisa digunakan
# di lingkungan multi-thread seperti FastAPI (async).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Sesi database: autocommit=False agar transaksi harus di-commit secara eksplisit,
# autoflush=False agar perubahan tidak langsung dikirim ke DB sebelum commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Kelas dasar untuk semua model ORM SQLAlchemy."""
    pass


def get_db():
    """
    Dependency function untuk FastAPI.
    Membuat sesi database baru per-request, lalu menutupnya setelah selesai.
    Digunakan dengan `Depends(get_db)` di endpoint router.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
