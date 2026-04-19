"""
routers/auth.py
---------------
Router untuk endpoint autentikasi: /register dan /login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models.organizer import Organizer
from schemas.organizer import OrganizerCreate, OrganizerResponse
from auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# CryptContext menggunakan bcrypt untuk hashing password.
# bcrypt adalah algoritma hashing yang aman dan lambat secara by-design,
# sehingga menyulitkan brute-force attack.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Mengubah plain-text password menjadi hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi apakah plain-text password cocok dengan hash yang tersimpan."""
    return pwd_context.verify(plain_password, hashed_password)


@router.post(
    "/register",
    response_model=OrganizerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi Organizer baru",
)
def register(organizer_data: OrganizerCreate, db: Session = Depends(get_db)):
    """
    Mendaftarkan penyelenggara (organizer) baru.

    - Cek duplikasi username & email.
    - Hash password sebelum menyimpan ke database.
    - Kembalikan data organizer (tanpa password).
    """
    # Cek apakah username sudah dipakai
    if db.query(Organizer).filter(Organizer.username == organizer_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{organizer_data.username}' sudah digunakan."
        )
    # Cek apakah email sudah dipakai
    if db.query(Organizer).filter(Organizer.email == organizer_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{organizer_data.email}' sudah terdaftar."
        )

    # Buat objek Organizer baru dengan password yang sudah di-hash
    new_organizer = Organizer(
        username=organizer_data.username,
        email=organizer_data.email,
        hashed_password=hash_password(organizer_data.password),
    )
    db.add(new_organizer)
    db.commit()
    db.refresh(new_organizer)   # Muat ulang dari DB untuk mendapatkan `id` yang di-generate
    return new_organizer


@router.post(
    "/login",
    summary="Login dan dapatkan JWT token",
)
def login(organizer_data: OrganizerCreate, db: Session = Depends(get_db)):
    """
    Login organizer dan mengembalikan JWT access token.

    Request body hanya memerlukan `username` dan `password`.
    Token dikembalikan dalam format Bearer dan digunakan untuk endpoint terproteksi.

    Sengaja tidak menggunakan `response_model` agar struktur respons token fleksibel.
    """
    # Cari organizer berdasarkan username
    organizer = db.query(Organizer).filter(
        Organizer.username == organizer_data.username
    ).first()

    # Jika tidak ditemukan ATAU password salah → kembalikan pesan error umum
    # (Jangan beri tahu mana yang salah untuk keamanan)
    if not organizer or not verify_password(organizer_data.password, organizer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buat JWT token: payload menggunakan `sub` (subject) berisi username
    access_token = create_access_token(data={"sub": organizer.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": f"Selamat datang, {organizer.username}!",
    }
