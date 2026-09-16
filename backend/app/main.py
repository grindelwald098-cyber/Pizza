from fastapi import FastAPI

from app.api.products import router as products_router
from app.api.category import router as category_router
from app.api.ingredients import router as ingredients_router
from app.api.sizes import router as sizes_router
from app.api.dough_type import router as dough_type_router
from app.api.user import router as user_router
from app.api.cart import router as cart_router
from app.api.auth import router as auth_router
from app.api.guest import router as guest_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(guest_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(products_router)
app.include_router(category_router)
app.include_router(ingredients_router)
app.include_router(sizes_router)
app.include_router(dough_type_router)