from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()  # از .env خوانده نمی‌کند مگر خودت .env بذاری یا env vars تنظیم کنی

from auth import router as auth_router
from shop import router as shop_router
from payment import router as payment_router
from db import init_db

app = FastAPI(title="Vitamino")

# CORS (در تولید محدودش کن)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# استاتیک + تمپلیت
app.mount("/static", StaticFiles(directory="static"), name="static")

# مسیرها
app.include_router(auth_router, prefix="/auth")
app.include_router(shop_router, prefix="/shop")
app.include_router(payment_router, prefix="/payment")

@app.on_event("startup")
def startup():
    # دیتابیس را در صورت نیاز اولیه‌سازی می‌کند (جداول users/products/orders)
    db_path = os.getenv("DB_PATH", "output(2)(1).sqlite")
    init_db(db_path)

@app.get("/ping")
def ping():
    return {"status": "ok"}
