"""
main.py
-------
Entry point utama aplikasi CampusEvent API.

Alur inisialisasi:
  1. Buat instance FastAPI dengan metadata (judul, deskripsi, versi).
  2. Import semua model ORM agar SQLAlchemy mengenali tabel-tabel yang ada.
  3. Buat semua tabel di database (jika belum ada) via `Base.metadata.create_all()`.
  4. Daftarkan semua router (auth & events) ke aplikasi.

Swagger UI tersedia di: http://127.0.0.1:8000/docs
ReDoc tersedia di      : http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI
from database import engine, Base

# Import model agar tabel ter-register ke Base.metadata sebelum create_all()
# Tanpa import ini, SQLAlchemy tidak tahu tabel apa saja yang perlu dibuat.
from models import organizer, event  # noqa: F401

from routers import auth, events

# Inisialisasi aplikasi FastAPI dengan informasi metadata untuk Swagger UI
app = FastAPI(
    title="CampusEvent API",
    description=(
        "## Sistem Manajemen Event & Webinar Kampus\n\n"
        "RESTful API microservice untuk mengelola event kampus dengan fitur:\n"
        "- **Autentikasi JWT**: Register & Login organizer\n"
        "- **CRUD Event**: Buat, lihat, edit, dan hapus event\n"
        "- **Kontrol Akses**: Hanya pemilik event yang dapat mengedit/menghapus\n\n"
        "### Cara Menggunakan Endpoint Terproteksi:\n"
        "1. Login via `/auth/login` untuk mendapatkan `access_token`\n"
        "2. Klik tombol **Authorize 🔒** di pojok kanan atas\n"
        "3. Masukkan token dengan format: `Bearer <token_anda>`\n"
    ),
    version="1.0.0",
    contact={
        "name": "CampusEvent UTS",
    },
)

# Buat semua tabel di database secara otomatis berdasarkan model yang sudah diimport.
# `checkfirst=True` (default) → tidak error jika tabel sudah ada.
Base.metadata.create_all(bind=engine)

# Daftarkan router ke aplikasi utama
# Prefix sudah didefinisikan di masing-masing router (/auth dan /events)
app.include_router(auth.router)
app.include_router(events.router)


@app.get("/", tags=["Root"], summary="Health Check")
def root():
    """Endpoint root untuk mengecek apakah API berjalan dengan baik."""
    return {
        "message": "Selamat datang di CampusEvent API! 🎓",
        "docs": "/docs",
        "version": "1.0.0",
    }
