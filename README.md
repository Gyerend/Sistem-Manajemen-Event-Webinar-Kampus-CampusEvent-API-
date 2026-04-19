# CampusEvent API

RESTful API untuk manajemen event dan webinar kampus, dibuat sebagai tugas UTS Pemrograman Web Lanjutan.

**Nama:** Gyerend Nydle Linta Mangaleuk  
**NIM:** H071241075

---

## Tech Stack

- **FastAPI** — framework utama
- **SQLite + SQLAlchemy** — database & ORM
- **JWT (python-jose)** — autentikasi token
- **Pydantic v2** — validasi input
- **passlib (bcrypt)** — hashing password

---

## Struktur Proyek

```
uts_lanjutn/
├── main.py
├── database.py
├── requirements.txt
├── models/
│   ├── organizer.py
│   └── event.py
├── schemas/
│   ├── organizer.py
│   └── event.py
├── auth/
│   └── jwt_handler.py
└── routers/
    ├── auth.py
    └── events.py
```

---

## Relasi Database

Relasi **One-to-Many**: satu `Organizer` bisa punya banyak `Event`.  
Diimplementasikan menggunakan `ForeignKey` dan `relationship()` dari SQLAlchemy.

```
Organizer (1) ──────► Event (N)
   id ◄──────── organizer_id (FK)
```

---

## Endpoint

| Method | Endpoint | Auth | Keterangan |
|--------|----------|------|-----------|
| POST | `/auth/register` | — | Daftar organizer |
| POST | `/auth/login` | — | Login, dapat token JWT |
| GET | `/events/` | — | Lihat semua event |
| GET | `/events/{id}` | — | Detail event |
| POST | `/events/` | ✅ JWT | Buat event baru |
| PUT | `/events/{id}` | ✅ JWT + Pemilik | Edit event |
| DELETE | `/events/{id}` | ✅ JWT + Pemilik | Hapus event |

---

## Cara Menjalankan

```bash
# Install dependensi
pip install -r requirements.txt

# Jalankan server
python -m uvicorn main:app --port 8000 --reload
```

Buka **http://127.0.0.1:8000/docs** untuk Swagger UI.

---

## Cara Pakai Endpoint yang Terproteksi

1. Register via `POST /auth/register`
2. Login via `POST /auth/login` → salin `access_token`
3. Klik **Authorize 🔒** di Swagger UI
4. Masukkan: `Bearer <token>` lalu klik Authorize
5. Sekarang bisa akses endpoint POST, PUT, DELETE

> Event yang dibuat otomatis terhubung ke akun yang sedang login.  
> Hanya pemilik event yang bisa edit atau hapus.
