from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID

from app.schemas.contacts import ContactCreate
from app.config.pg_database import get_db
from app.services.contacts import ContactService
from app.schemas.contacts import ContactResponse, ContactUpdate

router = APIRouter(tags=["Contacts"])


@router.post("/contacts", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    try:
        db_contact = await ContactService.create_contact(db, contact)
        return ContactResponse.from_orm(db_contact)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create contact: {str(e)}"
        )


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: UUID, db: Session = Depends(get_db)):
    try:
        contact = await ContactService.get_contact(db, contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve contact: {str(e)}"
        )


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID, contact_data: ContactUpdate, db: Session = Depends(get_db)
):
    try:
        updated_contact = await ContactService.update_contact(
            db, contact_id, contact_data.dict(exclude_unset=True)
        )
        if not updated_contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return updated_contact
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update contact: {str(e)}"
        )


@router.delete("/contacts/{contact_id}", response_model=Dict[str, Any])
async def delete_contact(contact_id: UUID, db: Session = Depends(get_db)):
    try:
        deleted = await ContactService.delete_contact(db, contact_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Contact not found")
        return {"detail": "Contact and related information deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete contact: {str(e)}"
        )
