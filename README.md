# 🎓 CampusEvent API — Sistem Manajemen Event & Webinar Kampus

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

**Tugas Ujian Tengah Semester (UTS)**  
Mata Kuliah: Pemrograman Web Lanjutan

| | |
|---|---|
| **Nama** | Gyerend Nydle Linta Mangaleuk |
| **NIM** | H071241075 |

</div>

---

## 📋 Deskripsi Proyek

**CampusEvent API** adalah RESTful API *microservice* yang dibangun menggunakan **FastAPI** untuk mengelola event dan webinar kampus. API ini memungkinkan penyelenggara (organizer) untuk mendaftarkan diri, login, dan mengelola event mereka secara penuh melalui operasi CRUD yang dilindungi oleh autentikasi **JWT (JSON Web Token)**.

---

## 🛠️ Stack Teknologi

| Komponen | Teknologi | Keterangan |
|---|---|---|
| Framework | FastAPI | Web framework modern berbasis Python |
| Database | SQLite | Database ringan berbasis file |
| ORM | SQLAlchemy | Pemetaan objek ke tabel database |
| Auth | JWT (python-jose) | Token autentikasi stateless |
| Validasi | Pydantic v2 | Validasi dan serialisasi data |
| Hashing | passlib (bcrypt) | Hashing password yang aman |
| Server | Uvicorn | ASGI server untuk FastAPI |

---

## 📁 Struktur Folder

```
uts_lanjutn/
├── main.py                 # Entry point aplikasi FastAPI
├── database.py             # Konfigurasi SQLAlchemy & session DB
├── requirements.txt        # Daftar dependensi Python
│
├── models/
│   ├── __init__.py
│   ├── organizer.py        # Model ORM: tabel `organizers`
│   └── event.py            # Model ORM: tabel `events` (FK → organizers)
│
├── schemas/
│   ├── __init__.py
│   ├── organizer.py        # Pydantic schema: validasi data Organizer
│   └── event.py            # Pydantic schema: validasi data Event
│
├── auth/
│   ├── __init__.py
│   └── jwt_handler.py      # Pembuatan & verifikasi JWT token
│
└── routers/
    ├── __init__.py
    ├── auth.py             # Endpoint: /auth/register & /auth/login
    └── events.py           # Endpoint: CRUD /events
```

---

## 🗃️ Entitas & Relasi Database

### Relasi: **One-to-Many**
> Satu `Organizer` dapat memiliki banyak `Event`

```
┌─────────────────────────┐       ┌─────────────────────────────┐
│        Organizer         │       │            Event             │
├─────────────────────────┤       ├─────────────────────────────┤
│ id (PK, auto-increment) │ ──┐   │ id (PK, auto-increment)     │
│ username (unique)       │   └──►│ organizer_id (FK → org.id)  │
│ email (unique)          │       │ title                       │
│ hashed_password         │       │ description                 │
└─────────────────────────┘       │ date                        │
                                  │ location                    │
                                  └─────────────────────────────┘
```

Relasi diimplementasikan via SQLAlchemy `relationship()`:
```python
# Di model Organizer (sisi "satu")
events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")

# Di model Event (sisi "banyak")
organizer = relationship("Organizer", back_populates="events")
```

---

## 🔌 Dokumentasi Endpoint API

### 🔓 Authentication (Publik)

| Method | Endpoint | Body | Response | Keterangan |
|--------|----------|------|----------|-----------|
| `POST` | `/auth/register` | `username`, `email`, `password` | `201 Created` | Daftar organizer baru |
| `POST` | `/auth/login` | `username`, `email`, `password` | `200 OK` + JWT Token | Login & dapatkan token |

### 📅 Events – Endpoint Publik

| Method | Endpoint | Auth | Response | Keterangan |
|--------|----------|------|----------|-----------|
| `GET` | `/events/` | ❌ Tidak perlu | `200 OK` | Lihat semua event |
| `GET` | `/events/{event_id}` | ❌ Tidak perlu | `200 OK` / `404` | Detail satu event |

### 🔐 Events – Endpoint Terproteksi JWT

| Method | Endpoint | Auth | Response | Keterangan |
|--------|----------|------|----------|-----------|
| `POST` | `/events/` | ✅ JWT Bearer | `201 Created` | Buat event baru |
| `PUT` | `/events/{event_id}` | ✅ JWT + Pemilik | `200 OK` / `403` / `404` | Edit event |
| `DELETE` | `/events/{event_id}` | ✅ JWT + Pemilik | `200 OK` / `403` / `404` | Hapus event |

### HTTP Status Code

| Kode | Kondisi |
|------|---------|
| `200 OK` | Request berhasil (GET, PUT, DELETE) |
| `201 Created` | Resource baru berhasil dibuat (POST) |
| `401 Unauthorized` | Token tidak ada, invalid, atau expired |
| `403 Forbidden` | Token valid, tapi bukan pemilik event |
| `404 Not Found` | Event tidak ditemukan |
| `422 Unprocessable Entity` | Validasi input Pydantic gagal |

---

## 🔑 Alur Autentikasi JWT

```
Client                          Server
  │                               │
  │── POST /auth/register ────────►│ Hash password (bcrypt) → simpan ke DB
  │◄─────────────────── 201 ──────│
  │                               │
  │── POST /auth/login ───────────►│ Verifikasi password → buat JWT token
  │◄─────── { access_token } ─────│  Payload: { "sub": "username", "exp": ... }
  │                               │
  │── POST /events/               │
  │   Header: Bearer <token> ─────►│ Decode token → ambil username → cari organizer
  │◄─────────────────── 201 ──────│ Simpan event dengan organizer_id otomatis
  │                               │
```

**Keamanan:**
- Password di-hash menggunakan **bcrypt** (tidak pernah simpan plain-text)
- JWT ditandatangani dengan **HMAC-SHA256 (HS256)**
- Token berlaku selama **30 menit**
- Di produksi: simpan `SECRET_KEY` di environment variable

---

## ⚙️ Cara Instalasi & Menjalankan

### 1. Clone / Download Proyek

```bash
# Masuk ke direktori proyek
cd "C:\Users\TUF GAMING\Documents\Pemrograman Web\uts_lanjutn"
```

### 2. (Opsional) Buat Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan Server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

> Jika port 8000 sudah dipakai, gunakan port lain: `--port 8001`

### 5. Akses Dokumentasi API

| URL | Keterangan |
|-----|-----------|
| http://127.0.0.1:8000/docs | **Swagger UI** (interaktif) |
| http://127.0.0.1:8000/redoc | **ReDoc** (dokumentasi lengkap) |
| http://127.0.0.1:8000/ | Health check |

---

## 🧪 Cara Uji API dengan Swagger UI

### Langkah 1 — Register

1. Buka `/docs` → bagian **Authentication**
2. Klik `POST /auth/register` → **Try it out**
3. Isi body:
   ```json
   {
     "username": "gyerend",
     "email": "gyerend@unhas.ac.id",
     "password": "password123"
   }
   ```
4. Klik **Execute** → harapkan `201 Created`

### Langkah 2 — Login & Dapatkan Token

1. Klik `POST /auth/login` → **Try it out**
2. Isi username & password yang sama
3. Salin nilai `access_token` dari response

### Langkah 3 — Authorize

1. Klik tombol **Authorize 🔒** di pojok kanan atas
2. Masukkan: `Bearer <token_anda>`
3. Klik **Authorize**

### Langkah 4 — Buat Event

1. Klik `POST /events/` → **Try it out**
2. Isi body:
   ```json
   {
     "title": "Webinar AI untuk Mahasiswa",
     "description": "Workshop mengenal machine learning dasar",
     "date": "2024-08-17 09:00",
     "location": "https://zoom.us/j/example"
   }
   ```
3. Klik **Execute** → harapkan `201 Created`

---

## 📦 Dependensi (`requirements.txt`)

```
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
sqlalchemy>=2.0.0
pydantic[email]>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

---

## 📝 Catatan Implementasi

### Relasi ORM SQLAlchemy
Relasi One-to-Many diimplementasi menggunakan `relationship()` dan `ForeignKey`. Atribut `back_populates` membuat relasi **dua arah**: dari Organizer bisa akses `.events`, dari Event bisa akses `.organizer`.

### JWT Dependency Injection
FastAPI menggunakan `Depends()` untuk menyuntikkan dependensi. `verify_token` otomatis dipanggil dan memvalidasi token sebelum fungsi endpoint dieksekusi.

### Ownership Check
Setiap operasi edit/hapus membandingkan `event.organizer_id` dengan `current_organizer.id` yang didekode dari token. Jika tidak cocok → `403 Forbidden`.

---

<div align="center">

**Gyerend Nydle Linta Mangaleuk | NIM: H071241075**  
Pemrograman Web Lanjutan — UTS 2024  
Universitas Hasanuddin

</div>
