"""
models/event.py
---------------
Model ORM untuk entitas Event (acara/webinar kampus).

Kelas `Event` dipetakan ke tabel `events` di database.
Atribut:
  - id            : Primary key (auto-increment).
  - title         : Judul event.
  - description   : Deskripsi event (opsional, boleh null).
  - date          : Tanggal & waktu pelaksanaan (String agar fleksibel).
  - location      : Lokasi / link online event.
  - organizer_id  : Foreign key ke tabel `organizers.id`.
                    Ini adalah sisi "Many" dalam relasi One-to-Many.
  - organizer     : Relasi balik ke objek Organizer pemilik event.
                    `back_populates="events"` harus sinkron dengan
                    nama atribut di model Organizer.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(String, nullable=False)
    location = Column(String, nullable=False)

    # Foreign Key: menghubungkan setiap Event ke satu Organizer pemilik.
    # `nullable=False` memastikan setiap event HARUS punya organizer.
    organizer_id = Column(Integer, ForeignKey("organizers.id"), nullable=False)

    # Relasi balik ke model Organizer (sisi "banyak" dari One-to-Many)
    organizer = relationship("Organizer", back_populates="events")
