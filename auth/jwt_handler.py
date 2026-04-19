"""
auth/jwt_handler.py
-------------------
Modul pengelola JWT (JSON Web Token).

ALUR KERJA JWT:
  1. User login → server membuat token dengan `create_access_token()`.
  2. Token berisi `sub` (subject = username) dan `exp` (expiry time).
  3. Token dikirim ke client dan disimpan (misal: localStorage).
  4. Setiap request berikutnya, client kirim token di header:
     `Authorization: Bearer <token>`
  5. Server memverifikasi token dengan `verify_token()`.
     Jika valid → lanjutkan request; jika tidak → 401 Unauthorized.

KEAMANAN:
  - `SECRET_KEY`: Kunci rahasia untuk menandatangani token. Di produksi,
    HARUS disimpan di environment variable, BUKAN hardcode.
  - `ALGORITHM`: HS256 (HMAC-SHA256) adalah algoritma simetris yang umum dipakai.
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Durasi token aktif (30 menit by default).
"""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ⚠️ Di produksi, gunakan: SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = "campus-event-uts-secret-key-2024-very-secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTPBearer: skema autentikasi yang mengharapkan header `Authorization: Bearer <token>`
# `auto_error=True` → FastAPI otomatis kembalikan 403 jika header tidak ada
bearer_scheme = HTTPBearer(auto_error=True)


def create_access_token(data: dict) -> str:
    """
    Membuat JWT access token.

    Args:
        data: Dictionary yang akan di-encode ke dalam token.
              Biasanya berisi {"sub": username}.

    Returns:
        String token JWT yang sudah di-sign.
    """
    to_encode = data.copy()
    # Hitung waktu kadaluarsa token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Encode payload menjadi JWT string menggunakan secret key & algoritma
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Dependency FastAPI: Memverifikasi JWT token dari header Authorization.

    Alur:
      1. Ekstrak token dari header `Authorization: Bearer <token>`.
      2. Decode dan verifikasi signature token menggunakan SECRET_KEY.
      3. Periksa apakah token sudah expired (jose melakukan ini secara otomatis).
      4. Ambil nilai `sub` (username) dari payload.
      5. Kembalikan username jika valid; raise HTTPException 401 jika tidak.

    Returns:
        username (str): Username dari payload token yang valid.

    Raises:
        HTTPException 401: Jika token tidak valid, expired, atau format salah.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa. Silakan login kembali.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT: verifikasi signature + cek expiry otomatis
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        # JWTError mencakup: signature invalid, token expired, format salah
        raise credentials_exception
