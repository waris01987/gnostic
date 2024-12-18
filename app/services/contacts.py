from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from pydantic import AnyUrl
from uuid import UUID

from app.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from app.models.contacts import (
    Contact,
    SocialAccounts,
    MeetingInfo,
    AdditionalInformation,
)


class ContactService:
    @staticmethod
    async def fetch_contact_info(db: Session, contact_uuid: UUID) -> ContactResponse:
        """
        Fetch a contact's information with related nested objects.
        """
        db_contact = (
            db.query(Contact)
            .options(
                selectinload(Contact.social_accounts),
                selectinload(Contact.meeting_info),
                selectinload(Contact.additional_information),
            )
            .filter(Contact.uuid == contact_uuid)
            .first()
        )

        if not db_contact:
            raise ValueError("Contact not found")

        response_data = {
            "uuid": db_contact.uuid,
            "title": db_contact.title,
            "first_name": db_contact.first_name,
            "middle_name": db_contact.middle_name,
            "last_name": db_contact.last_name,
            "country": db_contact.country,
            "country_of_stay": db_contact.country_of_stay,
            "personal_email": db_contact.personal_email,
            "personal_mobile": db_contact.personal_mobile,
            "birthday": db_contact.birthday,
            "bio": db_contact.bio,
            "group_ids": [],
            "social_accounts": db_contact.social_accounts.__dict__,
            "meeting_info": db_contact.meeting_info.__dict__,
            "additional_information": db_contact.additional_information.__dict__,
            "additional_details": db_contact.additional_details,
            "created_at": db_contact.created_at,
            "updated_at": db_contact.updated_at,
        }

        return ContactResponse(**response_data)

    @staticmethod
    async def create_contact(db: Session, contact: ContactCreate) -> ContactResponse:
        """
        Create a new contact and return its detailed information.
        """
        try:
            db_contact = Contact(
                title=contact.title,
                first_name=contact.first_name,
                middle_name=contact.middle_name,
                last_name=contact.last_name,
                country=contact.country,
                country_of_stay=contact.country_of_stay,
                personal_email=contact.personal_email,
                personal_mobile=contact.personal_mobile,
                birthday=contact.birthday,
                bio=contact.bio,
                additional_details=contact.additional_details,
            )
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)

            social_accounts_data = contact.social_accounts.dict(
                exclude_unset=True, by_alias=True
            )
            for key, value in social_accounts_data.items():
                if isinstance(value, AnyUrl):
                    social_accounts_data[key] = str(value)

            social_accounts = SocialAccounts(
                contact_id=db_contact.uuid,
                **social_accounts_data,
            )
            meeting_info = MeetingInfo(
                contact_id=db_contact.uuid,
                **contact.meeting_info.dict(exclude_unset=True),
            )
            additional_info = AdditionalInformation(
                contact_id=db_contact.uuid,
                **contact.additional_information.dict(exclude_unset=True),
            )

            db.add_all([social_accounts, meeting_info, additional_info])
            db.commit()

            return await ContactService.fetch_contact_info(db, db_contact.uuid)

        except IntegrityError:
            db.rollback()
            raise ValueError("Email already exists or invalid data provided")
        except Exception as e:
            db.rollback()
            raise Exception(f"Error creating contact: {str(e)}")

    @staticmethod
    async def get_contact(db: Session, contact_id: UUID) -> ContactResponse:
        """
        Retrieve an existing contact by UUID.
        """
        try:
            return await ContactService.fetch_contact_info(db, contact_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve contact: {str(e)}")

    @staticmethod
    async def update_contact(
        db: Session, contact_id: UUID, contact_data: ContactUpdate
    ) -> ContactResponse:
        """
        Update an existing contact with new data and return the updated contact information.
        """
        try:
            contact = db.query(Contact).filter(Contact.uuid == contact_id).first()
            if not contact:
                raise ValueError("Contact not found")

            for key, value in contact_data.dict(exclude_unset=True).items():
                if hasattr(contact, key):
                    setattr(contact, key, value)

            if contact_data.social_accounts:
                social_accounts_data = contact_data.social_accounts.dict(
                    exclude_unset=True
                )
                for key, value in social_accounts_data.items():
                    if hasattr(contact.social_accounts, key):
                        setattr(contact.social_accounts, key, value)

            if contact_data.meeting_info:
                meeting_info_data = contact_data.meeting_info.dict(exclude_unset=True)
                for key, value in meeting_info_data.items():
                    if hasattr(contact.meeting_info, key):
                        setattr(contact.meeting_info, key, value)

            if contact_data.additional_information:
                additional_info_data = contact_data.additional_information.dict(
                    exclude_unset=True
                )
                for key, value in additional_info_data.items():
                    if hasattr(contact.additional_information, key):
                        setattr(contact.additional_information, key, value)

            db.commit()

            return await ContactService.fetch_contact_info(db, contact_id)

        except IntegrityError:
            db.rollback()
            raise ValueError("Invalid data provided for update")
        except Exception as e:
            db.rollback()
            raise Exception(f"Error updating contact: {str(e)}")

    @staticmethod
    async def delete_contact(db: Session, contact_id: UUID) -> bool:
        """
        Delete a contact and all related information in other tables.
        """
        contact = (
            db.query(Contact)
            .options(
                selectinload(Contact.social_accounts),
                selectinload(Contact.meeting_info),
                selectinload(Contact.additional_information),
            )
            .filter(Contact.uuid == contact_id)
            .first()
        )

        if not contact:
            return False

        try:
            if contact.social_accounts:
                db.delete(contact.social_accounts)
            if contact.meeting_info:
                db.delete(contact.meeting_info)
            if contact.additional_information:
                db.delete(contact.additional_information)

            db.delete(contact)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise Exception(f"Error deleting contact: {str(e)}")
