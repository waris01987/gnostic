from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader

from app.routes import auth, role, permission, user, organisation, language, contacts

swagger_header = APIKeyHeader(name="Authorization", scheme_name="Gnostic JWT")
router = APIRouter()

router.include_router(auth.router)
router.include_router(user.router)
router.include_router(organisation.router)
router.include_router(role.router)
router.include_router(permission.router)
router.include_router(language.router)
router.include_router(contacts.router)
