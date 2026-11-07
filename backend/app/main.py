from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.products import router as products_router
from app.api.category import router as category_router
from app.api.ingredients import router as ingredients_router
from app.api.sizes import router as sizes_router
from app.api.dough_type import router as dough_type_router
from app.api.user import router as user_router
from app.api.cart import router as cart_router
from app.api.auth import router as auth_router
from app.api.guest import router as guest_router
from app.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)

_default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
_origins = [
    origin.strip()
    for origin in getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(guest_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(products_router)
app.include_router(category_router)
app.include_router(ingredients_router)
app.include_router(sizes_router)
app.include_router(dough_type_router)