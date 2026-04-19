"""
schemas/organizer.py
--------------------
Pydantic schemas untuk validasi data Organizer.

Skema dipisah berdasarkan use-case:
  - OrganizerCreate : Data yang diterima saat registrasi (include password).
  - OrganizerResponse: Data yang dikembalikan ke client (TANPA password & hash).

`model_config = ConfigDict(from_attributes=True)` mengizinkan Pydantic
membaca atribut dari objek ORM SQLAlchemy secara langsung (dulu: `orm_mode = True`).
"""

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class OrganizerCreate(BaseModel):
    """Schema untuk request body endpoint POST /register."""
    username: str
    email: EmailStr          # Validasi format email otomatis oleh Pydantic
    password: str

    @field_validator("username")
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username tidak boleh kosong.")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password minimal 6 karakter.")
        return v


class OrganizerResponse(BaseModel):
    """Schema untuk response (data yang dikembalikan ke client)."""
    id: int
    username: str
    email: str

    # Pydantic v2: izinkan konversi dari objek ORM (bukan hanya dict)
    model_config = ConfigDict(from_attributes=True)
