"""
models/organizer.py
-------------------
Model ORM untuk entitas Organizer (pengguna/penyelenggara event).

Kelas `Organizer` dipetakan ke tabel `organizers` di database.
Atribut:
  - id            : Primary key (auto-increment).
  - username      : Nama pengguna, unik dan tidak boleh null.
  - email         : Alamat email, unik dan tidak boleh null.
  - hashed_password: Kata sandi yang telah di-hash (TIDAK pernah simpan plain text).
  - events        : Relasi One-to-Many ke model Event.
                    `back_populates="organizer"` membuat relasi dua arah sehingga
                    dari objek Event kita bisa akses `.organizer`, dan dari objek
                    Organizer kita bisa akses `.events` (list of Event).
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Organizer(Base):
    __tablename__ = "organizers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    # Relasi One-to-Many: satu Organizer → banyak Event
    # `cascade="all, delete-orphan"` berarti jika Organizer dihapus,
    # semua Event miliknya juga ikut terhapus secara otomatis.
    events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
