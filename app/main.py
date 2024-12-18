from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles

from app.api.error_handlers import setup_error_handlers
from app.api.config import router
from app.models.base import Base
from app.config.pg_database import engine
from app.config.pg_test_database import test_engine
from app.middlewares.jwt_auth import JWTAuthMiddleware
from app.config.settings import PROFILE_PICTURE_DIR

# Create the database schema
Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=test_engine)

# Initialize the FastAPI app with CORS and JWT middlewares
app = FastAPI(
    title="Gnostic",
    version="1.0.0",
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(JWTAuthMiddleware),
    ],
)


# Health check endpoint
@app.get("/")
def health_check():
    return {"message": "GNOSTIC"}


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Store the original openapi method
original_openapi = app.openapi


# Custom OpenAPI schema with JWT BearerAuth
def get_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = original_openapi()  # Call the original method
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the default OpenAPI schema with the custom one
app.openapi = get_openapi
app.mount(
    f"/{PROFILE_PICTURE_DIR}",
    StaticFiles(directory=PROFILE_PICTURE_DIR),
    name="profile_picture",
)

# Include the routes and error handlers
app.include_router(router, prefix="/api/v1")
setup_error_handlers(app=app)
