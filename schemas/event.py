"""
schemas/event.py
----------------
Pydantic schemas untuk validasi data Event.

  - EventCreate  : Data yang diterima saat membuat/mengubah event.
  - EventResponse: Data yang dikembalikan ke client, termasuk `organizer_id`.
"""

from pydantic import BaseModel, ConfigDict, field_validator


class EventCreate(BaseModel):
    """Schema untuk request body POST /events dan PUT /events/{id}."""
    title: str
    description: str | None = None   # Opsional (boleh tidak diisi)
    date: str                         # Format bebas, misal "2024-08-17 09:00"
    location: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Judul event tidak boleh kosong.")
        return v

    @field_validator("location")
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Lokasi event tidak boleh kosong.")
        return v

    @field_validator("date")
    @classmethod
    def date_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tanggal event tidak boleh kosong.")
        return v


class EventResponse(BaseModel):
    """Schema untuk response event (data yang dikembalikan ke client)."""
    id: int
    title: str
    description: str | None
    date: str
    location: str
    organizer_id: int   # Menampilkan pemilik event

    model_config = ConfigDict(from_attributes=True)
