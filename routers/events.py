"""
routers/events.py
-----------------
Router untuk endpoint CRUD Event.

Endpoint Publik (tanpa autentikasi):
  - GET /events          → Daftar semua event
  - GET /events/{id}     → Detail event tertentu

Endpoint Terproteksi JWT (butuh header `Authorization: Bearer <token>`):
  - POST /events         → Buat event baru (otomatis terkait organizer yang login)
  - PUT /events/{id}     → Edit event (hanya pemilik)
  - DELETE /events/{id}  → Hapus event (hanya pemilik)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.event import Event
from models.organizer import Organizer
from schemas.event import EventCreate, EventResponse
from auth.jwt_handler import verify_token

router = APIRouter(prefix="/events", tags=["Events"])


def get_current_organizer(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Organizer:
    """
    Helper dependency: Mengambil objek Organizer dari database
    berdasarkan username yang didekode dari JWT token.

    Ini memastikan bahwa user yang sedang login benar-benar ada di database.
    """
    organizer = db.query(Organizer).filter(Organizer.username == username).first()
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organizer tidak ditemukan."
        )
    return organizer


# ─── PUBLIC ENDPOINTS ───────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[EventResponse],
    status_code=status.HTTP_200_OK,
    summary="Lihat semua event (publik)",
)
def get_all_events(db: Session = Depends(get_db)):
    """Mengembalikan daftar seluruh event yang tersedia. Tidak perlu login."""
    events = db.query(Event).all()
    return events


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Lihat detail event tertentu (publik)",
)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Mengembalikan detail satu event berdasarkan ID. Tidak perlu login."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )
    return event


# ─── PROTECTED ENDPOINTS (membutuhkan JWT) ──────────────────────────────────

@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat event baru (perlu login)",
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_organizer: Organizer = Depends(get_current_organizer),  # ← JWT check
):
    """
    Membuat event baru.

    Event OTOMATIS dikaitkan ke organizer yang sedang login melalui
    `organizer_id = current_organizer.id`. Client tidak perlu mengirim `organizer_id`.
    """
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        date=event_data.date,
        location=event_data.location,
        organizer_id=current_organizer.id,   # Ambil dari token, bukan dari body request
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit event (perlu login, hanya pemilik)",
)
def update_event(
    event_id: int,
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_organizer: Organizer = Depends(get_current_organizer),  # ← JWT check
):
    """
    Mengupdate event. Hanya organizer PEMILIK event yang bisa mengedit.

    Pengecekan kepemilikan: `event.organizer_id == current_organizer.id`.
    Jika bukan pemilik → 403 Forbidden.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )

    # Cek kepemilikan: apakah event ini milik organizer yang sedang login?
    if event.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengedit event ini."
        )

    # Update atribut event
    event.title = event_data.title
    event.description = event_data.description
    event.date = event_data.date
    event.location = event_data.location

    db.commit()
    db.refresh(event)
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    summary="Hapus event (perlu login, hanya pemilik)",
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_organizer: Organizer = Depends(get_current_organizer),  # ← JWT check
):
    """
    Menghapus event. Hanya organizer PEMILIK event yang bisa menghapus.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event dengan ID {event_id} tidak ditemukan."
        )

    # Cek kepemilikan
    if event.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk menghapus event ini."
        )

    db.delete(event)
    db.commit()
    return {"message": f"Event '{event.title}' berhasil dihapus."}
